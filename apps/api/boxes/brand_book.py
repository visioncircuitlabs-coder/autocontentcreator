"""Brand Book retrieval — voice/look slices with citations (not claims).

Fixture is an UNOFFICIAL DEMO — not Kenvue-approved.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from boxes.brand_pack import load_brand_pack

logger = logging.getLogger(__name__)

DEFAULT_BRAND_PATH = load_brand_pack()["book_path"]


def load_brand(path: Path | None = None) -> dict[str, Any]:
    path = path or DEFAULT_BRAND_PATH
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("brand.json must be an object")
    return raw


def query_brand(
    market: str,
    channel: str,
    *,
    path: Path | None = None,
) -> dict[str, Any]:
    """Return market/channel slice + citations. Never paste the whole book.

    Cards with channel "*" apply to every channel in that market.
    """
    book = load_brand(path)
    market_key = (market or "").strip().upper()
    channel_key = (channel or "").strip().lower()
    disclaimer = book.get("disclaimer", "UNOFFICIAL DEMO — not Kenvue-approved.")

    slice_cards: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []

    for card in book.get("cards") or []:
        if not isinstance(card, dict):
            continue
        card_market = str(card.get("market", "")).strip().upper()
        if card_market != market_key:
            continue
        card_channel = str(card.get("channel", "")).strip().lower()
        if card_channel not in (channel_key, "*"):
            continue

        entry = {
            "card_id": card.get("card_id"),
            "title": card.get("title"),
            "voice": card.get("voice"),
            "examples": [
                str(item).strip()
                for item in (card.get("examples") or [])
                if str(item).strip()
            ],
            "do": list(card.get("do") or []),
            "dont": list(card.get("dont") or []),
            "verify_state": card.get("verify_state", "unverified"),
            "expires_at": card.get("expires_at"),
            "disclaimer": disclaimer,
        }
        slice_cards.append(entry)
        citations.append(
            {
                "card_id": card.get("card_id"),
                "source_ref": card.get("source_ref"),
                "market": card_market,
                "channel": card.get("channel"),
                "verify_state": card.get("verify_state", "unverified"),
            }
        )

    return {
        "slice": slice_cards,
        "citations": citations,
        "disclaimer": disclaimer,
        "market": market_key,
        "channel": channel_key,
    }
