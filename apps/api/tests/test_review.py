"""Review, feedback, export. Reason required. No autonomous publish."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from models import Brief, Draft, TrendReport

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _write_png(path: Path, size: tuple[int, int] = (64, 64)) -> Path:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, (15, 17, 23)).save(path, "PNG")
    return path


def _report() -> TrendReport:
    return TrendReport(
        report_id="rep_review",
        signal_id="sig_review",
        what="Monsoon barrier-cream talk is rising.",
        why_now="Humidity plus AC commute.",
        who="r/IndianSkincareAddicts",
        angles=["humidity barrier"],
        risks=["do not treat humidity talk as a medical claim"],
        sources=[
            {
                "url": "https://news.example/skincare-spike",
                "fetched_at": "2026-08-19T12:00:00+00:00",
                "hash": "abc",
                "quote": "barrier-cream talk",
            }
        ],
        skeptic="nothing dropped",
        spent={"gets": 1, "searches": 1, "tokens": 0, "rupees": 0},
        capped_at="complete",
    )


def _brief() -> Brief:
    report = _report()
    return Brief(
        brief_id="brf_review",
        report_id=report.report_id,
        market="IN",
        sku="DEMO-HYDRO-BOOST",
        channel="instagram",
        format="instagram caption",
        report=report.model_dump(mode="json"),
        brand_slice={"slice": "demo"},
        claims=[{"text": "dermatologist tested", "status": "approved"}],
        wins=[],
        losses=[],
    )


def _draft(**kwargs) -> Draft:
    data = dict(
        draft_id="dft_rev_1",
        brief_id="brf_review",
        caption="Humidity ho, skin tight feel. Dermatologist tested.",
        variant=1,
        image_path=None,
        judge={
            "verdict": "PASS",
            "reasons": [],
            "rewrite": None,
            "implied_check": "skipped",
            "flag_human": False,
        },
        rules=[],
        round=1,
        flag_human=False,
    )
    data.update(kwargs)
    return Draft(**data)


def _seed(tmp_path: Path, *, flag_human: bool = False, with_image: bool = True) -> Draft:
    from db import upsert_brief, upsert_draft, upsert_reports

    upsert_reports([_report()])
    upsert_brief(_brief())
    image_path = None
    if with_image:
        image_path = str(_write_png(tmp_path / "images" / "dft_rev_1.png"))
    judge = {
        "verdict": "FAIL" if flag_human else "PASS",
        "reasons": ["stubborn fail"] if flag_human else [],
        "rewrite": None,
        "implied_check": "skipped",
        "flag_human": flag_human,
    }
    draft = _draft(
        image_path=image_path,
        flag_human=flag_human,
        judge=judge,
    )
    upsert_draft(draft)
    return draft


def test_reject_without_reason_fails(tmp_path: Path) -> None:
    from boxes.review import decide
    from db import list_decisions, list_track_record

    _seed(tmp_path)
    with pytest.raises((ValueError, ValidationError)):
        decide("dft_rev_1", "alice", "reject", "")
    with pytest.raises((ValueError, ValidationError)):
        decide("dft_rev_1", "alice", "reject", "   ")
    assert list_decisions() == []
    assert list_track_record() == []


def test_approve_without_reason_fails(tmp_path: Path) -> None:
    from boxes.review import decide

    _seed(tmp_path)
    with pytest.raises((ValueError, ValidationError)):
        decide("dft_rev_1", "alice", "approve", "")


def test_approve_writes_track_record(tmp_path: Path) -> None:
    from boxes.brief import load_track_record_examples
    from boxes.review import decide
    from db import list_decisions, list_queue, list_track_record

    _seed(tmp_path)
    decision = decide(
        "dft_rev_1",
        "alice",
        "approve",
        "On-brand. Approved claim only. No disease talk.",
    )
    assert decision.verdict == "approve"
    assert decision.user == "alice"
    assert "On-brand" in decision.reason
    assert decision.decided_at.tzinfo is not None

    stored = list_decisions()
    assert len(stored) == 1
    assert stored[0].draft_id == "dft_rev_1"
    assert stored[0].reason.startswith("On-brand")

    ledger = list_track_record()
    assert ledger, "approve must write Track Record the same day"
    blob = " ".join(str(row) for row in ledger)
    assert "alice" in blob
    assert "on-brand" in blob.lower()
    assert "dft_rev_1" in blob

    wins, losses = load_track_record_examples("DEMO-HYDRO-BOOST", "IN")
    assert losses == []
    assert wins
    win_blob = str(wins).lower()
    assert "on-brand" in win_blob
    assert "alice" in win_blob

    assert all(item.draft_id != "dft_rev_1" for item in list_queue())


def test_reject_with_reason_writes_loss(tmp_path: Path) -> None:
    from boxes.brief import load_track_record_examples
    from boxes.review import decide

    _seed(tmp_path)
    decide("dft_rev_1", "priya", "reject", "Sounds like a cure claim.")
    wins, losses = load_track_record_examples("DEMO-HYDRO-BOOST", "IN")
    assert wins == []
    assert losses
    assert "cure" in str(losses).lower()
    assert "priya" in str(losses).lower()


def test_flag_human_survives_reload(tmp_path: Path) -> None:
    from db import get_draft

    _seed(tmp_path, flag_human=True)
    loaded = get_draft("dft_rev_1")
    assert loaded is not None
    assert loaded.flag_human is True
    assert (loaded.judge or {}).get("flag_human") is True


def test_export_pack_is_paused_zip_not_publish(tmp_path: Path) -> None:
    from boxes.export import export_pack

    _seed(tmp_path, with_image=True)
    path = export_pack("dft_rev_1")
    assert Path(path).is_file()
    assert Path(path).suffix.lower() == ".zip"
    with ZipFile(path) as zf:
        names = {name.replace("\\", "/") for name in zf.namelist()}
        assert "meta.json" in names
        assert "preview.html" in names
        assert "caption.txt" in names
        png_names = [n for n in names if n.lower().endswith(".png")]
        assert png_names
        png = zf.read(png_names[0])
        assert png.startswith(PNG_MAGIC)
        meta = zf.read("meta.json").decode("utf-8").lower()
        preview = zf.read("preview.html").decode("utf-8").lower()
        caption = zf.read("caption.txt").decode("utf-8")
        assert "paused" in meta
        assert "false" in meta or "published\": false" in meta
        assert "publish" not in meta or "published" in meta
        assert "paused" in preview
        assert "humidity ho" in caption.lower()
        assert "live" not in meta
        assert "posted" not in meta


def test_post_review_http_requires_reason(tmp_path: Path) -> None:
    from main import app

    _seed(tmp_path)
    client = TestClient(app)
    res = client.post(
        "/review/dft_rev_1",
        json={"user": "alice", "verdict": "reject", "reason": ""},
    )
    assert res.status_code in (400, 422)
    body = res.json()
    assert "stack" not in str(body).lower()
    assert "trace" not in str(body).lower()
    assert "error" in body or "detail" in body


def test_post_review_http_approve(tmp_path: Path) -> None:
    from main import app

    _seed(tmp_path)
    client = TestClient(app)
    res = client.post(
        "/review/dft_rev_1",
        json={
            "user": "alice",
            "verdict": "approve",
            "reason": "Approved claim only, India market.",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["verdict"] == "approve"
    assert body["user"] == "alice"
    assert "Approved claim" in body["reason"]


def test_get_export_http_returns_zip(tmp_path: Path) -> None:
    from main import app

    _seed(tmp_path)
    client = TestClient(app)
    res = client.get("/export/dft_rev_1")
    assert res.status_code == 200
    assert "zip" in res.headers.get("content-type", "")
    assert res.content[:2] == b"PK"
    with ZipFile(BytesIO(res.content)) as zf:
        assert "preview.html" in zf.namelist()
        assert "meta.json" in zf.namelist()


def test_no_publish_route() -> None:
    from main import app

    paths = []
    for route in app.routes:
        path = getattr(route, "path", "") or ""
        paths.append(path)
        methods = getattr(route, "methods", None) or set()
        for method in methods:
            assert "publish" not in path.lower()
            assert "boost" not in path.lower()
            assert method != "PUBLISH"
    assert "/review/{draft_id}" in paths or any(p.startswith("/review/") for p in paths)
    assert any(p.startswith("/export/") for p in paths)
