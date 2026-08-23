import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from obs import emit, emit_error, setup_logging

from adapters.chat_litellm import build_chat
from boxes.belt import paint_chosen, run_factory, run_radar
from boxes.fixture_dive import persist_unofficial_fixture
from boxes.export import export_pack
from boxes.fetcher import run_fetch
from boxes.review import decide
from db import (
    get_brief,
    get_draft,
    get_report,
    init_db,
    list_concepts,
    list_drafts,
    list_queue,
    list_reports,
    list_scores,
    list_events,
    list_signals,
)
from models import Signal

logger = logging.getLogger(__name__)

FETCH_RATE_LIMIT = 6
FETCH_RATE_WINDOW_S = 60.0
_fetch_hits: dict[str, deque[float]] = defaultdict(deque)


def reset_rate_limit() -> None:
    _fetch_hits.clear()


def allow_radar_fetch(host: str, now: float | None = None) -> bool:
    stamp = time.monotonic() if now is None else now
    bucket = _fetch_hits[host]
    cutoff = stamp - FETCH_RATE_WINDOW_S
    while bucket and bucket[0] <= cutoff:
        bucket.popleft()
    if len(bucket) >= FETCH_RATE_LIMIT:
        return False
    bucket.append(stamp)
    return True


def _client_host(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _friendly(exc: Exception) -> JSONResponse:
    message = str(exc) or "Something went wrong. Please try again."
    lower = message.lower()
    status = 400
    if any(
        token in lower
        for token in ("not in the queue", "unknown report", "not found", "could not produce")
    ):
        status = 404
    return JSONResponse(status_code=status, content={"error": message})


class FactoryRunIn(BaseModel):
    report_id: str = Field(min_length=1)


class FactoryImageIn(BaseModel):
    draft_id: str = Field(min_length=1)


class ReviewIn(BaseModel):
    user: str = ""
    verdict: Literal["approve", "reject"]
    reason: str = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    init_db()
    emit("api_start", chat=bool(build_chat()))
    yield


app = FastAPI(title="Content Machine", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3050",
        "http://127.0.0.1:3050",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = uuid4().hex[:10]
    request.state.request_id = request_id
    started = time.monotonic()
    try:
        response = await call_next(request)
    except Exception as exc:
        emit_error(
            "http_crash",
            exc,
            method=request.method,
            path=request.url.path,
            request_id=request_id,
        )
        raise
    ms = int((time.monotonic() - started) * 1000)
    if request.url.path not in ("/health", "/events"):
        emit(
            "http",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            ms=ms,
            request_id=request_id,
            client=_client_host(request),
        )
    response.headers["X-Request-Id"] = request_id
    return response


@app.get("/health")
def health() -> dict[str, object]:
    return {"ok": True, "chat": bool(build_chat())}


class ClientEventIn(BaseModel):
    kind: str = Field(min_length=1, max_length=80)
    payload: dict[str, Any] = Field(default_factory=dict)


@app.post("/events")
def post_event(body: ClientEventIn, request: Request):
    emit(
        f"ui.{body.kind}",
        **body.payload,
        client=_client_host(request),
    )
    return {"ok": True}


@app.get("/events")
def get_events(limit: int = 80):
    return list_events(limit)


@app.post("/radar/fetch")
def radar_fetch(request: Request) -> list[Signal]:
    host = _client_host(request)
    if not allow_radar_fetch(host):
        return JSONResponse(
            status_code=429,
            content={"error": "Too many fetches. Please wait a minute and try again."},
        )
    return run_fetch()


@app.post("/radar/run")
def radar_run(request: Request):
    host = _client_host(request)
    if not allow_radar_fetch(host):
        return JSONResponse(
            status_code=429,
            content={"error": "Too many fetches. Please wait a minute and try again."},
        )
    try:
        pack = run_radar(chat=build_chat())
        return {
            "reports": pack.reports,
            "scores": pack.scores,
            "signals_seen": pack.signals,
            "deep_dives": pack.reports,
        }
    except ValueError as exc:
        return _friendly(exc)
    except Exception:
        logger.exception("radar run failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Trend fetch hit a snag. Please try again."},
        )


@app.post("/radar/fixture")
def radar_fixture():
    """Unofficial canned deep-dive. Not this Fetch. Lets Create post still run."""
    try:
        pack = persist_unofficial_fixture()
    except Exception:
        logger.exception("fixture dive failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Could not open that idea. Please try again."},
        )
    return {
        "fixture": True,
        "signal": pack["signal"],
        "score": pack["score"],
        "report": pack["report"],
    }


@app.post("/factory/run")
def factory_run(body: FactoryRunIn):
    try:
        return run_factory(body.report_id, chat=build_chat())
    except ValueError as exc:
        return _friendly(exc)
    except Exception:
        logger.exception("factory run failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Could not build a post from that report. Please try again."},
        )


@app.post("/factory/image")
def factory_image(body: FactoryImageIn):
    try:
        return paint_chosen(body.draft_id)
    except ValueError as exc:
        return _friendly(exc)
    except Exception:
        logger.exception("factory image failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Could not make that picture. Please try again."},
        )


@app.post("/review/{draft_id}")
def review_draft(draft_id: str, body: ReviewIn):
    try:
        return decide(draft_id, body.user, body.verdict, body.reason)
    except ValueError as exc:
        return _friendly(exc)
    except Exception:
        logger.exception("review failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Could not save that decision. Please try again."},
        )


@app.get("/export/{draft_id}")
def export_draft(draft_id: str):
    try:
        path = export_pack(draft_id)
    except ValueError as exc:
        return _friendly(exc)
    except Exception:
        logger.exception("export failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Could not pack that preview. Please try again."},
        )
    return FileResponse(
        path,
        media_type="application/zip",
        filename=path.name,
    )


@app.get("/signals")
def get_signals():
    return list_signals()


@app.get("/scores")
def get_scores():
    return list_scores()


@app.get("/reports")
def get_reports():
    return list_reports()


@app.get("/reports/{report_id}")
def get_one_report(report_id: str):
    report = get_report(report_id)
    if report is None:
        return JSONResponse(
            status_code=404,
            content={"error": "That report is not on the shelf."},
        )
    return report


@app.get("/briefs/{brief_id}")
def get_one_brief(brief_id: str):
    brief = get_brief(brief_id)
    if brief is None:
        return JSONResponse(
            status_code=404,
            content={"error": "That brief is not on the shelf."},
        )
    return {
        **brief.model_dump(mode="json"),
        "concepts": [item.model_dump(mode="json") for item in list_concepts(brief_id)],
    }


@app.get("/drafts")
def get_drafts():
    return list_drafts()


@app.get("/drafts/{draft_id}")
def get_one_draft(draft_id: str):
    draft = get_draft(draft_id)
    if draft is None:
        return JSONResponse(
            status_code=404,
            content={"error": "That draft is not in the queue."},
        )
    return draft


@app.get("/drafts/{draft_id}/image")
def get_draft_image(draft_id: str):
    draft = get_draft(draft_id)
    if draft is None:
        return JSONResponse(
            status_code=404,
            content={"error": "That draft is not in the queue."},
        )
    if not draft.image_path:
        return JSONResponse(
            status_code=404,
            content={"error": "No picture on that ticket yet."},
        )
    path = Path(draft.image_path)
    if not path.is_file():
        return JSONResponse(
            status_code=404,
            content={"error": "No picture on that ticket yet."},
        )
    return FileResponse(path, media_type="image/png")


@app.get("/queue")
def get_queue():
    return list_queue()
