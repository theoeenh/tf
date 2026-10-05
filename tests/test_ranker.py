import numpy as np
import pandas as pd

from algo import ranker as R


def _prices(n_stocks=40, n_days=900, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2017-01-02", periods=n_days)
    out = {}
    for i in range(n_stocks):
        c = 50 * np.exp(np.cumsum(rng.normal(0.0003, 0.02, n_days)))
        out[f"S{i:02d}"] = pd.DataFrame({"Open": c * (1 + rng.normal(0, 0.002, n_days)), "High": c * 1.01,
                                         "Low": c * 0.99, "Close": c, "Volume": rng.integers(1e5, 1e6, n_days)}, idx)
    return out


def _quiet(monkeypatch):
    monkeypatch.setattr(R.wide, "load_insider", lambda: pd.DataFrame())
    monkeypatch.setattr(R.wide, "index_of", lambda: {})
    monkeypatch.setattr(R, "MIN_TRAIN_WEEKS", 30)
    monkeypatch.setattr(R, "REFIT_WEEKS", 8)
    monkeypatch.setattr(R, "MIN_TRAIN_ROWS", 300)


def test_features_use_no_future_bar(monkeypatch):
    _quiet(monkeypatch)
    p = _prices()
    full = R.dataset(p)
    cut = p["S00"].index[700]
    part = R.dataset({a: df[df.index <= cut] for a, df in p.items()})
    common = part.index.intersection(full.index)
    feats = [f for f in R.FEATURES if f != "mkt_1m"]
    assert len(common) > 1000
    assert np.allclose(full.loc[common, feats].to_numpy(dtype=float), part.loc[common, feats].to_numpy(dtype=float),
                       equal_nan=True)


def test_walk_forward_scores_do_not_change_with_later_data(monkeypatch):
    _quiet(monkeypatch)
    p = _prices()
    s_full = R.walk_forward(R.dataset(p), "ridge")
    cut = p["S00"].index[780]
    s_part = R.walk_forward(R.dataset({a: df[df.index <= cut] for a, df in p.items()}), "ridge")
    common = s_part.index.intersection(s_full.index)
    early = common[common.get_level_values("date") <= cut - pd.Timedelta(days=60)]
    assert len(early) > 200
    assert np.allclose(s_full.loc[early], s_part.loc[early])


def test_target_is_relative_to_the_average_stock(monkeypatch):
    _quiet(monkeypatch)
    ds = R.dataset(_prices())
    m = ds["target"].groupby(level="date").mean().dropna()
    assert (m.abs() < 1e-9).all()


def test_no_feature_uses_todays_index_membership():
    assert "index" not in R.FEATURES  # today's S&P lists would tell the model which stocks grew
