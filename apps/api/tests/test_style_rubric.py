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
