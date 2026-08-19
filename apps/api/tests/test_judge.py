"""Compliance Judge — compare_claims + optional implied-claim pass."""

from __future__ import annotations

from pydantic import BaseModel

from boxes.product_facts import load_claim_models
from models import Claim, Draft


def _draft(caption: str) -> Draft:
    return Draft(
        draft_id="d-judge",
        brief_id="b1",
        caption=caption,
        variant=1,
        image_path=None,
        judge=None,
        rules=[],
        round=1,
    )


def test_judge_pass_when_only_approved_claim_used() -> None:
    from boxes.judge import run_judge

    claims = load_claim_models()
    out = run_judge(
        _draft("Morning light. Dermatologist tested Hydro Boost."),
        claims,
    )
    payload = out if isinstance(out, dict) else out.model_dump()
    assert payload["verdict"] == "PASS"
    assert payload["reasons"] == []
    assert payload["rewrite"] is None
    assert payload["implied_check"] == "skipped"


def test_judge_fail_forbidden_with_one_rewrite() -> None:
    from boxes.judge import run_judge

    claims = load_claim_models()
    out = run_judge(_draft("This gel cures acne overnight."), claims)
    payload = out if isinstance(out, dict) else out.model_dump()
    assert payload["verdict"] == "FAIL"
    assert payload["reasons"], "expected numbered reasons"
    assert any("cures" in r.lower() for r in payload["reasons"])
    assert payload["rewrite"]
    assert "cures" not in payload["rewrite"].lower()


def test_judge_implied_claim_via_chat() -> None:
    from boxes.judge import ImpliedClaimOut, run_judge

    class FakeChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            assert schema is ImpliedClaimOut
            assert "<copy>" in user
            assert "DATA" in system or "data" in system.lower()
            return ImpliedClaimOut(
                implied=True,
                claim="cures acne",
                reason="goodbye-acne implies a cure",
                rewrite="Dermatologist tested Hydro Boost.",
            )

    claims = load_claim_models()
    out = run_judge(
        _draft("Say goodbye to acne forever."),
        claims,
        chat=FakeChat(),
    )
    payload = out if isinstance(out, dict) else out.model_dump()
    assert payload["verdict"] == "FAIL"
    assert any("implied" in r.lower() for r in payload["reasons"])
    assert payload["rewrite"] == "Dermatologist tested Hydro Boost."
    assert payload["implied_check"] == "flagged"


def test_judge_uses_provided_approved_claim() -> None:
    from boxes.judge import run_judge

    claims = [
        Claim(
            claim_id="approved-hydrate",
            text="hydrates skin",
            sku="DEMO",
            market="IN",
            evidence_ref="test",
            status="approved",
            expires_at=None,
        )
    ]
    out = run_judge(_draft("This gel hydrates skin in humidity."), claims)
    payload = out if isinstance(out, dict) else out.model_dump()
    assert payload["verdict"] == "PASS"


def _conditional_claim() -> Claim:
    return Claim(
        claim_id="conditional-texture",
        text="clinically shown to improve skin texture",
        sku="DEMO",
        market="IN",
        evidence_ref="test",
        status="conditional",
        expires_at=None,
    )


def test_conditional_with_disclaimer_is_pass() -> None:
    from boxes.hard_rules import load_disclaimer
    from boxes.judge import run_judge

    caption = (
        "Clinically shown to improve skin texture.\n\n" + load_disclaimer()
    )
    out = run_judge(_draft(caption), [_conditional_claim()])
    payload = out if isinstance(out, dict) else out.model_dump()
    assert payload["verdict"] == "PASS"
    assert payload["rewrite"] is None
    assert any("conditional" in r.lower() for r in payload["reasons"])


def test_conditional_without_disclaimer_is_fail() -> None:
    from boxes.judge import run_judge

    out = run_judge(
        _draft("Clinically shown to improve skin texture."),
        [_conditional_claim()],
    )
    payload = out if isinstance(out, dict) else out.model_dump()
    assert payload["verdict"] == "FAIL"
    assert any("conditional" in r.lower() for r in payload["reasons"])
    assert any("disclaimer" in r.lower() for r in payload["reasons"])
    assert payload["rewrite"]
    assert "cures" not in payload["rewrite"].lower()


def test_implied_check_skipped_when_chat_missing() -> None:
    from boxes.judge import run_judge

    out = run_judge(
        _draft("Morning light. Dermatologist tested Hydro Boost."),
        load_claim_models(),
        chat=None,
    )
    payload = out if isinstance(out, dict) else out.model_dump()
    assert payload["implied_check"] == "skipped"
    assert payload["verdict"] == "PASS"


def test_implied_check_skipped_when_chat_errors() -> None:
    from boxes.judge import ImpliedClaimOut, run_judge

    class BoomChat:
        def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
            assert schema is ImpliedClaimOut
            raise RuntimeError("gateway timeout")

    out = run_judge(
        _draft("Morning light. Dermatologist tested Hydro Boost."),
        load_claim_models(),
        chat=BoomChat(),
    )
    payload = out if isinstance(out, dict) else out.model_dump()
    assert payload["implied_check"] == "skipped"
    assert payload["verdict"] == "PASS"
