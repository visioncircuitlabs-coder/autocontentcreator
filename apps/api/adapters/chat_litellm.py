"""Optional chat. No key → callers pass ChatModel=None and use templates."""

from __future__ import annotations

import json
import logging
import os

from pydantic import BaseModel

from adapters.resilience import retry_call

logger = logging.getLogger(__name__)


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
                timeout=20,
            )

        response = retry_call(_call)
        text = response.choices[0].message.content or "{}"
        return schema.model_validate_json(text)
