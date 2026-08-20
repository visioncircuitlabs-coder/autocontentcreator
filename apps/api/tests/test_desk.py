"""Command Center HTTP: radar envelope, brief+grid, draft PNG."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from models import Brief, Concept, Draft, TrendReport


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _write_png(path: Path) -> Path:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (48, 48), (20, 17, 14)).save(path, "PNG")
    return path


def test_radar_run_envelope_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    from main import app
    from models import TrendReport as Report

    report = Report(
        report_id="rep_desk",
        signal_id="sig_desk",
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
    monkeypatch.setattr("main.run_radar", lambda **_: [report])
    client = TestClient(app)
    res = client.post("/radar/run")
    assert res.status_code == 200
    body = res.json()
    for key in ("reports", "scores", "signals_seen", "deep_dives"):
        assert key in body
        assert isinstance(body[key], list)
    assert body["deep_dives"][0]["report_id"] == "rep_desk"
    assert "stack" not in str(body).lower()


def test_get_brief_includes_grid() -> None:
    from db import upsert_brief, upsert_concepts, upsert_reports
    from main import app

    report = TrendReport(
        report_id="rep_grid",
        signal_id="sig_grid",
        what="humidity talk",
        why_now="monsoon",
        who="desk",
        angles=["barrier"],
        risks=["no medical"],
        sources=[],
        skeptic="nothing dropped",
        spent={},
        capped_at="complete",
    )
    brief = Brief(
        brief_id="brf_grid",
        report_id="rep_grid",
        market="IN",
        sku="DEMO-HYDRO-BOOST",
        channel="instagram",
        format="instagram caption",
        report=report.model_dump(mode="json"),
        brand_slice={"voice": "warm"},
        claims=[{"text": "dermatologist tested", "status": "approved"}],
    )
    concept = Concept(
        concept_id="con_grid",
        brief_id="brf_grid",
        angle="humidity barrier",
        persona="AC-commute millennial",
        claim_safe_pain="post-AC tightness",
        channel="instagram",
        indic_register="hinglish",
        hook="Humidity ho, barrier calm rahe.",
        idea="routine fit",
    )
    upsert_reports([report])
    upsert_brief(brief)
    upsert_concepts([concept])

    client = TestClient(app)
    res = client.get("/briefs/brf_grid")
    assert res.status_code == 200
    body = res.json()
    assert body["brief_id"] == "brf_grid"
    assert body["sku"] == "DEMO-HYDRO-BOOST"
    assert body["concepts"][0]["angle"] == "humidity barrier"

    missing = client.get("/briefs/brf_missing")
    assert missing.status_code == 404
    assert "error" in missing.json()


def test_get_draft_image_png(tmp_path: Path) -> None:
    from db import upsert_draft
    from main import app

    png = _write_png(tmp_path / "dft_img.png")
    upsert_draft(
        Draft(
            draft_id="dft_img",
            brief_id="brf_img",
            caption="Dermatologist tested.",
            variant=1,
            image_path=str(png),
            judge={"verdict": "PASS", "flag_human": False},
            rules=[],
            round=1,
        )
    )
    client = TestClient(app)
    res = client.get("/drafts/dft_img/image")
    assert res.status_code == 200
    assert res.content[:8] == PNG_MAGIC

    missing = client.get("/drafts/dft_nope/image")
    assert missing.status_code == 404
    assert "error" in missing.json()
    assert "stack" not in str(missing.json()).lower()


def test_unofficial_fixture_dive_is_labeled_and_runnable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from boxes.fixture_dive import FIXTURE_REPORT_ID, SEED_URL
    from main import app

    monkeypatch.setenv("IMAGE_GEN_MODE", "stub")
    monkeypatch.setenv("IMAGE_OUT_DIR", str(tmp_path / "images"))
    client = TestClient(app)
    res = client.post("/radar/fixture")
    assert res.status_code == 200
    body = res.json()
    assert body["fixture"] is True
    report = body["report"]
    assert report["report_id"] == FIXTURE_REPORT_ID
    assert "hydro boost" in report["what"].lower()
    assert "india" in report["who"].lower()
    assert report["sources"]
    assert report["sources"][0]["url"] == SEED_URL
    assert report["sources"][0]["quote"]
    assert report["sources"][0]["hash"]

    stored = client.get(f"/reports/{FIXTURE_REPORT_ID}")
    assert stored.status_code == 200
    assert stored.json()["sources"][0]["quote"]

    factory = client.post("/factory/run", json={"report_id": FIXTURE_REPORT_ID})
    assert factory.status_code == 200
    drafts = factory.json()
    assert drafts
    assert drafts[0]["caption"].strip()
    assert "pcos" not in drafts[0]["caption"].lower()
