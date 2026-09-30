import json

import numpy as np
import pytest

from algo import analyst
from tests.test_engine import flat_bars


def test_view_files_in_repo_are_valid():
    """Every AI view written so far must parse (run after the analyst writes one)."""
    analyst.load_views()


def test_validate_rejects_bad_views():
    with pytest.raises(ValueError):
        analyst.validate_view({"asset": "BTC", "bias": 3, "confidence": 0.5, "horizon_days": 5, "reasoning": "x"})
    with pytest.raises(ValueError):
        analyst.validate_view({"asset": "BTC", "bias": 1, "confidence": 1.5, "horizon_days": 5, "reasoning": "x"})


def test_scoring_uses_only_moves_after_the_view(tmp_path):
    df = flat_bars(n=40)
    df["Close"] = np.r_[np.full(20, 100.0), np.linspace(100, 120, 20)]
    day = df.index[19]
    (tmp_path / f"{day:%Y-%m-%d}.json").write_text(json.dumps(
        [{"asset": "A", "bias": 1, "confidence": 0.7, "horizon_days": 5, "reasoning": "test"}]))
    views = analyst.load_views(tmp_path)
    s = analyst.score_views(views, {"A": df})
    assert len(s) == 1 and s.right.iloc[0] and s.move_atr.iloc[0] > 0
    assert analyst.bias_frame(views).loc[day, "A"] == 1


def test_views_not_due_are_not_scored(tmp_path):
    df = flat_bars(n=40)
    day = df.index[-3]
    (tmp_path / f"{day:%Y-%m-%d}.json").write_text(json.dumps(
        [{"asset": "A", "bias": -1, "confidence": 0.5, "horizon_days": 10, "reasoning": "test"}]))
    assert analyst.score_views(analyst.load_views(tmp_path), {"A": df}).empty
