"""Step envelope — every pipeline node reports attempts, duration, status.

A "step" wraps any callable with: uniform timing, structured events (via
obs.emit), attempt counting, and an optional run_id so radar → factory →
paint events can be correlated in the log and audit trail.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

from obs import emit

T = TypeVar("T")

# Module-level current pipeline run id (set by API handlers; best-effort).
_run_id: str | None = None


def set_run_id(run_id: str | None) -> None:
    global _run_id
    _run_id = run_id


def current_run_id() -> str | None:
    return _run_id


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


def step(name: str, fn: Callable[[], T], *, emit_events: bool = True) -> StepResult:
    """Run one pipeline step with uniform envelope. Never raises."""
    t0 = time.monotonic()
    result = StepResult(name=name, ok=False, ms=0)
    try:
        result.value = fn()
        result.ok = True
    except Exception as exc:  # noqa: BLE001 — envelope records everything
        result.error = f"{type(exc).__name__}: {exc}"
    finally:
        result.ms = int((time.monotonic() - t0) * 1000)
        if emit_events:
            payload: dict[str, Any] = dict(result.meta())
            rid = current_run_id()
            if rid:
                payload["run_id"] = rid
            emit("harness_step", **payload)
    return result


def step_required(name: str, fn: Callable[[], T]) -> T:
    """Like step(), but re-raises after recording (for mandatory nodes)."""
    res = step(name, fn)
    if not res.ok:
        raise RuntimeError(f"step {name} failed: {res.error}")
    return res.value
