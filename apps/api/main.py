import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from boxes.fetcher import run_fetch
from db import init_db
from models import Signal

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Content Machine", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/radar/fetch")
def radar_fetch(request: Request) -> list[Signal]:
    host = request.client.host if request.client else "unknown"
    if not allow_radar_fetch(host):
        return JSONResponse(
            status_code=429,
            content={"error": "Too many fetches. Please wait a minute and try again."},
        )
    return run_fetch()
