"""Strategy families for the finder, beyond the five textbook ones the live system trades.

Each family takes the whole universe (dict asset -> hourly bars, UTC bar starts) and returns
a signal per asset (+1 long, -1 short, 0 nothing) on the bar whose close triggers the trade
(the engine fills at the next bar's open). Only information known at that close is used.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import ASSET_CLASS, CRYPTO
from .indicators import atr

NY = "America/New_York"


def _panel(prices: dict, col: str = "Close") -> pd.DataFrame:
    return pd.DataFrame({a: df[col] for a, df in prices.items()})


def _entries(member: pd.DataFrame) -> pd.DataFrame:
    """1 on the bar an asset enters a set (not every bar it stays in it)."""
    m = member.fillna(False).astype(bool)
    return (m & ~m.shift(1, fill_value=False)).astype(int)


def _own(sig: pd.DataFrame, prices: dict) -> dict[str, pd.Series]:
    return {a: sig[a].reindex(df.index).fillna(0).astype(int) for a, df in prices.items() if a in sig}


def _session(df: pd.DataFrame) -> tuple[pd.Index, pd.Series]:
    ny = df.index.tz_localize("UTC").tz_convert(NY)
    day = pd.Index(ny.date)
    k = pd.Series(np.arange(len(df)), df.index).groupby(day).cumcount()
    return day, k


def xs_momentum(prices: dict, lookback: int = 120, top: int = 3) -> dict:
    """Cross-asset momentum: buy an asset when it enters the `top` strongest of the universe over
    the last `lookback` bars (ranked only among assets trading at that hour)."""
    ret = _panel(prices).pct_change(lookback, fill_method=None)
    rank = ret.rank(axis=1, ascending=False)
    return _own(_entries(rank <= top), prices)


def xs_reversal(prices: dict, lookback: int = 6, bottom: int = 3) -> dict:
    """Short-term reversal: buy an asset when it becomes one of the `bottom` worst over the last
    `lookback` bars (the trend filter keeps only those in a daily uptrend)."""
    ret = _panel(prices).pct_change(lookback, fill_method=None)
    rank = ret.rank(axis=1, ascending=True)
    return _own(_entries(rank <= bottom), prices)


def intraday_momentum(prices: dict, k: float = 0.5) -> dict:
    """Stocks / ETFs: a strong first half hour (move > k ATR) tends to carry into the last hour.
    Signal on the 14:00 New York bar's close, so the trade covers 15:00-16:00 (use a 1-bar exit)."""
    out = {}
    for a, df in prices.items():
        if a in CRYPTO:
            continue
        day, n = _session(df)
        first = df["Close"].where(n == 0) - df["Open"].where(n == 0)
        first = first.groupby(day).transform("first")
        z = first / atr(df)
        at = n == 5  # 9:30, 10, 11, 12, 13, 14 -> the 14:00 bar
        out[a] = (np.sign(z) * ((z.abs() > k) & at)).fillna(0).astype(int)
    return out


def gap_fade(prices: dict, g: float = 1.0) -> dict:
    """Stocks / ETFs: buy a gap down of more than `g` ATR at the open once the first bar closes
    (sell a gap up), for a move back toward the previous close."""
    out = {}
    for a, df in prices.items():
        if a in CRYPTO:
            continue
        day, n = _session(df)
        prev_close = df["Close"].shift(1)
        gap = (df["Open"] - prev_close) / atr(df)
        first = n == 0
        out[a] = ((first & (gap < -g)).astype(int) - (first & (gap > g)).astype(int)).fillna(0).astype(int)
    return out


def earnings_drift(prices: dict, x: float = 1.0) -> dict:
    """Stocks: after an earnings release, follow the first hour's reaction when it is larger than
    `x` ATR (post-earnings drift). Earnings dates are public in advance."""
    from . import news

    out = {}
    for a, df in prices.items():
        if ASSET_CLASS.get(a) != "stock":
            continue
        dates = {d.date() for d in news.earnings_dates(a)}
        if not dates:
            continue
        day, n = _session(df)
        prev_day = pd.Index([d - pd.Timedelta(days=1) for d in day])
        report = pd.Series([d in dates or p in dates for d, p in zip(day, prev_day)], df.index)  # before / after the bell
        move = (df["Close"] - df["Close"].shift(1)) / atr(df)
        s = (n == 0) & report
        out[a] = (np.sign(move) * (s & (move.abs() > x))).fillna(0).astype(int)
    return out


def volume_breakout(prices: dict, n: int = 20, m: float = 2.0) -> dict:
    """A new `n`-bar high on volume above `m` times its usual level (usual = same-hour average)."""
    out = {}
    for a, df in prices.items():
        hour = df.index.hour
        usual = df["Volume"].groupby(hour).transform(lambda v: v.rolling(20, min_periods=10).mean().shift(1))
        loud = df["Volume"] > m * usual
        up = df["Close"] > df["High"].rolling(n).max().shift(1)
        dn = df["Close"] < df["Low"].rolling(n).min().shift(1)
        out[a] = ((up & loud).astype(int) - (dn & loud).astype(int)).fillna(0).astype(int)
    return out


def btc_lead(prices: dict, k: float = 1.0) -> dict:
    """Crypto: when bitcoin jumps more than `k` of its hourly ATR, buy the alt coins that have not
    followed yet (moved less than half as much)."""
    if "BTC" not in prices:
        return {}
    btc = prices["BTC"]
    b = (btc["Close"] - btc["Open"]) / atr(btc)
    out = {}
    for a in ("ETH", "SOL"):
        if a not in prices:
            continue
        df = prices[a]
        z = ((df["Close"] - df["Open"]) / atr(df)).reindex(b.index)
        lag = (b > k) & (z < 0.5 * b)
        lead_dn = (b < -k) & (z > 0.5 * b)
        out[a] = (lag.astype(int) - lead_dn.astype(int)).reindex(df.index).fillna(0).astype(int)
    return out


# family -> (function, parameter grid)
PANEL_FAMILIES = {
    "xs_momentum": (xs_momentum, {"lookback": [60, 120, 240], "top": [2, 4]}),
    "xs_reversal": (xs_reversal, {"lookback": [3, 6, 12], "bottom": [2, 4]}),
    "intraday_momentum": (intraday_momentum, {"k": [0.3, 0.6, 1.0]}),
    "gap_fade": (gap_fade, {"g": [0.5, 1.0, 2.0]}),
    "earnings_drift": (earnings_drift, {"x": [0.5, 1.0, 2.0]}),
    "volume_breakout": (volume_breakout, {"n": [10, 20], "m": [1.5, 2.5]}),
    "btc_lead": (btc_lead, {"k": [0.75, 1.5]}),
}


# ------------------------------------------------------------------ S&P 500, daily bars (data="daily500")
# Signals fire on a day's close and fill at the next open. Insider filings count from their filing
# date: a Form 4 accepted after the close is still only traded the next morning.

def _on_days(dates: pd.Series, index: pd.DatetimeIndex) -> np.ndarray:
    """Position of the first trading day on or after each date (len(index) when past the end)."""
    return index.searchsorted(pd.DatetimeIndex(dates).normalize(), side="left")


def _insider(code: str = "P"):
    from . import wide

    t = wide.load_insider()
    if t.empty:
        raise FileNotFoundError("no insider data (python -m algo.wide)")
    return t[t["code"] == code]


def insider_cluster(prices: dict, buyers: int = 2, days: int = 30) -> dict:
    """Several insiders buying their own stock in the open market within `days` days: the day the
    number of distinct buyers reaches `buyers` (one signal per cluster)."""
    t = _insider("P")
    out = {}
    for a, df in prices.items():
        g = t[t["ticker"] == a].sort_values("filed") if len(t) else t
        s = np.zeros(len(df), int)
        last = pd.Timestamp("1900-01-01")
        for f in g["filed"].drop_duplicates():
            win = g[(g["filed"] > f - pd.Timedelta(days=days)) & (g["filed"] <= f)]
            if win["owner"].nunique() >= buyers and f - last > pd.Timedelta(days=days):
                p = _on_days(pd.Series([f]), df.index)[0]
                if p < len(df):
                    s[p] = 1
                last = f
        out[a] = pd.Series(s, df.index)
    return out


def insider_big_buy(prices: dict, min_value: float = 250_000, officer: bool = True) -> dict:
    """One insider buying at least `min_value` dollars in the open market (an officer only, e.g. CEO
    or CFO, if `officer`): the filing day."""
    t = _insider("P")
    if len(t) and officer:
        t = t[t["role"].fillna("").str.contains("Officer", case=False)]
    out = {}
    for a, df in prices.items():
        g = t[t["ticker"] == a] if len(t) else t
        if len(g):
            v = g.groupby(["accession", "filed"])["value"].sum().reset_index()
            v = v[v["value"] >= min_value]
            pos = _on_days(v["filed"], df.index)
        else:
            pos = []
        s = np.zeros(len(df), int)
        s[[p for p in pos if p < len(df)]] = 1
        out[a] = pd.Series(s, df.index)
    return out


def momentum_12_1(prices: dict, top: float = 0.1) -> dict:
    """Classic momentum: at each month end, buy the stocks in the top `top` share of the 12-month
    return skipping the last month (entries only, the exit rule decides the hold)."""
    close = _panel(prices)
    ret = close.shift(21) / close.shift(252) - 1
    month_end = close.index.to_series().dt.to_period("M") != close.index.to_series().shift(-1).dt.to_period("M")
    rank = ret.rank(axis=1, pct=True, ascending=False)
    sig = ((rank <= top) & month_end.to_numpy()[:, None]).astype(int)
    return _own(sig, prices)


def reversal_5d(prices: dict, bottom: float = 0.05) -> dict:
    """Short-term reversal: buy the worst `bottom` share of the last five days (weekly, Fridays)."""
    close = _panel(prices)
    ret = close / close.shift(5) - 1
    friday = close.index.dayofweek == 4
    rank = ret.rank(axis=1, pct=True, ascending=True)
    return _own(((rank <= bottom) & friday[:, None]).astype(int), prices)


def high_52w(prices: dict, within: float = 0.02) -> dict:
    """Close within `within` of its 52-week high for the first time in a month (anchoring: investors
    hesitate to buy near the high, so good news there is priced in slowly)."""
    close = _panel(prices)
    near = close >= (1 - within) * close.rolling(252, min_periods=200).max()
    fresh = near & ~near.shift(1, fill_value=False).rolling(21, min_periods=1).max().astype(bool)
    return _own(fresh.astype(int), prices)


WIDE_FAMILIES = {
    "insider_cluster": (insider_cluster, {"buyers": [2, 3], "days": [30, 90]}),
    "insider_big_buy": (insider_big_buy, {"min_value": [100_000, 500_000], "officer": [True, False]}),
    "momentum_12_1": (momentum_12_1, {"top": [0.05, 0.1]}),
    "reversal_5d": (reversal_5d, {"bottom": [0.02, 0.05]}),
    "high_52w": (high_52w, {"within": [0.01, 0.03]}),
}
