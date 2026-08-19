from __future__ import annotations

import logging

import httpx

from adapters.common import (
    REQUEST_TIMEOUT,
    build_signal,
    parse_unix,
    request_headers,
)
from models import Signal

logger = logging.getLogger(__name__)

SUBREDDIT_URLS = (
    "https://www.reddit.com/r/SkincareAddiction/hot.json?limit=15",
    "https://www.reddit.com/r/IndianSkincareAddicts/hot.json?limit=15",
)


class RedditJsonSource:
    name = "reddit"

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def fetch(self, query_id: str) -> list[Signal]:
        signals: list[Signal] = []
        errors = 0
        for url in SUBREDDIT_URLS:
            try:
                signals.extend(self._fetch_one(url, query_id))
            except Exception as exc:
                errors += 1
                logger.warning("reddit feed %s failed: %s", url, exc)
        if errors == len(SUBREDDIT_URLS) and not signals:
            raise RuntimeError("all reddit feeds failed")
        return signals

    def _fetch_one(self, url: str, query_id: str) -> list[Signal]:
        response = self.client.get(
            url,
            headers=request_headers(accept="application/json"),
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )
        response.raise_for_status()
        payload = response.json()
        children = []
        if isinstance(payload, dict):
            children = (payload.get("data") or {}).get("children") or []
        signals: list[Signal] = []
        for child in children:
            if not isinstance(child, dict):
                continue
            data = child.get("data") or {}
            if not isinstance(data, dict):
                continue
            post_id = str(data.get("id") or "")
            permalink = str(data.get("permalink") or "")
            if permalink.startswith("http"):
                post_url = permalink
            elif permalink:
                post_url = "https://www.reddit.com" + permalink
            else:
                post_url = str(data.get("url") or "")
            title = str(data.get("title") or "")
            snippet = str(data.get("selftext") or "")
            signal = build_signal(
                source="reddit",
                url=post_url,
                title=title,
                snippet=snippet,
                query_id=query_id,
                happened_at=parse_unix(data.get("created_utc")),
                lang="en",
                raw_ref=f"t3_{post_id}" if post_id else "",
            )
            if signal is not None:
                signals.append(signal)
        return signals
