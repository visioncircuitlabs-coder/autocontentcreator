"""Runs ledger + resume tests. Deterministic, no network."""

from __future__ import annotations

import pytest

from db import create_run, get_run, list_runs, record_step_result, update_run


@pytest.fixture()
def run_db(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "runs.db"))
    from db import init_db

    init_db()
    yield


def test_run_lifecycle(run_db):
    run = create_run("factory", params={"report_id": "rep_x"})
    assert run["status"] == "running"
    record_step_result(run["run_id"], {"name": "brief", "ok": True, "ms": 5, "attempts": 1})
    row = update_run(run["run_id"], status="done")
    assert row["status"] == "done"
    fresh = get_run(run["run_id"])
    assert [s["name"] for s in fresh["step_results"]] == ["brief"]


def test_step_results_replace_in_place(run_db):
    run = create_run("radar")
    record_step_result(run["run_id"], {"name": "fetch", "ok": False, "ms": 1})
    record_step_result(run["run_id"], {"name": "fetch", "ok": True, "ms": 9})
    steps = get_run(run["run_id"])["step_results"]
    assert len(steps) == 1
    assert steps[0]["ok"] is True


def test_interrupted_detection(run_db):
    from datetime import datetime, timedelta, timezone

    run = create_run("factory")
    stale_then = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()

    # simulate a row untouched for 45 minutes
    import sqlite3

    from db import connect

    conn = connect()
    conn.execute(
        "UPDATE runs SET updated_at = ? WHERE run_id = ?",
        (stale_then, run["run_id"]),
    )
    conn.commit()
    conn.close()

    now = datetime.now(timezone.utc)
    row = get_run(run["run_id"], now=now)
    assert row["status"] == "interrupted"
    listed = list_runs(status="interrupted", now=now)
    assert any(r["run_id"] == run["run_id"] for r in listed)


def test_list_runs_filters(run_db):
    a = create_run("radar")
    b = create_run("factory")
    update_run(b["run_id"], status="failed")
    radar_only = list_runs(kind="radar")
    assert all(r["kind"] == "radar" for r in radar_only)
    failed = list_runs(status="failed")
    assert [r["run_id"] for r in failed] == [b["run_id"]]


def test_resume_endpoint_flow(run_db, monkeypatch):
    """Resume of a failed factory re-runs and lands done (stubbed belt)."""
    from fastapi.testclient import TestClient

    import main as api_main
    from boxes.fixture_dive import persist_unofficial_fixture

    persist_unofficial_fixture()
    run = create_run(
        "factory",
        params={"report_id": "rep_fixture_dive"},
    )
    update_run(run["run_id"], status="failed")

    class NullChat:
        pass

    monkeypatch.setattr(api_main, "build_chat", lambda: None)
    client = TestClient(api_main.app)

    # still-running runs refuse resume politely
    running = create_run("factory", params={"report_id": "rep_fixture_dive"})
    res = client.post(f"/runs/{running['run_id']}/resume")
    assert res.status_code == 409

    res = client.post(f"/runs/{run['run_id']}/resume")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "done"
    assert body["resumed"] is True
    names = [s["name"] for s in body["step_results"]]
    assert "factory" in names


def test_resume_unknown_run_404(run_db):
    from fastapi.testclient import TestClient

    import main as api_main

    client = TestClient(api_main.app)
    res = client.post("/runs/run_nope/resume")
    assert res.status_code == 404
    assert "error" in res.json()