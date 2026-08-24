"""Learning loop tests: exemplar extraction, prompt block, wiring."""

from __future__ import annotations

import pytest

from boxes import learning
from boxes.feedback import write_feedback
from db import init_db, upsert_draft


@pytest.fixture()
def desk_db(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "learn.db"))
    init_db()
    learning.reset_learning_cache()
    yield
    learning.reset_learning_cache()


def _draft(draft_id: str, caption: str):
    from models import Draft

    return Draft(
        draft_id=draft_id,
        brief_id="brf_x",
        caption=caption,
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=1,
    )


def _record(draft_id, caption, verdict, user, reason):
    """Route through the real feedback path so track_record is populated."""
    from datetime import datetime, timezone

    from models import Decision

    decision = Decision(
        draft_id=draft_id,
        user=user,
        verdict=verdict,
        reason=reason,
        decided_at=datetime.now(timezone.utc),
    )
    write_feedback(decision, _draft(draft_id, caption))


def test_exemplars_rank_approved_by_win_rate(desk_db):
    _record("dft_a", "Gel first. Panic later.", "approve", "riya", "on-voice")
    _record("dft_b", "Humidity is a liar. Gel first.", "reject", "arjun", "off-brand")
    rows = learning.get_exemplars(limit=5)
    assert rows, "approved captions must surface as exemplars"
    assert rows[0]["caption"] == "Gel first. Panic later."
    assert all(r["wins"] >= 1 for r in rows)


def test_anti_patterns_collect_rejection_reasons(desk_db):
    _record("dft_c", "Best moisturizer ever!", "reject", "riya", "banned superlative")
    anti = learning.get_anti_patterns(limit=5)
    assert any("superlative" in a for a in anti)


def test_learning_block_empty_when_no_history():
    text, w, a = learning.learning_block()
    assert text == ""
    assert (w, a) == (0, 0)


def test_block_contains_winners_and_avoid_tags(desk_db):
    _record("dft_d", "Cleanse. Then Hydro Boost.", "approve", "riya", "tight")
    _record("dft_e", "Cures everything!", "reject", "arjun", "drug claim")
    text, w, a = learning.learning_block()
    assert "<winners>" in text and "<avoid>" in text
    assert w >= 1 and a >= 1
