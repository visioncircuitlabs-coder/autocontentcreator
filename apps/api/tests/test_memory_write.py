"""Memory write path: every human yes/no lands in the markdown memory.

Real API flow (radar fixture -> factory run -> review) plus the ops
/memory/rebuild endpoint, all against a temp MEMORY_DIR so the suite
never touches the developer's real brand memory.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def isolate_memory_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Mirror conftest's SQLITE_PATH isolation for the markdown store."""
    mem = tmp_path / "memory"
    monkeypatch.setenv("MEMORY_DIR", str(mem))
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    return mem


@pytest.fixture(autouse=True)
def stub_image_gen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Factory runs paint stub PNGs into tmp, never the network."""
    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    monkeypatch.setenv("IMAGE_OUT_DIR", str(tmp_path / "images"))


def _make_draft(client: TestClient) -> dict:
    """radar fixture -> factory run -> one queued draft dict."""
    from boxes.fixture_dive import FIXTURE_REPORT_ID

    res = client.post("/radar/fixture")
    assert res.status_code == 200, res.text
    res = client.post("/factory/run", json={"report_id": FIXTURE_REPORT_ID})
    assert res.status_code == 200, res.text
    drafts = res.json()
    assert drafts, "factory run must queue at least one draft"
    return drafts[0]


def test_approve_writes_ledger_entry(isolate_memory_dir: Path) -> None:
    from main import app

    client = TestClient(app)
    draft = _make_draft(client)
    res = client.post(
        f"/review/{draft['draft_id']}",
        json={
            "user": "alice",
            "verdict": "approve",
            "reason": "On-brand and claim-safe.",
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["verdict"] == "approve"
    assert body["user"] == "alice"

    ledger = isolate_memory_dir / "LEDGER.md"
    assert ledger.is_file(), sorted(
        str(p.relative_to(isolate_memory_dir))
        for p in isolate_memory_dir.rglob("*")
    )
    text = ledger.read_text(encoding="utf-8")
    assert draft["draft_id"] in text
    assert "alice" in text
    assert "approve" in text.lower()


def test_blank_reason_rejected_and_writes_nothing(
    isolate_memory_dir: Path,
) -> None:
    from db import list_decisions, list_track_record
    from main import app

    client = TestClient(app)
    draft = _make_draft(client)
    res = client.post(
        f"/review/{draft['draft_id']}",
        json={"user": "alice", "verdict": "reject", "reason": "   "},
    )
    assert res.status_code in (400, 422)
    body = res.json()
    assert "error" in body or "detail" in body
    assert "stack" not in str(body).lower()
    assert "trace" not in str(body).lower()

    assert list_decisions() == []
    assert list_track_record() == []
    assert not (isolate_memory_dir / "LEDGER.md").exists()


def test_memory_rebuild_open_mode_lists_seed_files(
    isolate_memory_dir: Path,
) -> None:
    from db import init_db
    from main import app

    init_db()
    client = TestClient(app)
    res = client.post("/memory/rebuild")  # no key: open mode when none exist
    assert res.status_code == 200, res.text
    body = res.json()
    names = "\n".join(str(item) for item in body.get("files", []))
    # Fresh dir: rebuild writes LEDGER.md AND seeds lessons.md itself,
    # so both names come back in the written-files list.
    assert "ledger.md" in names.lower()
    assert "lessons.md" in names.lower()
    assert isinstance(body.get("ledger_entries"), int)
    # lessons.md really is on disk afterwards.
    assert (isolate_memory_dir / "lessons.md").is_file()


def test_memory_rebuild_needs_admin_role(isolate_memory_dir: Path) -> None:
    from boxes.auth import create_key
    from boxes.memory_store import ensure_seed_files
    from db import init_db
    from main import app

    init_db()
    ensure_seed_files()
    admin_key = create_key("boss", "admin")
    approver_key = create_key("ops", "approver")
    client = TestClient(app)

    denied = client.post("/memory/rebuild", headers={"x-api-key": approver_key})
    assert denied.status_code == 401
    assert "error" in denied.json()

    ok = client.post("/memory/rebuild", headers={"x-api-key": admin_key})
    assert ok.status_code == 200, ok.text
    assert isinstance(ok.json().get("ledger_entries"), int)


def test_memory_failure_does_not_break_approval(
    isolate_memory_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import boxes.memory_store as memory_store
    from db import list_decisions, list_events
    from main import app

    def boom(entry: dict) -> None:
        raise RuntimeError("disk on fire")

    monkeypatch.setattr(memory_store, "record_decision", boom)

    client = TestClient(app)
    draft = _make_draft(client)
    res = client.post(
        f"/review/{draft['draft_id']}",
        json={
            "user": "priya",
            "verdict": "approve",
            "reason": "Fine for the feed.",
        },
    )

    assert res.status_code == 200, res.text
    stored = [d for d in list_decisions() if d.draft_id == draft["draft_id"]]
    assert len(stored) == 1
    kinds = {event["kind"] for event in list_events(500)}
    assert "memory_mirror_fail" in kinds


def test_startup_seeds_memory_files(isolate_memory_dir: Path) -> None:
    from main import app

    with TestClient(app):  # lifespan runs startup incl. ensure_seed_files
        pass
    # Boot seeds lessons.md only; LEDGER.md appears with the first decision.
    assert (isolate_memory_dir / "lessons.md").is_file()
    assert "Brand Lessons" in (isolate_memory_dir / "lessons.md").read_text(
        encoding="utf-8"
    )
