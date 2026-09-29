"""Run the full test plan for every strategy on BTC and gold and write a report.

    python -m algo.run                      # Yahoo, falls back to data/*.csv
    python -m algo.run --source csv         # cached CSVs only
    python -m algo.run --source synthetic   # fake prices, pipeline check only
"""
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, LogLocator
import pandas as pd

from . import data
from .engine import buy_and_hold
from .metrics import alpha_beta, equity_stats, summarize
from .research import (
    BASELINE_EXIT, COSTS, INITIAL_CAPITAL, grid_search, periods, pick_best, run, synthetic_prices, walk_forward,
)
from .strategies import STRATEGIES

ASSETS = ("BTC", "GOLD")
BENCHMARK = "SPY"

# Categorical slots 1-3 of the reference palette (validated all-pairs, light surface).
COLORS = {"strategy": "#2a78d6", "buy_hold": "#eb6834", "benchmark": "#1baf7a"}
INK, INK_MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

TABLE_COLS = {
    "final_equity": ("Final $", "{:,.0f}"),
    "total_return": ("Return", "{:+.1%}"),
    "cagr": ("CAGR", "{:+.1%}"),
    "sharpe": ("Sharpe", "{:.2f}"),
    "max_drawdown": ("Max DD", "{:.1%}"),
    "calmar": ("Calmar", "{:.2f}"),
    "trades": ("Trades", "{:.0f}"),
    "win_rate": ("Win %", "{:.0%}"),
    "avg_r": ("Avg R", "{:+.2f}"),
    "profit_factor": ("PF", "{:.2f}"),
    "exposure": ("Time in mkt", "{:.0%}"),
    "alpha": ("Alpha vs B&H", "{:+.1%}"),
    "beta": ("Beta", "{:.2f}"),
}


def fmt_table(rows: list[tuple[str, dict]]) -> str:
    cols = [c for c in TABLE_COLS if any(c in r for _, r in rows)]
    head = "| | " + " | ".join(TABLE_COLS[c][0] for c in cols) + " |"
    sep = "|---|" + "---:|" * len(cols)
    lines = [head, sep]
    for name, r in rows:
        cells = []
        for c in cols:
            v = r.get(c)
            cells.append("–" if v is None or pd.isna(v) else TABLE_COLS[c][1].format(v))
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def plot_equity(curves: dict[str, tuple[pd.Series, str]], title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=130)
    for label, (eq, role) in curves.items():
        ax.plot(eq.index, eq.values, color=COLORS[role], lw=1.5, label=label)
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(LogLocator(subs=(1, 2, 5)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v / 1e6:,.0f}M" if v >= 1e6 else f"${v / 1e3:,.0f}k" if v >= 1e3 else f"${v:,.0f}"))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    # End-of-line labels, pushed apart so they never overlap (log space).
    ends = sorted(((np.log10(eq.iloc[-1]), label, eq) for label, (eq, _) in curves.items()), key=lambda t: t[0])
    lo, hi = (np.log10(v) for v in ax.get_ylim())
    gap, placed = (hi - lo) * 0.06, []
    for y, label, eq in ends:
        y_lab = max(y, placed[-1] + gap) if placed else y
        placed.append(y_lab)
        ax.annotate(f"{label}  ${eq.iloc[-1]:,.0f}", (eq.index[-1], eq.iloc[-1]), xytext=(eq.index[-1] + (eq.index[-1] - eq.index[0]) * 0.01, 10 ** y_lab),
                    textcoords="data", va="center", ha="left", fontsize=8, color=INK,
                    xycoords="data", annotation_clip=False)
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_ylabel("Account value ($, log scale)", color=INK_MUTED, fontsize=9)
    ax.grid(True, color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK_MUTED, labelsize=8)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.subplots_adjust(right=0.8)
    fig.savefig(path)
    plt.close(fig)


def load_all(source: str) -> dict[str, pd.DataFrame]:
    if source == "synthetic":
        return {n: synthetic_prices(n) for n in (*ASSETS, BENCHMARK)}
    return {n: data.load(n, source) for n in (*ASSETS, BENCHMARK)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default="auto", choices=["auto", "yahoo", "csv", "synthetic"])
    ap.add_argument("--out", type=Path, default=None, help="report directory")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    out = args.out or Path("reports") / f"{date.today()}-{args.source}"
    out.mkdir(parents=True, exist_ok=True)
    prices = load_all(args.source)
    spy = prices[BENCHMARK]

    md = [f"# Strategy comparison – BTC & Gold ({date.today()})", ""]
    if args.source == "synthetic":
        md += ["> **SYNTHETIC DATA.** These numbers only check that the pipeline runs. "
               "They say nothing about real markets.", ""]
    md += [
        f"Account: ${INITIAL_CAPITAL:,.0f} per asset, 1% risk per trade, long only, no leverage. "
        "Signals on the close, fills on the next open, stop assumed first when a bar hits both levels.",
        "",
        "Costs per side: " + ", ".join(f"{a} {c.fee_bps:g} bps fee + {c.slippage_bps:g} bps slippage"
                                       for a, c in COSTS.items() if a in ASSETS) + ".",
        "",
        "Exit rules are tuned on the **train** period only (best Sharpe, min 10 trades); "
        "test, YTD and last month are untouched. Alpha is Jensen's alpha vs the asset's buy & hold.",
        "",
    ]
    leaderboard, leaderboard_pos = [], len(md)

    for asset in ASSETS:
        df = prices[asset]
        ppy = data.PERIODS_PER_YEAR[asset]
        per = periods(df.index[-1])
        md += [f"## {asset}", ""]

        for strat_name, strat in STRATEGIES.items():
            entries = strat(df)
            tr = per["train"]
            grid = grid_search(df, entries, asset, ppy, tr.start, tr.end)
            rule = pick_best(grid)
            md += [f"### {asset} · {strat_name}", "",
                   f"Exit chosen on train: stop **{rule.stop_atr:g} ATR**, reward:risk **{rule.rr:g}:1**", ""]

            rows = []
            for key in ("full_10y", "train", "test", "ytd", "last_month"):
                p = per[key]
                try:
                    res = run(df, entries, rule, asset, p.start, p.end)
                except ValueError:
                    continue
                bh = buy_and_hold(df, COSTS[asset], INITIAL_CAPITAL, p.start, p.end)
                strat_stats = summarize(res, ppy, bh)
                rows.append((f"**{p.name}**", strat_stats))
                rows.append((f"↳ {asset} buy & hold", equity_stats(bh, ppy)))
                spy_eq = buy_and_hold(spy, COSTS[BENCHMARK], INITIAL_CAPITAL, p.start, p.end)
                rows.append((f"↳ {BENCHMARK} benchmark", equity_stats(spy_eq, data.PERIODS_PER_YEAR[BENCHMARK])))
                if key == "full_10y":
                    plot_equity(
                        {strat_name: (res.equity, "strategy"), f"{asset} buy & hold": (bh, "buy_hold"),
                         f"{BENCHMARK}": (spy_eq, "benchmark")},
                        f"{asset} · {strat_name} · last 10 years", out / f"{asset}_{strat_name}_10y.png",
                    )
                    res.trades_df.to_csv(out / f"{asset}_{strat_name}_trades.csv", index=False)
                if key == "test":
                    leaderboard.append({"asset": asset, "strategy": strat_name, "rule": f"{rule.stop_atr:g} ATR / {rule.rr:g}:1",
                                        **{k: strat_stats[k] for k in ("cagr", "sharpe", "max_drawdown", "trades", "alpha")}})
            md += [fmt_table(rows), "", f"![equity]({asset}_{strat_name}_10y.png)", ""]

            # Baseline 3:1 over the full window for reference, and robustness of the grid.
            base = summarize(run(df, entries, BASELINE_EXIT, asset, per["full_10y"].start, None), ppy)
            md += [f"Baseline 2 ATR / 3:1 over 10 years: CAGR {base['cagr']:+.1%}, Sharpe {base['sharpe']:.2f}, "
                   f"max DD {base['max_drawdown']:.1%}, {base['trades']:.0f} trades.", ""]
            heat = grid.pivot(index="stop_atr", columns="rr", values="sharpe")
            md += ["Train-period Sharpe by exit rule (rows: stop in ATR, columns: reward:risk). "
                   "A good rule sits in a region of similar values, not an isolated peak:", "",
                   "| stop \\ rr | " + " | ".join(f"{c:g}:1" for c in heat.columns) + " |",
                   "|---|" + "---:|" * len(heat.columns)]
            md += [f"| {r:g} | " + " | ".join("–" if pd.isna(v) else f"{v:.2f}" for v in heat.loc[r]) + " |"
                   for r in heat.index]
            md += [""]

            wf_eq, wf_rules = walk_forward(df, entries, asset, ppy, first_test_year=2020)
            if not wf_eq.empty:
                wf_bh = buy_and_hold(df, COSTS[asset], INITIAL_CAPITAL, wf_eq.index[0], wf_eq.index[-1])
                s = equity_stats(wf_eq, ppy) | alpha_beta(wf_eq, wf_bh, ppy)
                b = equity_stats(wf_bh, ppy)
                md += [f"**Walk-forward {wf_eq.index[0].year}–{wf_eq.index[-1].year}** (re-tuned each year on the prior 4 years): "
                       f"CAGR {s['cagr']:+.1%} vs buy & hold {b['cagr']:+.1%}, Sharpe {s['sharpe']:.2f} vs {b['sharpe']:.2f}, "
                       f"max DD {s['max_drawdown']:.1%} vs {b['max_drawdown']:.1%}, alpha {s['alpha']:+.1%}.", "",
                       "| Year | Stop ATR | R:R | Return | Trades |", "|---|---:|---:|---:|---:|"]
                md += [f"| {int(r.year)} | {r.stop_atr:g} | {r.rr:g}:1 | {r['return']:+.1%} | {r.trades:.0f} |"
                       for _, r in wf_rules.iterrows()]
                md += [""]

    lb = pd.DataFrame(leaderboard).sort_values(["asset", "sharpe"], ascending=[True, False])
    md[leaderboard_pos:leaderboard_pos] = [
        "## Leaderboard – hold-out test 2023–2025", "",
        "| Asset | Strategy | Exit | CAGR | Sharpe | Max DD | Trades | Alpha |", "|---|---|---|---:|---:|---:|---:|---:|",
        *[f"| {r.asset} | {r.strategy} | {r.rule} | {r.cagr:+.1%} | {r.sharpe:.2f} | {r.max_drawdown:.1%} | {r.trades:.0f} | "
          f"{'–' if pd.isna(r.alpha) else f'{r.alpha:+.1%}'} |" for _, r in lb.iterrows()],
        "",
    ]
    (out / "report.md").write_text("\n".join(md))
    print(f"Report written to {out / 'report.md'}")


if __name__ == "__main__":
    main()
