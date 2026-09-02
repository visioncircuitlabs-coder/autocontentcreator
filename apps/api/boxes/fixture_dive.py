"""Unofficial canned deep-dive. Same seed as Task 10 belt tests. Not this Fetch."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from boxes.brand_pack import load_brand_pack
from models import Score, Signal, TrendReport

FIXTURE_SIGNAL_ID = "sig_fixture_dive"
FIXTURE_REPORT_ID = "rep_fixture_dive"
SEED_URL = "https://news.example/skincare-spike"
FOLLOW_URL = "https://news.example/follow"
SEED_QUOTE = (
    "Neutrogena Hydro Boost barrier-cream talk is rising among Indian shoppers."
)
FOLLOW_QUOTE = "Same-host follow-up on monsoon moisturizer routines."
STAMP = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)

LAYS_SEED_URL = "https://news.example/chile-limon-spike"
LAYS_FOLLOW_URL = "https://news.example/chile-limon-follow"


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def unofficial_fixture_pack() -> dict:
    """Labeled unofficial practice idea. Create post can run from this report."""
    pack = load_brand_pack()
    if pack.get("slug") == "lays":
        return _lays_fixture(pack)
    return _neutrogena_fixture()


def _neutrogena_fixture() -> dict:
    signal = Signal(
        signal_id=FIXTURE_SIGNAL_ID,
        seen_at=STAMP,
        happened_at=STAMP,
        source="rss",
        url=SEED_URL,
        title="Neutrogena Hydro Boost skincare sunscreen moisturizer",
        snippet="Ceramide serum and hyaluronic moisturizer for Indian monsoon skin.",
        query_id="skincare_in",
    )
    score = Score(
        signal_id=FIXTURE_SIGNAL_ID,
        brand_fit=8,
        velocity=6,
        safety="ok",
        reason="Practice idea. Hydro Boost in humid weather, not a medical claim.",
        gate="deep_dive",
        model="fixture",
        prompt_version="unofficial-fixture-1",
    )
    fetched = STAMP.isoformat()
    report = TrendReport(
        report_id=FIXTURE_REPORT_ID,
        signal_id=FIXTURE_SIGNAL_ID,
        what="Hydro Boost talk is up this week. Humid weather, tired skin after AC.",
        why_now="Humidity plus AC. A stand-in idea when live headlines are a weak brand match.",
        who="People in India talking about humid-weather skincare",
        angles=["humidity barrier", "monsoon routine fit", "AC-commute tightness"],
        risks=[
            "do not treat humidity talk as a medical claim",
            "do not treat this as a live brand approval",
        ],
        sources=[
            {
                "url": SEED_URL,
                "fetched_at": fetched,
                "hash": _hash(SEED_QUOTE),
                "quote": SEED_QUOTE,
            },
            {
                "url": FOLLOW_URL,
                "fetched_at": fetched,
                "hash": _hash(FOLLOW_QUOTE),
                "quote": FOLLOW_QUOTE,
            },
        ],
        skeptic="nothing dropped — fixture pages are canned, not live web",
        spent={"gets": 0, "searches": 0, "tokens": 0, "rupees": 0, "fixture": True},
        capped_at="fixture",
    )
    return {"signal": signal, "score": score, "report": report}


def _lays_fixture(pack: dict) -> dict:
    practice = pack.get("practice") or {}
    radar = pack.get("radar") or {}
    query_id = str(radar.get("query_id") or "snacks_in")
    quote = str(
        practice.get("quote")
        or "Chile Limón ridged chips are getting a closer look among Indian snackers this week."
    )
    follow = str(practice.get("follow") or "Same-host follow-up on monsoon evening snack talk.")
    signal = Signal(
        signal_id=FIXTURE_SIGNAL_ID,
        seen_at=STAMP,
        happened_at=STAMP,
        source="rss",
        url=LAYS_SEED_URL,
        title=str(practice.get("title") or "Lay's Chile Limón chips snacks flavour India"),
        snippet=str(
            practice.get("snippet")
            or "Ridged potato chips with lime and chilli flavour for Indian evenings."
        ),
        query_id=query_id,
    )
    score = Score(
        signal_id=FIXTURE_SIGNAL_ID,
        brand_fit=8,
        velocity=6,
        safety="ok",
        reason=str(practice.get("reason") or "Practice idea. Chile Limón flavour, not a health claim."),
        gate="deep_dive",
        model="fixture",
        prompt_version="unofficial-lays-1",
    )
    fetched = STAMP.isoformat()
    report = TrendReport(
        report_id=FIXTURE_REPORT_ID,
        signal_id=FIXTURE_SIGNAL_ID,
        what=str(
            practice.get("what")
            or "Chile Limón talk is up this week. Lime heat, ridged crunch, India evenings."
        ),
        why_now=str(
            practice.get("why_now")
            or "Humidity plus 4pm hunger. A stand-in idea when live headlines are a weak brand match."
        ),
        who=str(
            practice.get("who")
            or "People in India talking about chips, flavour, and evening snacks"
        ),
        angles=list(
            practice.get("angles")
            or ["lime-then-chilli", "4pm desk crunch", "monsoon evening pack"]
        ),
        risks=list(
            practice.get("risks")
            or [
                "do not treat snack talk as a health claim",
                "do not treat this as a PepsiCo or Lay's approval",
            ]
        ),
        sources=[
            {
                "url": LAYS_SEED_URL,
                "fetched_at": fetched,
                "hash": _hash(quote),
                "quote": quote,
            },
            {
                "url": LAYS_FOLLOW_URL,
                "fetched_at": fetched,
                "hash": _hash(follow),
                "quote": follow,
            },
        ],
        skeptic="nothing dropped — fixture pages are canned, not live web",
        spent={"gets": 0, "searches": 0, "tokens": 0, "rupees": 0, "fixture": True},
        capped_at="fixture",
    )
    return {"signal": signal, "score": score, "report": report}


def persist_unofficial_fixture() -> dict:
    """Write the fixture signal, deep_dive score, and report so factory can run."""
    from db import upsert_reports, upsert_scores, upsert_signals

    pack = unofficial_fixture_pack()
    upsert_signals([pack["signal"]])
    upsert_scores([pack["score"]])
    upsert_reports([pack["report"]])
    return pack
