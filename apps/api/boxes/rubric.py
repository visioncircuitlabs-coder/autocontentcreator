"""Style rubric (docs/style/rubric.md) as code: voice rules, modes, scoring.

Deterministic helpers only — no LLM here. The LLM-facing blocks are plain
strings dropped into strategist / copywriter system prompts.
"""

from __future__ import annotations

import re

# --- Voice rules for prompts (from rubric §2 + Appendix) --------------------

RUBRIC_VOICE = (
    "Voice: a knowledgeable, warm friend who knows skincare science — "
    "not a dermatologist lecturing, not an influencer gushing. "
    "Hook in <=8 words using command/contradiction/confession/specific-number; "
    "never open with the brand name or 'introducing'/'say hello to'. "
    "Every claim carries a number, ingredient+concentration, or timeframe. "
    "Concrete images over adjective pairs ('absorbs before your chai cools', "
    "never 'luxurious and nourishing'). Cut filler: very, really, actually, "
    "simply, just. Max one exclamation per caption, zero preferred. "
    "One CTA with a reason. INR pricing, Indian context (humidity, pollution, "
    "monsoon, festivals), Hinglish-light max 1-2 words in social only. "
    "Cosmetic-safe claims only: 'reduces the look of', 'visibly', 'helps with'."
)

BANNED_OPENERS = ("introducing", "say hello to", "we're excited", "we are excited")

# Rubric v2 deterministic tightenings (docs/bar/copy-bar.md §B1/B2).
# B1 — the hook line: <=8 words AND <=60 chars; a first line that LEADS with
# the brand name or an announcing word (F1 "brand-name opener") caps the hook
# at 2, and the one_line_fix names it.
HOOK_MAX_WORDS = 8
HOOK_MAX_CHARS = 60
BRAND_HOOK_NAMES = ("hydro boost", "neutrogena", "lay's", "lays", "chile limón", "chile limon")
ANNOUNCE_HOOK_WORDS = ("introducing", "say hello")
# B2 — voice physics: corporate announce register fails ANYWHERE in the copy,
# not just as an opener; caps emotional_truth at 2 (forces REWRITE).
EXCITED_ANNOUNCE = ("we're excited", "we are excited")

CLICHE_BLACKLIST = (
    "glow like never before",
    "unleash your",
    "game-changer",
    "game changer",
    "elevate your skincare",
    "revolutionary",
    "magical",
    "miracle",
    "luxurious and nourishing",
    "the perfect",
    "secret to radiant skin",
    "youthful glow",
    "holy grail",
    "skin goals",
)

FILLER_WORDS = ("very ", "really ", "actually ", "simply ", "just ")

SITUATION_WORDS = (
    "commute",
    "monsoon",
    "humidity",
    "humid",
    "ac ",
    "webcam",
    "3 pm",
    "night",
    "morning",
    "chai",
    "metro",
    "festival",
    "diwali",
    "gym",
    "office",
    "monday",
)

# --- Rubric modes: each caption variant is written in ONE distinct mode -----

MODES = ("imperative-compression", "peer-voice-intimate", "describe-dont-promise")

MODE_EXEMPLARS = {
    "imperative-compression": (
        "Nike-style imperative compression: 2-6 word verb-first commands, "
        "second person, zero hedging, product appears late or not at all. "
        "e.g. 'Wash your face tonight. Even tired. Especially tired.'"
    ),
    "peer-voice-intimate": (
        "Glossier-style peer voice: lowercase intimacy, texts-from-a-friend "
        "fragments, a confession or question with real stakes. "
        "e.g. 'i used to sleep in makeup. then i met a mirror at 9 am.'"
    ),
    "describe-dont-promise": (
        "Aesop-style literary restraint: full sentences, no exclamation, "
        "describe texture/ritual/formulation — never promise transformation. "
        "e.g. 'a gel-cream that absorbs before your chai cools, matte by morning.'"
    ),
}

MODE_PROMPT_BLOCK = (
    "Write each caption in a DIFFERENT rubric mode from <modes>; do not submit "
    "three near-identical captions:\n"
    + "\n".join(f"- {m}: {MODE_EXEMPLARS[m]}" for m in MODES)
)

# --- Dimension-scored deterministic craft check ------------------------------

DIMENSIONS = (
    "hook_strength",
    "rhythm_economy",
    "specificity",
    "emotional_truth",
    "brand_fit",
)

DIMENSION_FIXES = {
    "hook_strength": "Rewrite the first line as a <=8-word command, contradiction, confession, or specific number — never the brand name or 'Introducing'.",
    "rhythm_economy": "Cut filler words and doubled adjectives; vary sentence length so every word is load-bearing.",
    "specificity": "Anchor each benefit with a number, ingredient concentration, timeframe, or sensory detail.",
    "emotional_truth": "Root the emotion in a recognizable situation (3 PM webcam shine, monsoon commute) instead of adjectives; drop the 'we're excited' announce voice for a peer confession.",
    "brand_fit": "Remove cliche hype lines; keep warm peer-level voice and at most one exclamation.",
}


def find_cliches(text: str) -> list[str]:
    blob = (text or "").lower()
    return [c for c in CLICHE_BLACKLIST if c in blob]


def _first_sentence(text: str) -> str:
    parts = re.split(r"[.!?\n]", (text or "").strip(), maxsplit=1)
    return (parts[0] if parts else "").strip()


def score_dimensions(text: str) -> dict[str, int]:
    """Deterministic 1-5 scores on the five craft dimensions.

    Rubric v2 (copy-bar §B1/B2): first line over 8 words or 60 chars caps
    hook_strength at 3; a first line that leads with the brand name or an
    announcing word caps it at 2 (one_line_fix names it); "we're excited"
    anywhere caps emotional_truth at 2, forcing REWRITE regardless of avg.
    """
    body = (text or "").strip().replace("\u2019", "'")  # curly-apostrophe norm
    lower = body.lower()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", lower) if s.strip()]
    hook = _first_sentence(body)
    hook_lower = hook.lower()
    hook_words = len(hook.split())

    # D1 hook strength (B1)
    banned = any(lower.startswith(opener) for opener in BANNED_OPENERS)
    leads_with_brand_or_announce = hook_lower.startswith(
        BRAND_HOOK_NAMES + ANNOUNCE_HOOK_WORDS
    )
    if banned:
        hook_score = 1
    elif leads_with_brand_or_announce:
        hook_score = 2
    elif 0 < hook_words <= HOOK_MAX_WORDS and len(hook) <= HOOK_MAX_CHARS:
        hook_score = 5
    else:
        hook_score = 3  # overlong first line: capped, never a 5 (B1)

    # D3 rhythm & economy
    fillers = sum(1 for w in FILLER_WORDS if f" {w}" in f" {lower}")
    exclam = lower.count("!")
    if exclam > 1 or fillers >= 2:
        rhythm = 2
    elif exclam == 1 or fillers == 1:
        rhythm = 4
    else:
        rhythm = 5

    # D2 specificity
    if re.search(r"\d+%|\b\d+\s*(ml|g|x)\b|₹", lower):
        specificity = 5
    elif re.search(r"\d", lower):
        specificity = 4
    else:
        specificity = 3

    # D4 emotional truth
    situations = sum(1 for w in SITUATION_WORDS if w in lower)
    emotional = min(5, 3 + situations) if situations else 3
    if situations >= 2:
        emotional = 5
    if any(p in lower for p in EXCITED_ANNOUNCE):
        emotional = min(emotional, 2)  # B2 hard cap → min dim < 3 → REWRITE

    # D5 brand fit
    if find_cliches(body):
        brand_fit = 1
    elif exclam <= 1 and fillers <= 1:
        brand_fit = 5 if situations and specificity >= 4 else 4
    else:
        brand_fit = 3

    return {
        "hook_strength": hook_score,
        "rhythm_economy": rhythm,
        "specificity": specificity,
        "emotional_truth": emotional,
        "brand_fit": brand_fit,
    }


def style_verdict(scores: dict[str, int]) -> tuple[str, float, str | None]:
    """(verdict, average, one_line_fix). PASS bar: avg >= 3.8, no dimension < 3."""
    values = [max(1, min(5, int(scores.get(d, 0) or 0))) for d in DIMENSIONS]
    avg = round(sum(values) / len(values), 2)
    worst = min(DIMENSIONS, key=lambda d: scores.get(d, 5))
    if avg >= 3.8 and min(values) >= 3:
        return ("PASS", avg, None)
    return ("REWRITE", avg, DIMENSION_FIXES[worst])
