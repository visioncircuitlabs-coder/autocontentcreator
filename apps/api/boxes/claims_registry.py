"""Claims Registry — every benefit claim usable in copy, with evidence.

Each row carries a source citation (source_url), a review/expiry date
(review_by) and an approval status. A draft may only use a benefit phrase
that is present in this registry AND status == 'approved' AND not past its
review_by date. No LLM anywhere in this path.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from models import RegistryClaim

DEFAULT_REGISTRY_PATH = (
    Path(__file__).resolve().parent.parent / "fixtures" / "neutrogena" / "claims.json"
)


def load_registry(path: Path | None = None) -> list[RegistryClaim]:
    """Load registry rows from the fixture's 'registry' key."""
    path = path or DEFAULT_REGISTRY_PATH
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("registry fixture must be an object")
    rows = raw.get("registry") or []
    if not isinstance(rows, list):
        raise ValueError("fixture 'registry' must be a list")
    out: list[RegistryClaim] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        review = row.get("review_by")
        out.append(
            RegistryClaim(
                claim_id=str(row["claim_id"]),
                text=str(row["text"]),
                sku=str(row.get("sku") or "*"),
                market=str(row.get("market") or "IN"),
                source_url=str(row["source_url"]),
                evidence_ref=str(row.get("evidence_ref") or ""),
                status=row["status"],
                review_by=datetime.fromisoformat(str(review)) if review else None,
                notes=str(row.get("notes") or ""),
            )
        )
    return out


def seed_registry(path: Path | None = None) -> int:
    """Push the fixture registry into SQLite. Idempotent. Returns row count."""
    from db import upsert_registry_claims

    rows = load_registry(path)
    upsert_registry_claims(rows)
    return len(rows)


def list_registry(path: Path | None = None) -> list[RegistryClaim]:
    """Registry rows from SQLite; seeds from the fixture on first read."""
    from db import list_registry_claims

    if not list_registry_claims():
        seed_registry(path)
    return list_registry_claims()


def is_expired(claim: RegistryClaim, *, today: date | None = None) -> bool:
    """True when the claim's review date has passed and it must not be used."""
    if claim.review_by is None:
        return False
    day = today or datetime.now(timezone.utc).date()
    return claim.review_by.date() < day


def usable(claim: RegistryClaim, *, today: date | None = None) -> bool:
    """A claim may appear in copy only when approved, cited, and in its review window."""
    return (
        claim.status == "approved"
        and bool(claim.source_url.strip())
        and not is_expired(claim, today=today)
    )


def registry_phrases(path: Path | None = None) -> dict[str, list[str]]:
    """claim_id -> matchable phrases (text + fixture lookalikes)."""
    path = path or DEFAULT_REGISTRY_PATH
    raw = json.loads(path.read_text(encoding="utf-8"))
    phrases: dict[str, list[str]] = {}
    for row in raw.get("registry") or []:
        if not isinstance(row, dict) or not row.get("claim_id"):
            continue
        cid = str(row["claim_id"])
        items = [str(row.get("text") or "")]
        items.extend(str(p) for p in (row.get("lookalikes") or []) if p)
        phrases[cid] = [p for p in items if p.strip()]
    return phrases
