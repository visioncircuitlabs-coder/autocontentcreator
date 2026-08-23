"""Chat cost accounting — per-run token/$ wallet.

complete_json responses carry usage; the adapter reports each call here so
runs have a $ figure and a hard per-run cap. Plain module, thread-safe.
"""

from __future__ import annotations

import threading

# Conservative blended price for scoring/judging work, USD per 1M tokens.
# Text models on gateways vary; this is an upper-bound estimate for budgeting.
USD_PER_1M_INPUT = 3.0
USD_PER_1M_OUTPUT = 15.0
DEFAULT_RUN_BUDGET_USD = 0.50

_lock = threading.Lock()
_usage: dict[str, dict[str, float]] = {}


def _blank() -> dict[str, float]:
    return {"calls": 0.0, "in": 0.0, "out": 0.0, "usd": 0.0}


def record(model: str, usage: object | None) -> float:
    """Record one completion's usage; returns estimated USD."""
    if usage is None:
        return 0.0
    tin = float(getattr(usage, "input_tokens", 0) or getattr(usage, "prompt_tokens", 0) or 0)
    tout = float(getattr(usage, "output_tokens", 0) or getattr(usage, "completion_tokens", 0) or 0)
    usd = (tin / 1e6) * USD_PER_1M_INPUT + (tout / 1e6) * USD_PER_1M_OUTPUT
    with _lock:
        bucket = _usage.setdefault(model, _blank())
        bucket["calls"] += 1
        bucket["in"] += tin
        bucket["out"] += tout
        bucket["usd"] += usd
    return usd


def total_usd() -> float:
    with _lock:
        return round(sum(b["usd"] for b in _usage.values()), 6)


def summary() -> dict:
    with _lock:
        snap = {m: dict(b) for m, b in _usage.items()}
    out = {}
    total_calls = total_in = total_out = 0.0
    for m, b in snap.items():
        out[m] = {
            "calls": int(b["calls"]),
            "tokens_in": int(b["in"]),
            "tokens_out": int(b["out"]),
            "usd": round(b["usd"], 6),
        }
        total_calls += b["calls"]
        total_in += b["in"]
        total_out += b["out"]
    return {
        "models": out,
        "totals": {
            "calls": int(total_calls),
            "tokens_in": int(total_in),
            "tokens_out": int(total_out),
            "usd": round(sum(b["usd"] for b in snap.values()), 6),
        },
    }


def reset() -> None:
    with _lock:
        _usage.clear()
