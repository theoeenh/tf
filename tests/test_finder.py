import json
from dataclasses import asdict

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


def test_untraded_days_are_dropped_from_the_research_data(tmp_path, monkeypatch):
    from algo import wide

    days = pd.bdate_range("2020-01-01", periods=600)
    rows = pd.DataFrame({"symbol": "X", "date": days, "Open": 10.0, "High": 10.5, "Low": 9.5, "Close": 10.0,
                         "Volume": [0 if 100 <= i < 200 else 1000 for i in range(600)]})
    monkeypatch.setattr(wide, "WIDE_DIR", tmp_path)
    rows.to_csv(tmp_path / "daily.csv.gz", index=False)
    df = wide.load_daily(min_days=100)["X"]
    assert len(df) == 500 and (df["Volume"] > 0).all()


def test_a_strategy_that_works_in_some_sectors_gets_specialised_children():
    c = F.Candidate("insider_cluster", {"buyers": 2, "days": 30}, dict(F.DAILY_RULES["hold 20 days"]), data="daily500")
    row = {"by_group": '{"Energy": [0.4, 60], "Utilities": [-0.2, 50], "Financials": [0.3, 12]}'}
    kids = [k for k, _ in F.mutate(c, "shelf life: works on >= 55% of assets (S&P 500: of sectors)", row)]
    assets = {k.assets for k in kids}
    assert "sector:Energy" in assets  # worked there, with enough signals to judge
    assert "sector:Utilities" not in assets and "sector:Financials" not in assets  # lost there / too few signals
    assert {"sp400", "sp600"} <= assets


def _row(c, icir, ic=0.1, **kw):
    return {"id": c.id, "label": c.label(), "family": c.family, "candidate": json.dumps(asdict(c)), "s_icir": icir,
            "s_ic": ic, "s_events": 500, "s_sr_daily": 0.0, "s_n_days": 100, "s_skew": 0.0, "s_kurt": 3.0} | kw


def _child(parent, **change):
    return F.Candidate(**(asdict(parent) | change | {"notes": f"from {parent.id}: test"}))


def test_campaign_refines_its_best_version_and_drops_weak_ideas(monkeypatch, tmp_path):
    rule = dict(F.RULES["target 2R"])
    idea = F.Candidate("rsi2", {"rsi_n": 3, "threshold": 5.0, "trend_ma": 100}, rule)
    better = _child(idea, rule=dict(F.RULES["trailing 3 ATR"]))  # round 1 beat its parent
    weak = F.Candidate("donchian", {"n": 20, "trend_ma": 100}, rule)  # ICIR under the bar
    rows = [_row(idea, 0.25), _row(better, 0.40), _row(weak, -0.3)]
    monkeypatch.setattr(F, "OUT", tmp_path)
    pd.DataFrame(rows).to_csv(tmp_path / "registry.csv", index=False)
    camp = F.campaigns(F.score(F.registry())).set_index("root")
    assert camp.at[idea.id, "best"] == better.id and camp.at[idea.id, "status"] == "improving"
    assert camp.at[weak.id, "status"].startswith("stopped")
    tried = []
    monkeypatch.setattr(F, "run", lambda cands: tried.extend(cands) or F.registry())
    monkeypatch.setattr(F, "grid", lambda: [])
    monkeypatch.setattr(F, "backfill", lambda: None)
    F.loop(rounds=1)
    assert tried and all(k.notes.startswith(f"from {better.id}") for k in tried)  # only the survivor's best


def test_campaign_stops_after_the_round_cap(monkeypatch, tmp_path):
    c = F.Candidate("rsi2", {"rsi_n": 3, "threshold": 5.0, "trend_ma": 100}, dict(F.RULES["target 2R"]))
    chain = [c]
    for k in range(F.MAX_ROUNDS):
        chain.append(_child(chain[-1], params=chain[-1].params | {"rsi_n": 3 + k + 1}))
    rows = [_row(x, 0.3 + 0.01 * k) for k, x in enumerate(chain)]
    monkeypatch.setattr(F, "OUT", tmp_path)
    pd.DataFrame(rows).to_csv(tmp_path / "registry.csv", index=False)
    camp = F.campaigns(F.score(F.registry()))
    assert camp.iloc[0]["rounds"] == F.MAX_ROUNDS and camp.iloc[0]["status"].startswith("finished")
    tried = []
    monkeypatch.setattr(F, "run", lambda cands: tried.extend(cands) or F.registry())
    monkeypatch.setattr(F, "grid", lambda: [])
    monkeypatch.setattr(F, "backfill", lambda: None)
    F.loop(rounds=1)
    assert not tried


def test_hold_follows_where_the_edge_peaks():
    c = F.Candidate("insider_cluster", {"buyers": 2, "days": 30}, dict(F.DAILY_RULES["hold 5 days"]), data="daily500")
    kids = F.mutate(c, "", {"s_peak_h": 40})
    assert any(k.rule["max_bars"] == 40 for k, w in kids if "edge peaks" in w)
    assert not any("edge peaks" in w for _, w in F.mutate(c, "", {"s_peak_h": 6}))  # close enough to 5


def test_plateau_compares_with_parameter_neighbours():
    rule = dict(F.RULES["target 2R"])
    mk = lambda n, ic: _row(F.Candidate("donchian", {"n": n, "trend_ma": 100}, rule), 0.3, ic)  # noqa: E731
    rows = pd.DataFrame([mk(20, 0.10), mk(14, 0.08), mk(28, 0.06), mk(55, -0.5)])  # 55 is too far to count
    p = F.plateau(rows)
    assert abs(p[0] - 0.7) < 1e-9 and np.isnan(p[3])


def test_graduate_trades_only_after_it_graduates(monkeypatch, tmp_path):
    from algo import forward

    idx = pd.date_range("2025-01-01", periods=400, freq="B")
    c = 100 * np.exp(np.cumsum(np.random.default_rng(3).normal(0.0005, 0.01, len(idx))))
    df = pd.DataFrame({"Open": c, "High": c * 1.01, "Low": c * 0.99, "Close": c, "Volume": 1e6}, idx)
    cand = F.Candidate("momentum_12_1", {"top": 0.5}, dict(F.DAILY_RULES["hold 5 days"]), data="daily500")
    monkeypatch.setattr(F, "load", lambda include_vault=False, data="hourly": {"X": df, "Y": df * 1.1})
    monkeypatch.setattr(F, "signals", lambda c, p: {a: pd.Series(1, d.index) for a, d in p.items()})
    monkeypatch.setattr("algo.wide.costs", lambda syms: {s: F.COSTS["NVDA"] for s in syms})
    monkeypatch.setattr(forward, "FWD", tmp_path)
    info = {"since": "2026-01-05", "label": cand.label(), "candidate": json.dumps(asdict(cand))}
    r = forward.update_one("abc", info, {})
    t = pd.read_csv(tmp_path / "abc" / "trades.csv", parse_dates=["entry_date"])
    assert r["trades"] > 0 and (t["entry_date"] >= pd.Timestamp("2026-01-05")).all()
    assert "holding up" in forward.write([r]).read_text() or "behind" in (tmp_path / "report.md").read_text()


def test_insider_dip_needs_the_fall(monkeypatch):
    from algo import finder_families as FF

    idx = pd.bdate_range("2020-01-01", periods=120)
    falling = pd.DataFrame({"Close": np.linspace(100, 70, 120)}, idx)
    rising = pd.DataFrame({"Close": np.linspace(70, 100, 120)}, idx)
    filings = pd.DataFrame({"ticker": ["F", "F", "R", "R"], "code": "P", "owner": ["a", "b", "a", "b"],
                            "accession": ["1", "2", "3", "4"], "filed": pd.to_datetime(["2020-04-01", "2020-04-02"] * 2),
                            "value": 1e6, "role": "Officer"})
    monkeypatch.setattr(FF, "_insider", lambda code="P": filings)
    out = FF.insider_dip({"F": falling, "R": rising}, buyers=2, days=30, drop=0.05)
    assert out["F"].sum() == 1 and out["R"].sum() == 0


def test_merge_keeps_every_attempt_once(monkeypatch, tmp_path):
    monkeypatch.setattr(F, "OUT", tmp_path)
    pd.DataFrame({"id": ["a", "b"], "x": [1, 2]}).to_csv(tmp_path / "registry.csv", index=False)
    pd.DataFrame({"id": ["b", "c"], "x": [9, 3]}).to_csv(tmp_path / "other.csv", index=False)
    assert F.merge(str(tmp_path / "other.csv")) == 1
    r = pd.read_csv(tmp_path / "registry.csv")
    assert list(r["id"]) == ["a", "b", "c"] and r.loc[r.id == "b", "x"].item() == 2


def test_deflated_sharpe_counts_every_try_but_compares_like_with_like():
    calm = list(np.random.default_rng(1).normal(0.0, 0.02, 200))
    wild = list(np.random.default_rng(2).normal(0.0, 0.13, 600))
    own = F.deflated_sharpe(0.08, 1500, 0.0, 3.0, calm, n_trials=800)
    mixed = F.deflated_sharpe(0.08, 1500, 0.0, 3.0, calm + wild, n_trials=800)
    fewer = F.deflated_sharpe(0.08, 1500, 0.0, 3.0, calm, n_trials=200)
    assert mixed < 0.01 < own and fewer >= own  # more tries never make it easier


def test_earnings_reaction_buys_the_strong_reaction_at_its_close(monkeypatch):
    from algo import finder_families as FF

    idx = pd.bdate_range("2021-01-04", periods=120)
    rng = np.random.default_rng(5)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 120)))
    c[100:] *= 1.08  # +8% on day 100, about 8 normal days' moves
    v = np.full(120, 1e6)
    v[100] = 4e6
    df = pd.DataFrame({"Open": c, "High": c, "Low": c, "Close": c, "Volume": v}, idx)
    after_close = pd.Timestamp(idx[99]) + pd.Timedelta(hours=21)  # 16:00 NY: reacts the next session
    monkeypatch.setattr("algo.wide.load_earnings", lambda: pd.DataFrame(
        {"ticker": ["X"], "accepted": [str(after_close)], "day": [idx[100]]}))
    s = FF.earnings_reaction({"X": df}, z=3.0, volume=2.0)["X"]
    assert s.sum() == 1 and s.idxmax() == idx[100]
    cut = FF.earnings_reaction({"X": df.iloc[:101]}, z=3.0, volume=2.0)["X"]
    assert cut.iloc[100] == 1  # known at that close, without any later bar


def test_earnings_day_is_the_first_session_that_can_react(tmp_path, monkeypatch):
    from algo import wide

    monkeypatch.setattr(wide, "WIDE_DIR", tmp_path)
    pd.DataFrame({"ticker": ["A", "B"], "accepted": ["2026-07-30T20:30:28.000Z", "2026-07-14T10:30:38.000Z"]}).to_csv(
        tmp_path / "earnings.csv.gz", index=False)
    e = wide.load_earnings().set_index("ticker")["day"]
    assert e["A"] == pd.Timestamp("2026-07-31")  # after the close: next session
    assert e["B"] == pd.Timestamp("2026-07-14")  # 6:30 New York, before the open: same day


def test_recent_insider_file_with_mixed_date_formats(tmp_path, monkeypatch):
    """A recent-filings file written in two runs mixes '2026-05-22' and '2026-06-29 00:00:00'."""
    from algo import wide

    monkeypatch.setattr(wide, "WIDE_DIR", tmp_path)
    pd.DataFrame({"accession": ["a", "b"], "filed": ["2026-05-22", "2026-06-29 00:00:00"], "traded": [None, None],
                  "ticker": ["X", "X"], "owner": ["o1", "o2"], "code": ["P", "P"], "shares": [1, 2],
                  "price": [1.0, 2.0]}).to_csv(tmp_path / "insider_recent.csv.gz", index=False)
    t = wide.load_insider()
    assert str(t["filed"].dtype).startswith("datetime64") and t["filed"].max() == pd.Timestamp("2026-06-29")
