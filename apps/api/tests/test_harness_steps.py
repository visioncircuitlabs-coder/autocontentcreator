"""Harness step envelope tests."""

from __future__ import annotations

import pytest

from harness import steps
from harness.steps import step, step_required


def test_step_ok_records_value_and_timing():
    res = step("add", lambda: 1 + 1)
    assert res.ok
    assert res.value == 2
    assert res.attempts == 1
    assert res.ms >= 0
    assert res.error is None


def test_step_failure_never_raises():
    def boom():
        raise ValueError("bad input")

    res = step("boom", boom)
    assert not res.ok
    assert "ValueError" in (res.error or "")
    assert res.value is None


def test_step_emits_event_with_run_id():
    rid = steps.new_run_id()
    seen: dict = {}

    import harness.steps as hsteps

    seen: dict = {}

    def spy(kind, **payload):
        seen.update(payload)
        return "evt"

    orig = hsteps.emit
    hsteps.emit = spy
    try:
        step("tracked", lambda: None)
    finally:
        hsteps.emit = orig
    assert seen["step"] == "tracked"
    assert seen["run_id"] == rid


def test_step_required_reraises():
    def boom():
        raise RuntimeError("mandatory node down")

    with pytest.raises(RuntimeError, match="mandatory"):
        step_required("core", boom)


def test_set_run_id_roundtrip():
    steps.set_run_id("run_abc")
    assert steps.current_run_id() == "run_abc"
    steps.set_run_id(None)
    assert steps.current_run_id() is None
