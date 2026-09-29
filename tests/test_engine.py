import numpy as np
import pandas as pd
import pytest

from algo.engine import Costs, ExitRule, backtest, buy_and_hold
from algo.indicators import atr
from algo.strategies import STRATEGIES
from algo.research import synthetic_prices


def flat_bars(n=30, px=100.0, rng=2.0):
    """Quiet market: every bar is px +/- rng/2, so ATR converges to `rng`."""
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"Open": px, "High": px + rng / 2, "Low": px - rng / 2, "Close": px, "Volume": 0.0}, index=idx
    )


def signal_at(df, i):
    s = pd.Series(False, index=df.index)
    s.iloc[i] = True
    return s


def test_target_hit_pays_rr_times_risk():
    df = flat_bars()
    df.iloc[21, df.columns.get_loc("High")] = 200.0  # bar after entry spikes through the target
    res = backtest(df, signal_at(df, 19), ExitRule(stop_atr=1.0, rr=3.0), risk_pct=0.01)
    (t,) = res.trades
    assert t.entry_date == df.index[20] and t.reason == "target"
    assert t.r_multiple == pytest.approx(3.0)
    assert res.equity.iloc[-1] == pytest.approx(100_000 * 1.03, rel=1e-9)


def test_stop_hit_loses_one_r():
    df = flat_bars()
    df.iloc[21, df.columns.get_loc("Low")] = 50.0
    res = backtest(df, signal_at(df, 19), ExitRule(stop_atr=1.0, rr=3.0), risk_pct=0.01)
    (t,) = res.trades
    assert t.reason == "stop" and t.r_multiple == pytest.approx(-1.0)
    assert res.equity.iloc[-1] == pytest.approx(99_000.0)


def test_both_levels_in_one_bar_assumes_stop():
    df = flat_bars()
    df.iloc[21, df.columns.get_loc("Low")] = 50.0
    df.iloc[21, df.columns.get_loc("High")] = 200.0
    (t,) = backtest(df, signal_at(df, 19), ExitRule(1.0, 3.0)).trades
    assert t.reason == "stop"


def test_gap_through_stop_fills_at_open():
    df = flat_bars()
    df.iloc[21, :4] = [90.0, 91.0, 89.0, 90.0]
    (t,) = backtest(df, signal_at(df, 19), ExitRule(1.0, 3.0)).trades
    assert t.exit == pytest.approx(90.0)
    assert t.r_multiple < -1.0  # a gap loses more than the planned 1R


def test_no_lookahead_signal_fills_next_open():
    df = flat_bars()
    df["Open"] = np.arange(len(df)) + 100.0
    df["High"] = df["Open"] + 50  # wide bars so nothing exits
    df["Low"] = df["Open"] - 50
    res = backtest(df, signal_at(df, 19), ExitRule(10.0, 10.0))
    assert res.trades[0].entry == df["Open"].iloc[20]


def test_costs_reduce_pnl():
    df = flat_bars()
    df.iloc[21, df.columns.get_loc("High")] = 200.0
    free = backtest(df, signal_at(df, 19), ExitRule(1.0, 3.0))
    paid = backtest(df, signal_at(df, 19), ExitRule(1.0, 3.0), Costs(fee_bps=10, slippage_bps=5))
    assert paid.equity.iloc[-1] < free.equity.iloc[-1]


def test_position_never_exceeds_equity():
    df = flat_bars(rng=0.01)  # tiny ATR -> risk sizing would ask for huge size
    res = backtest(df, signal_at(df, 19), ExitRule(1.0, 3.0), risk_pct=0.01)
    assert res.trades[0].qty * res.trades[0].entry <= 100_000 + 1e-6


def test_window_starts_with_initial_capital():
    df = synthetic_prices("BTC")
    entries = STRATEGIES["donchian_trend"](df)
    res = backtest(df, entries, start="2020-01-01", end="2020-12-31")
    assert res.equity.index[0] == pd.Timestamp("2020-01-01")
    assert res.equity.iloc[0] == pytest.approx(100_000, rel=0.02)


def test_buy_and_hold_tracks_price():
    df = flat_bars()
    df["Close"] = np.linspace(100, 200, len(df))
    eq = buy_and_hold(df)
    assert eq.iloc[-1] == pytest.approx(200_000)


@pytest.mark.parametrize("name", list(STRATEGIES))
def test_strategies_do_not_use_future_data(name):
    """Changing future prices must not change past signals."""
    df = synthetic_prices("GOLD")
    base = STRATEGIES[name](df)
    cut = len(df) - 200
    shocked = df.copy()
    shocked.iloc[cut:, :4] *= 3.0
    after = STRATEGIES[name](shocked)
    pd.testing.assert_series_equal(base.iloc[:cut], after.iloc[:cut])


def test_atr_constant_range():
    assert atr(flat_bars(rng=2.0)).iloc[-1] == pytest.approx(2.0)


def short_signal_at(df, i):
    s = pd.Series(0, index=df.index)
    s.iloc[i] = -1
    return s


def test_short_target_and_stop():
    df = flat_bars()
    df.iloc[21, df.columns.get_loc("Low")] = 50.0
    (t,) = backtest(df, short_signal_at(df, 19), ExitRule(1.0, 3.0)).trades
    assert t.side == -1 and t.reason == "target" and t.r_multiple == pytest.approx(3.0)

    df = flat_bars()
    df.iloc[21, df.columns.get_loc("High")] = 150.0
    res = backtest(df, short_signal_at(df, 19), ExitRule(1.0, 3.0))
    (t,) = res.trades
    assert t.reason == "stop" and t.r_multiple == pytest.approx(-1.0)
    assert res.equity.iloc[-1] == pytest.approx(99_000.0)


def test_shorts_ignored_when_not_allowed():
    df = flat_bars()
    assert backtest(df, short_signal_at(df, 19), allow_short=False).trades == []


def test_short_pays_borrow_cost():
    df = flat_bars()
    free = backtest(df, short_signal_at(df, 19), ExitRule(10.0, 10.0))
    paid = backtest(df, short_signal_at(df, 19), ExitRule(10.0, 10.0), Costs(short_borrow_apr=0.365))
    days_held = (df.index[-1] - df.index[20]).days
    notional = paid.trades[0].qty * 100.0
    assert free.equity.iloc[-1] - paid.equity.iloc[-1] == pytest.approx(notional * 0.001 * days_held)
    assert paid.trades[0].fees == pytest.approx(notional * 0.001 * days_held)


def test_trailing_stop_locks_in_profit():
    df = flat_bars(n=40)
    # steady rally after entry, then a drop
    for k, i in enumerate(range(21, 30)):
        px = 100.0 + 3 * (k + 1)
        df.iloc[i, :4] = [px - 1, px + 1, px - 1, px]
    df.iloc[30, :4] = [127.0, 127.0, 90.0, 95.0]
    (t,) = backtest(df, signal_at(df, 19), ExitRule(2.0, None, trail_atr=2.0)).trades
    assert t.reason == "trail" and t.pnl > 0 and t.exit > t.entry


def test_opposite_signal_reverses():
    df = flat_bars(n=40)
    sig = pd.Series(0, index=df.index)
    sig.iloc[19], sig.iloc[25] = 1, -1
    trades = backtest(df, sig, ExitRule(10.0, 10.0)).trades
    assert [t.side for t in trades] == [1, -1]
    assert trades[0].reason == "reverse" and trades[0].exit_date == trades[1].entry_date == df.index[26]


def test_adaptive_uses_wider_target_in_strong_trend():
    df = flat_bars(n=60)
    df[["Open", "High", "Low", "Close"]] = df[["Open", "High", "Low", "Close"]].add(np.arange(60) * 2.0, axis=0)
    rule = ExitRule(1.0, rr=2.0, rr_strong=4.0, adaptive=True)
    (t,) = backtest(df, signal_at(df, 45), rule).trades[:1]
    dist = t.entry - t.initial_stop
    assert t.target == pytest.approx(t.entry + 4.0 * dist)  # steady rise -> ADX high -> 4:1


def test_fees_are_recorded_per_trade():
    df = flat_bars()
    df.iloc[21, df.columns.get_loc("High")] = 200.0
    (t,) = backtest(df, signal_at(df, 19), ExitRule(1.0, 3.0), Costs(fee_bps=10)).trades
    assert t.fees == pytest.approx(t.qty * (t.entry + t.exit) * 0.001)
