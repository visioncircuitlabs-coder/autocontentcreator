"""Radar + factory belt. Fixtures only. Queued draft, no live publish."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from models import Draft, Signal, TrendReport

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SEED_URL = "https://news.example/skincare-spike"
FOLLOW_URL = "https://news.example/follow"


class FixtureSource:
    name = "rss"

    def __init__(self, signals: list[Signal]) -> None:
        self._signals = signals

    def fetch(self, query_id: str) -> list[Signal]:
        _ = query_id
        return list(self._signals)


def _now() -> datetime:
    return datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)


def _dive_signal() -> Signal:
    return Signal(
        signal_id="sig_fixture_dive",
        seen_at=_now(),
        happened_at=_now(),
        source="rss",
        url=SEED_URL,
        title="Neutrogena Hydro Boost skincare sunscreen moisturizer",
        snippet="Ceramide serum and hyaluronic moisturizer for Indian monsoon skin.",
        query_id="skincare_in",
    )


def _kill_signal() -> Signal:
    return Signal(
        signal_id="sig_fixture_kill",
        seen_at=_now(),
        happened_at=_now(),
        source="rss",
        url="https://news.example/product-recall",
        title="Neutrogena product recall after adverse event",
        snippet="Customers hospitalized; FDA warning issued.",
        query_id="skincare_in",
    )


def _html(body: str, links: list[str]) -> str:
    anchors = "".join(f'<a href="{href}">more</a>' for href in links)
    return f"<html><body><p>{body}</p>{anchors}</body></html>"


def _research_client() -> httpx.Client:
    mapping = {
        SEED_URL: httpx.Response(
            200,
            text=_html(
                "Neutrogena Hydro Boost barrier-cream talk is rising among Indian shoppers.",
                [FOLLOW_URL],
            ),
            headers={"content-type": "text/html"},
        ),
        FOLLOW_URL: httpx.Response(
            200,
            text=_html("Same-host follow-up on monsoon moisturizer routines.", []),
            headers={"content-type": "text/html"},
        ),
        "product-recall": httpx.Response(200, text=_html("recall page", [])),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        for needle, response in mapping.items():
            if needle in url:
                return response
        return httpx.Response(404, text="not mocked: " + url)

    return httpx.Client(transport=httpx.MockTransport(handler))


def _tiny_gen():
    from PIL import Image

    class TinyGen:
        def generate(self, prompt: str, out_path: Path) -> Path:
            dest = Path(out_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (96, 96), (15, 17, 23)).save(dest, "PNG")
            return dest

    return TinyGen()


def test_run_radar_fetch_score_research_store() -> None:
    from boxes.belt import run_radar
    from db import list_reports, list_scores, list_signals

    reports = run_radar(
        sources=[FixtureSource([_dive_signal(), _kill_signal()])],
        client=_research_client(),
        chat=None,
        persist=True,
    )
    assert len(reports) == 1
    assert reports[0].signal_id == "sig_fixture_dive"
    assert reports[0].what
    signals = list_signals()
    scores = list_scores()
    stored = list_reports()
    assert {s.signal_id for s in signals} >= {"sig_fixture_dive", "sig_fixture_kill"}
    gates = {s.signal_id: s.gate for s in scores}
    assert gates["sig_fixture_dive"] == "deep_dive"
    assert gates["sig_fixture_kill"] == "discard"
    assert len(stored) == 1
    assert stored[0].report_id == reports[0].report_id


def test_belt_on_fixtures_produces_queued_draft(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from boxes.belt import run_factory, run_radar
    from db import get_draft, list_concepts, list_queue

    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    monkeypatch.setenv("IMAGE_OUT_DIR", str(tmp_path / "images"))

    reports = run_radar(
        sources=[FixtureSource([_dive_signal(), _kill_signal()])],
        client=_research_client(),
        chat=None,
        persist=True,
    )
    assert reports
    drafts = run_factory(reports[0].report_id, chat=None, image_gen=_tiny_gen())
    assert drafts
    assert all(isinstance(item, Draft) for item in drafts)
    queued = list_queue()
    assert queued, "factory must park at least one draft on the review queue"
    assert {item.draft_id for item in queued} == {item.draft_id for item in drafts}

    sample = queued[0]
    loaded = get_draft(sample.draft_id)
    assert loaded is not None
    assert loaded.caption.strip()
    assert loaded.judge is not None
    assert loaded.round >= 1
    assert loaded.image_path
    image = Path(loaded.image_path)
    assert image.is_file()
    assert image.read_bytes()[:8] == PNG_MAGIC
    assert loaded.flag_human is False or loaded.flag_human is True
    assert "flag_human" in (loaded.judge or {})
    assert "cures" not in loaded.caption.lower()
    assert "pcos" not in loaded.caption.lower()
    grid = list_concepts(loaded.brief_id)
    assert len(grid) >= 3
    assert grid[0].angle


def test_run_factory_unknown_report_fails() -> None:
    from boxes.belt import run_factory

    with pytest.raises(ValueError):
        run_factory("rep_missing")


def test_http_lists_and_radar_factory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from main import app
    from models import Decision

    report = TrendReport(
        report_id="rep_http",
        signal_id="sig_http",
        what="fixture",
        why_now="now",
        who="test",
        angles=["a"],
        risks=["r"],
        sources=[],
        skeptic="nothing dropped",
        spent={"gets": 0},
        capped_at="complete",
    )
    draft = Draft(
        draft_id="dft_http",
        brief_id="brf_http",
        caption="Dermatologist tested.",
        variant=1,
        image_path=None,
        judge={"verdict": "PASS", "flag_human": False},
        rules=[],
        round=1,
        flag_human=False,
    )
    decision = Decision(
        draft_id="dft_http",
        user="alice",
        verdict="approve",
        reason="ok for demo",
        decided_at=_now(),
    )
    monkeypatch.setattr("main.run_radar", lambda: [report])
    monkeypatch.setattr("main.run_factory", lambda report_id: [draft])
    monkeypatch.setattr("main.decide", lambda **kwargs: decision)

    client = TestClient(app)
    for path in ("/signals", "/scores", "/reports", "/drafts", "/queue"):
        res = client.get(path)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    radar = client.post("/radar/run")
    assert radar.status_code == 200
    envelope = radar.json()
    assert envelope["deep_dives"][0]["report_id"] == "rep_http"
    assert "reports" in envelope
    assert "scores" in envelope
    assert "signals_seen" in envelope

    factory = client.post("/factory/run", json={"report_id": "rep_http"})
    assert factory.status_code == 200
    assert factory.json()[0]["draft_id"] == "dft_http"

    missing = client.post("/factory/run", json={})
    assert missing.status_code in (400, 422)
