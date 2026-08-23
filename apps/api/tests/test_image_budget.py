"""Image budget gate tests — Grok is images-only with a hard $ cap."""

from __future__ import annotations

import pytest

from boxes import image_budget as ib


@pytest.fixture()
def budget_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "b.db"))
    monkeypatch.setenv("IMAGE_BUDGET_USD", "0.06")  # 3 images at 0.02
    (tmp_path / "spend.jsonl").unlink(missing_ok=True)
    yield tmp_path


def test_gate_allows_under_cap(budget_env):
    ib.record_spend(0.02)
    status = ib.spend_gate()
    assert status["spent"] == 0.02
    assert status["cap"] == 0.06


def test_gate_blocks_over_cap(budget_env):
    for _ in range(3):
        ib.record_spend(0.02)
    with pytest.raises(ib.BudgetExceeded):
        ib.spend_gate()


def test_spend_persists_across_instances(budget_env):
    ib.record_spend(0.04)
    assert ib.spent_usd() == pytest.approx(0.04)
    # fresh module state (simulated restart) — file read again
    assert ib.spent_usd() == pytest.approx(0.04)


def test_default_budget_is_two_dollars(monkeypatch, tmp_path):
    monkeypatch.delenv("IMAGE_BUDGET_USD", raising=False)
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "c.db"))
    assert ib.budget_usd() == 2.00
    # and a fresh wallet allows the first call
    ib.spend_gate()


def test_bad_budget_value_falls_back(monkeypatch, tmp_path):
    monkeypatch.setenv("IMAGE_BUDGET_USD", "lots")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "d.db"))
    assert ib.budget_usd() == 2.00


def test_corrupt_lines_ignored(budget_env):
    path = ib._spend_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"usd": 0.02}\nnot json\n{"usd": "x"}\n')
    assert ib.spent_usd() == pytest.approx(0.02)
