"""Brand Memory — the human-readable Markdown mirror of the SQLite ledger.

Two stores, one truth. SQLite (db.py) is the machine-speed source of record:
boxes.feedback.write_feedback() inserts every approve/reject into the
track_record table, and boxes.learning distills exemplars, anti-patterns and
hard bans from it at query time. This module renders that SAME data as five
small markdown files under a memory directory, because humans review diffs in
git — not SQL rows:

- LEDGER.md        append-only decision log (one entry per decision)
- winners.md       approved captions ranked by win rate
- anti-patterns.md most common rejection reasons
- bans.md          normalized captions rejected 2+ times for one category
- lessons.md       human-editable brand rules (seeded once; never clobbered)

The shape is Palantir-ontology-inspired: a decision is a first-class object a
person can read without opening a database shell. It is Claude-memory-tool
inspired too: memory lives in readable files over opaque blobs, so any editor
plus git can act as the UI. SQLite stays authoritative — every file here is
disposable and fully regenerable from list_track_record() via rebuild_all().
No LLM, no network, fully deterministic.

Where the files live comes from resolve_memory_dir(): the MEMORY_DIR env var
if set, else "data/memory" relative to the api root — mirroring how db.py
resolves DEFAULT_SQLITE_PATH="data/demo.db". Whole-file rewrites are atomic
(sibling tmp file, then os.replace); LEDGER.md grows by plain open-append.
Filesystem failures surface as a friendly ValueError instead of raw OSErrors.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from boxes import learning
from db import list_track_record

DEFAULT_MEMORY_DIR = "data/memory"

LEDGER_NAME = "LEDGER.md"
WINNERS_NAME = "winners.md"
ANTI_PATTERNS_NAME = "anti-patterns.md"
BANS_NAME = "bans.md"
LESSONS_NAME = "lessons.md"

LEDGER_HEADER = "# Decision Ledger\n\n"

# Humans edit lessons.md by hand; rebuild must never clobber it. Seed only.
LESSONS_SEED = (
    "# Brand Lessons\n"
    "\n"
    "Human-editable rules distilled from decisions. The machine reads every\n"
    "### lesson block; set status to retired to retire one. Do not change the\n"
    "block format — unparsable blocks are skipped silently.\n"
    "\n"
    "### les_001\n"
    "- status: active\n"
    "- scope: global\n"
    "- rule: Open with the skin moment, never with the brand name.\n"
    "- source: standing rule, demo fixture\n"
)


def resolve_memory_dir() -> Path:
    """Memory directory: $MEMORY_DIR when set, else data/memory (api root)."""
    return Path(os.environ.get("MEMORY_DIR", DEFAULT_MEMORY_DIR))


def _friendly_error() -> ValueError:
    """Operator-facing wrapper for memory-directory write failures."""
    return ValueError(
        "Could not write brand memory files. Check that "
        f"{resolve_memory_dir()} is writable."
    )


def _atomic_write(path: Path, text: str) -> None:
    """Rewrite a whole file atomically: sibling tmp first, then os.replace."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
            os.replace(tmp_name, path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
    except OSError as exc:
        raise _friendly_error() from exc


def _render_entry(row: dict) -> str:
    """One ledger block. Missing optional keys degrade to empty strings."""
    decided_at = str(row.get("decided_at") or "")
    draft_id = str(row.get("draft_id") or "")
    verdict = str(row.get("verdict") or "").strip().upper()
    user = str(row.get("user") or "")
    market = str(row.get("market") or "")
    sku = str(row.get("sku") or "")
    distilled = str(row.get("distilled") or "")
    return (
        f"## {decided_at} — {draft_id} — {verdict}\n"
        f"- by: {user}\n"
        f"- market: {market} · sku: {sku}\n"
        f"- why: {distilled}\n"
        "\n"
    )


def _has_entry(text: str, draft_id: object, decided_at: object) -> bool:
    """True when a heading already names both this draft_id and decided_at."""
    want_draft = str(draft_id or "")
    want_time = str(decided_at or "")
    if not want_draft or not want_time:
        return False
    for line in text.splitlines():
        if line.startswith("## ") and want_draft in line and want_time in line:
            return True
    return False


def record_decision(entry: dict) -> None:
    """Append one decision to LEDGER.md, then refresh the aggregate files.

    Idempotent per (draft_id, decided_at): a duplicate is not appended again,
    but aggregates still refresh so a wiped render self-heals.
    """
    row = dict(entry or {})
    ledger_path = resolve_memory_dir() / LEDGER_NAME
    chunk = _render_entry(row)
    try:
        exists = ledger_path.exists()
        current = ledger_path.read_text(encoding="utf-8") if exists else ""
        if not _has_entry(current, row.get("draft_id"), row.get("decided_at")):
            prefix = "" if exists else LEDGER_HEADER
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with open(ledger_path, "a", encoding="utf-8", newline="\n") as handle:
                handle.write(prefix + chunk)
    except OSError as exc:
        raise _friendly_error() from exc
    refresh_aggregates()


def refresh_aggregates() -> None:
    """Re-render winners/anti-patterns/bans from SQLite (cache dropped first)."""
    learning.reset_learning_cache()
    winners = learning.get_exemplars()
    anti_patterns = learning.get_anti_patterns()
    bans = learning.get_hard_bans()

    if winners:
        winners_text = (
            "# Winners\n\n"
            "Ranked approved captions (win rate). Machine-generated; "
            "regenerate with POST /memory/rebuild.\n\n"
        )
        winners_text += "".join(
            f"## {item['caption']}\n\n"
            f"- wins: {item['wins']} of {item['decisions']} decisions\n\n"
            for item in winners
        )
    else:
        winners_text = "# Winners\n\nNo approved exemplars yet.\n"

    if anti_patterns:
        anti_text = (
            "# Anti-patterns\n\n"
            "Most common rejection reasons. Machine-generated.\n\n"
        )
        anti_text += "".join(f"- {reason}\n" for reason in anti_patterns)
    else:
        anti_text = "# Anti-patterns\n\nNothing rejected yet.\n"

    if bans:
        bans_text = (
            "# Hard bans\n\n"
            "Normalized captions rejected 2+ times for one category — never "
            "regenerated. Machine-generated.\n\n"
        )
        bans_text += "".join(
            f"- {ban['normalized']}\n"
            f"  - category: {ban['category']} ({ban['rejects']} rejects)\n"
            for ban in bans
        )
    else:
        bans_text = "# Hard bans\n\nNo hard bans yet.\n"

    root = resolve_memory_dir()
    _atomic_write(root / WINNERS_NAME, winners_text)
    _atomic_write(root / ANTI_PATTERNS_NAME, anti_text)
    _atomic_write(root / BANS_NAME, bans_text)


def ensure_seed_files() -> None:
    """Create lessons.md with the seed content only when it is missing."""
    lessons_path = resolve_memory_dir() / LESSONS_NAME
    try:
        if lessons_path.exists():
            return
    except OSError as exc:
        raise _friendly_error() from exc
    _atomic_write(lessons_path, LESSONS_SEED)


def rebuild_all(preserve_lessons: bool = True) -> dict:
    """Regenerate all five memory files from SQLite, the source of truth.

    LEDGER.md is rebuilt oldest-first from list_track_record(); aggregates go
    through refresh_aggregates(). An existing lessons.md survives unless
    preserve_lessons=False (or the file was missing, in which case it is
    seeded fresh). Returns {"files": [...written...], "ledger_entries": N}.
    """
    rows = list(reversed(list_track_record()))  # oldest first
    ledger_text = LEDGER_HEADER + "".join(_render_entry(row) for row in rows)
    _atomic_write(resolve_memory_dir() / LEDGER_NAME, ledger_text)

    refresh_aggregates()

    written = [LEDGER_NAME, WINNERS_NAME, ANTI_PATTERNS_NAME, BANS_NAME]
    lessons_path = resolve_memory_dir() / LESSONS_NAME
    if not (preserve_lessons and lessons_path.exists()):
        _atomic_write(lessons_path, LESSONS_SEED)
        written.append(LESSONS_NAME)
    return {"files": written, "ledger_entries": len(rows)}
