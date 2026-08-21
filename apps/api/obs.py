"""Local debug log. JSON lines + SQLite. Never write API keys."""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

SECRET_KEYS = ("key", "token", "authorization", "password", "secret")
_REDACT = re.compile(r"(xai-|sk-|AIza)[A-Za-z0-9_-]{8,}", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_path() -> Path:
    raw = os.environ.get("LOG_PATH", "data/logs/machine.jsonl")
    path = Path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def scrub(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if any(token in key.lower() for token in SECRET_KEYS):
                out[key] = "[redacted]"
            else:
                out[key] = scrub(item)
        return out
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, str):
        return _REDACT.sub("[redacted]", value)
    return value


def setup_logging() -> None:
    root = logging.getLogger()
    if getattr(root, "_machine_logging", False):
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    root._machine_logging = True  # type: ignore[attr-defined]


def emit(kind: str, **payload: Any) -> str:
    """Write one event. Returns event id. Safe to call from anywhere."""
    event_id = uuid4().hex[:12]
    record = {
        "id": event_id,
        "ts": _now(),
        "kind": kind,
        "payload": scrub(payload),
    }
    line = json.dumps(record, default=str)
    try:
        with log_path().open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        logging.getLogger("obs").exception("could not write jsonl")
    try:
        from db import insert_event

        insert_event(event_id, record["ts"], kind, record["payload"])
    except Exception:
        logging.getLogger("obs").exception("could not write sqlite event")
    logging.getLogger("obs").info("%s %s", kind, line)
    return event_id


def emit_error(kind: str, exc: BaseException, **payload: Any) -> str:
    return emit(
        kind,
        error=str(exc),
        error_type=type(exc).__name__,
        trace=traceback.format_exc()[-4000:],
        **payload,
    )
