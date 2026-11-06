"""Optional chat. No key → callers pass ChatModel=None and use templates."""

from __future__ import annotations

import json
import logging
import os

from pydantic import BaseModel

from adapters.resilience import is_timeout, is_transient, retry_call
from harness.breaker import CHAT_BREAKER

logger = logging.getLogger(__name__)

DEFAULT_CHAT_TIMEOUT_S = 180.0


def chat_timeout_s() -> float:
    """Seconds for one LiteLLM completion. Override with CHAT_TIMEOUT_S."""
    raw = (os.environ.get("CHAT_TIMEOUT_S") or "").strip()
    try:
        value = float(raw) if raw else DEFAULT_CHAT_TIMEOUT_S
    except ValueError:
        value = DEFAULT_CHAT_TIMEOUT_S
    return max(1.0, value)


def _retry_chat(exc: Exception) -> bool:
    if is_timeout(exc):
        return False
    return is_transient(exc)


def build_chat() -> "LiteLLMChat | None":
    xai = os.environ.get("XAI_API_KEY", "").strip()
    gemini = os.environ.get("GEMINI_API_KEY", "").strip()
    groq = os.environ.get("GROQ_API_KEY", "").strip()
    if not xai and not gemini and not groq:
        return None
    model = os.environ.get("CHAT_MODEL", "").strip()
    if not model:
        if xai:
            model = "xai/grok-4.6"
        elif groq and not gemini:
            model = "groq/llama-3.3-70b-versatile"
        else:
            model = "gemini/gemini-2.0-flash"
    return LiteLLMChat(model=model)


class LiteLLMChat:
    def __init__(self, model: str = "xai/grok-4.6") -> None:
        self.model = model

    def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
        import litellm

        schema_hint = json.dumps(schema.model_json_schema())
        timeout = chat_timeout_s()

        def _call():
            return litellm.completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"{system}\nReturn JSON only. Schema: {schema_hint}",
                    },
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                timeout=timeout,
            )

        # One completion = one breaker trial. Timeouts are not retried here
        # (copywriter retries once at 180s). 5xx still retries inside this call.
        response = CHAT_BREAKER.call(lambda: retry_call(_call, retry_if=_retry_chat))
        from harness import chat_wallet

        chat_wallet.record(self.model, getattr(response, "usage", None))
        text = response.choices[0].message.content or "{}"
        return schema.model_validate_json(text)
