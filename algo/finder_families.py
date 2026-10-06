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


def insider_dip(prices: dict, buyers: int = 2, days: int = 30, drop: float = 0.10) -> dict:
    """Insiders buying after the stock fell: a cluster of open-market purchases (as insider_cluster)
    on a stock that is down more than `drop` from its close 20 trading days earlier. Insiders who
    buy into a fall are the classic contrarian signal (they know the business better than the
    sellers)."""
    cl = insider_cluster(prices, buyers=buyers, days=days)
    out = {}
    for a, s in cl.items():
        close = prices[a]["Close"]
        fell = close / close.shift(20) - 1 < -drop
        out[a] = (s.astype(bool) & fell).astype(int)
    return out


def earnings_reaction(prices: dict, z: float = 2.0, volume: float = 1.5, side: str = "up") -> dict:
    """Post-earnings drift: a stock that reacts strongly to its earnings release (the first session that
    could react: the release day if it came out before the 9:30 open, else the next) keeps drifting the
    same way for weeks. Buy at that session's close when the move is at least `z` times the stock's
    usual daily move (60 sessions before) on at least `volume` times its usual volume (20 sessions).
    side="down": the mirror image, buy the stocks that fell that hard (an overreaction that reverses:
    the 'up' version showed a strongly negative edge in 2017-2022 and 2023-25, so this idea was chosen
    after seeing the validation period; the vault is untouched).
    Release times: the SEC's 8-K item 2.02 filings (wide.load_earnings)."""
    from . import wide

    e = wide.load_earnings()
    out = {}
    for a, df in prices.items():
        s = np.zeros(len(df), int)
        days = e.loc[e["ticker"] == a, "day"]
        if len(days):
            close, vol = df["Close"].to_numpy(), df["Volume"].to_numpy(dtype=float)
            ret = np.r_[np.nan, close[1:] / close[:-1] - 1]
            sd = pd.Series(ret).rolling(60, min_periods=40).std().shift(1).to_numpy()
            usual = pd.Series(vol).rolling(20, min_periods=10).mean().shift(1).to_numpy()
            for p in np.unique(df.index.searchsorted(pd.DatetimeIndex(days), side="left")):
                if 0 < p < len(df) and sd[p] > 0 and usual[p] > 0:
                    move = ret[p] / sd[p] if side == "up" else -ret[p] / sd[p]
                    if move >= z and vol[p] / usual[p] >= volume:
                        s[p] = 1
        out[a] = pd.Series(s, df.index)
    return out


def earnings_overreaction(prices: dict, z: float = 2.0, volume: float = 1.5) -> dict:
    """Buy the stocks that fell hard on their earnings (earnings_reaction with side='down')."""
    return earnings_reaction(prices, z=z, volume=volume, side="down")


def ml_rank(prices: dict, model: str = "gbm", top: float = 0.02, short: bool = False, fund: bool = False) -> dict:
    """The ML ranker (algo/ranker.py): every Friday, buy the stocks in the top `top` share of the
    walk-forward score (each score from a model trained only on the past). A signal every week the
    stock is in the top; the exit rule decides the hold."""
    from . import ranker

    s = ranker.scores(prices, model, short, fund)  # short: + FINRA short selling; fund: + SEC fundamentals
    out = {}
    if s.empty:
        return {a: pd.Series(0, df.index) for a, df in prices.items()}
    wide_ = s.unstack("stock")
    pick = wide_.rank(axis=1, pct=True, ascending=False) <= top
    for a, df in prices.items():
        sig = pick[a].astype(int) if a in pick else pd.Series(0, pick.index)
        out[a] = sig.reindex(df.index).fillna(0).astype(int)
    return out


def insider_ml(prices: dict, model: str = "ridge", keep: float = 0.3) -> dict:
    """Insider clusters (2+ buyers in 90 days) that the ML scorer (algo/insider_ml.py) keeps: the
    `keep` share it rates best, each score from a model fitted only on clusters already over."""
    from . import insider_ml as iml

    k = iml.kept(prices, model, keep)
    k = k[k["keep"]] if len(k) else k
    out = {}
    for a, df in prices.items():
        days = pd.DatetimeIndex(k.loc[k["stock"] == a, "date"]) if len(k) else pd.DatetimeIndex([])
        out[a] = pd.Series(df.index.isin(days).astype(int), df.index)
    return out


def insider_low_short(prices: dict, buyers: int = 2, days: int = 90, max_rank: float = 0.5) -> dict:
    """Insider clusters where short sellers are NOT betting against the stock: the day a cluster
    forms (insider_cluster) and the stock's 20-day short share of off-exchange volume (FINRA, known
    from the next session) ranks in the lowest `max_rank` share of the S&P 1500 that day."""
    from . import wide

    sig = insider_cluster(prices, buyers=buyers, days=days)
    sv = wide.load_short_volume()
    if sv.empty:
        return {a: s * 0 for a, s in sig.items()}
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    sv = sv.reindex(index=idx, columns=list(prices)).shift(1)  # published after the close
    rank = sv.rolling(20, min_periods=10).mean().rank(axis=1, pct=True)
    return {a: (s * (rank[a].reindex(s.index) <= max_rank)).astype(int) for a, s in sig.items()}


WIDE_FAMILIES = {
    "insider_cluster": (insider_cluster, {"buyers": [2, 3], "days": [30, 90]}),
    "insider_big_buy": (insider_big_buy, {"min_value": [100_000, 500_000], "officer": [True, False]}),
    "momentum_12_1": (momentum_12_1, {"top": [0.05, 0.1]}),
    "reversal_5d": (reversal_5d, {"bottom": [0.02, 0.05]}),
    "high_52w": (high_52w, {"within": [0.01, 0.03]}),
    "insider_dip": (insider_dip, {"buyers": [2, 3], "days": [30, 90], "drop": [0.1, 0.2]}),
    "earnings_reaction": (earnings_reaction, {"z": [1.5, 2.5, 3.5], "volume": [1.5]},
                          {"rules": ["hold 20 days", "hold 40 days", "trailing 3 ATR, out in 60 days"]}),
    "earnings_overreaction": (earnings_overreaction, {"z": [1.5, 2.5, 3.5], "volume": [1.5]},
                              {"rules": ["hold 20 days", "hold 40 days", "trailing 3 ATR, out in 60 days"]}),
    # few versions on purpose (every one counts as a try): 2 models x 2 portfolio sizes, whole S&P 1500,
    # held one month (the horizon it is trained for)
    "ml_rank": (ml_rank, {"model": ["ridge", "gbm"], "top": [0.02, 0.05]},
                {"rules": ["hold 20 days"], "segments": ["sp1500"], "trend": False}),
    # the same ranker with FINRA short-selling features added (2026-10-05): its own 4 tries
    "ml_rank_short": (lambda prices, **p: ml_rank(prices, short=True, **p), {"model": ["ridge", "gbm"], "top": [0.02, 0.05]},
                      {"rules": ["hold 20 days"], "segments": ["sp1500"], "trend": False}),
    # the ranker with SEC fundamentals added too (2026-10-06): its own 4 tries
    "ml_rank_fund": (lambda prices, **p: ml_rank(prices, short=True, fund=True, **p), {"model": ["ridge", "gbm"], "top": [0.02, 0.05]},
                     {"rules": ["hold 20 days"], "segments": ["sp1500"], "trend": False}),
    # insider clusters where short sellers are not against the stock (FINRA short volume, 2026-10-05)
    "insider_low_short": (insider_low_short, {"buyers": [2, 3], "max_rank": [0.5, 0.3]},
                          {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                           "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insider clusters filtered by the ML scorer: 2 models x 2 shares kept, held the 60 sessions it is
    # trained for (wide stop: the model bets on the 3 months, not the first days)
    "insider_ml": (insider_ml, {"model": ["ridge", "gbm"], "keep": [0.5, 0.3]},
                   {"rules": {"hold 60 days": dict(stop_atr=4.0, rr=None, max_bars=60)}, "segments": ["sp1500"],
                    "trend": False}),
}
