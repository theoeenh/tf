"""Backtest the multi-asset system on daily and hourly bars and write a report.

    python -m algo.portfolio_run                  # Yahoo, falls back to data/*.csv
    python -m algo.portfolio_run --source csv     # cached CSVs only

Each variant's risk per trade is calibrated on the training window only, to
hit the target volatility; the test window is never used for any choice.
The learner runs through the whole history in time order (it can only use
trades already closed), so what it learned in training carries into test.
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from . import core, data, journal, news
from .engine import buy_and_hold
from .metrics import equity_stats
from .run import plot_equity
from .system import (
    ALL_VARIANTS, COSTS, MAX_GROSS, MAX_OPEN_RISK, OPTIONS, SLEEVE_RULES, TARGET_VOL, UNIVERSE, UNIVERSES, VARIANTS,
    bars_per_year, build_context, calibrate_risk, load_prices, run_random, run_variant,
)

log = logging.getLogger(__name__)

HIGHLIGHT = "long/short + learner + news"  # the full system, shown in detail
RANDOM_SEEDS = 20


def equal_weight(prices: dict[str, pd.DataFrame], start, end, capital=100_000.0) -> pd.Series:
    """Buy & hold every asset in equal weight, rebalanced each bar (assets join when listed)."""
    closes = pd.concat({a: df["Close"] for a, df in prices.items()}, axis=1, sort=True).ffill()
    rets = closes.pct_change().loc[start:end].mean(axis=1, skipna=True).fillna(0.0)
    return capital * (1 + rets).cumprod()


def window_stats(res, a, b, ppy) -> dict:
    eq = res.equity.loc[a:b]
    st = equity_stats(eq, ppy)
    t = res.trades_df
    if not t.empty:
        t = t[(t.exit_date >= eq.index[0]) & (t.exit_date <= eq.index[-1])]
    days = max((eq.index[-1] - eq.index[0]).days, 1)
    st |= {
        "trades": len(t),
        "per_day": len(t) / days,
        "shorts": int((t.side < 0).sum()) if len(t) else 0,
        "win_rate": (t.pnl > 0).mean() if len(t) else np.nan,
        "avg_r": t.r_multiple.mean() if len(t) else np.nan,
        "fees": t.fees.sum() if len(t) else 0.0,
        "gross": res.gross.loc[a:b].mean(),
    }
    return st


COLS = {
    "cagr": ("CAGR", "{:+.1%}"), "volatility": ("Vol", "{:.0%}"), "sharpe": ("Sharpe", "{:.2f}"),
    "max_drawdown": ("Max DD", "{:.1%}"), "trades": ("Trades", "{:.0f}"), "per_day": ("Trades/day", "{:.2f}"),
    "shorts": ("Shorts", "{:.0f}"), "win_rate": ("Win %", "{:.0%}"), "avg_r": ("Avg R", "{:+.2f}"),
    "fees": ("Fees $", "{:,.0f}"), "gross": ("Avg leverage", "{:.2f}x"),
}


def _summary_row(name: str, st: dict) -> dict:
    clean = name.replace("*", "").replace("↳ ", "").split(" (")[0]
    kind = "random" if "random" in name else "bench" if "↳" in name else "version"
    if kind == "random":
        clean = name.replace("*", "").replace("↳ ", "").split(" (skill")[0]
    return {"version": clean, "kind": kind,
            **{k: (float(st[k]) if k in st and np.isfinite(st[k]) else None)
               for k in ("cagr", "sharpe", "max_drawdown", "trades", "avg_r")}} | \
        {"max_dd": float(st["max_drawdown"]) if np.isfinite(st.get("max_drawdown", np.nan)) else None}


def table(rows: list[tuple[str, dict]]) -> str:
    cols = [c for c in COLS if any(c in r for _, r in rows)]
    out = ["| | " + " | ".join(COLS[c][0] for c in cols) + " |", "|---|" + "---:|" * len(cols)]
    for name, r in rows:
        out.append(f"| {name} | " + " | ".join(
            "–" if r.get(c) is None or pd.isna(r.get(c)) else COLS[c][1].format(r[c]) for c in cols) + " |")
    return "\n".join(out)


def study(prices, spy, train, test, label, out: Path, md: list[str], context: dict | None = None,
          variants: dict = VARIANTS, highlight: str = None, context_global: dict | None = None) -> dict:
    """Run every variant on one bar size; append the section to md."""
    global HIGHLIGHT
    HIGHLIGHT = highlight or HIGHLIGHT
    results, risks = {}, {}
    for name, v in variants.items():
        ctx = context_global if v.get("global") and context_global is not None else context
        log.info("%s: calibrating %s", label, name)
        risks[name] = calibrate_risk(prices, v["allow_short"], v["learn"], train[0], train[1],
                                     news=v.get("news", False), context=ctx,
                                     **{o: v.get(o, False) for o in OPTIONS})
        log.info("%s: running %s at %.2f%% risk per trade", label, name, 100 * risks[name])
        results[name] = run_variant(prices, v, risks[name], train[0], test[1], ctx)
    if HIGHLIGHT not in results:  # e.g. a --only run: show the last (newest) version in detail
        HIGHLIGHT = list(results)[-1]
    ppy = bars_per_year(results[HIGHLIGHT].equity.index)

    # Skill test: same system with random entries, several seeds.
    randoms = {}
    for name, short in (("long only", False), ("long/short", True)):
        log.info("%s: random-entry baseline %s", label, name)
        randoms[name] = [run_random(prices, short, risks.get(name, 0.0025), seed, train[0], test[1])
                         for seed in range(RANDOM_SEEDS)]

    ew = equal_weight(prices, train[0], test[1])
    spy_eq = buy_and_hold(spy, COSTS["SPY"], 100_000.0, train[0], test[1])
    spy_ppy = bars_per_year(spy_eq.index)

    md += [f"## {label}", ""]
    for wname, (a, b) in (("Train (risk calibrated here)", train), ("Test (never used for any choice)", test)):
        rows = [(f"**{n}** ({risks[n]:.2%}/trade)", window_stats(r, a, b, ppy)) for n, r in results.items()]
        for name, runs in randoms.items():
            stats = pd.DataFrame([window_stats(r, a, b, ppy) for r in runs]).mean().to_dict()
            rows.append((f"↳ *random entries, {name}* (skill test, avg of {RANDOM_SEEDS})", stats))
        rows += [("↳ equal-weight buy & hold, all 7 assets", equity_stats(ew.loc[a:b], ppy)),
                 ("↳ SPY", equity_stats(spy_eq.loc[a:b], spy_ppy))]
        if b == test[1]:  # the test window, as data (for the dashboard)
            summary = {"label": label, "window": f"{pd.Timestamp(a):%Y-%m-%d} to {'today' if b is None else b}",
                       "rows": [_summary_row(n, st) for n, st in rows],
                       "ml_reports": {n: r.learner.report() for n, r in results.items()
                                      if hasattr(r.learner, "report")}}
            (out / f"{label.split()[0].lower()}_summary.json").write_text(json.dumps(summary, indent=1,
                                                                                    default=float))
        md += [f"### {wname}: {pd.Timestamp(a).date()} → {pd.Timestamp(b).date() if b else 'today'}", "",
               table(rows), ""]

    hl = results[HIGHLIGHT]
    slug = label.split()[0].lower()
    plot_equity({HIGHLIGHT: (hl.equity, "strategy"), "equal-weight buy & hold": (ew, "buy_hold"),
                 "SPY": (spy_eq, "benchmark")}, f"{label} · {HIGHLIGHT}", out / f"{slug}_equity.png")
    md += [f"![equity]({slug}_equity.png)", ""]

    # What made and lost money, test window only.
    t = hl.trades_df
    tt = t[t.exit_date >= pd.Timestamp(test[0])]
    if not tt.empty:
        piv = tt.pivot_table(index="asset", columns="strategy", values="r_multiple", aggfunc="sum").round(1)
        md += [f"**Where the R came from in the test window ({HIGHLIGHT}), sum of R per asset × strategy:**", "",
               "| asset | " + " | ".join(piv.columns) + " |", "|---|" + "---:|" * len(piv.columns)]
        md += [f"| {a} | " + " | ".join("–" if pd.isna(v) else f"{v:+.1f}" for v in piv.loc[a]) + " |"
               for a in piv.index]
        md += [""]

    # Error analysis on all real trades.
    tj = journal.tag_stop_too_tight(t, prices)
    err = tj.groupby("error").agg(trades=("r_multiple", "size"), total_r=("r_multiple", "sum"),
                                  avg_r=("r_multiple", "mean")).sort_values("total_r")
    err["share"] = err.trades / err.trades.sum()
    md += [f"### What went wrong – diagnosis of every {HIGHLIGHT} trade", "",
           "| Diagnosis | Meaning | Trades | Share | Total R | Avg R |", "|---|---|---:|---:|---:|---:|"]
    md += [f"| {e} | {journal.ERRORS[e]} | {r.trades:.0f} | {r.share:.0%} | {r.total_r:+.1f} | {r.avg_r:+.2f} |"
           for e, r in err.iterrows()]
    md += [""]

    # What the learner learned, and whether skipping was right.
    lessons = hl.learner.lessons() if hl.learner else pd.DataFrame()
    sh = pd.DataFrame([s.__dict__ for s in hl.shadow_trades])
    md += ["### What the learner learned", ""]
    if not sh.empty:
        md += [f"It skipped **{len(sh)}** trades. Followed without money, those skipped trades averaged "
               f"**{sh.r_multiple.mean():+.2f}R** (total {sh.r_multiple.sum():+.1f}R). "
               + ("Negative = skipping them was right." if sh.r_multiple.mean() < 0 else
                  "Positive = skipping them cost money; the learner was wrong on balance."), ""]
    if not lessons.empty and "view" in lessons:
        views = ["setup", "news", "event", "ai"]
        md += ["What each view of the learner found (conditions with at least 10 trades):", "",
               "| View | Conditions tracked | Blocked now | Worst condition | Its avg R |", "|---|---:|---:|---|---:|"]
        for vname in views:
            g = lessons[lessons.view == vname]
            if g.empty:
                continue
            w = g.sort_values("recent_avg_r").iloc[0]
            md.append(f"| {vname} | {len(g)} | {(g.status == 'blocked').sum()} | {w.setup} | {w.recent_avg_r:+.2f} |")
        md += [""]
        for vname in ("news", "event"):
            g = lessons[lessons.view == vname].sort_values("recent_avg_r")
            if len(g):
                md += [f"**{vname.capitalize()} lessons** (all conditions with ≥ 10 trades):", "",
                       "| Condition | Trades | Avg R, all | Avg R, last 60 | Win % | Status |",
                       "|---|---:|---:|---:|---:|---|"]
                md += [f"| {r.setup} | {r.trades} | {r.avg_r:+.2f} | {r.recent_avg_r:+.2f} | {r.win_rate:.0%} | "
                       f"{r.status} |" for _, r in g.iterrows()]
                md += [""]
    if not lessons.empty:
        blocked = lessons[lessons.status == "blocked"].sort_values("recent_avg_r")
        md += [f"**{len(blocked)}** setups were blocked at the end of the run (their last up-to-60 trades averaged "
               f"below -0.1R). The 10 worst:", "",
               "| Setup | Trades seen | Avg R, all | Avg R, last 60 | Win % |", "|---|---:|---:|---:|---:|"]
        md += [f"| {r.setup} | {r.trades} | {r.avg_r:+.2f} | {r.recent_avg_r:+.2f} | {r.win_rate:.0%} |"
               for _, r in blocked.head(10).iterrows()]
        md += ["", "Best setups:", "", "| Setup | Trades seen | Avg R, all | Avg R, last 60 | Win % |",
               "|---|---:|---:|---:|---:|"]
        md += [f"| {r.setup} | {r.trades} | {r.avg_r:+.2f} | {r.recent_avg_r:+.2f} | {r.win_rate:.0%} |"
               for _, r in lessons.sort_values("recent_avg_r", ascending=False).head(5).iterrows()]
        md += [""]

    # The ML learner's predictions, each made before the trade's outcome was known.
    ml_rows = [(n, r.learner.report()) for n, r in results.items() if hasattr(r.learner, "report")]
    if ml_rows:
        md += ["### ML learner, out of sample", "",
               "Every prediction was made before the trade's result was known (walk-forward refits on closed "
               "trades only). AUC 0.50 = no better than a coin; the quintiles show the average R of trades "
               "ranked by the model's expected result, worst to best: rising = the ranking works.", "",
               "| Version | Refits | Judged | AUC | Taken | Taken avg R | Skipped | Skipped avg R | R by quintile |",
               "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for n, rep in ml_rows:
            if not rep.get("judged"):
                continue
            q = " / ".join(f"{v:+.2f}" for v in rep["by_quintile"].values())
            md.append(f"| {n} | {rep['fits']} | {rep['judged']} | {rep['auc']:.3f} | {rep['taken']} | "
                      f"{rep['taken_avg_r']:+.2f} | {rep['skipped']} | {rep['skipped_avg_r']:+.2f} | {q} |")
        md += [""]

    # Journal sample.
    md += ["### Journal – last 8 closed trades", ""]
    for _, r in tj[tj.reason != "end"].tail(8).iterrows():
        md += [f"- **{r.exit_date:%Y-%m-%d %H:%M} · {r.asset} · {r.strategy} · {r.r_multiple:+.2f}R** "
               f"({r.reason})  \n  *Thinking:* {r.rationale}  \n  *Lesson:* {r.lesson}"]
    md += [""]
    tj.to_csv(out / f"{slug}_journal.csv", index=False)
    if not sh.empty:
        sh.to_csv(out / f"{slug}_skipped_trades.csv", index=False)
    return results


def core_study(source: str, tactical: pd.Series, out: Path, md: list[str]) -> None:
    """Momentum core holdings, their random twin, and a 50/50 mix with the tactical system."""
    px = core.load_universe(source)
    data.TICKERS.setdefault("QQQ", "QQQ")
    qqq = data.load("QQQ", source)
    spy = data.load("SPY", source)
    start = "2017-01-01"
    w = core.momentum_weights(px)
    eq, _ = core.backtest_core(px, w, start)
    rand = [core.backtest_core(px, core.momentum_weights(px, rng=np.random.default_rng(s)), start)[0]
            for s in range(20)]
    ew_rets = px.pct_change().loc[start:].mean(axis=1, skipna=True).fillna(0.0)
    ew = 100_000 * (1 + ew_rets).cumprod()
    q_eq = buy_and_hold(qqq, COSTS["SPY"], 100_000.0, start)
    s_eq = buy_and_hold(spy, COSTS["SPY"], 100_000.0, start)
    tac = tactical.reindex(eq.index, method="ffill").dropna()
    mix_r = 0.5 * eq.pct_change() + 0.5 * tac.reindex(eq.index).pct_change()
    mix = 100_000 * (1 + mix_r.fillna(0.0)).cumprod()

    md += ["## Core holdings: own the strongest assets for months (momentum)", "",
           f"Universe fixed in advance: {', '.join(px.columns)} (the big tech names of end-2016, winners and "
           "laggards alike, plus crypto and metals). Each month: rank by 12-month return (skipping the last month), "
           f"keep assets above their 200-day average, hold the top {core.TOP_N} weighted by inverse volatility. "
           "No leverage, costs on every rebalance. The random twin holds 5 random assets from the same list.", ""]
    for wname, (a, b) in (("2017–2022", (start, "2022-12-31")), ("Test 2023 → today", ("2023-01-01", None))):
        rows = [("**Momentum core**", equity_stats(eq.loc[a:b], 252)),
                ("**50% core + 50% tactical system**", equity_stats(mix.loc[a:b], 252)),
                ("↳ *random 5 picks, same rules* (avg of 20)",
                 pd.DataFrame([equity_stats(r.loc[a:b], 252) for r in rand]).mean().to_dict()),
                ("↳ equal weight, whole list", equity_stats(ew.loc[a:b], 252)),
                ("↳ QQQ (Nasdaq 100)", equity_stats(q_eq.loc[a:b], 252)),
                ("↳ SPY", equity_stats(s_eq.loc[a:b], 252))]
        md += [f"### {wname}", "", table(rows), ""]
    plot_equity({"momentum core": (eq, "strategy"), "random 5 picks (avg)": (pd.concat(rand, axis=1).mean(axis=1),
                 "buy_hold"), "QQQ": (q_eq, "benchmark")}, "Core holdings since 2017", out / "core_equity.png")
    md += ["![core](core_equity.png)", ""]
    hy = core.holdings_by_year(w.loc["2016-12":])
    hy = hy.loc[:, hy.sum() > 0]
    md += ["Months held per year (decided each month end with only the data known then):", "",
           "| Asset | " + " | ".join(str(y) for y in hy.index) + " |", "|---|" + "---:|" * len(hy.index)]
    for a in hy.sum().sort_values(ascending=False).index:
        md.append(f"| {a} | " + " | ".join(str(int(v)) if v else "·" for v in hy[a]) + " |")
    md += [""]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default="auto", choices=["auto", "yahoo", "csv", "alpaca"])
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--skip-hourly", action="store_true")
    ap.add_argument("--hourly-only", action="store_true", help="only the hourly study (no daily, no core)")
    ap.add_argument("--upgrades", action="store_true",
                    help="also test the upgrades (trend filter, event blackout, ML learner)")
    ap.add_argument("--only", nargs="+", default=None, help="test only these versions (names from ALL_VARIANTS)")
    ap.add_argument("--universe", default="core", choices=list(UNIVERSES))
    args = ap.parse_args()
    variants = ALL_VARIANTS if args.upgrades else VARIANTS
    if args.only:
        variants = {n: ALL_VARIANTS[n] for n in args.only}
    universe = UNIVERSES[args.universe]
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    out = args.out or Path("reports") / f"{date.today()}-portfolio"
    out.mkdir(parents=True, exist_ok=True)

    md = [f"# Multi-asset system ({date.today()})", "",
          f"Universe: {', '.join(UNIVERSES[args.universe])}. Each asset runs all three strategies at once "
          "(" + ", ".join(f"{k}: {v.label()}" for k, v in SLEEVE_RULES.items()) + "), "
          "so up to 21 trades can be open together, and on hourly bars a strategy can trade many times a day.",
          "",
          f"One $100,000 account. Risk per trade is set on the training window so the account runs at about "
          f"**{TARGET_VOL:.0%} yearly volatility**; leverage up to {MAX_GROSS:g}x (6%/yr interest on borrowed cash), "
          f"at most {MAX_OPEN_RISK:.0%} of equity at risk across open trades.",
          "",
          "Costs on every fill: " + "; ".join(f"{a} {c.fee_bps:g}+{c.slippage_bps:g} bps"
                                             for a, c in COSTS.items() if a in UNIVERSES[args.universe])
          + " (fee + slippage per side). Shorts pay 10%/yr borrow on crypto, 1%/yr on stocks and metals.",
          "",
          "Variants: long only vs long/short, each with and without the **learner** (skips setups whose "
          "recent trades lost money; see `algo/journal.py`), and the full system with **news**: the learner "
          "also judges news tone and coverage, upcoming earnings / Fed / jobs events, and a news-momentum "
          "strategy trades bursts of one-sided news.", "",
          "**How to read this:** buy & hold tells you what the market did. The *random entries* rows run the "
          "exact same exits, sizing and costs with coin-flip entries: whatever they earn is market drift, "
          "not skill. A strategy shows real skill only by the margin it beats its random twin.", ""]

    daily = load_prices(args.source, "1d") if not args.hourly_only else None
    spy = data.load("SPY", args.source) if not args.hourly_only else None
    news_data = news.load_all(UNIVERSE if args.universe == "core" else universe)
    md += ["News data (point-in-time, see `algo/news.py`): GDELT daily tone and coverage for "
           f"{', '.join(k for k in news_data['gdelt'] if k != 'MACRO')}; "
           f"{len(news_data['fomc'])} Fed decision dates; earnings dates for "
           f"{', '.join(k for k, v in news_data['earnings'].items() if v)}; jobs report dates. "
           "The AI analyst is not in these backtests on purpose: a language model already knows what "
           "happened after any past headline, so its past calls would be fake. It is tested forward only.", ""]
    if not args.hourly_only:
        first = daily["BTC"].index[-1] - pd.DateOffset(years=10)
        res = study(daily, spy, (first, "2022-12-31"), ("2023-01-01", None), "Daily bars, 10 years", out, md,
                    build_context(daily, news_data), variants)
        core_study(args.source, res[HIGHLIGHT].equity, out, md)

    if not args.skip_hourly:
        hourly = load_prices(args.source, "1h", universe)
        spy_h = data.load("SPY", args.source, interval="1h")
        if args.source == "alpaca":  # hourly headlines with exact times
            news_data = news.load_all(universe, alpaca_news=True)
        idx = hourly["BTC"].index
        split = idx[0] + (idx[-1] - idx[0]) * 0.6
        span = f"{idx[0]:%Y-%m} to {idx[-1]:%Y-%m}"
        ctx_g = None
        if any(v.get("global") for v in variants.values()):  # Asia / Europe features for those versions
            ctx_g = build_context(hourly, news_data | {"global": news.load_global_indices()})
        study(hourly, spy_h, (idx[0] + pd.Timedelta(days=10), split), (split + pd.Timedelta(hours=1), None),
              f"Hourly bars, {span}", out, md, build_context(hourly, news_data), variants, context_global=ctx_g)

    (out / "report.md").write_text("\n".join(md))
    print(f"Report written to {out / 'report.md'}")


if __name__ == "__main__":
    main()
