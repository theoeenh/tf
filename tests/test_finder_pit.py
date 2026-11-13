"""The finder after 2026-11-12: research on the members of each day (not today's list applied to the past),
a luck bar measured on the tries' own weekly returns, and every old try scored again."""
import json
from dataclasses import asdict

import numpy as np
import pandas as pd
import pytest

from algo import finder as F
from algo import finder_families as FF
from algo import luck, wide, wide_pit
from algo import wide_pit as P

from test_wide_pit import table  # noqa: F401  (AAA always in the S&P 500, GONE left 1 Mar 2020, LATE joined later)


def daily(days, close=50.0, volume=1000.0):
    c = np.full(len(days), close) if np.isscalar(close) else np.asarray(close, float)
    return pd.DataFrame({"Open": c, "High": c + 0.5, "Low": c - 0.5, "Close": c, "Volume": volume}, index=days)


# ------------------------------------------------------------------ members of the day

def test_research_signals_count_only_while_a_member_the_runner_keeps_todays_list(table, monkeypatch):  # noqa: F811
    days = pd.bdate_range("2019-06-03", "2021-06-30")
    gone = wide.closing_bars(daily(days[days <= "2020-02-14"]), until=days[-1])     # bought out on 14 Feb 2020
    prices = {"AAA": daily(days), "GONE": gone, "LATE": daily(days)}
    seen = {}

    def every_day(p):
        seen.update({a: df.index[-1] for a, df in p.items()})
        return {a: pd.Series(1, df.index) for a, df in p.items()}
    monkeypatch.setitem(FF.WIDE_FAMILIES, "every_day", (every_day, {}))
    rule = dict(F.DAILY_RULES["hold 5 days"])
    big = F.Candidate("every_day", {}, rule, trend=False, assets="all", data="daily500")
    sig = F.signals(big, prices, pit=True)
    assert set(sig) == {"AAA", "GONE"}                                   # LATE was never in the S&P 500
    assert sig["AAA"].all()
    assert sig["GONE"][sig["GONE"].index <= "2020-02-14"].all()
    assert sig["GONE"][sig["GONE"].index > "2020-02-14"].sum() == 0      # no signal on its closing bars
    assert seen["GONE"] == pd.Timestamp("2020-02-14")                    # the strategy never even saw them
    assert len(sig["GONE"]) == len(gone)                                 # but the backtest has them, to exit
    both = F.signals(F.Candidate("every_day", {}, rule, trend=False, assets="sp1500", data="daily500"), prices, pit=True)
    assert both["LATE"][both["LATE"].index < "2020-06-01"].sum() == 0    # not before the list showed it
    assert both["LATE"][both["LATE"].index >= "2020-06-01"].all()
    # the trading accounts' runner (pit=False) trades today's list, whatever the day: unchanged
    monkeypatch.setattr(wide, "_table", lambda: pd.DataFrame({"symbol": ["AAA", "LATE"], "index": ["sp500", "sp400"],
                                                             "sector": ["Energy", "Energy"]}))
    live = F.signals(F.Candidate("every_day", {}, rule, trend=False, assets="sp1500", data="daily500"), prices)
    assert set(live) == {"AAA", "LATE"} and live["LATE"].all()


def test_without_the_history_table_nothing_changes(monkeypatch):
    days = pd.bdate_range("2020-01-01", periods=30)
    monkeypatch.setattr(wide, "_table", lambda: pd.DataFrame({"symbol": ["AAA"], "index": ["sp500"], "sector": ["Energy"]}))
    monkeypatch.setitem(FF.WIDE_FAMILIES, "every_day", (lambda p: {a: pd.Series(1, df.index) for a, df in p.items()}, {}))
    c = F.Candidate("every_day", {}, dict(F.DAILY_RULES["hold 5 days"]), trend=False, assets="all", data="daily500")
    assert not F.point_in_time("daily500")
    assert F.signals(c, {"AAA": daily(days), "ZZZ": daily(days)}, pit=True).keys() == {"AAA"}
    assert wide.sectors() == {"AAA": "Energy"}


def test_a_stock_that_stops_trading_is_paid_out_or_written_off():
    days = pd.bdate_range("2019-01-01", periods=300)
    bought = wide.closing_bars(daily(days, 80.0))
    assert len(bought) == 300 + wide.TAIL and (bought["Close"].iloc[300:] == 80.0).all()
    assert (bought["Volume"].iloc[300:] == 0).all() and bought.index[300] > days[-1]
    crash = np.r_[np.full(40, 500.0), np.linspace(500, 268, 259), 106.0]  # SVB: halted the day after -60%
    assert (wide.closing_bars(daily(days, crash))["Close"].iloc[300:] == wide.WORTHLESS).all()
    penny = np.linspace(5.0, 0.4, 300)
    assert (wide.closing_bars(daily(days, penny))["Close"].iloc[300:] == wide.WORTHLESS).all()
    # bought out in a market crash (AK Steel, March 2020: -43% in a month, -45% in a year): paid, not written off
    merger = np.r_[np.full(280, 2.9), np.linspace(2.8, 1.59, 20)]
    assert wide.closing_bars(daily(days, merger))["Close"].iloc[-1] == pytest.approx(1.59)
    slow = np.linspace(100.0, 70.0, 300)                                 # a weak stock bought at a low price
    assert wide.closing_bars(daily(days, slow))["Close"].iloc[-1] == pytest.approx(70.0)
    # a stock that only left the indexes and still trades is never written off, whatever its price
    assert wide.closing_bars(daily(days, penny), gone=False)["Close"].iloc[-1] == pytest.approx(0.4)
    assert wide.closing_bars(daily(days, 80.0), until=days[-1] + pd.Timedelta(days=7)).index[-1] <= days[-1] + pd.Timedelta(days=7)


def test_research_prices_cover_every_member_ever_over_its_own_days(table, tmp_path, monkeypatch):  # noqa: F811
    monkeypatch.setattr(wide, "WIDE_DIR", tmp_path)
    all_days = pd.bdate_range("2016-01-04", "2021-06-30")
    rows = []
    for sym, days in (("AAA", all_days), ("GONE", all_days[all_days <= "2020-02-14"]),
                      ("LATE", all_days[all_days >= "2019-01-02"]), ("NOBODY", all_days)):
        rows.append(daily(days).rename_axis("date").reset_index().assign(symbol=sym))
    # DROPPED left the S&P 500 on 1 March 2020 at 60 cents and still trades today: not a failure
    h = pd.concat([P.history(), pd.DataFrame([dict(symbol="DROPPED", index="sp500", start=pd.Timestamp("2015-12-01"),
                                                   end=pd.Timestamp("2020-03-01"), sector="Energy")])])
    h.to_csv(P.PATH, index=False)
    rows.append(daily(all_days, 0.6).rename_axis("date").reset_index().assign(symbol="DROPPED"))
    pd.concat(rows).to_csv(tmp_path / "daily.csv.gz", index=False)
    p = wide.load_daily_pit()
    assert set(p) == {"AAA", "GONE", "LATE", "DROPPED"}                  # NOBODY was never a member
    left = p["DROPPED"]
    assert (left["Volume"] > 0).sum() > 0 and left["Close"].iloc[-1] == pytest.approx(0.6)   # its last price
    assert len(left[(left["Volume"] > 0) & (left.index >= "2020-03-01")]) == P.GRACE
    assert p["AAA"].index[-1] == all_days[-1] and (p["AAA"]["Volume"] > 0).all()
    real = p["GONE"][p["GONE"]["Volume"] > 0]
    assert real.index[-1] == pd.Timestamp("2020-02-14") and len(p["GONE"]) == len(real) + wide.TAIL
    assert p["LATE"].index[0] == pd.Timestamp("2019-01-02")              # warm-up before it joined, as far as bars go
    assert set(wide.research_symbols()) >= {"AAA", "GONE", "LATE"}


def test_a_stock_with_no_bars_outside_the_vault_is_left_out_not_passed_on_empty(table, monkeypatch):  # noqa: F811
    """2026-11-12, first run on real prices: a company listed after the vault began came through as an
    empty table and stopped the run."""
    before = pd.bdate_range("2024-01-02", "2025-12-31")
    only_vault = pd.bdate_range("2025-09-01", "2025-12-31")
    barely = pd.bdate_range("2025-06-02", "2025-12-31")                  # 21 sessions before the vault
    monkeypatch.setattr(wide, "load_daily_pit", lambda: {"AAA": daily(before), "NEWCO": daily(only_vault),
                                                         "LATE": daily(barely)})
    p = F.load(data="daily500")
    assert set(p) == {"AAA"} and p["AAA"].index[-1] < pd.Timestamp(F.VAULT_START)
    assert set(F.load(include_vault=True, data="daily500")) == {"AAA", "NEWCO", "LATE"}


# ------------------------------------------------------------------ the luck check in the registry

def _registry(tmp_path, monkeypatch, tries: dict, extra_without_returns: int = 0):
    """A registry whose tries have these weekly returns stored (id -> array), plus tries without any."""
    monkeypatch.setattr(F, "OUT", tmp_path)
    F._returns.clear(), F._bars.clear(), F.LUCK.clear()
    weeks = pd.date_range("2017-01-06", periods=len(next(iter(tries.values()))), freq=luck.WEEK)
    luck.save(tmp_path / "returns", "daily500", "t", {k: pd.Series(v, weeks) for k, v in tries.items()})
    cand = json.dumps(asdict(F.Candidate("x", {}, {}, data="daily500")))
    ids = list(tries) + [f"old{k}" for k in range(extra_without_returns)]
    return pd.DataFrame({"id": ids, "candidate": cand, "s_sr_daily": 0.05, "s_n_days": 1500, "s_skew": 0.0,
                         "s_kurt": 3.0, "s_ic": 0.1, "s_icir": 0.3, "months": 40})


def test_luck_bar_is_measured_on_the_stored_returns_and_copies_do_not_raise_it(tmp_path, monkeypatch):
    rng = np.random.default_rng(7)
    ideas = {f"i{k}": rng.normal(0, 0.01, 313) for k in range(30)}
    ideas["skill"] = rng.normal(0.0035, 0.01, 313)
    base = F.score(_registry(tmp_path, monkeypatch, ideas)).set_index("id")
    assert base.at["skill", "s_dsr"] >= 0.90 and base.at["skill", "s_h_t"] > 5
    assert (base.drop("skill")["s_dsr"] < 0.90).all() and F.LUCK["tries"] == 31
    n_base = F.LUCK["independent_tries"]
    copies = ideas | {f"c{k}": ideas[f"i{k % 30}"] + rng.normal(0, 0.0005, 313) for k in range(300)}
    many = F.score(_registry(tmp_path / "b", monkeypatch, copies)).set_index("id")
    assert F.LUCK["tries"] == 331 and F.LUCK["independent_tries"] < 2 * n_base     # 331 tries, about 30 ideas
    assert many.at["skill", "s_dsr"] == pytest.approx(base.at["skill", "s_dsr"], abs=0.05)
    fresh = ideas | {f"n{k}": rng.normal(0, 0.01, 313) for k in range(300)}
    new = F.score(_registry(tmp_path / "c", monkeypatch, fresh)).set_index("id")
    assert F.LUCK["independent_tries"] > 5 * n_base                      # 300 new ideas raise the bar for all
    assert new.at["skill", "s_dsr"] < base.at["skill", "s_dsr"]


def test_tries_without_stored_returns_still_count_and_cannot_pass_on_the_easy_bar(tmp_path, monkeypatch):
    rng = np.random.default_rng(8)
    tries = {f"i{k}": rng.normal(0, 0.01, 313) for k in range(20)} | {"skill": rng.normal(0.003, 0.01, 313)}
    alone = F.score(_registry(tmp_path, monkeypatch, tries)).set_index("id")
    bar_alone = F.LUCK["bar_t"]
    mixed = F.score(_registry(tmp_path / "b", monkeypatch, tries, extra_without_returns=400)).set_index("id")
    assert F.LUCK["without_returns"] == 400 and F.LUCK["bar_t"] > bar_alone + 0.8
    assert mixed.at["skill", "s_dsr"] < alone.at["skill", "s_dsr"]
    assert mixed.loc[[f"old{k}" for k in range(5)], "s_dsr"].isna().all()   # no returns, no verdict
    assert "search: deflated Sharpe >= 0.90" in mixed.at["old0", "failed"]


def test_only_tries_that_could_pass_set_the_bar(tmp_path, monkeypatch):
    """2026-11-12, the first full run: strategies with one to thirty trades set the bar. One lucky week
    counted several times in a replay looks like a t-statistic of 5; no strategy can show that, and a
    try with fewer than 100 signals fails the first check whatever it earned."""
    rng = np.random.default_rng(9)
    real = {f"i{k}": rng.normal(0, 0.01, 313) for k in range(30)}
    one_trade = {}
    for k in range(300):                                                # one big week each, nothing else
        x = np.zeros(313)
        x[rng.integers(0, 313)] = 0.05
        one_trade[f"s{k}"] = x
    reg = _registry(tmp_path, monkeypatch, real).assign(s_events=500)
    F.score(reg)
    bar = F.LUCK["bar_t"]
    both = _registry(tmp_path / "b", monkeypatch, real | one_trade)
    F.score(both.assign(s_events=[500] * 30 + [1] * 300))
    assert F.LUCK["bar_t"] == pytest.approx(bar) and F.LUCK["tries"] == 330 and F.LUCK["could_pass"] == 30
    F._bars.clear()
    F.score(both.assign(s_events=500))                                  # had they traded enough, they would count
    assert F.LUCK["bar_t"] > bar + 0.5 and F.LUCK["could_pass"] == 330
    waiting = _registry(tmp_path / "c", monkeypatch, real, extra_without_returns=50)
    F.score(waiting.assign(s_events=[500] * 30 + [500] * 20 + [1] * 30))
    assert F.LUCK["without_returns"] == 20                              # only those that could pass raise the bar


def test_no_returns_stored_at_all_means_the_old_formula(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "OUT", tmp_path)
    F._returns.clear(), F._bars.clear(), F.LUCK.clear()
    cand = json.dumps(asdict(F.Candidate("x", {}, {}, data="daily500")))
    reg = pd.DataFrame({"id": [f"a{k}" for k in range(50)], "candidate": cand,
                        "s_sr_daily": np.linspace(-0.02, 0.06, 50), "s_n_days": 1500, "s_skew": 0.0, "s_kurt": 3.0,
                        "s_ic": 0.1, "s_icir": 0.3, "months": 40})
    out = F.score(reg)
    want = F.deflated_sharpe(0.06, 1500, 0.0, 3.0, reg["s_sr_daily"].tolist(), n_trials=50)
    assert out["s_dsr"].iloc[-1] == pytest.approx(want) and not F.LUCK
    assert F.luck_lines(out)[0].startswith("No weekly returns stored yet")


# ------------------------------------------------------------------ scoring every old try again

@pytest.fixture
def small_world(tmp_path, monkeypatch):
    """Three assets, six months of hourly bars, short search / validation windows: a real evaluate() in
    a second or two."""
    rng = np.random.default_rng(11)
    idx = pd.date_range("2024-01-01", "2024-06-30", freq="h")
    prices = {}
    for a in ("NVDA", "AAPL", "MSFT"):
        c = 100 * np.exp(np.cumsum(rng.normal(0.0001, 0.004, len(idx))))
        prices[a] = pd.DataFrame({"Open": c, "High": c * 1.002, "Low": c * 0.998, "Close": c, "Volume": 1e5}, idx)
    monkeypatch.setattr(F, "OUT", tmp_path)
    monkeypatch.setattr(F, "PERIODS", F.PERIODS | {"hourly": (("2024-01-10", "2024-04-30 23:59"),
                                                              ("2024-05-01", "2024-06-20 23:59"))})
    monkeypatch.setattr(F, "load", lambda include_vault=False, data="hourly": prices)
    F._returns.clear(), F._bars.clear(), F.LUCK.clear(), F._DATA.clear(), F._bench.clear()
    return prices


def test_a_run_stores_each_try_with_its_weekly_hedged_returns(small_world, tmp_path):
    rule = dict(F.RULES["target 2R, out in 12 bars"])
    cands = [F.Candidate("donchian", {"n": 20, "trend_ma": 100}, rule, trend=False),
             F.Candidate("rsi2", {"rsi_n": 2, "threshold": 10.0, "trend_ma": 100}, rule, trend=False)]
    reg = F.run(cands)
    assert len(reg) == 2 and reg["universe"].eq("fixed list").all() and reg["s_beta"].notna().all()
    store = luck.load(tmp_path / "returns", "hourly")
    assert set(store.columns) == {c.id for c in cands} and 15 <= len(store) <= 18     # the search window's weeks
    assert reg["s_h_t"].notna().all() and F.LUCK["tries"] == 2 and F.LUCK["without_returns"] == 0
    assert (tmp_path / "luck.json").exists() and "could pass at all" in (tmp_path / "report.md").read_text()


def test_rescore_scores_every_old_try_again_and_loses_none(small_world, tmp_path, monkeypatch):
    rule = dict(F.RULES["target 2R, out in 12 bars"])
    cands = [F.Candidate("donchian", {"n": n, "trend_ma": 100}, rule, trend=False) for n in (20, 30, 40)]
    broken = F.Candidate("no_such_family", {}, rule, trend=False)       # cannot be scored again
    old = pd.DataFrame([{"id": c.id, "label": c.label(), "family": c.family, "candidate": json.dumps(asdict(c)),
                         "s_events": 500, "s_ic": 9.9, "s_icir": 9.9, "s_avg_r": 9.9, "s_rand_avg_r": 0.0,
                         "s_return": 9.9, "s_sr_daily": 0.5, "s_n_days": 100, "s_skew": 0.0, "s_kurt": 3.0,
                         "v_ic": 9.9, "v_avg_r": 9.9, "v_return": 9.9, "months": 40} for c in cands + [broken]])
    old.to_csv(tmp_path / "registry.csv", index=False)
    for shard in (0, 1):
        F.rescore(shard, 2)
    parts = [pd.read_csv(p) for p in sorted((tmp_path / "rescore").glob("part-*/registry.csv"))]
    assert sum(len(p) for p in parts) == 3                              # each try in exactly one slice
    reg = F.rescore_merge().set_index("id")
    assert list(reg.index) == list(old["id"])                           # all four, in the old order
    assert (reg.loc[[c.id for c in cands], "universe"] == "fixed list").all()
    assert (reg.loc[[c.id for c in cands], "s_ic"] != 9.9).all()        # really scored again
    assert reg.at[broken.id, "universe"] == "not scored again" and reg.at[broken.id, "s_ic"] == 9.9
    assert pd.isna(reg.at[broken.id, "s_dsr"]) and "deflated Sharpe" in reg.at[broken.id, "failed"]   # cannot pass
    assert F.LUCK["tries"] == 4 and F.LUCK["without_returns"] == 1
    cmp_ = pd.read_csv(tmp_path / "rescore_compare.csv")
    assert len(cmp_) == 4 and {"s_ic_old", "s_ic_new", "gates_passed_old", "gates_passed_new"} <= set(cmp_.columns)
    again = F.rescore(0, 2)                                             # a restart finds nothing left to do
    assert len(pd.read_csv(again / "registry.csv")) == len(parts[0])


def test_vault_tests_wait_while_a_hold_is_set(tmp_path, monkeypatch):
    from algo import forward, notify

    reg = pd.DataFrame({"id": ["g1"], "label": ["graduate"], "gates_passed": [len(F.GATES)]})
    monkeypatch.setattr(F, "OUT", tmp_path)
    monkeypatch.setattr(F, "registry", lambda: reg)
    monkeypatch.setattr(F, "score", lambda r: r)
    called = []
    monkeypatch.setattr(notify, "send", lambda *a, **k: called.append("alert") or True)
    monkeypatch.setattr(F, "vault", lambda i: called.append("vault") or {})
    monkeypatch.setattr(forward, "start", lambda i: None)
    (tmp_path / "hold.json").write_text(json.dumps({"why": "the user looks at the re-scored registry first"}))
    assert F.promote() == [] and called == []
    (tmp_path / "hold.json").unlink()
    monkeypatch.setattr(F, "vault", lambda i: called.append("vault") or {
        "result": "FAIL", "return": 0.0, "avg_r": 0.0, "icir": 0.0, "search_icir": 0.0})
    F.promote()
    assert called[:2] == ["alert", "vault"]
