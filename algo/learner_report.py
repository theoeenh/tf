"""The learner's daily report: what the shared model has learned, and what changed.

    python -m algo.learner_report          # writes paper/learner/<date>.md and latest.json

Trained on the shared pool (every strategy on every asset, long and short, see
ml.Pool), the same brain all three accounts use. The report answers:
- Can it still tell good trades from bad ones? (checked on the most recent 20%
  of trades, which the model did not train on)
- What does it pay attention to? (permutation importance: how much worse the
  predictions get when one input is scrambled)
- What does it favour or avoid right now, by strategy, asset class and hour?
- What is new since yesterday: trades that closed, and how its views moved.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from . import news
from .ml import FEATURES, build_pool
from .paper import complete_bars, now_utc
from .system import build_context, load_prices

log = logging.getLogger(__name__)
OUT = Path(__file__).resolve().parent.parent / "paper" / "learner"

PLAIN = {
    "side": "long or short", "adx": "trend strength (ADX)", "atr_pct": "volatility (ATR %)",
    "vol_rank": "volatility vs its own past", "dist200": "distance to the 200-bar average",
    "dist50": "distance to the 50-bar average", "ret5": "momentum over 5 bars", "ret20": "momentum over 20 bars",
    "rsi14": "RSI(14)", "daily_trend": "daily trend agrees", "tone_z": "daily news tone (GDELT)",
    "attention_z": "daily news coverage (GDELT)", "days_to_earnings": "days to earnings",
    "days_to_fomc": "days to the Fed", "days_to_jobs": "days to the jobs report", "ai_bias": "AI analyst view",
    "news_1h": "articles in the last hour", "news_24h_z": "news coverage, 24 h vs usual",
    "news_tone": "headline tone, 24 h", "hour": "hour of the day", "weekday": "day of the week",
    "sleeve_recent_r": "how this strategy did lately on this asset", "sleeve_trades": "trades seen for this pair",
    "strategy_recent_r": "how this strategy did lately (all assets)",
    "asia_move": "how Asia moved on its last day", "europe_move": "how Europe moved on its last day",
} | {f"is_{s}": f"strategy: {s}" for s in ("donchian_trend", "squeeze_breakout", "rsi2_reversion",
                                              "news_momentum", "opening_range", "vwap_reversion")} \
  | {f"is_{c}": f"asset class: {c}" for c in ("crypto", "stock", "metal", "etf")}


def _model(X, y, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier

    m = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=150, min_samples_leaf=50,
                                       l2_regularization=1.0, early_stopping=False, random_state=seed)
    cols = ~np.all(np.isnan(X), axis=0)
    m.fit(X[:, cols], y)
    return m, cols


def analyse(pool_rows: pd.DataFrame, now: pd.Timestamp) -> dict:
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import roc_auc_score

    rows = pool_rows[pool_rows.exit_time < now].sort_values("exit_time").tail(20000)
    X = rows[list(FEATURES)].to_numpy(float)
    r = rows.r.to_numpy(float)
    y = (r > 0).astype(int)
    cut = int(len(rows) * 0.8)
    m, cols = _model(X[:cut], y[:cut])
    p_test = m.predict_proba(X[cut:][:, cols])[:, 1]
    auc = float(roc_auc_score(y[cut:], p_test)) if len(set(y[cut:])) == 2 else float("nan")
    q = pd.qcut(p_test, 5, labels=False, duplicates="drop")
    by_q = pd.Series(r[cut:]).groupby(q).mean().round(3).tolist()
    imp = permutation_importance(m, X[cut:][:, cols], y[cut:], n_repeats=5, random_state=0, scoring="roc_auc")
    names = [f for f, c in zip(FEATURES, cols) if c]
    importance = sorted(zip(names, imp.importances_mean), key=lambda t: -t[1])

    # today's brain: trained on everything closed so far, judging the last 30 days of signals
    full, fcols = _model(X, y)
    recent = rows[rows.exit_time >= now - pd.Timedelta(days=30)].copy()
    recent["p"] = full.predict_proba(recent[list(FEATURES)].to_numpy(float)[:, fcols])[:, 1] if len(recent) else []
    from .ml import ASSET_CLASS

    recent["cls"] = recent.asset.map(ASSET_CLASS)
    recent["hour"] = pd.to_datetime(recent.entry_time).dt.hour
    view = {k: recent.groupby(col).p.mean().round(3).to_dict() for k, col in
            (("strategy", "strategy"), ("asset_class", "cls"), ("hour", "hour"))} if len(recent) else {}
    last_day = rows[rows.exit_time >= now - pd.Timedelta(days=1)]
    return {"date": str(now.date()), "trained_on": int(len(rows)), "auc_recent": auc, "r_by_quintile": by_q,
            "importance": [(n, round(float(v), 4)) for n, v in importance[:10]],
            "view": view, "new_trades": int(len(last_day)),
            "new_trades_by_strategy": last_day.groupby("strategy").r.agg(["size", "mean"]).round(3)
            .reset_index().to_dict("records")}


def write(cfg_path: Path | None = None) -> Path:
    cfg_path = cfg_path or Path(__file__).resolve().parent.parent / "paper" / "config.json"
    cfg = json.loads(cfg_path.read_text())
    now = now_utc()
    prices = {a: complete_bars(df, a, cfg["interval"], now) for a, df in
              load_prices(cfg.get("source", "auto"), cfg["interval"], cfg["universe"], cfg.get("history_start")).items()}
    ctx = build_context(prices, news.load_all(list(prices), alpaca_news=cfg["interval"] != "1d"))
    pool = build_pool(prices, ctx)
    rep = analyse(pool.rows, now)
    OUT.mkdir(parents=True, exist_ok=True)
    prev_path = OUT / "latest.json"
    prev = json.loads(prev_path.read_text()) if prev_path.exists() else None
    prev_view = (prev or {}).get("view", {})

    def moved(kind):
        cur = rep["view"].get(kind, {})
        old = prev_view.get(kind, {})
        return sorted(((k, v - old[k]) for k, v in cur.items() if k in old and not pd.isna(old[k])),
                      key=lambda t: -abs(t[1]))[:3]

    md = [f"# What the learner learned – {rep['date']}", "",
          f"Shared brain of accounts A, B and C: trained on **{rep['trained_on']:,}** closed trades (every strategy "
          "on every asset, long and short, including the ones no account took).", "",
          "## Can it still tell good trades from bad?", "",
          f"On the most recent 20% of trades (not used for training): AUC **{rep['auc_recent']:.3f}** "
          "(0.50 = coin flip). Average R of those trades, ranked by the model from worst to best fifth: "
          + " / ".join(f"{v:+.2f}" for v in rep["r_by_quintile"]) + ". Rising from left to right = the ranking works.",
          "", "## What it pays attention to", ""]
    md += [f"{i}. {PLAIN.get(n, n)} ({v:+.4f})" for i, n_v in enumerate(rep["importance"], 1) for n, v in [n_v]]
    md += ["", "## What it favours now (chance of profit it gives signals of the last 30 days)", ""]
    for kind, label in (("strategy", "By strategy"), ("asset_class", "By asset class")):
        vals = rep["view"].get(kind, {})
        if vals:
            md += [f"**{label}:** " + ", ".join(f"{k} {v:.0%}" for k, v in sorted(vals.items(), key=lambda t: -t[1]))]
    hours = rep["view"].get("hour", {})
    if hours:
        best = sorted(hours.items(), key=lambda t: -t[1])
        md += [f"**Best hours (UTC):** " + ", ".join(f"{h}:00 {v:.0%}" for h, v in best[:3])
               + f"; worst: " + ", ".join(f"{h}:00 {v:.0%}" for h, v in best[-3:])]
    md += ["", "## Since yesterday", "",
           f"{rep['new_trades']} trades closed in the last 24 h (all strategies, followed with or without money)."]
    md += [f"- {d['strategy']}: {int(d['size'])} trade{'s' if d['size'] != 1 else ''}, avg {d['mean']:+.2f}R"
           for d in rep["new_trades_by_strategy"]]
    if prev:
        ch = moved("strategy") + moved("asset_class")
        md += ["", "Biggest changes in its views: " + (", ".join(f"{k} {v:+.1%}" for k, v in ch) if ch else "none")]
    else:
        md += ["", "First report: nothing to compare with yet."]
    out = OUT / f"{rep['date']}.md"
    out.write_text("\n".join(md) + "\n")
    prev_path.write_text(json.dumps(rep, indent=1, default=float))
    return out


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    print(f"Learner report: {write()}")


if __name__ == "__main__":
    main()
