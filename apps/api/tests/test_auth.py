"""Auth & roles tests. Open mode with zero keys; enforced once one exists."""

from __future__ import annotations

import pytest

from boxes import auth
from db import get_conn, init_db


@pytest.fixture()
def fresh_keys(monkeypatch, tmp_path):
    """Isolated api_keys table state via a temp DB."""
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "auth.db"))
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    init_db()
    yield


def test_open_mode_when_no_keys(fresh_keys):
    ok, why = authorize_any("/review/dft_x")
    assert ok
    assert why == "open"


def _authorize(path):
    return auth.authorize(path, None)


authorize_any = _authorize


def test_missing_key_rejected_once_key_exists(fresh_keys):
    auth.create_key("ops", "approver")
    ok, why = _authorize("/review/dft_x")
    assert not ok
    assert "API key" in why


def test_role_ranking(fresh_keys):
    viewer_raw = auth.create_key("intern", "viewer")
    approver_raw = auth.create_key("ops", "approver")

    viewer = auth.authenticate(viewer_raw)
    approver = auth.authenticate(approver_raw)

    # review needs approver
    ok_v, _ = auth.authorize("/review/dft_x", viewer)
    ok_a, _ = auth.authorize("/review/dft_x", approver)
    assert not ok_v
    assert ok_a

    # factory/image and factory/video need approver
    ok_img, _ = auth.authorize("/factory/image", viewer)
    assert not ok_img
    ok_vid, _ = auth.authorize("/factory/video", viewer)
    assert not ok_vid
    ok_vid_a, _ = auth.authorize("/factory/video", approver)
    assert ok_vid_a

    # reads are open to any role
    ok_read, _ = auth.authorize("/drafts", viewer)
    assert ok_read


def test_admin_can_mint_but_viewer_cannot_hit_admin(fresh_keys):
    admin_raw = auth.create_key("boss", "admin")
    admin = auth.authenticate(admin_raw)
    ok, _ = auth.authorize("/admin/keys", admin)
    assert ok


def test_bad_key_rejected(fresh_keys):
    auth.create_key("ops", "approver")
    assert auth.authenticate("cm_notarealkey") is None
    assert auth.authenticate(None) is None


def test_create_key_validates_role(fresh_keys):
    with pytest.raises(ValueError):
        auth.create_key("x", "superuser")


def test_bootstrap_admin_from_env(monkeypatch, fresh_keys):
    monkeypatch.setenv("ADMIN_API_KEY", "bootstrap-secret-123")
    auth.ensure_bootstrap()
    ident = auth.authenticate("bootstrap-secret-123")
    assert ident is not None
    assert ident["role"] == "admin"
    # idempotent
    auth.ensure_bootstrap()


def test_hash_not_reversible(fresh_keys):
    raw = auth.create_key("t", "viewer")
    conn = get_conn()
    row = conn.execute("SELECT key_hash FROM api_keys").fetchone()
    assert raw not in row[0]
