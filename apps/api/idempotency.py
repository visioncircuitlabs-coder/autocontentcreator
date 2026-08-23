"""Idempotency-Key cache for radar/factory runs. Same key within 10 min replays."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from db import connect

WINDOW_MINUTES = 10


def _ensure_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS idempotency_keys (
            key TEXT PRIMARY KEY,
            endpoint TEXT NOT NULL,
            ts TEXT NOT NULL,
            response TEXT NOT NULL
        )
        """
    )


def get_cached(key: str, endpoint: str) -> tuple[dict | None, bool]:
    """Return (response, True) when a fresh cached result exists for this key."""
    key = (key or "").strip()
    if not key:
        return None, False
    conn = connect()
    try:
        _ensure_table(conn)
        row = conn.execute(
            "SELECT ts, response FROM idempotency_keys WHERE key = ? AND endpoint = ?",
            (key, endpoint),
        ).fetchone()
        if row is None:
            return None, False
        ts = datetime.fromisoformat(str(row["ts"]))
        fresh = datetime.now(timezone.utc) - ts <= timedelta(minutes=WINDOW_MINUTES)
        if not fresh:
            return None, False
        return json.loads(row["response"]), True
    finally:
        conn.close()


def store(key: str, endpoint: str, response: object) -> None:
    """Cache a successful run result under this key. No-op without a key."""
    key = (key or "").strip()
    if not key:
        return
    conn = connect()
    try:
        _ensure_table(conn)
        conn.execute(
            "INSERT OR REPLACE INTO idempotency_keys (key, endpoint, ts, response)"
            " VALUES (?, ?, ?, ?)",
            (
                key,
                endpoint,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(response, default=str),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def purge_stale() -> int:
    """Drop entries older than the window. Returns rows removed."""
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=WINDOW_MINUTES)).isoformat()
    conn = connect()
    try:
        _ensure_table(conn)
        cur = conn.execute(
            "DELETE FROM idempotency_keys WHERE ts < ?", (cutoff,)
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
