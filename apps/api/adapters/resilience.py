"""Bounded retry-with-backoff for outbound adapters. Transient errors only."""

from __future__ import annotations

import logging
import random
import time
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAX_RETRIES = 2
BASE_DELAY_S = 1.0

# litellm error names (import avoided so the adapter stays optional)
_TRANSIENT_NAMES = {
    "APITimeoutError",
    "APIConnectionError",
    "InternalServerError",
    "ServiceUnavailableError",
    "ReadTimeout",
    "ConnectTimeout",
}


def is_transient(exc: Exception) -> bool:
    """True only for timeouts, connection failures, and 5xx. Never 4xx."""
    if isinstance(exc, (TimeoutError, ConnectionError, OSError)):
        return True
    try:
        import httpx
    except ImportError:  # pragma: no cover - httpx is a hard dep of the API
        httpx = None  # type: ignore[assignment]
    if httpx is not None:
        if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            return 500 <= exc.response.status_code < 600
    name = type(exc).__name__
    if name in _TRANSIENT_NAMES:
        return True
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return 500 <= status < 600
    return False


def retry_call(
    fn: Callable[[], T],
    *,
    retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY_S,
    sleep: Callable[[float], None] = time.sleep,
    jitter: bool = True,
) -> T:
    """Run fn; retry transient errors up to `retries` times with backoff.

    Backoff starts at base_delay and doubles per attempt, plus small jitter.
    Any non-transient error (4xx, bad payload, ...) is raised immediately.
    """
    attempt = 0
    while True:
        try:
            return fn()
        except Exception as exc:
            if attempt >= retries or not is_transient(exc):
                raise
            delay = base_delay * (2**attempt)
            if jitter:
                delay += random.uniform(0, base_delay)
            logger.warning(
                "transient error (%s): retry %s/%s in %.2fs",
                type(exc).__name__,
                attempt + 1,
                retries,
                delay,
            )
            attempt += 1
            sleep(delay)
