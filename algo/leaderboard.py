"""Compare strategies and system versions every day.

    python -m algo.leaderboard          # writes paper/leaderboard.md and paper/race.csv

1. The race: every version of the system (ALL_VARIANTS: the rule learner,
   the upgrades, the ML learner...) is paper-traded side by side from the same
   start date as the paper account, on the same bars, each after learning from
   the same history. Ranked by return, with the random-entry twin as the bar
   to beat. A version that keeps winning the race is the candidate to trade.
2. The strategy leaderboard: every strategy on every asset, over the last 7
   and 30 days and since the start, counting the trades the learner skipped
   (followed without money) separately. It shows which strategy works now,
   and whether the learner's skipping helps.
"""
from __future__ import annotations

import json
import logging

import numpy as np
import pandas as pd

from .metrics import equity_stats
from .paper import PAPER_DIR, bars_since, complete_bars, news_context, now_utc
from .system import ALL_VARIANTS, bars_per_year, load_prices, new_learner, run_random, run_variant

log = logging.getLogger(__name__)
RACE_SEEDS = 5


def run_race(prices: dict, cfg: dict, variants: dict = ALL_VARIANTS) -> tuple[pd.DataFrame, dict]:
    """Each variant from the paper start, after pre-training on the history before it."""
    start = pd.Timestamp(cfg["start"])
    hist_start = min(df.index[0] for df in prices.values())
    rows, results = [], {}
    ctx_all = news_context(prices, {"news": True}, cfg["interval"])
    for name, v in variants.items():
        learner = new_learner(v["learn"], v.get("news", False), v.get("ml", False), v.get("sizing", False))
        if learner is not None:
            run_variant(prices, v, cfg["risk_pct"], hist_start, start - pd.Timedelta(seconds=1), ctx_all,
                        learner=learner)
        res = run_variant(prices, v, cfg["risk_pct"], start, None, ctx_all, initial_capital=cfg["capital"],
                          close_at_end=False, learner=learner)
        results[name] = res
        rows.append({"version": name} | _stats(res, cfg["capital"]))
    for short in (False, True):
        runs = [run_random(prices, short, cfg["risk_pct"], seed, start, None) for seed in range(RACE_SEEDS)]
        st = pd.DataFrame([_stats(r, cfg["capital"]) for r in runs]).mean(numeric_only=True).to_dict()
        rows.append({"version": f"random entries, {'long/short' if short else 'long only'} (avg of {RACE_SEEDS})"}
                    | st)
    return pd.DataFrame(rows).sort_values("return", ascending=False), results


def _stats(res, capital: float) -> dict:
    eq = res.equity
    st = equity_stats(eq, bars_per_year(eq.index)) if len(eq) > 2 else {}
    t = res.trades_df
    return {"return": eq.iloc[-1] / capital - 1, "max_dd": st.get("max_drawdown", np.nan),
            "trades": len(t), "win_rate": (t.pnl > 0).mean() if len(t) else np.nan,
            "avg_r": t.r_multiple.mean() if len(t) else np.nan,
            "open": len([p for p in res.open_positions if not p["shadow"]]),
            "skipped": len(res.shadow_trades)}


def strategy_board(res, now: pd.Timestamp) -> pd.DataFrame:
    """Every strategy x asset: R over the last 7 / 30 days and in total; skipped trades apart."""
    real = res.trades_df.assign(kind="taken")
    sh = pd.DataFrame([t.__dict__ for t in res.shadow_trades]).assign(kind="skipped")
    t = pd.concat([real, sh], ignore_index=True) if len(sh) else real
    if t.empty:
        return pd.DataFrame()
    rows = []
    for (strat, asset), g in t.groupby(["strategy", "asset"]):
        tk = g[g.kind == "taken"]
        row = {"strategy": strat, "asset": asset}
        for label, days in (("7d", 7), ("30d", 30), ("all", None)):
            w = tk if days is None else tk[tk.exit_date >= now - pd.Timedelta(days=days)]
            row[f"R {label}"] = w.r_multiple.sum()
        row |= {"trades": len(tk), "win %": (tk.pnl > 0).mean() if len(tk) else np.nan,
                "avg R": tk.r_multiple.mean() if len(tk) else np.nan,
                "skipped": int((g.kind == "skipped").sum()),
                "skipped avg R": g[g.kind == "skipped"].r_multiple.mean()}
        rows.append(row)
    return pd.DataFrame(rows).sort_values("R 30d", ascending=False)


def _md_table(df: pd.DataFrame, pct=(), r=()) -> list[str]:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            if isinstance(v, float) and not np.isfinite(v):
                cells.append("–")
            elif c in pct:
                cells.append(f"{v:+.2%}" if c != "win_rate" and c != "win %" else f"{v:.0%}")
            elif c in r:
                cells.append(f"{v:+.2f}")
            elif isinstance(v, float):
                cells.append(f"{v:,.0f}")
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return out


def write() -> str:
    cfg = json.loads((PAPER_DIR / "config.json").read_text())
    now = now_utc()
    prices = {a: complete_bars(df, a, cfg["interval"], now)
              for a, df in load_prices(cfg.get("source", "auto"), cfg["interval"]).items()}
    start = pd.Timestamp(cfg["start"])
    md = [f"# Leaderboard – {now:%Y-%m-%d %H:%M} UTC", "",
          f"All versions paper-traded side by side since {start} UTC ({cfg['interval']} bars), same bars, "
          f"same ${cfg['capital']:,.0f} and {cfg['risk_pct']:.2%} risk per trade. The live account trades "
          f"**{cfg['variant']}**. Early days are noise: look for a version that stays ahead for weeks, and "
          "that beats the random-entry twins.", ""]
    if bars_since(prices, start) < 2:
        md += ["No complete bar since the start yet."]
    else:
        race, results = run_race(prices, cfg)
        race.to_csv(PAPER_DIR / "race.csv", index=False)
        md += ["## The race", ""]
        md += _md_table(race, pct=("return", "max_dd", "win_rate"), r=("avg_r",)) + [""]
        live = results.get(cfg["variant"])
        board = strategy_board(live, now) if live is not None else pd.DataFrame()
        md += [f"## Strategy leaderboard ({cfg['variant']})", "",
               "Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner "
               "refused, followed without money: a negative average means skipping them was right.", ""]
        md += (_md_table(board, pct=("win %",), r=("R 7d", "R 30d", "R all", "avg R", "skipped avg R"))
               if not board.empty else ["No closed trades yet."]) + [""]
        board.to_csv(PAPER_DIR / "board.csv", index=False)
        ml = getattr(live.learner, "report", None) if live is not None else None
        if ml:
            rep = ml()
            (PAPER_DIR / "ml.json").write_text(json.dumps(rep, default=float, indent=2))
            md += ["## ML learner, out of sample", "",
                   f"Refitted {rep['fits']} times. {rep['judged']} trades judged before their outcome was known."]
            if rep.get("judged"):
                md += [f"AUC {rep['auc']:.2f} (0.50 = no better than chance). Taken: {rep['taken']} trades, "
                       f"avg {rep['taken_avg_r']:+.2f}R. Skipped: {rep['skipped']}, avg {rep['skipped_avg_r']:+.2f}R."]
            md += [""]
    out = PAPER_DIR / "leaderboard.md"
    out.write_text("\n".join(md) + "\n")
    return str(out)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(f"Leaderboard: {write()}")


if __name__ == "__main__":
    main()
