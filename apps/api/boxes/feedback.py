"""Feedback Writer — reason required, distilled into Track Record the same day."""

from __future__ import annotations

from models import Decision, Draft
from db import get_brief, insert_track_record, list_track_record


def distill(reason: str) -> str:
    """Collapse whitespace. Demo has no Brand Brain write-back."""
    return " ".join((reason or "").split())[:280]


def write_feedback(decision: Decision, draft: Draft) -> dict:
    """Ledger row: draft + judge + named human + reason. Same day, no delay."""
    brief = get_brief(draft.brief_id) if draft.brief_id else None
    entry = {
        "draft_id": decision.draft_id,
        "decided_at": decision.decided_at.isoformat(),
        "user": decision.user,
        "verdict": decision.verdict,
        "reason": decision.reason,
        "distilled": distill(decision.reason),
        "caption": draft.caption or "",
        "judge": draft.judge,
        "sku": brief.sku if brief is not None else "",
        "market": brief.market if brief is not None else "",
        "flag_human": bool(draft.flag_human),
    }
    insert_track_record(entry)
    return entry


def load_track_examples(
    sku: str,
    market: str,
    n: int = 3,
) -> tuple[list[dict], list[dict]]:
    """3 wins + 3 losses for the brief pack. Empty is allowed."""
    sku_key = (sku or "").strip()
    market_key = (market or "").strip().upper()
    wins: list[dict] = []
    losses: list[dict] = []
    for row in list_track_record():
        row_sku = (row.get("sku") or "").strip()
        row_market = (row.get("market") or "").strip().upper()
        sku_ok = (not sku_key) or (not row_sku) or row_sku in (sku_key, "*")
        market_ok = (not market_key) or (not row_market) or row_market == market_key
        if not (sku_ok and market_ok):
            continue
        item = {
            "draft_id": row.get("draft_id"),
            "user": row.get("user"),
            "verdict": row.get("verdict"),
            "reason": row.get("reason"),
            "distilled": row.get("distilled"),
            "caption": (row.get("caption") or "")[:240],
            "decided_at": row.get("decided_at"),
        }
        if row.get("verdict") == "approve" and len(wins) < n:
            wins.append(item)
        elif row.get("verdict") == "reject" and len(losses) < n:
            losses.append(item)
        if len(wins) >= n and len(losses) >= n:
            break
    return wins, losses
