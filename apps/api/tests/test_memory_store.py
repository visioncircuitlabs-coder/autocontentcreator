"""Brand memory store tests: markdown mirror of the track_record ledger."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from boxes import learning, memory_store
from db import init_db, insert_track_record

BASE = datetime(2026, 8, 24, 10, 0, 0, tzinfo=timezone.utc)

CAPTION_WIN = "Gel first. Panic later."
CAPTION_BANNED = "Night shift ends, gel goes on first. Dermatologist tested."

EXPECTED_LESSONS_SEED = (
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


@pytest.fixture()
def mem_dir(monkeypatch, tmp_path) -> Path:
    """Isolated SQLite + MEMORY_DIR, mirroring conftest's SQLITE_PATH isolation."""
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "mem.db"))
    memory_dir = tmp_path / "memory"
    monkeypatch.setenv("MEMORY_DIR", str(memory_dir))
    init_db()
    learning.reset_learning_cache()
    yield memory_dir
    learning.reset_learning_cache()


def _entry(draft_id: str = "dft_m1", minutes: int = 0, **overrides) -> dict:
    """Entry shaped exactly like feedback.write_feedback()'s return value."""
    entry = {
        "draft_id": draft_id,
        "decided_at": (BASE + timedelta(minutes=minutes)).isoformat(),
        "user": "riya",
        "verdict": "approve",
        "reason": "on-voice gel moment",
        "distilled": "on-voice gel moment",
        "caption": CAPTION_WIN,
        "judge": None,
        "sku": "DEMO-HYDRO-BOOST",
        "market": "IN",
        "flag_human": False,
    }
    entry.update(overrides)
    return entry


def _seed(entry: dict) -> None:
    """Route through the real SQLite write path, then drop the read cache."""
    insert_track_record(entry)
    learning.reset_learning_cache()


def _ledger(mem_dir: Path) -> str:
    return (mem_dir / "LEDGER.md").read_text(encoding="utf-8")


def _headings(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("## ")]


# --- resolve_memory_dir ------------------------------------------------------


def test_resolve_memory_dir_honors_env(monkeypatch, tmp_path):
    monkeypatch.setenv("MEMORY_DIR", str(tmp_path / "custom"))
    assert memory_store.resolve_memory_dir() == tmp_path / "custom"


def test_resolve_memory_dir_defaults_to_data_memory(monkeypatch):
    monkeypatch.delenv("MEMORY_DIR", raising=False)
    assert memory_store.resolve_memory_dir() == Path("data/memory")


# --- record_decision ---------------------------------------------------------


def test_record_decision_creates_ledger_with_verdict_and_draft(mem_dir):
    memory_store.record_decision(_entry())
    text = _ledger(mem_dir)
    assert text.startswith("# Decision Ledger\n\n")
    assert f"## {BASE.isoformat()} — dft_m1 — APPROVE" in text
    assert "- by: riya" in text
    assert "- market: IN · sku: DEMO-HYDRO-BOOST" in text
    assert "- why: on-voice gel moment" in text


def test_record_decision_degrades_on_missing_optional_keys(mem_dir):
    sparse = {
        "draft_id": "dft_sparse",
        "decided_at": BASE.isoformat(),
        "verdict": "reject",
    }
    memory_store.record_decision(sparse)
    text = _ledger(mem_dir)
    assert f"## {BASE.isoformat()} — dft_sparse — REJECT" in text
    assert "- by: " in text
    assert "- market:  · sku: " in text


def test_record_decision_is_idempotent_per_draft_and_time(mem_dir):
    entry = _entry()
    memory_store.record_decision(entry)
    memory_store.record_decision(entry)
    assert len(_headings(_ledger(mem_dir))) == 1


def test_skipped_duplicate_still_refreshes_aggregates(mem_dir):
    entry = _entry()
    memory_store.record_decision(entry)
    (mem_dir / "winners.md").unlink()
    memory_store.record_decision(entry)  # duplicate: skipped append, fresh render
    assert (mem_dir / "winners.md").exists()


def test_same_draft_new_timestamp_is_a_separate_entry(mem_dir):
    memory_store.record_decision(_entry())
    memory_store.record_decision(_entry(minutes=5, verdict="reject"))
    assert len(_headings(_ledger(mem_dir))) == 2


# --- refresh_aggregates --------------------------------------------------------


def test_refresh_aggregates_renders_winners_from_track_record(mem_dir):
    _seed(_entry("dft_w1", minutes=0))
    _seed(_entry("dft_w2", minutes=5, user="arjun"))
    memory_store.refresh_aggregates()
    text = (mem_dir / "winners.md").read_text(encoding="utf-8")
    assert text.startswith(
        "# Winners\n\nRanked approved captions (win rate). "
        "Machine-generated; regenerate with POST /memory/rebuild.\n\n"
    )
    assert f"## {CAPTION_WIN}\n\n- wins: 2 of 2 decisions" in text


def test_refresh_aggregates_renders_anti_patterns(mem_dir):
    _seed(
        _entry(
            "dft_r1",
            verdict="reject",
            reason="off-brand tone",
            distilled="off-brand tone",
        )
    )
    memory_store.refresh_aggregates()
    text = (mem_dir / "anti-patterns.md").read_text(encoding="utf-8")
    assert text == (
        "# Anti-patterns\n\n"
        "Most common rejection reasons. Machine-generated.\n\n"
        "- off-brand tone\n"
    )


def test_refresh_aggregates_renders_hard_bans(mem_dir):
    _seed(
        _entry(
            "dft_b1",
            verdict="reject",
            caption=CAPTION_BANNED,
            reason="off-brand: reads like an ad",
            distilled="off-brand: reads like an ad",
        )
    )
    _seed(
        _entry(
            "dft_b2",
            minutes=5,
            verdict="reject",
            caption=CAPTION_BANNED,
            reason="off-brand tone",
            distilled="off-brand tone",
        )
    )
    memory_store.refresh_aggregates()
    text = (mem_dir / "bans.md").read_text(encoding="utf-8")
    assert text.startswith("# Hard bans\n\n")
    assert (
        f"- {learning.normalize_text(CAPTION_BANNED)}\n"
        "  - category: off-brand (2 rejects)\n"
    ) in text


def test_refresh_aggregates_empty_states(mem_dir):
    memory_store.refresh_aggregates()
    assert (mem_dir / "winners.md").read_text(encoding="utf-8") == (
        "# Winners\n\nNo approved exemplars yet.\n"
    )
    assert (mem_dir / "anti-patterns.md").read_text(encoding="utf-8") == (
        "# Anti-patterns\n\nNothing rejected yet.\n"
    )
    assert (mem_dir / "bans.md").read_text(encoding="utf-8") == (
        "# Hard bans\n\nNo hard bans yet.\n"
    )


# --- ensure_seed_files ---------------------------------------------------------


def test_ensure_seed_files_creates_lessons_once(mem_dir):
    memory_store.ensure_seed_files()
    lessons = mem_dir / "lessons.md"
    assert lessons.read_text(encoding="utf-8") == EXPECTED_LESSONS_SEED

    lessons.write_text(
        EXPECTED_LESSONS_SEED + "\n### les_002\n- status: active\n", encoding="utf-8"
    )
    memory_store.ensure_seed_files()  # second call must be a no-op
    assert lessons.read_text(encoding="utf-8") == (
        EXPECTED_LESSONS_SEED + "\n### les_002\n- status: active\n"
    )


# --- rebuild_all -----------------------------------------------------------------


def test_rebuild_all_regenerates_corrupted_ledger_oldest_first(mem_dir):
    _seed(_entry("dft_old", minutes=0))
    _seed(_entry("dft_mid", minutes=10, verdict="reject"))
    _seed(_entry("dft_new", minutes=20, user="arjun"))

    memory_store.ensure_seed_files()
    lessons = mem_dir / "lessons.md"
    lessons.write_text(EXPECTED_LESSONS_SEED + "\nHuman note: keep this.\n", encoding="utf-8")

    (mem_dir / "LEDGER.md").write_text("CORRUPTED GARBAGE", encoding="utf-8")
    result = memory_store.rebuild_all()

    text = _ledger(mem_dir)
    headings = _headings(text)
    assert len(headings) == 3
    assert "— dft_old — APPROVE" in headings[0]
    assert "— dft_mid — REJECT" in headings[1]
    assert "— dft_new — APPROVE" in headings[2]
    assert result["ledger_entries"] == 3
    assert set(result["files"]) == {
        "LEDGER.md",
        "winners.md",
        "anti-patterns.md",
        "bans.md",
    }
    assert lessons.read_text(encoding="utf-8").endswith("Human note: keep this.\n")


def test_rebuild_all_recreates_deleted_ledger(mem_dir):
    _seed(_entry("dft_solo"))
    memory_store.record_decision(_entry())  # ledger exists once...
    (mem_dir / "LEDGER.md").unlink()  # ...then vanishes
    result = memory_store.rebuild_all()

    text = _ledger(mem_dir)
    assert text.startswith("# Decision Ledger\n\n")
    assert len(_headings(text)) == 1
    assert result["ledger_entries"] == 1
    assert (mem_dir / "lessons.md").read_text(encoding="utf-8") == EXPECTED_LESSONS_SEED


def test_rebuild_all_can_reset_lessons_when_not_preserved(mem_dir):
    memory_store.ensure_seed_files()
    lessons = mem_dir / "lessons.md"
    lessons.write_text(EXPECTED_LESSONS_SEED + "\nHuman note: gone soon.\n", encoding="utf-8")

    result = memory_store.rebuild_all(preserve_lessons=False)

    assert lessons.read_text(encoding="utf-8") == EXPECTED_LESSONS_SEED
    assert "lessons.md" in result["files"]


# --- friendly errors -------------------------------------------------------------


def test_unwritable_memory_dir_raises_friendly_error(monkeypatch, tmp_path):
    blocker = tmp_path / "blocker.file"
    blocker.write_text("a file, not a directory", encoding="utf-8")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "err.db"))
    init_db()
    monkeypatch.setenv("MEMORY_DIR", str(blocker / "memory"))

    with pytest.raises(ValueError, match="Could not write brand memory files"):
        memory_store.record_decision(_entry())

    with pytest.raises(ValueError, match="Could not write brand memory files"):
        memory_store.rebuild_all()


# --- pre-rebuild checkpoints -----------------------------------------------------


def _populate_memory_dir(mem_dir: Path) -> None:
    """Give the memory dir all five .md files via the real write paths."""
    _seed(_entry("dft_cp"))
    memory_store.record_decision(_entry())
    memory_store.ensure_seed_files()


def test_rebuild_all_checkpoints_prior_files_before_rewrite(mem_dir):
    _populate_memory_dir(mem_dir)
    (mem_dir / "winners.md").write_text("STALE RENDER", encoding="utf-8")

    result = memory_store.rebuild_all()

    assert memory_store.list_checkpoints() == ["cp_001"]
    saved = (mem_dir / ".checkpoints" / "cp_001" / "winners.md")
    assert saved.read_text(encoding="utf-8") == "STALE RENDER"
    assert (mem_dir / "winners.md").read_text(encoding="utf-8") != "STALE RENDER"
    assert ".checkpoints" not in result["files"]


def test_second_rebuild_gets_next_sequential_checkpoint(mem_dir):
    _populate_memory_dir(mem_dir)

    memory_store.rebuild_all()
    memory_store.rebuild_all()

    assert memory_store.list_checkpoints() == ["cp_001", "cp_002"]


def test_checkpoint_pruning_keeps_only_latest_five_sorted(mem_dir):
    _populate_memory_dir(mem_dir)

    for _ in range(7):
        memory_store.rebuild_all()

    checkpoints = memory_store.list_checkpoints()
    assert len(checkpoints) == 5
    assert checkpoints == sorted(checkpoints)
    assert checkpoints == ["cp_003", "cp_004", "cp_005", "cp_006", "cp_007"]
    for pruned in ("cp_001", "cp_002"):
        assert not (mem_dir / ".checkpoints" / pruned).exists()


def test_rebuild_with_empty_memory_dir_creates_no_checkpoint(mem_dir):
    result = memory_store.rebuild_all()

    assert not (mem_dir / ".checkpoints").exists()
    assert memory_store.list_checkpoints() == []
    assert ".checkpoints" not in result["files"]


# --- append_draft_lesson -----------------------------------------------------------


def test_append_draft_lesson_appends_next_id_as_draft(mem_dir):
    memory_store.ensure_seed_files()
    new_id = memory_store.append_draft_lesson(
        "Never open with a discount code.",
        source="anti-pattern watcher",
        scope="reels",
    )

    assert new_id == "les_002"
    text = (mem_dir / "lessons.md").read_text(encoding="utf-8")
    assert (
        "\n### les_002\n"
        "- status: draft\n"
        "- scope: reels\n"
        "- rule: Never open with a discount code.\n"
        "- source: anti-pattern watcher\n"
    ) in text

    # Drafts are invisible to the active-only public parser...
    assert [lesson["id"] for lesson in learning.get_active_lessons()] == ["les_001"]

    # ...until a human promotes one by flipping status in the file.
    (mem_dir / "lessons.md").write_text(
        text.replace("### les_002\n- status: draft", "### les_002\n- status: active"),
        encoding="utf-8",
    )
    assert [lesson["id"] for lesson in learning.get_active_lessons()] == [
        "les_001",
        "les_002",
    ]


def test_append_draft_lesson_dedupe_returns_existing_id_without_appending(mem_dir):
    memory_store.ensure_seed_files()

    first = memory_store.append_draft_lesson("Keep hooks under twelve words.")
    duplicate = memory_store.append_draft_lesson("  keep   HOOKS under twelve words. ")
    hits_active_seed = memory_store.append_draft_lesson(
        "Open with the skin moment, never with the brand name."
    )
    retired_does_not_block = memory_store.append_draft_lesson("Gone.")

    assert first == "les_002"
    assert duplicate == first, "normalized rule match returns the existing id"
    assert hits_active_seed == "les_001"
    assert retired_does_not_block == "les_003", "retired rules don't block re-proposal"

    text = (mem_dir / "lessons.md").read_text(encoding="utf-8")
    assert text.count("### les_") == 3  # seed + exactly two drafts, no dupes


def test_append_draft_lesson_unwritable_memory_dir_raises_friendly_error(
    monkeypatch, tmp_path
):
    blocker = tmp_path / "blocker.file"
    blocker.write_text("a file, not a directory", encoding="utf-8")
    monkeypatch.setenv("MEMORY_DIR", str(blocker / "memory"))

    with pytest.raises(ValueError, match="Could not write brand memory files"):
        memory_store.append_draft_lesson("A rule that will never land.")
