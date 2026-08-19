"""Optional LiteLLM chat adapter. Scorer works with ChatModel=None (keyword fallback)."""

from __future__ import annotations

import os

from pydantic import BaseModel


class LiteLLMChat:
    """Thin stub. Requires GEMINI_API_KEY (or LITELLM_API_KEY) at call time."""

    def __init__(self, model: str = "gemini/gemini-2.0-flash") -> None:
        self.model = model

    def complete_json(self, system: str, user: str, schema: type) -> BaseModel:
        if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("LITELLM_API_KEY")):
            raise RuntimeError(
                "No chat API key set; use ChatModel=None for keyword fallback"
            )
        raise NotImplementedError(
            "LiteLLM wiring is deferred; Scorer keyword fallback covers demos without a key"
        )
