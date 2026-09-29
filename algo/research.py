"""Test plan: in-sample tuning, out-of-sample tests and walk-forward analysis."""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .engine import Costs, ExitRule, Result, backtest
from .metrics import summarize

# Transaction costs per asset, per side.
# BTC: typical exchange taker fee + spread. GLD: low commission + tight spread.
COSTS = {
    "BTC": Costs(fee_bps=10, slippage_bps=5),
    "GOLD": Costs(fee_bps=1, slippage_bps=2),
    "SPY": Costs(fee_bps=1, slippage_bps=1),
}

# Exit rules searched on the training period only. 6:2 is the same ratio as
# 3:1; what differs between assets is how wide the stop is (in ATRs).
STOP_ATR_GRID = (1.5, 2.0, 2.5, 3.0)
RR_GRID = (1.5, 2.0, 3.0, 4.0)
BASELINE_EXIT = ExitRule(stop_atr=2.0, rr=3.0)

MIN_TRADES = 10  # a parameter set with fewer trades in training is not trusted
RISK_PCT = 0.01
INITIAL_CAPITAL = 100_000.0


@dataclass(frozen=True)
class Period:
    name: str
    start: str
    end: str | None


def periods(last_date: pd.Timestamp) -> dict[str, Period]:
    """The fixed test calendar. Nothing after TRAIN is used for tuning."""
    return {
        "full_10y": Period("Full 10 years", str((last_date - pd.DateOffset(years=10)).date()), None),
        "train": Period("Train (tuning)", str((last_date - pd.DateOffset(years=10)).date()), "2022-12-31"),
        "test": Period("Test 2023-2025 (hold-out)", "2023-01-01", "2025-12-31"),
        "ytd": Period("2026 YTD", "2026-01-01", None),
        "last_month": Period("Last month", str((last_date - pd.DateOffset(months=1)).date()), None),
    }


def run(df, entries, exit_rule, asset, start, end) -> Result:
    return backtest(
        df, entries, exit_rule, COSTS[asset], INITIAL_CAPITAL, RISK_PCT, start=start, end=end
    )


def grid_search(df, entries, asset, ppy, start, end) -> pd.DataFrame:
    """Sharpe, CAGR, max DD and trade count for every exit rule on one window."""
    rows = []
    for stop_atr, rr in itertools.product(STOP_ATR_GRID, RR_GRID):
        rule = ExitRule(stop_atr, rr)
        s = summarize(run(df, entries, rule, asset, start, end), ppy)
        rows.append({"stop_atr": stop_atr, "rr": rr, **s})
    return pd.DataFrame(rows)


def pick_best(grid: pd.DataFrame) -> ExitRule:
    ok = grid[(grid.trades >= MIN_TRADES) & grid.sharpe.notna()]
    if ok.empty:
        return BASELINE_EXIT
    best = ok.loc[ok.sharpe.idxmax()]
    return ExitRule(float(best.stop_atr), float(best.rr))


def walk_forward(df, entries, asset, ppy, first_test_year: int, train_years: int = 4) -> tuple[pd.Series, pd.DataFrame]:
    """Each calendar year, re-tune the exit rule on the previous `train_years`
    years, then trade the year out-of-sample. Returns the chained OOS equity
    curve and the rule chosen each year."""
    last_year = df.index[-1].year
    chunks, chosen = [], []
    equity_level = INITIAL_CAPITAL
    for year in range(first_test_year, last_year + 1):
        tr_start, tr_end = f"{year - train_years}-01-01", f"{year - 1}-12-31"
        if pd.Timestamp(tr_start) < df.index[0] + pd.Timedelta(days=250):
            continue  # not enough warm-up history
        rule = pick_best(grid_search(df, entries, asset, ppy, tr_start, tr_end))
        res = run(df, entries, rule, asset, f"{year}-01-01", f"{year}-12-31")
        scaled = res.equity / res.equity.iloc[0] * equity_level
        equity_level = scaled.iloc[-1]
        chunks.append(scaled)
        s = summarize(res, ppy)
        chosen.append({"year": year, "stop_atr": rule.stop_atr, "rr": rule.rr,
                       "return": s["total_return"], "trades": s["trades"]})
    if not chunks:
        return pd.Series(dtype=float), pd.DataFrame(chosen)
    eq = pd.concat(chunks)
    eq = eq[~eq.index.duplicated(keep="first")]
    return eq, pd.DataFrame(chosen)


def synthetic_prices(name: str, start: str = "2014-01-01", end: str = "2026-09-29", seed: int = 0) -> pd.DataFrame:
    """Regime-switching random walk with OHLC, for testing the pipeline when no
    market data is available. Results on it say nothing about real markets."""
    rng = np.random.default_rng(seed + (0 if name == "BTC" else 1 if name == "GOLD" else 2))
    freq = "D" if name == "BTC" else "B"
    idx = pd.date_range(start, end, freq=freq)
    vol = {"BTC": 0.04, "GOLD": 0.009, "SPY": 0.011}[name]
    drift_levels = np.array([-1.0, 0.0, 1.5]) * vol / 8
    regime = np.zeros(len(idx), dtype=int)
    for t in range(1, len(idx)):
        regime[t] = regime[t - 1] if rng.random() > 1 / 90 else rng.integers(3)
    rets = drift_levels[regime] + vol * rng.standard_t(4, len(idx)) / np.sqrt(2)
    close = 100 * np.exp(np.cumsum(rets))
    open_ = np.r_[close[0], close[:-1]] * np.exp(rng.normal(0, vol / 4, len(idx)))
    rng_hl = np.abs(rng.normal(0, vol / 2, len(idx)))
    high = np.maximum(open_, close) * np.exp(rng_hl)
    low = np.minimum(open_, close) * np.exp(-rng_hl)
    return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": 0.0}, index=idx)
