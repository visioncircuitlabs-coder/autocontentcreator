"""Grok Imagine video. Async submit + poll. Image-to-video from the campaign still."""

from __future__ import annotations

import base64
import logging
import os
import time
from pathlib import Path

import httpx

from adapters.resilience import retry_call
from harness.breaker import VIDEO_BREAKER

logger = logging.getLogger(__name__)

IMAGINE_VIDEO_URL = "https://api.x.ai/v1/videos/generations"
DEFAULT_MODEL = "grok-imagine-video-1.5"
DURATION_S = 5
ASPECT_RATIO = "3:4"  # closest listed ratio to the 4:5 feed; overlay crops to 4:5
RESOLUTION = "720p"
SUBMIT_TIMEOUT_S = 60.0
POLL_TIMEOUT_S = 60.0
DOWNLOAD_TIMEOUT_S = 60.0
POLL_INTERVAL_S = 5.0
POLL_BUDGET_S = 900.0  # docs: several minutes; SDK long-wait example is 15 min
TICKS_PER_USD = 10_000_000_000  # xAI usage.cost_in_usd_ticks
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class ImagineVideoGen:
    def __init__(
        self,
        client: httpx.Client | None = None,
        *,
        key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.client = client
        self.key = key if key is not None else os.environ.get("XAI_API_KEY", "")
        self.model = (model or os.environ.get("VIDEO_GEN_MODEL") or DEFAULT_MODEL).strip()

    def generate(
        self,
        prompt: str,
        out_path: Path,
        *,
        source_image: Path | None = None,
    ) -> Path:
        from boxes.video_budget import (
            COST_PER_VIDEO_USD,
            record_video_spend,
            spend_gate,
        )

        key = (self.key or "").strip()
        if not key:
            raise RuntimeError("XAI_API_KEY is empty. Imagine video cannot run.")
        still = Path(source_image) if source_image is not None else None
        if still is None or not still.is_file():
            raise RuntimeError("Make the picture first. Then we can make a short video.")
        spend_gate()
        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "duration": DURATION_S,
            "aspect_ratio": ASPECT_RATIO,
            "resolution": RESOLUTION,
            "generate_audio": False,
            "image": {"url": _image_data_url(still)},
        }
        owns = self.client is None
        client = self.client or httpx.Client(timeout=SUBMIT_TIMEOUT_S, follow_redirects=True)
        try:

            def _submit():
                response = client.post(IMAGINE_VIDEO_URL, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()

            body = retry_call(lambda: VIDEO_BREAKER.call(_submit))
            request_id = _request_id(body)
            if not request_id:
                raise RuntimeError("Imagine video did not return a request id.")
            done = _poll_until_done(client, headers, request_id)
            blob = _video_bytes(client, done)
            if not blob:
                raise RuntimeError("Imagine returned no video bytes.")
            dest.write_bytes(blob)
            record_video_spend(_cost_usd(done, COST_PER_VIDEO_USD))
            return dest
        except httpx.HTTPStatusError as exc:
            logger.warning("Imagine video HTTP failed: %s", exc)
            raise RuntimeError(
                "Grok Imagine did not return a short video. Check the key and try again."
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


def _request_id(body: object) -> str:
    if not isinstance(body, dict):
        return ""
    raw = body.get("request_id") or body.get("id")
    return raw.strip() if isinstance(raw, str) else ""


def _poll_until_done(
    client: httpx.Client,
    headers: dict[str, str],
    request_id: str,
) -> dict:
    deadline = time.monotonic() + POLL_BUDGET_S
    url = f"https://api.x.ai/v1/videos/{request_id}"
    while time.monotonic() < deadline:
        response = client.get(url, headers=headers, timeout=POLL_TIMEOUT_S)
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict):
            raise RuntimeError("Imagine video status was not a JSON object.")
        status = str(body.get("status") or "").lower()
        if status == "done":
            return body
        if status in {"failed", "expired"}:
            err = body.get("error") if isinstance(body.get("error"), dict) else {}
            message = err.get("message") if isinstance(err, dict) else None
            raise RuntimeError(
                str(message)
                or "Grok Imagine could not make that short video. Try again."
            )
        time.sleep(POLL_INTERVAL_S)
    raise RuntimeError("Grok Imagine took too long to make the short video. Try again.")


def _video_bytes(client: httpx.Client, body: dict) -> bytes:
    video = body.get("video")
    if not isinstance(video, dict):
        return b""
    if video.get("respect_moderation") is False:
        raise RuntimeError("That short video did not pass moderation. Try another version.")
    url = video.get("url")
    if isinstance(url, str) and url.startswith("http"):
        got = client.get(url, timeout=DOWNLOAD_TIMEOUT_S)
        got.raise_for_status()
        return got.content or b""
    return b""


def _cost_usd(body: dict, fallback: float) -> float:
    usage = body.get("usage")
    if isinstance(usage, dict):
        ticks = usage.get("cost_in_usd_ticks")
        try:
            if ticks is not None:
                return max(0.0, float(ticks) / TICKS_PER_USD)
        except (TypeError, ValueError):
            pass
    return fallback
