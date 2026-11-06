"""Video budget gate — separate USD cap from stills."""

from __future__ import annotations

import pytest

from boxes import image_budget as ib
from boxes import video_budget as vb


@pytest.fixture()
def budget_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "b.db"))
    monkeypatch.setenv("VIDEO_BUDGET_USD", "0.80")  # two 5s clips at $0.40
    (tmp_path / "spend.jsonl").unlink(missing_ok=True)
    yield tmp_path


def test_video_gate_allows_under_cap(budget_env):
    vb.record_video_spend(0.40)
    status = vb.spend_gate()
    assert status["spent"] == pytest.approx(0.40)
    assert status["cap"] == pytest.approx(0.80)


def test_video_gate_blocks_over_cap(budget_env):
    vb.record_video_spend(0.40)
    vb.record_video_spend(0.40)
    with pytest.raises(vb.BudgetExceeded):
        vb.spend_gate()


def test_video_spend_does_not_eat_image_budget(budget_env):
    vb.record_video_spend(0.40)
    assert ib.spent_usd() == pytest.approx(0.0)
    assert vb.spent_usd() == pytest.approx(0.40)
    ib.spend_gate()


def test_default_video_budget_is_two_dollars(monkeypatch, tmp_path):
    monkeypatch.delenv("VIDEO_BUDGET_USD", raising=False)
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "c.db"))
    assert vb.budget_usd() == 2.00
    vb.spend_gate()
