"""SLO rollups — per-step latency/error percentiles + degraded-run gauge.

Closes two gaps from docs/bar/agentic-bar.md using only the event history
that already lands in the events table (no new instrumentation):

- G3: per-step p50/p95 latency and error-rate computed over a rolling
  window from kind='harness_step' payloads (emitted by harness/steps.py).
- E2: degraded-mode visibility — count runs that finished degraded in the
  window, from two signals already in the log:
    1. template-mode start: radar_start/factory_start whose payload has no
       chat model (belt.py emits chat=None when running on templates);
    2. resume-without-clean-end: resume_* events for a run kind with no
       matching radar_end/factory_end after them (a fully successful resume
       re-emits the belt's *_end; a skipped or failed resume does not).

Feeds GET /slo and one line of /metrics. Read-only over SQLite; the
degraded counter never raises so /metrics cannot regress because of it.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

from db import connect, get_step_ms_series, init_db

DEFAULT_HOURS = 24
MAX_HOURS = 24 * 30  # one month of lookback is plenty for an ops window

END_KIND_FOR_RUN = {"radar": "radar_end", "factory": "factory_end"}
START_KINDS = ("radar_start", "factory_start")
RESUME_PREFIX = "resume_"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_hours(raw: object) -> float:
    """Coerce ?hours= into a positive float window. Friendly ValueError."""
    if raw is None or raw == "":
        return float(DEFAULT_HOURS)
    try:
        hours = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError("Hours must be a number, like /slo?hours=24.") from None
    if not math.isfinite(hours) or hours <= 0 or hours > MAX_HOURS:
        raise ValueError(f"Hours must be between 1 minute and {MAX_HOURS}. Try /slo?hours=24.")
    return hours


def percentile(values: list[float], pct: float) -> float:
    """Linear-interpolated percentile (numpy 'linear' method) of a sample.

    percentile([10, 20, 30, 40], 50) == 25.0 — halfway between the middle
    pair; percentile([x], _) is always x.
    """
    if not values:
        raise ValueError("percentile needs at least one value")
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * (pct / 100.0)
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return ordered[lo]
    frac = rank - lo
    return ordered[lo] + (ordered[hi] - ordered[lo]) * frac


def step_rollups(hours: float = DEFAULT_HOURS) -> dict[str, dict]:
    """Per-step {count, p50_ms, p95_ms, error_rate} over the last `hours`.

    Groups harness_step events by payload['step']. error_rate is the share
    of executions with ok=false (skipped stages are ok=true by contract).
    """
    series = get_step_ms_series(hours)
    groups: dict[str, list[tuple[bool, int]]] = {}
    for row in series:
        groups.setdefault(row["step"], []).append((row["ok"], row["ms"]))
    out: dict[str, dict] = {}
    for name, runs in sorted(groups.items()):
        total = len(runs)
        errors = sum(1 for ok, _ in runs if not ok)
        mss = [ms for _, ms in runs]
        out[name] = {
            "count": total,
            "p50_ms": int(round(percentile(mss, 50))),
            "p95_ms": int(round(percentile(mss, 95))),
            "error_rate": round(errors / total, 4) if total else 0.0,
        }
    return out


def degraded_runs(hours: float = DEFAULT_HOURS) -> int:
    """Count degraded finishes in the last `hours`. Never raises.

    A run counts once per signal kind:
    - each radar_start/factory_start with no chat model in its payload;
    - one per run kind whose resume_* events in the window have no clean
      radar_end/factory_end at-or-after the first resume stamp.
    """
    try:
        init_db()
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        conn = connect()
        try:
            rows = conn.execute(
                "SELECT ts, kind, payload FROM events WHERE ts >= ? ORDER BY ts ASC",
                (cutoff,),
            ).fetchall()
        finally:
            conn.close()

        template_starts = 0
        resume_stamps: dict[str, list[str]] = {}
        end_stamps: dict[str, list[str]] = {kind: [] for kind in END_KIND_FOR_RUN}
        for row in rows:
            kind = row["kind"]
            payload = _payload_of(row["payload"])
            if kind in START_KINDS:
                if not payload.get("chat"):
                    template_starts += 1
            elif kind.startswith(RESUME_PREFIX):
                run_kind = payload.get("run_kind")
                if run_kind in END_KIND_FOR_RUN:
                    resume_stamps.setdefault(run_kind, []).append(row["ts"])
            elif kind in END_KIND_FOR_RUN.values():
                run_kind = next(k for k, v in END_KIND_FOR_RUN.items() if v == kind)
                end_stamps[run_kind].append(row["ts"])

        resumed_without_clean_end = sum(
            1
            for run_kind, stamps in resume_stamps.items()
            if stamps and not any(ts >= min(stamps) for ts in end_stamps[run_kind])
        )
        return template_starts + resumed_without_clean_end
    except Exception:  # noqa: BLE001 — /metrics depends on this staying up
        return 0


def _payload_of(raw: object) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def slo_snapshot(raw_hours: object = None) -> dict:
    """The whole GET /slo body: step rollups + generated_at + the gauge."""
    hours = parse_hours(raw_hours)
    return {
        "steps": step_rollups(hours),
        "generated_at": _utc_now_iso(),
        "hours": hours,
        "degraded_runs_24h": degraded_runs(DEFAULT_HOURS),
    }
