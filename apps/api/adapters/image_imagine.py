"""Grok Imagine. Neutrogena is text-to-image. Chile Limón is image-edit from the pack.

Logo on the real pack may stay in the edit. Pillow stamps the Neutrogena wordmark
and disclaimer after generate; Lays skips that stamp.
"""

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
IMAGINE_EDIT_URL = "https://api.x.ai/v1/images/edits"
DEFAULT_MODEL = "grok-imagine-image"
DEFAULT_EDIT_MODEL = "grok-imagine-image-2.0"
TIMEOUT_S = 180.0
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class ImagineImageGen:
    def __init__(
        self,
        client: httpx.Client | None = None,
        *,
        key: str | None = None,
        model: str | None = None,
        edit_model: str | None = None,
    ) -> None:
        self.client = client
        self.key = key if key is not None else os.environ.get("XAI_API_KEY", "")
        self.model = (model or os.environ.get("IMAGE_GEN_MODEL") or DEFAULT_MODEL).strip()
        self.edit_model = (
            edit_model or os.environ.get("IMAGE_EDIT_MODEL") or DEFAULT_EDIT_MODEL
        ).strip()

    def generate(
        self,
        prompt: str,
        out_path: Path,
        *,
        source_image: Path | None = None,
    ) -> Path:
        from boxes.image_budget import record_spend, spend_gate

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
        pack = Path(source_image) if source_image is not None else None
        if pack is not None and pack.is_file():
            url = IMAGINE_EDIT_URL
            payload = {
                "model": self.edit_model,
                "prompt": prompt,
                "n": 1,
                "aspect_ratio": "4:5",
                "response_format": "url",
                "image": {"url": _image_data_url(pack), "type": "image_url"},
            }
        else:
            url = IMAGINE_URL
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
                response = client.post(url, json=payload, headers=headers)
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


def _image_data_url(path: Path) -> str:
    raw = Path(path).read_bytes()
    if raw.startswith(PNG_MAGIC):
        mime = "image/png"
    elif raw[:2] == b"\xff\xd8":
        mime = "image/jpeg"
    elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        mime = "image/webp"
    else:
        from io import BytesIO

        from PIL import Image

        buf = BytesIO()
        Image.open(path).convert("RGB").save(buf, format="JPEG", quality=90)
        raw = buf.getvalue()
        mime = "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


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
