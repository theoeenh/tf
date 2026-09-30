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

from .indicators import adx, atr, rsi, sma

# ---------------------------------------------------------------- features


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Market context for every bar, known at that bar's close."""
    a = atr(df)
    c = df["Close"]
    atr_pct = a / c
    return pd.DataFrame({
        "adx": adx(df),
        "sma200": sma(c, 200),
        "atr_pct": atr_pct,
        # where today's volatility sits within the last 250 bars (0 = calmest, 1 = wildest)
        "vol_rank": atr_pct.rolling(250, min_periods=50).rank(pct=True),
        # for the machine-learning learner: distances and momentum in ATRs, RSI(14)
        "dist200": (c - sma(c, 200)) / a,
        "dist50": (c - sma(c, 50)) / a,
        "ret5": (c - c.shift(5)) / a,
        "ret20": (c - c.shift(20)) / a,
        "rsi14": rsi(c, 14),
    }, index=df.index)


def regime(adx_value: float) -> str:
    if not np.isfinite(adx_value):
        return "unknown"
    return "chop" if adx_value < 20 else "trend" if adx_value < 30 else "strong"


def vol_bucket(rank: float) -> str:
    if not np.isfinite(rank):
        return "unknown"
    return "low" if rank < 1 / 3 else "mid" if rank < 2 / 3 else "high"


def news_bucket(tone_z: float) -> str:
    if tone_z is None or not np.isfinite(tone_z):
        return "unknown"
    return "negative" if tone_z < -1 else "positive" if tone_z > 1 else "neutral"


def buzz_bucket(attention_z: float) -> str:
    if attention_z is None or not np.isfinite(attention_z):
        return "unknown"
    return "spike" if attention_z > 1.5 else "normal"


def event_bucket(feats: dict) -> str:
    """The scheduled event closest ahead, if it is imminent."""
    if feats.get("days_to_earnings", np.inf) <= 3:
        return "earnings"
    if feats.get("days_to_fomc", np.inf) <= 1:
        return "fomc"
    if feats.get("days_to_jobs", np.inf) <= 0:
        return "jobs report"
    return "none"


def ai_bucket(side: int, ai_bias: float) -> str:
    if ai_bias is None or not np.isfinite(ai_bias) or ai_bias == 0:
        return "none"
    return "agree" if np.sign(ai_bias) == side else "disagree"


def context(side: int, close: float, feats: dict) -> dict:
    aligned = np.isfinite(feats["sma200"]) and side * (close - feats["sma200"]) > 0
    return {
        "side": side,
        "adx": feats["adx"],
        "regime": regime(feats["adx"]),
        "vol": vol_bucket(feats["vol_rank"]),
        "atr_pct": feats["atr_pct"],
        "aligned": bool(aligned),
        "tone_z": feats.get("tone_z", np.nan),
        "attention_z": feats.get("attention_z", np.nan),
        "news": news_bucket(feats.get("tone_z")),
        "buzz": buzz_bucket(feats.get("attention_z")),
        "event": event_bucket(feats),
        "days_to_earnings": feats.get("days_to_earnings", np.inf),
        "ai": ai_bucket(side, feats.get("ai_bias")),
        "ai_bias": feats.get("ai_bias", np.nan),
    }


# ---------------------------------------------------------------- reasoning

SETUPS = {
    "donchian_trend": ("broke out of its 55-bar {hl}", "trend following"),
    "squeeze_breakout": ("broke out of a volatility squeeze to the {ud}", "volatility breakout"),
    "rsi2_reversion": ("made a sharp 2-bar {move} (RSI-2 extreme)", "mean reversion"),
    "news_momentum": ("had a burst of {tone} news and price confirmed it", "news momentum"),
}


def rationale(asset: str, strategy: str, side: int, ctx: dict, entry: float, stop: float,
              target: float | None, risk_usd: float, rr: float | None) -> str:
    """The 'thinking process' written at entry."""
    what, family = SETUPS.get(strategy, ("gave a signal", strategy))
    what = what.format(hl="high" if side > 0 else "low", ud="upside" if side > 0 else "downside",
                       move="dip" if side > 0 else "spike", tone="positive" if side > 0 else "negative")
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
    if ctx.get("news", "unknown") != "unknown":
        parts.append(f"News: {ctx['news']} tone ({ctx['tone_z']:+.1f}σ vs usual), "
                     f"{'a spike in' if ctx['buzz'] == 'spike' else 'normal'} coverage.")
    if ctx.get("event", "none") != "none":
        parts.append(f"Warning: {ctx['event']} coming up while in the trade.")
    if ctx.get("ai", "none") != "none":
        parts.append(f"AI analyst view {ctx['ai_bias']:+.0f}: it {ctx['ai']}s with this trade.")
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
    "event_gap": "Held through a scheduled event (earnings / Fed) and price gapped through the stop.",
    "news_against": "Traded against strongly one-sided news and lost.",
}


def diagnose(r: float, gross_r: float, mfe_r: float, ctx: dict, strategy: str) -> str:
    """Classify a closed trade. Uses only what was known when it closed."""
    if r > 0:
        return "none"
    if gross_r > 0:
        return "fees_ate_edge"
    if r < -1.2:
        return "event_gap" if ctx.get("event", "none") != "none" else "gap_through_stop"
    if mfe_r >= 1.0:
        return "gave_back_profit"
    if not ctx["aligned"]:
        return "counter_trend"
    news = ctx.get("news", "unknown")
    if (news == "negative" and gross_r <= 0 and r < 0 and _side_of(ctx) > 0) or \
            (news == "positive" and r < 0 and _side_of(ctx) < 0):
        return "news_against"
    if ctx["regime"] == "chop" and strategy != "rsi2_reversion":
        return "choppy_market"
    if mfe_r < 0.3:
        return "wrong_immediately"
    return "normal_loss"


def _side_of(ctx: dict) -> int:
    return ctx.get("side", 0)


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
    size: float = 1.0  # multiplier on the normal position size (the ML learner bets more when confident)


class Learner:
    """Learns which conditions lose money for each strategy.

    Each closed trade (real, or skipped-but-tracked "shadow" trade) is filed
    under several views of its situation:
      setup: strategy, direction, trend regime, volatility, trend alignment
      news:  strategy, direction, news tone, news coverage (GDELT)
      event: strategy, direction, scheduled event ahead (earnings, Fed, jobs)
      ai:    strategy, direction, whether the AI analyst agreed
    The asset is left out on purpose, so a lesson learned on ETH also
    protects SOL. Before a new trade, if any view of its situation has at
    least `min_trades` recent results averaging below `min_avg_r`, the trade
    is skipped. Skipped trades are still followed as shadow trades, so a
    condition that starts working again gets unblocked.
    """

    ALL_VIEWS = ("setup", "news", "event", "ai")

    def __init__(self, min_trades: int = 15, min_avg_r: float = -0.1, memory: int = 60,
                 views: tuple[str, ...] = ("setup",)):
        self.min_trades, self.min_avg_r, self.memory, self.views = min_trades, min_avg_r, memory, views
        self.history: dict[tuple, list[float]] = defaultdict(list)

    @staticmethod
    def key(strategy: str, side: int, ctx: dict) -> tuple:
        return (strategy, "long" if side > 0 else "short", ctx["regime"], ctx["vol"], ctx["aligned"])

    def keys(self, strategy: str, side: int, ctx: dict, **_) -> list[tuple]:
        d = "long" if side > 0 else "short"
        out = [("setup",) + tuple(self.key(strategy, side, ctx))] if "setup" in self.views else []
        if "news" in self.views and ctx.get("news", "unknown") != "unknown":
            out.append(("news", strategy, d, ctx["news"], ctx["buzz"]))
        if "event" in self.views and ctx.get("event", "none") != "none":
            out.append(("event", strategy, d, ctx["event"]))
        if "ai" in self.views and ctx.get("ai", "none") != "none":
            out.append(("ai", strategy, d, ctx["ai"]))
        return out

    def judge(self, keys: list[tuple]) -> Verdict:
        for k in keys:
            past = self.history[k][-self.memory:]
            if len(past) >= self.min_trades and np.mean(past) < self.min_avg_r:
                return Verdict(True, f"SKIPPED by learner: the last {len(past)} trades with "
                                     f"{describe_key(k)} averaged {np.mean(past):+.2f}R.")
        return Verdict(False, "")

    def record(self, keys: list[tuple], r: float, when=None) -> None:
        for k in keys:
            self.history[k].append(r)

    def lessons(self, min_trades: int = 10) -> pd.DataFrame:
        rows = [{"view": k[0], "setup": describe_key(k), "trades": len(v), "avg_r": np.mean(v),
                 "recent_avg_r": np.mean(v[-self.memory:]), "win_rate": np.mean(np.array(v) > 0),
                 "status": "blocked" if self.judge([k]).skip else "allowed"}
                for k, v in self.history.items() if len(v) >= min_trades]
        return pd.DataFrame(rows).sort_values("avg_r") if rows else pd.DataFrame()


def describe_key(key: tuple) -> str:
    view, rest = key[0], key[1:]
    if view == "setup":
        strategy, side, reg, vol, aligned = rest
        return f"{strategy} {side}, {reg} market, {vol} vol, {'with' if aligned else 'against'} trend"
    if view == "news":
        strategy, side, tone, buzz = rest
        return f"{strategy} {side} on {tone} news, {buzz} coverage"
    if view == "event":
        strategy, side, event = rest
        return f"{strategy} {side} with {event} ahead"
    strategy, side, ai = rest
    return f"{strategy} {side} when the AI analyst {'agreed' if ai == 'agree' else 'disagreed'}"
