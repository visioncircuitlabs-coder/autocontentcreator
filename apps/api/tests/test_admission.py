"""Admission control tests: capacity, priority, shedding, telemetry."""

from __future__ import annotations

import threading
import time

import pytest

from harness import admission


@pytest.fixture(autouse=True)
def reset_state():
    admission._lock.acquire()
    admission._active = 0
    admission._shed_count = 0
    admission._lock.release()
    yield


def test_slot_admits_and_releases():
    with admission.run_slot("interactive"):
        assert admission.stats()["active_runs"] == 1
    assert admission.stats()["active_runs"] == 0


def test_capacity_cap_enforced():
    with admission.run_slot("interactive"):
        with admission.run_slot("interactive"):
            assert admission.stats()["active_runs"] == 2
            with pytest.raises(admission.Overloaded):
                admission.run_slot("batch").__enter__()


def test_batch_sheds_immediately_interactive_waits():
    started = time.monotonic()

    def hold():
        with admission.run_slot("interactive"):
            time.sleep(0.4)

    t = threading.Thread(target=hold)
    t.start()
    time.sleep(0.05)  # let holder take the only slot (cap=2, so take both)

    def hold2():
        with admission.run_slot("interactive"):
            time.sleep(0.3)

    t2 = threading.Thread(target=hold2)
    t2.start()
    time.sleep(0.05)

    # batch at full capacity → instant shed
    with pytest.raises(admission.Overloaded):
        admission.run_slot("batch").__enter__()
    assert time.monotonic() - started < 0.25
    # interactive waits for a slot and gets in
    with admission.run_slot("interactive"):
        pass
    t.join()
    t2.join()


def test_shed_counter_telemetry():
    before = admission.stats()["shed_total"]
    with admission.run_slot("interactive"):
        pass
    # saturate both slots directly
    assert admission._admit("batch", 0.0)
    assert admission._admit("batch", 0.0)
    # now full: batch shed must increment the counter
    assert not admission._admit("batch", 0.0)
    assert admission.stats()["shed_total"] >= before + 1
    # interactive also sheds once its grace expires
    assert not admission._admit("interactive", 0.01)
    # release
    with admission._lock:
        admission._active -= 2


def test_overload_carries_retry_after():
    err = admission.Overloaded()
    assert err.retry_after_s > 0
