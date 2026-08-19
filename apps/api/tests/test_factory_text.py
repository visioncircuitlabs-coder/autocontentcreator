"""Brief (code only) + Strategist grid + Copywriter 2–3 variants."""

from __future__ import annotations

import inspect

from models import Concept, Draft, TrendReport
from pydantic import BaseModel


def _report() -> TrendReport:
    return TrendReport(
        report_id="rep_demo_barrier",
        signal_id="sig-dive",
        what="Monsoon barrier-cream talk is rising among Indian shoppers.",
        why_now="Humidity plus AC commute is the weekly complaint.",
        who="r/IndianSkincareAddicts + beauty news",
        angles=["humidity barrier", "AC tightness", "monsoon routine"],
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
        spent={"gets": 2, "searches": 2, "tokens": 0, "rupees": 0},
        capped_at="complete",
    )


def _seed_report() -> str:
    from boxes.brief import build_brief
    from db import upsert_reports

    report = _report()
    upsert_reports([report])
    return build_brief(report.report_id)


def _concept(brief_id: str = "b1") -> Concept:
    return Concept(
        concept_id="con_demo",
        brief_id=brief_id,
        angle="humidity barrier",
        persona="AC-commute millennial",
        claim_safe_pain="post-AC tightness",
        channel="instagram",
        indic_register="hinglish",
        hook="Humidity ho, skin tight feel.",
        idea="Monsoon commute tightness, not a disease story.",
    )


def _blob(items: list) -> str:
    parts: list[str] = []
    for item in items:
        if hasattr(item, "model_dump"):
            parts.append(str(item.model_dump()).lower())
        else:
            parts.append(str(item).lower())
    return " ".join(parts)


def test_brief_module_has_no_llm() -> None:
    from boxes import brief as brief_mod
    from boxes.brief import build_brief

    source = inspect.getsource(brief_mod)
    assert "ChatModel" not in source
    assert "complete_json" not in source
    assert "litellm" not in source.lower()
    assert "openai" not in source.lower()
    assert "chat" not in inspect.signature(build_brief).parameters


def test_build_brief_packs_report_brand_claims_and_empty_track() -> None:
    from boxes.brief import load_brief, load_track_record_examples

    brief_id = _seed_report()
    pack = load_brief(brief_id)
    assert pack.brief_id == brief_id
    assert pack.report_id == "rep_demo_barrier"
    assert pack.report["what"]
    assert pack.brand_slice.get("slice")
    assert pack.claims
    assert any(c.get("status") == "approved" for c in pack.claims)
    wins, losses = load_track_record_examples(pack.sku, pack.market)
    assert wins == []
    assert losses == []
    assert pack.wins == []
    assert pack.losses == []


def test_build_brief_is_deterministic() -> None:
    from boxes.brief import build_brief
    from db import upsert_reports

    upsert_reports([_report()])
    first = build_brief("rep_demo_barrier")
    second = build_brief("rep_demo_barrier")
    assert first == second
    assert first.startswith("brf_")


def test_strategist_grid_has_no_pcos() -> None:
    from boxes.strategist import run_strategist

    brief_id = _seed_report()
    concepts = run_strategist(brief_id)
    assert len(concepts) >= 3
    for concept in concepts:
        assert concept.angle
        assert concept.persona
        assert concept.claim_safe_pain
        assert concept.channel
        assert concept.indic_register
        assert concept.brief_id == brief_id
    blob = _blob(concepts)
    assert "pcos" not in blob
    assert "thyroid" not in blob
    assert "diabetes" not in blob


def test_strategist_strips_disease_names_from_chat() -> None:
    from boxes.strategist import ConceptGridOut, ConceptOut, run_strategist

    class SickChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            assert schema is ConceptGridOut
            assert "<brief>" in user
            assert "DATA" in system or "data" in system.lower()
            return ConceptGridOut(
                concepts=[
                    ConceptOut(
                        angle="PCOS warrior support",
                        persona="thyroid patient",
                        claim_safe_pain="PCOS acne",
                        channel="instagram",
                        indic_register="hinglish",
                        hook="For PCOS warriors",
                        idea="A diabetes-friendly cream story",
                    )
                ]
            )

    brief_id = _seed_report()
    concepts = run_strategist(brief_id, chat=SickChat())
    assert concepts
    blob = _blob(concepts)
    assert "pcos" not in blob
    assert "thyroid" not in blob
    assert "diabetes" not in blob


def test_copywriter_returns_two_to_three_drafts() -> None:
    from boxes.copywriter import run_copywriter

    brief_id = _seed_report()
    drafts = run_copywriter(_concept(brief_id), round=1)
    assert 2 <= len(drafts) <= 3
    assert all(isinstance(item, Draft) for item in drafts)
    assert {item.variant for item in drafts} == set(range(1, len(drafts) + 1))
    assert all(item.round == 1 for item in drafts)
    assert all(item.brief_id == brief_id for item in drafts)
    assert all(item.caption.strip() for item in drafts)
    blob = _blob(drafts)
    assert "pcos" not in blob
    assert "cures" not in blob


def test_copywriter_rewrite_uses_numbered_reasons() -> None:
    from boxes.copywriter import run_copywriter

    brief_id = _seed_report()
    drafts = run_copywriter(
        _concept(brief_id),
        round=2,
        judge_reasons=['1. forbidden claim "cures acne"'],
        seed_caption="This gel cures acne overnight.",
    )
    assert 2 <= len(drafts) <= 3
    assert all(item.round == 2 for item in drafts)
    blob = _blob(drafts)
    assert "cures" not in blob


def test_loop_default_rewrite_uses_copywriter() -> None:
    from boxes.loop import default_rewrite, run_loop

    source = inspect.getsource(default_rewrite)
    assert "rewrite_draft" in source or "run_copywriter" in source

    out = run_loop(
        Draft(
            draft_id="d-factory",
            brief_id="b1",
            caption="This gel cures acne overnight.",
            variant=1,
            image_path=None,
            judge=None,
            rules=[],
            round=1,
        )
    )
    assert "cures" not in out.caption.lower()
    assert out.round <= 3
