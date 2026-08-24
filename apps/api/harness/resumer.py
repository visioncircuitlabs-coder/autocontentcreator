"""Resume a failed/interrupted run from its ledger row.

Pragmatic contract (per docs/bar/agentic-bar.md C3):
- every stage re-runs through belt functions whose writes are idempotent
  upserts keyed by content hashes/ids, so "rerun" is always safe;
- stages whose inputs already exist are recorded as skipped (fast path)
  where a cheap existence check is available;
- the run row collects ordered StepResult entries and ends done/failed.
"""

from __future__ import annotations

import time

from db import create_run, get_report, get_run, record_step_result, update_run
from harness.steps import StepResult
from obs import emit
from ports import ChatModel


def _snapshot(res: StepResult) -> dict:
    return {
        "name": res.name,
        "ok": res.ok,
        "ms": res.ms,
        "attempts": res.attempts,
        "error": res.error,
        "skipped": res.skipped,
        "started_at": res.started_at,
    }


def resume_run(run: dict, *, chat: ChatModel | None, now=None) -> dict:
    """Resume one radar or factory run. Returns the refreshed run row."""
    from boxes.belt import run_factory, run_radar  # local: avoid import cycle

    rid = run["run_id"]
    kind = run["kind"]
    params = run.get("params") or {}
    update_run(rid, status="running")
    emit("resume_start", run_kind=kind)

    def record(name: str, fn, *, skip_if):
        t0 = time.monotonic()
        if skip_if():
            entry = {
                "name": name,
                "ok": True,
                "ms": int((time.monotonic() - t0) * 1000),
                "attempts": 0,
                "error": None,
                "skipped": True,
                "started_at": "",
            }
            record_step_result(rid, entry)
            return None
        try:
            fn()
            ok, err = True, None
        except Exception as exc:  # noqa: BLE001 — envelope records everything
            ok, err = False, f"{type(exc).__name__}: {exc}"
        entry = {
            "name": name,
            "ok": ok,
            "ms": int((time.monotonic() - t0) * 1000),
            "attempts": 1,
            "error": err,
            "skipped": False,
            "started_at": "",
        }
        record_step_result(rid, entry)
        if not ok:
            raise RuntimeError(f"stage {name} failed: {err}")

    try:
        if kind == "radar":
            report_id = params.get("report_id")

            def have_report():
                return bool(report_id) and get_report(report_id) is not None

            pack = None

            def do_radar():
                nonlocal pack
                pack = run_radar(chat=chat)

            record("radar", do_radar, skip_if=have_report)
        else:
            report_id = params.get("report_id")

            drafts: list = []

            def do_factory():
                nonlocal drafts
                drafts = run_factory(report_id or "", chat=chat)

            # factory resume: brief/concepts upsert idempotently; the cheap
            # correctness choice is to rerun factory (skip only never)
            def have_drafts():
                return False

            record("factory", do_factory, skip_if=have_drafts)
        update_run(rid, status="done")
        emit("resume_end", run_kind=kind, ok=True)
    except Exception:
        update_run(rid, status="failed")
        emit("resume_end", run_kind=kind, ok=False)
        raise

    fresh = get_run(rid) or {}
    fresh["resumed"] = True
    return fresh
