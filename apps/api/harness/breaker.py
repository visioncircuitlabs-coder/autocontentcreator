"""Circuit breaker for outbound model calls.

Closed → calls flow normally. After `threshold` consecutive failures the
breaker OPENS for `cooldown_s`: callers get FastFail immediately instead of
waiting through retries. After cooldown it HALF-OPENS: one trial call passes;
success closes it, failure reopens (with backoff doubling up to a cap).

Plain code, thread-safe, injectable clock/sleep for deterministic tests.
"""

from __future__ import annotations

import threading
import time


class BreakerOpen(RuntimeError):
    """Raised on call attempts while the breaker is open."""

    def __init__(self, retry_after_s: float) -> None:
        super().__init__(
            f"model breaker open — failing fast, retry in {retry_after_s:.0f}s"
        )
        self.retry_after_s = retry_after_s


class CircuitBreaker:
    def __init__(
        self,
        *,
        threshold: int = 3,
        cooldown_s: float = 60.0,
        max_cooldown_s: float = 600.0,
        clock: callable = time.monotonic,  # type: ignore[assignment]
        sleep: callable = time.sleep,  # type: ignore[assignment]
    ) -> None:
        self.threshold = threshold
        self.cooldown_s = cooldown_s
        self.max_cooldown_s = max_cooldown_s
        self._clock = clock
        self._sleep = sleep
        self._lock = threading.Lock()
        self._state = "closed"
        self._failures = 0
        self._opened_at = 0.0
        self._current_cooldown = cooldown_s

    @property
    def state(self) -> str:
        with self._lock:
            if self._state == "open" and (
                self._clock() - self._opened_at >= self._current_cooldown
            ):
                return "half_open"
            return self._state

    def before_call(self) -> None:
        """Raise BreakerOpen if a call may not proceed right now."""
        with self._lock:
            if self._state == "closed":
                return
            elapsed = self._clock() - self._opened_at
            if self._state == "half_open":
                return  # one trial call allowed
            if elapsed >= self._current_cooldown:
                self._state = "half_open"
                return
            raise BreakerOpen(self._current_cooldown - elapsed)

    def record_success(self) -> None:
        with self._lock:
            self._state = "closed"
            self._failures = 0
            self._current_cooldown = self.cooldown_s

    def record_failure(self) -> None:
        with self._lock:
            if self._state == "half_open":
                # trial failed — reopen with doubled cooldown
                self._current_cooldown = min(
                    self._current_cooldown * 2, self.max_cooldown_s
                )
                self._state = "open"
                self._opened_at = self._clock()
                return
            self._failures += 1
            if self._failures >= self.threshold:
                self._state = "open"
                self._opened_at = self._clock()

    def call(self, fn, *args, **kwargs):
        """Guarded call: before_call → fn → record outcome."""
        self.before_call()
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self.record_failure()
            raise
        self.record_success()
        return result

    def reset(self) -> None:
        with self._lock:
            self._state = "closed"
            self._failures = 0
            self._current_cooldown = self.cooldown_s


# Shared process-wide breaker for the chat model path. All LLM steps
# (scorer, strategist, copywriter, judge, craft) route through this so a
# dead upstream fails fast everywhere instead of per-step retry pain.
CHAT_BREAKER = CircuitBreaker(threshold=3, cooldown_s=60.0)
