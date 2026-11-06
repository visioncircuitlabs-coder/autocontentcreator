"""Product Facts — compare copy to the claims library (do not ask 'is this legal?').

Fixture is an UNOFFICIAL DEMO — not Kenvue-approved.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Literal

from boxes.brand_pack import load_brand_pack
from models import Claim

logger = logging.getLogger(__name__)

DEFAULT_CLAIMS_PATH = None  # resolved live via load_brand_pack()

ClaimStatus = Literal["approved", "conditional", "forbidden"]


def _normalize(s: str) -> str:
    """Lowercase, collapse whitespace, unify dash variants for lookalike match."""
    s = s.lower()
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _pattern_for(phrase: str) -> re.Pattern[str]:
    """Exact phrase with flexible whitespace/dashes; word boundaries for short tokens."""
    norm = _normalize(phrase)
    # Escape then allow flexible whitespace / hyphen between words
    parts = re.split(r"[\s\-]+", norm)
    parts = [re.escape(p) for p in parts if p]
    if not parts:
        return re.compile(r"(?!)")  # never matches
    body = r"[\s\-]+".join(parts)
    # Word-ish boundaries so "heals" does not match inside "wheels"
    return re.compile(rf"(?<!\w){body}(?!\w)", re.IGNORECASE)


def load_claims(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or load_brand_pack()["claims_path"]
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("claims.json must be an object")
    claims = raw.get("claims") or []
    if not isinstance(claims, list):
        raise ValueError("claims.json 'claims' must be a list")
    return [c for c in claims if isinstance(c, dict)]


def load_claim_models(path: Path | None = None) -> list[Claim]:
    """Map fixture rows onto the shared Claim model (lookalikes stay on the raw dict)."""
    out: list[Claim] = []
    for row in load_claims(path):
        expires = row.get("expires_at")
        out.append(
            Claim(
                claim_id=str(row["claim_id"]),
                text=str(row["text"]),
                sku=str(row.get("sku") or "*"),
                market=str(row.get("market") or "IN"),
                evidence_ref=str(row.get("evidence_ref") or ""),
                status=row["status"],  # validated by Claim
                expires_at=expires,
            )
        )
    return out


def compare_claims(
    text: str,
    *,
    path: Path | None = None,
) -> list[dict[str, str]]:
    """Find claim phrases (exact + simple lookalike) in text.

    Returns list of {span, claim_id, status} in left-to-right order.
    Overlapping hits: longer / earlier phrase wins; one span per claim_id max.
    """
    if not text:
        return []

    rows = load_claims(path)
    candidates: list[tuple[int, int, str, str, str]] = []
    # (start, end, span, claim_id, status)

    for row in rows:
        claim_id = str(row.get("claim_id") or "")
        status = str(row.get("status") or "")
        if not claim_id or status not in ("approved", "conditional", "forbidden"):
            continue
        phrases = [str(row.get("text") or "")]
        phrases.extend(str(p) for p in (row.get("lookalikes") or []) if p)
        for phrase in phrases:
            if not phrase.strip():
                continue
            pat = _pattern_for(phrase)
            for m in pat.finditer(text):
                candidates.append((m.start(), m.end(), m.group(0), claim_id, status))

    # Prefer longer spans, then earlier start
    candidates.sort(key=lambda c: (-(c[1] - c[0]), c[0]))

    used_ranges: list[tuple[int, int]] = []
    seen_ids: set[str] = set()
    hits: list[tuple[int, dict[str, str]]] = []

    def overlaps(a: int, b: int) -> bool:
        for x, y in used_ranges:
            if a < y and b > x:
                return True
        return False

    for start, end, span, claim_id, status in candidates:
        if claim_id in seen_ids:
            continue
        if overlaps(start, end):
            continue
        seen_ids.add(claim_id)
        used_ranges.append((start, end))
        hits.append(
            (
                start,
                {"span": span, "claim_id": claim_id, "status": status},
            )
        )

    hits.sort(key=lambda h: h[0])
    return [h[1] for h in hits]
