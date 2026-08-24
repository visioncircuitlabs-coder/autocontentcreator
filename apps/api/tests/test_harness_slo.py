"""SLO rollups: percentile math, /slo shape, degraded-run gauge (bar G3+E2).

Seeds events straight into the temp DB (conftest isolates SQLITE_PATH per
test) and checks that the numbers /slo reports match what actually happened.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

import harness.slo as slo
from boxes.metrics import collect_metrics
from db import insert_event
from main import app

client = TestClient(app)

NOW = datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def seed_step(
    name: str,
    ms: int,
    *,
    ok: bool = True,
    when: datetime | None = None,
    eid: str | None = None,
) -> None:
    """Insert one kind='harness_step' event like harness/steps.py emits."""
    insert_event(
        eid or f"ev-{name}-{ms}-{when}",
        _iso(when or NOW),
        "harness_step",
        {"step": name, "ok": ok, "ms": ms, "attempts": 1, "error": None if ok else "boom"},
    )


# --- percentile math -------------------------------------------------------


def test_percentile_interpolates_known_series() -> None:
    assert slo.percentile([10, 20, 30, 40], 50) == pytest.approx(25.0)
    assert slo.percentile([10, 20, 30, 40], 95) == pytest.approx(38.5)
    assert slo.percentile([100, 200, 300, 400, 500], 50) == pytest.approx(300.0)
    assert slo.percentile([100, 200, 300, 400, 500], 95) == pytest.approx(480.0)


def test_percentile_handles_single_value_and_order() -> None:
    assert slo.percentile([7], 50) == pytest.approx(7.0)
    assert slo.percentile([7], 95) == pytest.approx(7.0)
    # unsorted input must not change the answer
    assert slo.percentile([40, 10, 30, 20], 50) == pytest.approx(25.0)
    with pytest.raises(ValueError):
        slo.percentile([], 50)


# --- per-step rollups ------------------------------------------------------


def test_rollups_match_seeded_series() -> None:
    for i, ms in enumerate((100, 200, 300, 400, 500)):
        seed_step("fetch_trends", ms, eid=f"f{i}")
    seed_step("score_signals", 10, ok=True, eid="s1")
    seed_step("score_signals", 20, ok=False, eid="s2")
    seed_step("score_signals", 30, ok=True, eid="s3")

    rolls = slo.step_rollups(hours=24)

    assert set(rolls) == {"fetch_trends", "score_signals"}
    fetch = rolls["fetch_trends"]
    assert fetch["count"] == 5
    assert fetch["p50_ms"] == 300
    assert fetch["p95_ms"] == 480
    assert fetch["error_rate"] == 0.0

    score = rolls["score_signals"]
    assert score["count"] == 3
    assert score["error_rate"] == pytest.approx(round(1 / 3, 4))


def test_rollups_window_excludes_old_steps() -> None:
    seed_step("fetch_trends", 100, when=NOW - timedelta(hours=25), eid="old")
    seed_step("fetch_trends", 200, when=NOW - timedelta(minutes=5), eid="new")

    fresh_only = slo.step_rollups(hours=24)
    assert fresh_only["fetch_trends"]["count"] == 1
    assert fresh_only["fetch_trends"]["p50_ms"] == 200

    wider = slo.step_rollups(hours=48)
    assert wider["fetch_trends"]["count"] == 2


def test_rollups_skip_malformed_payloads() -> None:
    insert_event("bad-json", _iso(NOW), "harness_step", "not-json{{{")
    insert_event(
        "no-ms", _iso(NOW), "harness_step", {"step": "mystery"}
    )  # missing ms
    assert slo.step_rollups(hours=24) == {}


# --- degraded-run counter --------------------------------------------------


def test_template_mode_start_counts_as_degraded() -> None:
    # belt.py emits chat=None when no chat model is configured
    insert_event("t1", _iso(NOW), "radar_start", {"chat": None})
    assert slo.degraded_runs(hours=24) == 1
    insert_event("t2", _iso(NOW), "factory_start", {})
    assert slo.degraded_runs(hours=24) == 2
    # a real model name means full mode — not degraded
    insert_event("t3", _iso(NOW), "radar_start", {"chat": "xai/grok-2"})
    assert slo.degraded_runs(hours=24) == 2


def test_resume_without_clean_end_counts_degraded() -> None:
    insert_event(
        "r1", _iso(NOW - timedelta(minutes=4)), "resume_start", {"run_kind": "factory"}
    )
    insert_event(
        "r2",
        _iso(NOW - timedelta(minutes=3)),
        "resume_end",
        {"run_kind": "factory", "ok": False},
    )
    # factory_end absent after the resume → degraded finish
    assert slo.degraded_runs(hours=24) == 1

    # a later clean factory run closes it out → no longer counts
    insert_event("f9", _iso(NOW - timedelta(minutes=1)), "factory_end", {})
    assert slo.degraded_runs(hours=24) == 0


def test_successful_full_resume_is_not_degraded() -> None:
    # belt re-emits radar_end during a successful resume, so the ladder worked
    insert_event(
        "r1", _iso(NOW - timedelta(minutes=4)), "resume_start", {"run_kind": "radar"}
    )
    insert_event("e1", _iso(NOW - timedelta(minutes=3)), "radar_end", {})
    insert_event(
        "r2", _iso(NOW - timedelta(minutes=2)), "resume_end", {"run_kind": "radar", "ok": True}
    )
    assert slo.degraded_runs(hours=24) == 0


def test_old_degraded_events_do_not_count() -> None:
    insert_event(
        "r1",
        _iso(NOW - timedelta(hours=30)),
        "resume_end",
        {"run_kind": "radar", "ok": False},
    )
    # outside the 24h window → invisible; inside 48h → one stuck resume
    assert slo.degraded_runs(hours=24) == 0
    assert slo.degraded_runs(hours=48) == 1

    insert_event("t1", _iso(NOW - timedelta(hours=30)), "radar_start", {"chat": None})
    assert slo.degraded_runs(hours=24) == 0
    assert slo.degraded_runs(hours=48) == 2


def test_degraded_counter_never_raises(monkeypatch) -> None:
    def explode(*args, **kwargs):
        raise RuntimeError("disk on fire")

    monkeypatch.setattr(slo, "connect", explode)
    assert slo.degraded_runs(hours=24) == 0


def test_parse_hours_rejects_junk() -> None:
    assert slo.parse_hours(None) == 24.0
    assert slo.parse_hours("") == 24.0
    assert slo.parse_hours("12") == 12.0
    for junk in ("abc", "-1", "0", "1e400", "876000"):
        with pytest.raises(ValueError):
            slo.parse_hours(junk)


# --- endpoint --------------------------------------------------------------


def test_slo_endpoint_shape_on_quiet_desk() -> None:
    body = client.get("/slo").json()
    assert set(body) >= {"steps", "generated_at", "hours", "degraded_runs_24h"}
    assert body["steps"] == {}
    assert body["hours"] == 24
    assert body["degraded_runs_24h"] == 0
    datetime.fromisoformat(body["generated_at"])  # parseable stamp


def test_slo_endpoint_reports_seeded_steps_and_gauge() -> None:
    seed_step("fetch_trends", 120, eid="f1")
    seed_step("fetch_trends", 480, eid="f2")
    insert_event("t1", _iso(NOW), "radar_start", {"chat": None})

    body = client.get("/slo").json()
    assert body["steps"]["fetch_trends"] == {
        "count": 2,
        "p50_ms": 300,
        "p95_ms": 462,  # rank 0.95 between two points → 120 + 0.95*360
        "error_rate": 0.0,
    }
    assert body["degraded_runs_24h"] == 1


def test_slo_endpoint_honors_hours_param() -> None:
    seed_step("fetch_trends", 100, when=NOW - timedelta(hours=25), eid="old")
    body = client.get("/slo?hours=48").json()
    assert body["hours"] == 48
    assert body["steps"]["fetch_trends"]["count"] == 1
    assert client.get("/slo?hours=24").json()["steps"] == {}


@pytest.mark.parametrize("junk", ["abc", "-5", "0", "999999999"])
def test_slo_endpoint_friendly_error_on_bad_hours(junk: str) -> None:
    resp = client.get(f"/slo?hours={junk}")
    assert resp.status_code == 400
    payload = resp.json()
    assert set(payload) == {"error"}
    assert "hour" in payload["error"].lower()


# --- /metrics one-liner ----------------------------------------------------


def test_metrics_includes_degraded_gauge() -> None:
    assert collect_metrics()["degraded_runs_24h"] == 0
    insert_event("t1", _iso(NOW), "radar_start", {"chat": None})
    assert collect_metrics()["degraded_runs_24h"] == 1
