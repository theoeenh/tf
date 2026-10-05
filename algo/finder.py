"""Strategy finder, steps 1-3: locked data periods, one score card per strategy, shelf life.

    python -m algo.finder grid            # score the built-in families over a parameter grid
    python -m algo.finder loop --rounds 3 # grid of untried families, then rounds of improved children
    python -m algo.finder report          # rewrite paper/finder/report.md from the registry
    python -m algo.finder vault <id>      # the ONE vault test of a candidate that passed every gate

1. Locked periods (hourly bars, 2023 -> now):
   - search     2023-01-11 -> 2024-12-31   iterate here as much as wanted
   - validation 2025-01-01 -> 2025-06-30   out-of-sample check of each candidate
   - vault      2025-07-01 -> now          sealed: the data is not even loaded unless a candidate
                                           that passed every gate is sent there, once (logged; a
                                           second try is refused)
2. Score card (every attempt is written to the registry, so the number of tries is known):
   - edge: average move after a signal, in the trade's direction, in ATRs, over the trade's
     horizon; per month, its mean is the IC and mean / std across months the ICIR
   - trading: the strategy alone through the portfolio engine with real costs and exits
     (return, Sharpe, max drawdown, trades, average R)
   - versus random entries with the same exits and number of signals
   - deflated Sharpe: the chance the Sharpe is real after accounting for how many strategies
     were tried (Bailey & Lopez de Prado); the bar rises with every attempt
3. Shelf life (search + validation months): share of positive months, longest losing run,
   first half vs second half (decay), every market regime (up / down / flat months), breadth
   (share of assets where it works).
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import logging
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import strategies as S
from .engine import ExitRule
from .indicators import atr
from .metrics import equity_stats
from .portfolio import PortfolioConfig, Sleeve, run_portfolio
from .system import COSTS, MAX_GROSS, MAX_OPEN_RISK, UNIVERSE_WIDE, load_prices

log = logging.getLogger(__name__)
OUT = Path(__file__).resolve().parent.parent / "paper" / "finder"
SEARCH = ("2023-01-11", "2024-12-31 23:59")
VALIDATION = ("2025-01-01", "2025-06-30 23:59")
# per data set: (search, validation). Same sealed vault for both.
PERIODS = {"hourly": (SEARCH, VALIDATION),
           "daily500": (("2017-01-01", "2022-12-31 23:59"), ("2023-01-01", "2025-06-30 23:59"))}
VAULT_START = "2025-07-01"
RISK = 0.004
SEEDS = 3

FAMILIES = {
    "donchian": (S.donchian_breakout, {"n": [20, 55, 120], "trend_ma": [100, 200]}),
    "squeeze": (S.squeeze_breakout, {"n": [20], "k": [2.0], "lookback": [60, 120], "pct": [0.1, 0.2]}),
    "rsi2": (S.rsi2_reversion, {"rsi_n": [2, 3], "threshold": [5.0, 10.0], "trend_ma": [100, 200]}),
    "opening_range": (S.opening_range_breakout, {"n_open": [1, 2]}),
    "vwap": (S.vwap_reversion, {"k": [1.5, 2.0, 2.5], "trend_ma": [200]}),
}
RULES = {
    "target 2R": dict(stop_atr=2.0, rr=2.0),
    "target 2R, out in 12 bars": dict(stop_atr=1.5, rr=2.0, max_bars=12),
    "trailing 3 ATR": dict(stop_atr=2.5, rr=None, trail_atr=3.0),
    "out after 1 bar": dict(stop_atr=1.5, rr=None, max_bars=1),
    "target 1.5R, out in 6 bars": dict(stop_atr=1.0, rr=1.5, max_bars=6),
}
DAILY_RULES = {  # daily bars: holds of days to weeks
    "hold 5 days": dict(stop_atr=2.5, rr=None, max_bars=5),
    "hold 10 days": dict(stop_atr=3.0, rr=None, max_bars=10),
    "hold 20 days": dict(stop_atr=3.0, rr=None, max_bars=20),
    "hold 40 days": dict(stop_atr=4.0, rr=None, max_bars=40),
    "target 3R, out in 20 days": dict(stop_atr=2.0, rr=3.0, max_bars=20),
    "trailing 3 ATR, out in 60 days": dict(stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60),
}
ASSET_SETS = {
    "all": lambda a: True,
    "stocks": lambda a: ASSET_CLASS.get(a) == "stock",
    "etfs": lambda a: ASSET_CLASS.get(a) in ("etf", "metal"),
    "crypto": lambda a: a in S_CRYPTO,
    "stocks+etfs": lambda a: a not in S_CRYPTO,
}


@dataclass
class Candidate:
    family: str
    params: dict
    rule: dict
    short: bool = False
    trend: bool = True  # only with the daily trend (as the live system)
    assets: str = "all"  # all / stocks / etfs / crypto / stocks+etfs
    data: str = "hourly"  # hourly: the live universe, hourly bars; daily500: S&P 500, daily bars
    notes: str = ""

    @property
    def id(self) -> str:
        key = json.dumps([self.family, self.params, self.rule, self.short, self.trend]
                         + ([self.assets] if self.assets != "all" else [])
                         + ([self.data] if self.data != "hourly" else []), sort_keys=True)
        return hashlib.sha1(key.encode()).hexdigest()[:10]

    def label(self) -> str:
        p = ", ".join(f"{k}={v}" for k, v in self.params.items())
        r = ", ".join(f"{k}={v}" for k, v in self.rule.items())
        if self.data == "daily500":
            where = {"all": "S&P 500", "sp400": "S&P 400 (mid)", "sp600": "S&P 600 (small)",
                     "sp1500": "S&P 1500"}.get(self.assets, self.assets.replace("sector:", "sector "))
            return (f"{self.family}({p}) | {r}{'' if self.trend else ' | no trend filter'} | "
                    f"{where}, daily")
        return (f"{self.family}({p}) | {r}{' | long/short' if self.short else ''}"
                f"{'' if self.trend else ' | no trend filter'}{'' if self.assets == 'all' else ' | ' + self.assets}")

    def horizon(self) -> int:
        return int(self.rule.get("max_bars") or (24 if self.data == "hourly" else 10))


# ------------------------------------------------------------------ data (vault sealed)

def load(include_vault: bool = False, data: str = "hourly") -> dict[str, pd.DataFrame]:
    if data == "daily500":
        from . import wide

        prices = wide.load_daily()
    else:
        prices = load_prices("alpaca", "1h", UNIVERSE_WIDE)
    if not include_vault:  # the vault months are not even in memory
        prices = {a: df[df.index < pd.Timestamp(VAULT_START)] for a, df in prices.items()}
    return prices


def signals(c: Candidate, prices) -> dict[str, pd.Series]:
    if c.data == "daily500":
        from . import wide

        keep = wide.segment(c.assets)
    else:
        keep = ASSET_SETS[c.assets]
    prices = {a: df for a, df in prices.items() if keep(a)}
    if c.family in WIDE_FAMILIES:
        raw = WIDE_FAMILIES[c.family][0](prices, **c.params)
    elif c.family in PANEL_FAMILIES:  # cross-asset families see the whole universe at once
        raw = PANEL_FAMILIES[c.family][0](prices, **c.params)
    else:
        fn = FAMILIES[c.family][0]
        raw = {a: fn(df, **c.params) for a, df in prices.items()
               if not (c.family == "opening_range" and a in S_CRYPTO)}
    out = {}
    for a, s in raw.items():
        df = prices[a]
        s = s.reindex(df.index).fillna(0).astype(int)
        if c.trend:
            s = S.with_trend(s, S.daily_trend(df))
        if not c.short:
            s = s.clip(lower=0)
        out[a] = s
    return out


from .data import ASSET_CLASS  # noqa: E402
from .data import CRYPTO as S_CRYPTO  # noqa: E402
from .finder_families import PANEL_FAMILIES, WIDE_FAMILIES  # noqa: E402


# ------------------------------------------------------------------ 2. score card

def edge_events(sig: dict[str, pd.Series], prices, horizon: int) -> pd.DataFrame:
    """Every signal: time, asset, side and the move to `horizon` bars later from the next open, in ATRs,
    minus the asset's ordinary move over the same horizon in the same period (its drift): in a rising
    market every long signal would otherwise look good. Only the extra move counts."""
    rows = []
    for a, s in sig.items():
        df = prices[a]
        ev = s[s != 0]
        if ev.empty:
            continue
        a_atr = atr(df).to_numpy()
        o, c = df["Open"].to_numpy(), df["Close"].to_numpy()
        pos = df.index.get_indexer(ev.index)
        lo, hi = max(pos.min(), 1), min(pos.max(), len(df) - horizon - 1)
        k = np.arange(lo, hi + 1)
        move = (c[k + horizon] - o[k + 1]) / a_atr[k]
        drift = float(np.nanmean(move[np.isfinite(move)])) if len(k) else 0.0
        for p, side, t in zip(pos, ev.to_numpy(), ev.index):
            if p + horizon >= len(df) or not np.isfinite(a_atr[p]) or a_atr[p] <= 0:
                continue
            rows.append((t, a, int(side), side * ((c[p + horizon] - o[p + 1]) / a_atr[p] - drift)))
    ev = pd.DataFrame(rows, columns=["time", "asset", "side", "edge"])
    ev["edge"] = ev["edge"].clip(-10, 10)  # a few huge gaps (splits, tiny ATR at the open) must not decide the score
    return ev


def monthly_ic(events: pd.DataFrame) -> pd.Series:
    if events.empty:
        return pd.Series(dtype=float)
    return events.groupby(events["time"].dt.to_period("M"))["edge"].mean()


def backtest(c: Candidate, prices, sig, start, end, seed: int | None = None):
    rule = ExitRule(**c.rule)
    if c.data == "daily500":  # 500 stocks: only those with a signal in the window, and only the window
        a0, b0 = pd.Timestamp(start), pd.Timestamp(end)
        sig = {a: s for a, s in sig.items() if (s[(s.index >= a0) & (s.index <= b0)] != 0).any()}
        lo = a0 - pd.Timedelta(days=400)  # warm-up for the indicators the exits use
        prices = {a: prices[a][(prices[a].index >= lo) & (prices[a].index <= b0)] for a in sig}
        sig = {a: s.reindex(prices[a].index).fillna(0).astype(int) for a, s in sig.items()}
    sl = []
    rng = np.random.default_rng(seed) if seed is not None else None
    for a, s in sig.items():
        if rng is not None:  # random twin: same exits, same number of signals, random timing (and side)
            inside = (s.index >= pd.Timestamp(start)) & (s.index <= pd.Timestamp(end))
            fire = rng.random(len(s)) < (s[inside] != 0).mean()  # same rate as the signals in the window
            side = np.where(rng.random(len(s)) < 0.5, 1, -1) if c.short else 1
            s = pd.Series(np.where(fire, side, 0), s.index)
        sl.append(Sleeve(a, c.family, s, rule, c.short))
    cfg = PortfolioConfig(risk_pct=RISK, max_gross=MAX_GROSS, max_open_risk=MAX_OPEN_RISK)
    if c.data == "daily500":
        from . import wide

        costs = wide.costs(sig)
    else:
        costs = COSTS
    return run_portfolio({a: prices[a] for a in sig}, sl, costs, cfg, start, end)


def trading_stats(res) -> dict:
    eq = res.equity
    daily = eq.resample("D").last().dropna()
    r = daily.pct_change().dropna()
    t = res.trades_df
    st = equity_stats(daily, 365)
    return {"return": eq.iloc[-1] / eq.iloc[0] - 1, "sharpe": st["sharpe"], "max_dd": st["max_drawdown"],
            "trades": len(t), "avg_r": t.r_multiple.mean() if len(t) else np.nan,
            "sr_daily": r.mean() / r.std() if r.std() > 0 else 0.0, "n_days": len(r),
            "skew": float(r.skew()) if len(r) > 3 else 0.0, "kurt": float(r.kurt() + 3) if len(r) > 3 else 3.0}


def deflated_sharpe(sr: float, n_obs: int, skew: float, kurt: float, trial_srs: list[float]) -> float:
    """Probability that the true (per-day) Sharpe is above what the best of N random tries would
    reach by luck. N = number of strategies tried so far (the registry)."""
    from scipy.stats import norm

    n = max(len(trial_srs), 1)
    var = float(np.var(trial_srs)) if n > 1 else 0.0
    if n > 1 and var > 0:
        g = 0.5772156649
        sr0 = math.sqrt(var) * ((1 - g) * norm.ppf(1 - 1 / n) + g * norm.ppf(1 - 1 / (n * math.e)))
    else:
        sr0 = 0.0
    den = math.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4 * sr * sr))
    return float(norm.cdf((sr - sr0) * math.sqrt(max(n_obs - 1, 1)) / den))


# ------------------------------------------------------------------ 3. shelf life

def shelf_life(events: pd.DataFrame, prices, groups: dict | None = None) -> dict:
    """groups: asset -> group for the breadth test (S&P 500: its sector, as most stocks only get a
    signal or two; the live universe: each asset on its own)."""
    ic = monthly_ic(events)
    if len(ic) < 6:
        return {"months": len(ic)}
    pos = (ic > 0).astype(int)
    runs = pos.groupby((pos != pos.shift()).cumsum()).agg(["first", "size"])
    longest_bad = int(runs[runs["first"] == 0]["size"].max()) if (runs["first"] == 0).any() else 0
    half = len(ic) // 2
    # market regime of each month: equal-weight move of the whole universe
    closes = pd.DataFrame({a: df["Close"].resample("ME").last() for a, df in prices.items()})
    mkt = closes.pct_change(fill_method=None).mean(axis=1)
    mkt.index = mkt.index.to_period("M")
    reg = pd.cut(mkt.reindex(ic.index), [-np.inf, -0.02, 0.02, np.inf], labels=["down", "flat", "up"])
    by_reg = ic.groupby(reg, observed=False).mean()
    key = events["asset"].map(groups) if groups else events["asset"]
    if groups is None:  # specialised in one group: breadth over its stocks with a few signals each
        n = events.groupby("asset")["edge"].transform("size")
        if (events[n >= 3]["asset"].nunique()) >= 5:
            events, key = events[n >= 3], events[n >= 3]["asset"]
    by_asset = events.groupby(key)["edge"].mean()
    count = events.groupby(key)["edge"].size()
    return {"months": len(ic), "pos_months": float(pos.mean()), "longest_bad_run": longest_bad,
            "ic_first_half": float(ic.iloc[:half].mean()), "ic_second_half": float(ic.iloc[half:].mean()),
            "regimes_positive": int((by_reg > 0).sum()), "regimes_seen": int(by_reg.notna().sum()),
            "breadth": float((by_asset > 0).mean()),
            # edge per group (sector, or asset), for the loop: where does it work?
            "by_group": json.dumps({str(k): [round(float(v), 4), int(count[k])] for k, v in by_asset.items()})}


# ------------------------------------------------------------------ gates and registry

GATES = {  # a candidate must pass all of them to be offered to the vault
    "search: at least 100 signals": lambda s: s["s_events"] >= 100,
    "search: positive edge (IC)": lambda s: s["s_ic"] > 0,
    "search: ICIR >= 0.2 (stable month to month)": lambda s: s["s_icir"] >= 0.2,
    "search: beats random entries (avg R)": lambda s: s["s_avg_r"] > s["s_rand_avg_r"],
    "search: deflated Sharpe >= 0.90": lambda s: s["s_dsr"] >= 0.90,
    "validation: positive edge": lambda s: s["v_ic"] > 0,
    "validation: beats random entries": lambda s: s["v_avg_r"] > s["v_rand_avg_r"],
    "validation: makes money after costs": lambda s: s["v_return"] > 0,
    "shelf life: positive in >= 55% of months": lambda s: s["pos_months"] >= 0.55,
    "shelf life: no decay (2nd half >= half of 1st)": lambda s: s["ic_second_half"] >= 0.5 * s["ic_first_half"],
    "shelf life: positive in every market regime seen": lambda s: s["regimes_positive"] == s["regimes_seen"],
    "shelf life: works on >= 55% of assets (S&P 500: of sectors)": lambda s: s["breadth"] >= 0.55,
    "decay: edge still >= half its peak at the exit, peak after the first bar":
        lambda s: s["s_exit_vs_peak"] >= 0.5 and s["s_peak_h"] > 1,
    "robust: parameter neighbours keep >= half the edge (2+ tested)": lambda s: s["plateau"] >= 0.5,
}


def registry() -> pd.DataFrame:
    path = OUT / "registry.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def evaluate(c: Candidate, prices) -> dict:
    sig = signals(c, prices)
    row = {"id": c.id, "label": c.label(), "family": c.family, "candidate": json.dumps(asdict(c))}
    search, validation = PERIODS[c.data]
    for w, (a, b) in (("s", search), ("v", validation)):
        win = {k: v[(v.index >= pd.Timestamp(a)) & (v.index <= pd.Timestamp(b))] for k, v in sig.items()}
        ev = edge_events(win, prices, c.horizon())
        ic = monthly_ic(ev)
        row |= {f"{w}_events": len(ev), f"{w}_ic": float(ic.mean()) if len(ic) else np.nan,
                f"{w}_icir": float(ic.mean() / ic.std()) if len(ic) > 2 and ic.std() > 0 else np.nan}
        st = trading_stats(backtest(c, prices, sig, a, b))
        row |= {f"{w}_{k}": v for k, v in st.items()}
        rnd = [trading_stats(backtest(c, prices, sig, a, b, seed=sd)) for sd in range(SEEDS)]
        row |= {f"{w}_rand_avg_r": float(np.nanmean([r["avg_r"] for r in rnd])),
                f"{w}_rand_return": float(np.mean([r["return"] for r in rnd]))}
    s_win = {k: v[(v.index >= pd.Timestamp(search[0])) & (v.index <= pd.Timestamp(search[1]))] for k, v in sig.items()}
    row |= edge_curve(c, s_win, prices)
    both = {k: v[(v.index >= pd.Timestamp(search[0])) & (v.index <= pd.Timestamp(validation[1]))]
            for k, v in sig.items()}
    groups = None
    if c.data == "daily500" and not c.assets.startswith("sector:"):
        from . import wide

        groups = wide.sectors()
    row |= shelf_life(edge_events(both, prices, c.horizon()), prices, groups)
    return row


HORIZONS = {"daily500": [1, 2, 5, 10, 20, 40, 60], "hourly": [1, 2, 3, 6, 12, 24, 48]}


def edge_curve(c: Candidate, sig: dict, prices) -> dict:
    """How long the edge lasts (search window): the average extra move after a signal at several
    horizons. Where it peaks is how long the trade should be held; an edge that is mostly gone by
    the strategy's exit, or peaks on the first bar, is not tradeable after costs."""
    hs = sorted(set(HORIZONS[c.data]) | {c.horizon()})
    curve = {}
    for h in hs:
        ev = edge_events(sig, prices, h)
        curve[h] = float(ev["edge"].mean()) if len(ev) else np.nan
    vals = pd.Series(curve).dropna()
    if vals.empty:
        return {"s_edge_curve": json.dumps(curve)}
    peak_h = int(vals.idxmax())
    peak = float(vals.max())
    at_exit = curve.get(c.horizon(), np.nan)
    return {"s_edge_curve": json.dumps({str(k): round(v, 4) for k, v in curve.items()}), "s_peak_h": peak_h,
            "s_peak_edge": peak, "s_exit_vs_peak": float(at_exit / peak) if peak > 0 else np.nan}


def _neighbour_key(c: dict) -> str:
    return json.dumps([c["family"], c["rule"], c.get("short"), c.get("trend"), c.get("assets", "all"),
                       c.get("data", "hourly"), sorted(c["params"])], sort_keys=True)


def plateau(rows: pd.DataFrame) -> pd.Series:
    """Robustness: the average search edge of the tested parameter neighbours (one parameter moved
    by up to 60%) relative to the strategy's own. A real edge works across a range of reasonable
    parameters; one magic number does not. NaN when fewer than 2 neighbours were tested."""
    cands = rows["candidate"].map(json.loads)
    groups: dict[str, list[int]] = {}
    for i, c in cands.items():
        groups.setdefault(_neighbour_key(c), []).append(i)
    out = pd.Series(np.nan, rows.index)
    for idx in groups.values():
        for i in idx:
            p = cands[i]["params"]
            nb = []
            for j in idx:
                q = cands[j]["params"]
                diff = [k for k in p if q.get(k) != p[k]]
                if len(diff) != 1 or isinstance(p[diff[0]], bool) or not isinstance(p[diff[0]], (int, float)):
                    continue
                k = diff[0]
                if p[k] and 0.6 <= q[k] / p[k] <= 1.67:
                    nb.append(rows.at[j, "s_ic"])
            own = rows.at[i, "s_ic"]
            if len(nb) >= 2 and own > 0:
                out[i] = float(np.nanmean(nb) / own)
    return out


def score(rows: pd.DataFrame) -> pd.DataFrame:
    """Deflated Sharpe with N = every attempt so far, then the gates."""
    rows = rows.copy().reset_index(drop=True)
    rows["plateau"] = plateau(rows)
    srs = rows["s_sr_daily"].fillna(0).tolist()
    rows["s_dsr"] = [deflated_sharpe(r.s_sr_daily, int(r.s_n_days), r.s_skew, r.s_kurt, srs)
                     for r in rows.itertuples()]
    passed, failed = [], []
    for _, r in rows.iterrows():
        f = [g for g, ok in GATES.items() if not _safe(ok, r)]
        failed.append("; ".join(f))
        passed.append(len(GATES) - len(f))
    rows["gates_passed"], rows["failed"] = passed, failed
    return rows


def _safe(fn, r) -> bool:
    try:
        return bool(fn(r))
    except (KeyError, TypeError, ValueError):
        return False


def run(candidates: list[Candidate]) -> pd.DataFrame:
    OUT.mkdir(parents=True, exist_ok=True)
    data: dict[str, dict] = {}  # each data set loaded once, when first needed
    reg = registry()
    done = set(reg["id"]) if len(reg) else set()
    new = []
    for i, c in enumerate(candidates, 1):
        if c.id in done:
            continue
        log.info("[%d/%d] %s", i, len(candidates), c.label())
        try:
            if c.data not in data:
                data[c.data] = load(data=c.data)
            new.append(evaluate(c, data[c.data]))
        except (OSError, KeyError, ValueError) as exc:  # e.g. research data missing tonight: skip, not counted
            log.warning("skipped %s: %r", c.label(), exc)
            continue
        reg = pd.concat([reg, pd.DataFrame(new[-1:])], ignore_index=True)
        reg.to_csv(OUT / "registry.csv", index=False)  # saved after every attempt
    reg = score(reg)
    reg.to_csv(OUT / "registry.csv", index=False)
    report(reg)
    return reg


def grid(families: dict | None = None) -> list[Candidate]:
    out = []
    for fam, (_, space) in (families or FAMILIES | PANEL_FAMILIES | WIDE_FAMILIES).items():
        wide_ = fam in WIDE_FAMILIES
        keys = list(space)
        for vals in itertools.product(*(space[k] for k in keys)):
            for rule in (DAILY_RULES if wide_ else RULES).values():
                for seg in (("all", "sp400", "sp600") if wide_ else ("all",)):  # S&P 500, mid, small companies
                    out.append(Candidate(fam, dict(zip(keys, vals)), dict(rule), assets=seg,
                                         data="daily500" if wide_ else "hourly"))
    return out


# ------------------------------------------------------------------ 4-5. the loop: read why it fails, try a better version

SEARCH_GATES = [g for g in GATES if g.startswith("search:")]
LONGER = {"n", "lookback", "trend_ma", "rsi_n"}  # parameters that make a strategy slower when raised


def fitness(r) -> tuple:
    """Ranking for picking parents: search gates and search ICIR only. Validation and the shelf-life
    months (which include validation) are never used to rank, only to gate, or they would leak."""
    return (sum(_safe(GATES[g], r) for g in SEARCH_GATES), np.nan_to_num(r["s_icir"], nan=-9))


def _neighbours(c: Candidate, keys=None) -> list[dict]:
    out = []
    for k, v in c.params.items():
        if keys is not None and k not in keys or isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        for f in (0.7, 1.4):
            nv = max(1, int(round(v * f))) if isinstance(v, int) else round(v * f, 2)
            if nv != v:
                out.append(c.params | {k: nv})
    return out


def mutate(c: Candidate, failed: str, row: dict | None = None) -> list[tuple[Candidate, str]]:
    """Children of a candidate, the ones its failures point to first."""
    kids: list[tuple[Candidate, str]] = []

    def add(why, **change):
        kids.append((Candidate(**(asdict(c) | change | {"notes": f"from {c.id}: {why}"})), why))

    rules = DAILY_RULES if c.data == "daily500" else RULES
    peak_h = row.get("s_peak_h") if row else None
    if peak_h is not None and np.isfinite(peak_h) and peak_h > 1 and not (c.horizon() / 1.5 <= peak_h <= c.horizon() * 1.5):
        # the edge peaks well before / after the exit: hold for as long as it lasts
        add(f"edge peaks at {int(peak_h)} bars, exit at {c.horizon()} -> hold {int(peak_h)}",
            rule=c.rule | {"max_bars": int(peak_h)})
    if c.data == "daily500" and ("assets" in failed or "regime" in failed):
        # specialise: the sectors where it worked (enough signals there to judge), then company size
        groups = json.loads(row["by_group"]) if row and isinstance(row.get("by_group"), str) else {}
        if not c.assets.startswith("sector:"):
            good = sorted(((v[0], g) for g, v in groups.items() if v[0] > 0 and v[1] >= 30), reverse=True)
            for _, g in good[:4]:
                add(f"works only in some sectors -> only {g}", assets=f"sector:{g}")
        if c.assets == "all":
            for seg in ("sp400", "sp600", "sp1500"):
                add(f"try other company sizes -> {seg}", assets=seg)
    if "assets" in failed and c.data == "hourly":  # works on some assets only: try it where it might belong
        for a in ASSET_SETS:
            if a != c.assets:
                add(f"breadth failed -> only {a}", assets=a)
    if "random" in failed or "costs" in failed:  # entries no better than chance with these exits
        for name, rule in rules.items():
            if rule != c.rule:
                add(f"no better than random -> exit '{name}'", rule=dict(rule))
    if "decay" in failed or "ICIR" in failed:  # unstable or fading: slower versions
        for p in _neighbours(c, LONGER):
            if any(p[k] > c.params[k] for k in p if k in LONGER):
                add("unstable / decaying -> slower", params=p)
    if "regime" in failed:
        add("fails in some regime -> " + ("no trend filter" if c.trend else "with trend filter"), trend=not c.trend)
    for p in _neighbours(c):
        add("parameter neighbour", params=p)
    return kids


MAX_ROUNDS = 5  # refinement rounds per idea: more is just slower overfitting
SURVIVE_ICIR = 0.2  # search ICIR a campaign's best version needs to stay alive (the ICIR gate)


def lineage(reg: pd.DataFrame) -> pd.DataFrame:
    """Each strategy's campaign (the original idea it descends from) and its round (0 = the idea,
    1 = a first improvement, ...), from the 'from <parent>' notes."""
    notes = reg["candidate"].map(lambda x: json.loads(x).get("notes", ""))
    parent = {i: (n[5:15] if n.startswith("from ") else None) for i, n in zip(reg["id"], notes)}
    root, depth = {}, {}
    for i in reg["id"]:
        p, d, seen = i, 0, set()
        while parent.get(p) and parent[p] in parent and p not in seen:
            seen.add(p)
            p, d = parent[p], d + 1
        root[i], depth[i] = p, d
    return pd.DataFrame({"root": reg["id"].map(root), "round": reg["id"].map(depth)}, index=reg.index)


def campaigns(reg: pd.DataFrame) -> pd.DataFrame:
    """One row per campaign: its best version so far (search data only), rounds used, and status."""
    reg = reg.join(lineage(reg))
    reg["fit"] = [fitness(r) for r in reg.to_dict("records")]
    rows = []
    for root, g in reg.groupby("root"):
        best = g.loc[max(g.index, key=lambda i: g.at[i, "fit"])]
        alive = np.nan_to_num(best["s_icir"], nan=-9) >= SURVIVE_ICIR
        status = ("done: all gates" if best["gates_passed"] == len(GATES) else
                  "stopped: ICIR below the bar" if not alive else
                  f"finished: {MAX_ROUNDS} rounds" if g["round"].max() >= MAX_ROUNDS else "improving")
        rows.append({"root": root, "best": best["id"], "label": best["label"], "rounds": int(g["round"].max()),
                     "tried": len(g), "best_gates": int(best["gates_passed"]), "best_icir": best["s_icir"],
                     "root_gates": int(g.loc[g["id"] == root, "gates_passed"].iloc[0]) if (g["id"] == root).any() else np.nan,
                     "fit": best["fit"], "status": status,
                     "path": [int(g[g["round"] <= k]["gates_passed"].max()) for k in range(int(g["round"].max()) + 1)]})
    return pd.DataFrame(rows).sort_values("fit", ascending=False)


def backfill() -> None:
    """Edge-decay columns for strategies scored before they existed (signals only, no backtest)."""
    reg = registry()
    if reg.empty:
        return
    if "s_peak_h" not in reg:
        reg["s_peak_h"] = np.nan
    todo = reg.index[reg["s_peak_h"].isna() & reg.get("s_edge_curve", pd.Series(np.nan, reg.index)).isna()]
    data: dict[str, dict] = {}
    for n, i in enumerate(todo, 1):
        c = Candidate(**json.loads(reg.at[i, "candidate"]))
        try:
            if c.data not in data:
                data[c.data] = load(data=c.data)
            prices = data[c.data]
            a, b = PERIODS[c.data][0]
            win = {k: v[(v.index >= pd.Timestamp(a)) & (v.index <= pd.Timestamp(b))]
                   for k, v in signals(c, prices).items()}
            for k, v in edge_curve(c, win, prices).items():
                reg.at[i, k] = v
        except (OSError, KeyError, ValueError) as exc:
            log.warning("no edge curve for %s: %r", c.label(), exc)
        if n % 50 == 0:
            log.info("edge curves %d/%d", n, len(todo))
            reg.to_csv(OUT / "registry.csv", index=False)
    reg.to_csv(OUT / "registry.csv", index=False)


def loop(rounds: int = 3, parents: int = 12, per_round: int = 48) -> pd.DataFrame:
    """Campaigns: every round, the best version of each surviving idea (search ICIR >= the bar, at
    most MAX_ROUNDS rounds deep) gets improved versions aimed at why it fails; the best version of a
    campaign stays its parent until a child beats it. Ideas below the bar are dropped, so the pool
    gets smaller and stronger. New ideas (families, exits) enter through the grid."""
    backfill()
    run(grid())  # any family or exit not tried yet goes first (already tried ones are skipped)
    for rnd in range(1, rounds + 1):
        reg = score(registry())
        done = set(reg["id"])
        rows = {r["id"]: r for r in reg.to_dict("records")}
        depth = dict(zip(reg["id"], lineage(reg)["round"]))
        todo: dict[str, list] = {}
        for camp in campaigns(reg).itertuples():
            if camp.status != "improving":
                continue
            best = rows[camp.best]
            if depth[best["id"]] >= MAX_ROUNDS:
                continue
            c = Candidate(**json.loads(best["candidate"]))
            all_kids = [(k, w) for k, w in mutate(c, best["failed"] if isinstance(best["failed"], str) else "", best)
                        if k.id not in done]
            aimed = [k for k, w in all_kids if w != "parameter neighbour"]
            near = [k for k, w in all_kids if w == "parameter neighbour"]  # also needed for the robustness gate
            kids = [k for pair in itertools.zip_longest(aimed, near) for k in pair if k]
            if kids:
                todo[camp.root] = kids
            if len(todo) == parents:
                break
        picked = [k for grp in itertools.zip_longest(*todo.values()) for k in grp if k][:per_round]
        if not picked:
            log.info("round %d: no campaign left to improve (new ideas needed)", rnd)
            break
        log.info("round %d: %d improved versions of %d campaigns", rnd, len(picked), len(todo))
        reg = run(picked)
    return reg


# ------------------------------------------------------------------ vault (once per candidate)

def vault(cid: str) -> dict:
    reg = score(registry())
    row = reg[reg["id"] == cid]
    if row.empty:
        raise SystemExit(f"{cid} is not in the registry")
    if row.iloc[0]["gates_passed"] < len(GATES):
        raise SystemExit(f"{cid} failed gates ({row.iloc[0]['failed']}): it does not go to the vault")
    log_path = OUT / "vault_log.json"
    used = json.loads(log_path.read_text()) if log_path.exists() else {}
    if cid in used:
        raise SystemExit(f"{cid} already had its vault test on {used[cid]['date']}: {used[cid]['result']}")
    c = Candidate(**json.loads(row.iloc[0]["candidate"]))
    prices = load(include_vault=True, data=c.data)
    sig = signals(c, prices)
    end = max(df.index[-1] for df in prices.values())
    st = trading_stats(backtest(c, prices, sig, VAULT_START, end))
    rnd = [trading_stats(backtest(c, prices, sig, VAULT_START, end, seed=s)) for s in range(SEEDS)]
    win = {k: v[v.index >= pd.Timestamp(VAULT_START)] for k, v in sig.items()}
    ic = monthly_ic(edge_events(win, prices, c.horizon()))
    icir = float(ic.mean() / ic.std()) if len(ic) > 2 and ic.std() > 0 else np.nan
    s_icir = float(row.iloc[0]["s_icir"])
    # an overfit strategy keeps some edge but loses its consistency: the ICIR must hold at least half
    ok = (st["return"] > 0 and st["avg_r"] > np.nanmean([r["avg_r"] for r in rnd]) and ic.mean() > 0
          and np.nan_to_num(icir, nan=-9) >= 0.5 * s_icir)
    used[cid] = {"date": str(pd.Timestamp.now().date()), "label": c.label(), "result": "PASS" if ok else "FAIL",
                 "return": st["return"], "avg_r": st["avg_r"], "ic": float(ic.mean()), "icir": icir,
                 "search_icir": s_icir}
    log_path.write_text(json.dumps(used, indent=1, default=float))
    return used[cid]


def merge(other: str) -> int:
    """Union of this registry and another copy (e.g. the remote one): every attempt is kept once,
    whoever ran it (the nightly workflow and a local run can both add rows the same day)."""
    mine, theirs = registry(), pd.read_csv(other) if Path(other).exists() else pd.DataFrame()
    both = pd.concat([mine, theirs[~theirs["id"].isin(mine["id"])]] if len(theirs) else [mine], ignore_index=True)
    both.to_csv(OUT / "registry.csv", index=False)
    return len(both) - len(mine)


def promote() -> list[dict]:
    """Every strategy that passed all the gates takes its one vault test (the user's standing go,
    2026-10-05); one that passes it starts forward paper trading (algo.forward). Phone alerts both."""
    from . import forward, notify

    reg = score(registry())
    used = json.loads((OUT / "vault_log.json").read_text()) if (OUT / "vault_log.json").exists() else {}
    out = []
    for r in reg[reg["gates_passed"] == len(GATES)].itertuples():
        if r.id in used:
            continue
        res = vault(r.id)
        out.append(res | {"id": r.id})
        msg = (f"{r.label}: vault (data from {VAULT_START}, never seen) return {res['return']:+.1%}, "
               f"avg {res['avg_r']:+.2f}R, ICIR {res['icir']:+.2f} vs {res['search_icir']:+.2f} in the search.")
        if res["result"] == "PASS":
            forward.start(r.id)
            notify.send("finder: a strategy passed the vault, paper trading starts", msg, "tada", "high")
        else:
            notify.send("finder: a strategy failed its vault test", msg, "x", "default")
    return out


# ------------------------------------------------------------------ report

def report(reg: pd.DataFrame) -> Path:
    n = len(reg)
    top = reg.sort_values(["gates_passed", "s_icir"], ascending=False).head(25)
    md = [f"# Strategy finder – {pd.Timestamp.now():%Y-%m-%d}", "",
          f"**{n} strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). "
          f"Hourly (live universe): search {SEARCH[0]} → {SEARCH[1][:10]}, validation {VALIDATION[0]} → "
          f"{VALIDATION[1][:10]}. S&P 500 daily: search {PERIODS['daily500'][0][0]} → {PERIODS['daily500'][0][1][:10]}, "
          f"validation {PERIODS['daily500'][1][0]} → {PERIODS['daily500'][1][1][:10]}. Both: "
          f"vault from {VAULT_START} (sealed). {len(GATES)} gates; only a candidate passing all of them may "
          "take its one vault test.", "",
          "| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | "
          "return v | DSR | months + | regimes + | breadth | first failed gate |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in top.iterrows():
        md.append(f"| {r.gates_passed}/{len(GATES)} | `{r.id}` {r.label.replace('|', '·')} | {r.s_ic:+.3f} | {r.s_icir:+.2f} | "
                  f"{r.v_ic:+.3f} | {r.s_avg_r:+.2f} / {r.s_rand_avg_r:+.2f} | {r.v_avg_r:+.2f} / {r.v_rand_avg_r:+.2f} | "
                  f"{r.v_return:+.1%} | {r.s_dsr:.2f} | {r.get('pos_months', np.nan):.0%} | "
                  f"{int(r.get('regimes_positive', 0))}/{int(r.get('regimes_seen', 0))} | {r.get('breadth', np.nan):.0%} | "
                  f"{(r.failed or 'none – vault candidate').split(';')[0]} |")
    camp = campaigns(reg)
    alive = camp[camp["status"] == "improving"]
    md += ["", f"## Campaigns: each idea refined round by round (max {MAX_ROUNDS} rounds)", "",
           f"{len(camp)} ideas tried; **{len(alive)} still improving** (search ICIR >= {SURVIVE_ICIR}), "
           f"{int((camp['status'] == 'stopped: ICIR below the bar').sum())} dropped below the bar, "
           f"{int(camp['status'].str.startswith('finished').sum())} finished their {MAX_ROUNDS} rounds.", "",
           "| idea → best version so far | rounds | tried | gates by round | ICIR | status |", "|---|---|---|---|---|---|"]
    for r in camp[camp["status"] != "stopped: ICIR below the bar"].head(15).itertuples():
        md.append(f"| `{r.best}` {r.label.replace('|', '·')} | {r.rounds} | {r.tried} | "
                  f"{' → '.join(map(str, r.path))} | {r.best_icir:+.2f} | {r.status} |")
    best = reg.sort_values(["gates_passed", "s_icir"], ascending=False).groupby("family").head(1)
    md += ["", "## Best of each family", "", "| family | tried | best gates | its ICIR (search) | strategy |", "|---|---|---|---|---|"]
    md += [f"| {r.family} | {int((reg['family'] == r.family).sum())} | {r.gates_passed}/{len(GATES)} | {r.s_icir:+.2f} | "
           f"`{r.id}` {r.label.replace('|', '·')} |" for _, r in best.iterrows()]
    notes = reg["candidate"].map(lambda x: json.loads(x).get("notes", "") if isinstance(x, str) else "")
    kids = reg[notes.str.startswith("from ")]
    if len(kids):
        md += ["", f"## The loop: {len(kids)} children tried (improved versions aimed at a parent's failures)", ""]
        why = notes[notes.str.startswith("from ")].str.split(": ", n=1).str[1].str.split(" -> ").str[0]
        for w, g in kids.groupby(why.values):
            md.append(f"- {w}: {len(g)} tried, best {int(g['gates_passed'].max())}/{len(GATES)} gates")
    fails = pd.Series([f for x in reg["failed"].fillna("") for f in x.split("; ") if f]).value_counts()
    md += ["", "## Why strategies fail (all attempts)", ""] + [f"- {k}: {v} of {n}" for k, v in fails.items()]
    log_path = OUT / "vault_log.json"
    if log_path.exists():
        md += ["", "## Vault tests (one per strategy, final)", ""]
        md += [f"- `{k}` {v['label']}: **{v['result']}** (return {v['return']:+.1%}, avg R {v['avg_r']:+.2f}, "
               f"IC {v['ic']:+.3f}, ICIR {v.get('icir', float('nan')):+.2f} vs {v.get('search_icir', float('nan')):+.2f} "
               f"in the search) on {v['date']}" for k, v in json.loads(log_path.read_text()).items()]
    path = OUT / "report.md"
    path.write_text("\n".join(md) + "\n")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("grid")
    sub.add_parser("report")
    lp = sub.add_parser("loop")
    lp.add_argument("--rounds", type=int, default=3)
    lp.add_argument("--per-round", type=int, default=48)
    sub.add_parser("promote")
    mg = sub.add_parser("merge")
    mg.add_argument("other")
    v = sub.add_parser("vault")
    v.add_argument("id")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.cmd == "grid":
        reg = run(grid())
        print(f"{len(reg)} strategies in the registry; report: {OUT / 'report.md'}")
    elif args.cmd == "loop":
        reg = loop(args.rounds, per_round=args.per_round)
        print(f"{len(reg)} strategies in the registry; report: {OUT / 'report.md'}")
    elif args.cmd == "merge":
        print(f"{merge(args.other)} rows added from {args.other}")
    elif args.cmd == "promote":
        print(promote() or "no new strategy passed every gate")
    elif args.cmd == "report":
        print(report(score(registry())))
    else:
        print(vault(args.id))


if __name__ == "__main__":
    main()
