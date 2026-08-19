import pytest


@pytest.fixture(autouse=True)
def isolate_sqlite(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "demo.db"))


@pytest.fixture(autouse=True)
def reset_fetch_limiter() -> None:
    from main import reset_rate_limit

    reset_rate_limit()
