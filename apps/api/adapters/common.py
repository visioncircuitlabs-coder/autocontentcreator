from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from html import unescape
from typing import Literal

from models import Signal

USER_AGENT = "ContentMachineDemo/0.1"
DEFAULT_QUERY_ID = "skincare_in"
MARKET = "IN"
SNIPPET_MAX = 500
REQUEST_TIMEOUT = 20.0

SourceName = Literal["gdelt", "news_rss", "reddit", "rss"]

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

LANG_MAP = {
    "english": "en",
    "en": "en",
    "hindi": "hi",
    "hi": "hi",
    "tamil": "ta",
    "ta": "ta",
    "spanish": "es",
    "french": "fr",
}


def request_headers(*, accept: str = "*/*") -> dict[str, str]:
    return {"User-Agent": USER_AGENT, "Accept": accept}


def normalize_url(url: str) -> str:
    return (url or "").strip()


def signal_id_for(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()


def clip_text(text: str, limit: int = SNIPPET_MAX) -> str:
    cleaned = _WS_RE.sub(" ", _TAG_RE.sub(" ", unescape(text or ""))).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def lang_code(raw: str | None) -> str:
    if not raw:
        return "en"
    key = raw.strip().lower()
    if key in LANG_MAP:
        return LANG_MAP[key]
    if len(key) == 2 and key.isalpha():
        return key
    return "en"


def parse_gdelt_seendate(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%dT%H%M%S"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def parse_unix(ts: float | int | str | None) -> datetime | None:
    if ts is None or ts == "":
        return None
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def build_signal(
    *,
    source: SourceName,
    url: str,
    title: str,
    snippet: str,
    query_id: str,
    happened_at: datetime | None = None,
    lang: str = "en",
    raw_ref: str = "",
    seen_at: datetime | None = None,
) -> Signal | None:
    url = normalize_url(url)
    title = clip_text(title, 300)
    if not url or not title:
        return None
    seen = aware(seen_at) or datetime.now(timezone.utc)
    text = clip_text(snippet) or title
    return Signal(
        signal_id=signal_id_for(url),
        seen_at=seen,
        happened_at=aware(happened_at),
        source=source,
        url=url,
        title=title,
        snippet=text,
        lang=lang_code(lang),
        market=MARKET,
        query_id=query_id,
        raw_ref=(raw_ref or "")[:200],
    )
