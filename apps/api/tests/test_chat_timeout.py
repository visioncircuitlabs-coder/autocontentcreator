"""Chat timeout default is 180s; one slow Grok call must not trip the breaker."""

from __future__ import annotations

import pytest
from pydantic import BaseModel


class _Tiny(BaseModel):
    x: int


def _fake_response(payload: str = '{"x": 1}'):
    class Msg:
        content = payload

    class Choice:
        message = Msg()

    class Resp:
        choices = [Choice()]
        usage = None

    return Resp()


def test_chat_timeout_default_is_180s(monkeypatch: pytest.MonkeyPatch) -> None:
    from adapters.chat_litellm import DEFAULT_CHAT_TIMEOUT_S, chat_timeout_s

    monkeypatch.delenv("CHAT_TIMEOUT_S", raising=False)
    assert DEFAULT_CHAT_TIMEOUT_S == 180
    assert chat_timeout_s() == 180.0


def test_chat_timeout_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    from adapters.chat_litellm import chat_timeout_s

    monkeypatch.setenv("CHAT_TIMEOUT_S", "45")
    assert chat_timeout_s() == 45.0


def test_complete_json_passes_180s_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    import litellm

    from adapters.chat_litellm import LiteLLMChat
    from harness.breaker import CHAT_BREAKER

    monkeypatch.delenv("CHAT_TIMEOUT_S", raising=False)
    captured: dict = {}

    def fake_completion(**kwargs):
        captured.update(kwargs)
        return _fake_response()

    monkeypatch.setattr(litellm, "completion", fake_completion)
    CHAT_BREAKER.reset()
    try:
        out = LiteLLMChat(model="xai/grok-4.6").complete_json("sys", "user", _Tiny)
    finally:
        CHAT_BREAKER.reset()
    assert out.x == 1
    assert captured["timeout"] == 180.0


def test_one_timeout_does_not_open_chat_breaker(monkeypatch: pytest.MonkeyPatch) -> None:
    import litellm

    from adapters.chat_litellm import LiteLLMChat
    from harness.breaker import CHAT_BREAKER

    def boom(**kwargs):
        raise TimeoutError("slow grok")

    monkeypatch.setattr(litellm, "completion", boom)
    CHAT_BREAKER.reset()
    chat = LiteLLMChat(model="xai/grok-4.6")
    try:
        with pytest.raises(TimeoutError):
            chat.complete_json("sys", "user", _Tiny)
        assert CHAT_BREAKER.state == "closed"
        with pytest.raises(TimeoutError):
            chat.complete_json("sys", "user", _Tiny)
        assert CHAT_BREAKER.state == "closed"
        with pytest.raises(TimeoutError):
            chat.complete_json("sys", "user", _Tiny)
        assert CHAT_BREAKER.state == "open"
    finally:
        CHAT_BREAKER.reset()
