"""Grok Imagine. Unlocked photo; Lays designed type may be in the prompt. Legal overlay happens after."""

from __future__ import annotations

import base64
import logging
import os
from pathlib import Path

import httpx

from adapters.resilience import retry_call
from harness.breaker import IMAGE_BREAKER

logger = logging.getLogger(__name__)

IMAGINE_URL = "https://api.x.ai/v1/images/generations"
DEFAULT_MODEL = "grok-imagine-image"
TIMEOUT_S = 90.0


class ImagineImageGen:
    def __init__(
        self,
        client: httpx.Client | None = None,
        *,
        key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.client = client
        self.key = key if key is not None else os.environ.get("XAI_API_KEY", "")
        self.model = (model or os.environ.get("IMAGE_GEN_MODEL") or DEFAULT_MODEL).strip()

    def generate(self, prompt: str, out_path: Path) -> Path:
        from boxes.image_budget import BudgetExceeded, record_spend, spend_gate

        key = (self.key or "").strip()
        if not key:
            raise RuntimeError("XAI_API_KEY is empty. Imagine cannot run.")
        spend_gate()  # hard $ cap — Grok is images-only budget
        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "aspect_ratio": "4:5",
            "response_format": "url",
        }
        owns = self.client is None
        client = self.client or httpx.Client(timeout=TIMEOUT_S, follow_redirects=True)
        try:

            def _attempt():
                response = client.post(IMAGINE_URL, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()

            body = retry_call(lambda: IMAGE_BREAKER.call(_attempt))
            blob = _image_bytes(client, body)
            if not blob:
                raise RuntimeError("Imagine returned no picture bytes.")
            dest.write_bytes(blob)
            record_spend(0.02)  # only successful images cost
            return dest
        except httpx.HTTPStatusError as exc:
            logger.warning("Imagine HTTP failed: %s", exc)
            raise RuntimeError(
                "Grok Imagine did not return a picture. Check the key and try Make a post again."
            ) from exc
        finally:
            if owns:
                client.close()


def _image_bytes(client: httpx.Client, body: object) -> bytes:
    if not isinstance(body, dict):
        return b""
    rows = body.get("data")
    if not isinstance(rows, list) or not rows:
        return b""
    first = rows[0]
    if not isinstance(first, dict):
        return b""
    raw_b64 = first.get("b64_json") or first.get("b64")
    if isinstance(raw_b64, str) and raw_b64.strip():
        return base64.b64decode(raw_b64)
    url = first.get("url")
    if isinstance(url, str) and url.startswith("http"):
        got = client.get(url)
        got.raise_for_status()
        return got.content or b""
    return b""
