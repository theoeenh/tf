import pandas as pd

from algo import options as O

TODAY = pd.Timestamp("2026-10-05")


def _c(sym, strike, delta, bid, ask, exp="2026-11-13"):
    return {"symbol": sym, "expiry": exp, "strike": strike, "bid": bid, "ask": ask, "delta": delta, "name": sym}


def test_long_call_sized_by_premium():
    cs = [_c("C1", 230, 0.62, 9.8, 10.0), _c("C2", 250, 0.35, 3.0, 3.1)]
    d = O.design("long_call", cs, 100_000)
    assert d["legs"] == [{"symbol": "C1", "qty": 3, "price": 10.0}] and d["max_loss"] == 3000


def test_bull_put_spread_sells_the_030_put_and_buys_protection_below():
    cs = [_c("P230", 230, -0.31, 5.0, 5.2), _c("P220", 220, -0.16, 2.0, 2.1), _c("P240", 240, -0.45, 9, 9.3)]
    d = O.design("bull_put_spread", cs, 100_000)
    legs = {leg["symbol"]: leg["qty"] for leg in d["legs"]}
    credit, width = 5.0 - 2.1, 10
    assert legs["P220"] > 0 and legs["P230"] < 0 and legs["P220"] == -legs["P230"]
    assert abs(d["max_loss"] - (width - credit) * 100 * legs["P220"]) < 1e-6 and d["max_loss"] <= 3000
    assert d["cost"] < 0  # a credit


def test_spread_with_too_little_credit_is_skipped():
    cs = [_c("P230", 230, -0.30, 1.0, 1.1), _c("P220", 220, -0.15, 0.9, 1.0)]
    assert O.design("bull_put_spread", cs, 100_000) is None


def test_entries_respect_freshness_limits_and_one_position_per_stock():
    bull = {"NVDA": {"r": 0.1, "spot": 235}, "AMD": {"r": 1.2, "spot": 640}}   # AMD: old move
    bear = {"TSLA": {"spot": 400}}
    book = {"open": [{"playbook": "long_call", "underlying": "NVDA"}], "closed": []}

    def chain_for(und, kind, spot):
        k = spot / 100  # option prices in proportion to the stock
        if kind == "call":
            return [_c(f"{und}C", spot, 0.6, 4.9 * k, 5.0 * k), _c(f"{und}C2", spot * 1.05, 0.3, 2.0 * k, 2.05 * k),
                    _c(f"{und}C3", spot * 1.1, 0.15, 0.7 * k, 0.72 * k)]
        return [_c(f"{und}P", spot, -0.6, 4.9 * k, 5.0 * k), _c(f"{und}P2", spot * 0.95, -0.3, 2.0 * k, 2.05 * k),
                _c(f"{und}P3", spot * 0.9, -0.15, 0.7 * k, 0.72 * k)]

    got = {(e["playbook"], e["underlying"]) for e in O.entries(book, bull, bear, 100_000, chain_for)}
    assert ("long_call", "NVDA") not in got and ("long_call", "AMD") not in got  # held / not fresh
    assert {("bull_put_spread", "NVDA"), ("long_put", "TSLA"), ("bear_call_spread", "TSLA")} <= got


def test_exits_follow_each_playbook_rule():
    book = {"open": [
        {"playbook": "long_call", "underlying": "NVDA", "expiry": "2026-11-20", "opened": "2026-10-01", "legs": [], "cost": 3000},
        {"playbook": "long_put", "underlying": "TSLA", "expiry": "2026-11-20", "opened": "2026-10-01", "legs": [], "cost": 3000},
        {"playbook": "bull_put_spread", "underlying": "QQQ", "expiry": "2026-11-20", "opened": "2026-10-01", "legs": [1, 2], "cost": -1000},
        {"playbook": "long_call", "underlying": "QQQ", "expiry": "2026-10-12", "opened": "2026-09-01", "legs": [], "cost": 3000}]}
    out = {(p["playbook"], p["underlying"]): why for p, why in
           O.exits(book, {"QQQ": {"r": 0, "spot": 1}}, {"TSLA": 1}, TODAY, lambda p: 400.0)}
    assert "closed the stock" in out[("long_call", "NVDA")]
    assert "trend turned up" in out[("long_put", "TSLA")]
    assert "half the credit" in out[("bull_put_spread", "QQQ")]
    assert "expiry" in out[("long_call", "QQQ")]


def test_close_cost_buys_back_short_legs_at_ask():
    p = {"legs": [{"symbol": "L", "qty": 2}, {"symbol": "S", "qty": -2}]}
    q = {"L": {"bp": 1.0, "ap": 1.1}, "S": {"bp": 3.0, "ap": 3.2}}
    assert abs(O.close_cost(p, q) - (2 * 3.2 * 100 - 2 * 1.0 * 100)) < 1e-9


def test_spy_put_spread_sells_025_and_buys_010_with_a_smaller_credit_floor():
    cs = [_c("P700", 700, -0.26, 9.0, 9.2, "2026-11-20"), _c("P670", 670, -0.10, 4.6, 4.7, "2026-11-20"),
          _c("P720", 720, -0.40, 14.0, 14.3, "2026-11-20")]
    d = O.design("spy_put_spread", cs, 100_000)
    legs = {leg["symbol"]: leg["qty"] for leg in d["legs"]}
    assert legs["P700"] < 0 < legs["P670"] and d["cost"] < 0      # credit 4.3 on width 30: 14%
    assert d["max_loss"] <= 3000


def test_spy_put_spread_opens_once_a_week_up_to_four():
    def chain_for(und, kind, spot, dte=None):
        assert und == "SPY" and dte == (30, 45)
        return [_c("P700", 700, -0.25, 9.0, 9.2, "2026-11-20"), _c("P670", 670, -0.10, 4.6, 4.7, "2026-11-20")]

    def run(book, day):
        return [e for e in O.entries(book, {}, {}, 100_000, chain_for, ["spy_put_spread"], pd.Timestamp(day),
                                     {"SPY": 760.0}) if e["playbook"] == "spy_put_spread"]

    assert len(run({"open": [], "closed": []}, "2026-10-21")) == 1
    recent = {"playbook": "spy_put_spread", "underlying": "SPY", "opened": "2026-10-19 14:30"}
    assert run({"open": [recent], "closed": []}, "2026-10-21") == []               # 2 days later: wait
    assert len(run({"open": [recent], "closed": []}, "2026-10-26")) == 1          # a week later: next one
    old = [dict(recent, opened=f"2026-09-{d} 14:30") for d in (1, 8, 15, 22)]
    assert run({"open": old, "closed": []}, "2026-10-21") == []                    # 4 open: full
    assert run({"open": [], "closed": [recent]}, "2026-10-21") == []               # counts closed ones too


def test_inactive_playbooks_open_nothing_and_new_positions_record_their_source():
    bull = {"PEP": {"r": 0.1, "spot": 130}}
    bear = {"TSLA": {"spot": 400}}

    def chain_for(und, kind, spot, dte=None):
        k = spot / 100
        if kind == "call":
            return [_c(f"{und}C", spot, 0.6, 4.9 * k, 5.0 * k)]
        return [_c(f"{und}P2", spot * 0.95, -0.3, 2.0 * k, 2.05 * k), _c(f"{und}P3", spot * 0.9, -0.15, 0.7 * k, 0.72 * k)]

    got = O.entries({"open": [], "closed": []}, bull, bear, 100_000, chain_for,
                    ["long_call", "bull_put_spread"], TODAY, {}, "D")
    assert {(e["playbook"], e["underlying"]) for e in got} == {("long_call", "PEP"), ("bull_put_spread", "PEP")}
    assert all(e["source"] == "D" for e in got)


def test_exits_follow_the_source_account_and_spy_spreads_only_their_own_rules():
    book = {"open": [
        {"playbook": "long_call", "underlying": "MSFT", "expiry": "2026-12-18", "opened": "2026-10-05", "legs": [], "cost": 2800},
        {"playbook": "long_call", "underlying": "PEP", "source": "D", "expiry": "2026-12-18", "opened": "2026-10-20",
         "legs": [], "cost": 2000},
        {"playbook": "spy_put_spread", "underlying": "SPY", "expiry": "2026-11-20", "opened": "2026-10-20",
         "legs": [1, 2], "cost": -500},
        {"playbook": "spy_put_spread", "underlying": "SPY", "expiry": "2026-10-25", "opened": "2026-09-20",
         "legs": [1, 2], "cost": -500}]}
    bulls = {"A": {"MSFT": {"r": 0, "spot": 1}}, "D": {}}
    out = {(p["underlying"], p["expiry"]): why for p, why in
           O.exits(book, bulls["A"], {}, TODAY, lambda p: 400.0, bulls)}
    assert ("MSFT", "2026-12-18") not in out                         # A still holds it: an old A position stays
    assert "account D closed the stock" in out[("PEP", "2026-12-18")]
    assert ("SPY", "2026-11-20") not in out                          # no signal exit; 400 > half the credit
    assert "days to expiry" in out[("SPY", "2026-10-25")]            # 20 days left < 21


def test_spy_put_spread_narrows_the_protection_to_fit_the_budget():
    """2026-10-20, real SPY quotes: a 0.25 / 0.10 spread is 34 points wide and risks ~$3,080 per spread,
    more than 3% of $95,000; the protective leg moves up until one spread fits."""
    cs = [_c("P747", 747, -0.249, 5.56, 5.59, "2026-11-20"), _c("P713", 713, -0.10, 2.30, 2.35, "2026-11-20"),
          _c("P720", 720, -0.12, 2.74, 2.76, "2026-11-20"), _c("P730", 730, -0.154, 3.42, 3.52, "2026-11-20")]
    d = O.design("spy_put_spread", cs, 95_000)
    legs = {leg["symbol"]: leg["qty"] for leg in d["legs"]}
    assert legs == {"P747": -1, "P720": 1} and d["max_loss"] <= 0.03 * 95_000


def test_reconcile_flags_legs_the_book_does_not_know_and_odd_prices():
    """2026-10-22: Alpaca's equity rose $9,450 while the book's positions gained about $1,650."""
    from algo.options import reconcile

    book = {"open": [{"legs": [{"symbol": "AVGO261120P00347500", "qty": 1, "price": 22.1},
                               {"symbol": "IWM261120C00286000", "qty": -4, "price": 3.2}]}]}
    q = {"AVGO261120P00347500": {"bp": 30.0, "ap": 31.0}, "IWM261120C00286000": {"bp": 2.0, "ap": 2.2},
         "MSFT261120C00520000": {"bp": 10.0, "ap": 10.4}}
    positions = [{"symbol": "AVGO261120P00347500", "qty": "1", "market_value": "3050"},       # = mid: ok
                 {"symbol": "IWM261120C00286000", "qty": "-4", "market_value": "0"},          # short leg at 0
                 {"symbol": "MSFT261120C00520000", "qty": "1", "market_value": "1020"}]       # not in the book
    out = "\n".join(reconcile(book, q, positions))
    assert "| AVGO261120P00347500 | 1 | $3,050 | $3,050 | ok |" in out
    assert "| IWM261120C00286000 | -4 | $0 | $-840 | Alpaca's price far from the quotes |" in out
    assert "| MSFT261120C00520000 | 1 | $1,020 | $1,020 | book 0 |" in out
    assert "Alpaca values the positions at $4,070; at the quotes' mid they are worth $3,230 (difference $+840)" in out
