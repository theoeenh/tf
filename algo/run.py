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
    COSTS, DIRECTIONS, EXIT_MODES, INITIAL_CAPITAL, grid_search, periods, pick_best, run, synthetic_prices,
    walk_forward,
)
from .strategies import STRATEGIES

ASSETS = ("BTC", "GOLD")
SELECTION_END, OOS_START = "2022-12-31", "2023-01-01"
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
    "shorts": ("of which short", "{:.0f}"),
    "win_rate": ("Win %", "{:.0%}"),
    "avg_r": ("Avg R", "{:+.2f}"),
    "profit_factor": ("PF", "{:.2f}"),
    "fees": ("Fees $", "{:,.0f}"),
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


def evaluate(df, signals, asset, ppy, per, mode, direction) -> dict:
    """Tune on train, then measure every period and the walk-forward."""
    tr = per["train"]
    rule = pick_best(grid_search(df, signals, asset, ppy, tr.start, tr.end, mode, direction))
    out = {"rule": rule, "stats": {}, "results": {}}
    for key, p in per.items():
        try:
            res = run(df, signals, rule, asset, p.start, p.end, direction)
        except ValueError:
            continue
        bh = buy_and_hold(df, COSTS[asset], INITIAL_CAPITAL, p.start, p.end)
        out["results"][key] = res
        out["stats"][key] = summarize(res, ppy, bh)
    wf_eq, wf_rules = walk_forward(df, signals, asset, ppy, mode, direction)
    out["wf_eq"], out["wf_rules"] = wf_eq, wf_rules
    if not wf_eq.empty:
        wf_bh = buy_and_hold(df, COSTS[asset], INITIAL_CAPITAL, wf_eq.index[0], wf_eq.index[-1])
        out["wf"] = equity_stats(wf_eq, ppy) | alpha_beta(wf_eq, wf_bh, ppy)
        out["wf_bh"] = equity_stats(wf_bh, ppy)
        # Split the walk-forward: 2020-2022 is used to pick finalists, 2023+ judges them.
        sel, oos = wf_eq[:SELECTION_END], wf_eq[OOS_START:]
        out["wf_sel_sharpe"] = equity_stats(sel, ppy)["sharpe"]
        oos_bh = buy_and_hold(df, COSTS[asset], INITIAL_CAPITAL, oos.index[0], oos.index[-1])
        out["wf_oos"] = equity_stats(oos, ppy) | alpha_beta(oos, oos_bh, ppy)
        out["wf_oos_bh"] = equity_stats(oos_bh, ppy)
    return out


def pct(v, f="{:+.1%}"):
    return "–" if v is None or pd.isna(v) else f.format(v)


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
        f"Account: ${INITIAL_CAPITAL:,.0f} per asset, 1% risk per trade, no leverage. "
        "Signals on the close, fills on the next open, stop assumed first when a bar hits both levels, "
        "an opposite signal reverses the position.",
        "",
        "Costs, all included in every number below: " + "; ".join(
            f"{a} {c.fee_bps:g} bps fee + {c.slippage_bps:g} bps slippage per side"
            + (f", shorts pay {c.short_borrow_apr:.0%}/yr borrow" if "long_short" in DIRECTIONS[a] else "")
            for a, c in COSTS.items() if a in ASSETS) + ".",
        "",
        "Exit families (each rule tuned on the **train** period only, best Sharpe with ≥ 10 trades):",
        "- **fixed** – one reward:risk for every trade (e.g. 2 ATR stop + 3:1 = your 6:2).",
        "- **trailing** – no target; a trailing stop follows the best close and lets winners run.",
        "- **adaptive** – normal markets use ~2:1 (4:2); when ADX ≥ 25 (strong trend) the target widens "
        "to 3:1 / 4:1 (6:2 / 8:2) or is dropped for a trailing stop.",
        "",
        "**Walk-forward** re-tunes the rule every January on the previous 4 years and trades the next year "
        "blind. It is the most honest number here. Alpha = Jensen's alpha vs the asset's buy & hold.",
        "",
    ]
    lb_pos = len(md)
    board, evals = [], {}

    for asset in ASSETS:
        df = prices[asset]
        ppy = data.PERIODS_PER_YEAR[asset]
        per = periods(df.index[-1])
        for strat_name, strat in STRATEGIES.items():
            signals = strat(df)
            for direction in DIRECTIONS[asset]:
                for mode in EXIT_MODES:
                    logging.info("%s %s %s %s", asset, strat_name, direction, mode)
                    ev = evaluate(df, signals, asset, ppy, per, mode, direction)
                    key = (asset, strat_name, direction, mode)
                    evals[key] = ev
                    st = ev["stats"]
                    board.append({
                        "key": key, "asset": asset, "strategy": strat_name, "direction": direction.replace("_", "/"),
                        "mode": mode, "rule": ev["rule"].label(),
                        "train_sharpe": st["train"]["sharpe"], "wf_sel_sharpe": ev.get("wf_sel_sharpe"),
                        "wf_cagr": ev.get("wf_oos", {}).get("cagr"), "wf_sharpe": ev.get("wf_oos", {}).get("sharpe"),
                        "wf_dd": ev.get("wf_oos", {}).get("max_drawdown"), "wf_alpha": ev.get("wf_oos", {}).get("alpha"),
                        "ytd": st.get("ytd", {}).get("total_return"),
                        "trades": st["full_10y"]["trades"], "fees": st["full_10y"]["fees"],
                    })

    board = pd.DataFrame(board)
    finalists = {a: board[board.asset == a].sort_values("wf_sel_sharpe", ascending=False).iloc[0] for a in ASSETS}

    lb = ["## Leaderboard – all combinations", "",
          "The walk-forward is split in two. **WF 2020–22** is used to pick the finalist (★, best Sharpe there). "
          "**WF 2023–today** was never used for any choice: it is the real out-of-sample result. "
          "Rows are sorted by that out-of-sample Sharpe.", ""]
    for asset in ASSETS:
        ev0 = evals[board[board.asset == asset].iloc[0]["key"]]
        bh_wf = ev0.get("wf_oos_bh", {})
        ppy = data.PERIODS_PER_YEAR[asset]
        by = equity_stats(buy_and_hold(prices[asset], COSTS[asset], INITIAL_CAPITAL, "2026-01-01", None), ppy)
        lb += [f"### {asset}", "",
               "| | Strategy | Dir | Exit | Rule (from train) | Train Sharpe | WF 2020–22 Sharpe "
               "| **WF 2023– Sharpe** | WF 2023– CAGR | WF 2023– Max DD | WF 2023– Alpha | 2026 YTD | 10y trades | 10y fees $ |",
               "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for _, r in board[board.asset == asset].sort_values("wf_sharpe", ascending=False).iterrows():
            star = "★" if r.key == finalists[asset].key else ""
            lb.append(f"| {star} | {r.strategy} | {r.direction} | {r['mode']} | {r.rule} | {pct(r.train_sharpe, '{:.2f}')} "
                      f"| {pct(r.wf_sel_sharpe, '{:.2f}')} | **{pct(r.wf_sharpe, '{:.2f}')}** | {pct(r.wf_cagr)} "
                      f"| {pct(r.wf_dd)} | {pct(r.wf_alpha)} | {pct(r.ytd)} | {r.trades:.0f} | {r.fees:,.0f} |")
        lb.append(f"| | *{asset} buy & hold* | | | | | | **{pct(bh_wf.get('sharpe'), '{:.2f}')}** | {pct(bh_wf.get('cagr'))} "
                  f"| {pct(bh_wf.get('max_drawdown'))} | | {pct(by['total_return'])} | | |")
        lb.append("")

    # Detail for each finalist.
    for asset in ASSETS:
        f = finalists[asset]
        ev = evals[f.key]
        df, ppy = prices[asset], data.PERIODS_PER_YEAR[asset]
        per = periods(df.index[-1])
        name = f"{f.strategy} · {f.direction} · {f['mode']}"
        md_rows = []
        for key, p in per.items():
            if key not in ev["stats"]:
                continue
            md_rows.append((f"**{p.name}**", ev["stats"][key]))
            bh = buy_and_hold(df, COSTS[asset], INITIAL_CAPITAL, p.start, p.end)
            md_rows.append((f"↳ {asset} buy & hold", equity_stats(bh, ppy)))
            spy_eq = buy_and_hold(spy, COSTS[BENCHMARK], INITIAL_CAPITAL, p.start, p.end)
            md_rows.append((f"↳ {BENCHMARK} benchmark", equity_stats(spy_eq, data.PERIODS_PER_YEAR[BENCHMARK])))
        full = per["full_10y"]
        res = ev["results"]["full_10y"]
        bh = buy_and_hold(df, COSTS[asset], INITIAL_CAPITAL, full.start, None)
        spy_eq = buy_and_hold(spy, COSTS[BENCHMARK], INITIAL_CAPITAL, full.start, None)
        plot_equity({"strategy": (res.equity, "strategy"), f"{asset} buy & hold": (bh, "buy_hold"),
                     BENCHMARK: (spy_eq, "benchmark")},
                    f"{asset} finalist · {name} · last 10 years", out / f"{asset}_finalist_10y.png")
        res.trades_df.to_csv(out / f"{asset}_finalist_trades.csv", index=False)
        md += [f"## {asset} finalist: {name}", "", f"Rule: **{ev['rule'].label()}**", "",
               fmt_table(md_rows), "", f"![equity]({asset}_finalist_10y.png)", ""]
        if not ev["wf_rules"].empty:
            md += ["Walk-forward, rule re-chosen each year:", "",
                   "| Year | Rule | Return | Trades | Fees $ |", "|---|---|---:|---:|---:|"]
            md += [f"| {int(r.year)} | {r.rule} | {r['return']:+.1%} | {r.trades:.0f} | {r.fees:,.0f} |"
                   for _, r in ev["wf_rules"].iterrows()]
            md += [""]

    # Portfolio: the two finalists with half the capital each.
    half = INITIAL_CAPITAL / 2
    port_md = ["## Portfolio – both finalists, $50k each", "",
               "Each finalist runs on its own $50k with the same rules. Compared with 50/50 buy & hold "
               "of BTC and gold (not rebalanced) and with SPY.", ""]
    rows = []
    for key in ("full_10y", "test", "ytd"):
        p = periods(prices["BTC"].index[-1])[key]
        legs, bh_legs = [], []
        for asset in ASSETS:
            f = finalists[asset]
            sig = STRATEGIES[f.strategy](prices[asset])
            r = run(prices[asset], sig, evals[f.key]["rule"], asset, p.start, p.end, f.key[2], capital=half)
            legs.append(r.equity)
            bh_legs.append(buy_and_hold(prices[asset], COSTS[asset], half, p.start, p.end))
        idx = legs[0].index.union(legs[1].index)
        port = sum(l.reindex(idx).ffill().fillna(half) for l in legs)
        port_bh = sum(l.reindex(idx).ffill().fillna(half) for l in bh_legs)
        spy_eq = buy_and_hold(spy, COSTS[BENCHMARK], INITIAL_CAPITAL, p.start, p.end)
        rows += [(f"**{p.name}**", equity_stats(port, 365) | alpha_beta(port, port_bh, 365)),
                 ("↳ 50/50 BTC + gold buy & hold", equity_stats(port_bh, 365)),
                 (f"↳ {BENCHMARK} benchmark", equity_stats(spy_eq, 252))]
        if key == "full_10y":
            corr = pd.concat([l.reindex(idx).ffill().pct_change() for l in legs], axis=1).corr().iloc[0, 1]
            plot_equity({"portfolio": (port, "strategy"), "50/50 buy & hold": (port_bh, "buy_hold"),
                         BENCHMARK: (spy_eq, "benchmark")},
                        "Portfolio of both finalists · last 10 years", out / "portfolio_10y.png")
    port_md += [fmt_table(rows), "", f"Correlation of the two strategies' daily returns: **{corr:.2f}**", "",
                "![portfolio](portfolio_10y.png)", ""]
    md += port_md

    md[lb_pos:lb_pos] = lb
    (out / "report.md").write_text("\n".join(md))
    board.drop(columns=["key"]).to_csv(out / "leaderboard.csv", index=False)
    print(f"Report written to {out / 'report.md'}")


if __name__ == "__main__":
    main()
