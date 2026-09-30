import numpy as np
import pandas as pd

from algo.ml import MLLearner


def feed(learner, n, rng, t0=pd.Timestamp("2025-01-01")):
    """Synthetic trades: strong trends (ADX > 30) win 2R, weak ones lose 1R."""
    for i in range(n):
        adx = rng.uniform(5, 60)
        key = learner.keys("donchian_trend", 1, {}, asset="BTC", time=t0 + pd.Timedelta(hours=i),
                           feats={"adx": adx, "atr_pct": 0.01})
        learner.judge(key)
        learner.record(key, 2.0 if adx > 30 else -1.0)


def test_learns_which_trades_to_skip_walk_forward():
    ml = MLLearner(min_trades=200, refit_days=1)
    feed(ml, 1500, np.random.default_rng(0))
    assert ml.fits > 0
    t = pd.Timestamp("2025-06-01")
    good = ml.keys("donchian_trend", 1, {}, asset="ETH", time=t, feats={"adx": 50, "atr_pct": 0.01})
    bad = ml.keys("donchian_trend", 1, {}, asset="ETH", time=t, feats={"adx": 10, "atr_pct": 0.01})
    assert not ml.judge(good).skip and ml.judge(bad).skip
    rep = ml.report()
    assert rep["auc"] > 0.9 and rep["taken_avg_r"] > 0 > rep["skipped_avg_r"]


def test_allows_everything_until_enough_trades_and_never_uses_open_trades():
    ml = MLLearner(min_trades=200, refit_days=1)
    feed(ml, 150, np.random.default_rng(1))
    assert ml.model is None and ml.fits == 0  # too few closed trades: no model, nothing skipped
    key = ml.keys("rsi2_reversion", -1, {}, asset="NVDA", time=pd.Timestamp("2025-02-01"), feats={"adx": 10})
    assert not ml.judge(key).skip
    assert len(ml.y) == 150  # a trade only enters the training data once it is recorded (closed)


def test_sizing_bets_more_on_better_trades():
    ml = MLLearner(min_trades=200, refit_days=1, sizing=True)
    feed(ml, 1500, np.random.default_rng(2))
    key = ml.keys("donchian_trend", 1, {}, asset="SOL", time=pd.Timestamp("2025-06-01"), feats={"adx": 50})
    v = ml.judge(key)
    assert not v.skip and v.size > 1
