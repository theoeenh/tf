"""The finder's luck check: is a strategy's Sharpe more than the best of all the tries would reach by
chance alone?

Until 2026-11-12 the check (deflated Sharpe, Bailey & Lopez de Prado) put the bar at the best score
expected from N INDEPENDENT tries with N = every strategy ever tried. Two things were wrong with it:

- the tries are not independent. Thousands of them are the same idea with another exit, parameter or
  sector, and move together week after week. Counting each as a fresh throw of the dice puts the bar
  where no strategy of this kind can reach it, and every new idea tested pushes it higher;
- it measured the raw Sharpe. A strategy that only buys stocks earns something in a rising market
  with no skill at all, so being invested was counted as skill.

Now, with the same formula and the same pass mark (0.90):

1. each try is judged on the part of its returns its own universe does not explain: its daily
   returns minus beta times the equal-weight return of the stocks it may trade (hedged()). Weekly sums
   of that series are kept for every try (paper/finder/returns/);
2. the bar is MEASURED, not assumed: history is replayed many times with every try stripped of its
   average (no skill anywhere) but the weeks kept together across tries, so tries that move together
   still move together. The best t-statistic of each replay is what luck alone hands the luckiest try;
   its average is the bar (null_max()). Every try still counts, and a new one can only raise the bar,
   but a near-copy of an old try raises it by almost nothing;
3. deflated Sharpe = the chance the strategy's true Sharpe is above that bar (deflated()).

effective_n() translates the bar into "as many independent tries", for the report only.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
import pandas as pd

WEEK = "W-FRI"
REPLAYS = 1000
BLOCK = 4  # weeks: average length of the blocks of history a replay is made of
SEED = 20261112
_EULER = 0.5772156649
TINY = 1e-9  # a weekly spread below this is rounding, not a strategy that traded


# ------------------------------------------------------------------ one try's returns

def hedged(equity: pd.Series, bench: pd.Series) -> tuple[pd.Series, float]:
    """(weekly sums of the daily returns the benchmark does not explain, beta). equity: the strategy's
    account value, one point a day; bench: daily returns of the stocks it may trade, equal weight."""
    r = equity.pct_change().dropna()
    if r.empty:
        return pd.Series(dtype=float), 0.0
    m = bench.reindex(r.index).fillna(0.0)
    var = float(m.var()) if len(m) > 1 else 0.0
    beta = float(r.cov(m) / var) if len(r) >= 30 and var > 0 else 0.0
    return (r - beta * m).resample(WEEK).sum(), beta


def stats(x: np.ndarray) -> dict:
    """t-statistic, per-week Sharpe, skew and kurtosis of each column (one try per column)."""
    x = np.asarray(x, float)
    n = len(x)
    mu, sd = x.mean(axis=0), x.std(axis=0, ddof=1)
    ok = sd > TINY
    z = np.where(ok, (x - mu) / np.where(ok, x.std(axis=0), 1.0), 0.0)
    sr = np.where(ok, mu / np.where(ok, sd, 1.0), 0.0)
    return {"n": n, "sr": sr, "t": sr * math.sqrt(n), "skew": (z ** 3).mean(axis=0),
            "kurt": np.where(ok, (z ** 4).mean(axis=0), 3.0)}


# ------------------------------------------------------------------ what luck alone gives the best try

def _blocks(n: int, rng: np.random.Generator) -> np.ndarray:
    """Row numbers of one replay: blocks of consecutive weeks starting at random places (stationary
    bootstrap, average block BLOCK weeks), so a few weeks of momentum in the returns stay together."""
    jump = rng.random(n) < 1.0 / BLOCK
    jump[0] = True
    start = rng.integers(0, n, n)
    idx = np.empty(n, int)
    for i in range(n):
        idx[i] = start[i] if jump[i] else (idx[i - 1] + 1) % n
    return idx


def null_max(mats: list[np.ndarray], replays: int = REPLAYS, seed: int = SEED) -> np.ndarray:
    """The best t-statistic among all the tries in each replay of a world where no try has any skill.
    mats: one (weeks x tries) matrix per data set. The tries of a data set are replayed together (same
    weeks for all, so their overlap is kept); data sets cover different years and are replayed apart."""
    rng = np.random.default_rng(seed)
    out = np.full(replays, -np.inf)
    for x in mats:
        x = np.asarray(x, np.float32)
        x = x - x.mean(axis=0)  # no skill: every try's average is zero
        x = x[:, x.std(axis=0) > TINY]  # a try that never traded cannot be the luckiest
        n = len(x)
        if x.shape[1] == 0 or n < 3:
            continue
        for b in range(replays):
            s = x[_blocks(n, rng)]
            sd = s.std(axis=0, ddof=1)
            t = np.where(sd > TINY, s.mean(axis=0) / np.where(sd > TINY, sd, 1.0), 0.0) * math.sqrt(n)
            out[b] = max(out[b], float(t.max()))
    return np.where(np.isfinite(out), out, 0.0)


def expected_max(n: float) -> float:
    """Best of n independent standard normal draws, on average (the formula the old check used)."""
    from scipy.stats import norm

    if n <= 1:
        return 0.0
    return float((1 - _EULER) * norm.ppf(1 - 1 / n) + _EULER * norm.ppf(1 - 1 / (n * math.e)))


def effective_n(bar: float) -> float:
    """How many INDEPENDENT tries would put the bar at the same height."""
    if bar <= 0:
        return 1.0
    lo, hi = 0.0, 16.0  # log of n
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if expected_max(math.exp(mid)) < bar else (lo, mid)
    return math.exp((lo + hi) / 2)


def deflated(sr: float, n: int, skew: float, kurt: float, bar_t: float) -> float:
    """Chance that the true Sharpe is above the luck bar. sr: per-week Sharpe of the try over n weeks,
    bar_t: the bar as a t-statistic (the average of null_max)."""
    from scipy.stats import norm

    sr0 = bar_t / math.sqrt(n)
    den = math.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4 * sr * sr))
    return float(norm.cdf((sr - sr0) * math.sqrt(max(n - 1, 1)) / den))


# ------------------------------------------------------------------ the tries' weekly returns, on disk

def save(folder: Path, dataset: str, stamp: str, weekly: dict[str, pd.Series]) -> Path | None:
    """One small file per run: the weekly hedged returns of the tries it scored (never rewritten by a
    later run, so git stores each try once)."""
    if not weekly:
        return None
    folder.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(weekly).sort_index().fillna(0.0)
    path = folder / f"{dataset}-{stamp}.npz"
    np.savez_compressed(path, ids=np.array(df.columns, dtype=str),
                        weeks=df.index.values.astype("datetime64[D]"), r=df.to_numpy(np.float16))  # 3 digits: enough
    return path


def load(folder: Path, dataset: str) -> pd.DataFrame:
    """weeks x tries for one data set (a try saved twice: the latest file wins)."""
    parts = []
    for p in sorted(folder.glob(f"{dataset}-*.npz")):
        z = np.load(p, allow_pickle=False)
        parts.append(pd.DataFrame(z["r"].astype(np.float32), index=pd.DatetimeIndex(z["weeks"]), columns=z["ids"]))
    if not parts:
        return pd.DataFrame()
    df = pd.concat(parts, axis=1)
    return df.loc[:, ~df.columns.duplicated(keep="last")].sort_index().fillna(0.0)


def key(mats: list[np.ndarray], ids: list[str]) -> str:
    h = hashlib.sha1(",".join(ids).encode())
    for x in mats:
        h.update(np.ascontiguousarray(x, np.float32).tobytes())
    return h.hexdigest()[:16]
