"""Unofficial canned deep-dive. Same seed as Task 10 belt tests. Not this Fetch."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

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


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def unofficial_fixture_pack() -> dict:
    """Labeled unofficial Neutrogena fixture. Create post can run from this report."""
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
        why_now=(
            "Practice idea. Use this when live news does not give us a closer look."
        ),
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


def persist_unofficial_fixture() -> dict:
    """Write the fixture signal, deep_dive score, and report so factory can run."""
    from db import upsert_reports, upsert_scores, upsert_signals

    pack = unofficial_fixture_pack()
    upsert_signals([pack["signal"]])
    upsert_scores([pack["score"]])
    upsert_reports([pack["report"]])
    return pack
