"""Brief Builder — code pack only. Same inputs → same brief. No model."""

from __future__ import annotations

import hashlib
import logging

from boxes.brand_book import query_brand
from boxes.brand_pack import load_brand_pack
from boxes.product_facts import load_claims
from boxes.products import hero_sku
from db import get_brief, get_report, upsert_brief
from models import Brief

logger = logging.getLogger(__name__)

DEFAULT_MARKET = "IN"
DEFAULT_CHANNEL = "instagram"
DEFAULT_FORMAT = "instagram caption"
DEFAULT_SKU = "DEMO-HYDRO-BOOST"


def load_track_record_examples(
    sku: str,
    market: str,
    n: int = 3,
) -> tuple[list[dict], list[dict]]:
    """3 wins + 3 losses from the Track Record ledger. Empty is allowed."""
    from boxes.feedback import load_track_examples

    return load_track_examples(sku, market, n)


def load_brief(brief_id: str) -> Brief:
    pack = get_brief(brief_id)
    if pack is None:
        raise ValueError(f"unknown brief_id: {brief_id}")
    return pack


def _featured_sku(sku: str | None) -> str:
    if sku and sku.strip():
        return sku.strip()
    featured = hero_sku()
    if featured:
        return featured
    for row in load_claims():
        row_sku = str(row.get("sku") or "").strip()
        if row.get("status") == "approved" and row_sku and row_sku != "*":
            return row_sku
    pack = load_brand_pack()
    return str(pack.get("hero_sku") or DEFAULT_SKU)


def _claims_for_sku(sku: str, market: str) -> list[dict]:
    market_key = (market or DEFAULT_MARKET).strip().upper()
    out: list[dict] = []
    for row in load_claims():
        row_market = str(row.get("market") or DEFAULT_MARKET).strip().upper()
        if row_market != market_key:
            continue
        row_sku = str(row.get("sku") or "*").strip() or "*"
        if row_sku not in (sku, "*"):
            continue
        out.append(row)
    return out


def _brief_id(report_id: str, market: str, channel: str, sku: str, fmt: str) -> str:
    raw = f"{report_id}|{market}|{channel}|{sku}|{fmt}"
    return "brf_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def build_brief(
    report_id: str,
    *,
    sku: str | None = None,
    market: str = DEFAULT_MARKET,
    channel: str = DEFAULT_CHANNEL,
    format: str = DEFAULT_FORMAT,
) -> str:
    """Assemble report + brand slice + SKU claims + track examples. Code only."""
    report = get_report(report_id)
    if report is None:
        raise ValueError(f"unknown report_id: {report_id}")

    market_key = (market or DEFAULT_MARKET).strip().upper() or DEFAULT_MARKET
    channel_key = (channel or DEFAULT_CHANNEL).strip().lower() or DEFAULT_CHANNEL
    fmt = (format or DEFAULT_FORMAT).strip() or DEFAULT_FORMAT
    featured = _featured_sku(sku)
    brand = query_brand(market_key, channel_key)
    claims = _claims_for_sku(featured, market_key)
    wins, losses = load_track_record_examples(featured, market_key, n=3)
    brief_id = _brief_id(report_id, market_key, channel_key, featured, fmt)
    pack = Brief(
        brief_id=brief_id,
        report_id=report.report_id,
        market=market_key,
        sku=featured,
        channel=channel_key,
        format=fmt,
        report=report.model_dump(mode="json"),
        brand_slice=brand,
        claims=claims,
        wins=list(wins)[:3],
        losses=list(losses)[:3],
    )
    upsert_brief(pack)
    logger.info("brief %s from report %s sku=%s", brief_id, report_id, featured)
    return brief_id
