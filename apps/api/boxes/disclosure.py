"""Disclosure formatter — per-market paid-post labels (compliance bar G7).

Every material-connection post must carry an approved label, placed where the
target market's rules say it cannot be missed:
  - IN  (ASCI): exact approved term, first two lines, never buried in a
    hashtag cluster (IN-1..IN-3);
  - US  (FTC 16 CFR 255): unambiguous disclosure, unavoidable/proximate —
    codified here as within the first two lines;
  - EU  (UCPD): clear commercial identifier in the content itself.

Video-duration timing rules (§3) do not apply yet: the demo produces static
captions only. Deterministic, no LLM — same class of rule as hard_rules.
"""

from __future__ import annotations

import re

# Approved label vocabulary per market (superset allowed downstream).
COMMON_LABELS = (
    "advertisement",
    "sponsored",
    "collaboration",
    "collab",
    "partnership",
    "affiliate",
    "free gift",
    "paid promotion",
    "paid partnership",
    "#ad",
    "ad",
)
MARKET_LABELS: dict[str, tuple[str, ...]] = {
    "IN": COMMON_LABELS,
    "US": COMMON_LABELS + ("paid by",),
    "EU": COMMON_LABELS + ("werbung", "publicité", "publicite"),
}
# Canonical label injected when a paid caption lacks one. Short, approved in
# every modelled market, and survives character-limited platforms.
CANONICAL_LABEL = "#ad"

# Longer alternatives first so "advertisement" wins over bare "ad".
_LABEL_RE = re.compile(
    r"(?i)(?<![\w#])(#ad|advertisement|paid promotion|paid partnership|"
    r"paid by|partnership|collaboration|collab|affiliate|free gift|"
    r"sponsored|werbung|publicit[ée]|ad)(?!\w)"
)
_HASHTAG_LINE_RE = re.compile(r"^(#\S+\s*)+$")


def _labels_for(market: str | None) -> tuple[str, ...]:
    return MARKET_LABELS.get((market or "").upper(), COMMON_LABELS)


def _matches(caption: str, market: str | None) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in _LABEL_RE.finditer(caption or "")]


def _first_two_span(lines: list[tuple[int, int, str]]) -> tuple[int, int]:
    """Char range covering the first two non-empty lines."""
    nonempty = [(s, e, txt) for s, e, txt in lines if txt.strip()]
    head = nonempty[:2]
    if not head:
        return (0, 0)
    return (head[0][0], head[-1][1])


def _with_offsets(caption: str) -> list[tuple[int, int, str]]:
    out: list[tuple[int, int, str]] = []
    pos = 0
    for line in (caption or "").splitlines():
        out.append((pos, pos + len(line), line))
        pos += len(line) + 1
    return out


def _is_hashtag_only(line: str) -> bool:
    return bool(_HASHTAG_LINE_RE.match(line.strip()))


def disclosure_violations(caption: str, market: str | None = None) -> list[str]:
    """Return violation strings for a PAID caption. Empty list = compliant.

    Checks, in order:
      - an approved label appears at all;
      - it sits within the first two non-empty lines (unmissable placement);
      - when placement fails and every occurrence hides in a trailing
        hashtag cluster, name that specifically (IN-3 anti-pattern).
    """
    mkt = (market or "IN").upper()
    hits = _matches(caption, mkt)
    if not hits:
        return [
            f"paid post missing disclosure label for market {mkt}: "
            "use #ad or Sponsored"
        ]
    lines = _with_offsets(caption)
    start, end = _first_two_span(lines)
    if any(s < end and e > start for s, e in hits):
        return []
    hashtag_lines = [(s, e) for s, e, line in lines if _is_hashtag_only(line)]
    all_buried = all(
        any(hs < le and he > ls for ls, le in hashtag_lines) for hs, he in hits
    )
    if all_buried:
        return [
            f"disclosure label buried in hashtag cluster for market {mkt}: "
            "move it above the hashtags, into the first two lines"
        ]
    return [
        f"disclosure label must sit in the first two lines for market {mkt} "
        "(ASCI/FTC/UCPD placement)"
    ]


def has_paid_label(caption: str, market: str | None = None) -> bool:
    return bool(_matches(caption, market))


def ensure_disclosure(caption: str, market: str | None = None) -> str:
    """Deterministically place the label so disclosure_violations passes.

    Strips any existing label tokens (controlled vocabulary, safe to move)
    and re-injects one canonical label as its own first line. Idempotent;
    never invents content. Used by the loop so a paid run converges without
    burning rewrite rounds on placement.
    """
    body = caption or ""
    body = _LABEL_RE.sub("", body)
    body = re.sub(r"[ \t]{2,}", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if not body:
        return CANONICAL_LABEL
    return f"{CANONICAL_LABEL}\n\n{body}"
