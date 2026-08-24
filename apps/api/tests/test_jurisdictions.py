"""G2/G8: jurisdiction-aware registry — market clearance blocks claims."""

from __future__ import annotations

from datetime import date

import pytest

from models import RegistryClaim


def _claim(**kw) -> RegistryClaim:
    base = dict(
        claim_id="reg-x",
        text="spf protects",
        sku="*",
        market="IN",
        source_url="https://example.com/evidence",
        evidence_ref="x",
        status="approved",
        review_by=None,
        notes="",
        jurisdictions=[],
    )
    base.update(kw)
    return RegistryClaim(**base)


def test_worldwide_when_no_jurisdictions():
    c = _claim(jurisdictions=[])
    from boxes.claims_registry import usable

    assert usable(c, today=date(2026, 1, 1), market="US")
    assert usable(c, today=date(2026, 1, 1), market="EU")


def test_market_list_blocks_uncleared_jurisdiction():
    c = _claim(jurisdictions=["IN", "US"])
    from boxes.claims_registry import usable

    assert usable(c, today=date(2026, 1, 1), market="in")  # case-insensitive
    assert usable(c, today=date(2026, 1, 1), market="US")
    assert not usable(c, today=date(2026, 1, 1), market="EU")
    # no-market call keeps old semantics (registry-wide check only)
    assert usable(c, today=date(2026, 1, 1))


def test_non_approved_never_usable_regardless_of_market():
    from boxes.claims_registry import usable

    for status in ("restricted", "forbidden"):
        assert not usable(_claim(status=status), market="IN")


def test_check_registry_flags_market_block(monkeypatch, tmp_path):
    """A phrase whose only covering claim is market-blocked → violation."""
    from boxes import hard_rules
    from boxes.claims_registry import list_registry
    from models import RegistryClaim as RC

    rows = [
        RC(
            claim_id="reg-spf-protects",
            text="spf protects",
            sku="*",
            source_url="https://e.example",
            status="approved",
            review_by=None,
            jurisdictions=["IN"],
        )
    ]
    monkeypatch.setattr("boxes.claims_registry.list_registry", lambda: rows)
    monkeypatch.setattr(
        "boxes.hard_rules.load_disclaimer", lambda: "Always patch-test."
    )

    text = "SPF protects all day. Always patch-test."
    ok_in = hard_rules.check_registry(text, market="IN")
    bad_eu = hard_rules.check_registry(text, market="EU")

    assert not any("not cleared" in r for r in ok_in)
    assert any("not cleared for market EU" in r for r in bad_eu)


def test_fixture_spf_claim_has_jurisdictions():
    """Fixture seed demonstrates the G2 schema (IN+US cleared, not EU)."""
    from boxes.claims_registry import load_registry

    rows = {r.claim_id: r for r in load_registry()}
    spf = rows["reg-spf-protects"]
    assert spf.jurisdictions == ["IN", "US"]
    derm = rows["reg-derm-tested"]
    assert derm.jurisdictions == []  # worldwide


def test_db_roundtrip_preserves_jurisdictions(tmp_path, monkeypatch):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "g2.db"))
    from db import init_db, list_registry_claims, upsert_registry_claims

    init_db()
    upsert_registry_claims([_claim(jurisdictions=["IN", "US"])])
    row = list_registry_claims()[0]
    assert row.jurisdictions == ["IN", "US"]
