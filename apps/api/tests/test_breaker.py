"""Circuit breaker tests — deterministic via injected clock/sleep."""

from __future__ import annotations

import pytest

from harness.breaker import BreakerOpen, CircuitBreaker


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def test_closed_allows_calls():
    br = CircuitBreaker(threshold=2, cooldown_s=10)
    assert br.call(lambda: 42) == 42
    assert br.state == "closed"


def test_opens_after_threshold_consecutive_failures():
    br = CircuitBreaker(threshold=2, cooldown_s=10)

    def boom():
        raise ValueError("upstream down")

    for _ in range(2):
        with pytest.raises(ValueError):
            br.call(boom)
    assert br.state == "open"
    with pytest.raises(BreakerOpen):
        br.before_call()


def test_open_fails_fast_without_calling_fn():
    br = CircuitBreaker(threshold=1, cooldown_s=10)
    calls = {"n": 0}

    def boom():
        calls["n"] += 1
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        br.call(boom)
    # while open, fn must NOT be invoked
    with pytest.raises(BreakerOpen):
        br.call(boom)
    assert calls["n"] == 1


def test_half_open_after_cooldown_then_success_closes():
    clock = FakeClock()
    br = CircuitBreaker(threshold=1, cooldown_s=60, clock=clock)

    def boom():
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        br.call(boom)
    clock.t = 61
    assert br.state == "half_open"
    assert br.call(lambda: "ok") == "ok"
    assert br.state == "closed"


def test_half_open_failure_reopens_with_doubled_cooldown():
    clock = FakeClock()
    br = CircuitBreaker(threshold=1, cooldown_s=60, max_cooldown_s=600, clock=clock)

    def boom():
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        br.call(boom)
    clock.t = 61
    with pytest.raises(RuntimeError):
        br.call(boom)  # half-open trial fails → reopen
    assert br.state == "open"
    # doubled: not yet half-open at 61+59=120? cooldown now 120 from t=61 → 181
    clock.t = 150
    assert br.state == "open"
    clock.t = 200
    assert br.state == "half_open"


def test_success_resets_failure_count():
    br = CircuitBreaker(threshold=3, cooldown_s=10)

    def boom():
        raise ValueError()

    for _ in range(2):
        with pytest.raises(ValueError):
            br.call(boom)
    assert br.call(lambda: 1) == 1  # resets
    for _ in range(2):
        with pytest.raises(ValueError):
            br.call(boom)
    assert br.state == "closed"  # only 2 consecutive since reset


def test_reset_clears_everything():
    br = CircuitBreaker(threshold=1, cooldown_s=10)

    def boom():
        raise ValueError()

    with pytest.raises(ValueError):
        br.call(boom)
    br.reset()
    assert br.state == "closed"
