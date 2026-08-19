import pytest


@pytest.fixture(autouse=True)
def isolate_sqlite(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "demo.db"))
