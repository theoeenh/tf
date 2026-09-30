"""How sure can we be that an edge is real? Bootstrap confidence ranges.

    python -m algo.confidence --variant "long + trend + blackout + ML"

A backtest gives one number (e.g. +0.15R per trade), but with a few hundred
trades that number could be luck. Resampling asks: if the same kind of
trades happened again in a different order / mix, how much would the result
move?

- Trades: draw the test window's trades with replacement, 10,000 times ->
  range of the average R, and the share of draws at or below 0R.
- Days: draw blocks of consecutive days of the equity curve (block
  bootstrap, keeps the link between trades of the same days) -> range of the
  yearly return.
"""
from __future__ import annotations

import argparse
import logging

import numpy as np
import pandas as pd

N_DRAWS = 10_000


def trade_bootstrap(r: np.ndarray, n: int = N_DRAWS, seed: int = 0) -> dict:
    """Average R of the trades: point estimate, 90% range, chance it is <= 0."""
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 10:
        return {"trades": len(r)}
    rng = np.random.default_rng(seed)
    means = r[rng.integers(0, len(r), (n, len(r)))].mean(axis=1)
    return {"trades": len(r), "avg_r": float(r.mean()), "lo": float(np.percentile(means, 5)),
            "hi": float(np.percentile(means, 95)), "p_le_0": float((means <= 0).mean())}


def day_bootstrap(equity: pd.Series, block: int = 10, n: int = 2000, seed: int = 0) -> dict:
    """Yearly return from daily equity changes, resampled in blocks of `block` days."""
    d = equity.resample("D").last().dropna().pct_change().dropna().to_numpy()
    if len(d) < 3 * block:
        return {"days": len(d)}
    rng = np.random.default_rng(seed)
    k = int(np.ceil(len(d) / block))
    starts = rng.integers(0, len(d) - block + 1, (n, k))
    idx = (starts[:, :, None] + np.arange(block)).reshape(n, -1)[:, :len(d)]
    growth = np.prod(1 + d[idx], axis=1)
    years = len(d) / 365.25
    cagr = growth ** (1 / years) - 1
    point = float(np.prod(1 + d) ** (1 / years) - 1)
    return {"days": len(d), "cagr": point, "lo": float(np.percentile(cagr, 5)),
            "hi": float(np.percentile(cagr, 95)), "p_le_0": float((cagr <= 0).mean())}


def describe(name: str, tb: dict, db: dict) -> str:
    if "avg_r" not in tb or "cagr" not in db:
        return f"{name}: too few trades or days to judge."
    return (f"{name}: {tb['trades']} trades, avg {tb['avg_r']:+.3f}R (90% range {tb['lo']:+.3f} to "
            f"{tb['hi']:+.3f}R, {tb['p_le_0']:.0%} chance the true edge is <= 0). Yearly return "
            f"{db['cagr']:+.1%} (90% range {db['lo']:+.1%} to {db['hi']:+.1%}, {db['p_le_0']:.0%} chance <= 0).")


def main() -> None:
    from . import news
    from .system import ALL_VARIANTS, OPTIONS, UNIVERSES, build_context, calibrate_risk, load_prices, run_random
    from .system import run_variant

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", default="long + trend + blackout + ML")
    ap.add_argument("--source", default="alpaca")
    ap.add_argument("--random-seeds", type=int, default=5)
    ap.add_argument("--universe", default="core", choices=["core", "wide"])
    args = ap.parse_args()
    logging.basicConfig(level=logging.WARNING)
    prices = load_prices(args.source, "1h", UNIVERSES[args.universe])
    ctx = build_context(prices, news.load_all(list(prices), alpaca_news=args.source == "alpaca"))
    idx = prices["BTC"].index
    train = (idx[0] + pd.Timedelta(days=10), idx[0] + (idx[-1] - idx[0]) * 0.6)
    test_start = train[1] + pd.Timedelta(hours=1)
    v = ALL_VARIANTS[args.variant]
    risk = calibrate_risk(prices, v["allow_short"], v["learn"], *train, news=v.get("news", False), context=ctx,
                          **{o: v.get(o, False) for o in OPTIONS})
    res = run_variant(prices, v, risk, train[0], None, ctx)
    t = res.trades_df
    t = t[t.exit_date >= test_start]
    print(describe(f"{args.variant} (test window from {test_start:%Y-%m-%d})",
                   trade_bootstrap(t.r_multiple.to_numpy()), day_bootstrap(res.equity.loc[test_start:])))
    for s in range(args.random_seeds):
        rr = run_random(prices, v["allow_short"], risk, s, train[0], None)
        tr = rr.trades_df
        tr = tr[tr.exit_date >= test_start]
        print(describe(f"  random twin, seed {s}", trade_bootstrap(tr.r_multiple.to_numpy()),
                       day_bootstrap(rr.equity.loc[test_start:])))


if __name__ == "__main__":
    main()
