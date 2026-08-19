"""Review & Approve — named human, reason required. Not a publish button."""

from __future__ import annotations

from datetime import datetime, timezone

from boxes.feedback import write_feedback
from db import get_draft, insert_decision
from models import Decision

ALLOWED = {"approve", "reject"}


def decide(draft_id: str, user: str, verdict: str, reason: str) -> Decision:
    """Last yes/no on a draft. Reason is required. Does not publish."""
    who = (user or "").strip()
    why = (reason or "").strip()
    if not who:
        raise ValueError("A named person must approve or reject.")
    if not why:
        raise ValueError("A reason is required. Same miss should not survive twice.")
    if verdict not in ALLOWED:
        raise ValueError("Verdict must be approve or reject.")
    draft = get_draft(draft_id)
    if draft is None:
        raise ValueError("That draft is not in the queue.")
    decision = Decision(
        draft_id=draft_id,
        user=who,
        verdict=verdict,  # type: ignore[arg-type]
        reason=why,
        decided_at=datetime.now(timezone.utc),
    )
    insert_decision(decision)
    write_feedback(decision, draft)
    return decision
