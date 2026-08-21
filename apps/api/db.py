from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from models import Brief, Concept, Decision, Draft, Score, Signal, TrendReport

DEFAULT_SQLITE_PATH = "data/demo.db"


def get_sqlite_path() -> str:
    return os.environ.get("SQLITE_PATH", DEFAULT_SQLITE_PATH)


def connect() -> sqlite3.Connection:
    path = get_sqlite_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column(
    conn: sqlite3.Connection, table: str, column: str, ddl: str
) -> None:
    cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


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

            CREATE TABLE IF NOT EXISTS briefs (
                brief_id TEXT PRIMARY KEY,
                report_id TEXT NOT NULL,
                pack TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS concepts (
                concept_id TEXT PRIMARY KEY,
                brief_id TEXT NOT NULL,
                pack TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS drafts (
                draft_id TEXT PRIMARY KEY,
                brief_id TEXT NOT NULL,
                caption TEXT NOT NULL,
                variant INTEGER NOT NULL,
                image_path TEXT,
                judge TEXT,
                rules TEXT NOT NULL,
                round INTEGER NOT NULL,
                flag_human INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS decisions (
                draft_id TEXT NOT NULL,
                user TEXT NOT NULL,
                verdict TEXT NOT NULL,
                reason TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                PRIMARY KEY (draft_id, decided_at)
            );

            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                ts TEXT NOT NULL,
                kind TEXT NOT NULL,
                payload TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS track_record (
                draft_id TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                user TEXT NOT NULL,
                verdict TEXT NOT NULL,
                reason TEXT NOT NULL,
                distilled TEXT NOT NULL,
                caption TEXT NOT NULL DEFAULT '',
                judge TEXT,
                sku TEXT,
                market TEXT,
                flag_human INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (draft_id, decided_at)
            );
            """
        )
        _ensure_column(
            conn, "drafts", "flag_human", "flag_human INTEGER NOT NULL DEFAULT 0"
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


def upsert_reports(reports: list[TrendReport]) -> None:
    """Persist deep-dive rows. One report per report_id."""
    init_db()
    conn = connect()
    try:
        conn.executemany(
            """
            INSERT OR REPLACE INTO reports (
                report_id, signal_id, what, why_now, who,
                angles, risks, sources, skeptic, spent, capped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    r.report_id,
                    r.signal_id,
                    r.what,
                    r.why_now,
                    r.who,
                    json.dumps(r.angles),
                    json.dumps(r.risks),
                    json.dumps(r.sources),
                    r.skeptic,
                    json.dumps(r.spent),
                    r.capped_at,
                )
                for r in reports
            ],
        )
        conn.commit()
    finally:
        conn.close()


def _json_load(value, default):
    if value is None or value == "":
        return default
    if isinstance(value, (list, dict)):
        return value
    return json.loads(value)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _signal_from_row(row: sqlite3.Row) -> Signal:
    return Signal(
        signal_id=row["signal_id"],
        seen_at=_parse_dt(row["seen_at"]) or datetime.now(timezone.utc),
        happened_at=_parse_dt(row["happened_at"]),
        source=row["source"],
        url=row["url"],
        title=row["title"],
        snippet=row["snippet"],
        lang=row["lang"],
        market=row["market"],
        query_id=row["query_id"],
        raw_ref=row["raw_ref"] or "",
    )


def _score_from_row(row: sqlite3.Row) -> Score:
    return Score(
        signal_id=row["signal_id"],
        brand_fit=row["brand_fit"],
        velocity=row["velocity"],
        safety=row["safety"],
        reason=row["reason"],
        gate=row["gate"],
        model=row["model"],
        prompt_version=row["prompt_version"],
    )


def _report_from_row(row: sqlite3.Row) -> TrendReport:
    return TrendReport(
        report_id=row["report_id"],
        signal_id=row["signal_id"],
        what=row["what"],
        why_now=row["why_now"],
        who=row["who"],
        angles=_json_load(row["angles"], []),
        risks=_json_load(row["risks"], []),
        sources=_json_load(row["sources"], []),
        skeptic=row["skeptic"],
        spent=_json_load(row["spent"], {}),
        capped_at=row["capped_at"],
    )


def _flag_human_from_row(row: sqlite3.Row, judge: dict | None) -> bool:
    flag = False
    keys = row.keys()
    if "flag_human" in keys and row["flag_human"] is not None:
        flag = bool(row["flag_human"])
    if not flag and isinstance(judge, dict):
        flag = bool(judge.get("flag_human"))
    return flag


def _draft_from_row(row: sqlite3.Row) -> Draft:
    judge = _json_load(row["judge"], None)
    flag = _flag_human_from_row(row, judge if isinstance(judge, dict) else None)
    if isinstance(judge, dict):
        judge = dict(judge)
        judge["flag_human"] = flag
    return Draft(
        draft_id=row["draft_id"],
        brief_id=row["brief_id"],
        caption=row["caption"],
        variant=row["variant"],
        image_path=row["image_path"],
        judge=judge,
        rules=_json_load(row["rules"], []),
        round=row["round"],
        flag_human=flag,
    )


def _decision_from_row(row: sqlite3.Row) -> Decision:
    return Decision(
        draft_id=row["draft_id"],
        user=row["user"],
        verdict=row["verdict"],
        reason=row["reason"],
        decided_at=_parse_dt(row["decided_at"]) or datetime.now(timezone.utc),
    )


def get_report(report_id: str) -> TrendReport | None:
    """Load one TrendReport, or None if missing."""
    init_db()
    conn = connect()
    try:
        row = conn.execute(
            "SELECT * FROM reports WHERE report_id = ?",
            (report_id,),
        ).fetchone()
        if row is None:
            return None
        return _report_from_row(row)
    finally:
        conn.close()


def upsert_brief(brief: Brief) -> None:
    """Persist one factory brief pack. Same brief_id replaces."""
    init_db()
    conn = connect()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO briefs (brief_id, report_id, pack)
            VALUES (?, ?, ?)
            """,
            (brief.brief_id, brief.report_id, brief.model_dump_json()),
        )
        conn.commit()
    finally:
        conn.close()


def upsert_concepts(concepts: list[Concept]) -> None:
    """Persist the strategist grid for a brief. Same concept_id replaces."""
    if not concepts:
        return
    init_db()
    conn = connect()
    try:
        conn.executemany(
            """
            INSERT OR REPLACE INTO concepts (concept_id, brief_id, pack)
            VALUES (?, ?, ?)
            """,
            [(item.concept_id, item.brief_id, item.model_dump_json()) for item in concepts],
        )
        conn.commit()
    finally:
        conn.close()


def list_concepts(brief_id: str) -> list[Concept]:
    """Load the concept grid for one brief, or empty if none stored."""
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT pack FROM concepts WHERE brief_id = ? ORDER BY concept_id",
            (brief_id,),
        ).fetchall()
        return [Concept.model_validate_json(row["pack"]) for row in rows]
    finally:
        conn.close()


def get_brief(brief_id: str) -> Brief | None:
    """Load one Brief pack, or None if missing."""
    init_db()
    conn = connect()
    try:
        row = conn.execute(
            "SELECT pack FROM briefs WHERE brief_id = ?",
            (brief_id,),
        ).fetchone()
        if row is None:
            return None
        return Brief.model_validate_json(row["pack"])
    finally:
        conn.close()


def upsert_draft(draft: Draft) -> None:
    """Persist a factory draft. flag_human is a column and copied into judge JSON."""
    init_db()
    judge = dict(draft.judge) if isinstance(draft.judge, dict) else {}
    if draft.judge is not None and not isinstance(draft.judge, dict):
        judge = {"value": draft.judge}
    flag = bool(draft.flag_human) or bool(judge.get("flag_human"))
    judge["flag_human"] = flag
    payload = judge if draft.judge is not None or flag else None
    conn = connect()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO drafts (
                draft_id, brief_id, caption, variant, image_path,
                judge, rules, round, flag_human
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                draft.draft_id,
                draft.brief_id,
                draft.caption,
                draft.variant,
                draft.image_path,
                json.dumps(payload) if payload is not None else None,
                json.dumps(list(draft.rules or [])),
                draft.round,
                1 if flag else 0,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_draft(draft_id: str) -> Draft | None:
    init_db()
    conn = connect()
    try:
        row = conn.execute(
            "SELECT * FROM drafts WHERE draft_id = ?",
            (draft_id,),
        ).fetchone()
        if row is None:
            return None
        return _draft_from_row(row)
    finally:
        conn.close()


def insert_decision(decision: Decision) -> None:
    init_db()
    conn = connect()
    try:
        conn.execute(
            """
            INSERT INTO decisions (draft_id, user, verdict, reason, decided_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                decision.draft_id,
                decision.user,
                decision.verdict,
                decision.reason,
                decision.decided_at.isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def insert_track_record(entry: dict) -> None:
    init_db()
    conn = connect()
    try:
        judge = entry.get("judge")
        conn.execute(
            """
            INSERT OR REPLACE INTO track_record (
                draft_id, decided_at, user, verdict, reason, distilled,
                caption, judge, sku, market, flag_human
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["draft_id"],
                entry["decided_at"],
                entry["user"],
                entry["verdict"],
                entry["reason"],
                entry.get("distilled") or entry["reason"],
                entry.get("caption") or "",
                json.dumps(judge) if judge is not None else None,
                entry.get("sku") or "",
                entry.get("market") or "",
                1 if entry.get("flag_human") else 0,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def list_signals() -> list[Signal]:
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM signals ORDER BY seen_at DESC, signal_id"
        ).fetchall()
        return [_signal_from_row(row) for row in rows]
    finally:
        conn.close()


def list_scores() -> list[Score]:
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM scores ORDER BY signal_id"
        ).fetchall()
        return [_score_from_row(row) for row in rows]
    finally:
        conn.close()


def list_reports() -> list[TrendReport]:
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM reports ORDER BY report_id"
        ).fetchall()
        return [_report_from_row(row) for row in rows]
    finally:
        conn.close()


def list_drafts() -> list[Draft]:
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM drafts ORDER BY round DESC, draft_id"
        ).fetchall()
        return [_draft_from_row(row) for row in rows]
    finally:
        conn.close()


def list_queue() -> list[Draft]:
    """Drafts that have not yet been approved or rejected."""
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT d.* FROM drafts d
            WHERE NOT EXISTS (
                SELECT 1 FROM decisions x WHERE x.draft_id = d.draft_id
            )
            ORDER BY d.round DESC, d.draft_id
            """
        ).fetchall()
        return [_draft_from_row(row) for row in rows]
    finally:
        conn.close()


def list_decisions() -> list[Decision]:
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM decisions ORDER BY decided_at DESC"
        ).fetchall()
        return [_decision_from_row(row) for row in rows]
    finally:
        conn.close()


def list_track_record() -> list[dict]:
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM track_record ORDER BY decided_at DESC"
        ).fetchall()
        out: list[dict] = []
        for row in rows:
            out.append(
                {
                    "draft_id": row["draft_id"],
                    "decided_at": row["decided_at"],
                    "user": row["user"],
                    "verdict": row["verdict"],
                    "reason": row["reason"],
                    "distilled": row["distilled"],
                    "caption": row["caption"],
                    "judge": _json_load(row["judge"], None),
                    "sku": row["sku"] or "",
                    "market": row["market"] or "",
                    "flag_human": bool(row["flag_human"]),
                }
            )
        return out
    finally:
        conn.close()


def insert_event(event_id: str, ts: str, kind: str, payload: object) -> None:
    init_db()
    conn = connect()
    try:
        conn.execute(
            "INSERT INTO events (id, ts, kind, payload) VALUES (?, ?, ?, ?)",
            (event_id, ts, kind, json.dumps(payload, default=str)),
        )
        conn.commit()
    finally:
        conn.close()


def list_events(limit: int = 100) -> list[dict]:
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT id, ts, kind, payload FROM events ORDER BY ts DESC LIMIT ?",
            (max(1, min(limit, 500)),),
        ).fetchall()
        out: list[dict] = []
        for row in rows:
            out.append(
                {
                    "id": row["id"],
                    "ts": row["ts"],
                    "kind": row["kind"],
                    "payload": _json_load(row["payload"], {}),
                }
            )
        return out
    finally:
        conn.close()
