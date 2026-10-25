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


def liquidity_sweep(prices: dict, n: int = 7, k: float = 0.0) -> dict:
    """Liquidity sweep (stop hunt, false breakout): the bar trades below the lowest low of the previous
    `n` bars, where the longs' stops sit, then closes back above it by at least `k` ATR: the selling
    ran out, buy (the mirror above the highs: sell). n=7 is about the previous session on stock bars."""
    out = {}
    for a, df in prices.items():
        lo, hi = df["Low"].rolling(n).min().shift(1), df["High"].rolling(n).max().shift(1)
        room = k * atr(df)
        up = (df["Low"] < lo) & (df["Close"] > lo + room)
        dn = (df["High"] > hi) & (df["Close"] < hi - room)
        out[a] = (up.astype(int) - dn.astype(int)).fillna(0).astype(int)
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
    # stop hunt below the recent lows / above the highs, then back inside (2026-10-20, user's idea)
    "liquidity_sweep": (liquidity_sweep, {"n": [7, 35], "k": [0.0, 0.25]}),
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


def insider_after_earnings(prices: dict, buyers: int = 2, window: int = 30, max_reaction: float = 0.0) -> dict:
    """Insiders buying right after their company's earnings: a cluster of open-market purchases
    (insider_cluster, 90 days) that forms within `window` sessions after an earnings release whose
    first-reaction session return was at most `max_reaction` (0.0: the market did not like it).
    Insiders may only trade in the window after results; buying after a bad reaction says they think
    the market got it wrong. Release times: SEC 8-K item 2.02 (wide.load_earnings); everything is
    known at the signal session's close."""
    from . import wide

    sig = insider_cluster(prices, buyers=buyers, days=90)
    e = wide.load_earnings()
    out = {}
    for a, df in prices.items():
        s = sig[a].to_numpy().copy()
        days = e.loc[e["ticker"] == a, "day"] if len(e) else []
        react = np.full(len(df), -1)  # the last earnings reaction session at or before each session
        if len(days):
            close = df["Close"].to_numpy()
            ret = np.r_[np.nan, close[1:] / close[:-1] - 1]
            for p in np.unique(df.index.searchsorted(pd.DatetimeIndex(days), side="left")):
                if 0 < p < len(df) and ret[p] <= max_reaction:
                    react[p] = p
            react = np.maximum.accumulate(react)
        idx = np.arange(len(df))
        ok = (react >= 0) & (idx - react <= window)
        out[a] = pd.Series((s.astype(bool) & ok).astype(int), df.index)
    return out


def insider_conviction(prices: dict, buyers: int = 2, min_bp: float = 5.0) -> dict:
    """Insider clusters where the insiders put real money in relative to the company's size: the day a
    cluster forms (insider_cluster, 90 days) and the dollars bought by insiders in those 90 days
    (filings up to that day) are at least `min_bp` basis points of the market value (shares outstanding
    from the last 10-Q / 10-K filed before that day, algo/fundamentals.py, times that day's close)."""
    from . import fundamentals

    sig = insider_cluster(prices, buyers=buyers, days=90)
    t = _insider("P")
    fd = fundamentals.load()
    shares = fd[fd["item"] == "shares"] if len(fd) else fd
    out = {}
    for a, df in prices.items():
        s = sig[a]
        days = s.index[s.to_numpy() > 0]
        keep = pd.Series(0, s.index)
        if len(days):
            g = t[t["ticker"] == a]
            sh = fundamentals._known(shares[shares["ticker"] == a], pd.DatetimeIndex(days)) if len(shares) else None
            for d in days:
                bought = g.loc[(g["filed"] > d - pd.Timedelta(days=90)) & (g["filed"] <= d), "value"].sum()
                n = sh.loc[d] if sh is not None else np.nan
                if n > 0 and bought / (n * df.at[d, "Close"]) * 1e4 >= min_bp:
                    keep.loc[d] = 1
        out[a] = keep.astype(int)
    return out


def insider_confirm(prices: dict, buyers: int = 2, wait: int = 20, ma: int = 50) -> dict:
    """Insider clusters, bought only once the price confirms them: after a cluster forms
    (insider_cluster, 90 days), the first session within `wait` sessions (the cluster day included)
    whose close crosses above its `ma`-session average. Insiders are often early; waiting for the
    turn should cut the trades that keep falling. One signal per cluster; closes up to that day only."""
    sig = insider_cluster(prices, buyers=buyers, days=90)
    out = {}
    for a, df in prices.items():
        close = df["Close"]
        avg = close.rolling(ma, min_periods=ma).mean()
        cross = ((close > avg) & (close.shift(1) <= avg.shift(1))).to_numpy()
        above = (close > avg).to_numpy()
        s = np.zeros(len(df), int)
        for p in np.flatnonzero(sig[a].to_numpy() > 0):
            hit = [q for q in range(p, min(p + wait, len(df))) if cross[q] or (q == p and above[q])]
            if hit:
                s[hit[0]] = 1
        out[a] = pd.Series(s, df.index)
    return out


def insider_sector_wave(prices: dict, buyers: int = 2, companies: int = 3, window: int = 30) -> dict:
    """Insider clusters that come in a sector-wide wave: the day a cluster forms (insider_cluster,
    90 days) and at least `companies` different companies of the same sector (this one included) had a
    cluster form within the last `window` calendar days. Insiders across a whole sector buying at once
    says more about the sector's next months than one company alone. Signals up to that day only."""
    from . import wide

    sig = insider_cluster(prices, buyers=buyers, days=90)
    sector = wide.sectors()
    days = {a: s.index[s.to_numpy() > 0] for a, s in sig.items()}
    by_sector: dict[str, list] = {}
    for a, ds in days.items():
        for d in ds:
            by_sector.setdefault(sector.get(a, "?"), []).append((d, a))
    out = {}
    for a, s in sig.items():
        keep = pd.Series(0, s.index)
        events = by_sector.get(sector.get(a, "?"), [])
        for d in days[a]:
            names = {b for (e, b) in events if d - pd.Timedelta(days=window) < e <= d}
            if len(names) >= companies and sector.get(a):
                keep.loc[d] = 1
        out[a] = keep.astype(int)
    return out


def insider_fresh(prices: dict, buyers: int = 2, gap: int = 730) -> dict:
    """Clusters of "opportunistic" insiders (Cohen, Malloy and Pomorski 2012): only purchases by an insider
    who had not bought this stock in the `gap` calendar days before count. Routine buyers (every year, same
    month) carry little news; an insider buying for the first time in years does. The day the number of
    distinct fresh buyers within 90 days reaches `buyers` (one signal per cluster). Filings up to that day
    only (the data starts in 2016: in the first `gap` days everyone looks fresh)."""
    return _fresh(prices, _insider("P"), buyers, gap)


def _fresh(prices: dict, t: pd.DataFrame, buyers: int, gap: int) -> dict:
    t = t.sort_values("filed") if len(t) else t
    if len(t):
        t = t.drop_duplicates(["ticker", "owner", "filed"])
        prev = t.groupby(["ticker", "owner"])["filed"].shift(1)
        t = t[prev.isna() | (t["filed"] - prev > pd.Timedelta(days=gap))]
    out = {}
    for a, df in prices.items():
        g = t[t["ticker"] == a] if len(t) else t
        s = np.zeros(len(df), int)
        last = pd.Timestamp("1900-01-01")
        for f in g["filed"].drop_duplicates() if len(g) else []:
            win = g[(g["filed"] > f - pd.Timedelta(days=90)) & (g["filed"] <= f)]
            if win["owner"].nunique() >= buyers and f - last > pd.Timedelta(days=90):
                p_ = _on_days(pd.Series([f]), df.index)[0]
                if p_ < len(df):
                    s[p_] = 1
                last = f
        out[a] = pd.Series(s, df.index)
    return out


def insider_fresh_officer(prices: dict, buyers: int = 1, gap: int = 365) -> dict:
    """insider_fresh, counting only officers (CEO, CFO, ... per the Form 4 role): the people who run the
    company and know its next quarters best. An officer buying for the first time in `gap` days, alone
    (`buyers`=1) or with another fresh officer within 90 days. Filings up to that day only."""
    t = _insider("P")
    if len(t):
        t = t[t["role"].fillna("").str.contains("Officer", case=False)]
    return _fresh(prices, t, buyers, gap)


def insider_fresh_wave(prices: dict, buyers: int = 2, companies: int = 3, window: int = 30) -> dict:
    """The two best 13/14 ideas together: a cluster of fresh insider buyers (insider_fresh, first purchase
    in 180 days) on a day when at least `companies` companies of the same sector (this one included) had
    an insider cluster (insider_cluster, 2 buyers in 90 days) within the last `window` calendar days.
    Each edge alone fails only the luck check; if they are partly independent, together they should
    keep the better trades. Filings and clusters up to that day only."""
    from . import wide

    fresh = insider_fresh(prices, buyers=buyers, gap=180)
    clusters = insider_cluster(prices, buyers=2, days=90)
    sector = wide.sectors()
    events: dict[str, list] = {}
    for a, sig in clusters.items():
        for d in sig.index[sig.to_numpy() > 0]:
            events.setdefault(sector.get(a, "?"), []).append((d, a))
    out = {}
    for a, sig in fresh.items():
        keep = pd.Series(0, sig.index)
        sec = sector.get(a)
        for d in sig.index[sig.to_numpy() > 0]:
            names = {b for (e, b) in events.get(sec, []) if d - pd.Timedelta(days=window) < e <= d}
            if sec and len(names | {a}) >= companies:
                keep.loc[d] = 1
        out[a] = keep.astype(int)
    return out


def insider_underwater(prices: dict, buyers: int = 2, discount: float = 0.10) -> dict:
    """Buy below the insiders' own price: the first close at least `discount` under the average price
    (value-weighted) that `buyers` or more distinct insiders paid in open-market purchases filed in the
    last 90 calendar days. Insiders rarely buy to lose; a stock trading well below where several of them
    just bought is either a mistake by them or a bargain. One signal per 90 days per stock; filings and
    closes up to that day only."""
    t = _insider("P")
    if len(t):
        t = t[(t["price"] > 0) & (t["shares"] > 0)].sort_values("filed")
    by = dict(tuple(t.groupby("ticker"))) if len(t) else {}
    out = {}
    for a, df in prices.items():
        s = np.zeros(len(df), int)
        g = by.get(a)
        if g is not None:
            filed = pd.DatetimeIndex(g["filed"]).normalize().to_numpy()
            val = np.concatenate([[0.0], np.cumsum((g["price"] * g["shares"]).to_numpy(float))])
            sh = np.concatenate([[0.0], np.cumsum(g["shares"].to_numpy(float))])
            owners = g["owner"].to_numpy()
            idx = df.index.to_numpy()
            hi = np.searchsorted(filed, idx, side="right")                            # filed <= d
            lo = np.searchsorted(filed, idx - np.timedelta64(90, "D"), side="right")  # filed > d - 90
            close = df["Close"].to_numpy(float)
            last = None
            for i in np.flatnonzero(hi > lo):
                d = df.index[i]
                if last is not None and d - last <= pd.Timedelta(days=90):
                    continue
                vwap = (val[hi[i]] - val[lo[i]]) / (sh[hi[i]] - sh[lo[i]])
                if close[i] <= vwap * (1 - discount) and len(set(owners[lo[i]:hi[i]])) >= buyers:
                    s[i] = 1
                    last = d
        out[a] = pd.Series(s, df.index)
    return out


def _once_per(days_sig: list, index: pd.DatetimeIndex, gap: int = 90) -> np.ndarray:
    """1 on each signal position (sorted, < len(index)), keeping one per `gap` calendar days."""
    s = np.zeros(len(index), int)
    last = None
    for i in sorted(set(days_sig)):
        if i >= len(index):
            break
        if last is None or index[i] - last > pd.Timedelta(days=gap):
            s[i] = 1
            last = index[i]
    return s


def insider_clean(prices: dict, buyers: int = 1, quiet: int = 180) -> dict:
    """Insider buying with no insider selling: the day `buyers` or more distinct insiders have filed
    open-market purchases within 30 days, while no insider sale (Form 4 code S) was filed in the `quiet`
    calendar days up to that day. Buying while colleagues also sell is often diversification noise; buying
    while nobody sells is a cleaner vote. One signal per 90 days per stock; filings up to that day only."""
    buys, sells = _insider("P"), _insider("S")
    bb = dict(tuple(buys.sort_values("filed").groupby("ticker"))) if len(buys) else {}
    ss = {a: pd.DatetimeIndex(g["filed"]).normalize().sort_values()
          for a, g in sells.groupby("ticker")} if len(sells) else {}
    out = {}
    for a, df in prices.items():
        g, hits = bb.get(a), []
        if g is not None:
            filed = pd.DatetimeIndex(g["filed"]).normalize()
            owners = g["owner"].to_numpy()
            sold = ss.get(a, pd.DatetimeIndex([]))
            for j, d in enumerate(filed):
                if len(set(owners[(filed > d - pd.Timedelta(days=30)) & (filed <= d)])) < buyers:
                    continue
                if ((sold > d - pd.Timedelta(days=quiet)) & (sold <= d)).any():
                    continue
                hits.append(int(_on_days(pd.Series([d]), df.index)[0]))
        out[a] = pd.Series(_once_per(hits, df.index), df.index)
    return out


def insider_repeat(prices: dict, buys: int = 2, window: int = 60) -> dict:
    """One insider coming back for more: the day the same person files their `buys`-th open-market
    purchase of the stock within `window` calendar days (separate filing days). Adding again after a
    first buy shows more conviction than a single purchase. One signal per 90 days per stock; filings up
    to that day only."""
    t = _insider("P")
    by = dict(tuple(t.sort_values("filed").groupby("ticker"))) if len(t) else {}
    out = {}
    for a, df in prices.items():
        g, hits = by.get(a), []
        if g is not None:
            for _, h in g.groupby("owner"):
                days = pd.DatetimeIndex(h["filed"]).normalize().unique().sort_values()
                for k in range(buys - 1, len(days)):
                    if days[k] - days[k - buys + 1] <= pd.Timedelta(days=window):
                        hits.append(int(_on_days(pd.Series([days[k]]), df.index)[0]))
        out[a] = pd.Series(_once_per(hits, df.index), df.index)
    return out


def insider_market_stress(prices: dict, buyers: int = 1, drop: float = 0.05) -> dict:
    """Insiders buying while the whole market is falling: an insider cluster (insider_cluster, 30 days)
    kept only when the median stock of the universe lost at least `drop` over the last 20 sessions
    (closes up to the signal day). Insiders who buy into a broad sell-off are betting on their own
    company, not on the market; forced selling by funds can push good stocks too low."""
    sig = insider_cluster(prices, buyers=buyers, days=30)
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    close = pd.DataFrame({a: df["Close"] for a, df in prices.items()}).reindex(idx)
    market = (close / close.shift(20) - 1).median(axis=1)
    stressed = market <= -drop
    return {a: (s.astype(bool) & stressed.reindex(s.index).fillna(False).to_numpy()).astype(int)
            for a, s in sig.items()}


TOP_TITLES = {"ceo": r"\bCEO\b|CHIEF EXECUTIVE",
              "ceo_cfo": r"\bCEO\b|CHIEF EXECUTIVE|\bCFO\b|CHIEF FINANCIAL"}


def insider_top_exec(prices: dict, min_value: float = 100_000, who: str = "ceo") -> dict:
    """The boss buys: an open-market purchase of at least `min_value` dollars (one filing day, summed)
    by the chief executive (who='ceo') or the chief executive or finance officer (who='ceo_cfo'), from
    the Form 4 title. They know the company best and buy with their own money. One signal per 90 days
    per stock; filings up to that day only."""
    t = _insider("P")
    if len(t):
        t = t[t["title"].fillna("").str.upper().str.contains(TOP_TITLES[who], regex=True)]
        t = t.assign(day=pd.DatetimeIndex(t["filed"]).normalize())
        t = t.groupby(["ticker", "owner", "day"], as_index=False)["value"].sum()
        t = t[t["value"] >= min_value]
    by = {a: g["day"] for a, g in t.groupby("ticker")} if len(t) else {}
    out = {}
    for a, df in prices.items():
        d = by.get(a)
        hits = list(_on_days(d, df.index)) if d is not None else []
        out[a] = pd.Series(_once_per(hits, df.index), df.index)
    return out


_VOTES_CACHE: dict = {}


def _insider_votes(prices: dict) -> dict:
    """Signals of five different insider ideas (one version each, chosen before this family existed),
    computed once per price panel."""
    key = (id(prices), len(prices))
    if key not in _VOTES_CACHE:
        _VOTES_CACHE.clear()
        _VOTES_CACHE[key] = {
            "fresh": insider_fresh(prices, buyers=2, gap=365),
            "underwater": insider_underwater(prices, buyers=1, discount=0.10),
            "top_exec": insider_top_exec(prices, min_value=100_000, who="ceo_cfo"),
            "clean": insider_clean(prices, buyers=1, quiet=180),
            "after_earnings": insider_after_earnings(prices, buyers=2, window=30)}
    return _VOTES_CACHE[key]


def insider_consensus(prices: dict, votes: int = 2, window: int = 20) -> dict:
    """Several insider ideas agree: the day at least `votes` of five different insider signals
    (fresh buyers, buying under the insiders' price, the CEO/CFO buying, buying while nobody sells,
    buying after a bad earnings reaction) have fired on the stock within the last `window` sessions.
    Each idea alone is close but fails the luck check; stocks where several agree should carry more
    edge per trade. One signal per 90 days per stock; every vote uses data up to its own day."""
    comp = _insider_votes(prices)
    out = {}
    for a, df in prices.items():
        fired = np.zeros(len(df), int)
        for c in comp.values():
            v = c[a].to_numpy() > 0
            fired += pd.Series(v).rolling(window, min_periods=1).max().to_numpy().astype(int)
        hits = list(np.flatnonzero(fired >= votes))
        out[a] = pd.Series(_once_per(hits, df.index), df.index)
    return out


def insider_deep_value(prices: dict, buyers: int = 1, below: float = 0.3) -> dict:
    """Insiders buying a stock far below its one-year high: an insider cluster (insider_cluster, 30
    days) on a day the close is at least `below` under the highest close of the last 252 sessions.
    Insiders buying after a long, deep fall are the classic contrarian signal (different from a
    short 20-day dip). Closes up to the signal day only."""
    sig = insider_cluster(prices, buyers=buyers, days=30)
    out = {}
    for a, df in prices.items():
        c = df["Close"]
        deep = (c <= c.rolling(252, min_periods=126).max() * (1 - below)).to_numpy()
        out[a] = pd.Series((sig[a].to_numpy().astype(bool) & deep).astype(int), df.index)
    return out


def insider_sector_laggard(prices: dict, buyers: int = 1, lag: float = 0.10) -> dict:
    """Insiders buying the laggard of its sector: an insider cluster (insider_cluster, 30 days) on a day
    the stock's 60-session return trails the median of its sector (wide.sectors) by at least `lag`.
    A stock that fell behind its peers is more likely company-specific bad news; insiders buying it
    say the news is overdone. Closes up to the signal day only."""
    from . import wide

    sig = insider_cluster(prices, buyers=buyers, days=30)
    sector = wide.sectors()
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    close = pd.DataFrame({a: df["Close"] for a, df in prices.items()}).reindex(idx)
    r60 = close / close.shift(60) - 1
    groups: dict[str, list] = {}
    for a in r60.columns:
        groups.setdefault(sector.get(a, "?"), []).append(a)
    by_group = {g: r60[cols].median(axis=1) for g, cols in groups.items()}
    med = pd.DataFrame({a: by_group[sector.get(a, "?")] for a in r60.columns})
    behind = (r60 <= med - lag) & pd.Series({a: bool(sector.get(a)) for a in r60.columns})
    return {a: (s.astype(bool) & behind[a].reindex(s.index).fillna(False).to_numpy()).astype(int)
            for a, s in sig.items()}


def insider_low_vol(prices: dict, buyers: int = 1, max_rank: float = 0.3) -> dict:
    """Insiders buying a quiet stock: an insider cluster (insider_cluster, 30 days) in a stock whose
    60-session volatility of daily returns ranks in the calmest `max_rank` of the universe that day.
    The same insider edge with less day-to-day noise should give a steadier result per trade (the luck
    check rewards a higher Sharpe, not a bigger average). Closes up to the signal day only."""
    sig = insider_cluster(prices, buyers=buyers, days=30)
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    close = pd.DataFrame({a: df["Close"] for a, df in prices.items()}).reindex(idx)
    vol = close.pct_change(fill_method=None).rolling(60, min_periods=40).std()
    calm = vol.rank(axis=1, pct=True) <= max_rank
    return {a: (s.astype(bool) & calm[a].reindex(s.index).fillna(False).to_numpy()).astype(int)
            for a, s in sig.items()}


def insider_high_short(prices: dict, buyers: int = 1, min_rank: float = 0.7) -> dict:
    """The opposite bet of insider_low_short: insiders buying a stock that short sellers ARE betting
    against, i.e. its 20-day short share of off-exchange volume (FINRA, known from the next session)
    ranks in the top `1 - min_rank` of the universe that day. When the insiders are right the shorts
    have to buy back (a squeeze). Insider cluster over 30 days; data up to the signal day only."""
    from . import wide

    sig = insider_cluster(prices, buyers=buyers, days=30)
    sv = wide.load_short_volume()
    if sv.empty:
        return {a: s * 0 for a, s in sig.items()}
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    sv = sv.reindex(index=idx, columns=list(prices)).shift(1)  # published after the close
    rank = sv.rolling(20, min_periods=10).mean().rank(axis=1, pct=True)
    return {a: (s * (rank[a].reindex(s.index) >= min_rank)).astype(int) for a, s in sig.items()}


def insider_momentum(prices: dict, buyers: int = 1, min_rank: float = 0.7) -> dict:
    """Insiders adding to a winner: an insider cluster (30 days) in a stock whose 120-session return
    ranks in the top `1 - min_rank` of the universe that day. Most insider ideas so far buy weakness;
    this one tests whether insiders buying strength (momentum + insider conviction) is steadier.
    Closes up to the signal day only."""
    sig = insider_cluster(prices, buyers=buyers, days=30)
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    close = pd.DataFrame({a: df["Close"] for a, df in prices.items()}).reindex(idx)
    rank = (close / close.shift(120) - 1).rank(axis=1, pct=True)
    strong = rank >= min_rank
    return {a: (s.astype(bool) & strong[a].reindex(s.index).fillna(False).to_numpy()).astype(int)
            for a, s in sig.items()}


def insider_turn(prices: dict, buyers: int = 1, window: int = 20) -> dict:
    """Insiders bought a falling stock; wait for the turn: an insider cluster (30 days) on a day the
    close is under its 50-session average, then the signal is the first close back above the 20-session
    average within `window` sessions after it (none: no trade). The near-misses buy weakness at once and
    fail on decay and shelf life; waiting for the price to agree should skip the falling knives.
    Closes up to the signal day only."""
    sig = insider_cluster(prices, buyers=buyers, days=30)
    out = {}
    for a, df in prices.items():
        c = df["Close"]
        ma20 = c.rolling(20, min_periods=20).mean()
        weak = (c < c.rolling(50, min_periods=50).mean()).to_numpy()
        cross = ((c > ma20) & (c.shift(1) <= ma20.shift(1))).to_numpy()
        s = np.zeros(len(df), int)
        for i in np.flatnonzero(sig[a].to_numpy().astype(bool) & weak):
            after = np.flatnonzero(cross[i + 1:i + 1 + window])
            if len(after):
                s[i + 1 + after[0]] = 1
        out[a] = pd.Series(s, df.index)
    return out


def _opportunistic(t: pd.DataFrame, years: int) -> pd.DataFrame:
    """The purchases that break the insider's habit: not routine, where routine means the same insider
    bought the same stock in the same calendar month in each of the `years` previous years (Cohen-
    Malloy-Pomorski 2012). Only filings of earlier years decide."""
    if not len(t):
        return t
    t = t.assign(year=t["filed"].dt.year, month=t["filed"].dt.month)
    seen = set(zip(t["ticker"], t["owner"], t["year"], t["month"]))
    routine = np.array([all((tk, ow, y - k, m) in seen for k in range(1, years + 1))
                        for tk, ow, y, m in zip(t["ticker"], t["owner"], t["year"], t["month"])], bool)
    return t[~routine]


def _clusters(t: pd.DataFrame, prices: dict, buyers: int, days: int = 30) -> dict:
    """The day `buyers` distinct insiders have bought within `days` days (one signal per cluster)."""
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


def insider_opportunistic(prices: dict, buyers: int = 1, years: int = 2) -> dict:
    """Insider buys that break the insider's habit (Cohen-Malloy-Pomorski 2012): a purchase is routine
    when the same insider also bought the same stock in the same calendar month in each of the `years`
    previous years (a yearly plan, no news in it), opportunistic otherwise. Signal: the day `buyers`
    distinct insiders have bought opportunistically within 30 days (one signal per cluster). Only
    filings of earlier years decide what is routine."""
    return _clusters(_opportunistic(_insider("P"), years), prices, buyers)


def insider_opportunistic_low_short(prices: dict, buyers: int = 1, max_rank: float = 0.3) -> dict:
    """The two best ideas together: an opportunistic insider cluster (insider_opportunistic, 1 year of
    habit) in a stock short sellers are not betting against (20-day short share of off-exchange volume,
    FINRA, known from the next session, in the lowest `max_rank` of the universe that day; account D's
    filter). Two independent votes should give a steadier edge, the luck check's weak point."""
    from . import wide

    sig = insider_opportunistic(prices, buyers=buyers, years=1)
    sv = wide.load_short_volume()
    if sv.empty:
        return {a: s * 0 for a, s in sig.items()}
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    sv = sv.reindex(index=idx, columns=list(prices)).shift(1)  # published after the close
    rank = sv.rolling(20, min_periods=10).mean().rank(axis=1, pct=True)
    return {a: (s * (rank[a].reindex(s.index) <= max_rank)).astype(int) for a, s in sig.items()}


def insider_opportunistic_exec(prices: dict, who: str = "ceo_cfo", years: int = 1) -> dict:
    """The boss breaks the habit: an opportunistic purchase (insider_opportunistic) by the chief
    executive (who='ceo') or the chief executive or finance officer ('ceo_cfo'), from the Form 4 title.
    One signal per 30 days per stock."""
    t = _opportunistic(_insider("P"), years)
    if len(t):
        t = t[t["title"].fillna("").str.upper().str.contains(TOP_TITLES[who], regex=True)]
    return _clusters(t, prices, buyers=1)


def insider_opportunistic_wave(prices: dict, companies: int = 3, window: int = 30) -> dict:
    """The best campaign (insider_sector_wave) and the newest 13/14 (insider_opportunistic) together: an
    opportunistic insider buy (1 year of habit) on a day when at least `companies` companies of the same
    sector (this one included) had an opportunistic insider buy within the last `window` calendar days.
    Insiders across a sector breaking their habits at once is news about the sector, not one company's
    yearly plan. Filings up to that day only."""
    from . import wide

    sig = insider_opportunistic(prices, buyers=1, years=1)
    sector = wide.sectors()
    events: dict[str, list] = {}
    for a, s in sig.items():
        for d in s.index[s.to_numpy() > 0]:
            events.setdefault(sector.get(a, "?"), []).append((d, a))
    out = {}
    for a, s in sig.items():
        keep = pd.Series(0, s.index)
        sec = sector.get(a)
        for d in s.index[s.to_numpy() > 0]:
            names = {b for (e, b) in events.get(sec, []) if d - pd.Timedelta(days=window) < e <= d}
            if sec and len(names | {a}) >= companies:
                keep.loc[d] = 1
        out[a] = keep.astype(int)
    return out


def momentum_low_short(prices: dict, top: float = 0.1, max_rank: float = 0.3) -> dict:
    """Market data only, no insiders: momentum winners short sellers stay away from. At each month end,
    the stocks in the top `top` share of the 12-month return skipping the last month (momentum_12_1)
    whose 20-day short share of off-exchange volume (FINRA, known from the next session) ranks in the
    lowest `max_rank` of the universe that day. Heavily shorted stocks do worse (Boehmer-Jones-Zhang
    2008); the winners nobody bets against should keep momentum's edge with fewer of its crashes."""
    from . import wide

    sig = momentum_12_1(prices, top=top)
    sv = wide.load_short_volume()
    if sv.empty:
        return {a: s * 0 for a, s in sig.items()}
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    sv = sv.reindex(index=idx, columns=list(prices)).shift(1)  # published after the close
    rank = sv.rolling(20, min_periods=10).mean().rank(axis=1, pct=True)
    return {a: (s * (rank[a].reindex(s.index) <= max_rank)).astype(int) for a, s in sig.items()}


def insider_wave_low_short(prices: dict, companies: int = 3, max_rank: float = 0.3) -> dict:
    """The best campaign with account D's filter: an insider cluster during a sector-wide wave of insider
    buying (insider_sector_wave, 2 buyers) in a stock short sellers are not betting against (20-day short
    share of off-exchange volume, FINRA, known from the next session, in the lowest `max_rank` that day)."""
    from . import wide

    sig = insider_sector_wave(prices, buyers=2, companies=companies)
    sv = wide.load_short_volume()
    if sv.empty:
        return {a: s * 0 for a, s in sig.items()}
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    sv = sv.reindex(index=idx, columns=list(prices)).shift(1)  # published after the close
    rank = sv.rolling(20, min_periods=10).mean().rank(axis=1, pct=True)
    return {a: (s * (rank[a].reindex(s.index) <= max_rank)).astype(int) for a, s in sig.items()}


def sector_momentum(prices: dict, top: int = 3, ma: int = 200) -> dict:
    """Market data only: account B's idea (trend + momentum, monthly) inside the stock market. At each
    month end, rank the sectors by the median 12-1 month return of their stocks; buy the stocks of the
    `top` sectors that trade above their own `ma`-day average. Closes up to that day only."""
    from . import wide

    close = _panel(prices)
    ret = close.shift(21) / close.shift(252) - 1
    sector = pd.Series({a: wide.sectors().get(a) for a in close.columns}).dropna()
    med = ret[sector.index].T.groupby(sector).median().T                       # date x sector
    best = med.rank(axis=1, ascending=False, method="first") <= top
    in_best = pd.DataFrame({a: best[sector[a]] for a in sector.index}, index=close.index).reindex(columns=close.columns,
                                                                                                   fill_value=False)
    above = close > close.rolling(ma, min_periods=ma).mean()
    month_end = close.index.to_series().dt.to_period("M") != close.index.to_series().shift(-1).dt.to_period("M")
    return _own((in_best & above & month_end.to_numpy()[:, None]).astype(int), prices)


def insider_sector_stress(prices: dict, buyers: int = 1, drop: float = 0.10) -> dict:
    """Insiders buying while their own sector is falling: an insider cluster (insider_cluster, 30 days)
    kept only when the median stock of the same sector lost at least `drop` over the last 60 sessions
    (closes up to the signal day). insider_market_stress (11/14) on the whole market; here the sell-off
    is the sector's, where forced selling hits a company's peers too."""
    from . import wide

    sig = insider_cluster(prices, buyers=buyers, days=30)
    close = _panel(prices)
    ret = close / close.shift(60) - 1
    sector = pd.Series({a: wide.sectors().get(a) for a in close.columns}).dropna()
    med = ret[sector.index].T.groupby(sector).median().T                       # date x sector
    out = {}
    for a, s in sig.items():
        sec = sector.get(a)
        if sec is None:
            out[a] = s * 0
            continue
        fell = (med[sec] <= -drop).reindex(s.index).fillna(False).to_numpy()
        out[a] = (s.astype(bool) & fell).astype(int)
    return out


def momentum_low_vol(prices: dict, top: float = 0.1, max_vol: float = 0.5) -> dict:
    """Market data only: momentum without the jumpy stocks. At each month end, the stocks in the top `top`
    share of the 12-1 month return whose 60-day volatility ranks in the lowest `max_vol` of the universe.
    Steady winners keep winning more reliably than winners made by a few big jumps (Da-Gurun-Warachka
    2014, "frog in the pan"); calmer stocks also cut momentum's crashes. Closes up to that day only."""
    close = _panel(prices)
    ret = close.shift(21) / close.shift(252) - 1
    vol = np.log(close / close.shift(1)).rolling(60, min_periods=60).std()
    winners = ret.rank(axis=1, pct=True, ascending=False) <= top
    calm = vol.rank(axis=1, pct=True) <= max_vol
    month_end = close.index.to_series().dt.to_period("M") != close.index.to_series().shift(-1).dt.to_period("M")
    return _own((winners & calm & month_end.to_numpy()[:, None]).astype(int), prices)


def overnight_momentum(prices: dict, lookback: int = 20, top: float = 0.1) -> dict:
    """Market data only: stocks whose gains come overnight (close to next open) keep outperforming
    (Lou-Polk-Skouras 2019: overnight returns carry the persistent buying, intraday ones the noise).
    Each Friday, buy the stocks in the top `top` share of the sum of the last `lookback` overnight
    returns. Opens and closes up to the signal day only."""
    close, open_ = _panel(prices), _panel(prices, "Open")
    night = np.log(open_ / close.shift(1)).rolling(lookback, min_periods=lookback).sum()
    rank = night.rank(axis=1, pct=True, ascending=False)
    friday = close.index.dayofweek == 4
    return _own(((rank <= top) & friday[:, None]).astype(int), prices)


def insider_accumulation(prices: dict, buyers: int = 1, volume: float = 2.0) -> dict:
    """Insiders bought and the market follows: within 10 sessions after an insider cluster (30 days),
    the first up day (close above the day before) on at least `volume` times the stock's usual volume
    (average of the 50 sessions before that day). Big buyers joining the insiders is a second, independent
    vote. Closes and volumes up to the signal day only."""
    sig = insider_cluster(prices, buyers=buyers, days=30)
    out = {}
    for a, df in prices.items():
        c, v = df["Close"], df["Volume"].astype(float)
        usual = v.rolling(50, min_periods=50).mean().shift(1)
        heavy = ((v >= volume * usual) & (c > c.shift(1))).to_numpy()
        s = np.zeros(len(df), int)
        for i in np.flatnonzero(sig[a].to_numpy().astype(bool)):
            after = np.flatnonzero(heavy[i + 1:i + 11])
            if len(after):
                s[i + 1 + after[0]] = 1
        out[a] = pd.Series(s, df.index)
    return out


def insider_fund(prices: dict, buyers: int = 2, feature: str = "f_sue", min_rank: float = 0.5) -> dict:
    """Insider clusters in companies whose last filed fundamentals look good: the day a cluster forms
    (insider_cluster, 90 days) and the stock's `feature` (algo/fundamentals.py: f_sue = earnings
    surprise vs a year earlier, f_ey = earnings yield) ranks in the top `1 - min_rank` of the S&P 1500
    that day. Fundamentals count from the session after their 10-Q / 10-K was filed."""
    from . import fundamentals

    sig = insider_cluster(prices, buyers=buyers, days=90)
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in prices.values()))))
    close = pd.DataFrame({a: df["Close"] for a, df in prices.items()}).reindex(idx)
    f = fundamentals.features(idx, close)[feature]
    rank = f.rank(axis=1, pct=True)
    return {a: (s * (rank[a].reindex(s.index) >= min_rank)).astype(int) for a, s in sig.items()}


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
    # insider clusters in companies that just beat (SUE) or are cheap on earnings (SEC XBRL, 2026-10-06)
    "insider_fund": (insider_fund, {"buyers": [2, 3], "feature": ["f_sue", "f_ey"]},
                     {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                      "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insider clusters right after an earnings release the market did not like (2026-10-07)
    "insider_after_earnings": (insider_after_earnings, {"buyers": [2, 3], "window": [20, 40]},
                               {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                                "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insider clusters with real money relative to the company's size (2026-10-08)
    "insider_conviction": (insider_conviction, {"buyers": [2, 3], "min_bp": [2.0, 10.0]},
                           {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                            "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insider clusters bought once the price turns up through its average (2026-10-09)
    "insider_confirm": (insider_confirm, {"buyers": [2, 3], "wait": [10, 30]},
                        {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                         "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insider clusters in a sector-wide wave of insider buying (2026-10-10)
    "insider_sector_wave": (insider_sector_wave, {"buyers": [2, 3], "companies": [3, 5]},
                            {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                             "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # clusters of insiders buying for the first time in 1-2 years ("opportunistic", 2026-10-11)
    "insider_fresh": (insider_fresh, {"buyers": [1, 2], "gap": [365, 730]},
                      {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                       "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # the same, officers only (CEO, CFO...) (2026-10-12)
    "insider_fresh_officer": (insider_fresh_officer, {"buyers": [1, 2], "gap": [180, 365]},
                              {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                               "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # fresh insider buyers during a sector-wide wave of insider clusters (2026-10-13)
    "insider_fresh_wave": (insider_fresh_wave, {"buyers": [1, 2], "companies": [3, 5]},
                           {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                            "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # buying below the price several insiders just paid (2026-10-14)
    "insider_underwater": (insider_underwater, {"buyers": [1, 2], "discount": [0.05, 0.15]},
                           {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                            "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insider buying while no insider sells (2026-10-15)
    "insider_clean": (insider_clean, {"buyers": [1, 2], "quiet": [180, 365]},
                      {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                       "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # the same insider buying again within weeks (2026-10-15)
    "insider_repeat": (insider_repeat, {"buys": [2, 3], "window": [30, 90]},
                       {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                        "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insiders buying while the whole market sells off (2026-10-16)
    "insider_market_stress": (insider_market_stress, {"buyers": [1, 2], "drop": [0.03, 0.06]},
                              {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                               "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # the CEO (or CFO) buying with their own money (2026-10-16)
    "insider_top_exec": (insider_top_exec, {"min_value": [100_000, 500_000], "who": ["ceo", "ceo_cfo"]},
                         {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                          "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # several insider ideas agreeing on the same stock (2026-10-17)
    "insider_consensus": (insider_consensus, {"votes": [2, 3], "window": [10, 30]},
                          {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                           "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insiders buying 30-50% under the one-year high (2026-10-17)
    "insider_deep_value": (insider_deep_value, {"buyers": [1, 2], "below": [0.3, 0.5]},
                           {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                            "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insiders buying the laggard of its sector (2026-10-18)
    "insider_sector_laggard": (insider_sector_laggard, {"buyers": [1, 2], "lag": [0.10, 0.20]},
                               {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                                "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insiders buying calm, low-volatility stocks (2026-10-18)
    "insider_low_vol": (insider_low_vol, {"buyers": [1, 2], "max_rank": [0.3, 0.5]},
                        {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                         "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insiders buying heavily shorted stocks: the squeeze (2026-10-19)
    "insider_high_short": (insider_high_short, {"buyers": [1, 2], "min_rank": [0.7, 0.9]},
                           {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                            "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insiders buying the year's strong performers (2026-10-19)
    "insider_momentum": (insider_momentum, {"buyers": [1, 2], "min_rank": [0.7, 0.9]},
                         {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                          "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insiders bought a falling stock: buy when the price turns back up (2026-10-20)
    "insider_turn": (insider_turn, {"buyers": [1, 2], "window": [10, 20]},
                     {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                      "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insider buys that break the insider's yearly habit (2026-10-21)
    "insider_opportunistic": (insider_opportunistic, {"buyers": [1, 2], "years": [2, 3]},
                              {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                               "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # opportunistic insider buys where short sellers are not against the stock (2026-10-22)
    "insider_opportunistic_low_short": (insider_opportunistic_low_short, {"buyers": [1, 2], "max_rank": [0.3, 0.5]},
                                        {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                                         "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # the CEO or CFO breaking the habit (2026-10-22)
    "insider_opportunistic_exec": (insider_opportunistic_exec, {"who": ["ceo", "ceo_cfo"], "years": [1, 2]},
                                   {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                                    "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # opportunistic insider buys in a sector-wide wave of them (2026-10-23)
    "insider_opportunistic_wave": (insider_opportunistic_wave, {"companies": [3, 5], "window": [30, 60]},
                                   {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                                    "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # market and FINRA data only: momentum winners short sellers avoid, monthly (2026-10-23)
    "momentum_low_short": (momentum_low_short, {"top": [0.05, 0.1], "max_rank": [0.3, 0.5]},
                           {"rules": ["hold 20 days", "trailing 3 ATR, out in 60 days"],
                            "segments": ["sp1500"], "trend": False}),
    # insider waves where short sellers are not against the stock (2026-10-24)
    "insider_wave_low_short": (insider_wave_low_short, {"companies": [3, 5], "max_rank": [0.3, 0.5]},
                               {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                                "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # market data only: the strongest sectors' stocks above their average, monthly (2026-10-24)
    "sector_momentum": (sector_momentum, {"top": [2, 3], "ma": [100, 200]},
                        {"rules": ["hold 20 days", "trailing 3 ATR, out in 60 days"],
                         "segments": ["sp1500"], "trend": False}),
    # insider clusters while the stock's own sector sells off (2026-10-25)
    "insider_sector_stress": (insider_sector_stress, {"buyers": [1, 2], "drop": [0.08, 0.15]},
                              {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                               "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # market data only: steady momentum winners (low volatility), monthly (2026-10-25)
    "momentum_low_vol": (momentum_low_vol, {"top": [0.05, 0.1], "max_vol": [0.3, 0.5]},
                         {"rules": ["hold 20 days", "trailing 3 ATR, out in 60 days"],
                          "segments": ["sp1500"], "trend": False}),
    # market data only: overnight-return momentum, weekly (2026-10-21)
    "overnight_momentum": (overnight_momentum, {"lookback": [20, 60], "top": [0.05, 0.1]},
                           {"rules": ["hold 20 days", "trailing 3 ATR, out in 60 days"],
                            "segments": ["sp1500"], "trend": False}),
    # insiders bought, then a heavy-volume up day: big buyers follow (2026-10-20)
    "insider_accumulation": (insider_accumulation, {"buyers": [1, 2], "volume": [1.5, 2.5]},
                             {"rules": ["hold 40 days", "trailing 3 ATR, out in 60 days"],
                              "segments": ["sp1500", "sector:Industrials"], "trend": False}),
    # insider clusters filtered by the ML scorer: 2 models x 2 shares kept, held the 60 sessions it is
    # trained for (wide stop: the model bets on the 3 months, not the first days)
    "insider_ml": (insider_ml, {"model": ["ridge", "gbm"], "keep": [0.5, 0.3]},
                   {"rules": {"hold 60 days": dict(stop_atr=4.0, rr=None, max_bars=60)}, "segments": ["sp1500"],
                    "trend": False}),
}
