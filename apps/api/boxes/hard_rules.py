"""Hard Rules — gazette tokens and required labels. Unbribable, no LLM."""

from __future__ import annotations

import re
from pathlib import Path

from boxes.product_facts import compare_claims
from models import Draft

DEFAULT_DISCLAIMER_PATH = (
    Path(__file__).resolve().parent.parent / "fixtures" / "neutrogena" / "disclaimer.txt"
)

BANNED_TOKENS = ("cures", "heals", "best", "only", "guaranteed")


def strip_banned_tokens(text: str) -> str:
    """Drop gazette tokens and #ad. Used by the copywriter rewrite path."""
    out = text or ""
    for token in BANNED_TOKENS:
        out = re.sub(rf"(?<!\w){re.escape(token)}(?!\w)", "", out, flags=re.IGNORECASE)
    out = re.sub(r"(?i)#ad\b", "", out)
    out = re.sub(r"\s+([.,!?])", r"\1", out)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()

# Product-effect words that count as a benefit line (disclaimer required).
BENEFIT_MARKERS = (
    "hydrate",
    "hydrates",
    "hydrating",
    "hydration",
    "moisturize",
    "moisturizes",
    "moisturizing",
    "moisturise",
    "moisturises",
    "protect",
    "protects",
    "protecting",
    "brighten",
    "brightens",
    "soothe",
    "soothes",
    "reduce",
    "reduces",
    "prevent",
    "prevents",
    "nourish",
    "nourishes",
    "glow",
    "glowing",
    "spf",
)

_AD_RE = re.compile(r"(?i)#ad\b")
_WS_RE = re.compile(r"\s+")


def load_disclaimer(path: Path | None = None) -> str:
    path = path or DEFAULT_DISCLAIMER_PATH
    return path.read_text(encoding="utf-8").strip()


def _norm_ws(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def has_disclaimer(text: str, disclaimer: str) -> bool:
    if not disclaimer:
        return False
    return _norm_ws(disclaimer) in _norm_ws(text or "")


def without_disclaimer(text: str, disclaimer: str) -> str:
    """Drop the fixture disclaimer so its wording cannot trip token rules."""
    if not text:
        return ""
    if not disclaimer:
        return text
    if disclaimer in text:
        return text.replace(disclaimer, " ")
    norm_d = _norm_ws(disclaimer)
    norm_t = _norm_ws(text)
    if norm_d and norm_d in norm_t:
        return norm_t.replace(norm_d, " ")
    return text


def has_benefit_line(text: str) -> bool:
    if not text or not text.strip():
        return False
    hits = compare_claims(text)
    if any(h.get("status") in ("approved", "conditional") for h in hits):
        return True
    for marker in BENEFIT_MARKERS:
        if re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", text, flags=re.IGNORECASE):
            return True
    return False


def run_hard_rules(
    draft: Draft,
    *,
    organic: bool = True,
    disclaimer: str | None = None,
) -> list[str]:
    """Return violation strings. Empty list = pass."""
    caption = draft.caption or ""
    disc = load_disclaimer() if disclaimer is None else disclaimer
    body = without_disclaimer(caption, disc)
    reasons: list[str] = []

    for token in BANNED_TOKENS:
        if re.search(rf"(?<!\w){re.escape(token)}(?!\w)", body, flags=re.IGNORECASE):
            reasons.append(f"banned token: {token}")

    has_ad = bool(_AD_RE.search(caption))
    if organic and has_ad:
        reasons.append("organic demo forbids #ad")
    if not organic and not has_ad:
        reasons.append("paid placement requires #ad")

    if has_benefit_line(body) and not has_disclaimer(caption, disc):
        reasons.append("benefit line requires market disclaimer")

    return reasons
