"""Learning loop v1 — past winners & rejection reasons back into the writer prompt.

Reads the track_record ledger (same tables feedback.py writes), distills:
- exemplars: APPROVED captions ranked by win rate (approvals / decisions per
  identical normalized caption text),
- anti-patterns: most common rejection reason strings.

Pure read-side + prompt block. Data-only output; jailbreak guards live in the
writer system prompt. Results are cached per process with a short TTL so bursty
factory runs do not re-query SQLite on every call.
"""

from __future__ import annotations

import re
import time
from collections import Counter

from db import list_track_record

CACHE_TTL = 300.0

_CACHE: dict[tuple[str, str], tuple[float, object]] = {}

_MAX_LINE = 240


def reset_learning_cache() -> None:
    """Drop cached exemplars/anti-patterns (tests, or a fresh factory run)."""
    _CACHE.clear()


def _cached(key: tuple[str, str], fn):
    now = time.monotonic()
    hit = _CACHE.get(key)
    if hit is not None and now - hit[0] < CACHE_TTL:
        return hit[1]
    value = fn()
    _CACHE[key] = (now, value)
    return value


def normalize_text(text: str) -> str:
    """Whitespace-collapsed, lowercased key for grouping identical captions."""
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _sku_ok(row_sku: str, sku_key: str) -> bool:
    sku_key = (sku_key or "").strip()
    row_sku = (row_sku or "").strip()
    return (not sku_key) or (not row_sku) or row_sku in (sku_key, "*")


def get_exemplars(sku: str | None = None, limit: int = 5) -> list[dict]:
    """Highest-win-rate approved captions.

    Win rate = approvals / total decisions for one identical normalized
    caption text. Rows with zero approvals never qualify. Ties break by
    approval count, then recency.
    """
    sku_key = (sku or "").strip()

    def compute() -> list[dict]:
        stats: dict[str, dict] = {}
        for row in list_track_record():
            verdict = (row.get("verdict") or "").strip().lower()
            if verdict not in ("approve", "reject"):
                continue
            caption = (row.get("caption") or "").strip()
            if not caption:
                continue
            if not _sku_ok(row.get("sku") or "", sku_key):
                continue
            key = normalize_text(caption)
            entry = stats.setdefault(
                key,
                {"caption": caption[:_MAX_LINE], "wins": 0, "decisions": 0, "last": ""},
            )
            decided_at = str(row.get("decided_at") or "")
            if decided_at > entry["last"]:
                entry["last"] = decided_at
                entry["caption"] = caption[:_MAX_LINE]
            entry["decisions"] += 1
            if verdict == "approve":
                entry["wins"] += 1
        pool = [entry for entry in stats.values() if entry["wins"] > 0]
        pool.sort(
            key=lambda e: (
                -(e["wins"] / e["decisions"]) if e["decisions"] else 0.0,
                -e["wins"],
                e["last"],
            ),
            reverse=False,
        )
        return [
            {"caption": e["caption"], "wins": e["wins"], "decisions": e["decisions"]}
            for e in pool[: max(1, int(limit))]
        ]

    return _cached(("exemplars", sku_key.lower()), compute)


def get_anti_patterns(limit: int = 5) -> list[str]:
    """Most common rejection reason strings (distilled reason preferred)."""
    limit = max(1, int(limit))

    def compute() -> list[str]:
        counter: Counter[str] = Counter()
        for row in list_track_record():
            if (row.get("verdict") or "").strip().lower() != "reject":
                continue
            reason = (row.get("distilled") or row.get("reason") or "").strip()
            if not reason:
                continue
            counter[normalize_text(reason)[:280]] += 1
        ranked = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
        return [reason for reason, _ in ranked[:limit]]

    return _cached(("anti", ""), compute)


def learning_block(
    sku: str | None = None,
    *,
    winners_limit: int = 5,
    avoid_limit: int = 5,
) -> tuple[str, int, int]:
    """`<winners>` + `<avoid>` prompt block. Returns (text, n_winners, n_avoid).

    Empty string when the ledger has nothing to teach yet — callers skip the
    tags entirely rather than shipping empty scaffolding.
    """
    winners = get_exemplars(sku=sku, limit=winners_limit)
    avoid = get_anti_patterns(limit=avoid_limit)
    if not winners and not avoid:
        return "", 0, 0
    parts: list[str] = []
    if winners:
        lines = "\n".join(
            f"- {w['caption']} [approved {w['wins']}/{w['decisions']} times]"
            for w in winners
        )
        parts.append(f"<winners>\n{lines}\n</winners>")
    if avoid:
        lines = "\n".join(f"- {reason}" for reason in avoid)
        parts.append(f"<avoid>\n{lines}\n</avoid>")
    return "\n".join(parts), len(winners), len(avoid)
