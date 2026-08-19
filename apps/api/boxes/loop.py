"""Improvement loop — writer ≠ judge. Max 3 rounds, then flag a human."""

from __future__ import annotations

from collections.abc import Callable

from boxes.hard_rules import run_hard_rules
from boxes.judge import run_judge
from boxes.product_facts import load_claim_models
from models import Claim, Draft
from ports import ChatModel

Rewriter = Callable[[Draft, list[str]], Draft]


def default_rewrite(draft: Draft, reasons: list[str]) -> Draft:
    """Send numbered fail reasons to the copywriter; keep one cleaned caption."""
    from boxes.copywriter import rewrite_draft

    return rewrite_draft(draft, reasons)


def run_loop(
    draft: Draft,
    max_rounds: int = 3,
    *,
    rewriter: Rewriter | None = None,
    claims: list[Claim] | None = None,
    chat: ChatModel | None = None,
    organic: bool = True,
) -> Draft:
    """Evaluate hard rules + judge. On FAIL, rewrite. Stop at max_rounds."""
    rewrite_fn = rewriter or default_rewrite
    claim_list = claims if claims is not None else load_claim_models()
    current = draft if draft.round >= 1 else draft.model_copy(update={"round": 1})

    while True:
        rules = run_hard_rules(current, organic=organic)
        verdict = run_judge(current, claim_list, chat=chat)
        passed = (not rules) and verdict.verdict == "PASS"
        flag_human = (not passed) and current.round >= max_rounds

        payload = verdict.model_dump()
        payload["flag_human"] = flag_human  # in-memory only; Task 10 persists drafts to SQLite
        current = current.model_copy(
            update={
                "rules": rules,
                "judge": payload,
                "flag_human": flag_human,
            }
        )

        if passed or flag_human:
            return current

        reasons = list(rules) + list(verdict.reasons)
        rewritten = rewrite_fn(current, reasons)
        current = rewritten.model_copy(update={"round": current.round + 1})
