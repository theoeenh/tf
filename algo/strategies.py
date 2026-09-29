"""Entry signals for the three candidate strategies.

Each strategy returns an int Series: +1 at bar t means "go long at the open
of bar t+1", -1 means "go short", 0 means nothing. Exits (stops, targets,
trailing) are handled by the engine so the strategies can be compared under
the same risk rules. Whether shorts are taken is decided per asset.

Strategy parameters are fixed at textbook defaults on purpose: only the exit
rule is tuned, which keeps the number of knobs (and the overfitting risk) low.
"""
from __future__ import annotations

from typing import Callable

import pandas as pd

from .indicators import bollinger, rsi, sma


def _combine(long: pd.Series, short: pd.Series) -> pd.Series:
    return long.astype(int) - short.astype(int)


def donchian_breakout(df: pd.DataFrame, n: int = 55, trend_ma: int = 200) -> pd.Series:
    """Trend following: close breaks the highest high (lowest low) of the
    previous n bars, in the direction of the long-term moving average."""
    ma = sma(df["Close"], trend_ma)
    long = (df["Close"] > df["High"].rolling(n).max().shift(1)) & (df["Close"] > ma)
    short = (df["Close"] < df["Low"].rolling(n).min().shift(1)) & (df["Close"] < ma)
    return _combine(long, short)


def squeeze_breakout(
    df: pd.DataFrame, n: int = 20, k: float = 2.0, lookback: int = 120, pct: float = 0.2, memory: int = 5
) -> pd.Series:
    """Volatility breakout: after a quiet period (Bollinger width in the bottom
    `pct` of the last `lookback` bars, within the last `memory` bars), close
    breaks out of the bands."""
    lower, mid, upper = bollinger(df["Close"], n, k)
    width = (upper - lower) / mid
    squeezed = width <= width.rolling(lookback).quantile(pct)
    recently_squeezed = squeezed.astype(float).rolling(memory).max().shift(1) == 1
    return _combine((df["Close"] > upper) & recently_squeezed, (df["Close"] < lower) & recently_squeezed)


def rsi2_reversion(df: pd.DataFrame, rsi_n: int = 2, threshold: float = 10.0, trend_ma: int = 200) -> pd.Series:
    """Mean reversion (Connors RSI-2): buy a sharp dip in an uptrend, sell a
    sharp rally in a downtrend."""
    r, ma = rsi(df["Close"], rsi_n), sma(df["Close"], trend_ma)
    return _combine((r < threshold) & (df["Close"] > ma), (r > 100 - threshold) & (df["Close"] < ma))


STRATEGIES: dict[str, Callable[[pd.DataFrame], pd.Series]] = {
    "donchian_trend": donchian_breakout,
    "squeeze_breakout": squeeze_breakout,
    "rsi2_reversion": rsi2_reversion,
}
