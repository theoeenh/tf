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

import numpy as np
import pandas as pd

from .indicators import adx as adx_indicator
from .indicators import atr as atr_indicator


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
    """Run the strategy on df between start and end.

    Indicators and signals may use data before `start` (warm-up); trading and
    the equity curve start at `start`.
    """
    atr = atr_indicator(df, atr_n).to_numpy()
    adx = adx_indicator(df).to_numpy() if exit_rule.adaptive else None
    sig = signals.reindex(df.index).fillna(0).astype(int).to_numpy()
    if not allow_short:
        sig = np.where(sig < 0, 0, sig)
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
    dates = df.index
    days = dates.to_numpy().astype("datetime64[D]").astype(np.int64)

    i0 = 0 if start is None else int(dates.searchsorted(pd.Timestamp(start)))
    i1 = len(df) if end is None else int(dates.searchsorted(pd.Timestamp(end), side="right"))
    if i1 - i0 < 2:
        raise ValueError("backtest window has fewer than 2 bars")

    slip = costs.slippage_bps / 1e4
    fee = costs.fee_bps / 1e4

    cash = initial_capital
    q = 0.0  # signed quantity
    side = 0
    entry_px = stop = initial_stop = risk_usd = extreme = 0.0
    target: float | None = None
    entry_i = -1
    trade_fees = 0.0
    trades: list[Trade] = []
    equity = np.empty(i1 - i0)
    exposure = np.zeros(i1 - i0)

    def fill(raw: float, direction: int) -> float:
        """Price paid (+1 buy) or received (-1 sell) after slippage."""
        return raw * (1 + direction * slip)

    def close_position(i: int, raw_px: float, reason: str) -> None:
        nonlocal cash, q, side, trade_fees
        px = fill(raw_px, -side)
        exit_fee = abs(q) * px * fee
        cash += q * px - exit_fee
        trade_fees += exit_fee
        pnl = q * (px - entry_px) - trade_fees
        trades.append(Trade(side, dates[entry_i], dates[i], entry_px, px, abs(q), initial_stop, target,
                            pnl, trade_fees, pnl / risk_usd, reason))
        q, side = 0.0, 0

    def open_position(i: int, direction: int) -> None:
        nonlocal cash, q, side, entry_px, stop, initial_stop, target, risk_usd, extreme, entry_i, trade_fees
        px = fill(o[i], direction)
        dist = exit_rule.stop_atr * atr[i - 1]
        size = min(risk_pct * cash / dist, cash / (px * (1 + fee)))
        if size <= 0:
            return
        strong = exit_rule.adaptive and adx[i - 1] >= exit_rule.adx_threshold
        rr = exit_rule.rr_strong if strong else exit_rule.rr
        side, q = direction, direction * size
        entry_px, entry_i, extreme = px, i, px
        stop = initial_stop = px - direction * dist
        target = None if rr is None else px + direction * rr * dist
        risk_usd = size * dist
        trade_fees = size * px * fee
        cash -= q * px + trade_fees

    for i in range(i0, i1):
        # Borrow cost of a short held overnight (calendar days, so weekends count).
        if side < 0 and i > i0:
            cost = abs(q) * c[i - 1] * costs.short_borrow_apr * (days[i] - days[i - 1]) / 365
            cash -= cost
            trade_fees += cost

        want = sig[i - 1] if i > i0 else 0
        opened_today = False
        if side != 0 and want == -side:
            close_position(i, o[i], "reverse")
        if side == 0 and want != 0 and np.isfinite(atr[i - 1]) and atr[i - 1] > 0 \
                and (not exit_rule.adaptive or np.isfinite(adx[i - 1])):
            open_position(i, want)
            opened_today = side != 0

        if side != 0:
            s = side
            adverse, favorable = (l[i], h[i]) if s > 0 else (h[i], l[i])
            stop_reason = "stop" if stop == initial_stop else "trail"
            if not opened_today and s * (o[i] - stop) <= 0:
                close_position(i, o[i], stop_reason)
            elif not opened_today and target is not None and s * (o[i] - target) >= 0:
                close_position(i, o[i], "target")
            elif s * (adverse - stop) <= 0:
                close_position(i, stop, stop_reason)
            elif target is not None and s * (favorable - target) >= 0:
                close_position(i, target, "target")
            elif exit_rule.max_bars is not None and i - entry_i + 1 >= exit_rule.max_bars:
                close_position(i, c[i], "time")

        # Trail the stop on the close, for use from the next bar.
        if side != 0 and exit_rule.trail_atr is not None and np.isfinite(atr[i]):
            extreme = max(extreme, c[i]) if side > 0 else min(extreme, c[i])
            new_stop = extreme - side * exit_rule.trail_atr * atr[i]
            stop = max(stop, new_stop) if side > 0 else min(stop, new_stop)

        if side != 0 and i == i1 - 1:
            close_position(i, c[i], "end")

        equity[i - i0] = cash + q * c[i]
        exposure[i - i0] = side

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
