"""Trade journal: the reasoning behind each entry, a diagnosis of each exit,
and a learner that turns past mistakes into rules.

Everything here is deterministic, so a backtest and a paper-trading run write
the same journal for the same bars. The learner only ever sees trades that
were already closed at the moment it is asked, so it cannot peek at the future.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .indicators import adx, atr, sma

# ---------------------------------------------------------------- features


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Market context for every bar, known at that bar's close."""
    a = atr(df)
    atr_pct = a / df["Close"]
    return pd.DataFrame({
        "adx": adx(df),
        "sma200": sma(df["Close"], 200),
        "atr_pct": atr_pct,
        # where today's volatility sits within the last 250 bars (0 = calmest, 1 = wildest)
        "vol_rank": atr_pct.rolling(250, min_periods=50).rank(pct=True),
    }, index=df.index)


def regime(adx_value: float) -> str:
    if not np.isfinite(adx_value):
        return "unknown"
    return "chop" if adx_value < 20 else "trend" if adx_value < 30 else "strong"


def vol_bucket(rank: float) -> str:
    if not np.isfinite(rank):
        return "unknown"
    return "low" if rank < 1 / 3 else "mid" if rank < 2 / 3 else "high"


def context(side: int, close: float, feats: dict) -> dict:
    aligned = np.isfinite(feats["sma200"]) and side * (close - feats["sma200"]) > 0
    return {
        "adx": feats["adx"],
        "regime": regime(feats["adx"]),
        "vol": vol_bucket(feats["vol_rank"]),
        "atr_pct": feats["atr_pct"],
        "aligned": bool(aligned),
    }


# ---------------------------------------------------------------- reasoning

SETUPS = {
    "donchian_trend": ("broke out of its 55-bar {hl}", "trend following"),
    "squeeze_breakout": ("broke out of a volatility squeeze to the {ud}", "volatility breakout"),
    "rsi2_reversion": ("made a sharp 2-bar {move} (RSI-2 extreme)", "mean reversion"),
}


def rationale(asset: str, strategy: str, side: int, ctx: dict, entry: float, stop: float,
              target: float | None, risk_usd: float, rr: float | None) -> str:
    """The 'thinking process' written at entry."""
    what, family = SETUPS.get(strategy, ("gave a signal", strategy))
    what = what.format(hl="high" if side > 0 else "low", ud="upside" if side > 0 else "downside",
                       move="dip" if side > 0 else "spike")
    direction = "LONG" if side > 0 else "SHORT"
    trend = "with" if ctx["aligned"] else "AGAINST"
    parts = [
        f"{direction} {asset} ({family}): price {what}.",
        f"Trading {trend} the 200-bar trend. ADX {ctx['adx']:.0f} = {ctx['regime']} market, "
        f"{ctx['vol']} volatility (ATR {ctx['atr_pct']:.1%} of price).",
        f"Plan: entry {entry:,.2f}, stop {stop:,.2f}, "
        + (f"target {target:,.2f} ({rr:g}:1)" if target is not None else "no target, trailing stop lets it run")
        + f"; risking ${risk_usd:,.0f}.",
    ]
    if ctx["regime"] == "strong" and target is not None and rr is not None and rr > 2:
        parts.append("Strong trend, so the target was widened.")
    return " ".join(parts)


# ---------------------------------------------------------------- diagnosis

ERRORS = {
    "none": "Plan worked.",
    "fees_ate_edge": "Right direction, but fees and slippage turned a small gain into a loss.",
    "gap_through_stop": "Price gapped through the stop, so the loss was bigger than planned.",
    "gave_back_profit": "Was at least 1R in profit, then gave it all back: exit management failed.",
    "counter_trend": "Traded against the 200-bar trend and lost.",
    "choppy_market": "Breakout/trend setup in a choppy market (ADX < 20) failed.",
    "wrong_immediately": "Moved against the trade right away: the signal itself was wrong.",
    "normal_loss": "Valid setup, planned 1R loss. Normal variance, no clear mistake.",
    "stop_too_tight": "Stopped out, then price went on to the target: the stop was inside the noise.",
}


def diagnose(r: float, gross_r: float, mfe_r: float, ctx: dict, strategy: str) -> str:
    """Classify a closed trade. Uses only what was known when it closed."""
    if r > 0:
        return "none"
    if gross_r > 0:
        return "fees_ate_edge"
    if r < -1.2:
        return "gap_through_stop"
    if mfe_r >= 1.0:
        return "gave_back_profit"
    if not ctx["aligned"]:
        return "counter_trend"
    if ctx["regime"] == "chop" and strategy != "rsi2_reversion":
        return "choppy_market"
    if mfe_r < 0.3:
        return "wrong_immediately"
    return "normal_loss"


def lesson(error: str, r: float, mfe_r: float, reason: str) -> str:
    if error == "none":
        how = {"target": "target hit", "trail": "trailing stop banked the move",
               "reverse": "closed on an opposite signal", "end": "still open at the end of the test"}.get(reason, reason)
        extra = f" Peak was {mfe_r:+.1f}R, kept {r:+.1f}R." if mfe_r - r > 1 else ""
        return f"{ERRORS['none']} {how.capitalize()} ({r:+.2f}R).{extra}"
    return f"{ERRORS[error]} ({r:+.2f}R, best point {mfe_r:+.1f}R)"


def tag_stop_too_tight(trades: pd.DataFrame, prices: dict[str, pd.DataFrame], bars: int = 20) -> pd.DataFrame:
    """After the fact: flag stop-outs where price reached the planned target
    within `bars` bars of the exit. Reporting only, never used for learning."""
    trades = trades.copy()
    for k, t in trades.iterrows():
        if t.reason != "stop" or t.target is None or pd.isna(t.target):
            continue
        after = prices[t.asset].loc[t.exit_date:].iloc[1:bars + 1]
        hit = (after["High"] >= t.target).any() if t.side > 0 else (after["Low"] <= t.target).any()
        if hit:
            trades.at[k, "error"] = "stop_too_tight"
            trades.at[k, "lesson"] = f"{ERRORS['stop_too_tight']} ({t.r_multiple:+.2f}R)"
    return trades


# ---------------------------------------------------------------- learning


@dataclass
class Verdict:
    skip: bool
    reason: str


class Learner:
    """Learns which market conditions lose money for each strategy.

    Each closed trade (real or skipped-but-tracked "shadow" trade) is filed
    under its setup: strategy, direction, trend regime, volatility bucket and
    trend alignment. The asset is left out on purpose, so a lesson learned on
    ETH also protects SOL. Before a new trade, if the same setup has at least
    `min_trades` past results averaging below `min_avg_r`, the trade is skipped.
    Skipped trades are still followed as shadow trades, so a setup that starts
    working again gets unblocked.
    """

    def __init__(self, min_trades: int = 15, min_avg_r: float = -0.1, memory: int = 60):
        self.min_trades, self.min_avg_r, self.memory = min_trades, min_avg_r, memory
        self.history: dict[tuple, list[float]] = defaultdict(list)

    @staticmethod
    def key(strategy: str, side: int, ctx: dict) -> tuple:
        return (strategy, "long" if side > 0 else "short", ctx["regime"], ctx["vol"], ctx["aligned"])

    def judge(self, key: tuple) -> Verdict:
        past = self.history[key][-self.memory:]
        if len(past) >= self.min_trades and np.mean(past) < self.min_avg_r:
            return Verdict(True, f"SKIPPED by learner: the last {len(past)} trades with this setup "
                                 f"({describe_key(key)}) averaged {np.mean(past):+.2f}R.")
        return Verdict(False, "")

    def record(self, key: tuple, r: float) -> None:
        self.history[key].append(r)

    def lessons(self, min_trades: int = 10) -> pd.DataFrame:
        rows = [{"setup": describe_key(k), "trades": len(v), "avg_r": np.mean(v),
                 "recent_avg_r": np.mean(v[-self.memory:]), "win_rate": np.mean(np.array(v) > 0),
                 "status": "blocked" if self.judge(k).skip else "allowed"}
                for k, v in self.history.items() if len(v) >= min_trades]
        return pd.DataFrame(rows).sort_values("avg_r") if rows else pd.DataFrame()


def describe_key(key: tuple) -> str:
    strategy, side, reg, vol, aligned = key
    return f"{strategy} {side}, {reg} market, {vol} vol, {'with' if aligned else 'against'} trend"
