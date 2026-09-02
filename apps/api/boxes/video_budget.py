"""Video budget gate — Grok Imagine video is a separate USD cap from stills.

Every live video call goes through spend_gate() before the HTTP request and
record_spend() after. Past the cap, calls fail friendly (stub fallback keeps
the walk alive). Same spend.jsonl as stills, tagged adapter=grok-imagine-video.
"""

from __future__ import annotations

import os

from boxes.image_budget import BudgetExceeded, record_spend, spent_usd as media_spent

# grok-imagine-video-1.5 list price, USD per second (720p text-to-video).
COST_PER_SECOND_USD = 0.08
DURATION_S = 5
COST_PER_VIDEO_USD = round(COST_PER_SECOND_USD * DURATION_S, 4)

DEFAULT_BUDGET_USD = 2.00
ADAPTER = "grok-imagine-video"


def budget_usd() -> float:
    raw = os.environ.get("VIDEO_BUDGET_USD", "").strip()
    try:
        return float(raw) if raw else DEFAULT_BUDGET_USD
    except ValueError:
        return DEFAULT_BUDGET_USD


def spent_usd() -> float:
    return media_spent(adapter=ADAPTER)


def spend_gate(estimate_usd: float | None = None) -> dict:
    """Raise BudgetExceeded past cap; return status dict otherwise."""
    cost = COST_PER_VIDEO_USD if estimate_usd is None else estimate_usd
    used = spent_usd()
    cap = budget_usd()
    if used + cost > cap + 1e-9:
        raise BudgetExceeded(
            f"Video budget exhausted: ${used:.2f} of ${cap:.2f} spent. "
            "A short stub clip will be used instead."
        )
    return {"spent": used, "cap": cap, "this_call": cost}


def record_video_spend(usd: float) -> None:
    record_spend(usd, adapter=ADAPTER)
