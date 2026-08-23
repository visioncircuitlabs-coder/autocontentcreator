"""Image budget gate — Grok Imagine is IMAGES ONLY with a hard USD cap.

Every Imagine call goes through spend_gate() before the HTTP request and
record_spend() after. Past the cap, calls fail friendly (stub fallback keeps
the walk alive). Spend lives in data/spend.jsonl so it survives restarts.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# grok-imagine-image list price per image, USD. Conservative flat rate.
COST_PER_IMAGE_USD = 0.02

DEFAULT_BUDGET_USD = 2.00


def _spend_path() -> Path:
    base = os.environ.get("SQLITE_PATH", "data/demo.db")
    return Path(base).parent / "spend.jsonl"


def budget_usd() -> float:
    raw = os.environ.get("IMAGE_BUDGET_USD", "").strip()
    try:
        return float(raw) if raw else DEFAULT_BUDGET_USD
    except ValueError:
        return DEFAULT_BUDGET_USD


def spent_usd() -> float:
    path = _spend_path()
    if not path.is_file():
        return 0.0
    total = 0.0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            total += float(json.loads(line).get("usd", 0.0))
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    return round(total, 4)


class BudgetExceeded(RuntimeError):
    pass


def spend_gate(estimate_usd: float | None = None) -> dict:
    """Raise BudgetExceeded past cap; return status dict otherwise."""
    cost = COST_PER_IMAGE_USD if estimate_usd is None else estimate_usd
    used = spent_usd()
    cap = budget_usd()
    if used + cost > cap + 1e-9:
        raise BudgetExceeded(
            f"Image budget exhausted: ${used:.2f} of ${cap:.2f} spent. "
            "Stub cards will be used instead."
        )
    return {"spent": used, "cap": cap, "this_call": cost}


def record_spend(usd: float, adapter: str = "grok-imagine") -> None:
    path = _spend_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "usd": round(float(usd), 4),
        "adapter": adapter,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
