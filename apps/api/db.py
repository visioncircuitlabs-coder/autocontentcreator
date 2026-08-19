from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from models import Score, Signal

DEFAULT_SQLITE_PATH = "data/demo.db"


def get_sqlite_path() -> str:
    return os.environ.get("SQLITE_PATH", DEFAULT_SQLITE_PATH)


def connect() -> sqlite3.Connection:
    path = get_sqlite_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create demo tables if they do not exist."""
    conn = connect()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                seen_at TEXT NOT NULL,
                happened_at TEXT,
                source TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                snippet TEXT NOT NULL,
                lang TEXT NOT NULL DEFAULT 'en',
                market TEXT NOT NULL DEFAULT 'IN',
                query_id TEXT NOT NULL,
                raw_ref TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS scores (
                signal_id TEXT PRIMARY KEY,
                brand_fit INTEGER NOT NULL,
                velocity INTEGER NOT NULL,
                safety TEXT NOT NULL,
                reason TEXT NOT NULL,
                gate TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_version TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                signal_id TEXT NOT NULL,
                what TEXT NOT NULL,
                why_now TEXT NOT NULL,
                who TEXT NOT NULL,
                angles TEXT NOT NULL,
                risks TEXT NOT NULL,
                sources TEXT NOT NULL,
                skeptic TEXT NOT NULL,
                spent TEXT NOT NULL,
                capped_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS claims (
                claim_id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                sku TEXT NOT NULL,
                market TEXT NOT NULL,
                evidence_ref TEXT NOT NULL,
                status TEXT NOT NULL,
                expires_at TEXT
            );

            CREATE TABLE IF NOT EXISTS drafts (
                draft_id TEXT PRIMARY KEY,
                brief_id TEXT NOT NULL,
                caption TEXT NOT NULL,
                variant INTEGER NOT NULL,
                image_path TEXT,
                judge TEXT,
                rules TEXT NOT NULL,
                round INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decisions (
                draft_id TEXT NOT NULL,
                user TEXT NOT NULL,
                verdict TEXT NOT NULL,
                reason TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                PRIMARY KEY (draft_id, decided_at)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def upsert_signals(signals: list[Signal]) -> None:
    """Persist Radar rows. Datetimes stored as ISO-8601 (timezone-aware)."""
    init_db()
    conn = connect()
    try:
        conn.executemany(
            """
            INSERT OR REPLACE INTO signals (
                signal_id, seen_at, happened_at, source, url, title,
                snippet, lang, market, query_id, raw_ref
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    s.signal_id,
                    s.seen_at.isoformat(),
                    s.happened_at.isoformat() if s.happened_at else None,
                    s.source,
                    s.url,
                    s.title,
                    s.snippet,
                    s.lang,
                    s.market,
                    s.query_id,
                    s.raw_ref,
                )
                for s in signals
            ],
        )
        conn.commit()
    finally:
        conn.close()


def upsert_scores(scores: list[Score]) -> None:
    """Persist scorer rows. One score per signal_id."""
    init_db()
    conn = connect()
    try:
        conn.executemany(
            """
            INSERT OR REPLACE INTO scores (
                signal_id, brand_fit, velocity, safety, reason,
                gate, model, prompt_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    s.signal_id,
                    s.brand_fit,
                    s.velocity,
                    s.safety,
                    s.reason,
                    s.gate,
                    s.model,
                    s.prompt_version,
                )
                for s in scores
            ],
        )
        conn.commit()
    finally:
        conn.close()
