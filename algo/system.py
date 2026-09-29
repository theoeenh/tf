"""The multi-asset trading system: universe, costs, strategies and risk.

Shared by the portfolio backtest (`portfolio_run`) and paper trading
(`paper`), so both run exactly the same rules.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data, journal
from .engine import Costs, ExitRule
from .metrics import equity_stats
from .portfolio import PortfolioConfig, PortfolioResult, Sleeve, run_portfolio
from .strategies import STRATEGIES

# Higher-volatility universe: three cryptos, two high-beta tech stocks, and
# precious metals (silver is ~1.5x as volatile as gold) for diversification.
UNIVERSE = ("BTC", "ETH", "SOL", "NVDA", "TSLA", "GOLD", "SILVER")

# Per side, on every fill. Shorts pay a yearly borrow / funding rate.
COSTS = {
    "BTC": Costs(fee_bps=10, slippage_bps=5, short_borrow_apr=0.10),
    "ETH": Costs(fee_bps=10, slippage_bps=5, short_borrow_apr=0.10),
    "SOL": Costs(fee_bps=10, slippage_bps=10, short_borrow_apr=0.10),
    "NVDA": Costs(fee_bps=1, slippage_bps=3, short_borrow_apr=0.01),
    "TSLA": Costs(fee_bps=1, slippage_bps=3, short_borrow_apr=0.01),
    "GOLD": Costs(fee_bps=1, slippage_bps=2, short_borrow_apr=0.01),
    "SILVER": Costs(fee_bps=1, slippage_bps=3, short_borrow_apr=0.01),
    "SPY": Costs(fee_bps=1, slippage_bps=1),
}

# One exit rule per strategy, fixed in advance (from the BTC/gold study, so
# out-of-sample for every other asset). "4:2 normally, 6:2 in strong trends"
# for the two signal types with a natural target; the squeeze breakout lets
# winners run with a trailing stop.
SLEEVE_RULES = {
    "donchian_trend": ExitRule(stop_atr=2.5, rr=2.0, rr_strong=3.0, adaptive=True),
    "squeeze_breakout": ExitRule(stop_atr=3.0, rr=None, trail_atr=4.0),
    "rsi2_reversion": ExitRule(stop_atr=2.5, rr=2.0, rr_strong=3.0, adaptive=True),
}

TARGET_VOL = 0.20  # yearly volatility the account is sized for ("higher volatility")
MAX_GROSS = 2.0  # up to 2x notional / equity
MAX_OPEN_RISK = 0.15  # at most 15% of equity at risk across open trades
MAX_RISK_PCT = 0.03  # never more than 3% of equity on one trade

VARIANTS = {
    "long only": dict(allow_short=False, learn=False),
    "long only + learner": dict(allow_short=False, learn=True),
    "long/short": dict(allow_short=True, learn=False),
    "long/short + learner": dict(allow_short=True, learn=True),
}


def load_prices(source: str = "auto", interval: str = "1d", assets=UNIVERSE) -> dict[str, pd.DataFrame]:
    return {a: data.load(a, source, interval=interval) for a in assets}


def build_sleeves(prices: dict[str, pd.DataFrame], allow_short: bool) -> list[Sleeve]:
    return [Sleeve(asset, name, fn(prices[asset]), SLEEVE_RULES[name], allow_short)
            for asset in prices for name, fn in STRATEGIES.items()]


def bars_per_year(index: pd.DatetimeIndex) -> float:
    years = (index[-1] - index[0]).total_seconds() / (365.25 * 86400)
    return len(index) / years


def run_system(prices, allow_short: bool, learn: bool, risk_pct: float, start=None, end=None,
               initial_capital: float = 100_000.0, close_at_end: bool = True,
               learner: journal.Learner | None = None) -> PortfolioResult:
    if learner is None and learn:
        learner = journal.Learner()
    cfg = PortfolioConfig(initial_capital=initial_capital, risk_pct=risk_pct, max_gross=MAX_GROSS,
                          max_open_risk=MAX_OPEN_RISK, learner=learner if learn else None)
    return run_portfolio(prices, build_sleeves(prices, allow_short), COSTS, cfg, start, end,
                         close_at_end=close_at_end)


def calibrate_risk(prices, allow_short: bool, learn: bool, start, end, target_vol: float = TARGET_VOL) -> float:
    """Risk per trade that gives `target_vol` yearly volatility on the
    calibration window (training data only)."""
    risk = 0.01
    for _ in range(3):  # a few rounds because the leverage cap is not linear
        eq = run_system(prices, allow_short, learn, risk, start, end).equity
        vol = equity_stats(eq, bars_per_year(eq.index))["volatility"]
        if not np.isfinite(vol) or vol <= 0:
            break
        risk = float(np.clip(risk * target_vol / vol, 0.001, MAX_RISK_PCT))
    return risk


def random_sleeves(prices, allow_short: bool, seed: int) -> list[Sleeve]:
    """Same sleeves, exits and signal frequency, but entries at random.
    The skill test: a real strategy must beat this, not just buy & hold."""
    rng = np.random.default_rng(seed)
    out = []
    for s in build_sleeves(prices, allow_short):
        real = s.signals.reindex(prices[s.asset].index).fillna(0)
        fire = rng.random(len(real)) < (real != 0).mean()
        side = np.where(rng.random(len(real)) < 0.5, 1, -1) if allow_short else 1
        out.append(Sleeve(s.asset, s.strategy, pd.Series(np.where(fire, side, 0), real.index), s.exit_rule,
                          allow_short))
    return out


def run_random(prices, allow_short: bool, risk_pct: float, seed: int, start=None, end=None) -> PortfolioResult:
    cfg = PortfolioConfig(risk_pct=risk_pct, max_gross=MAX_GROSS, max_open_risk=MAX_OPEN_RISK)
    return run_portfolio(prices, random_sleeves(prices, allow_short, seed), COSTS, cfg, start, end)
