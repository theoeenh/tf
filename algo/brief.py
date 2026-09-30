"""Daily brief: what is coming today and this week, what the news says, what
the system sees, and the task for the AI analyst.

    python -m algo.brief                 # writes paper/brief.md

The AI analyst (a Claude session, run by hand or on a schedule) reads
paper/brief.md, writes its views to paper/ai_views/<date>.json in the format
described in algo/analyst.py, and nothing else. The views then enter the
learner and are scored against what the market did.
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from . import analyst, core, news
from .indicators import adx, sma
from .paper import PAPER_DIR, complete_bars, now_utc
from .strategies import STRATEGIES, news_momentum
from .system import UNIVERSE, load_prices

log = logging.getLogger(__name__)
AI_TASK = """## Task for the AI analyst

Read everything above. For each asset, decide whether the news, the events ahead and the
market picture give an edge over the next 1–20 trading days. Rules:
- Use only what is in this brief and in the linked headlines. Do not use anything you
  believe you know about prices after the brief's date.
- No view (bias 0) is a good answer when nothing stands out. Do not force calls.
- Flag scheduled events that could gap the price (earnings, Fed decision, jobs report).
- Explain your reasoning in 1–3 sentences a finance student can check later.

Write a JSON list to `paper/ai_views/{date}.json`, one object per asset:
`{{"asset": "NVDA", "bias": -2..2, "confidence": 0..1, "horizon_days": 1..20,
  "key_events": ["..."], "reasoning": "..."}}`
Then run `python -m pytest -q tests/test_analyst.py` to check the file parses.
"""


def upcoming_events(news_data: dict, today: pd.Timestamp, days: int = 7, extra_earnings: dict | None = None):
    end = today + pd.Timedelta(days=days)
    rows = [(d, "Fed (FOMC) rate decision") for d in news_data["fomc"] if today <= d <= end]
    rows += [(d, "US jobs report (first Friday, approx.)") for d in news_data["jobs"] if today <= d <= end]
    for a, dates in {**news_data["earnings"], **(extra_earnings or {})}.items():
        rows += [(d, f"{a} earnings") for d in dates if today <= d <= end]
    return sorted(rows)


def asset_snapshot(name: str, df: pd.DataFrame, nf: pd.DataFrame | None) -> list[str]:
    c = df["Close"]
    last = c.index[-1]
    trend = "above" if c.iloc[-1] > sma(c, 200).iloc[-1] else "below"
    a = adx(df).iloc[-1]
    r1w = c.iloc[-1] / c.iloc[-6] - 1 if len(c) > 6 else np.nan
    r1m = c.iloc[-1] / c.iloc[-22] - 1 if len(c) > 22 else np.nan
    sigs = [f"{k} {'BUY' if v.iloc[-1] > 0 else 'SELL'}" for k, fn in STRATEGIES.items()
            if (v := fn(df)).iloc[-1] != 0]
    if nf is not None:
        nm = news_momentum(df, nf).iloc[-1]
        if nm != 0:
            sigs.append(f"news_momentum {'BUY' if nm > 0 else 'SELL'}")
    lines = [f"### {name} — {c.iloc[-1]:,.2f} ({last:%Y-%m-%d})",
             f"1 week {r1w:+.1%}, 1 month {r1m:+.1%}; {trend} its 200-day average; ADX {a:.0f}.",
             f"Signals for the next open: {', '.join(sigs) if sigs else 'none'}."]
    if nf is not None and len(nf.dropna()):
        row = nf.dropna().iloc[-1]
        lines.append(f"News (GDELT, to {nf.dropna().index[-1]:%Y-%m-%d}): tone {row.tone_z:+.1f}σ vs usual, "
                     f"coverage {row.attention_z:+.1f}σ.")
    heads = news.headlines(name, limit=5)
    if heads:
        lines += ["Headlines:"] + [f"- {h['title']} ({(h['published'] or '')[:16]})" for h in heads]
    return lines + [""]


def write_brief(source: str = "auto") -> Path:
    now = now_utc()
    today = now.normalize()
    cfg_path = PAPER_DIR / "config.json"  # the live account's assets
    assets = json.loads(cfg_path.read_text())["universe"] if cfg_path.exists() else UNIVERSE
    prices = {a: complete_bars(df, a, "1d", now) for a, df in load_prices(source, "1d", assets).items()}
    try:
        news_data = news.load_all(assets)
    except Exception as exc:
        log.warning("news unavailable (%s)", exc)
        news_data = {"fomc": [], "jobs": news.jobs_report_dates(), "gdelt": {}, "earnings": {}}

    px = core.load_universe(source)
    w = core.momentum_weights(px)
    picks = w.iloc[-1][w.iloc[-1] > 0].sort_values(ascending=False)
    core_earn = {a: news.earnings_dates(a) for a in picks.index if a in core.CORE_STOCKS}

    md = [f"# Daily brief — {today:%A %d %B %Y}", ""]
    ev = upcoming_events(news_data, today, 7, core_earn)
    md += ["## Coming up in the next 7 days", ""]
    md += [f"- **{d:%a %d %b}**: {what}" for d, what in ev] or ["- No scheduled market-moving events found."]
    md += ["", "## Core holdings this month (momentum)", ""]
    md += [f"- {a}: {wt:.0%}" for a, wt in picks.items()] or ["- Cash (nothing passes the filters)."]
    md += ["", "## Assets", ""]
    for a, df in prices.items():
        nf = news.news_features(news_data["gdelt"][a], df.index) if a in news_data["gdelt"] else None
        md += asset_snapshot(a, df, nf)
    status = PAPER_DIR / "status.md"
    if status.exists():
        md += ["## Paper account", "", *status.read_text().splitlines()[2:6], ""]
    views = analyst.load_views()
    if not views.empty:
        md += ["## AI analyst track record", "", analyst.track_record(analyst.score_views(views, prices)), ""]
    md += [AI_TASK.format(date=f"{today:%Y-%m-%d}")]
    out = PAPER_DIR / "brief.md"
    PAPER_DIR.mkdir(exist_ok=True)
    out.write_text("\n".join(md) + "\n")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default="auto", choices=["auto", "yahoo", "csv"])
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(f"Brief written to {write_brief(args.source)}")


if __name__ == "__main__":
    main()
