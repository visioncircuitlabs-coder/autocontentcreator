from contextlib import asynccontextmanager

from fastapi import FastAPI

from boxes.fetcher import run_fetch
from db import init_db
from models import Signal


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Content Machine", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/radar/fetch")
def radar_fetch() -> list[Signal]:
    return run_fetch()
