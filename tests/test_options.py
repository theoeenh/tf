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
