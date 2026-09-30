"""Core holdings: own the assets that are already winning, for months at a time.

The honest version of "buying NVDA in 2017". Nobody could know in 2017 that
NVDA would rise 100x, but anyone could see it was one of the strongest stocks
of the previous year. This sleeve picks assets on exactly that kind of public,
point-in-time evidence:

- Universe fixed in advance: the large US tech/growth stocks of end-2016 (the
  laggards included: Intel, IBM, Cisco...), plus bitcoin, ether, gold, silver.
- Every month end: rank by 12-month return excluding the last month (the
  classic momentum signal), keep only assets above their 200-day average,
  optionally drop those whose news tone collapsed, and hold the top 5.
- Weights: inverse volatility (calmer assets get more money), fully invested
  at most, no leverage. Trades at the next close, costs on every rebalance.

Skill test: the same rules with 5 random picks each month.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from . import data

log = logging.getLogger(__name__)

# Largest US tech / growth names at the end of 2016 (not today's winners),
# plus the non-equity assets of the trading system.
CORE_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "AMD", "INTC", "CSCO", "ORCL", "IBM", "QCOM",
               "TXN", "ADBE", "CRM", "NFLX", "TSLA", "AVGO", "MU", "PYPL"]
CORE_OTHER = {"BTC": "BTC-USD", "ETH": "ETH-USD", "GOLD": "GLD", "SILVER": "SLV"}
TOP_N = 5
COST_BPS = {"crypto": 15.0, "other": 4.0}  # fee + slippage per side


def load_universe(source: str = "auto") -> pd.DataFrame:
    """Daily closes on the US trading calendar (crypto sampled on those days)."""
    for s in CORE_STOCKS:
        data.TICKERS.setdefault(s, s)
    closes = {}
    for name in CORE_STOCKS + list(CORE_OTHER):
        try:
            closes[name] = data.load(name, source)["Close"]
        except Exception as exc:
            log.warning("skipping %s (%s)", name, exc)
    spy_days = data.load("SPY", source).index
    px = pd.concat(closes, axis=1, sort=True).ffill().reindex(spy_days)
    return px


def momentum_weights(px: pd.DataFrame, top_n: int = TOP_N, news_tone: pd.DataFrame | None = None,
                     rng: np.random.Generator | None = None) -> pd.DataFrame:
    """Target weights decided at each month end (row = decision date)."""
    month_ends = px.groupby([px.index.year, px.index.month]).tail(1).index
    mom = px.shift(21) / px.shift(252) - 1  # 12-1 month return
    above = px > px.rolling(200).mean()
    vol = px.pct_change().rolling(60).std()
    rows = {}
    for d in month_ends:
        ok = mom.loc[d].notna() & above.loc[d] & vol.loc[d].notna()
        if news_tone is not None and d in news_tone.index:
            bad = news_tone.loc[d].reindex(px.columns) < -1.5  # tone collapsed vs its own history
            ok &= ~bad.fillna(False)
        cands = mom.loc[d][ok]
        if rng is not None:  # random twin: same number of picks, any listed asset
            listed = px.loc[d].notna() & vol.loc[d].notna()
            pool = list(listed[listed].index)
            picks = list(rng.choice(pool, size=min(len(cands.nlargest(top_n)), len(pool)), replace=False))
        else:
            picks = list(cands.nlargest(top_n).index)
        w = pd.Series(0.0, index=px.columns)
        if picks:
            inv = 1 / vol.loc[d, picks]
            w[picks] = inv / inv.sum()
        rows[d] = w
    return pd.DataFrame(rows).T


def backtest_core(px: pd.DataFrame, weights: pd.DataFrame, start=None, end=None,
                  capital: float = 100_000.0) -> tuple[pd.Series, pd.DataFrame]:
    """Close-to-close returns; weights from a decision date apply from the next day."""
    rets = px.pct_change().fillna(0.0)
    held = weights.reindex(px.index).ffill().shift(1).fillna(0.0)  # decided at close, earn from next bar
    # weights drift with prices between rebalances
    w = held.copy()
    port = np.zeros(len(px))
    cur = np.zeros(px.shape[1])
    cost = np.array([COST_BPS["crypto"] if c in ("BTC", "ETH") else COST_BPS["other"] for c in px.columns]) / 1e4
    reb_days = set(weights.index)
    r = rets.to_numpy()
    target = held.to_numpy()
    idx = px.index
    for i in range(len(px)):
        if i > 0 and idx[i - 1] in reb_days:  # rebalance at yesterday's close
            trade = np.abs(target[i] - cur)
            port[i] -= (trade * cost).sum()
            cur = target[i].copy()
        day = (cur * r[i]).sum()
        port[i] += day
        growth = cur * (1 + r[i])
        cur = growth / (1 + day) if (1 + day) > 0 else growth
        w.iloc[i] = cur
    eq = capital * pd.Series(1 + port, idx).cumprod()
    eq = eq.loc[start:end]
    return eq / eq.iloc[0] * capital, w.loc[start:end]


def holdings_by_year(weights: pd.DataFrame) -> pd.DataFrame:
    """How many month-ends each asset was held, per year."""
    held = (weights > 0).astype(int)
    by_year = held.groupby(held.index.year).sum()
    return by_year.loc[:, by_year.sum() > 0]
