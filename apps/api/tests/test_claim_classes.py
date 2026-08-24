"""Claim-class gate tests (compliance-bar G3 split)."""

from __future__ import annotations

from boxes.claim_classes import T2_VERBS, SUPERLATIVES, classify_token_hit


def test_drug_class_verbs_are_unconditional():
    for verb in ("cures", "heals", "treats", "prevents", "guarantees"):
        assert classify_token_hit(verb) == "unconditional"


def test_superlatives_classify_as_backable():
    for word in ("best", "only", "#1"):
        assert classify_token_hit(word) == "superlative"
    assert classify_token_hit("guaranteed") == "superlative"


def test_unknown_words_do_not_crash():
    assert classify_token_hit("hydrates") == "unknown"


def test_lists_are_disjoint():
    assert not (set(T2_VERBS) & set(SUPERLATIVES))
