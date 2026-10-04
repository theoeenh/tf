import numpy as np
import pandas as pd

from algo import finder as F


def test_deflated_sharpe_bar_rises_with_the_number_of_tries():
    one = F.deflated_sharpe(0.05, 500, 0.0, 3.0, [0.05])
    many = F.deflated_sharpe(0.05, 500, 0.0, 3.0, list(np.random.default_rng(0).normal(0, 0.04, 300)))
    assert one > 0.8 and many < one


def test_edge_removes_the_drift():
    idx = pd.date_range("2024-01-01", periods=400, freq="h")
    c = np.linspace(100, 140, 400)  # steady rise: every long looks good before the drift is removed
    df = pd.DataFrame({"Open": c, "High": c + 1, "Low": c - 1, "Close": c, "Volume": 1.0}, idx)
    sig = pd.Series(0, idx)
    sig.iloc[100:300:10] = 1
    ev = F.edge_events({"X": sig}, {"X": df}, 12)
    assert abs(ev["edge"].mean()) < 1e-6


def test_vault_is_sealed_by_default(monkeypatch):
    idx = pd.date_range("2025-06-25", "2025-07-05", freq="h")
    df = pd.DataFrame({"Open": 1.0, "High": 1.0, "Low": 1.0, "Close": 1.0, "Volume": 1.0}, idx)
    monkeypatch.setattr(F, "load_prices", lambda *a, **k: {"X": df})
    assert F.load()["X"].index.max() < pd.Timestamp(F.VAULT_START)
    assert F.load(include_vault=True)["X"].index.max() > pd.Timestamp(F.VAULT_START)


def _bars(close, start="2024-03-04 14:00", freq="h"):
    idx = pd.date_range(start, periods=len(close), freq=freq)
    c = np.asarray(close, float)
    return pd.DataFrame({"Open": c, "High": c + 0.5, "Low": c - 0.5, "Close": c, "Volume": 100.0}, idx)


def test_cross_asset_momentum_enters_once_when_an_asset_becomes_the_strongest():
    from algo.finder_families import xs_momentum

    n = 60
    up = _bars(np.r_[np.full(30, 100.0), np.linspace(100, 130, 30)])
    flat = {f"F{i}": _bars(100 + 0.1 * np.arange(n) + 0.01 * i) for i in range(3)}  # slow steady rise
    sig = xs_momentum({"UP": up} | flat, lookback=5, top=1)
    assert sig["UP"].sum() == 1  # one entry, not one per bar it stays on top
    assert sig["UP"].idxmax() > up.index[30]


def test_panel_signals_use_no_future_bar():
    from algo.finder_families import PANEL_FAMILIES

    rng = np.random.default_rng(1)
    prices = {a: _bars(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300)))) for a in ("BTC", "ETH", "SOL", "SPY", "QQQ")}
    cut = 200
    for fam, (fn, space) in PANEL_FAMILIES.items():
        if fam == "earnings_drift":
            continue
        params = {k: v[0] for k, v in space.items()}
        full = fn(prices, **params)
        part = fn({a: df.iloc[:cut] for a, df in prices.items()}, **params)
        for a in part:
            assert (full[a].iloc[:cut] == part[a]).all(), fam


def test_children_follow_the_failures():
    c = F.Candidate("donchian", {"n": 20, "trend_ma": 100}, dict(F.RULES["target 2R"]))
    kids = F.mutate(c, "shelf life: works on >= 55% of assets; search: beats random entries (avg R)")
    whys = [w for _, w in kids]
    assert any("only stocks" in w for w in whys)
    assert any("exit" in w for w in whys)
    assert all(k.id != c.id for k, _ in kids)
    slower = F.mutate(c, "search: ICIR >= 0.2 (stable month to month)")
    assert any(k.params["n"] > 20 for k, w in slower if "slower" in w)


def test_ranking_never_looks_at_validation():
    base = {"s_events": 500, "s_ic": 0.1, "s_icir": 0.3, "s_avg_r": 0.2, "s_rand_avg_r": 0.1, "s_dsr": 0.5}
    good_v = base | {"v_ic": 0.5, "v_return": 0.3}
    bad_v = base | {"v_ic": -0.5, "v_return": -0.3}
    assert F.fitness(good_v) == F.fitness(bad_v)


def test_old_ids_do_not_change_with_the_asset_filter():
    c = F.Candidate("rsi2", {"rsi_n": 3}, {"stop_atr": 2.0, "rr": 2.0})
    assert c.id == F.Candidate("rsi2", {"rsi_n": 3}, {"stop_atr": 2.0, "rr": 2.0}, assets="all").id
    assert c.id != F.Candidate("rsi2", {"rsi_n": 3}, {"stop_atr": 2.0, "rr": 2.0}, assets="stocks").id


def _daily(n=400, seed=0):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    return _bars(c, start="2020-01-01", freq="B")


def test_insider_cluster_fires_once_on_the_filing_day(monkeypatch):
    from algo import finder_families as FF

    df = _daily()
    filings = pd.DataFrame({"ticker": "X", "code": "P", "owner": ["a", "b", "c"], "accession": ["1", "2", "3"],
                            "filed": pd.to_datetime(["2020-03-02", "2020-03-10", "2020-03-12"]),
                            "value": 1e6, "role": "Officer"})
    monkeypatch.setattr(FF, "_insider", lambda code="P": filings)
    s = FF.insider_cluster({"X": df}, buyers=2, days=30)["X"]
    assert s.sum() == 1 and s.idxmax() == pd.Timestamp("2020-03-10")  # the second buyer's filing day
    weekend = filings.assign(filed=pd.to_datetime(["2020-03-02", "2020-03-14", "2020-03-20"]))  # a Saturday
    monkeypatch.setattr(FF, "_insider", lambda code="P": weekend)
    s = FF.insider_cluster({"X": df}, buyers=2, days=30)["X"]
    assert s.idxmax() == pd.Timestamp("2020-03-16")  # the next trading day, never before the filing


def test_daily_factor_families_use_no_future_bar():
    from algo.finder_families import WIDE_FAMILIES

    prices = {f"S{i}": _daily(seed=i) for i in range(20)}
    cut = 300
    for fam in ("momentum_12_1", "reversal_5d", "high_52w"):
        fn, space = WIDE_FAMILIES[fam]
        params = {k: v[0] for k, v in space.items()}
        full = fn(prices, **params)
        part = fn({a: df.iloc[:cut] for a, df in prices.items()}, **params)
        for a in part:
            # the last bar of the cut may differ only for momentum's month-end test (needs the next day)
            n = cut - 1 if fam == "momentum_12_1" else cut
            assert (full[a].iloc[:n] == part[a].iloc[:n]).all(), fam


def test_daily_candidates_keep_their_own_id_and_rules():
    c = F.Candidate("insider_cluster", {"buyers": 2, "days": 30}, dict(F.DAILY_RULES["hold 20 days"]), data="daily500")
    assert c.id != F.Candidate("insider_cluster", {"buyers": 2, "days": 30}, dict(F.DAILY_RULES["hold 20 days"])).id
    kids = F.mutate(c, "search: beats random entries (avg R)")
    assert all(k.data == "daily500" and k.rule in F.DAILY_RULES.values() for k, _ in kids)
