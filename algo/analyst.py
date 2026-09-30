"""AI analyst: stores the daily views an AI model writes after reading the
brief, scores them against what the market did next, and feeds them to the
learner.

Why this is forward-only: a language model has read about the past. Asked
about NVDA news from 2017, it already knows NVDA went up 100x afterwards, so
a backtest of its old calls would be fake. Its views therefore only count
from the day they are written, in paper trading, and the learner decides from
that record whether they deserve any weight.

A view file is `paper/ai_views/YYYY-MM-DD.json`:
    [{"asset": "NVDA", "bias": 1, "confidence": 0.6, "horizon_days": 5,
      "key_events": ["earnings Nov 19"], "reasoning": "..."}, ...]
bias: -2 strong sell, -1 sell, 0 no view, 1 buy, 2 strong buy.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .indicators import atr

VIEWS_DIR = Path(__file__).resolve().parent.parent / "paper" / "ai_views"
FIELDS = ("asset", "bias", "confidence", "horizon_days", "key_events", "reasoning")


def validate_view(v: dict) -> dict:
    missing = [f for f in ("asset", "bias", "confidence", "horizon_days", "reasoning") if f not in v]
    if missing:
        raise ValueError(f"view missing {missing}: {v}")
    bias = int(v["bias"])
    if bias not in (-2, -1, 0, 1, 2):
        raise ValueError(f"bias must be -2..2, got {bias}")
    conf = float(v["confidence"])
    if not 0 <= conf <= 1:
        raise ValueError(f"confidence must be 0..1, got {conf}")
    return {"asset": str(v["asset"]).upper(), "bias": bias, "confidence": conf,
            "horizon_days": int(np.clip(int(v["horizon_days"]), 1, 30)),
            "key_events": list(v.get("key_events", [])), "reasoning": str(v["reasoning"])}


def load_views(directory: Path = VIEWS_DIR) -> pd.DataFrame:
    rows = []
    for f in sorted(directory.glob("*.json")):
        day = pd.Timestamp(f.stem)
        for v in json.loads(f.read_text()):
            rows.append({"date": day} | validate_view(v))
    return pd.DataFrame(rows, columns=["date", *FIELDS])


def bias_frame(views: pd.DataFrame) -> pd.DataFrame | None:
    """date x asset table of bias (the model's view written on that date)."""
    if views.empty:
        return None
    return views.pivot_table(index="date", columns="asset", values="bias", aggfunc="last")


def score_views(views: pd.DataFrame, prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """For every view whose horizon has passed: the move from the next close
    after the view to the close `horizon_days` bars later, in ATRs, signed by
    the view. Positive = the AI was right."""
    out = []
    for _, v in views.iterrows():
        df = prices.get(v.asset)
        if df is None or v.bias == 0:
            continue
        a = atr(df)
        after = df.index[df.index > v.date]
        if len(after) <= v.horizon_days:
            continue  # not due yet
        t0, t1 = after[0], after[v.horizon_days]
        move = (df.at[t1, "Close"] - df.at[t0, "Close"]) / a.loc[:t0].iloc[-1]
        out.append({"date": v.date, "asset": v.asset, "bias": v.bias, "confidence": v.confidence,
                    "move_atr": move, "score_atr": np.sign(v.bias) * move, "right": np.sign(v.bias) * move > 0})
    return pd.DataFrame(out)


def track_record(scored: pd.DataFrame) -> str:
    if scored.empty:
        return "No AI views have reached their horizon yet."
    lines = [f"{len(scored)} scored views: right {scored.right.mean():.0%} of the time, "
             f"average {scored.score_atr.mean():+.2f} ATR in the called direction.", "",
             "| Asset | Views | Right | Avg ATR in called direction |", "|---|---:|---:|---:|"]
    for a, g in scored.groupby("asset"):
        lines.append(f"| {a} | {len(g)} | {g.right.mean():.0%} | {g.score_atr.mean():+.2f} |")
    hi = scored[scored.confidence >= 0.6]
    if len(hi):
        lines += ["", f"High-confidence views (≥ 0.6): {len(hi)}, right {hi.right.mean():.0%}, "
                      f"average {hi.score_atr.mean():+.2f} ATR."]
    return "\n".join(lines)
