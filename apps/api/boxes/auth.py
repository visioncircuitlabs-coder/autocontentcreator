"""Auth & roles — API keys with viewer / approver / admin roles.

Enterprise lock: only a named, authenticated approver can record a decision.
Keys live in the api_keys table. Bootstrap admin key comes from env
ADMIN_API_KEY at first start; if unset, local development stays open and a
warning is emitted once.
"""

from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timezone

from db import get_conn, init_db

ROLES = ("viewer", "approver", "admin")

# Endpoints by minimum role. Anything not listed is viewer (read) or open.
WRITE_ROLES: dict[str, str] = {
    "/radar/run": "viewer",
    "/radar/fetch": "viewer",
    "/factory/run": "viewer",
    "/factory/image": "approver",
    "/factory/video": "approver",
    "/review": "approver",
    "/memory/rebuild": "admin",
    "/events": "viewer",
}

_admin_warned = False


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def ensure_bootstrap() -> None:
    """Create the admin key from env once, on first start."""
    global _admin_warned
    init_db()
    conn = get_conn()
    raw = os.environ.get("ADMIN_API_KEY", "").strip()
    if not raw:
        if not _admin_warned:
            row = conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()
            if row and row[0] == 0:
                print("auth: no ADMIN_API_KEY set and no keys exist — API runs open")
            _admin_warned = True
        return
    if not conn.execute(
        "SELECT 1 FROM api_keys WHERE key_hash = ?", (_hash(raw),)
    ).fetchone():
        conn.execute(
            "INSERT INTO api_keys (key_hash, name, role, created_at) VALUES (?,?,?,?)",
            (
                _hash(raw),
                "bootstrap-admin",
                "admin",
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()


def create_key(name: str, role: str) -> str:
    """Admin action: mint a new key. Returns the raw key ONCE."""
    if role not in ROLES:
        raise ValueError(f"Role must be one of {', '.join(ROLES)}.")
    if not name.strip():
        raise ValueError("A key name is required.")
    raw = "cm_" + secrets.token_urlsafe(24)
    conn = get_conn()
    conn.execute(
        "INSERT INTO api_keys (key_hash, name, role, created_at) VALUES (?,?,?,?)",
        (_hash(raw), name.strip(), role, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    return raw


def authenticate(header_value: str | None) -> dict | None:
    """Return {name, role} for a valid key, None if missing/unknown."""
    if not header_value or not header_value.strip():
        return None
    conn = get_conn()
    row = conn.execute(
        "SELECT name, role FROM api_keys WHERE key_hash = ?", (_hash(header_value.strip()),)
    ).fetchone()
    if not row:
        return None
    return {"name": row[0], "role": row[1]}


def authorize(path: str, identity: dict | None) -> tuple[bool, str]:
    """(allowed, reason). Open mode when no keys exist at all."""
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0]
    if count == 0:
        return True, "open"
    if identity is None:
        return False, "An API key is required. Ask your admin for one."
    need = "viewer"
    for prefix, role in WRITE_ROLES.items():
        if path.startswith(prefix):
            need = role
            break
    rank = {r: i for i, r in enumerate(ROLES)}
    if rank[identity["role"]] >= rank[need]:
        return True, identity["role"]
    return False, f"Your role ({identity['role']}) cannot do this. Needs {need}."
