"""Event-driven daily backtester, long and short, with ATR-based exits.

Execution model (chosen to be conservative, not flattering):
- A signal on bar t's close is filled at bar t+1's open. No look-ahead.
  Signals: +1 = go long, -1 = go short, 0 = nothing.
- Initial stop = entry -/+ stop_atr * ATR at the signal bar (1R of risk).
- Target = entry +/- rr * stop distance. `rr` can depend on the trend regime
  (ADX at the signal bar): `rr` in normal markets, `rr_strong` in strong
  trends. A target of None means "no target", i.e. let the trade run.
- Optional trailing stop: `trail_atr` ATRs behind the best close since entry.
  It only ever tightens, and is updated on the close for use from the next bar.
- An opposite signal closes the position at the next open and reverses it.
- If the open gaps through a level, the fill is at the open. If a bar
  touches both stop and target, the stop is assumed to hit first.
- Every fill pays slippage (worse price) and a fee on notional. Shorts also
  pay a borrow / funding cost per calendar day on the position's value.
- Size risks `risk_pct` of equity between entry and initial stop, capped so
  the position's notional never exceeds equity (no leverage).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd



@dataclass(frozen=True)
class ExitRule:
    stop_atr: float = 2.0  # initial stop distance in ATRs (= 1R)
    rr: float | None = 3.0  # target in R; None = no target
    trail_atr: float | None = None  # trailing stop distance in ATRs; None = off
    rr_strong: float | None = None  # target in R when ADX >= adx_threshold (None = no target)
    adaptive: bool = False  # use rr_strong in strong trends
    adx_threshold: float = 25.0
    max_bars: int | None = None  # optional time stop

    def label(self) -> str:
        def r(x):
            return "run" if x is None else f"{x:g}:1"

        s = f"{self.stop_atr:g} ATR stop, "
        s += f"{r(self.rr)} / trend {r(self.rr_strong)}" if self.adaptive else r(self.rr)
        if self.trail_atr is not None:
            s += f", trail {self.trail_atr:g} ATR"
        return s


@dataclass(frozen=True)
class Costs:
    fee_bps: float = 0.0  # per side, on notional
    slippage_bps: float = 0.0  # per side, applied to the fill price
    short_borrow_apr: float = 0.0  # yearly cost of holding a short, on notional


@dataclass
class Trade:
    side: int  # +1 long, -1 short
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry: float
    exit: float
    qty: float
    initial_stop: float
    target: float | None
    pnl: float  # net of every cost
    fees: float  # exchange fees + borrow cost (slippage is already in the prices)
    r_multiple: float  # pnl / initial risk
    reason: str  # "stop", "trail", "target", "reverse", "time", "end"
    # Journal fields (filled by the portfolio engine).
    asset: str = ""
    strategy: str = ""
    mfe_r: float = float("nan")  # best unrealised profit during the trade, in R
    mae_r: float = float("nan")  # worst unrealised loss during the trade, in R
    regime: str = ""  # chop / trend / strong (ADX at entry)
    vol: str = ""  # low / mid / high volatility at entry
    aligned: bool = True  # traded with the 200-bar trend
    error: str = ""  # diagnosis, see journal.ERRORS
    rationale: str = ""  # reasoning at entry
    lesson: str = ""  # what the trade taught
    shadow: bool = False  # skipped by the learner, followed without money


@dataclass
class Result:
    equity: pd.Series
    trades: list[Trade] = field(default_factory=list)
    exposure: pd.Series | None = None  # +1 long, -1 short, 0 flat

    @property
    def trades_df(self) -> pd.DataFrame:
        return pd.DataFrame([t.__dict__ for t in self.trades])


def backtest(
    df: pd.DataFrame,
    signals: pd.Series,
    exit_rule: ExitRule = ExitRule(),
    costs: Costs = Costs(),
    initial_capital: float = 100_000.0,
    risk_pct: float = 0.01,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
    allow_short: bool = True,
    atr_n: int = 14,
) -> Result:
    """Run one strategy on one asset between start and end.

    Indicators and signals may use data before `start` (warm-up); trading and
    the equity curve start at `start`. This is the portfolio engine with a
    single sleeve and no leverage.
    """
    from .portfolio import PortfolioConfig, Sleeve, run_portfolio

    res = run_portfolio(
        {"asset": df},
        [Sleeve("asset", "", signals, exit_rule, allow_short)],
        {"asset": costs},
        PortfolioConfig(initial_capital=initial_capital, risk_pct=risk_pct, max_gross=1.0),
        start=start, end=end, atr_n=atr_n,
    )
    return Result(res.equity, res.trades, res.net_side.rename("exposure"))


def buy_and_hold(
    df: pd.DataFrame,
    costs: Costs = Costs(),
    initial_capital: float = 100_000.0,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
) -> pd.Series:
    """Equity curve of buying at the first open of the window and holding."""
    w = df.loc[start:end]
    px = w["Open"].iloc[0] * (1 + costs.slippage_bps / 1e4)
    qty = initial_capital / (px * (1 + costs.fee_bps / 1e4))
    cash = initial_capital - qty * px * (1 + costs.fee_bps / 1e4)
    return (cash + qty * w["Close"]).rename("equity")
