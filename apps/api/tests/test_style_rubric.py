"""Style rubric wiring — dimension scores, cliche blacklist, mode-diverse variants."""

from __future__ import annotations

from boxes.judge import StyleScore
from models import Concept, Draft


def _draft(caption: str) -> Draft:
    return Draft(
        draft_id="d-style",
        brief_id="b1",
        caption=caption,
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=1,
    )


def _concept() -> Concept:
    return Concept(
        concept_id="con_style",
        brief_id="b1",
        angle="humidity barrier",
        persona="AC-commute millennial",
        claim_safe_pain="post-AC tightness",
        channel="instagram",
        indic_register="hinglish",
        hook="Humidity ho, skin tight feel.",
        idea="Monsoon commute tightness.",
    )


def test_judge_returns_dimension_scores_and_style_verdict() -> None:
    from boxes.judge import run_judge

    result = run_judge(_draft("Wash your face tonight. 2% retinal, visibly calmer in 8 weeks."), claims=[])
    assert result.style is not None
    assert isinstance(result.style, StyleScore)
    dims = result.style.dimensions
    expected = {
        "hook_strength",
        "rhythm_economy",
        "specificity",
        "emotional_truth",
        "brand_fit",
    }
    assert set(dims) == expected
    assert all(1 <= v <= 5 for v in dims.values())
    assert result.style.verdict in ("PASS", "REWRITE")
    if result.style.verdict == "REWRITE":
        assert result.style.one_line_fix


def test_judge_rewrite_verdict_carries_one_line_fix() -> None:
    from boxes.judge import run_judge

    weak = "Introducing Hydro Boost. It is really very nice for your routine."
    result = run_judge(_draft(weak), claims=[])
    assert result.style is not None
    assert result.style.verdict == "REWRITE"
    assert result.style.one_line_fix
    # Compliance verdict stays independent of craft scoring.
    assert result.verdict == "PASS"
    assert any("style rubric" in row for row in result.reasons)


def test_craft_cliche_blacklist_fires_without_chat() -> None:
    from boxes.craft import review_craft
    from boxes.rubric import find_cliches

    hits = find_cliches("Glow like never before — unleash your inner game-changer.")
    assert len(hits) >= 3
    out = review_craft(
        _draft("Glow like never before with our elevate your skincare ritual.\n\nDermatologist tested."),
        chat=None,
    )
    assert out.verdict == "FAIL"
    assert any("blacklist" in row for row in out.reasons)
    assert out.dimensions and all(1 <= v <= 5 for v in out.dimensions.values())


def test_copywriter_generates_distinct_rubric_modes_when_chat_available() -> None:
    """Mocked chat (no network): three captions must come back in three modes."""
    from boxes.copywriter import CopyOut, run_copywriter
    from boxes.rubric import MODES

    captions_by_mode = {
        "imperative-compression": "Cleanse tonight. Even tired. Hydro Boost after — dermatologist tested.",
        "peer-voice-intimate": "ac day, tight skin, same story na. hydro boost on the night shelf. dermatologist tested.",
        "describe-dont-promise": "A gel-cream applied after cleansing: Hydro Boost, dermatologist tested, matte by morning.",
    }
    order = list(MODES)

    class ModeChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            assert schema is CopyOut
            # The prompt must carry the rubric voice + the three named modes.
            assert "<rubric>" in user
            for mode in MODES:
                assert mode in user
            return CopyOut(captions=[captions_by_mode[m] for m in order])

    drafts = run_copywriter(_concept(), round=1, chat=ModeChat())
    texts = [d.caption.lower() for d in drafts]
    assert len(set(texts)) >= 2
    for mode, caption in captions_by_mode.items():
        key = caption.lower()
        assert any(item.startswith(key) for item in texts), f"missing {mode} variant"


def test_strategist_prompt_carries_rubric_voice_and_exemplars() -> None:
    import inspect

    from boxes import strategist

    source = inspect.getsource(strategist)
    assert "<rubric>" in source
    assert "RUBRIC_VOICE" in source
    assert "Nike imperative compression" in source
    assert "peer voice" in source.lower()
    assert "poetry-line + proof-line" in source


# --- Rubric v2 (docs/bar/copy-bar.md §B1/B2) — deterministic scorer upgrades ---


def test_rubric_v2_overlong_first_line_caps_hook_strength() -> None:
    """B1: first line >8 words OR >60 chars → hook_strength capped at 3."""
    from boxes.rubric import score_dimensions

    long_hook = (
        "Ninety percent humidity and my skin still felt tight by four in the "
        "afternoon on the late train. One gel step changed that."
    )
    dims = score_dimensions(long_hook)
    assert dims["hook_strength"] <= 3

    # Same body, but a tight first sentence: hook earns its 5 again.
    tight_hook = (
        "Tight skin by 4pm, ninety percent humidity. One gel step changed that."
    )
    assert score_dimensions(tight_hook)["hook_strength"] == 5


def test_rubric_v2_brand_or_announce_in_first_line_caps_hook_at_two() -> None:
    """B1: a first line that LEADS with the brand name or 'introducing'/'say
    hello' → hook_strength <=2, and the one_line_fix names the problem.
    Mid-sentence product mentions stay safe ('Cleanse. Then Hydro Boost.')."""
    from boxes.rubric import score_dimensions, style_verdict

    for caption in (
        "Hydro Boost is all you need tonight.",
        "Neutrogena presents your clearest season.",
        "Say hello to moisture that lasts.",
        "Introducing the gel everyone asked for.",
    ):
        dims = score_dimensions(caption)
        assert dims["hook_strength"] <= 2, caption
        verdict, _avg, fix = style_verdict(dims)
        assert verdict == "REWRITE"
        assert fix and ("brand" in fix.lower() or "introducing" in fix.lower())

    # Product named after the pivot of the first line does NOT cap the hook.
    assert score_dimensions("Night: double cleanse, then Hydro Boost.")[
        "hook_strength"
    ] == 5


def test_rubric_v2_excited_announce_forces_rewrite_regardless_of_average() -> None:
    """B2: 'we're excited'/'we are excited' anywhere → emotional_truth <=2 and
    REWRITE even when every other dimension is strong."""
    from boxes.rubric import score_dimensions, style_verdict

    # Hook is clean and scores 5; only the mid-caption announce voice fails.
    excited = (
        "Our gel survived ninety percent humidity in testing. "
        "We're excited to share the 72-hour proof."
    )
    dims = score_dimensions(excited)
    assert dims["hook_strength"] == 5  # failure is NOT the hook this time
    assert dims["emotional_truth"] <= 2
    verdict, avg, fix = style_verdict(dims)
    assert verdict == "REWRITE"
    assert fix  # worst dim carries a fix even at a passing average
    assert avg >= 3.8  # REWRITE happens regardless of the average


def test_rubric_v2_excited_announce_matches_curly_apostrophe() -> None:
    from boxes.rubric import score_dimensions

    dims = score_dimensions("We\u2019re excited to announce our new moisturizer!")
    assert dims["emotional_truth"] <= 2
