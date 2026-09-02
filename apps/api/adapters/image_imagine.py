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
DEFAULT_MODEL = "grok-imagine-image-2.0"
LEGACY_MODELS = frozenset({"grok-imagine-image"})
ASPECT_RATIO = "3:4"  # xAI does not accept 4:5; art_director crop-covers to 1080×1350
RESOLUTION = "2k"
QUALITY = "medium"
TIMEOUT_S = 90.0
ERROR_BODY_LIMIT = 2000


def resolve_imagine_model(raw: str | None) -> str:
    """Pin Imagine to 2.0. Stale IMAGE_GEN_MODEL=grok-imagine-image still works."""
    token = (raw or "").strip()
    if not token or token in LEGACY_MODELS:
        return DEFAULT_MODEL
    return token


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
        env_model = os.environ.get("IMAGE_GEN_MODEL") if model is None else model
        self.model = resolve_imagine_model(env_model)

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
            "aspect_ratio": ASPECT_RATIO,
            "resolution": RESOLUTION,
            "quality": QUALITY,
            "response_format": "url",
        }
        owns = self.client is None
        client = self.client or httpx.Client(timeout=TIMEOUT_S, follow_redirects=True)
        try:

            def _attempt():
                response = client.post(IMAGINE_URL, json=payload, headers=headers)
                if response.status_code >= 400:
                    logger.warning(
                        "Imagine HTTP %s body=%s",
                        response.status_code,
                        (response.text or "")[:ERROR_BODY_LIMIT],
                    )
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
            extra = ""
            try:
                extra = (exc.response.text or "")[:ERROR_BODY_LIMIT]
            except Exception:
                extra = ""
            logger.warning("Imagine HTTP failed: %s body=%s", exc, extra)
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
