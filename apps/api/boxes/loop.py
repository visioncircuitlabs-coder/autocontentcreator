"""Improvement loop — writer ≠ judge. Max 3 rounds, then flag a human."""

from __future__ import annotations

from collections.abc import Callable

from boxes.craft import review_craft
from boxes.hard_rules import run_hard_rules
from boxes.judge import run_judge
from boxes.product_facts import load_claim_models
from models import Claim, Draft
from ports import ChatModel

Rewriter = Callable[[Draft, list[str]], Draft]


def default_rewrite(
    draft: Draft,
    reasons: list[str],
    *,
    chat: ChatModel | None = None,
) -> Draft:
    """Send numbered fail reasons to the copywriter; keep one cleaned caption."""
    from boxes.copywriter import rewrite_draft

    return rewrite_draft(draft, reasons, chat=chat)


def run_loop(
    draft: Draft,
    max_rounds: int = 3,
    *,
    rewriter: Rewriter | None = None,
    claims: list[Claim] | None = None,
    chat: ChatModel | None = None,
    organic: bool = True,
    market: str | None = None,
) -> Draft:
    """Hard rules + claims judge + AI craft review. Rewrite. Max rounds, then a person.

    market (optional): target jurisdiction for per-market claim clearance (G8).
    Falls back to the brief's market when the draft's brief is resolvable.
    """
    if rewriter is None:

        def rewrite_fn(draft: Draft, reasons: list[str]) -> Draft:
            return default_rewrite(draft, reasons, chat=chat)

    else:
        rewrite_fn = rewriter
    claim_list = claims if claims is not None else load_claim_models()
    if market is None and draft.brief_id:
        from db import get_brief

        brief = get_brief(draft.brief_id)
        if brief is not None:
            market = brief.market
    current = draft if draft.round >= 1 else draft.model_copy(update={"round": 1})

    while True:
        if not organic:
            # Paid posts: place the disclosure label deterministically before
            # judging (G7). Idempotent — a compliant caption passes unchanged.
            from boxes.disclosure import ensure_disclosure

            fixed = ensure_disclosure(current.caption, market)
            if fixed != current.caption:
                current = current.model_copy(update={"caption": fixed})
        rules = run_hard_rules(current, organic=organic, market=market)
        if rules:
            # Deterministic failure — skip judge + craft (saves 2 chat calls
            # per round) and go straight to rewrite with exact reasons.
            if current.round >= max_rounds:
                current = current.model_copy(update={"rules": rules, "flag_human": True})
                return current
            rewritten = rewrite_fn(current, list(rules))
            current = rewritten.model_copy(update={"round": current.round + 1})
            continue
        verdict = run_judge(current, claim_list, chat=chat)
        craft = review_craft(current, chat=chat)
        passed = (
            (not rules)
            and verdict.verdict == "PASS"
            and craft.verdict == "PASS"
        )
        flag_human = (not passed) and current.round >= max_rounds

        payload = verdict.model_dump()
        payload["flag_human"] = flag_human
        payload["craft"] = craft.verdict
        payload["craft_reasons"] = list(craft.reasons)
        payload["craft_dimensions"] = dict(craft.dimensions)
        current = current.model_copy(
            update={
                "rules": rules,
                "judge": payload,
                "flag_human": flag_human,
            }
        )

        if passed or flag_human:
            return current

        reasons = list(rules) + list(verdict.reasons) + list(craft.reasons)
        style = verdict.style
        if (
            style is not None
            and style.verdict == "REWRITE"
            and style.one_line_fix
            and not any("style rubric" in row for row in reasons)
        ):
            reasons.append(
                f"note: style rubric {style.verdict} (avg {style.average}) — {style.one_line_fix}"
            )
        rewritten = rewrite_fn(current, reasons)
        current = rewritten.model_copy(update={"round": current.round + 1})
