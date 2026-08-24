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


# --- Learning v2: hard-ban memory -------------------------------------------

BANNED_CAPTION = "Night shift ends, gel goes on first. Dermatologist tested."


def _concept(brief_id: str = "brf_x"):
    from models import Concept

    return Concept(
        concept_id="con_learn",
        brief_id=brief_id,
        angle="humidity barrier",
        persona="AC-commute millennial",
        claim_safe_pain="post-AC tightness",
        channel="instagram",
        indic_register="hinglish",
        idea="Monsoon commute tightness, not a disease story.",
    )


def _reject_twice(caption: str, reason_1: str, reason_2: str) -> None:
    _record("dft_ban1", caption, "reject", "riya", reason_1)
    _record("dft_ban2", caption, "reject", "arjun", reason_2)
    learning.reset_learning_cache()


def test_hard_bans_after_two_same_category_rejects(desk_db):
    _reject_twice(BANNED_CAPTION, "off-brand: reads like an ad", "off-brand tone")
    bans = learning.get_hard_bans()
    match = [
        b
        for b in bans
        if b["normalized"] == learning.normalize_text(BANNED_CAPTION)
    ]
    assert match, "two same-category rejections must hard-ban the caption"
    assert match[0]["rejects"] == 2
    assert match[0]["category"] == "off-brand"


def test_single_or_mixed_category_rejects_do_not_ban(desk_db):
    _record("dft_ban3", BANNED_CAPTION, "reject", "riya", "off-brand tone")
    _record("dft_ban4", "Solo reject stays allowed.", "approve", "arjun", "fine")
    learning.reset_learning_cache()
    assert learning.get_hard_bans() == []

    _reject_twice(BANNED_CAPTION, "too long for a post", "drug claim vibes")
    assert learning.get_hard_bans() == [], "mixed categories must not hard-ban"


def test_third_generation_filters_banned_chat_candidate(desk_db):
    """Two rejects of the same caption -> the next generation attempt drops it."""
    from boxes.copywriter import CopyOut, run_copywriter

    _reject_twice(BANNED_CAPTION, "off-brand: reads like an ad", "off-brand tone")

    class StubbornChat:
        """Chat keeps returning the twice-rejected caption."""

        def complete_json(self, system, user, schema):
            assert schema is CopyOut
            return CopyOut(captions=[BANNED_CAPTION, "A", "B"])

    drafts = run_copywriter(_concept(), round=3, chat=StubbornChat())
    banned_key = learning.normalize_text(BANNED_CAPTION)
    produced = {learning.normalize_text(d.caption) for d in drafts}
    assert banned_key not in produced, "banned caption must be filtered"
    assert 2 <= len(drafts) <= 3, "templates must still fill the quota"


def test_template_output_skips_hard_banned_caption(desk_db):
    from boxes.copywriter import run_copywriter

    first = run_copywriter(_concept(), round=1)
    assert len(first) >= 2
    victim = first[0].caption

    _reject_twice(victim, "off-brand: reads like an ad", "off-brand again")
    second = run_copywriter(_concept(), round=2)

    produced = {learning.normalize_text(d.caption) for d in second}
    assert learning.normalize_text(victim) not in produced
    assert len(second) >= 2


# --- Learning v2: degradation provenance ------------------------------------


class _NoImpliedChat:
    def complete_json(self, system, user, schema):
        from boxes.judge import ImpliedClaimOut

        return ImpliedClaimOut(implied=False)


def test_judge_flags_missing_chat_as_degradation():
    from boxes.judge import run_judge

    result = run_judge(_draft("dft_deg1", "Gel first. Panic later."), [], chat=None)
    assert result.produced_under_degradation is True
    payload = result.model_dump()
    assert payload["produced_under_degradation"] is True


def test_judge_flags_open_breaker_as_degradation():
    from harness.breaker import CHAT_BREAKER
    from boxes.judge import run_judge

    for _ in range(CHAT_BREAKER.threshold):
        CHAT_BREAKER.record_failure()
    try:
        assert CHAT_BREAKER.state != "closed"
        result = run_judge(
            _draft("dft_deg2", "Gel first. Panic later."), [], chat=_NoImpliedChat()
        )
        assert result.produced_under_degradation is True
    finally:
        CHAT_BREAKER.reset()


def test_judge_with_chat_and_closed_breaker_is_not_degraded():
    from harness.breaker import CHAT_BREAKER
    from boxes.judge import run_judge

    CHAT_BREAKER.reset()
    result = run_judge(
        _draft("dft_deg3", "Gel first. Panic later."), [], chat=_NoImpliedChat()
    )
    assert CHAT_BREAKER.state == "closed"
    assert result.produced_under_degradation is False
