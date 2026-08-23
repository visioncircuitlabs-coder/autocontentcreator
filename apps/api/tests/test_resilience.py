"""Resilience: bounded retry/backoff, idempotency keys, /health/deep."""

from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

import idempotency
from adapters.resilience import is_transient, retry_call
from main import app

client = TestClient(app)


# --- transient classification -------------------------------------------------


def test_timeouts_and_connections_are_transient() -> None:
    assert is_transient(httpx.TimeoutException("slow")) is True
    assert is_transient(httpx.ConnectError("refused")) is True
    assert is_transient(TimeoutError("t")) is True


def test_5xx_is_transient_4xx_never() -> None:
    req = httpx.Request("POST", "https://x.test")
    err5 = httpx.HTTPStatusError("boom", request=req, response=httpx.Response(503))
    err4 = httpx.HTTPStatusError("nope", request=req, response=httpx.Response(429))
    assert is_transient(err5) is True
    assert is_transient(err4) is False


def test_litellm_style_errors_by_name() -> None:
    class APITimeoutError(Exception):
        pass

    assert is_transient(APITimeoutError("t")) is True


# --- retry_call ----------------------------------------------------------------


def test_retry_call_succeeds_after_transient_failures() -> None:
    sleeps: list[float] = []
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise httpx.ConnectError("refused")
        return "ok"

    out = retry_call(flaky, sleep=sleeps.append, jitter=False)
    assert out == "ok"
    assert calls["n"] == 3
    assert sleeps == [1.0, 2.0]


def test_retry_call_does_not_retry_4xx() -> None:
    req = httpx.Request("GET", "https://x.test")
    sleeps: list[float] = []

    def bad() -> None:
        raise httpx.HTTPStatusError(
            "forbidden", request=req, response=httpx.Response(403)
        )

    with pytest.raises(httpx.HTTPStatusError):
        retry_call(bad, sleep=sleeps.append)
    assert sleeps == []


def test_retry_call_gives_up_after_max_retries() -> None:
    sleeps: list[float] = []
    calls = {"n": 0}

    def always_down() -> None:
        calls["n"] += 1
        raise httpx.ReadTimeout("down")

    with pytest.raises(httpx.ReadTimeout):
        retry_call(always_down, sleep=sleeps.append, jitter=False)
    assert calls["n"] == 3  # first try + 2 retries
    assert len(sleeps) == 2


def test_retry_jitter_stays_bounded() -> None:
    delays: list[float] = []
    calls = {"n": 0}

    def flaky() -> int:
        calls["n"] += 1
        if calls["n"] < 2:
            raise httpx.ConnectError("refused")
        return 1

    retry_call(flaky, sleep=delays.append)
    assert 1.0 <= delays[0] <= 2.0


# --- idempotency store ----------------------------------------------------------


def test_idempotency_roundtrip_and_expiry(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "demo.db"))
    idempotency.store("key-1", "radar_run", {"ok": True})
    cached, hit = idempotency.get_cached("key-1", "radar_run")
    assert hit is True and cached == {"ok": True}

    # different endpoint namespace does not match
    _, hit2 = idempotency.get_cached("key-1", "factory_run")
    assert hit2 is False

    # stale entry (older than the window) does not replay
    from datetime import datetime, timedelta, timezone
    from db import connect

    old_ts = (datetime.now(timezone.utc) - timedelta(minutes=11)).isoformat()
    conn = connect()
    conn.execute(
        "UPDATE idempotency_keys SET ts = ? WHERE key = ?", (old_ts, "key-1")
    )
    conn.commit()
    conn.close()

    _, hit3 = idempotency.get_cached("key-1", "radar_run")
    assert hit3 is False

    # empty key never caches
    idempotency.store("", "radar_run", {"x": 1})
    _, hit4 = idempotency.get_cached("", "radar_run")
    assert hit4 is False


# --- endpoints -------------------------------------------------------------------


def test_health_deep_reports_fields(monkeypatch) -> None:
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    client.get("/health")  # triggers init_db via lifespan-less call? ensure db exists
    from db import init_db

    init_db()
    res = client.get("/health/deep")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["chat_configured"] is False
    assert body["image_mode"] == "stub"
    assert body["db_path_bytes"] > 0
    for field in ("last_radar_run_at", "last_factory_run_at"):
        assert field in body
    assert set(body["counts"]) == {"signals", "drafts", "decisions"}


def test_radar_run_replays_same_idempotency_key(monkeypatch) -> None:
    from main import reset_rate_limit

    reset_rate_limit()

    class FakePack:
        reports = [{"report_id": "r1"}]
        scores = []
        signals = 3

    calls = {"n": 0}

    def fake_radar(chat=None):
        calls["n"] += 1
        return FakePack()

    monkeypatch.setattr("main.run_radar", fake_radar)

    headers = {"Idempotency-Key": "abc-123"}
    first = client.post("/radar/run", headers=headers)
    second = client.post("/radar/run", headers=headers)
    assert first.status_code == 200 and second.status_code == 200
    assert calls["n"] == 1
    assert first.json()["signals_seen"] == second.json()["signals_seen"]

    # different key runs again
    third = client.post("/radar/run", headers={"Idempotency-Key": "other"})
    assert third.status_code == 200
    assert calls["n"] == 2


def test_factory_run_accepts_idempotency_key(monkeypatch) -> None:
    calls = {"n": 0}

    def fake_factory(report_id, chat=None):
        calls["n"] += 1
        return {"drafts": [{"caption": "hi"}], "brief_id": "b1"}

    monkeypatch.setattr("main.run_factory", fake_factory)

    headers = {"Idempotency-Key": "fact-1"}
    first = client.post("/factory/run", json={"report_id": "r1"}, headers=headers)
    second = client.post("/factory/run", json={"report_id": "r1"}, headers=headers)
    assert first.status_code == 200 and second.status_code == 200
    assert calls["n"] == 1
