"""Loop short-circuit: hard-rule failure must skip judge+craft chat calls."""

from __future__ import annotations

from models import Draft
from boxes.loop import run_loop


class CountingChat:
    """Records how many times the model is consulted."""

    def __init__(self) -> None:
        self.calls = 0

    def complete_json(self, system: str, user: str, schema: type):
        self.calls += 1
        # minimal plausible JSON for whatever schema asks
        return schema.model_validate_json("{}")


def _draft_with_banned_word() -> Draft:
    return Draft(
        draft_id="dft_test",
        brief_id="brf_test",
        caption="This gel cures acne overnight.",
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=0,
    )


def test_rule_failure_skips_judge_and_craft_chat():
    chat = CountingChat()
    out = run_loop(_draft_with_banned_word(), max_rounds=2, chat=chat)
    # Round 1 short-circuits: judge/craft never see the dirty caption.
    # Total = 1 rewrite call (round 1) + judge + craft on the fixed round-2
    # caption = 3. The old path would burn 5 (judge+craft on the dirty
    # round-1 caption too). Assert the saving explicitly.
    assert chat.calls <= 3
    assert not (out.rules or [])


def test_clean_draft_still_goes_through_full_gate():
    from boxes.product_facts import load_claim_models

    good = Draft(
        draft_id="dft_ok",
        brief_id="brf_ok",
        caption=(
            "Hydro Boost is dermatologist tested.\n\n"
            "Always patch-test. Consult a dermatologist for skin concerns."
        ),
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=0,
    )
    chat = CountingChat()
    out = run_loop(good, max_rounds=3, claims=load_claim_models(), chat=chat)
    assert not (out.rules or [])
    # judge + craft each consult the model at least once on a clean draft
    assert chat.calls >= 1
