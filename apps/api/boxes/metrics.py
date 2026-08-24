"""Ops visibility — one dict of the numbers that matter on the desk.

Feeds GET /metrics: approve rate, image spend vs budget, breaker state,
last radar/factory runs. Everything comes from single queries over the
existing tables (plus the shared CHAT_BREAKER and boxes.image_budget),
so the endpoint stays cheap enough to poll every 30 seconds.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone

from boxes.image_budget import budget_usd, spent_usd
from db import connect, init_db
from harness.breaker import CHAT_BREAKER
from harness.slo import degraded_runs

# Captured when this module first loads (≈ API process start).
PROCESS_STARTED_AT = time.time()

PAINT_WINDOW_HOURS = 24


def _window_cutoff_iso(hours: float = PAINT_WINDOW_HOURS) -> str:
    """ISO stamp `hours` ago. Event ts values are ISO-8601 UTC strings."""
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _draft_stats(conn) -> dict:
    """drafts_total, flag_human_rate, avg_judge_rounds in one pass."""
    row = conn.execute(
        """
        SELECT COUNT(*) AS total,
               COALESCE(SUM(flag_human), 0) AS flagged,
               AVG(round) AS avg_round
        FROM drafts
        """
    ).fetchone()
    total = int(row["total"])
    return {
        "drafts_total": total,
        "flag_human_rate": round(int(row["flagged"]) / total, 4) if total else None,
        "avg_judge_rounds": round(float(row["avg_round"]), 2)
        if row["avg_round"] is not None
        else None,
    }


def _decision_stats(conn) -> dict:
    """decisions_total and approve_rate in one pass."""
    row = conn.execute(
        """
        SELECT COUNT(*) AS total,
               COALESCE(SUM(CASE WHEN verdict = 'approve' THEN 1 ELSE 0 END), 0)
                   AS approved
        FROM decisions
        """
    ).fetchone()
    total = int(row["total"])
    return {
        "decisions_total": total,
        "approve_rate": round(int(row["approved"]) / total, 4) if total else None,
    }


def _event_stats(conn) -> dict:
    """Last-run timestamps plus paints inside the rolling window."""
    row = conn.execute(
        """
        SELECT MAX(CASE WHEN kind = 'radar_end' THEN ts END) AS radar_ts,
               MAX(CASE WHEN kind = 'factory_end' THEN ts END) AS factory_ts
        FROM events
        WHERE kind IN ('radar_end', 'factory_end')
        """
    ).fetchone()
    painted = 0
    rows = conn.execute(
        "SELECT payload FROM events WHERE kind = 'paint_end' AND ts >= ?",
        (_window_cutoff_iso(),),
    ).fetchall()
    for paint in rows:
        try:
            if json.loads(paint["payload"]).get("image"):
                painted += 1
        except (json.JSONDecodeError, TypeError):
            continue
    return {
        "images_painted_24h": painted,
        "last_radar_run_at": row["radar_ts"],
        "last_factory_run_at": row["factory_ts"],
    }


def _chat_model() -> str | None:
    """Configured chat model name, or None when running template-only."""
    from adapters.chat_litellm import build_chat

    return getattr(build_chat(), "model", None)


def collect_metrics() -> dict:
    """The whole ops picture as a plain JSON-able dict."""
    init_db()
    conn = connect()
    try:
        stats = {**_draft_stats(conn), **_decision_stats(conn), **_event_stats(conn)}
    finally:
        conn.close()
    return {
        **stats,
        "image_spend_usd": spent_usd(),
        "image_budget_usd": budget_usd(),
        "breaker_state": CHAT_BREAKER.state,
        "chat_model": _chat_model(),
        "uptime_s": max(0, int(time.time() - PROCESS_STARTED_AT)),
        "degraded_runs_24h": degraded_runs(),
    }
