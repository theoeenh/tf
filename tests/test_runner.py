import json
from dataclasses import asdict

import numpy as np
import pandas as pd

from algo import finder as F
from algo import runner as RN


def _df(n=300, start="2025-01-02"):
    idx = pd.bdate_range(start, periods=n)
    c = 100 + np.cumsum(np.random.default_rng(1).normal(0, 1, n))
    return pd.DataFrame({"Open": c, "High": c + 1, "Low": c - 1, "Close": c, "Volume": 1e6}, idx)


def test_todays_bar_waits_for_the_close():
    df = _df(5, "2026-10-01")
    morning = pd.Timestamp("2026-10-07 09:05")
    evening = pd.Timestamp("2026-10-07 16:30")
    assert RN.complete_sessions(df, morning).index[-1] == pd.Timestamp("2026-10-06")
    assert RN.complete_sessions(df, evening).index[-1] == pd.Timestamp("2026-10-07")


def test_last_session_signal_becomes_an_entry_sized_by_risk():
    c = F.Candidate("insider_cluster", {"buyers": 3, "days": 90}, dict(F.DAILY_RULES["hold 20 days"]), data="daily500")
    df = _df()
    sig = {"X": pd.Series(0, df.index), "Y": pd.Series(0, df.index), "Z": pd.Series(0, df.index)}
    sig["X"].iloc[-1] = 1
    sig["Y"].iloc[-1] = 1
    sig["Z"].iloc[-2] = 1  # yesterday's: already in the replay
    out = RN.pending_entries(c, sig, {"X": df, "Y": df, "Z": df}, held={"Y"}, equity=100_000)
    assert [o["asset"] for o in out] == ["X"]
    o = out[0]
    risk = (o["mark"] - o["stop"]) * o["qty"]
    assert abs(risk - F.RISK * 100_000) < 1e-6 or o["qty"] * o["mark"] <= 2.0 * 100_000 / 4 + 1e-6
    assert o["pending"] and o["stop"] < o["mark"]


def test_insider_coverage_needs_the_whole_window():
    import pandas as pd
    from algo.runner import insider_coverage

    today = pd.Timestamp("2026-10-06")
    days = {d.strftime("%Y%m%d") for d in pd.bdate_range("2026-06-20", "2026-10-05")}
    assert insider_coverage(days, pd.Timestamp("2026-03-31"), today)[0]
    gap = {d for d in days if not "20260801" <= d <= "20260815"}
    ok, why = insider_coverage(gap, pd.Timestamp("2026-03-31"), today)
    assert not ok and "2026-07-31" in why
    stale = {d for d in days if d < "20260925"}
    assert not insider_coverage(stale, pd.Timestamp("2026-03-31"), today)[0]


def test_short_coverage_needs_the_previous_session():
    from algo.runner import short_coverage

    fri, mon = pd.Timestamp("2026-10-09"), pd.Timestamp("2026-10-12")
    assert short_coverage(fri, mon)[0]                       # Monday: Friday's file is the latest
    assert short_coverage(pd.Timestamp("2026-10-08"), pd.Timestamp("2026-10-09"))[0]
    assert not short_coverage(pd.Timestamp("2026-10-01"), mon)[0]  # a week behind: no new entries
    assert not short_coverage(None, mon)[0]


def test_each_universe_has_its_own_recent_filings_and_both_are_loaded(tmp_path, monkeypatch):
    from algo import wide

    monkeypatch.setattr(wide, "WIDE_DIR", tmp_path)
    row = dict(traded=None, code="P", shares=1, price=1.0, value=1.0, plan=0, role="", title="")
    pd.DataFrame([dict(accession="a", owner="o1", filed="2026-07-01", ticker="GE", **row)]).to_csv(
        wide.recent_paths("insider_recent")[0], index=False)
    pd.DataFrame([dict(accession="a", owner="o1", filed="2026-07-01", ticker="GE", **row),
                  dict(accession="b", owner="o2", filed="2026-07-02", ticker="AAPL", **row)]).to_csv(
        wide.recent_paths("insider_recent_all")[0], index=False)
    t = wide.load_insider()
    assert sorted(t["accession"]) == ["a", "b"]  # union, the shared filing once
    assert wide.recent_paths("insider_recent_all")[1].name == "insider_recent_all_days.txt"


def test_orders_carry_the_last_session_replayed():
    """The broker sync checks the prices since that session for stops filled at Alpaca (2026-10-23:
    without it account D bought PRIM back after its stop had sold it)."""
    df = _df(5, "2026-10-19")
    live = [{"asset": "PRIM", "strategy": "s", "side": 1, "qty": 32.3, "stop": 63.76, "target": None,
             "mark": 66.89, "entry": 75.47, "unrealised_r": -0.69}]
    o = RN.position_orders(live, {"PRIM": df})[0]
    assert o["bar"] == "2026-10-23" and o["qty"] == 32.3 and o["r"] == -0.69
    c = F.Candidate("insider_cluster", {"buyers": 3, "days": 90}, dict(F.DAILY_RULES["hold 20 days"]), data="daily500")
    long = _df(300, "2025-08-20")
    sig = {"X": pd.Series(0, long.index)}
    sig["X"].iloc[-1] = 1
    assert RN.pending_entries(c, sig, {"X": long}, set(), 100_000)[0]["bar"] == f"{long.index[-1]:%Y-%m-%d}"


def test_idle_cash_follows_spy_by_the_book_s_unused_share():
    days = pd.bdate_range("2026-10-23", periods=4)
    book = pd.Series([100_000.0, 100_000.0, 101_000.0, 101_000.0], days)     # +1% on day 3 from the trades
    gross = pd.Series([0.0, 0.5, 0.5, 1.2], days)                               # half invested, then over 1
    spy = pd.Series([500.0, 505.0, 510.05, 515.15], days)                      # about +1% a day
    eq = RN.with_idle_spy(book, gross, spy, 94_600.0)
    assert eq.iloc[0] == 94_600.0
    assert abs(eq.iloc[1] / eq.iloc[0] - (1 + 0.01 - 1e-4 * 0)) < 1e-9          # all idle on day 1: SPY's +1%
    r2 = 0.01 + 0.5 * (510.05 / 505 - 1)                                        # book +1%, half in SPY
    assert abs(eq.iloc[2] / eq.iloc[1] - (1 + r2 - 0.5 * 1e-4)) < 1e-9
    assert abs(eq.iloc[3] / eq.iloc[2] - (1 + 0.5 * (515.15 / 510.05 - 1))) < 1e-9  # weight from the day before


# ------------------------------------------------------------------ the members of each day (2026-11-14)

import pytest

SESS = pd.bdate_range("2025-01-02", periods=330)
START, PIT, MOVE = SESS[280], SESS[285], SESS[300]  # the account's start, the fix, the day the lists change
RULE = dict(stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60)


def _flat(until=len(SESS)):
    idx = SESS[:until]
    return pd.DataFrame({"Open": 100.0, "High": 101.0, "Low": 99.0, "Close": 100.0, "Volume": 1e6}, idx)


@pytest.fixture
def table(tmp_path, monkeypatch):
    """An account that started on START and trades the members of each day from PIT on. On MOVE the
    lists change: LEFT and AFTER leave, JOIN and JOIN2 join. OLD left long before. GONE is bought out:
    its last bar is the session before SESS[310]. Each stock's bars: flat at 100 (no stop is ever hit)."""
    from algo import wide, wide_pit

    day = lambda d: None if d is None else f"{pd.Timestamp(d):%Y-%m-%d}"
    spell = lambda s, start, end: dict(symbol=s, index="sp500", start=day(start), end=day(end), sector="Energy")
    hist = [spell("KEEP", "2015-12-01", None), spell("LEFT", "2015-12-01", MOVE), spell("AFTER", "2015-12-01", MOVE),
            spell("JOIN", MOVE, None), spell("JOIN2", MOVE, None), spell("OLD", "2015-12-01", SESS[100]),
            spell("GONE", "2015-12-01", SESS[310])]
    (tmp_path / "wide").mkdir()
    pd.DataFrame(hist).to_csv(tmp_path / "wide" / "members_history.csv", index=False)
    pd.DataFrame([dict(symbol=s, sector="Energy", index="sp500") for s in ("KEEP", "JOIN", "JOIN2")]).to_csv(
        tmp_path / "wide" / "members.csv", index=False)
    monkeypatch.setattr(wide, "WIDE_DIR", tmp_path / "wide")
    monkeypatch.setattr(wide_pit, "PATH", tmp_path / "wide" / "members_history.csv")
    wide_pit._cache.clear()
    bars = {s: _flat() for s in ("KEEP", "LEFT", "AFTER", "JOIN", "JOIN2", "OLD")} | {"GONE": _flat(310)}
    asked = []

    def load_bars(symbols, now_ny, since=None):
        asked.append(sorted(symbols))
        return {s: bars[s].copy() for s in symbols if s in bars}

    monkeypatch.setattr(RN, "load_bars", load_bars)
    monkeypatch.setattr(RN, "PIT_FROM", PIT)
    monkeypatch.setattr(RN, "PAPER_DIR", tmp_path / "acct")
    (tmp_path / "acct").mkdir()
    sent = []
    monkeypatch.setattr(RN.notify, "send", lambda *a, **k: sent.append(a) or True)

    def fake_buy(prices, buys):  # a buy signal on session number buys[stock]
        return {a: pd.Series([int(a in buys and d == SESS[buys[a]]) for d in df.index], df.index)
                for a, df in prices.items()}

    monkeypatch.setitem(F.WIDE_FAMILIES, "fake_buy", (fake_buy, {}))

    def run(buys):
        c = F.Candidate("fake_buy", {"buys": buys}, RULE, trend=False, assets="sp1500", data="daily500")
        (tmp_path / "acct" / "config.json").write_text(json.dumps(
            {"name": "T", "candidate": json.dumps(asdict(c)), "start": f"{START:%Y-%m-%d}", "capital": 100_000}))
        out = RN.update(fetch_insider=False)
        trades = (pd.read_csv(tmp_path / "acct" / "trades.csv") if (tmp_path / "acct" / "trades.csv").exists()
                  else pd.DataFrame(columns=["asset"]))
        return {"held": sorted(o["asset"] for o in out["orders"]), "new": sorted(o["asset"] for o in out["pending"]),
                "trades": trades, "asked": asked[-1], "sent": sent,
                "status": (tmp_path / "acct" / "status.md").read_text()}

    return run


def test_a_held_stock_that_leaves_the_index_stays_until_its_own_exit(table):
    """Until 2026-11-14 the runner loaded today's members only: a held stock that left the index
    vanished from the replay (no exit booked, the past rewritten) and the sync sold it."""
    r = table({"KEEP": 290, "LEFT": 290})
    assert r["held"] == ["KEEP", "LEFT"]
    assert "OLD" not in r["asked"]  # it left before the accounts traded the members of each day


def test_a_stock_gets_no_entry_once_it_has_left(table):
    r = table({"KEEP": 290, "AFTER": 305, "LEFT": len(SESS) - 1})
    assert r["held"] == ["KEEP"] and r["new"] == [] and not len(r["trades"])


def test_a_stock_that_joins_is_traded_from_that_day_only(table):
    """A new member used to be replayed from the account's start: trades the account never made."""
    assert table({"JOIN": 290})["held"] == []            # the signal came before it joined
    r = table({"JOIN2": 305, "JOIN": len(SESS) - 1})
    assert r["held"] == ["JOIN2"] and r["new"] == ["JOIN"]


def test_before_the_fix_the_account_keeps_the_list_it_traded(table):
    """Nothing in an account's past may change: before PIT_FROM it traded the members of that day
    (LEFT was one), whatever the earlier date."""
    assert table({"LEFT": 281, "KEEP": 281})["held"] == ["KEEP", "LEFT"]


def test_a_held_stock_that_stops_trading_is_closed_at_its_last_price(table):
    """A bought-out company's bars stop. The position is closed at its last price on the next session
    (the holder is paid in cash), not carried for ever at a stale price."""
    r = table({"KEEP": 290, "GONE": 290})
    assert r["held"] == ["KEEP"]
    t = r["trades"]
    assert list(t["asset"]) == ["GONE"] and t["reason"].iloc[0] == "left the market"
    assert abs(t["exit"].iloc[0] - 100.0) < 0.5 and str(t["exit_date"].iloc[0])[:10] == f"{SESS[310]:%Y-%m-%d}"
    assert "GONE" in r["status"] and not r["sent"]


def test_a_position_that_vanishes_without_an_exit_is_reported(table, tmp_path):
    """The replay starts from scratch each run: if a position of the last plan is neither open nor
    closed in the new one (its bars disappeared, a data revision), say so on the phone and in the
    status; never silently."""
    first = table({"KEEP": 290, "LEFT": 290})
    assert not first["sent"] and "without" not in first["status"]
    plan = json.loads((tmp_path / "acct" / "orders.json").read_text())
    assert {o["asset"] for o in plan} == {"KEEP", "LEFT"}
    r = table({"KEEP": 290})  # LEFT's entry is no longer in the replay
    assert r["held"] == ["KEEP"]
    assert len(r["sent"]) == 1 and "LEFT" in r["sent"][0][1] and "LEFT" in r["status"]
    assert len(table({"KEEP": 290})["sent"]) == 1  # reported once, not at every run
