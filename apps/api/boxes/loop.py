"""Improvement loop — writer ≠ judge. Max 3 rounds, then flag a human."""

from __future__ import annotations

import re
from collections.abc import Callable

from boxes.hard_rules import (
    BANNED_TOKENS,
    has_benefit_line,
    has_disclaimer,
    load_disclaimer,
    run_hard_rules,
)
from boxes.judge import run_judge
from boxes.product_facts import load_claim_models
from models import Claim, Draft
from ports import ChatModel

Rewriter = Callable[[Draft, list[str]], Draft]


def strip_banned_tokens(text: str) -> str:
    out = text or ""
    for token in BANNED_TOKENS:
        out = re.sub(rf"(?<!\w){re.escape(token)}(?!\w)", "", out, flags=re.IGNORECASE)
    out = re.sub(r"(?i)#ad\b", "", out)
    out = re.sub(r"\s+([.,!?])", r"\1", out)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()


def default_rewrite(draft: Draft, reasons: list[str]) -> Draft:
    """Stub rewriter until Task 8 copywriter. Apply judge.rewrite or strip tokens."""
    _ = reasons  # Task 8 copywriter will consume numbered reasons
    suggested = (draft.judge or {}).get("rewrite") if draft.judge else None
    if isinstance(suggested, str) and suggested.strip():
        caption = suggested.strip()
    else:
        caption = draft.caption or ""
    caption = strip_banned_tokens(caption)
    disc = load_disclaimer()
    if has_benefit_line(caption) and not has_disclaimer(caption, disc):
        caption = f"{caption}\n\n{disc}"
    return draft.model_copy(update={"caption": caption})


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
        payload["flag_human"] = flag_human
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
