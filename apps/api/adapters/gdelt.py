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
from boxes.brand_pack import load_brand_pack

logger = logging.getLogger(__name__)

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_QUERY = "neutrogena OR skincare"


def _articles_or_fail(payload: object) -> list[dict]:
    """HTTP 200 is not success if GDELT sent an error or no article list."""
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        err = payload.get("error")
        if err:
            raise RuntimeError(f"GDELT error: {err}")
        if "articles" not in payload:
            raise RuntimeError("GDELT response missing article list")
        raw = payload.get("articles")
        if not isinstance(raw, list):
            raise RuntimeError("GDELT article list is not a list")
        return [row for row in raw if isinstance(row, dict)]
    raise RuntimeError("GDELT returned unexpected JSON")


class GdeltSource:
    name = "gdelt"

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def fetch(self, query_id: str) -> list[Signal]:
        radar = load_brand_pack().get("radar") or {}
        query = str(radar.get("gdelt") or GDELT_QUERY)
        response = self.client.get(
            GDELT_DOC_URL,
            params={
                "query": query,
                "mode": "ArtList",
                "maxrecords": "20",
                "format": "json",
            },
            headers=request_headers(accept="application/json"),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        if not response.content or not response.content.strip():
            raise RuntimeError("GDELT returned an empty body")
        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError("GDELT returned non-JSON") from exc

        articles = _articles_or_fail(payload)

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
