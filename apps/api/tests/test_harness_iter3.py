"""Harness iteration-3 tests: image breaker, contextvar run-id, chat wallet."""

from __future__ import annotations

import threading

from harness import chat_wallet
from harness.breaker import IMAGE_BREAKER, BreakerOpen, CircuitBreaker
from harness.steps import current_run_id, new_run_id, set_run_id


def test_image_breaker_exists_and_opens():
    br = CircuitBreaker(threshold=1, cooldown_s=999)

    def boom():
        raise RuntimeError("imagine down")

    try:
        br.call(boom)
    except RuntimeError:
        pass
    try:
        br.call(boom)
    except BreakerOpen:
        pass
    assert br.state == "open"


def test_run_id_is_context_isolated():
    set_run_id(None)
    results = {}

    def worker(name: str):
        # each thread has its own context copy in real asyncio/threads via copy_context;
        # here we just verify set/get roundtrip per-thread isolation of the var value
        results[name] = current_run_id()

    rid = new_run_id()
    t = threading.Thread(target=worker, args=("t1",))
    t.start()
    t.join()
    # fresh threads see the default (None), not the parent's run id — no bleed
    assert results["t1"] is None
    assert current_run_id() == rid  # this context still holds its own


def test_wallet_records_usage():
    chat_wallet.reset()

    class U:
        input_tokens = 1000
        output_tokens = 500

    usd = chat_wallet.record("test-model", U())
    expected = (1000 / 1e6) * 3.0 + (500 / 1e6) * 15.0
    assert abs(usd - expected) < 1e-9
    s = chat_wallet.summary()
    assert s["totals"]["calls"] == 1
    assert s["models"]["test-model"]["tokens_in"] == 1000
    chat_wallet.reset()
    assert chat_wallet.summary()["totals"]["calls"] == 0


def test_wallet_handles_none_and_alt_fields():
    chat_wallet.reset()
    assert chat_wallet.record("m", None) == 0.0

    class Alt:
        prompt_tokens = 100
        completion_tokens = 50

    usd = chat_wallet.record("m2", Alt())
    assert usd > 0
    chat_wallet.reset()


def test_chat_breaker_shared_instance_unchanged():
    from harness.breaker import CHAT_BREAKER

    assert CHAT_BREAKER.state == "closed"
