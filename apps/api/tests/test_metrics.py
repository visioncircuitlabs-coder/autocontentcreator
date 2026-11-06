"""Ops visibility: /metrics numbers must match what actually happened."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

import boxes.metrics as metrics
from boxes.image_budget import record_spend
from boxes.metrics import collect_metrics
from db import insert_decision, insert_event, upsert_draft
from harness.breaker import CHAT_BREAKER
from main import app
from models import Decision, Draft

client = TestClient(app)

METRIC_KEYS = {
    "drafts_total",
    "decisions_total",
    "approve_rate",
    "flag_human_rate",
    "avg_judge_rounds",
    "images_painted_24h",
    "videos_made_24h",
    "image_spend_usd",
    "image_budget_usd",
    "video_spend_usd",
    "video_budget_usd",
    "breaker_state",
    "chat_model",
    "last_radar_run_at",
    "last_factory_run_at",
    "uptime_s",
    "degraded_runs_24h",
}


def _draft(
    draft_id: str = "d1",
    *,
    flag: bool = False,
    rounds: int = 1,
    image: str | None = None,
) -> Draft:
    return Draft(
        draft_id=draft_id,
        brief_id="b1",
        caption="Monsoon skin, sorted.",
        variant=1,
        image_path=image,
        judge=None,
        rules=[],
        round=rounds,
        flag_human=flag,
    )


def _decision(
    draft_id: str,
    verdict: str,
    decided_at: datetime,
    user: str = "ana",
) -> Decision:
    return Decision(
        draft_id=draft_id,
        user=user,
        verdict=verdict,  # type: ignore[arg-type]
        reason="checked the claims myself",
        decided_at=decided_at,
    )


def test_metrics_endpoint_shape_on_empty_desk() -> None:
    body = client.get("/metrics").json()
    assert set(body) == METRIC_KEYS
    assert body["drafts_total"] == 0
    assert body["decisions_total"] == 0
    assert body["approve_rate"] is None
    assert body["flag_human_rate"] is None
    assert body["avg_judge_rounds"] is None
    assert body["images_painted_24h"] == 0
    assert body["videos_made_24h"] == 0
    assert body["last_radar_run_at"] is None
    assert body["last_factory_run_at"] is None
    assert body["breaker_state"] == "closed"
    assert body["uptime_s"] >= 0


def test_rates_and_rounds_match_the_tables() -> None:
    now = datetime.now(timezone.utc)
    upsert_draft(_draft("d1"))
    upsert_draft(_draft("d2", flag=True, rounds=3))
    upsert_draft(_draft("d3", rounds=2))
    insert_decision(_decision("d1", "approve", now))
    insert_decision(_decision("d2", "reject", now + timedelta(seconds=5)))
    data = collect_metrics()
    assert data["drafts_total"] == 3
    assert data["decisions_total"] == 2
    assert data["approve_rate"] == pytest.approx(0.5)
    assert data["flag_human_rate"] == pytest.approx(round(1 / 3, 4))
    assert data["avg_judge_rounds"] == pytest.approx(2.0)


def test_paint_window_and_last_run_timestamps() -> None:
    now = datetime.now(timezone.utc)
    insert_event(
        "e-old",
        (now - timedelta(hours=30)).isoformat(),
        "paint_end",
        {"image": True},
    )
    insert_event(
        "e-fresh",
        (now - timedelta(minutes=5)).isoformat(),
        "paint_end",
        {"image": True},
    )
    insert_event(
        "e-stub",
        (now - timedelta(minutes=1)).isoformat(),
        "paint_end",
        {"image": False},
    )
    insert_event("e-radar", (now - timedelta(minutes=9)).isoformat(), "radar_end", {})
    insert_event(
        "e-factory", (now - timedelta(minutes=7)).isoformat(), "factory_end", {}
    )
    data = collect_metrics()
    assert data["images_painted_24h"] == 1
    assert data["last_radar_run_at"] is not None
    assert data["last_factory_run_at"] is not None


def test_spend_comes_from_image_budget() -> None:
    record_spend(0.02)
    record_spend(0.04)
    data = collect_metrics()
    assert data["image_spend_usd"] == pytest.approx(0.06)
    assert data["image_budget_usd"] > 0


def test_breaker_state_is_read_live() -> None:
    try:
        for _ in range(CHAT_BREAKER.threshold):
            CHAT_BREAKER.record_failure()
        assert collect_metrics()["breaker_state"] == "open"
    finally:
        CHAT_BREAKER.reset()
    assert collect_metrics()["breaker_state"] == "closed"


def test_uptime_grows_from_process_start(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "PROCESS_STARTED_AT", metrics.PROCESS_STARTED_AT - 90)
    assert collect_metrics()["uptime_s"] >= 90
