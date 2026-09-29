"""Event-driven, long-only daily backtester with bracket (stop + target) exits.

Execution model (chosen to be conservative, not flattering):
- A signal on bar t's close is filled at bar t+1's open. No look-ahead.
- The stop and target are set from ATR at the signal bar:
      stop   = entry - stop_atr * ATR
      target = entry + stop_atr * rr * ATR
- If the next open gaps through the stop or target, the fill is at the open.
- If a bar touches both stop and target, the stop is assumed to hit first.
- Every fill pays slippage (worse price) and a fee on notional.
- Position size risks `risk_pct` of current equity between entry and stop,
  capped so the position never exceeds equity (no leverage).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .indicators import atr as atr_indicator


@dataclass(frozen=True)
class ExitRule:
    stop_atr: float = 2.0  # stop distance in ATRs
    rr: float = 3.0  # reward / risk: target distance = rr * stop distance
    max_bars: int | None = None  # optional time stop, in bars


@dataclass(frozen=True)
class Costs:
    fee_bps: float = 0.0  # per side, on notional
    slippage_bps: float = 0.0  # per side, applied to the fill price


@dataclass
class Trade:
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry: float
    exit: float
    qty: float
    stop: float
    target: float
    pnl: float  # net of fees and slippage
    r_multiple: float  # pnl / initial risk
    reason: str  # "stop", "target", "time", "end"


@dataclass
class Result:
    equity: pd.Series
    trades: list[Trade] = field(default_factory=list)
    exposure: pd.Series | None = None  # 1 while in a position

    @property
    def trades_df(self) -> pd.DataFrame:
        return pd.DataFrame([t.__dict__ for t in self.trades])


def backtest(
    df: pd.DataFrame,
    entries: pd.Series,
    exit_rule: ExitRule = ExitRule(),
    costs: Costs = Costs(),
    initial_capital: float = 100_000.0,
    risk_pct: float = 0.01,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
    atr_n: int = 14,
) -> Result:
    """Run the strategy on df between start and end.

    Indicators and signals may use data before `start` (warm-up); trading and
    the equity curve start at `start`.
    """
    atr = atr_indicator(df, atr_n).to_numpy()
    sig = entries.reindex(df.index).fillna(False).to_numpy(dtype=bool)
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
    dates = df.index

    i0 = 0 if start is None else int(dates.searchsorted(pd.Timestamp(start)))
    i1 = len(df) if end is None else int(dates.searchsorted(pd.Timestamp(end), side="right"))
    if i1 - i0 < 2:
        raise ValueError("backtest window has fewer than 2 bars")

    slip = costs.slippage_bps / 1e4
    fee = costs.fee_bps / 1e4

    cash = initial_capital
    qty = 0.0
    entry_px = stop = target = risk_usd = 0.0
    entry_i = -1
    entry_fee = 0.0
    trades: list[Trade] = []
    equity = np.empty(i1 - i0)
    exposure = np.zeros(i1 - i0)

    def close_position(i: int, raw_px: float, reason: str) -> None:
        nonlocal cash, qty
        px = raw_px * (1 - slip)
        exit_fee = qty * px * fee
        cash += qty * px - exit_fee
        pnl = qty * (px - entry_px) - entry_fee - exit_fee
        trades.append(
            Trade(dates[entry_i], dates[i], entry_px, px, qty, stop, target, pnl, pnl / risk_usd, reason)
        )
        qty = 0.0

    for i in range(i0, i1):
        entered_today = False
        # 1) Fill a pending entry from yesterday's signal at today's open.
        if qty == 0 and i > i0 and sig[i - 1] and np.isfinite(atr[i - 1]) and atr[i - 1] > 0:
            px = o[i] * (1 + slip)
            dist = exit_rule.stop_atr * atr[i - 1]
            eq = cash
            size = min(risk_pct * eq / dist, eq / (px * (1 + fee)))
            if size > 0:
                qty = size
                entry_px, entry_i = px, i
                stop, target = px - dist, px + exit_rule.rr * dist
                risk_usd = qty * dist
                entry_fee = qty * px * fee
                cash -= qty * px + entry_fee
                entered_today = True

        # 2) Manage an open position against today's bar.
        if qty > 0:
            if not entered_today and o[i] <= stop:
                close_position(i, o[i], "stop")
            elif not entered_today and o[i] >= target:
                close_position(i, o[i], "target")
            elif l[i] <= stop:
                close_position(i, stop, "stop")
            elif h[i] >= target:
                close_position(i, target, "target")
            elif exit_rule.max_bars is not None and i - entry_i + 1 >= exit_rule.max_bars:
                close_position(i, c[i], "time")

        if qty > 0 and i == i1 - 1:
            close_position(i, c[i], "end")

        equity[i - i0] = cash + qty * c[i]
        exposure[i - i0] = 1.0 if qty > 0 else 0.0

    idx = dates[i0:i1]
    return Result(pd.Series(equity, idx, name="equity"), trades, pd.Series(exposure, idx, name="exposure"))


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
