import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from boxes.belt import run_factory, run_radar
from boxes.export import export_pack
from boxes.fetcher import run_fetch
from boxes.review import decide
from db import (
    get_draft,
    get_report,
    init_db,
    list_drafts,
    list_queue,
    list_reports,
    list_scores,
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


class ReviewIn(BaseModel):
    user: str = ""
    verdict: Literal["approve", "reject"]
    reason: str = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Content Machine", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


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
        return run_radar()
    except ValueError as exc:
        return _friendly(exc)
    except Exception:
        logger.exception("radar run failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Trend fetch hit a snag. Please try again."},
        )


@app.post("/factory/run")
def factory_run(body: FactoryRunIn):
    try:
        return run_factory(body.report_id)
    except ValueError as exc:
        return _friendly(exc)
    except Exception:
        logger.exception("factory run failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Could not build a post from that report. Please try again."},
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


@app.get("/queue")
def get_queue():
    return list_queue()
