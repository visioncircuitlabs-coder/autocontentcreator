"""Optional HTTP ImageGen. POST {prompt, size}. Never send the logo."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import httpx

from adapters.common import REQUEST_TIMEOUT, request_headers
from adapters.resilience import retry_call

logger = logging.getLogger(__name__)

DEFAULT_SIZE = "1080x1350"


class HttpImageGen:
    """Save response bytes from IMAGE_GEN_URL. Overlay happens after, in compose."""

    def __init__(
        self,
        client: httpx.Client | None = None,
        *,
        url: str | None = None,
        key: str | None = None,
        size: str = DEFAULT_SIZE,
    ) -> None:
        self.client = client
        self.url = url if url is not None else os.environ.get("IMAGE_GEN_URL", "")
        self.key = key if key is not None else os.environ.get("IMAGE_GEN_KEY", "")
        self.size = size or DEFAULT_SIZE

    def generate(self, prompt: str, out_path: Path) -> Path:
        url = (self.url or "").strip()
        if not url:
            raise RuntimeError(
                "IMAGE_GEN_URL is empty. Leave IMAGE_GEN_MODE=stub or paste an image API."
            )

        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        headers = {**request_headers(accept="image/*,application/octet-stream"), "Authorization": f"Bearer {self.key}"}
        payload = {"prompt": prompt, "size": self.size}

        owns = self.client is None
        client = self.client or httpx.Client(
            timeout=REQUEST_TIMEOUT, headers=request_headers()
        )
        try:

            def _attempt():
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response

            response = retry_call(_attempt)
        except httpx.HTTPStatusError as exc:
            logger.warning("image HTTP failed: %s", exc)
            raise RuntimeError(
                "The image service did not return a picture. Stay on stub mode or check the API."
            ) from exc
        finally:
            if owns:
                client.close()

        if not response.content:
            raise RuntimeError("The image service returned an empty picture.")

        dest.write_bytes(response.content)
        return dest
