from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import feedparser
import httpx
import yaml

from adapters.common import (
    REQUEST_TIMEOUT,
    SourceName,
    build_signal,
    request_headers,
)
from models import Signal

logger = logging.getLogger(__name__)

GOOGLE_NEWS_URL = (
    "https://news.google.com/rss/search?q=skincare+OR+neutrogena&hl=en-IN"
)
# Google News RSS often returns ~100 items; keep parity with GDELT maxrecords=20.
RSS_MAX = 20
SOURCES_YML = Path(__file__).resolve().parent.parent / "fixtures" / "sources.yml"


class NewsRssSource:
    name = "news_rss"

    def __init__(self, client: httpx.Client, url: str = GOOGLE_NEWS_URL) -> None:
        self.client = client
        self.url = url

    def fetch(self, query_id: str) -> list[Signal]:
        return fetch_rss(
            self.client,
            url=self.url,
            source="news_rss",
            query_id=query_id,
        )


class ExtraRssSource:
    name = "rss"

    def __init__(self, client: httpx.Client, url: str, query_id: str = "rss") -> None:
        self.client = client
        self.url = url
        self.query_id = query_id

    def fetch(self, query_id: str) -> list[Signal]:
        pack = self.query_id or query_id
        return fetch_rss(self.client, url=self.url, source="rss", query_id=pack)


def fetch_rss(
    client: httpx.Client,
    *,
    url: str,
    source: SourceName,
    query_id: str,
) -> list[Signal]:
    response = client.get(
        url,
        headers=request_headers(accept="application/rss+xml, application/xml, text/xml, */*"),
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
    )
    response.raise_for_status()
    parsed = feedparser.parse(response.content)
    signals: list[Signal] = []
    for entry in parsed.entries[:RSS_MAX]:
        link = str(entry.get("link") or "")
        title = str(entry.get("title") or "")
        # Title/snippet/url only. Never keep content:encoded / full HTML.
        snippet = str(entry.get("summary") or entry.get("description") or "")
        guid = str(entry.get("id") or "")
        happened = None
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            try:
                happened = datetime(*published[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                happened = None
        raw_ref = guid if guid and not guid.startswith("http") else ""
        signal = build_signal(
            source=source,
            url=link,
            title=title,
            snippet=snippet,
            query_id=query_id,
            happened_at=happened,
            lang="en",
            raw_ref=raw_ref,
        )
        if signal is not None:
            signals.append(signal)
    logger.info("%s fetched %s items from %s", source, len(signals), url)
    return signals


def extra_rss_sources(
    client: httpx.Client,
    path: Path | None = None,
) -> list[ExtraRssSource]:
    yml = path or SOURCES_YML
    if not yml.is_file():
        return []
    try:
        data: Any = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        logger.warning("sources.yml unreadable: %s", exc)
        return []
    feeds = data.get("rss") if isinstance(data, dict) else None
    if not isinstance(feeds, list):
        return []
    sources: list[ExtraRssSource] = []
    for feed in feeds:
        if not isinstance(feed, dict):
            continue
        feed_url = str(feed.get("url") or "").strip()
        if not feed_url:
            continue
        sources.append(
            ExtraRssSource(
                client,
                url=feed_url,
                query_id=str(feed.get("query_id") or "rss"),
            )
        )
    return sources
