import numpy as np
import pandas as pd

from algo.strategies import opening_range_breakout, vwap_reversion


def day_bars(day, closes, highs=None, lows=None, start_hour=13):
    idx = pd.date_range(f"{day} {start_hour}:00", periods=len(closes), freq="h")
    c = pd.Series(closes, idx, dtype=float)
    return pd.DataFrame({"Open": c, "High": highs if highs is not None else c + 0.5,
                         "Low": lows if lows is not None else c - 0.5, "Close": c, "Volume": 100.0})


def test_opening_range_first_break_only_and_never_inside_the_range():
    # first two bars set the range 99.5..101.5; bar 3 inside, bar 4 breaks up, bar 5 breaks again
    df = day_bars("2026-09-29", [100, 101, 101, 103, 104, 99])
    s = opening_range_breakout(df)
    assert list(s) == [0, 0, 0, 1, 0, 0]


def test_opening_range_resets_each_day_and_can_go_short():
    a = day_bars("2026-09-29", [100, 101, 101, 103, 104, 99])
    b = day_bars("2026-09-30", [100, 101, 98, 97, 96, 95])
    s = opening_range_breakout(pd.concat([a, b]))
    assert list(s.iloc[6:]) == [0, 0, -1, 0, 0, 0]


def test_vwap_reversion_buys_a_stretch_below_vwap_in_an_uptrend():
    idx = pd.date_range("2026-01-01", periods=24 * 20, freq="h")
    c = pd.Series(np.linspace(100, 200, len(idx)), idx)  # long uptrend
    c.iloc[-1] = c.iloc[-2] - 8  # sharp drop far below today's VWAP, still above the 200-bar average
    df = pd.DataFrame({"Open": c, "High": c + 0.3, "Low": c - 0.3, "Close": c, "Volume": 10.0})
    s = vwap_reversion(df)
    assert s.iloc[-1] == 1 and (s.iloc[-24:-1] == 0).all()
