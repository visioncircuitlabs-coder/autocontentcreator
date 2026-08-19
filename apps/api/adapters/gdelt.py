from __future__ import annotations

import logging

import httpx

from adapters.common import (
    REQUEST_TIMEOUT,
    build_signal,
    parse_gdelt_seendate,
    request_headers,
)
from models import Signal

logger = logging.getLogger(__name__)

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_QUERY = "neutrogena OR skincare"


class GdeltSource:
    name = "gdelt"

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def fetch(self, query_id: str) -> list[Signal]:
        response = self.client.get(
            GDELT_DOC_URL,
            params={
                "query": GDELT_QUERY,
                "mode": "ArtList",
                "maxrecords": "20",
                "format": "json",
            },
            headers=request_headers(accept="application/json"),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError("GDELT returned non-JSON") from exc

        articles: list[dict] = []
        if isinstance(payload, dict):
            raw = payload.get("articles") or []
            if isinstance(raw, list):
                articles = [row for row in raw if isinstance(row, dict)]
        elif isinstance(payload, list):
            articles = [row for row in payload if isinstance(row, dict)]

        signals: list[Signal] = []
        for row in articles:
            url = str(row.get("url") or "")
            title = str(row.get("title") or "")
            domain = str(row.get("domain") or "")
            snippet = title if not domain else f"{title} ({domain})"
            signal = build_signal(
                source="gdelt",
                url=url,
                title=title,
                snippet=snippet,
                query_id=query_id,
                happened_at=parse_gdelt_seendate(row.get("seendate")),
                lang=str(row.get("language") or "en"),
                raw_ref=domain,
            )
            if signal is not None:
                signals.append(signal)
        logger.info("gdelt fetched %s articles", len(signals))
        return signals
