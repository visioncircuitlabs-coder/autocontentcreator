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
    assert "soft close" not in blob
    assert "no miracle talk" not in blob
    assert "is try it" not in blob


def test_copywriter_keeps_model_lines_and_drops_stage_notes() -> None:
    from boxes.copywriter import CopyOut, run_copywriter
    from boxes.hard_rules import load_disclaimer

    disc = load_disclaimer()

    class WriterChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            assert schema is CopyOut
            assert "<examples>" in user
            assert "Hydro Boost after" in user or "hydro boost after" in user.lower()
            return CopyOut(
                captions=[
                    "Double cleanse at night. Hydro Boost after — dermatologist tested.",
                    "Humid commute, then a short PM routine. Hydro Boost is dermatologist tested.",
                    "Soft close: add to routine. No miracle talk.",
                    "A",
                    "B",
                    "C",
                    "D",
                    "Explore Hydro Boost — no miracle talk.",
                ]
            )

    brief_id = _seed_report()
    drafts = run_copywriter(_concept(brief_id), round=1, chat=WriterChat())
    blob = _blob(drafts)
    assert "soft close" not in blob
    assert "no miracle talk" not in blob
    assert "double cleanse" in blob
    assert disc.split(".")[0].lower() in blob


def test_copywriter_retries_once_then_keeps_model_lines() -> None:
    from boxes.copywriter import COPY_CHAT_ATTEMPTS, CopyOut, run_copywriter
    from boxes.hard_rules import load_disclaimer

    calls = {"n": 0}
    disc = load_disclaimer()

    class Flaky:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            calls["n"] += 1
            if calls["n"] == 1:
                raise TimeoutError("slow grok")
            return CopyOut(
                captions=[
                    "Double cleanse at night. Hydro Boost after — dermatologist tested.",
                    "Humid commute, then a short PM routine. Hydro Boost is dermatologist tested.",
                    "Night shelf, one gel. Hydro Boost, dermatologist tested.",
                ]
            )

    brief_id = _seed_report()
    drafts = run_copywriter(_concept(brief_id), round=1, chat=Flaky())
    assert calls["n"] == COPY_CHAT_ATTEMPTS
    blob = _blob(drafts)
    assert "double cleanse" in blob
    assert "night gel step after cleansing" not in blob.lower()
    assert disc.split(".")[0].lower() in blob


def test_templates_only_when_there_is_no_chat() -> None:
    from boxes.copywriter import run_copywriter

    class Dead:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            raise TimeoutError("slow grok")

    brief_id = _seed_report()
    with_chat = run_copywriter(_concept(brief_id), round=1, chat=Dead())
    assert with_chat == []

    no_chat = run_copywriter(_concept(brief_id), round=1, chat=None)
    assert 2 <= len(no_chat) <= 3
    assert any("hydro boost" in item.caption.lower() for item in no_chat)


def test_copywriter_rewrite_uses_numbered_reasons() -> None:
    from boxes.copywriter import run_copywriter

    brief_id = _seed_report()
    seed = (
        "Monday light. Miracle glow water for humid days. "
        "Dermatologist tested Hydro Boost."
    )
    drafts = run_copywriter(
        _concept(brief_id),
        round=2,
        judge_reasons=['1. drop "Miracle glow water" — unsubstantiated'],
        seed_caption=seed,
        chat=None,
    )
    assert 2 <= len(drafts) <= 3
    assert all(item.round == 2 for item in drafts)
    blob = _blob(drafts)
    assert "miracle glow water" not in blob
    assert any("monday light" in item.caption.lower() for item in drafts)


def test_loop_threads_chat_to_copywriter() -> None:
    from boxes.copywriter import CopyOut
    from boxes.hard_rules import load_disclaimer
    from boxes.judge import ImpliedClaimOut
    from boxes.loop import run_loop

    seen: list[str] = []
    disc = load_disclaimer()
    clean = "Monday light. Dermatologist tested Hydro Boost.\n\n" + disc

    class FactoryChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            seen.append(schema.__name__)
            if schema is ImpliedClaimOut:
                return ImpliedClaimOut(implied=False)
            if schema.__name__ == "CraftOut":
                from boxes.craft import CraftOut

                return CraftOut(verdict="PASS", reasons=[])
            assert schema is CopyOut
            assert "<reasons>" in user
            return CopyOut(captions=[clean, "Humidity commute. Dermatologist tested.\n\n" + disc])

    out = run_loop(
        Draft(
            draft_id="d-chat",
            brief_id="b1",
            caption="This gel cures acne overnight.",
            variant=1,
            image_path=None,
            judge=None,
            rules=[],
            round=1,
        ),
        chat=FactoryChat(),
    )
    assert "CopyOut" in seen
    assert "cures" not in out.caption.lower()


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
