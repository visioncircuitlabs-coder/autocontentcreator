#!/usr/bin/env python3
"""Optional smoke walk against a running API. Skips cleanly if the API is down.

Usage (API already up on :8000):
  python scripts/demo_walk.py

Does not require Docker, Gemini, or IMAGE_GEN. Uses the unofficial Neutrogena
fixture so the belt still walks with empty GEMINI_API_KEY.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any

BASE = "http://127.0.0.1:8000"
TIMEOUT = 60


def _req(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    *,
    expect_json: bool = True,
) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as res:
        raw = res.read()
        if not expect_json:
            return raw
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))


def main() -> int:
    try:
        health = _req("GET", "/health")
    except Exception as exc:  # noqa: BLE001 — smoke skip
        print(f"SKIP: API not reachable at {BASE} ({exc})")
        return 0

    if not isinstance(health, dict) or not health.get("ok"):
        print(f"SKIP: unexpected /health payload: {health!r}")
        return 0

    print("ok: /health")

    # Prove Fetch exists; live sources may flake — fixture carries the belt.
    try:
        signals = _req("POST", "/radar/fetch")
        count = len(signals) if isinstance(signals, list) else 0
        print(f"ok: /radar/fetch -> {count} signal(s)")
    except urllib.error.HTTPError as exc:
        print(f"warn: /radar/fetch HTTP {exc.code} (continuing via fixture)")
    except Exception as exc:  # noqa: BLE001
        print(f"warn: /radar/fetch failed ({exc}); continuing via fixture")

    fixture = _req("POST", "/radar/fixture")
    report = fixture.get("report") if isinstance(fixture, dict) else None
    if not isinstance(report, dict) or not report.get("report_id"):
        print(f"FAIL: fixture dive missing report: {fixture!r}")
        return 1
    report_id = report["report_id"]
    print(f"ok: /radar/fixture -> {report_id}")

    drafts = _req("POST", "/factory/run", {"report_id": report_id})
    if not isinstance(drafts, list) or not drafts:
        print(f"FAIL: factory returned no drafts: {drafts!r}")
        return 1
    draft = drafts[0]
    draft_id = draft.get("draft_id")
    if not draft_id:
        print(f"FAIL: draft missing id: {draft!r}")
        return 1
    print(f"ok: /factory/run -> {draft_id} ({len(drafts)} draft(s))")

    try:
        png = _req("GET", f"/drafts/{draft_id}/image", expect_json=False)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: draft image ({exc})")
        return 1
    if not isinstance(png, (bytes, bytearray)) or not png.startswith(b"\x89PNG"):
        print("FAIL: draft image is not a PNG")
        return 1
    print(f"ok: /drafts/{draft_id}/image ({len(png)} bytes)")

    decision = _req(
        "POST",
        f"/review/{draft_id}",
        {
            "user": "demo_walk",
            "verdict": "approve",
            "reason": "Smoke walk: unofficial Neutrogena fixture post looks fine.",
        },
    )
    if not isinstance(decision, dict) or decision.get("verdict") != "approve":
        print(f"FAIL: review approve: {decision!r}")
        return 1
    print(f"ok: /review/{draft_id} approve")

    try:
        zipped = _req("GET", f"/export/{draft_id}", expect_json=False)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: export ({exc})")
        return 1
    if not isinstance(zipped, (bytes, bytearray)) or zipped[:2] != b"PK":
        print("FAIL: export is not a ZIP")
        return 1
    print(f"ok: /export/{draft_id} ({len(zipped)} bytes)")
    print("PASS: demo walk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
