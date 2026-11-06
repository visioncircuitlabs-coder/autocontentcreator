from __future__ import annotations

import logging
import os

import httpx

from adapters.common import DEFAULT_QUERY_ID, REQUEST_TIMEOUT, USER_AGENT, normalize_url
from adapters.gdelt import GdeltSource
from adapters.grok_web import GrokWebSource
from adapters.news_rss import NewsRssSource, extra_rss_sources
from adapters.reddit_json import RedditJsonSource
from boxes.brand_pack import load_brand_pack
from models import Signal
from obs import emit
from ports import TrendSource

logger = logging.getLogger(__name__)


def build_client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
    )


def default_sources(client: httpx.Client) -> list[TrendSource]:
    sources: list[TrendSource] = [
        GdeltSource(client),
        NewsRssSource(client),
        RedditJsonSource(client),
    ]
    sources.extend(extra_rss_sources(client))
    if os.environ.get("XAI_API_KEY", "").strip():
        sources.append(GrokWebSource())
    return sources


def dedupe_by_url(signals: list[Signal]) -> list[Signal]:
    seen: set[str] = set()
    unique: list[Signal] = []
    for signal in signals:
        key = normalize_url(signal.url)
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(signal)
    return unique


def run_fetch(
    query_id: str | None = None,
    *,
    sources: list[TrendSource] | None = None,
    client: httpx.Client | None = None,
    persist: bool = True,
) -> list[Signal]:
    """Collect free-source signals. One dead source logs and the rest continue."""
    radar = load_brand_pack().get("radar") or {}
    query_id = query_id or str(radar.get("query_id") or DEFAULT_QUERY_ID)
    owns_client = client is None
    client = client or build_client()
    try:
        srcs = sources if sources is not None else default_sources(client)

        def _one(source):
            try:
                batch = source.fetch(query_id)
                emit("fetch_source", source=source.name, n=len(batch), ok=True)
                return batch
            except Exception as exc:
                logger.warning("%s failed: %s", source.name, exc)
                emit("fetch_source", source=source.name, n=0, ok=False, error=str(exc))
                return []

        # Sources are independent hosts — fetch in parallel. One dead
        # source logs and the rest continue (isolation preserved).
        from concurrent.futures import ThreadPoolExecutor

        collected: list[Signal] = []
        workers = min(len(srcs), 4) if srcs else 0
        if workers:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for batch in pool.map(_one, srcs):
                    collected.extend(batch)
        unique = dedupe_by_url(collected)
        if persist:
            from db import upsert_signals

            upsert_signals(unique)
        return unique
    finally:
        if owns_client:
            client.close()
