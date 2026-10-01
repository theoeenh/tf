import numpy as np
import pandas as pd

from algo import fast


def session_bars(days=3):
    """5-minute regular-session bars (UTC) for a few days, a slow random walk."""
    idx = []
    for d in pd.bdate_range("2026-03-02", periods=days):  # New York UTC-5 in early March
        idx += list(pd.date_range(d + pd.Timedelta(hours=14, minutes=30), periods=78, freq="5min"))
    idx = pd.DatetimeIndex(idx)
    rng = np.random.default_rng(0)
    c = 100 + np.cumsum(rng.normal(0, 0.05, len(idx)))
    return pd.DataFrame({"Open": c, "High": c + 0.05, "Low": c - 0.05, "Close": c, "Volume": 1000.0}, idx)


def test_last_bar_is_1555_new_york():
    df = session_bars()
    last = fast.last_bar_of_session(df)
    assert last.sum() == 3
    assert all(t.hour == 20 and t.minute == 55 for t in df.index[last])  # 15:55 New York


def test_orb_one_signal_per_day_and_not_in_the_first_15_minutes():
    df = session_bars()
    df.iloc[10, df.columns.get_loc("Close")] = 200  # a huge break at 10:20
    s = fast.orb15(df)
    day = df.index.normalize()
    assert (s != 0).groupby(day).sum().max() <= 1
    k = df.groupby(day).cumcount()
    assert not (s[k < 3] != 0).any()


def test_flat_at_close_holds_no_stock_overnight():
    df = session_bars(5)
    prices = {"QQQ": df}
    res = fast.run(prices, ["vwap_fade", "range_break", "rsi2_5m"], {"QQQ": fast.STOCK_COST}, None, None,
                   risk=0.01)
    for t in res.trades:
        assert pd.Timestamp(t.entry_date).normalize() == pd.Timestamp(t.exit_date).normalize()
