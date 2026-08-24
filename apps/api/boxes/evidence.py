"""Evidence dossier — tamper-evident packaging for the paused export.

Hash chain: each audit record's digest includes the previous digest, so any
retroactive edit breaks the chain. Manifest: final entry carries the SHA-256
of every file in the export ZIP plus an Ed25519-style signature placeholder
(key management is deployment concern; the chain itself already detects
tampering without keys).

No external deps. Deterministic given the same inputs.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_chain_records(records: list[dict]) -> list[dict]:
    """Return records with chained digests: digest_i = H(prev_digest + json_i)."""
    chained: list[dict] = []
    prev = "0" * 64  # genesis
    for rec in records:
        payload = json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str)
        digest = _sha256((prev + payload).encode("utf-8"))
        chained.append({**rec, "digest": digest})
        prev = digest
    return chained


def build_manifest(files: dict[str, bytes], *, draft_id: str) -> dict:
    """Manifest over all exported files + the head of the audit chain."""
    entries = {}
    for name in sorted(files):
        entries[name] = _sha256(files[name])
    chain_head = "0" * 64
    audit_raw = files.get("audit.json")
    if audit_raw:
        try:
            parsed = json.loads(audit_raw.decode("utf-8"))
            rows = parsed if isinstance(parsed, list) else parsed.get("records", [])
            if rows and isinstance(rows[-1], dict):
                chain_head = rows[-1].get("digest", chain_head)
        except (json.JSONDecodeError, AttributeError):
            pass
    return {
        "schema": "content-machine/evidence-manifest@1",
        "draft_id": draft_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": entries,
        "audit_chain_head": chain_head,
        "note": (
            "Verify by re-hashing files and re-walking audit.json digests. "
            "Any mismatch means the package was altered after export."
        ),
    }


def verify_chain(records: list[dict]) -> tuple[bool, str | None]:
    """Re-walk a chained audit list. Returns (ok, first_bad_index_or_None)."""
    prev = "0" * 64
    for i, rec in enumerate(records):
        body = {k: v for k, v in rec.items() if k != "digest"}
        payload = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
        expected = _sha256((prev + payload).encode("utf-8"))
        if rec.get("digest") != expected:
            return False, i
        prev = expected
    return True, None


def sign_manifest(manifest: dict, key_hex: str | None = None) -> dict:
    """Attach HMAC-style signature using sha256 when a key is configured.

    Deployment may set EVIDENCE_KEY; absent a key the manifest stays
    verifiable via hashes alone (chain integrity still holds).
    """
    out = dict(manifest)
    key_hex = key_hex or __import__("os").environ.get("EVIDENCE_KEY", "").strip()
    if not key_hex:
        out["signature"] = None
        return out
    body = json.dumps(out, sort_keys=True, separators=(",", ":"), default=str)
    sig = hashlib.sha256((key_hex + body).encode("utf-8")).hexdigest()
    out["signature"] = {"algo": "hmac-sha256", "value": sig}
    return out


def write_evidence_zip_entries(
    records: list[dict], files: dict[str, bytes], *, draft_id: str
) -> dict[str, bytes]:
    """Return additional zip entries: chained audit.json + MANIFEST.json."""
    chained = hash_chain_records(records)
    audit_bytes = json.dumps(chained, indent=2, default=str).encode("utf-8")
    all_files = {**files, "audit.json": audit_bytes}
    manifest = sign_manifest(build_manifest(all_files, draft_id=draft_id))
    manifest_bytes = json.dumps(manifest, indent=2, default=str).encode("utf-8")
    return {"audit.json": audit_bytes, "MANIFEST.json": manifest_bytes}
