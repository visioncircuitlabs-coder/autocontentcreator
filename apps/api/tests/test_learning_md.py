"""Markdown lessons file: tolerant parser + prompt wiring.

Covers boxes/learning.resolve_lessons_path / get_active_lessons and the
<lessons> tag folded into learning_block output. The lessons.md format is
the human-editable contract shared with boxes/memory_store.py:

    # Brand Lessons

    <any prose>

    ### les_001
    - status: active
    - scope: global
    - rule: One-line rule text here.
    - source: where it came from
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from boxes import learning
from db import insert_track_record

WELL_FORMED = """\
# Brand Lessons

Rules humans wrote by hand. Edit freely.

### les_001
- status: active
- scope: global
- rule: Never promise cures; describe relief instead.
- source: review round 12

### les_002
- status: retired
- scope: instagram
- rule: Old monsoon-post rule we dropped.
- source: legacy import
"""


@pytest.fixture(autouse=True)
def _isolated_memory_dir(tmp_path, monkeypatch):
    """Point MEMORY_DIR at a fresh dir and keep the ledger cache empty."""
    monkeypatch.setenv("MEMORY_DIR", str(tmp_path))
    learning.reset_learning_cache()
    yield
    learning.reset_learning_cache()


# --- resolve_lessons_path ----------------------------------------------------


def test_resolve_lessons_path_defaults_to_data_memory(monkeypatch):
    monkeypatch.delenv("MEMORY_DIR", raising=False)
    assert learning.resolve_lessons_path().as_posix().endswith(
        "data/memory/lessons.md"
    )


def test_resolve_lessons_path_honors_memory_dir_env(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_DIR", str(tmp_path / "custom"))
    resolved = learning.resolve_lessons_path()
    assert resolved == tmp_path / "custom" / "lessons.md"


# --- get_active_lessons: parsing ----------------------------------------------


def test_parses_active_block_with_all_fields(tmp_path):
    path = tmp_path / "lessons.md"
    path.write_text(WELL_FORMED, encoding="utf-8")
    lessons = learning.get_active_lessons(path)
    assert len(lessons) == 1, "only the active block is returned"
    lesson = lessons[0]
    assert lesson["id"] == "les_001"
    assert lesson["status"].lower() == "active"
    assert lesson["scope"] == "global"
    assert lesson["rule"] == "Never promise cures; describe relief instead."
    assert lesson["source"] == "review round 12"


def test_status_comparison_is_case_insensitive(tmp_path):
    path = tmp_path / "lessons.md"
    path.write_text(
        "### les_009\n- status: ACTIVE\n- scope: reels\n- rule: Keep hooks short.\n",
        encoding="utf-8",
    )
    lessons = learning.get_active_lessons(path)
    assert [lesson["id"] for lesson in lessons] == ["les_009"]


def test_retired_only_file_yields_no_lessons(tmp_path):
    path = tmp_path / "lessons.md"
    path.write_text(
        "### les_002\n- status: retired\n- scope: global\n- rule: Gone.\n",
        encoding="utf-8",
    )
    assert learning.get_active_lessons(path) == []


def test_unknown_fields_and_prose_ignored(tmp_path):
    path = tmp_path / "lessons.md"
    path.write_text(
        "# Brand Lessons\n\n"
        "Freeform prose between blocks must not break anything.\n\n"
        "### not_a_lesson\n- status: active\n- scope: wrong-heading\n\n"
        "### les_003\n"
        "- owner: riya\n"
        "- priority: high\n"
        "- status: active\n"
        "- scope: packaging\n"
        "- rule: Name the ingredient before the benefit.\n"
        "- source: brand review\n"
        "- notes: this extra field is ignored\n",
        encoding="utf-8",
    )
    lessons = learning.get_active_lessons(path)
    assert len(lessons) == 1
    assert lessons[0]["id"] == "les_003"
    assert lessons[0]["scope"] == "packaging"


def test_malformed_file_never_raises(tmp_path):
    """Random prose, broken fields, missing rules -> [] or partial, no exception."""
    garbage = (
        "this is not markdown at all\n"
        "### les_broken\n"
        "- status active (missing colon)\n"
        "- :value with no key\n"
        "- rule: \n"
        "#### deep heading ###\n"
        "### les_missing_rule\n"
        "- status: active\n"
        "- scope: global\n"
        "&&& total nonsense &&&\n"
        "### les_ok\n"
        "- status: Active\n"
        "- rule: Survivors still parse.\n"
    )
    path = tmp_path / "lessons.md"
    path.write_text(garbage, encoding="utf-8")
    lessons = learning.get_active_lessons(path)
    assert isinstance(lessons, list)
    assert [lesson["id"] for lesson in lessons] == ["les_ok"]
    assert lessons[0]["rule"] == "Survivors still parse."


def test_pure_garbage_file_yields_empty_list(tmp_path):
    path = tmp_path / "lessons.md"
    path.write_text("just some prose\nwith no lesson blocks\n", encoding="utf-8")
    assert learning.get_active_lessons(path) == []


def test_empty_file_yields_empty_list(tmp_path):
    path = tmp_path / "lessons.md"
    path.write_text("", encoding="utf-8")
    assert learning.get_active_lessons(path) == []


def test_missing_file_returns_empty_list(tmp_path):
    assert learning.get_active_lessons(tmp_path / "nope" / "lessons.md") == []


def test_default_path_used_when_none_given(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_DIR", str(tmp_path))
    (tmp_path / "lessons.md").write_text(
        "### les_env\n- status: active\n- scope: global\n- rule: Env path works.\n",
        encoding="utf-8",
    )
    lessons = learning.get_active_lessons()
    assert [lesson["rule"] for lesson in lessons] == ["Env path works."]


def test_no_caching_rereads_edits(tmp_path):
    path = tmp_path / "lessons.md"
    path.write_text(
        "### les_live\n- status: active\n- scope: global\n- rule: Before edit.\n",
        encoding="utf-8",
    )
    assert learning.get_active_lessons(path)[0]["rule"] == "Before edit."
    path.write_text(
        "### les_live\n- status: active\n- scope: global\n- rule: After edit.\n",
        encoding="utf-8",
    )
    assert learning.get_active_lessons(path)[0]["rule"] == "After edit."


# --- learning_block wiring -----------------------------------------------------


def test_learning_block_appends_lessons_tag_when_ledger_empty():
    lessons_md = learning.resolve_lessons_path()
    lessons_md.parent.mkdir(parents=True, exist_ok=True)
    lessons_md.write_text(WELL_FORMED, encoding="utf-8")
    # conftest isolates SQLITE_PATH per-test, so the track-record ledger is empty.
    text, n_winners, n_avoid = learning.learning_block()
    assert "<lessons>" in text and "</lessons>" in text
    assert "[global] Never promise cures; describe relief instead." in text
    assert "Old monsoon-post rule" not in text, "retired lessons stay out"
    assert (n_winners, n_avoid) == (0, 0)


def test_learning_block_still_returns_empty_when_everything_empty():
    text, n_winners, n_avoid = learning.learning_block()
    assert text == ""
    assert (n_winners, n_avoid) == (0, 0)


# --- get_lesson_suggestions ----------------------------------------------------


BASE = datetime(2026, 8, 24, 10, 0, 0, tzinfo=timezone.utc)

REASON_COVERED = "sounds like an ad not a friend"
REASON_UNCOVERED_A = "emoji walls bury the message"
REASON_UNCOVERED_B = "price shock in the first line"


def _seed_reject(distilled: str, draft_id: str, minutes: int = 0) -> None:
    """Route one rejection through the real SQLite write path."""
    insert_track_record(
        {
            "draft_id": draft_id,
            "decided_at": (BASE + timedelta(minutes=minutes)).isoformat(),
            "user": "riya",
            "verdict": "reject",
            "reason": distilled,
            "distilled": distilled,
            "caption": f"caption {draft_id}",
            "judge": None,
            "sku": "DEMO-HYDRO-BOOST",
            "market": "IN",
            "flag_human": False,
        }
    )
    learning.reset_learning_cache()


def _write_lessons_rule(rule: str, status: str = "active") -> None:
    lessons_md = learning.resolve_lessons_path()
    lessons_md.parent.mkdir(parents=True, exist_ok=True)
    lessons_md.write_text(
        "# Brand Lessons\n\n"
        f"### les_001\n- status: {status}\n- scope: global\n"
        f"- rule: {rule}\n- source: human review\n",
        encoding="utf-8",
    )


def test_get_lesson_suggestions_excludes_covered_includes_uncovered():
    _seed_reject(REASON_COVERED, "dft_a1")
    _seed_reject(REASON_COVERED, "dft_a2", minutes=1)
    _seed_reject(REASON_UNCOVERED_B, "dft_b1", minutes=2)
    _seed_reject(REASON_UNCOVERED_A, "dft_c1", minutes=3)
    # Rule embeds a 4-word contiguous slice of REASON_COVERED verbatim.
    _write_lessons_rule("Anything that sounds like an ad not a friend is out.")

    suggestions = learning.get_lesson_suggestions()

    assert suggestions == [
        {"reason": REASON_UNCOVERED_A, "count": 1},
        {"reason": REASON_UNCOVERED_B, "count": 1},
    ], "the covered reason never comes back, uncovered ones do"
    assert learning.get_lesson_suggestions(limit=1) == [
        {"reason": REASON_UNCOVERED_A, "count": 1}
    ]


def test_get_lesson_suggestions_treats_draft_and_retired_rules_as_coverage():
    _seed_reject(REASON_COVERED, "dft_r1")
    for status in ("draft", "retired"):
        _write_lessons_rule(
            "Anything that sounds like an ad not a friend is out.", status=status
        )
        assert learning.get_lesson_suggestions() == []


def test_get_lesson_suggestions_empty_when_no_rejections():
    assert learning.get_lesson_suggestions() == []
