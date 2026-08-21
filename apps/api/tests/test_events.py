from obs import emit, scrub


def test_scrub_hides_keys() -> None:
    out = scrub({"XAI_API_KEY": "xai-secret", "title": "hello"})
    assert out["XAI_API_KEY"] == "[redacted]"
    assert out["title"] == "hello"


def test_emit_roundtrip(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "e.db"))
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "e.jsonl"))
    event_id = emit("test_kind", n=3)
    from db import list_events

    rows = list_events(10)
    assert rows
    assert rows[0]["id"] == event_id
    assert rows[0]["kind"] == "test_kind"
    assert rows[0]["payload"]["n"] == 3
