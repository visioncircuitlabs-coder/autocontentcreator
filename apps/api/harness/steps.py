"""Step envelope — every pipeline node reports attempts, duration, status.

A "step" wraps any callable with: uniform timing, structured events (via
obs.emit), attempt counting, and an optional run_id so radar → factory →
paint events can be correlated in the log and audit trail.

When a run row exists (see harness.runs / db.create_run) each StepResult is
also persisted onto that row, keyed by run_id, so interrupted runs can be
inspected and resumed instead of restarted cold.
"""

from __future__ import annotations

import contextvars
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

from obs import emit

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Per-context pipeline run id (contextvar: safe under concurrent runs).
_run_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "harness_run_id", default=None
)


def set_run_id(run_id: str | None) -> None:
    _run_id_var.set(run_id)


def current_run_id() -> str | None:
    return _run_id_var.get()


def new_run_id(prefix: str = "run") -> str:
    from uuid import uuid4

    rid = f"{prefix}_{uuid4().hex[:10]}"
    set_run_id(rid)
    return rid


@dataclass
class StepResult:
    name: str
    ok: bool
    ms: int
    attempts: int = 1
    error: str | None = None
    value: Any = None
    exc: Exception | None = None  # original failure; re-raised by require_step
    resumable: bool = True  # False → resume reruns this stage (idempotent upserts)
    skipped: bool = False  # True → stage satisfied from stored artifacts on resume
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def meta(self) -> dict:
        return {
            "step": self.name,
            "ok": self.ok,
            "ms": self.ms,
            "attempts": self.attempts,
            "error": self.error,
        }

    def record(self) -> dict:
        """JSON-safe snapshot persisted onto the run row."""
        return {
            "name": self.name,
            "ok": self.ok,
            "ms": self.ms,
            "attempts": self.attempts,
            "error": self.error,
            "started_at": self.started_at,
            "resumable": self.resumable,
            "skipped": self.skipped,
        }


def _persist(result: StepResult) -> None:
    """Best-effort write of one StepResult into the active run row."""
    rid = current_run_id()
    if not rid:
        return
    try:
        from db import record_step_result

        record_step_result(rid, result.record())
    except Exception:  # noqa: BLE001 — bookkeeping must never break the belt
        logger.warning("could not persist step %s for %s", result.name, rid)


def step(
    name: str,
    fn: Callable[[], T],
    *,
    emit_events: bool = True,
    resumable: bool = True,
) -> StepResult:
    """Run one pipeline step with uniform envelope. Never raises."""
    t0 = time.monotonic()
    result = StepResult(name=name, ok=False, ms=0, resumable=resumable)
    try:
        result.value = fn()
        result.ok = True
    except Exception as exc:  # noqa: BLE001 — envelope records everything
        result.error = f"{type(exc).__name__}: {exc}"
        result.exc = exc
    finally:
        result.ms = int((time.monotonic() - t0) * 1000)
        if emit_events:
            payload: dict[str, Any] = dict(result.meta())
            rid = current_run_id()
            if rid:
                payload["run_id"] = rid
            emit("harness_step", **payload)
        _persist(result)
    return result


def step_skipped(
    name: str,
    *,
    value: Any = None,
    reason: str = "",
    resumable: bool = True,
) -> StepResult:
    """Record a stage satisfied from stored artifacts during a resume."""
    result = StepResult(
        name=name, ok=True, ms=0, attempts=0, value=value,
        resumable=resumable, skipped=True,
    )
    payload: dict[str, Any] = dict(result.meta())
    payload["skipped"] = True
    if reason:
        payload["reason"] = reason
    rid = current_run_id()
    if rid:
        payload["run_id"] = rid
    emit("harness_step", **payload)
    _persist(result)
    return result


def require_step(result: StepResult) -> Any:
    """Return a successful step's value, else re-raise the original error.

    Raising the captured exception keeps ValueError-style friendly errors
    intact through the envelope.
    """
    if not result.ok:
        if result.exc is not None:
            raise result.exc
        raise RuntimeError(f"step {result.name} failed: {result.error}")
    return result.value


def step_required(name: str, fn: Callable[[], T]) -> T:
    """Like step(), but re-raises after recording (for mandatory nodes)."""
    return require_step(step(name, fn))
