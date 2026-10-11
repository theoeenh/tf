import math

import pandas as pd

from algo import optiondata as D

TODAY = pd.Timestamp("2026-10-12")


def _snap(iv, delta, bid, ask, vol):
    return {"latestQuote": {"bp": bid, "ap": ask}, "latestTrade": {"p": (bid + ask) / 2}, "dailyBar": {"v": vol},
            "greeks": {"delta": delta, "gamma": 0.01, "vega": 0.2, "theta": -0.05}, "impliedVolatility": iv}


def _chain():
    snaps = {}
    for exp, iv in (("261111", 0.20), ("261211", 0.25)):  # 30 and 60 days out
        snaps[f"SPY{exp}C00100000"] = _snap(iv, 0.52, 2.9, 3.1, 100)
        snaps[f"SPY{exp}P00100000"] = _snap(iv, -0.48, 2.9, 3.1, 300)
        snaps[f"SPY{exp}P00090000"] = _snap(iv + 0.06, -0.24, 0.9, 1.0, 50)
        snaps[f"SPY{exp}C00110000"] = _snap(iv - 0.02, 0.26, 0.8, 0.9, 50)
    return pd.DataFrame(D.rows_from_snapshots("SPY", snaps, TODAY))


def test_parse_occ():
    o = D.parse_occ("AAPL261120C00250000")
    assert o["type"] == "call" and o["strike"] == 250 and o["expiry"] == pd.Timestamp("2026-11-20")
    assert D.parse_occ("garbage") is None


def test_features_from_a_chain():
    f = D.features(_chain(), 100.0)
    assert f["iv30"] == 0.2 and f["iv7"] == 0.2 and f["iv90"] == 0.25  # flat outside the expiries
    w = (0.2 ** 2 * 30 + (0.25 ** 2 * 60 - 0.2 ** 2 * 30) * 15 / 30) / 45  # 45 days: blended in variance
    assert abs(D._at_tenor([(30, 0.2), (60, 0.25)], 45) - math.sqrt(w)) < 1e-12
    assert f["move30"] == 0.06  # straddle 3 + 3 on a price of 100
    assert f["skew25"] == 0.08  # put 0.26 - call 0.18
    assert f["volume"] == 1000 and f["pc_volume"] == round(700 / 300, 3)


def test_due_once_a_day_in_the_last_hour():
    at = lambda h: pd.Timestamp(f"2026-10-12 {h}:20", tz="America/New_York")  # noqa: E731
    assert not D.due(at(14), True, set())
    assert D.due(at(15), True, set())
    assert not D.due(at(15), True, {"2026-10-12"})
    assert not D.due(at(15), False, set())


def test_underlyings_are_the_traded_stocks_without_crypto_plus_spy():
    u = D.underlyings()
    assert "SPY" in u and "GLD" in u and not any("/" in s for s in u)
