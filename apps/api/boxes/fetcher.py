from __future__ import annotations

import logging

import httpx

from adapters.common import DEFAULT_QUERY_ID, REQUEST_TIMEOUT, USER_AGENT, normalize_url
from adapters.gdelt import GdeltSource
from adapters.news_rss import NewsRssSource, extra_rss_sources
from adapters.reddit_json import RedditJsonSource
from models import Signal
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
    query_id: str = DEFAULT_QUERY_ID,
    *,
    sources: list[TrendSource] | None = None,
    client: httpx.Client | None = None,
    persist: bool = True,
) -> list[Signal]:
    """Collect free-source signals. One dead source logs and the rest continue."""
    owns_client = client is None
    client = client or build_client()
    try:
        srcs = sources if sources is not None else default_sources(client)
        collected: list[Signal] = []
        for source in srcs:
            try:
                collected.extend(source.fetch(query_id))
            except Exception as exc:
                logger.warning("%s failed: %s", source.name, exc)
        unique = dedupe_by_url(collected)
        if persist:
            from db import upsert_signals

            upsert_signals(unique)
        return unique
    finally:
        if owns_client:
            client.close()
