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


def test_parameter_neighbours_keep_shares_below_one():
    """2026-10-28: insider_stress_low_short(max_rank=0.98) had a neighbour max_rank=1.37: a share of the
    universe above 100% switches the short filter off, so the 'new' idea scored as insider_sector_stress."""
    c = F.Candidate("insider_stress_low_short", {"drop": 0.15, "max_rank": 0.98}, dict(F.RULES["target 2R"]))
    ps = F._neighbours(c)
    assert {p["max_rank"] for p in ps} == {0.98, 0.69} and all(0 < p["drop"] < 1 for p in ps)
    k = F.Candidate("intraday_momentum", {"k": 0.75}, dict(F.RULES["target 2R"]))
    assert {p["k"] for p in F._neighbours(k)} == {0.52, 1.05}  # not a share: may pass 1


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


def test_insider_low_short_uses_only_published_short_data(monkeypatch):
    """The short-volume filter on day t reads ratios up to t-1 (FINRA publishes after the close)."""
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-01", periods=60)
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in ("AAA", "BBB", "CCC", "DDD")}
    sig_day = days[40]
    monkeypatch.setattr(ff, "insider_cluster", lambda p, buyers, days: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    base = pd.DataFrame({"AAA": 0.1, "BBB": 0.2, "CCC": 0.3, "DDD": 0.4}, index=days)
    monkeypatch.setattr(wide, "load_short_volume", lambda: base)
    a = ff.insider_low_short(prices, max_rank=0.5)
    moved = base.copy()
    moved.loc[sig_day:, "AAA"] = 9.0  # the signal day's own ratio and later: unknown that day
    monkeypatch.setattr(wide, "load_short_volume", lambda: moved)
    b = ff.insider_low_short(prices, max_rank=0.5)
    assert a["AAA"].loc[sig_day] == 1 and a["DDD"].loc[sig_day] == 0
    assert all(a[k].equals(b[k]) for k in a)


def test_insider_fund_uses_only_filed_fundamentals(monkeypatch):
    """The fundamentals filter on day t reads only filings made before t."""
    from algo import finder_families as ff, fundamentals

    days = pd.bdate_range("2021-01-01", periods=60)
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in ("AAA", "BBB", "CCC", "DDD")}
    sig_day = days[40]
    monkeypatch.setattr(ff, "insider_cluster", lambda p, buyers, days: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    rows = [(t, "eps_q", end, end + pd.Timedelta(days=30), v) for t, base in
            (("AAA", 1.0), ("BBB", 0.5), ("CCC", 0.2), ("DDD", 0.1))
            for k, (end, v) in enumerate((pd.Timestamp("2018-03-31") + pd.DateOffset(months=3 * i), base * i + (i % 3))
                                         for i in range(10))]
    fd = pd.DataFrame(rows, columns=["ticker", "item", "end", "filed", "val"])
    monkeypatch.setattr(fundamentals, "load", lambda: fd)
    a = ff.insider_fund(prices, feature="f_sue", min_rank=0.5)
    # a filing made on the signal day (its numbers known from the next session) changes nothing
    late = pd.DataFrame([("AAA", "eps_q", pd.Timestamp("2020-12-31"), sig_day, -100.0)], columns=fd.columns)
    monkeypatch.setattr(fundamentals, "load", lambda: pd.concat([fd, late], ignore_index=True))
    b = ff.insider_fund(prices, feature="f_sue", min_rank=0.5)
    assert sum(int(a[k].loc[sig_day]) for k in a) >= 1
    assert all(a[k].equals(b[k]) for k in a)


def test_insider_after_earnings_uses_only_past_releases(monkeypatch):
    """A cluster counts only after a release already out at the signal session (none from the future),
    and only when that release's reaction was negative."""
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-04", periods=80)
    close = pd.Series(100.0, days)
    close.iloc[30] = 95.0  # reaction to the release of day 30: -5%
    prices = {"AAA": pd.DataFrame({"Close": close}), "BBB": pd.DataFrame({"Close": pd.Series(100.0, days)})}
    sig_day = days[45]
    monkeypatch.setattr(ff, "insider_cluster", lambda p, buyers, days: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    e = pd.DataFrame({"ticker": ["AAA", "AAA"], "day": [days[30], days[50]]})  # day 50: after the signal
    monkeypatch.setattr(wide, "load_earnings", lambda: e)
    a = ff.insider_after_earnings(prices, window=20)
    assert a["AAA"].loc[sig_day] == 1 and a["BBB"].sum() == 0
    monkeypatch.setattr(wide, "load_earnings", lambda: e.iloc[1:])  # only the future release
    b = ff.insider_after_earnings(prices, window=20)
    assert b["AAA"].sum() == 0
    assert ff.insider_after_earnings(prices, window=10)["AAA"].sum() == 0  # 15 sessions after: too late


def test_insider_conviction_uses_only_known_shares_and_purchases(monkeypatch):
    """Size uses shares outstanding filed before the signal day, and purchases filed up to it."""
    from algo import finder_families as ff, fundamentals

    days = pd.bdate_range("2021-01-04", periods=60)
    prices = {"AAA": pd.DataFrame({"Close": 10.0}, index=days)}
    sig_day = days[40]
    monkeypatch.setattr(ff, "insider_cluster", lambda p, buyers, days: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    buys = pd.DataFrame({"ticker": "AAA", "filed": [days[30], days[45]], "owner": ["o1", "o2"],
                         "value": [60_000.0, 1e9], "code": "P"})  # the second is filed after the signal
    monkeypatch.setattr(ff, "_insider", lambda code="P": buys)
    sh = pd.DataFrame({"ticker": "AAA", "item": "shares", "end": pd.to_datetime(["2020-09-30", "2020-12-31"]),
                       "filed": [days[0], sig_day], "val": [1e6, 1e9]})  # the 2nd known only from the next day
    monkeypatch.setattr(fundamentals, "load", lambda: sh)
    # $60k on 1M shares x $10 = 60 bp: kept at 10 bp; the later purchase and share count change nothing
    assert ff.insider_conviction(prices, min_bp=10.0)["AAA"].loc[sig_day] == 1
    assert ff.insider_conviction(prices, min_bp=100.0)["AAA"].sum() == 0


def test_insider_confirm_waits_for_the_cross_and_uses_no_future_close(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=120)
    close = pd.Series(100.0, days)
    close.iloc[60:70] = 90.0          # below its average after the cluster on day 60
    close.iloc[70:] = 105.0           # crosses back above on day 70
    prices = {"AAA": pd.DataFrame({"Close": close})}
    monkeypatch.setattr(ff, "insider_cluster", lambda p, buyers, days: {
        a: pd.Series((p[a].index == p[a].index[60]).astype(int), p[a].index) for a in p})
    a = ff.insider_confirm(prices, wait=20, ma=50)["AAA"]
    assert a.sum() == 1 and a.iloc[70] == 1
    assert ff.insider_confirm(prices, wait=5, ma=50)["AAA"].sum() == 0  # no cross within 5 sessions
    # the signal on day 70 does not change when later closes change
    cut = {"AAA": pd.DataFrame({"Close": close.iloc[:71]})}
    assert ff.insider_confirm(cut, wait=20, ma=50)["AAA"].iloc[70] == 1


def test_insider_sector_wave_counts_only_past_clusters(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-04", periods=80)
    names = ["A1", "A2", "A3", "B1"]
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in names}
    when = {"A1": days[10], "A2": days[20], "A3": days[30], "B1": days[25]}  # A3's comes after A1's signal
    monkeypatch.setattr(ff, "insider_cluster", lambda p, buyers, days: {
        a: pd.Series((p[a].index == when[a]).astype(int), p[a].index) for a in p})
    monkeypatch.setattr(wide, "sectors", lambda: {"A1": "Ind", "A2": "Ind", "A3": "Ind", "B1": "Tech"})
    out = ff.insider_sector_wave(prices, companies=3, window=60)
    assert out["A1"].sum() == 0 and out["A2"].sum() == 0  # not yet 3 companies on their day
    assert out["A3"].loc[days[30]] == 1                     # the third of the wave
    assert out["B1"].sum() == 0                             # another sector does not count


def test_merge_insider_recent_unions_rows_and_days(tmp_path, monkeypatch):
    from algo import wide

    monkeypatch.setattr(wide, "WIDE_DIR", tmp_path)
    cols = dict(traded=None, ticker="X", code="P", shares=1, price=1.0)
    pd.DataFrame([dict(accession="a", owner="o1", filed="2026-07-01", **cols)]).to_csv(
        tmp_path / "insider_recent.csv.gz", index=False)
    (tmp_path / "insider_recent_days.txt").write_text("20260701\n")
    other = tmp_path / "other"; other.mkdir()
    pd.DataFrame([dict(accession="a", owner="o1", filed="2026-07-01 00:00:00", **cols),
                  dict(accession="b", owner="o2", filed="2026-07-02", **cols)]).to_csv(
        other / "r.csv.gz", index=False)
    (other / "d.txt").write_text("20260702\n")
    assert wide.merge_insider_recent(other / "r.csv.gz", other / "d.txt") == 2
    assert (tmp_path / "insider_recent_days.txt").read_text().split() == ["20260701", "20260702"]


def test_insider_recent_skips_days_missing_from_the_sec_listing(tmp_path, monkeypatch):
    """A holiday has no daily index and the SEC answers 403 for it: the quarter listing tells."""
    import json as _json
    from algo import insider, wide

    monkeypatch.setattr(wide, "WIDE_DIR", tmp_path)
    monkeypatch.setattr(wide, "_bulk_end", lambda: pd.Timestamp("2026-06-30"))
    monkeypatch.setattr(insider, "cik", lambda t: 1)
    (insider.INSIDER_DIR).mkdir(parents=True, exist_ok=True)
    asked = []

    def sec(url):
        asked.append(url)
        if url.endswith("index.json"):
            return _json.dumps({"directory": {"item": [{"name": "form.20260702.idx"}, {"name": "form.20260706.idx"}]}}).encode()
        if "form.2026070" in url:
            return b"header\n"
        raise OSError("SEC refused " + url)

    monkeypatch.setattr(wide, "_sec", sec)
    monkeypatch.setattr(pd.Timestamp, "now", classmethod(lambda cls, tz=None: pd.Timestamp("2026-07-20", tz=tz)))
    wide.update_insider_recent(tickers=[])
    assert not any("form.20260703" in u for u in asked)
    done = (tmp_path / "insider_recent_days.txt").read_text().split()
    assert "20260703" in done and "20260702" in done and "20260706" in done


def test_a_strategy_passing_every_gate_alerts_the_phone_before_its_vault_test(monkeypatch, tmp_path):
    from algo import finder as F, forward, notify

    reg = pd.DataFrame({"id": ["g1", "g2"], "label": ["graduate", "almost"],
                        "gates_passed": [len(F.GATES), len(F.GATES) - 1]})
    monkeypatch.setattr(F, "OUT", tmp_path)
    monkeypatch.setattr(F, "registry", lambda: reg)
    monkeypatch.setattr(F, "score", lambda r: r)
    sent, order = [], []
    monkeypatch.setattr(notify, "send", lambda title, *a, **k: sent.append(title) or order.append("alert") or True)
    monkeypatch.setattr(F, "vault", lambda i: order.append("vault") or {
        "result": "FAIL", "return": 0.0, "avg_r": 0.0, "icir": 0.0, "search_icir": 0.0})
    monkeypatch.setattr(forward, "start", lambda i: None)
    F.promote()
    assert sent[0] == f"finder: a strategy passed all {len(F.GATES)} checks" and order[:2] == ["alert", "vault"]
    assert len(sent) == 2  # only the 14/14 one: its alert, then its vault result


def test_insider_fresh_counts_only_first_buys_in_the_gap_and_known_filings(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=300)
    prices = {"AAA": pd.DataFrame({"Close": 10.0}, index=days)}
    rows = [("r", "2021-01-05"), ("r", "2021-06-01"),  # routine: bought 5 months before
            ("f", "2021-06-03"),                         # fresh
            ("g", "2021-12-01")]                         # fresh, but the next cluster window
    t = pd.DataFrame([dict(ticker="AAA", owner=o, filed=pd.Timestamp(d), code="P") for o, d in rows])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_fresh(prices, buyers=2, gap=365)["AAA"]
    # 2021-01-05 (r, first ever) + 2021-06-03 (f) are > 90 days apart; r's June buy is not fresh
    assert out.sum() == 0
    t.loc[len(t)] = dict(ticker="AAA", owner="h", filed=pd.Timestamp("2021-06-10"), code="P")
    out = ff.insider_fresh(prices, buyers=2, gap=365)["AAA"]
    assert out.loc["2021-06-10"] == 1 and out.sum() == 1   # f + h, on the day the second is filed
    early = ff.insider_fresh({"AAA": prices["AAA"].loc[:"2021-06-09"]}, buyers=2, gap=365)["AAA"]
    assert early.sum() == 0                                # later filings never count


def test_insider_fresh_officer_counts_only_officers(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=120)
    prices = {"AAA": pd.DataFrame({"Close": 10.0}, index=days)}
    t = pd.DataFrame([dict(ticker="AAA", owner="d", filed=pd.Timestamp("2021-02-01"), code="P", role="Director"),
                      dict(ticker="AAA", owner="c", filed=pd.Timestamp("2021-03-01"), code="P", role="Officer")])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_fresh_officer(prices, buyers=1, gap=365)["AAA"]
    assert out.sum() == 1 and out.loc["2021-03-01"] == 1  # the director's buy does not count
    assert ff.insider_fresh_officer(prices, buyers=2, gap=365)["AAA"].sum() == 0


def test_insider_fresh_wave_needs_a_past_sector_wave(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-04", periods=80)
    names = ["A1", "A2", "A3", "B1"]
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in names}
    on = lambda when: (lambda p, **k: {a: pd.Series((p[a].index == when.get(a)).astype(int), p[a].index)  # noqa: E731
                                       for a in p})
    monkeypatch.setattr(ff, "insider_fresh", on({"A3": days[30], "B1": days[30]}))
    monkeypatch.setattr(ff, "insider_cluster", on({"A1": days[10], "A2": days[20], "A3": days[40]}))
    monkeypatch.setattr(wide, "sectors", lambda: {"A1": "Ind", "A2": "Ind", "A3": "Ind", "B1": "Tech"})
    out = ff.insider_fresh_wave(prices, buyers=1, companies=3, window=60)
    assert out["A3"].loc[days[30]] == 1   # A1 + A2 clusters before, A3 itself: 3 companies
    assert out["B1"].sum() == 0           # no wave in its sector
    out = ff.insider_fresh_wave(prices, buyers=1, companies=4, window=60)
    assert out["A3"].sum() == 0           # A3's own later cluster (day 40) never counts


def test_insider_underwater_uses_only_filed_purchases_and_past_closes(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=60)
    close = pd.Series(100.0, index=days)
    close.iloc[30:] = 88.0                                   # 12% under the insiders' price from day 30
    prices = {"AAA": pd.DataFrame({"Close": close})}
    t = pd.DataFrame([dict(ticker="AAA", owner="o1", filed=days[10], code="P", price=100.0, shares=1000),
                      dict(ticker="AAA", owner="o2", filed=days[20], code="P", price=100.0, shares=500),
                      dict(ticker="AAA", owner="o3", filed=days[40], code="P", price=50.0, shares=99999)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_underwater(prices, buyers=2, discount=0.10)["AAA"]
    assert out.loc[days[30]] == 1 and out.sum() == 1         # o3's later cheap purchase changes nothing before
    assert ff.insider_underwater(prices, buyers=3, discount=0.10)["AAA"].iloc[:40].sum() == 0
    assert ff.insider_underwater(prices, buyers=2, discount=0.15)["AAA"].sum() == 0


def test_insider_clean_skips_stocks_with_recent_insider_sales(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=300)
    prices = {"AAA": pd.DataFrame({"Close": pd.Series(100.0, index=days)})}
    buys = pd.DataFrame([dict(ticker="AAA", owner="o1", filed=days[10], code="P", price=100.0, shares=10),
                         dict(ticker="AAA", owner="o2", filed=days[200], code="P", price=100.0, shares=10)])
    sells = pd.DataFrame([dict(ticker="AAA", owner="o9", filed=days[150], code="S", price=100.0, shares=10),
                          dict(ticker="AAA", owner="o9", filed=days[250], code="S", price=100.0, shares=10)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": buys if code == "P" else sells)
    out = ff.insider_clean(prices, buyers=1, quiet=180)["AAA"]
    assert out.loc[days[10]] == 1 and out.sum() == 1        # day 200: a sale 50 sessions before; day 250's is later
    assert ff.insider_clean(prices, buyers=1, quiet=30)["AAA"].loc[days[200]] == 1
    assert ff.insider_clean(prices, buyers=2, quiet=30)["AAA"].sum() == 0


def test_insider_repeat_fires_on_the_same_owners_second_buy(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=200)
    prices = {"AAA": pd.DataFrame({"Close": pd.Series(100.0, index=days)})}
    t = pd.DataFrame([dict(ticker="AAA", owner="o1", filed=days[10], code="P", price=100.0, shares=10),
                      dict(ticker="AAA", owner="o2", filed=days[15], code="P", price=100.0, shares=10),
                      dict(ticker="AAA", owner="o1", filed=days[30], code="P", price=100.0, shares=10),
                      dict(ticker="AAA", owner="o2", filed=days[150], code="P", price=100.0, shares=10)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_repeat(prices, buys=2, window=60)["AAA"]
    assert out.loc[days[30]] == 1 and out.sum() == 1         # o1 again 20 sessions later; o2's second is too late
    assert ff.insider_repeat(prices, buys=2, window=20)["AAA"].sum() == 0
    assert ff.insider_repeat(prices, buys=3, window=60)["AAA"].sum() == 0


def test_insider_market_stress_needs_a_falling_market_up_to_that_day(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=80)
    fall = pd.Series(100.0, index=days)
    fall.iloc[30:] = 90.0                                    # every stock -10% from day 30
    prices = {a: pd.DataFrame({"Close": fall.copy()}) for a in ("AAA", "BBB", "CCC")}
    t = pd.DataFrame([dict(ticker="AAA", owner="o1", filed=days[25], code="P", price=100.0, shares=10),
                      dict(ticker="BBB", owner="o2", filed=days[35], code="P", price=90.0, shares=10)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_market_stress(prices, buyers=1, drop=0.05)
    assert out["AAA"].sum() == 0                             # the fall came after AAA's buy
    assert out["BBB"].loc[days[35]] == 1 and out["BBB"].sum() == 1
    assert ff.insider_market_stress(prices, buyers=1, drop=0.15)["BBB"].sum() == 0


def test_insider_top_exec_filters_on_title_and_value(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=200)
    prices = {"AAA": pd.DataFrame({"Close": pd.Series(100.0, index=days)})}
    row = dict(ticker="AAA", code="P", price=100.0, shares=1000)
    t = pd.DataFrame([row | dict(owner="o1", filed=days[10], title="Director", value=900_000),
                      row | dict(owner="o2", filed=days[20], title="EVP, Chief Financial Officer", value=150_000),
                      row | dict(owner="o3", filed=days[150], title="President and CEO", value=60_000),
                      row | dict(owner="o3", filed=days[150], title="President and CEO", value=60_000)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    ceo = ff.insider_top_exec(prices, min_value=100_000, who="ceo")["AAA"]
    assert ceo.loc[days[150]] == 1 and ceo.sum() == 1        # two filings that day add up to 120k
    both = ff.insider_top_exec(prices, min_value=100_000, who="ceo_cfo")["AAA"]
    assert both.loc[days[20]] == 1 and both.loc[days[150]] == 1 and both.sum() == 2
    assert ff.insider_top_exec(prices, min_value=500_000, who="ceo_cfo")["AAA"].sum() == 0


def test_insider_consensus_counts_only_votes_already_fired(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=60)
    prices = {"AAA": pd.DataFrame({"Close": pd.Series(100.0, index=days)})}

    def one(i):
        return {"AAA": pd.Series((np.arange(60) == i).astype(int), days)}

    comp = {"fresh": one(10), "underwater": one(15), "top_exec": one(40),
            "clean": one(59), "after_earnings": {"AAA": pd.Series(0, days)}}
    monkeypatch.setattr(ff, "_insider_votes", lambda p: comp)
    out = ff.insider_consensus(prices, votes=2, window=10)["AAA"]
    assert out.loc[days[15]] == 1 and out.sum() == 1           # 10 and 15 agree; 40 is alone
    assert ff.insider_consensus(prices, votes=2, window=5)["AAA"].sum() == 0
    assert ff.insider_consensus(prices, votes=3, window=60)["AAA"].iloc[:40].sum() == 0


def test_insider_deep_value_needs_the_fall_before_the_buy(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=400)
    close = pd.Series(100.0, index=days)
    close.iloc[300:] = 60.0                                   # -40% from day 300
    prices = {"AAA": pd.DataFrame({"Close": close})}
    t = pd.DataFrame([dict(ticker="AAA", owner="o1", filed=days[250], code="P", price=100.0, shares=10),
                      dict(ticker="AAA", owner="o2", filed=days[350], code="P", price=60.0, shares=10)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_deep_value(prices, buyers=1, below=0.3)["AAA"]
    assert out.loc[days[350]] == 1 and out.sum() == 1
    assert ff.insider_deep_value(prices, buyers=1, below=0.5)["AAA"].sum() == 0


def test_insider_sector_laggard_compares_with_its_sector_up_to_that_day(monkeypatch):
    from algo import finder_families as ff
    from algo import wide

    days = pd.bdate_range("2021-01-04", periods=150)
    up = pd.Series(np.linspace(100, 130, 150), index=days)
    lag = up.copy()
    lag.iloc[100:] = up.iloc[100:] * 0.8                      # AAA falls 20% behind its peers from day 100
    prices = {"AAA": pd.DataFrame({"Close": lag}), "BBB": pd.DataFrame({"Close": up}),
              "CCC": pd.DataFrame({"Close": up.copy()})}
    t = pd.DataFrame([dict(ticker="AAA", owner="o1", filed=days[80], code="P", price=100.0, shares=10),
                      dict(ticker="AAA", owner="o2", filed=days[120], code="P", price=100.0, shares=10)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    monkeypatch.setattr(wide, "sectors", lambda: {"AAA": "Tech", "BBB": "Tech", "CCC": "Tech"})
    out = ff.insider_sector_laggard(prices, buyers=1, lag=0.10)["AAA"]
    assert out.loc[days[120]] == 1 and out.sum() == 1        # day 80: not behind yet
    assert ff.insider_sector_laggard(prices, buyers=1, lag=0.30)["AAA"].sum() == 0


def test_insider_low_vol_ranks_volatility_known_that_day(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=150)
    rng = np.random.default_rng(0)
    calm = pd.Series(100 * np.cumprod(1 + rng.normal(0, 0.002, 150)), index=days)
    wild = pd.Series(100 * np.cumprod(1 + rng.normal(0, 0.03, 150)), index=days)
    prices = {"CALM": pd.DataFrame({"Close": calm}), "WILD": pd.DataFrame({"Close": wild}),
              "MID": pd.DataFrame({"Close": pd.Series(100 * np.cumprod(1 + rng.normal(0, 0.01, 150)), days)})}
    t = pd.DataFrame([dict(ticker=a, owner="o" + a, filed=days[100], code="P", price=100.0, shares=10)
                      for a in prices])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_low_vol(prices, buyers=1, max_rank=0.4)
    assert out["CALM"].loc[days[100]] == 1 and out["WILD"].sum() == 0 and out["MID"].sum() == 0


def test_insider_high_short_uses_only_published_short_data(monkeypatch):
    """Same rule as insider_low_short, the other end of the ranking: day t reads ratios up to t-1."""
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-01", periods=60)
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in ("AAA", "BBB", "CCC", "DDD")}
    sig_day = days[40]
    monkeypatch.setattr(ff, "insider_cluster", lambda p, buyers, days: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    base = pd.DataFrame({"AAA": 0.1, "BBB": 0.2, "CCC": 0.3, "DDD": 0.4}, index=days)
    monkeypatch.setattr(wide, "load_short_volume", lambda: base)
    a = ff.insider_high_short(prices, min_rank=0.75)
    moved = base.copy()
    moved.loc[sig_day:, "AAA"] = 9.0  # AAA heavily shorted from the signal day on: not known yet
    monkeypatch.setattr(wide, "load_short_volume", lambda: moved)
    b = ff.insider_high_short(prices, min_rank=0.75)
    assert a["DDD"].loc[sig_day] == 1 and a["AAA"].loc[sig_day] == 0
    assert all(a[k].equals(b[k]) for k in a)


def test_insider_momentum_ranks_past_returns_only(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=200)
    up = pd.Series(np.linspace(100, 200, 200), index=days)
    flat = pd.Series(100.0, index=days)
    late = flat.copy()
    late.iloc[151:] = 300.0                                   # jumps after the signal day
    prices = {"UP": pd.DataFrame({"Close": up}), "FLAT": pd.DataFrame({"Close": flat}),
              "LATE": pd.DataFrame({"Close": late})}
    t = pd.DataFrame([dict(ticker=a, owner="o" + a, filed=days[150], code="P", price=100.0, shares=10)
                      for a in prices])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_momentum(prices, buyers=1, min_rank=0.9)
    assert out["UP"].loc[days[150]] == 1 and out["LATE"].sum() == 0 and out["FLAT"].sum() == 0


def test_insider_turn_waits_for_the_close_back_above_its_average(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=200)
    close = pd.Series(100.0, index=days)
    close.iloc[60:110] = np.linspace(99, 80, 50)              # falling: the insider buys on day 100
    close.iloc[110:] = 90.0                                   # day 110: back above the 20-day average
    prices = {"AAA": pd.DataFrame({"Close": close})}
    t = pd.DataFrame([dict(ticker="AAA", owner="o1", filed=days[100], code="P", price=81.0, shares=10)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_turn(prices, buyers=1, window=20)["AAA"]
    assert out.loc[days[110]] == 1 and out.sum() == 1
    assert ff.insider_turn(prices, buyers=1, window=5)["AAA"].sum() == 0    # the turn came too late
    later = close.copy()
    later.iloc[111:] = 50.0                                   # what happens after the signal changes nothing
    out2 = ff.insider_turn({"AAA": pd.DataFrame({"Close": later})}, buyers=1, window=20)["AAA"]
    assert out2.loc[days[110]] == 1 and out2.sum() == 1
    up = pd.Series(np.linspace(100, 150, 200), index=days)    # a cluster in a rising stock: not weakness
    assert ff.insider_turn({"AAA": pd.DataFrame({"Close": up})}, buyers=1, window=20)["AAA"].sum() == 0


def test_insider_accumulation_needs_a_heavy_up_day_after_the_buy(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2021-01-04", periods=120)
    close = pd.Series(100.0, index=days)
    vol = pd.Series(1000.0, index=days)
    close.iloc[85:] = 103.0                                   # day 85: up on 3x the usual volume
    vol.iloc[85] = 3000.0
    vol.iloc[70] = 5000.0                                     # heavy day before the buy: does not count
    prices = {"AAA": pd.DataFrame({"Close": close, "Volume": vol})}
    t = pd.DataFrame([dict(ticker="AAA", owner="o1", filed=days[80], code="P", price=100.0, shares=10)])
    monkeypatch.setattr(ff, "_insider", lambda code="P": t)
    out = ff.insider_accumulation(prices, buyers=1, volume=2.0)["AAA"]
    assert out.loc[days[85]] == 1 and out.sum() == 1
    assert ff.insider_accumulation(prices, buyers=1, volume=3.5)["AAA"].sum() == 0
    later = vol.copy()
    later.iloc[86:] = 100_000.0                               # future volume does not move the signal
    out2 = ff.insider_accumulation({"AAA": pd.DataFrame({"Close": close, "Volume": later})}, buyers=1,
                                   volume=2.0)["AAA"]
    assert out2.loc[days[85]] == 1 and out2.sum() == 1


def test_liquidity_sweep_needs_the_close_back_inside():
    from algo.finder_families import liquidity_sweep

    idx = pd.date_range("2025-01-02 14:00", periods=40, freq="h")
    df = pd.DataFrame({"Open": 100.0, "High": 101.0, "Low": 99.0, "Close": 100.0, "Volume": 1.0}, index=idx)
    df.iloc[20, df.columns.get_loc("Low")] = 97.0             # sweeps the 7-bar low (99), closes at 100
    df.iloc[30, df.columns.get_loc("Low")] = 97.0             # breaks the low and stays below: no signal
    df.iloc[30, df.columns.get_loc("Close")] = 98.0
    df.iloc[25, df.columns.get_loc("High")] = 103.0           # sweeps the highs, closes back at 100: sell
    s = liquidity_sweep({"X": df}, n=7)["X"]
    assert s.iloc[20] == 1 and s.iloc[25] == -1 and s.iloc[30] == 0
    assert set(s.iloc[:20]) == {0}


def test_insider_opportunistic_skips_the_yearly_routine_buyer(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2019-01-01", "2023-12-29")
    prices = {"AAA": pd.DataFrame({"Close": pd.Series(100.0, index=days)})}
    rows = [dict(ticker="AAA", owner="routine", filed=pd.Timestamp(f"{y}-03-10"), code="P", price=1.0, shares=1)
            for y in (2019, 2020, 2021, 2022)]              # every March: a plan, not news
    rows.append(dict(ticker="AAA", owner="fresh", filed=pd.Timestamp("2022-08-15"), code="P", price=1.0, shares=1))
    monkeypatch.setattr(ff, "_insider", lambda code="P": pd.DataFrame(rows))
    out = ff.insider_opportunistic(prices, buyers=1, years=2)["AAA"]
    hits = set(out.index[out == 1].strftime("%Y-%m-%d"))
    # 2019 and 2020 March buys have no 2-year history yet (opportunistic); 2021 and 2022 are routine
    assert hits == {"2019-03-11", "2020-03-10", "2022-08-15"}


def test_overnight_momentum_uses_past_opens_and_closes_only():
    from algo.finder_families import overnight_momentum

    days = pd.bdate_range("2024-01-01", periods=80)
    flat = pd.Series(100.0, index=days)
    gaps = pd.DataFrame({"Open": flat * 1.0, "Close": flat})
    up = gaps.copy()
    up["Open"] = np.r_[100.0, [101.0] * 79]               # opens 1% above the previous close every day
    up["Close"] = 100.0
    prices = {"UP": up, "FLAT": gaps, "F2": gaps.copy(), "F3": gaps.copy()}
    full = overnight_momentum(prices, lookback=20, top=0.25)
    assert full["UP"].sum() > 0 and full["FLAT"].sum() == 0
    part = overnight_momentum({a: df.iloc[:60] for a, df in prices.items()}, lookback=20, top=0.25)
    assert (full["UP"].iloc[:60] == part["UP"]).all()


def test_insider_opportunistic_low_short_reads_published_short_data_only(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-01", periods=60)
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in ("AAA", "BBB", "CCC", "DDD")}
    sig_day = days[40]
    monkeypatch.setattr(ff, "insider_opportunistic", lambda p, buyers, years: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    base = pd.DataFrame({"AAA": 0.1, "BBB": 0.2, "CCC": 0.3, "DDD": 0.4}, index=days)
    monkeypatch.setattr(wide, "load_short_volume", lambda: base)
    a = ff.insider_opportunistic_low_short(prices, max_rank=0.25)
    moved = base.copy()
    moved.loc[sig_day:, "AAA"] = 9.0  # AAA heavily shorted from the signal day on: not known yet
    monkeypatch.setattr(wide, "load_short_volume", lambda: moved)
    b = ff.insider_opportunistic_low_short(prices, max_rank=0.25)
    assert a["AAA"].loc[sig_day] == 1 and a["DDD"].loc[sig_day] == 0
    assert all(a[k].equals(b[k]) for k in a)


def test_insider_opportunistic_exec_keeps_the_boss_breaking_the_habit(monkeypatch):
    from algo import finder_families as ff

    days = pd.bdate_range("2019-01-01", "2023-12-29")
    prices = {"AAA": pd.DataFrame({"Close": pd.Series(100.0, index=days)})}
    row = lambda owner, title, d: dict(ticker="AAA", owner=owner, title=title, filed=pd.Timestamp(d),  # noqa: E731
                                       code="P", price=1.0, shares=1)
    rows = [row("ceo", "Chief Executive Officer", f"{y}-03-10") for y in (2019, 2020, 2021)]  # yearly plan
    rows += [row("ceo", "Chief Executive Officer", "2022-08-15"),                              # breaks it
             row("dir", "Director", "2022-09-15")]                                             # not the boss
    monkeypatch.setattr(ff, "_insider", lambda code="P": pd.DataFrame(rows))
    out = ff.insider_opportunistic_exec(prices, who="ceo", years=1)["AAA"]
    assert set(out.index[out == 1].strftime("%Y-%m-%d")) == {"2019-03-11", "2022-08-15"}


def test_insider_opportunistic_wave_counts_earlier_buys_of_the_same_sector_only(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2022-01-03", periods=60)
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in ("A1", "A2", "A3", "B1")}
    on = {"A1": days[10], "A2": days[15], "A3": days[20], "B1": days[12]}
    monkeypatch.setattr(ff, "insider_opportunistic", lambda p, buyers, years: {
        a: pd.Series((p[a].index == on[a]).astype(int), p[a].index) for a in p})
    monkeypatch.setattr(wide, "sectors", lambda: {"A1": "Ind", "A2": "Ind", "A3": "Ind", "B1": "Tech"})
    out = ff.insider_opportunistic_wave(prices, companies=3, window=30)
    assert out["A3"].loc[days[20]] == 1                       # the third company of the wave
    assert out["A1"].sum() == 0 and out["A2"].sum() == 0      # A3's later buy is not known then
    assert out["B1"].sum() == 0                               # another sector does not count


def test_momentum_low_short_reads_published_short_data_only(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-01", periods=60)
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in ("AAA", "BBB", "CCC", "DDD")}
    sig_day = days[40]
    monkeypatch.setattr(ff, "momentum_12_1", lambda p, top: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    base = pd.DataFrame({"AAA": 0.1, "BBB": 0.2, "CCC": 0.3, "DDD": 0.4}, index=days)
    monkeypatch.setattr(wide, "load_short_volume", lambda: base)
    a = ff.momentum_low_short(prices, top=0.1, max_rank=0.25)
    moved = base.copy()
    moved.loc[sig_day:, "AAA"] = 9.0  # AAA heavily shorted from the signal day on: not known yet
    monkeypatch.setattr(wide, "load_short_volume", lambda: moved)
    b = ff.momentum_low_short(prices, top=0.1, max_rank=0.25)
    assert a["AAA"].loc[sig_day] == 1 and a["DDD"].loc[sig_day] == 0
    assert all(a[k].equals(b[k]) for k in a)


def test_insider_wave_low_short_reads_published_short_data_only(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-01", periods=60)
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in ("AAA", "BBB", "CCC", "DDD")}
    sig_day = days[40]
    monkeypatch.setattr(ff, "insider_sector_wave", lambda p, buyers, companies: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    base = pd.DataFrame({"AAA": 0.1, "BBB": 0.2, "CCC": 0.3, "DDD": 0.4}, index=days)
    monkeypatch.setattr(wide, "load_short_volume", lambda: base)
    a = ff.insider_wave_low_short(prices, companies=3, max_rank=0.25)
    moved = base.copy()
    moved.loc[sig_day:, "AAA"] = 9.0  # AAA heavily shorted from the signal day on: not known yet
    monkeypatch.setattr(wide, "load_short_volume", lambda: moved)
    b = ff.insider_wave_low_short(prices, companies=3, max_rank=0.25)
    assert a["AAA"].loc[sig_day] == 1 and a["DDD"].loc[sig_day] == 0
    assert all(a[k].equals(b[k]) for k in a)


def test_insider_stress_low_short_reads_published_short_data_only(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2021-01-01", periods=60)
    prices = {a: pd.DataFrame({"Close": 10.0}, index=days) for a in ("AAA", "BBB", "CCC", "DDD")}
    sig_day = days[40]
    monkeypatch.setattr(ff, "insider_sector_stress", lambda p, buyers, drop: {
        a: pd.Series((p[a].index == sig_day).astype(int), p[a].index) for a in p})
    base = pd.DataFrame({"AAA": 0.1, "BBB": 0.2, "CCC": 0.3, "DDD": 0.4}, index=days)
    monkeypatch.setattr(wide, "load_short_volume", lambda: base)
    a = ff.insider_stress_low_short(prices, drop=0.1, max_rank=0.25)
    moved = base.copy()
    moved.loc[sig_day:, "AAA"] = 9.0  # AAA heavily shorted from the signal day on: not known yet
    monkeypatch.setattr(wide, "load_short_volume", lambda: moved)
    b = ff.insider_stress_low_short(prices, drop=0.1, max_rank=0.25)
    assert a["AAA"].loc[sig_day] == 1 and a["DDD"].loc[sig_day] == 0
    assert all(a[k].equals(b[k]) for k in a)


def test_sector_reversal_buys_the_drop_against_its_sector_on_fridays_with_past_closes_only(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2024-01-01", periods=60)
    f = max(i for i, d in enumerate(days) if d.dayofweek == 4 and i < 55)
    drop = pd.Series(100.0, index=days)
    drop.iloc[f - 4:] = np.linspace(98, 90, 5).tolist() + [90.0] * (len(days) - f - 1)
    flat = pd.Series(100.0, index=days)
    prices = {"I1": pd.DataFrame({"Close": drop}), "I2": pd.DataFrame({"Close": flat}),
              "T1": pd.DataFrame({"Close": drop}), "T2": pd.DataFrame({"Close": drop * 1.0})}
    monkeypatch.setattr(wide, "sectors", lambda: {"I1": "Ind", "I2": "Ind", "T1": "Tech", "T2": "Tech"})
    full = ff.sector_reversal(prices, lookback=5, bottom=0.25)
    # I1 fell 10% while its sector's median fell 5%; T1 fell as much as its whole sector: no signal
    assert full["I1"].loc[days[f]] == 1 and full["I1"].sum() == 1
    assert full["T1"].sum() == 0 and full["I2"].sum() == 0
    part = ff.sector_reversal({a: df.iloc[:f + 1] for a, df in prices.items()}, lookback=5, bottom=0.25)
    assert all((full[a].iloc[:f + 1] == part[a]).all() for a in prices)


def test_sector_washout_buys_the_fallen_sector_on_its_first_bounce_with_past_closes_only(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2024-01-01", periods=120)
    fall = np.r_[np.full(30, 100.0), np.linspace(100, 75, 60), np.linspace(75, 75, 10), np.linspace(75.5, 80, 20)]
    prices = {"I1": pd.DataFrame({"Close": pd.Series(fall, index=days)}),
              "I2": pd.DataFrame({"Close": pd.Series(fall * 1.02, index=days)}),
              "T1": pd.DataFrame({"Close": pd.Series(100.0 + np.sin(np.arange(120)), index=days)})}
    monkeypatch.setattr(wide, "sectors", lambda: {"I1": "Ind", "I2": "Ind", "T1": "Tech"})
    full = ff.sector_washout(prices, drop=0.15, bounce=5)
    hit = full["I1"].index[full["I1"] == 1]
    assert len(hit) == 1 and hit[0] == days[100] and full["I2"].loc[hit[0]] == 1 and full["T1"].sum() == 0
    cut = days.get_loc(hit[0]) + 1
    part = ff.sector_washout({a: df.iloc[:cut] for a, df in prices.items()}, drop=0.15, bounce=5)
    assert all((full[a].iloc[:cut] == part[a]).all() for a in prices)


def test_insider_stress_leader_keeps_the_stocks_ahead_of_their_sector(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2024-01-01", periods=100)
    t = np.arange(100)
    prices = {"LEAD": pd.DataFrame({"Close": pd.Series(100 - 0.05 * t, index=days)}),
              "LAG": pd.DataFrame({"Close": pd.Series(100 - 0.3 * t, index=days)}),
              "MID": pd.DataFrame({"Close": pd.Series(100 - 0.2 * t, index=days)})}
    on = days[90]
    monkeypatch.setattr(ff, "insider_sector_stress", lambda p, buyers, drop: {
        a: pd.Series((p[a].index == on).astype(int), p[a].index) for a in p})
    monkeypatch.setattr(wide, "sectors", lambda: {"LEAD": "Ind", "LAG": "Ind", "MID": "Ind"})
    out = ff.insider_stress_leader(prices, drop=0.1, lead=0.0)
    assert out["LEAD"].loc[on] == 1 and out["LAG"].sum() == 0 and out["MID"].sum() == 0
    part = ff.insider_stress_leader({a: df.iloc[:91] for a, df in prices.items()}, drop=0.1, lead=0.0)
    assert all((out[a].iloc[:91] == part[a]).all() for a in prices)


def test_sector_momentum_buys_the_strong_sector_and_uses_past_closes_only(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2024-01-01", periods=320)
    up = pd.Series(100 * 1.002 ** np.arange(320), index=days)
    down = pd.Series(100 * 0.999 ** np.arange(320), index=days)
    prices = {"U1": pd.DataFrame({"Close": up}), "U2": pd.DataFrame({"Close": up * 1.1}),
              "D1": pd.DataFrame({"Close": down}), "D2": pd.DataFrame({"Close": down * 0.9})}
    monkeypatch.setattr(wide, "sectors", lambda: {"U1": "Tech", "U2": "Tech", "D1": "Energy", "D2": "Energy"})
    full = ff.sector_momentum(prices, top=1, ma=100)
    assert full["U1"].sum() > 0 and full["D1"].sum() == 0
    month_ends = full["U1"].index[full["U1"] == 1]
    assert all(d.month != (d + pd.offsets.BDay(1)).month for d in month_ends[:-1])  # month ends (+ the data's end)
    part = ff.sector_momentum({a: df.iloc[:280] for a, df in prices.items()}, top=1, ma=100)
    assert (full["U1"].iloc[:279] == part["U1"].iloc[:279]).all()


def test_insider_sector_stress_needs_the_sector_down_before_the_signal(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2024-01-01", periods=120)
    fall = pd.Series(np.r_[[100.0] * 40, np.linspace(100, 80, 80)], index=days)   # the sector falls from day 40
    flat = pd.Series(100.0, index=days)
    prices = {"S1": pd.DataFrame({"Close": fall}), "S2": pd.DataFrame({"Close": fall * 1.01}),
              "T1": pd.DataFrame({"Close": flat}), "T2": pd.DataFrame({"Close": flat})}
    on = {"S1": days[50], "S2": days[110], "T1": days[110], "T2": days[60]}
    monkeypatch.setattr(ff, "insider_cluster", lambda p, buyers, days: {
        a: pd.Series((p[a].index == on[a]).astype(int), p[a].index) for a in p})
    monkeypatch.setattr(wide, "sectors", lambda: {"S1": "Ind", "S2": "Ind", "T1": "Tech", "T2": "Tech"})
    out = ff.insider_sector_stress(prices, buyers=1, drop=0.10)
    assert out["S2"].loc[days[110]] == 1          # sector down about 20% over 60 sessions
    assert out["S1"].sum() == 0                   # day 50: down only ~2.5% so far
    assert out["T1"].sum() == 0 and out["T2"].sum() == 0
    part = ff.insider_sector_stress({a: df.iloc[:111] for a, df in prices.items()}, buyers=1, drop=0.10)
    assert part["S2"].loc[days[110]] == 1         # the same with no later prices


def test_momentum_low_vol_keeps_the_steady_winner_and_past_closes_only():
    from algo.finder_families import momentum_low_vol

    days = pd.bdate_range("2024-01-01", periods=320)
    t = np.arange(320)
    steady = pd.Series(100 * 1.002 ** t, index=days)
    jumpy = pd.Series(100 * 1.002 ** t * (1 + 0.05 * np.sin(t)), index=days)
    prices = {"STEADY": pd.DataFrame({"Close": steady}), "JUMPY": pd.DataFrame({"Close": jumpy * 1.3}),
              "FLAT1": pd.DataFrame({"Close": pd.Series(100.0, index=days)}),
              "FLAT2": pd.DataFrame({"Close": pd.Series(100.0, index=days) * (1 + 0.04 * np.sin(t))})}
    full = momentum_low_vol(prices, top=0.5, max_vol=0.5)
    assert full["STEADY"].sum() > 0 and full["JUMPY"].sum() == 0
    part = momentum_low_vol({a: df.iloc[:280] for a, df in prices.items()}, top=0.5, max_vol=0.5)
    assert (full["STEADY"].iloc[:279] == part["STEADY"].iloc[:279]).all()


def test_insider_wave_stress_needs_the_sector_down_before_the_wave(monkeypatch):
    from algo import finder_families as ff, wide

    days = pd.bdate_range("2024-01-01", periods=120)
    fall = pd.Series(np.r_[[100.0] * 40, np.linspace(100, 80, 80)], index=days)
    prices = {"S1": pd.DataFrame({"Close": fall}), "S2": pd.DataFrame({"Close": fall * 1.01}),
              "T1": pd.DataFrame({"Close": pd.Series(100.0, index=days)})}
    on = {"S1": days[50], "S2": days[110], "T1": days[110]}
    monkeypatch.setattr(ff, "insider_sector_wave", lambda p, buyers, companies: {
        a: pd.Series((p[a].index == on[a]).astype(int), p[a].index) for a in p})
    monkeypatch.setattr(wide, "sectors", lambda: {"S1": "Ind", "S2": "Ind", "T1": "Tech"})
    out = ff.insider_wave_stress(prices, companies=3, drop=0.10)
    assert out["S2"].loc[days[110]] == 1 and out["S1"].sum() == 0 and out["T1"].sum() == 0
    part = ff.insider_wave_stress({a: df.iloc[:111] for a, df in prices.items()}, companies=3, drop=0.10)
    assert part["S2"].loc[days[110]] == 1


def test_momentum_pullback_buys_a_winner_s_dip_on_fridays_with_past_closes_only():
    from algo.finder_families import momentum_pullback

    days = pd.bdate_range("2024-01-01", periods=320)
    t = np.arange(320)
    win = 100 * 1.003 ** t
    win[-8:-3] *= 0.93                                          # a dip in the last weeks
    prices = {"WIN": pd.DataFrame({"Close": pd.Series(win, index=days)}),
              "LOSE": pd.DataFrame({"Close": pd.Series(100 * 0.998 ** t, index=days)}),
              "FLAT": pd.DataFrame({"Close": pd.Series(100.0 + np.sin(t), index=days)}),
              "UP": pd.DataFrame({"Close": pd.Series(100 * 1.001 ** t, index=days)})}
    full = momentum_pullback(prices, top=0.5, bottom=0.25)
    hits = full["WIN"].index[full["WIN"] == 1]
    assert len(hits) and all(d.dayofweek == 4 for d in hits)
    part = momentum_pullback({a: df.iloc[:300] for a, df in prices.items()}, top=0.5, bottom=0.25)
    assert (full["WIN"].iloc[:300] == part["WIN"]).all()
