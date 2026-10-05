import pandas as pd

from algo import options as O

TODAY = pd.Timestamp("2026-10-05")


def _c(sym, exp, delta, bid, ask):
    return ({"symbol": sym, "expiration_date": exp, "name": sym},
            {sym: {"latestQuote": {"bp": bid, "ap": ask}, "greeks": {"delta": delta}}})


def test_choose_takes_the_liquid_call_nearest_to_060_delta():
    cs, snaps = [], {}
    for sym, exp, d, b, a in [("X1", "2026-11-13", 0.58, 5.0, 5.2),     # 39 days, fine
                              ("X2", "2026-11-13", 0.61, 5.0, 6.5),     # nearer delta but spread 26%
                              ("X3", "2026-10-16", 0.60, 5.0, 5.1),     # 11 days: too short
                              ("X4", "2026-11-13", 0.80, 9.0, 9.1)]:
        c, s = _c(sym, exp, d, b, a)
        cs.append(c)
        snaps |= s
    assert O.choose(cs, snaps, TODAY)["symbol"] == "X1"


def test_plan_sells_what_a_closed_and_buys_fresh_signals_within_budget():
    plan = [{"asset": "NVDA", "qty": 50.0, "r": 0.1, "mark": 235.0},
            {"asset": "AMD", "qty": 20.0, "r": 1.4, "mark": 640.0},       # old move: no chase
            {"asset": "QQQ", "qty": 30.0, "r": -0.1, "mark": 750.0}]
    held = [{"symbol": "AAPL261120C00250000", "qty": "3"},              # A no longer holds AAPL
            {"symbol": "QQQ261009C00740000", "qty": "2"}]               # 4 days to expiry
    pick = lambda und: {"symbol": f"{und}261120C00230000", "ask": 10.0, "delta": 0.6, "dte": 46}  # noqa: E731
    o = O.plan_orders(plan, held, 100_000, TODAY, pick)
    sells = {x["underlying"]: x for x in o if x["side"] == "sell"}
    buys = {x["underlying"]: x for x in o if x["side"] == "buy"}
    assert set(sells) == {"AAPL", "QQQ"} and set(buys) == {"NVDA", "QQQ"}
    assert buys["NVDA"]["qty"] == 3  # 3% of $100k = $3,000 / ($10 x 100)
    assert o.index(next(x for x in o if x["side"] == "buy")) > o.index(next(x for x in o if x["side"] == "sell"))


def test_no_contract_when_one_is_too_expensive_and_crypto_ignored():
    plan = [{"asset": "NVDA", "qty": 50.0, "r": 0.0, "mark": 235.0}, {"asset": "BTC", "qty": 0.5, "r": 0.0, "mark": 1}]
    pick = lambda und: {"symbol": "NVDA261120C00100000", "ask": 140.0, "delta": 0.6, "dte": 46}  # $14,000 a contract
    assert O.plan_orders(plan, [], 100_000, TODAY, pick) == []
    assert O.underlying_of("NVDA261106C00220000") == "NVDA" and str(O.expiry_of("NVDA261106C00220000").date()) == "2026-11-06"
