"""Performance statistics."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .engine import Result


def equity_stats(equity: pd.Series, periods_per_year: int) -> dict[str, float]:
    rets = equity.pct_change().dropna()
    years = len(rets) / periods_per_year
    total = equity.iloc[-1] / equity.iloc[0] - 1
    cagr = (1 + total) ** (1 / years) - 1 if years > 0 and total > -1 else np.nan
    vol = rets.std() * np.sqrt(periods_per_year)
    downside = rets[rets < 0].std() * np.sqrt(periods_per_year)
    dd = equity / equity.cummax() - 1
    max_dd = dd.min()
    return {
        "final_equity": equity.iloc[-1],
        "total_return": total,
        "cagr": cagr,
        "volatility": vol,
        "sharpe": rets.mean() / rets.std() * np.sqrt(periods_per_year) if rets.std() > 0 else np.nan,
        "sortino": rets.mean() * periods_per_year / downside if downside > 0 else np.nan,
        "max_drawdown": max_dd,
        "calmar": cagr / abs(max_dd) if max_dd < 0 else np.nan,
    }


def trade_stats(result: Result) -> dict[str, float]:
    t = result.trades_df
    exposure = result.exposure.abs().mean() if result.exposure is not None else np.nan
    if t.empty:
        return {"trades": 0, "shorts": 0, "win_rate": np.nan, "avg_r": np.nan, "profit_factor": np.nan,
                "fees": 0.0, "exposure": exposure}
    wins, losses = t.loc[t.pnl > 0, "pnl"], t.loc[t.pnl <= 0, "pnl"]
    return {
        "trades": len(t),
        "shorts": int((t.side < 0).sum()),
        "win_rate": len(wins) / len(t),
        "avg_r": t.r_multiple.mean(),  # expectancy per trade, in units of risk, after costs
        "profit_factor": wins.sum() / -losses.sum() if losses.sum() < 0 else np.inf,
        "fees": t.fees.sum(),  # exchange fees + short borrow, in $
        "exposure": exposure,
    }


def alpha_beta(strategy: pd.Series, benchmark: pd.Series, periods_per_year: int) -> dict[str, float]:
    """Jensen's alpha (annualised) and beta of strategy returns vs a benchmark,
    plus the information ratio of the excess returns."""
    s, b = strategy.pct_change(), benchmark.reindex(strategy.index).ffill().pct_change()
    df = pd.concat([s, b], axis=1).dropna()
    if len(df) < 20 or df.iloc[:, 1].var() == 0:
        return {"alpha": np.nan, "beta": np.nan, "info_ratio": np.nan}
    beta = df.cov().iloc[0, 1] / df.iloc[:, 1].var()
    alpha = (df.iloc[:, 0].mean() - beta * df.iloc[:, 1].mean()) * periods_per_year
    active = df.iloc[:, 0] - df.iloc[:, 1]
    ir = active.mean() / active.std() * np.sqrt(periods_per_year) if active.std() > 0 else np.nan
    return {"alpha": alpha, "beta": beta, "info_ratio": ir}


def summarize(result: Result, periods_per_year: int, benchmark: pd.Series | None = None) -> dict[str, float]:
    out = equity_stats(result.equity, periods_per_year) | trade_stats(result)
    if benchmark is not None:
        out |= alpha_beta(result.equity, benchmark, periods_per_year)
    return out
