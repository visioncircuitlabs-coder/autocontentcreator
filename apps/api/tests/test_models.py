from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models import Claim, Decision, Signal


def test_claim_status_rejects_unknown() -> None:
    with pytest.raises(ValidationError):
        Claim(
            claim_id="c1",
            text="Hydrates skin",
            sku="SKU-1",
            market="IN",
            evidence_ref="ev1",
            status="maybe",  # type: ignore[arg-type]
            expires_at=None,
        )


def test_claim_status_accepts_allowed() -> None:
    claim = Claim(
        claim_id="c1",
        text="Hydrates skin",
        sku="SKU-1",
        market="IN",
        evidence_ref="ev1",
        status="approved",
        expires_at=None,
    )
    assert claim.status == "approved"


def test_signal_requires_url() -> None:
    with pytest.raises(ValidationError):
        Signal(
            signal_id="s1",
            seen_at=datetime.now(timezone.utc),
            happened_at=None,
            source="gdelt",
            title="t",
            snippet="sn",
            query_id="q1",
        )  # type: ignore[call-arg]


def test_decision_requires_reason() -> None:
    with pytest.raises(ValidationError):
        Decision(
            draft_id="d1",
            user="alice",
            verdict="approve",
            reason="",
            decided_at=datetime.now(timezone.utc),
        )


def test_decision_accepts_nonempty_reason() -> None:
    decision = Decision(
        draft_id="d1",
        user="alice",
        verdict="reject",
        reason="off-brand tone",
        decided_at=datetime.now(timezone.utc),
    )
    assert decision.reason == "off-brand tone"
    assert decision.verdict == "reject"


def test_init_db_creates_tables(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "demo.db"
    monkeypatch.setenv("SQLITE_PATH", str(db_path))

    from db import init_db

    init_db()

    import sqlite3

    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    finally:
        conn.close()

    names = {r[0] for r in rows}
    assert names >= {
        "signals",
        "scores",
        "reports",
        "claims",
        "drafts",
        "decisions",
    }
