"""Hard Rules — banned tokens, organic #ad off, benefit disclaimer."""

from __future__ import annotations

from pathlib import Path

from models import Draft

DISCLAIMER = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "neutrogena"
    / "disclaimer.txt"
).read_text(encoding="utf-8").strip()


def _draft(caption: str, *, round: int = 1) -> Draft:
    return Draft(
        draft_id="d-rules",
        brief_id="b1",
        caption=caption,
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=round,
    )


def test_cures_fails_rules() -> None:
    from boxes.hard_rules import run_hard_rules

    reasons = run_hard_rules(_draft("This gel cures acne overnight."))
    assert reasons, "expected hard-rule failures"
    assert any("cures" in r.lower() for r in reasons)


def test_other_banned_tokens_fail() -> None:
    from boxes.hard_rules import run_hard_rules

    for token in ("heals", "best", "only", "guaranteed"):
        reasons = run_hard_rules(_draft(f"Our {token} formula for monsoon skin."))
        assert any(token in r.lower() for r in reasons), token


def test_ad_hashtag_fails_organic_demo() -> None:
    from boxes.hard_rules import run_hard_rules

    reasons = run_hard_rules(_draft("Soft light. #ad"))
    assert any("#ad" in r.lower() or "organic" in r.lower() for r in reasons)


def test_paid_placement_requires_ad() -> None:
    from boxes.hard_rules import run_hard_rules

    missing = run_hard_rules(_draft("Soft light on a Monday."), organic=False)
    assert any("#ad" in r.lower() for r in missing)
    ok = run_hard_rules(_draft("Soft light on a Monday. #ad"), organic=False)
    assert ok == []


def test_benefit_line_requires_fixture_disclaimer() -> None:
    from boxes.hard_rules import run_hard_rules

    bare = run_hard_rules(_draft("Hydro Boost hydrates skin through the monsoon."))
    assert any("disclaimer" in r.lower() for r in bare)

    with_disc = run_hard_rules(
        _draft(f"Hydro Boost hydrates skin through the monsoon.\n\n{DISCLAIMER}")
    )
    assert with_disc == []


def test_no_benefit_line_skips_disclaimer() -> None:
    from boxes.hard_rules import run_hard_rules

    assert run_hard_rules(_draft("Monday light. Soft skin mood.")) == []
