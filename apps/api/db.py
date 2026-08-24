from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from models import Brief, Concept, Decision, Draft, RegistryClaim, Score, Signal, TrendReport

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

            CREATE TABLE IF NOT EXISTS api_keys (
                key_hash TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
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

            CREATE TABLE IF NOT EXISTS claims_registry (
                            claim_id TEXT PRIMARY KEY,
                            text TEXT NOT NULL,
                            sku TEXT NOT NULL DEFAULT '*',
                            market TEXT NOT NULL DEFAULT 'IN',
                            source_url TEXT NOT NULL,
                            evidence_ref TEXT NOT NULL DEFAULT '',
                            status TEXT NOT NULL,
                            review_by TEXT,
                            notes TEXT NOT NULL DEFAULT '',
                            jurisdictions TEXT NOT NULL DEFAULT '[]',
                            seeded_at TEXT
                        );

            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'running',
                step_results TEXT NOT NULL DEFAULT '[]',
                params TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        _ensure_column(
            conn, "drafts", "flag_human", "flag_human INTEGER NOT NULL DEFAULT 0"
        )
        _ensure_column(
            conn,
            "claims_registry",
            "jurisdictions",
            "jurisdictions TEXT NOT NULL DEFAULT '[]'",
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


def get_step_ms_series(hours: float = 24) -> list[dict]:
    """Parsed harness_step timing rows for the last `hours`.

    One row per step execution: {"ts", "step", "ok", "ms"}. Feeds the SLO
    percentiles in harness/slo.py — list_events() is capped and unfiltered,
    so this walks only kind='harness_step' inside the window. Rows with a
    malformed payload are skipped, never raise.
    """
    init_db()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=max(0.0, hours))).isoformat()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT ts, payload FROM events"
            " WHERE kind = 'harness_step' AND ts >= ? ORDER BY ts ASC",
            (cutoff,),
        ).fetchall()
    finally:
        conn.close()
    out: list[dict] = []
    for row in rows:
        try:
            payload = json.loads(row["payload"])
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue
        step_name = payload.get("step")
        ms = payload.get("ms")
        if not isinstance(step_name, str) or not isinstance(ms, (int, float)):
            continue
        out.append(
            {
                "ts": row["ts"],
                "step": step_name,
                "ok": bool(payload.get("ok")),
                "ms": ms,
            }
        )
    return out


def upsert_registry_claims(claims: list[RegistryClaim]) -> None:
    """Persist claims-registry rows. Same claim_id replaces (seed is source of truth)."""
    if not claims:
        return
    init_db()
    conn = connect()
    try:
        now = datetime.now(timezone.utc).isoformat()
        conn.executemany(
            """
            INSERT OR REPLACE INTO claims_registry (
                claim_id, text, sku, market, source_url, evidence_ref,
                status, review_by, notes, jurisdictions, seeded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    c.claim_id,
                    c.text,
                    c.sku,
                    c.market,
                    c.source_url,
                    c.evidence_ref,
                    c.status,
                    c.review_by.isoformat() if c.review_by else None,
                    c.notes,
                    json.dumps(c.jurisdictions or []),
                    now,
                )
                for c in claims
            ],
        )
        conn.commit()
    finally:
        conn.close()


def list_registry_claims() -> list[RegistryClaim]:
    """Load the claims registry from SQLite. Empty list if never seeded."""
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM claims_registry ORDER BY claim_id"
        ).fetchall()
        out: list[RegistryClaim] = []
        for row in rows:
            review = row["review_by"]
            parsed = None
            if review:
                try:
                    parsed = _parse_dt(review)
                except ValueError:
                    parsed = None
            out.append(
                RegistryClaim(
                    claim_id=row["claim_id"],
                    text=row["text"],
                    sku=row["sku"] or "*",
                    market=row["market"] or "IN",
                    source_url=row["source_url"],
                    evidence_ref=row["evidence_ref"] or "",
                    status=row["status"],
                    review_by=parsed,
                    notes=row["notes"] or "",
                    jurisdictions=_json_load(
                        row["jurisdictions"] if "jurisdictions" in row.keys() else "[]",
                        [],
                    ),
                )
            )
        return out
    finally:
        conn.close()


_RUN_LEDGER_STARTS = "--- Run ledger: per-run step results for resumable pipelines ---"

RUN_KINDS = ("radar", "factory")
RUN_STATUSES = ("running", "done", "failed", "interrupted")
STALE_RUNNING_AFTER_S = 30 * 60  # running longer than this reads as interrupted


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _effective_run_status(status: str, updated_at: str | None, now: datetime | None) -> str:
    """A row stuck in 'running' past the staleness window reads as interrupted."""
    if status != "running":
        return status
    stamp = _parse_dt(updated_at)
    if stamp is None:
        return status
    now_dt = now or datetime.now(timezone.utc)
    if (now_dt - stamp).total_seconds() > STALE_RUNNING_AFTER_S:
        return "interrupted"
    return status


def _run_from_row(row: sqlite3.Row, now: datetime | None = None) -> dict:
    keys = row.keys()
    status = _effective_run_status(
        row["status"], row["updated_at"] if "updated_at" in keys else None, now
    )
    return {
        "run_id": row["run_id"],
        "kind": row["kind"],
        "status": status,
        "step_results": _json_load(row["step_results"], []) if "step_results" in keys else [],
        "params": _json_load(row["params"], {}) if "params" in keys else {},
        "created_at": row["created_at"] if "created_at" in keys else None,
        "updated_at": row["updated_at"] if "updated_at" in keys else None,
    }


def create_run(
    kind: str, *, params: dict | None = None, run_id: str | None = None
) -> dict:
    """Open a ledger row for one radar/factory run. Starts life as 'running'."""
    if kind not in RUN_KINDS:
        raise ValueError("Runs are either 'radar' or 'factory'.")
    init_db()
    rid = run_id or f"run_{uuid4().hex[:10]}"
    ts = _now_iso()
    conn = connect()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO runs (
                run_id, kind, status, step_results, params, created_at, updated_at
            ) VALUES (?, ?, 'running', '[]', ?, ?, ?)
            """,
            (rid, kind, json.dumps(params or {}), ts, ts),
        )
        conn.commit()
    finally:
        conn.close()
    return get_run(rid) or {
        "run_id": rid,
        "kind": kind,
        "status": "running",
        "step_results": [],
        "params": params or {},
        "created_at": ts,
        "updated_at": ts,
    }


def update_run(run_id: str, *, status: str | None = None) -> dict | None:
    """Flip a run's status and bump updated_at. None if unknown."""
    if status is not None and status not in RUN_STATUSES:
        raise ValueError("That run status does not exist.")
    init_db()
    conn = connect()
    try:
        if conn.execute("SELECT 1 FROM runs WHERE run_id = ?", (run_id,)).fetchone() is None:
            return None
        sets = ["updated_at = ?"]
        args: list[object] = [_now_iso()]
        if status is not None:
            sets.append("status = ?")
            args.append(status)
        args.append(run_id)
        conn.execute(f"UPDATE runs SET {', '.join(sets)} WHERE run_id = ?", args)
        conn.commit()
    finally:
        conn.close()
    return get_run(run_id)


def record_step_result(run_id: str, entry: dict) -> None:
    """Append one StepResult snapshot into the run's ordered step list.

    Same-name entries replace in place so reruns stay idempotent per run.
    Raises ValueError when the run row does not exist.
    """
    init_db()
    conn = connect()
    try:
        row = conn.execute(
            "SELECT step_results FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"That run was not found: {run_id}")
        steps_list = _json_load(row["step_results"], [])
        if not isinstance(steps_list, list):
            steps_list = []
        replaced = False
        out: list[dict] = []
        for item in steps_list:
            if isinstance(item, dict) and item.get("name") == entry.get("name"):
                out.append(entry)
                replaced = True
            else:
                out.append(item)
        if not replaced:
            out.append(entry)
        conn.execute(
            "UPDATE runs SET step_results = ?, updated_at = ? WHERE run_id = ?",
            (json.dumps(out), _now_iso(), run_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_run(run_id: str, *, now: datetime | None = None) -> dict | None:
    """Load one run row; stale 'running' rows surface as 'interrupted'."""
    init_db()
    conn = connect()
    try:
        row = conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            return None
        return _run_from_row(row, now=now)
    finally:
        conn.close()


def list_runs(
    *,
    status: str | None = None,
    kind: str | None = None,
    limit: int = 100,
    now: datetime | None = None,
) -> list[dict]:
    """Newest-first run listing with optional status/kind filters."""
    if status is not None and status not in RUN_STATUSES:
        raise ValueError("Unknown run status. Use running, done, failed or interrupted.")
    if kind is not None and kind not in RUN_KINDS:
        raise ValueError("Unknown run kind. Use radar or factory.")
    init_db()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY created_at DESC, run_id DESC"
        ).fetchall()
    finally:
        conn.close()
    out = [_run_from_row(row, now=now) for row in rows]
    if status is not None:
        out = [item for item in out if item["status"] == status]
    if kind is not None:
        out = [item for item in out if item["kind"] == kind]
    return out[: max(1, min(limit, 500))]


def find_brief_id_for_report(report_id: str) -> str | None:
    """Most recent brief built from a report — lets factory resume skip rebuilds."""
    init_db()
    conn = connect()
    try:
        row = conn.execute(
            "SELECT brief_id FROM briefs WHERE report_id = ? ORDER BY rowid DESC LIMIT 1",
            (report_id,),
        ).fetchone()
        return row["brief_id"] if row else None
    finally:
        conn.close()


_INIT_DONE = ""


def get_conn() -> sqlite3.Connection:
    """Open a connection with row access by name.

    Minimal shared helper: same settings as connect(). Ensures the schema
    exists first so early callers cannot hit a missing table. Callers own
    commit/close.
    """
    global _INIT_DONE
    path = get_sqlite_path()
    if _INIT_DONE != path:
        init_db()
        _INIT_DONE = path
    return connect()
