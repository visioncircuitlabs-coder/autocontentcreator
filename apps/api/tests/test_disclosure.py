"""Disclosure formatter (G7) — per-market paid-post labels. No LLM."""

from __future__ import annotations

from models import Draft

# ---------------------------------------------------------------------------
# Unit: label vocabulary
# ---------------------------------------------------------------------------


def test_label_vocabulary_recognized() -> None:
    from boxes.disclosure import has_paid_label

    for label in ("#ad", "Sponsored", "Paid partnership", "Collab"):
        assert has_paid_label(f"{label}\n\nNice gel day.", "IN"), label


def test_unknown_text_is_not_a_label() -> None:
    from boxes.disclosure import has_paid_label

    assert not has_paid_label("My honest routine, no sponsor here.", "IN")


def test_regional_labels_per_market() -> None:
    from boxes.disclosure import has_paid_label

    assert has_paid_label("Werbung: gel day.", "EU")
    assert has_paid_label("Publicité — gel day.", "EU")
    # Label vocabulary is a shared superset: any approved label counts in
    # any market; placement rules are what differ per market.
    assert has_paid_label("Werbung: gel day.", "US")


# ---------------------------------------------------------------------------
# Unit: placement rules
# ---------------------------------------------------------------------------


def test_missing_label_fails() -> None:
    from boxes.disclosure import disclosure_violations

    reasons = disclosure_violations("Soft light on a Monday. Gel step.", "IN")
    assert reasons and "missing" in reasons[0]


def test_label_in_first_two_lines_passes() -> None:
    from boxes.disclosure import disclosure_violations

    ok = disclosure_violations("#ad\n\nMonsoon humidity, meet Hydro Boost.", "IN")
    assert ok == []
    ok2 = disclosure_violations(
        "Longer opening line about the weather.\nSponsored — gel saves the day.",
        "US",
    )
    assert ok2 == []


def test_buried_in_hashtag_cluster_fails() -> None:
    from boxes.disclosure import disclosure_violations

    caption = (
        "Soft light on a Monday and my desk plant agrees.\n"
        "One gel step before the commute.\n\n"
        "#skincare #monsoon #ad #hydrated #routine"
    )
    reasons = disclosure_violations(caption, "IN")
    assert reasons and "hashtag" in reasons[0].lower()


def test_label_after_second_line_but_not_hashtags_fails() -> None:
    from boxes.disclosure import disclosure_violations

    caption = (
        "Line one of a meandering caption.\n"
        "Line two still setting the scene.\n"
        "Line three finally says Sponsored."
    )
    reasons = disclosure_violations(caption, "US")
    assert reasons and "first two lines" in reasons[0]


# ---------------------------------------------------------------------------
# Unit: deterministic injection
# ---------------------------------------------------------------------------


def test_ensure_disclosure_places_label_first() -> None:
    from boxes.disclosure import disclosure_violations, ensure_disclosure

    out = ensure_disclosure("Soft light. One gel step.\n\n#ad #skincare", "IN")
    assert out.startswith("#ad")
    assert "#ad #skincare" not in out  # old buried token removed
    assert disclosure_violations(out, "IN") == []


def test_ensure_disclosure_is_idempotent() -> None:
    from boxes.disclosure import ensure_disclosure

    once = ensure_disclosure("Soft light. One gel step.", "IN")
    twice = ensure_disclosure(once, "IN")
    assert once == twice


# ---------------------------------------------------------------------------
# Integration: hard_rules paid branch is market-aware
# ---------------------------------------------------------------------------


def _draft(caption: str) -> Draft:
    return Draft(
        draft_id="d-disc",
        brief_id="b1",
        caption=caption,
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=1,
    )


def test_paid_without_any_label_still_flagged() -> None:
    from boxes.hard_rules import run_hard_rules

    reasons = run_hard_rules(_draft("Soft light on a Monday."), organic=False)
    assert any("#ad" in r.lower() for r in reasons)
    assert any("missing" in r.lower() for r in reasons)


def test_paid_buried_label_now_fails_rules() -> None:
    from boxes.hard_rules import run_hard_rules

    caption = (
        "Soft light on a Monday.\nGel step before the commute.\n\n"
        "#skincare #ad #monsoon"
    )
    reasons = run_hard_rules(_draft(caption), organic=False, market="IN")
    assert any("hashtag" in r.lower() for r in reasons)


def test_paid_well_placed_label_passes() -> None:
    from boxes.hard_rules import run_hard_rules

    caption = "#ad\n\nSoft light on a Monday. One gel step before the commute."
    assert run_hard_rules(_draft(caption), organic=False, market="IN") == []


def test_organic_mode_unaffected_by_disclosure_checks() -> None:
    from boxes.hard_rules import run_hard_rules

    caption = (
        "Soft light on a Monday.\nGel step before the commute.\n\n"
        "#skincare #ad #monsoon"
    )
    reasons = run_hard_rules(_draft(caption), organic=True, market="IN")
    assert any("#ad" in r.lower() or "organic" in r.lower() for r in reasons)


# ---------------------------------------------------------------------------
# Integration: loop converges a paid draft without burning rewrite rounds
# ---------------------------------------------------------------------------


def test_loop_paid_run_converges_with_label_placed() -> None:
    from boxes.hard_rules import load_disclaimer
    from boxes.loop import run_loop

    rewrites: list[list[str]] = []

    def passthrough(draft: Draft, reasons: list[str]) -> Draft:
        rewrites.append(list(reasons))
        return draft

    caption = (
        "Tight skin after the AC all day.\nHydro Boost at night — "
        f"dermatologist tested.\n\n{load_disclaimer()}\n\n#skincare #ad"
    )
    out = run_loop(
        _draft(caption),
        max_rounds=3,
        rewriter=passthrough,
        organic=False,
        market="IN",
    )
    assert out.caption.startswith("#ad"), out.caption
    assert out.rules == [], out.rules
