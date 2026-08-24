"""Learning loop v1 — past winners & rejection reasons back into the writer prompt.

Reads the track_record ledger (same tables feedback.py writes), distills:
- exemplars: APPROVED captions ranked by win rate (approvals / decisions per
  identical normalized caption text),
- anti-patterns: most common rejection reason strings.

Pure read-side + prompt block. Data-only output; jailbreak guards live in the
writer system prompt. Results are cached per process with a short TTL so bursty
factory runs do not re-query SQLite on every call.
"""

from __future__ import annotations

import os
import re
import time
from collections import Counter
from pathlib import Path

from db import list_track_record

CACHE_TTL = 300.0

_CACHE: dict[tuple[str, str], tuple[float, object]] = {}

_MAX_LINE = 240


def reset_learning_cache() -> None:
    """Drop cached exemplars/anti-patterns (tests, or a fresh factory run)."""
    _CACHE.clear()


def _cached(key: tuple[str, str], fn):
    now = time.monotonic()
    hit = _CACHE.get(key)
    if hit is not None and now - hit[0] < CACHE_TTL:
        return hit[1]
    value = fn()
    _CACHE[key] = (now, value)
    return value


def normalize_text(text: str) -> str:
    """Whitespace-collapsed, lowercased key for grouping identical captions."""
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _sku_ok(row_sku: str, sku_key: str) -> bool:
    sku_key = (sku_key or "").strip()
    row_sku = (row_sku or "").strip()
    return (not sku_key) or (not row_sku) or row_sku in (sku_key, "*")


def get_exemplars(sku: str | None = None, limit: int = 5) -> list[dict]:
    """Highest-win-rate approved captions.

    Win rate = approvals / total decisions for one identical normalized
    caption text. Rows with zero approvals never qualify. Ties break by
    approval count, then recency.
    """
    sku_key = (sku or "").strip()

    def compute() -> list[dict]:
        stats: dict[str, dict] = {}
        for row in list_track_record():
            verdict = (row.get("verdict") or "").strip().lower()
            if verdict not in ("approve", "reject"):
                continue
            caption = (row.get("caption") or "").strip()
            if not caption:
                continue
            if not _sku_ok(row.get("sku") or "", sku_key):
                continue
            key = normalize_text(caption)
            entry = stats.setdefault(
                key,
                {"caption": caption[:_MAX_LINE], "wins": 0, "decisions": 0, "last": ""},
            )
            decided_at = str(row.get("decided_at") or "")
            if decided_at > entry["last"]:
                entry["last"] = decided_at
                entry["caption"] = caption[:_MAX_LINE]
            entry["decisions"] += 1
            if verdict == "approve":
                entry["wins"] += 1
        pool = [entry for entry in stats.values() if entry["wins"] > 0]
        pool.sort(
            key=lambda e: (
                -(e["wins"] / e["decisions"]) if e["decisions"] else 0.0,
                -e["wins"],
                e["last"],
            ),
            reverse=False,
        )
        return [
            {"caption": e["caption"], "wins": e["wins"], "decisions": e["decisions"]}
            for e in pool[: max(1, int(limit))]
        ]

    return _cached(("exemplars", sku_key.lower()), compute)


def get_anti_patterns(limit: int = 5) -> list[str]:
    """Most common rejection reason strings (distilled reason preferred)."""
    limit = max(1, int(limit))

    def compute() -> list[str]:
        counter: Counter[str] = Counter()
        for row in list_track_record():
            if (row.get("verdict") or "").strip().lower() != "reject":
                continue
            reason = (row.get("distilled") or row.get("reason") or "").strip()
            if not reason:
                continue
            counter[normalize_text(reason)[:280]] += 1
        ranked = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
        return [reason for reason, _ in ranked[:limit]]

    return _cached(("anti", ""), compute)


def _reason_category(reason: str) -> str:
    """Category = first word of the distilled (fallback raw) reason string.

    'off-brand: reads like an ad' and 'OFF-BRAND tone' share a bucket;
    punctuation on the token is ignored.
    """
    words = normalize_text(reason).split(" ")
    if not words:
        return ""
    return words[0].strip(",:;.!?'\"()-—")


def get_hard_bans(limit: int = 20) -> list[dict]:
    """Captions whose normalized text was rejected 2+ times for one category.

    Hard-ban memory (competitive bar R3): the prompt-level <avoid> block asks
    nicely; this is the enforcement side. A caption that came back twice with
    the same first-word rejection category must never be regenerated — callers
    filter generated candidates against these normalized texts.
    """
    limit = max(1, int(limit))

    def compute() -> list[dict]:
        rejects: dict[str, dict] = {}
        for row in list_track_record():
            if (row.get("verdict") or "").strip().lower() != "reject":
                continue
            caption = (row.get("caption") or "").strip()
            if not caption:
                continue
            reason = (row.get("distilled") or row.get("reason") or "").strip()
            if not reason:
                continue
            key = normalize_text(caption)
            entry = rejects.setdefault(
                key, {"caption": caption[:_MAX_LINE], "categories": Counter()}
            )
            category = _reason_category(reason)
            if not category:
                continue
            entry["categories"][category] += 1
        bans: list[dict] = []
        for key, entry in rejects.items():
            top_category, count = entry["categories"].most_common(1)[0]
            if count < 2:
                continue
            bans.append(
                {
                    "caption": entry["caption"],
                    "normalized": key,
                    "category": top_category,
                    "rejects": count,
                }
            )
        bans.sort(key=lambda b: (-b["rejects"], b["normalized"]))
        return bans[:limit]

    return _cached(("bans", ""), compute)


# --- Human-edited lessons (Markdown read path) --------------------------------
#
# boxes/memory_store.py maintains data/memory/lessons.md as a human-editable
# lessons file; this side only READS it so hand edits flow back into the
# writer prompt. Parsing is deliberately tolerant: a mangled file must never
# break generation, so garbage between blocks is skipped silently.
#
# Contract (one block):
#     ### les_001
#     - status: active
#     - scope: global
#     - rule: One-line rule text here.
#     - source: where it came from

DEFAULT_MEMORY_DIR = "data/memory"

_LESSON_FIELD_KEYS = frozenset({"status", "scope", "rule", "source"})


def resolve_lessons_path() -> Path:
    """Path of the Markdown lessons file ($MEMORY_DIR/lessons.md).

    Same env-default convention as db.DEFAULT_SQLITE_PATH ("data/demo.db").
    """
    base = os.environ.get("MEMORY_DIR", DEFAULT_MEMORY_DIR)
    return Path(base) / "lessons.md"


def _parse_all_lessons(text: str) -> list[dict]:
    """Extract every parseable lesson dict per the contract; never raises.

    Same fields as get_active_lessons returns, but ANY status passes
    (active/draft/retired/...) as long as the block carries a non-empty
    rule — callers doing coverage/dedupe work need retired rules too.
    """
    lessons: list[dict] = []
    fields: dict[str, str] = {}
    lesson_id = ""

    def flush() -> None:
        nonlocal fields, lesson_id
        if not lesson_id:
            return  # prose/garbage outside any "### les_" block
        rule = fields.get("rule", "").strip()
        if rule:
            lessons.append(
                {
                    "id": lesson_id,
                    "status": fields.get("status", "").strip().lower(),
                    "scope": fields.get("scope", "").strip(),
                    "rule": rule,
                    "source": fields.get("source", "").strip(),
                }
            )
        fields, lesson_id = {}, ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("### les_"):
            flush()  # previous block ends here (if any)
            lesson_id = line[4:].strip()  # keep the full id, e.g. "les_001"
        elif line.startswith("### "):
            flush()  # any other heading just terminates the current block
        elif line.startswith("- ") and ":" in line and lesson_id:
            key, _, value = line[2:].partition(":")
            key = key.strip().lower()
            if key in _LESSON_FIELD_KEYS:
                fields[key] = value.strip()  # unknown keys dropped; last wins
    flush()  # EOF ends the final block
    return lessons


def _parse_lessons(text: str) -> list[dict]:
    """Active-only view of _parse_all_lessons (the public contract)."""
    return [
        lesson
        for lesson in _parse_all_lessons(text)
        if lesson["status"] == "active"
    ]


def get_active_lessons(path: Path | None = None) -> list[dict]:
    """Active human-written lessons from the Markdown file.

    Returns [{"id", "status", "scope", "rule", "source"}] for blocks whose
    status is "active" (case-insensitive) and that carry a non-empty rule.
    Blocks missing a rule are skipped; unparsable content is ignored
    silently. Deliberately uncached — humans edit the file live and it is
    tiny. Missing/unreadable file -> [].
    """
    lessons_path = path if path is not None else resolve_lessons_path()
    try:
        text = lessons_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return _parse_lessons(text)


def learning_block(
    sku: str | None = None,
    *,
    winners_limit: int = 5,
    avoid_limit: int = 5,
) -> tuple[str, int, int]:
    """`<winners>` + `<avoid>` + `<lessons>` prompt block.

    Returns (text, n_winners, n_avoid) — the counts cover only ledger rows;
    human-written Markdown lessons (data/memory/lessons.md, edited live)
    ride along as an appended <lessons> tag without changing the counts.

    Empty string when neither the ledger nor the lessons file has anything
    to teach — callers skip the tags entirely rather than shipping empty
    scaffolding.
    """
    winners = get_exemplars(sku=sku, limit=winners_limit)
    avoid = get_anti_patterns(limit=avoid_limit)
    lessons = get_active_lessons()
    if not winners and not avoid and not lessons:
        return "", 0, 0
    parts: list[str] = []
    if winners:
        lines = "\n".join(
            f"- {w['caption']} [approved {w['wins']}/{w['decisions']} times]"
            for w in winners
        )
        parts.append(f"<winners>\n{lines}\n</winners>")
    if avoid:
        lines = "\n".join(f"- {reason}" for reason in avoid)
        parts.append(f"<avoid>\n{lines}\n</avoid>")
    if lessons:
        lines = "\n".join(f"- [{l['scope']}] {l['rule']}" for l in lessons)
        parts.append(f"<lessons>\n{lines}\n</lessons>")
    return "\n".join(parts), len(winners), len(avoid)


# --- Lesson suggestions (machine-proposed, human-promoted) ---------------------
#
# Anti-patterns no lesson covers yet are candidates for a new rule. memory_store
# writes them as status:"draft" blocks via append_draft_lesson(); a human then
# promotes or retires them by editing lessons.md. Coverage is deliberately
# crude but deterministic: an anti-pattern counts as covered when some 4-word
# contiguous slice of it appears inside a lesson rule (or the texts match
# outright) — good enough to stop re-suggesting what a rule already says.

_COVERAGE_WINDOW = 4


def _covered_by_rules(reason: str, rules: list[str]) -> bool:
    """True when any 4 consecutive words of reason appear in some rule."""
    reason_norm = normalize_text(reason)
    if not reason_norm:
        return True  # nothing to suggest anyway
    words = reason_norm.split(" ")
    windows = (
        {" ".join(words[i : i + _COVERAGE_WINDOW]) for i in range(len(words) - 3)}
        if len(words) >= _COVERAGE_WINDOW
        else set()
    )
    for rule in rules:
        rule_norm = normalize_text(rule)
        if not rule_norm:
            continue
        if reason_norm == rule_norm:
            return True
        if any(window in rule_norm for window in windows):
            return True
    return False


def get_lesson_suggestions(limit: int = 5) -> list[dict]:
    """Top rejection reasons NOT covered by any existing lesson rule.

    Counts are recomputed from list_track_record() exactly like
    get_anti_patterns does internally (distilled reason preferred); coverage
    is checked against every parseable lessons.md rule — active, draft AND
    retired — so re-proposing something a human already retired is avoided.
    Returns [{"reason", "count"}] ranked by count desc, then reason asc;
    capped at `limit`. Deliberately uncached like get_active_lessons.
    """
    limit = max(1, int(limit))
    counter: Counter[str] = Counter()
    for row in list_track_record():
        if (row.get("verdict") or "").strip().lower() != "reject":
            continue
        reason = (row.get("distilled") or row.get("reason") or "").strip()
        if not reason:
            continue
        counter[normalize_text(reason)[:280]] += 1

    try:
        text = resolve_lessons_path().read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    rules = [lesson["rule"] for lesson in _parse_all_lessons(text)]

    ranked = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    suggestions: list[dict] = []
    for reason, count in ranked:
        if len(suggestions) >= limit:
            break
        if _covered_by_rules(reason, rules):
            continue
        suggestions.append({"reason": reason, "count": count})
    return suggestions
