"""Claims registry: seed, storage, and hard-rule checking against it."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest


@pytest.fixture()
def seeded_registry():
    from boxes.claims_registry import seed_registry

    n = seed_registry()
    assert n >= 5
    return n


def test_fixture_rows_carry_citation_and_review_date(seeded_registry) -> None:
    from boxes.claims_registry import load_registry

    rows = {r.claim_id: r for r in load_registry()}
    approved = [r for r in rows.values() if r.status == "approved"]
    assert approved, "fixture must contain approved claims"
    for row in approved:
        assert row.source_url.strip(), row.claim_id
        assert row.review_by is not None, row.claim_id
    assert any("hyaluronic" in r.text.lower() for r in approved)
    assert any("dermatologist" in r.text.lower() for r in approved)
    statuses = {r.status for r in rows.values()}
    assert {"approved", "restricted", "forbidden"} <= statuses


def test_seed_persists_to_sqlite(seeded_registry) -> None:
    from db import list_registry_claims

    rows = list_registry_claims()
    assert len(rows) == seeded_registry
    ids = {r.claim_id for r in rows}
    assert "reg-ha-hydrates" in ids
    for row in rows:
        assert isinstance(row.review_by, datetime) or row.review_by is None


def test_usable_requires_approved_cited_unexpired() -> None:
    from boxes.claims_registry import RegistryClaim, usable

    good = RegistryClaim(
        claim_id="a",
        text="x",
        source_url="https://example.com/evidence",
        status="approved",
        review_by=datetime(2099, 1, 1, tzinfo=timezone.utc),
    )
    assert usable(good)
    assert not usable(
        good.model_copy(update={"status": "restricted"})
    )
    assert not usable(good.model_copy(update={"source_url": ""}))
    expired = good.model_copy(
        update={"review_by": datetime(2020, 1, 1, tzinfo=timezone.utc)}
    )
    assert usable(expired, today=date(2019, 1, 1))
    assert not usable(expired)


def test_check_registry_passes_registered_approved_claim(seeded_registry) -> None:
    from boxes.hard_rules import check_registry

    text = "Dermatologist tested. Hyaluronic acid hydrates skin instantly."
    assert check_registry(text) == []


def test_check_registry_flags_unregistered_benefit(seeded_registry) -> None:
    from boxes.hard_rules import check_registry

    reasons = check_registry("Our gel brightens dull skin.")
    assert reasons
    assert any("unregistered benefit claim" in r for r in reasons)


def test_check_registry_flags_restricted_and_forbidden(seeded_registry) -> None:
    from boxes.hard_rules import check_registry

    restricted = check_registry("It will brightens dark spots in a week.")
    assert any("status=restricted" in r for r in restricted)

    forbidden = check_registry("This cures acne overnight.")
    assert any("status=forbidden" in r for r in forbidden)


def test_check_registry_flags_expired_review_date(seeded_registry) -> None:
    from boxes.hard_rules import check_registry

    today = date(2030, 1, 1)  # every fixture review_by has passed by then
    reasons = check_registry(
        "Hyaluronic acid hydrates skin instantly.", today=today
    )
    assert any("review_by" in r for r in reasons)
