from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from models import Score, Signal


def _signal(
    *,
    signal_id: str = "sig1",
    title: str = "Neutrogena sunscreen for Indian summer",
    snippet: str = "Ceramide moisturizer under 500 INR.",
    source: str = "news_rss",
    url: str = "https://example.com/skincare",
    happened_at: datetime | None = None,
    seen_at: datetime | None = None,
) -> Signal:
    now = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
    return Signal(
        signal_id=signal_id,
        seen_at=seen_at or now,
        happened_at=happened_at if happened_at is not None else now - timedelta(hours=2),
        source=source,  # type: ignore[arg-type]
        url=url,
        title=title,
        snippet=snippet,
        query_id="skincare_in",
        raw_ref="",
    )


def test_kill_word_forces_discard() -> None:
    from boxes.scorer import run_score

    signal = _signal(
        title="Neutrogena product recall after adverse event",
        snippet="Customers hospitalized; FDA warning issued.",
    )
    scores = run_score([signal], chat=None, persist=False)
    assert len(scores) == 1
    score = scores[0]
    assert score.safety == "kill"
    assert score.gate == "discard"
    assert score.signal_id == signal.signal_id


def test_job_ad_exclusion_is_kill() -> None:
    from boxes.scorer import run_score

    signal = _signal(
        title="Neutrogena is hiring for marketing roles",
        snippet="We're hiring. Apply now. Careers at J&J.",
        url="https://jobs.example.com/neutrogena",
    )
    scores = run_score([signal], chat=None, persist=False)
    assert scores[0].safety == "kill"
    assert scores[0].gate == "discard"


def test_username_spam_exclusion_is_kill() -> None:
    from boxes.scorer import run_score

    signal = _signal(
        title="Random spam from u/neutrogena",
        snippet="Follow @neutrogena for giveaways unrelated to skincare claims.",
        url="https://www.reddit.com/user/neutrogena/comments/xyz",
    )
    scores = run_score([signal], chat=None, persist=False)
    assert scores[0].safety == "kill"
    assert scores[0].gate == "discard"


def test_fallback_scoring_without_llm() -> None:
    from boxes.scorer import run_score

    strong = _signal(
        signal_id="strong",
        title="Neutrogena Hydro Boost hyaluronic acid serum",
        snippet="Skincare moisturizer with ceramides for dry skin in India.",
    )
    weak = _signal(
        signal_id="weak",
        title="Local cricket match postponed",
        snippet="Rain delays play in Kochi stadium.",
        url="https://example.com/cricket",
    )
    scores = {s.signal_id: s for s in run_score([strong, weak], chat=None, persist=False)}
    assert scores["strong"].model == "keyword-fallback"
    assert scores["strong"].brand_fit >= 8
    assert scores["strong"].gate == "deep_dive"
    assert scores["strong"].safety == "ok"
    assert 1 <= scores["strong"].velocity <= 10
    assert scores["weak"].brand_fit < 5
    assert scores["weak"].gate == "discard"
    assert scores["weak"].model == "keyword-fallback"


@pytest.mark.parametrize(
    ("brand_fit", "safety", "expected_gate"),
    [
        (4, "ok", "discard"),
        (5, "ok", "background"),
        (7, "ok", "background"),
        (8, "ok", "deep_dive"),
        (10, "ok", "deep_dive"),
        (9, "kill", "discard"),
        (6, "kill", "discard"),
        (8, "watch", "deep_dive"),
    ],
)
def test_gate_thresholds(
    brand_fit: int, safety: str, expected_gate: str
) -> None:
    from boxes.scorer import decide_gate

    assert decide_gate(brand_fit=brand_fit, safety=safety) == expected_gate  # type: ignore[arg-type]


def test_chat_model_brand_fit_when_provided() -> None:
    from boxes.scorer import BrandFitOut, run_score

    class FakeChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            assert schema is BrandFitOut
            return BrandFitOut(brand_fit=9, reason="on-brand skincare talk")

    signal = _signal(title="Dry skin tips this monsoon", snippet="Barrier cream ideas.")
    scores = run_score([signal], chat=FakeChat(), persist=False)
    assert scores[0].brand_fit == 9
    assert scores[0].gate == "deep_dive"
    assert scores[0].reason == "on-brand skincare talk"
    assert scores[0].model != "keyword-fallback"


def test_chat_garbage_falls_back_to_watch_not_fake_eight() -> None:
    from boxes.scorer import run_score

    class BadChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            raise ValueError("model returned garbage")

    signal = _signal(
        title="Moisturizer thread",
        snippet="Ceramide cream recommendations.",
    )
    scores = run_score([signal], chat=BadChat(), persist=False)
    assert scores[0].safety == "watch"
    assert scores[0].brand_fit < 8
    assert scores[0].gate in ("discard", "background")


def test_velocity_recency_and_source_rank() -> None:
    from boxes.scorer import score_velocity

    now = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
    fresh_reddit = _signal(
        source="reddit",
        happened_at=now - timedelta(hours=1),
        seen_at=now,
    )
    old_rss = _signal(
        source="news_rss",
        happened_at=now - timedelta(days=14),
        seen_at=now,
    )
    fresh_v = score_velocity(fresh_reddit, now=now)
    old_v = score_velocity(old_rss, now=now)
    assert 1 <= old_v <= 10
    assert 1 <= fresh_v <= 10
    assert fresh_v > old_v


def test_run_score_persists_to_scores(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "demo.db"))
    from boxes.scorer import run_score
    from db import connect, init_db

    init_db()
    signal = _signal(
        title="Neutrogena sunscreen SPF talk",
        snippet="Skincare routine with moisturizer.",
    )
    scores = run_score([signal], chat=None, persist=True)
    assert len(scores) == 1

    conn = connect()
    try:
        row = conn.execute(
            "SELECT signal_id, brand_fit, velocity, safety, gate, model, prompt_version "
            "FROM scores WHERE signal_id = ?",
            (signal.signal_id,),
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row["signal_id"] == scores[0].signal_id
    assert row["gate"] == scores[0].gate
    assert row["prompt_version"] == scores[0].prompt_version


def test_kill_overrides_high_brand_fit_from_chat() -> None:
    from boxes.scorer import BrandFitOut, run_score

    class FakeChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            return BrandFitOut(brand_fit=10, reason="would be deep dive")

    signal = _signal(
        title="Class action lawsuit after product recall",
        snippet="Adverse event reports rising.",
    )
    scores = run_score([signal], chat=FakeChat(), persist=False)
    assert scores[0].safety == "kill"
    assert scores[0].gate == "discard"
