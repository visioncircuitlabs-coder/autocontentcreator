"""Improvement loop — max 3 rounds, then flag a human."""

from __future__ import annotations

from models import Draft


def _draft(caption: str, *, round: int = 1) -> Draft:
    return Draft(
        draft_id="d-loop",
        brief_id="b1",
        caption=caption,
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=round,
    )


def _flagged(draft: Draft) -> bool:
    if getattr(draft, "flag_human", False):
        return True
    judge = draft.judge or {}
    return bool(judge.get("flag_human"))


def test_loop_stops_at_3() -> None:
    from boxes.loop import run_loop

    calls = {"n": 0}

    def stubborn(draft: Draft, reasons: list[str]) -> Draft:
        calls["n"] += 1
        assert reasons, "rewriter must receive fail reasons"
        return draft.model_copy(update={"caption": "This cream cures everything."})

    out = run_loop(
        _draft("This gel cures acne overnight."),
        max_rounds=3,
        rewriter=stubborn,
    )
    assert out.round == 3
    assert _flagged(out)
    assert calls["n"] == 2
    assert calls["n"] < 3 or out.round == 3


def test_loop_default_rewrite_can_pass() -> None:
    from boxes.loop import run_loop

    out = run_loop(_draft("This gel cures acne overnight."))
    assert out.round <= 3
    assert not _flagged(out)
    assert out.rules == []
    judge = out.judge or {}
    assert judge.get("verdict") == "PASS"
    assert "cures" not in out.caption.lower()


def test_craft_review_rejects_unpasteable_without_chat() -> None:
    from boxes.craft import review_craft
    from boxes.hard_rules import load_disclaimer

    disc = load_disclaimer()
    out = review_craft(
        _draft(f"Hydro Boost is Try it in the PM routine.\n\n{disc}"),
        chat=None,
    )
    assert out.verdict == "FAIL"
    assert out.reasons


def test_loop_craft_fail_triggers_ai_rewrite() -> None:
    from boxes.craft import CraftOut
    from boxes.copywriter import CopyOut
    from boxes.hard_rules import load_disclaimer
    from boxes.judge import ImpliedClaimOut
    from boxes.loop import run_loop
    from pydantic import BaseModel

    disc = load_disclaimer()
    clean = f"Night: double cleanse, then Hydro Boost. Dermatologist tested.\n\n{disc}"
    weak = f"Hydro Boost is dermatologist tested.\n\n{disc}"
    calls = {"craft": 0}

    class Chat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            if schema is ImpliedClaimOut:
                return ImpliedClaimOut(implied=False)
            if schema is CraftOut:
                calls["craft"] += 1
                if "double cleanse" in user.lower():
                    return CraftOut(verdict="PASS", reasons=[])
                return CraftOut(verdict="FAIL", reasons=["1. Name the night routine."])
            raise AssertionError(schema)

    def rewrite(draft: Draft, reasons: list[str]) -> Draft:
        assert reasons
        return draft.model_copy(update={"caption": clean})

    out = run_loop(_draft(weak), chat=Chat(), rewriter=rewrite)
    assert calls["craft"] >= 1
    assert (out.judge or {}).get("craft") == "PASS"
    assert "double cleanse" in out.caption.lower()


def test_loop_sends_reasons_to_rewriter() -> None:
    from boxes.loop import run_loop
    from boxes.hard_rules import load_disclaimer

    seen: list[list[str]] = []
    clean = (
        "Monday light. Dermatologist tested Hydro Boost.\n\n" + load_disclaimer()
    )

    def once(draft: Draft, reasons: list[str]) -> Draft:
        seen.append(list(reasons))
        return draft.model_copy(update={"caption": clean})

    out = run_loop(_draft("This gel cures acne."), max_rounds=3, rewriter=once)
    assert seen, "expected at least one rewrite"
    blob = " ".join(seen[0]).lower()
    assert "cures" in blob
    assert not _flagged(out)
    assert out.round <= 3
