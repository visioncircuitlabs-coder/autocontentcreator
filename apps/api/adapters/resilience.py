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


def is_timeout(exc: Exception) -> bool:
    """Slow upstream. Callers may count these as one failure; do not retry them at a 10-minute budget."""
    if isinstance(exc, TimeoutError):
        return True
    try:
        import httpx

        if isinstance(exc, httpx.TimeoutException):
            return True
    except ImportError:
        pass
    return "timeout" in type(exc).__name__.lower()


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
    retry_if: Callable[[Exception], bool] | None = None,
) -> T:
    """Run fn; retry matching errors up to `retries` times with backoff.

    Backoff starts at base_delay and doubles per attempt, plus small jitter.
    `retry_if` defaults to `is_transient`. Non-matching errors raise immediately.
    """
    should = retry_if if retry_if is not None else is_transient
    attempt = 0
    while True:
        try:
            return fn()
        except Exception as exc:
            if attempt >= retries or not should(exc):
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
