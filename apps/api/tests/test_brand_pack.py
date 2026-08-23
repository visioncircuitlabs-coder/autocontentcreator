"""Brand pack loader — slug → fixture pack, multi-brand tenancy groundwork."""

from __future__ import annotations

import pytest

from boxes import brand_pack
from boxes.brand_pack import (
    DEFAULT_SLUG,
    UnknownBrandSlugError,
    available_slugs,
    brand_pack_dir,
    load_brand_pack,
    resolve_slug,
)


def test_default_slug_is_neutrogena(monkeypatch):
    monkeypatch.delenv("BRAND_SLUG", raising=False)
    assert resolve_slug() == "neutrogena"
    assert resolve_slug("NEUTROGENA") == "neutrogena"
    assert resolve_slug("") == "neutrogena"


def test_env_var_selects_pack(monkeypatch):
    monkeypatch.setenv("BRAND_SLUG", DEFAULT_SLUG)
    pack = load_brand_pack()
    assert pack["slug"] == "neutrogena"
    assert pack["name"] == "Neutrogena"


def test_explicit_slug_beats_env(monkeypatch):
    monkeypatch.setenv("BRAND_SLUG", "nope-not-real")
    assert resolve_slug(DEFAULT_SLUG) == "neutrogena"


def test_neutrogena_pack_contents_match_fixtures():
    pack = load_brand_pack("neutrogena")
    assert pack["disclaimer"].startswith("Always patch-test.")
    assert isinstance(pack["banned_words"], list)
    assert pack["banned_words"] == []
    assert "Neutrogena in India" in pack["locked_query"]
    assert pack["wordmark"] == "NEUTROGENA"
    for key in (
        "book_path",
        "claims_path",
        "disclaimer_path",
        "exclusion_path",
        "logo_path",
    ):
        assert pack[key].is_file(), key


def test_unknown_slug_lists_available_slugs():
    with pytest.raises(UnknownBrandSlugError) as err:
        brand_pack_dir("does-not-exist")
    message = str(err.value)
    assert "does-not-exist" in message
    for slug in available_slugs():
        assert slug in message


def test_available_slugs_include_neutrogena():
    assert DEFAULT_SLUG in available_slugs()
