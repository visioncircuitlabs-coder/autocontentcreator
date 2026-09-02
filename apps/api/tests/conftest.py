import pytest


@pytest.fixture(autouse=True)
def isolate_sqlite(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "demo.db"))
    # Brand memory mirrors SQLite; isolate both or a runtime lessons.md
    # leaks into every test that builds prompts.
    monkeypatch.setenv("MEMORY_DIR", str(tmp_path / "memory"))


@pytest.fixture(autouse=True)
def default_brand(monkeypatch) -> None:
    """Neutrogena stays the test default. Lays tests opt in via lays_brand."""
    monkeypatch.setenv("BRAND_SLUG", "neutrogena")


@pytest.fixture
def lays_brand(monkeypatch) -> None:
    monkeypatch.setenv("BRAND_SLUG", "lays")


@pytest.fixture(autouse=True)
def reset_fetch_limiter() -> None:
    from main import reset_rate_limit

    reset_rate_limit()
