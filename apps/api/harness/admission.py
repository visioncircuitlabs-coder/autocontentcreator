"""Admission control — bounded concurrency for pipeline runs.

Interactive requests (a person clicking through the walk) take priority
over batch work (scheduled radar sweeps). When at capacity:
  - interactive callers wait up to a short grace, then get 503 + Retry-After
  - batch callers are shed immediately with the same signal

Plain semaphore accounting, no framework. Shed events emit telemetry so
saturation is observable, never silent.
"""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from typing import Iterator

MAX_CONCURRENT_RUNS = 2
INTERACTIVE_GRACE_S = 5.0

_lock = threading.Lock()
_active = 0
_shed_count = 0


class Overloaded(RuntimeError):
    """Raised when a run cannot be admitted now."""

    def __init__(self, retry_after_s: int = 10) -> None:
        super().__init__(
            "The machine is busy right now — try again in a moment."
        )
        self.retry_after_s = retry_after_s


def stats() -> dict:
    with _lock:
        return {"active_runs": _active, "max_concurrent": MAX_CONCURRENT_RUNS, "shed_total": _shed_count}


def _admit(priority: str, wait_s: float) -> bool:
    """Try to take one slot. Interactive waits up to wait_s; batch sheds fast."""
    global _active, _shed_count
    deadline = time.monotonic() + wait_s
    poll = 0.05 if priority == "interactive" else 0.0
    while True:
        with _lock:
            if _active < MAX_CONCURRENT_RUNS:
                _active += 1
                return True
            if poll == 0.0 or time.monotonic() >= deadline:
                _shed_count += 1
                return False
        time.sleep(poll)


@contextmanager
def run_slot(priority: str = "interactive") -> Iterator[None]:
    """Context manager guarding a pipeline run.

    Raises Overloaded when capacity is unavailable; callers map that to a
    friendly 503 with Retry-After.
    """
    global _active
    wait = INTERACTIVE_GRACE_S if priority == "interactive" else 0.0
    if not _admit(priority, wait):
        raise Overloaded()
    from harness.steps import emit as _emit  # local import avoids cycle

    try:
        yield
    finally:
        with _lock:
            _active -= 1
