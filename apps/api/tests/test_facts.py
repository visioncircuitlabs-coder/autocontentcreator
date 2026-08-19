"""Brand Book + Product Facts fixtures (unofficial Neutrogena demo)."""

from __future__ import annotations


def test_compare_cures_acne_is_forbidden() -> None:
    from boxes.product_facts import compare_claims

    hits = compare_claims("Our new gel cures acne overnight.")
    assert hits, "expected at least one hit"
    forbidden = [h for h in hits if h["status"] == "forbidden"]
    assert any(h["claim_id"] for h in forbidden)
    assert any("cures acne" in h["span"].lower() for h in forbidden)


def test_compare_dermatologist_tested_is_approved() -> None:
    from boxes.product_facts import compare_claims

    hits = compare_claims("Formula is dermatologist tested for sensitive skin.")
    assert hits, "expected at least one hit"
    approved = [h for h in hits if h["status"] == "approved"]
    assert any("dermatologist tested" in h["span"].lower() for h in approved)
    assert all(h["status"] == "approved" for h in approved)


def test_compare_lookalike_heals_is_forbidden() -> None:
    from boxes.product_facts import compare_claims

    # simple lookalike: punctuation / casing around the forbidden token
    hits = compare_claims("This cream Heals! dry patches fast.")
    assert any(h["status"] == "forbidden" and "heal" in h["span"].lower() for h in hits)


def test_compare_number_one_sunscreen_forbidden() -> None:
    from boxes.product_facts import compare_claims

    hits = compare_claims("Try the #1 sunscreen this summer.")
    assert any(h["status"] == "forbidden" for h in hits)
    assert any("#1 sunscreen" in h["span"].lower() for h in hits)


def test_query_brand_returns_slice_and_citations() -> None:
    from boxes.brand_book import query_brand

    result = query_brand(market="IN", channel="instagram")
    assert "slice" in result
    assert "citations" in result
    assert result["slice"], "expected a non-empty brand slice for IN/instagram"
    assert result["citations"], "every slice must cite a source"
    # unofficial demo label must travel with the slice
    blob = str(result).lower()
    assert "unofficial" in blob or "not kenvue" in blob


def test_query_brand_scopes_market() -> None:
    from boxes.brand_book import query_brand

    us = query_brand(market="US", channel="instagram")
    # Neutrogena India fixture must not silently serve US as if in-scope
    assert us["slice"] == [] or all(
        c.get("market") != "IN" for c in us.get("citations", [])
    )


def test_fixtures_labeled_unofficial() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent / "fixtures" / "neutrogena"
    brand = (root / "brand.json").read_text(encoding="utf-8").lower()
    claims = (root / "claims.json").read_text(encoding="utf-8").lower()
    disclaimer = (root / "disclaimer.txt").read_text(encoding="utf-8").lower()
    assert "unofficial" in brand
    assert "unofficial" in claims
    assert "unofficial" in disclaimer or "not kenvue" in disclaimer
    assert (root / "logo.svg").is_file()
