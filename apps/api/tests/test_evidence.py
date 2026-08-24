"""Evidence dossier tests: chain integrity, tamper detection, manifest."""

from __future__ import annotations

from boxes.evidence import (
    build_manifest,
    hash_chain_records,
    sign_manifest,
    verify_chain,
    write_evidence_zip_entries,
)


def _records():
    return [
        {"step": "fetch", "ok": True, "n": 3},
        {"step": "score", "ok": True, "gates": {"deep_dive": 1}},
        {"step": "review", "user": "riya", "verdict": "approve"},
    ]


def test_chain_verifies_when_untampered():
    chained = hash_chain_records(_records())
    ok, bad = verify_chain(chained)
    assert ok and bad is None


def test_chain_detects_any_edit():
    chained = hash_chain_chain = hash_chain_records(_records())
    tampered = [dict(r) for r in chained]
    tampered[1]["ok"] = False  # retroactive edit
    ok, bad = verify_chain(tampered)
    assert not ok
    assert bad in (1, 2)  # edited row or the next one depending on payload


def test_chain_detects_deletion():
    chained = hash_chain_records(_records())
    ok, _ = verify_chain(chained[1:])
    assert not ok  # genesis break


def test_manifest_hashes_files_and_carries_chain_head():
    chained = hash_chain_records(_records())
    files = {
        "caption.txt": b"hello",
        "audit.json": b'{"records": ' + str(chained).replace("'", '"').encode() + b"}",
    }
    manifest = build_manifest(files, draft_id="dft_z")
    import hashlib

    assert manifest["files"]["caption.txt"] == hashlib.sha256(b"hello").hexdigest()
    assert len(manifest["audit_chain_head"]) == 64
    # head with unparseable audit falls back to zeros gracefully
    m2 = build_manifest({"audit.json": b"not json"}, draft_id="dft_z")
    assert m2["audit_chain_head"] == "0" * 64


def test_signature_present_only_with_key(monkeypatch):
    monkeypatch.delenv("EVIDENCE_KEY", raising=False)
    m = build_manifest({}, draft_id="x")
    assert sign_manifest(m)["signature"] is None
    monkeypatch.setenv("EVIDENCE_KEY", "secret-key")
    s = sign_manifest(build_manifest({}, draft_id="x"))
    assert s["signature"]["algo"] == "hmac-sha256"
    # tamper breaks signature verification (recompute differs)
    tampered = dict(s)
    tampered["draft_id"] = "dft_other"
    body = __import__("json").dumps(
        {k: v for k, v in tampered.items() if k != "signature"},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    import hashlib

    expected = hashlib.sha256(("secret-key" + body).encode()).hexdigest()
    assert expected != s["signature"]["value"]


def test_write_evidence_entries_roundtrip():
    extra = write_evidence_zip_entries(
        _records(), {"caption.txt": b"x"}, draft_id="dft_q"
    )
    import json

    audit = json.loads(extra["audit.json"])
    ok, bad = verify_chain(audit)
    assert ok and bad is None
    manifest = json.loads(extra["MANIFEST.json"])
    assert manifest["files"]["caption.txt"]
    assert manifest["files"]["audit.json"]
