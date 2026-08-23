"""Audit trail tests: provenance JSON, printable HTML, ZIP entries, friendly errors."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from db import (
    init_db,
    insert_decision,
    upsert_brief,
    upsert_concepts,
    upsert_draft,
    upsert_reports,
    upsert_scores,
    upsert_signals,
)
from models import Brief, Concept, Decision, Draft, Score, Signal, TrendReport


def _seed(brief_id: str = "br-a") -> str:
    init_db()
    now = datetime.now(timezone.utc)
    upsert_signals(
        [
            Signal(
                signal_id="sig-1",
                seen_at=now,
                happened_at=now,
                source="gdelt",
                url="https://example.com/a",
                title="Hydration trend",
                snippet="Everyone wants dewy skin.",
                query_id="skincare_in",
            )
        ]
    )
    upsert_scores(
        [
            Score(
                signal_id="sig-1",
                brand_fit=9,
                velocity=8,
                safety="ok",
                reason="Strong fit",
                gate="deep_dive",
                model="test-model",
                prompt_version="v1",
            )
        ]
    )
    upsert_reports(
        [
            TrendReport(
                report_id="rep-1",
                signal_id="sig-1",
                what="Dewy skin spike",
                why_now="Monsoon humidity",
                who="Urban 20s",
                angles=["angle one", "angle two"],
                risks=["overclaim risk"],
                sources=[{"url": "https://example.com/a", "quote": "dewy"}],
                skeptic="Single source.",
                spent={"reads": 1},
                capped_at="2026-01-01T00:00:00+00:00",
            )
        ]
    )
    upsert_brief(
        Brief(
            brief_id=brief_id,
            report_id="rep-1",
            sku="hydro_boost",
            report={"what": "Dewy skin spike"},
            brand_slice={"voice": "warm"},
            claims=[{"claim_id": "c1", "text": "hydration"}],
        )
    )
    upsert_concepts(
        [
            Concept(
                concept_id="con-1",
                brief_id=brief_id,
                angle="morning routine",
                persona="commuter",
                claim_safe_pain="tight skin by noon",
                channel="instagram",
                indic_register="Hinglish light",
            )
        ]
    )
    # Chosen draft (passed) + a rejected sibling variant with judge reasons.
    upsert_draft(
        Draft(
            draft_id="dr-good",
            brief_id=brief_id,
            caption="Good caption.",
            variant=2,
            image_path=None,
            judge={
                "verdict": "PASS",
                "reasons": [],
                "craft": "PASS",
                "craft_reasons": [],
                "flag_human": False,
            },
            rules=[],
            round=2,
        )
    )
    upsert_draft(
        Draft(
            draft_id="dr-bad",
            brief_id=brief_id,
            caption="Best gel ever, guaranteed cure!",
            variant=1,
            image_path=None,
            judge={
                "verdict": "FAIL",
                "reasons": ["banned word 'guaranteed'"],
                "craft": "FAIL",
                "craft_reasons": ["hook is flat"],
                "flag_human": False,
            },
            rules=["gazette ban: guaranteed"],
            round=1,
        )
    )
    insert_decision(
        Decision(
            draft_id="dr-good",
            user="priya",
            verdict="approve",
            reason="Matches approved claims.",
            decided_at=now,
        )
    )
    return "dr-good"


def test_build_audit_full_chain() -> None:
    from boxes.audit import build_audit

    audit = build_audit(_seed())
    assert audit["draft"]["draft_id"] == "dr-good"
    assert audit["signal"]["signal_id"] == "sig-1"
    assert audit["score"]["gate"] == "deep_dive"
    assert audit["report"]["report_id"] == "rep-1"
    assert audit["brief"]["brief_id"] == "br-a"
    assert len(audit["concepts"]) == 1
    ids = {v["draft_id"] for v in audit["variants"]}
    assert {"dr-good", "dr-bad"} <= ids
    rejected = next(v for v in audit["variants"] if v["draft_id"] == "dr-bad")
    assert rejected["judge"]["verdict"] == "FAIL"
    assert "guaranteed" in " ".join(rejected["judge"]["reasons"])
    assert audit["decisions"][0]["user"] == "priya"
    assert audit["image_provenance"]["prompt_used"]
    assert "no logo" in audit["image_provenance"]["prompt_used"]


def test_audit_unknown_draft_is_friendly() -> None:
    client = TestClient(__import__("main").app)
    resp = client.get("/audit/does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert set(body) == {"error"}
    assert "Traceback" not in body["error"]


def test_audit_html_endpoint_printable() -> None:
    _seed()
    client = TestClient(__import__("main").app)
    resp = client.get("/audit/dr-good/html")
    assert resp.status_code == 200
    text = resp.text
    assert "<script" not in text.lower()
    assert "priya" in text and "guaranteed" in text
    assert "PAUSED" in text


def test_export_zip_contains_audit_entries() -> None:
    import os

    from boxes.export import export_pack

    os.environ["IMAGE_GEN_MODE"] = "stub"
    _seed()
    dest = export_pack("dr-good")
    with zipfile.ZipFile(dest) as zf:
        names = set(zf.namelist())
        assert "audit.json" in names
        assert "audit.html" in names
        audit = json.loads(zf.read("audit.json"))
        assert audit["draft"]["draft_id"] == "dr-good"
        html_text = zf.read("audit.html").decode("utf-8")
        assert "priya" in html_text
