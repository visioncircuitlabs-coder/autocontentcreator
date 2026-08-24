"""Compliance gap G3: split the banned-token gate into unconditional T2
drug-class verbs vs superlatives that a registry entry may back.

Per docs/bar/compliance-bar.md: 'cures/heals/treats/prevents/guarantees' are
unconditional rejects (DMRA / drug-boundary). Superlatives ('best', 'only')
reject unless an approved registry phrase explicitly covers them.
"""

from __future__ import annotations

# Unconditional drug-class verbs — never acceptable in skincare copy.
T2_VERBS = ("cures", "heals", "treats", "prevents", "guarantees")

# Superlatives/absolutes — reject unless registry-approved comparison exists.
SUPERLATIVES = ("best", "only", "#1", "number one")


def classify_token_hit(token: str) -> str:
    t = token.strip().lower()
    if t in T2_VERBS:
        return "unconditional"
    if t in SUPERLATIVES or t in ("guaranteed",):
        return "superlative"
    return "unknown"
