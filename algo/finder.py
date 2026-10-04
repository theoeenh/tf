"""Strategy finder, steps 1-3: locked data periods, one score card per strategy, shelf life.

    python -m algo.finder grid            # score the built-in families over a parameter grid
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
}


@dataclass
class Candidate:
    family: str
    params: dict
    rule: dict
    short: bool = False
    trend: bool = True  # only with the daily trend (as the live system)
    notes: str = ""

    @property
    def id(self) -> str:
        key = json.dumps([self.family, self.params, self.rule, self.short, self.trend], sort_keys=True)
        return hashlib.sha1(key.encode()).hexdigest()[:10]

    def label(self) -> str:
        p = ", ".join(f"{k}={v}" for k, v in self.params.items())
        r = ", ".join(f"{k}={v}" for k, v in self.rule.items())
        return f"{self.family}({p}) | {r}{' | long/short' if self.short else ''}{'' if self.trend else ' | no trend filter'}"

    def horizon(self) -> int:
        return int(self.rule.get("max_bars") or 24)


# ------------------------------------------------------------------ data (vault sealed)

def load(include_vault: bool = False) -> dict[str, pd.DataFrame]:
    prices = load_prices("alpaca", "1h", UNIVERSE_WIDE)
    if not include_vault:  # the vault months are not even in memory
        prices = {a: df[df.index < pd.Timestamp(VAULT_START)] for a, df in prices.items()}
    return prices


def signals(c: Candidate, prices) -> dict[str, pd.Series]:
    fn = FAMILIES[c.family][0]
    out = {}
    for a, df in prices.items():
        if c.family == "opening_range" and a in S_CRYPTO:
            continue
        s = fn(df, **c.params).reindex(df.index).fillna(0).astype(int)
        if c.trend:
            s = S.with_trend(s, S.daily_trend(df))
        if not c.short:
            s = s.clip(lower=0)
        out[a] = s
    return out


from .data import CRYPTO as S_CRYPTO  # noqa: E402


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
    sl = []
    rng = np.random.default_rng(seed) if seed is not None else None
    for a, s in sig.items():
        if rng is not None:  # random twin: same exits, same number of signals, random timing (and side)
            fire = rng.random(len(s)) < (s != 0).mean()
            side = np.where(rng.random(len(s)) < 0.5, 1, -1) if c.short else 1
            s = pd.Series(np.where(fire, side, 0), s.index)
        sl.append(Sleeve(a, c.family, s, rule, c.short))
    cfg = PortfolioConfig(risk_pct=RISK, max_gross=MAX_GROSS, max_open_risk=MAX_OPEN_RISK)
    return run_portfolio(prices, sl, COSTS, cfg, start, end)


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

def shelf_life(events: pd.DataFrame, prices) -> dict:
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
    by_asset = events.groupby("asset")["edge"].mean()
    return {"months": len(ic), "pos_months": float(pos.mean()), "longest_bad_run": longest_bad,
            "ic_first_half": float(ic.iloc[:half].mean()), "ic_second_half": float(ic.iloc[half:].mean()),
            "regimes_positive": int((by_reg > 0).sum()), "regimes_seen": int(by_reg.notna().sum()),
            "breadth": float((by_asset > 0).mean())}


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
    "shelf life: works on >= 55% of assets": lambda s: s["breadth"] >= 0.55,
}


def registry() -> pd.DataFrame:
    path = OUT / "registry.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def evaluate(c: Candidate, prices) -> dict:
    sig = signals(c, prices)
    row = {"id": c.id, "label": c.label(), "family": c.family, "candidate": json.dumps(asdict(c))}
    for w, (a, b) in (("s", SEARCH), ("v", VALIDATION)):
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
    both = {k: v[(v.index >= pd.Timestamp(SEARCH[0])) & (v.index <= pd.Timestamp(VALIDATION[1]))]
            for k, v in sig.items()}
    row |= shelf_life(edge_events(both, prices, c.horizon()), prices)
    return row


def score(rows: pd.DataFrame) -> pd.DataFrame:
    """Deflated Sharpe with N = every attempt so far, then the gates."""
    rows = rows.copy()
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
    prices = load()
    reg = registry()
    done = set(reg["id"]) if len(reg) else set()
    new = []
    for i, c in enumerate(candidates, 1):
        if c.id in done:
            continue
        log.info("[%d/%d] %s", i, len(candidates), c.label())
        new.append(evaluate(c, prices))
        reg = pd.concat([reg, pd.DataFrame(new[-1:])], ignore_index=True)
        reg.to_csv(OUT / "registry.csv", index=False)  # saved after every attempt
    reg = score(reg)
    reg.to_csv(OUT / "registry.csv", index=False)
    report(reg)
    return reg


def grid() -> list[Candidate]:
    out = []
    for fam, (_, space) in FAMILIES.items():
        keys = list(space)
        for vals in itertools.product(*(space[k] for k in keys)):
            for rule in RULES.values():
                out.append(Candidate(fam, dict(zip(keys, vals)), dict(rule)))
    return out


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
    prices = load(include_vault=True)
    sig = signals(c, prices)
    end = max(df.index[-1] for df in prices.values())
    st = trading_stats(backtest(c, prices, sig, VAULT_START, end))
    rnd = [trading_stats(backtest(c, prices, sig, VAULT_START, end, seed=s)) for s in range(SEEDS)]
    win = {k: v[v.index >= pd.Timestamp(VAULT_START)] for k, v in sig.items()}
    ic = monthly_ic(edge_events(win, prices, c.horizon()))
    ok = st["return"] > 0 and st["avg_r"] > np.nanmean([r["avg_r"] for r in rnd]) and ic.mean() > 0
    used[cid] = {"date": str(pd.Timestamp.now().date()), "label": c.label(), "result": "PASS" if ok else "FAIL",
                 "return": st["return"], "avg_r": st["avg_r"], "ic": float(ic.mean())}
    log_path.write_text(json.dumps(used, indent=1, default=float))
    return used[cid]


# ------------------------------------------------------------------ report

def report(reg: pd.DataFrame) -> Path:
    n = len(reg)
    top = reg.sort_values(["gates_passed", "s_icir"], ascending=False).head(25)
    md = [f"# Strategy finder – {pd.Timestamp.now():%Y-%m-%d}", "",
          f"**{n} strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). "
          f"Search {SEARCH[0]} → {SEARCH[1][:10]}, validation {VALIDATION[0]} → {VALIDATION[1][:10]}, "
          f"vault from {VAULT_START} (sealed). {len(GATES)} gates; only a candidate passing all of them may "
          "take its one vault test.", "",
          "| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | "
          "return v | DSR | months + | regimes + | breadth | first failed gate |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in top.iterrows():
        md.append(f"| {r.gates_passed}/{len(GATES)} | `{r.id}` {r.label} | {r.s_ic:+.3f} | {r.s_icir:+.2f} | "
                  f"{r.v_ic:+.3f} | {r.s_avg_r:+.2f} / {r.s_rand_avg_r:+.2f} | {r.v_avg_r:+.2f} / {r.v_rand_avg_r:+.2f} | "
                  f"{r.v_return:+.1%} | {r.s_dsr:.2f} | {r.get('pos_months', np.nan):.0%} | "
                  f"{int(r.get('regimes_positive', 0))}/{int(r.get('regimes_seen', 0))} | {r.get('breadth', np.nan):.0%} | "
                  f"{(r.failed or 'none – vault candidate').split(';')[0]} |")
    fails = pd.Series([f for x in reg["failed"].fillna("") for f in x.split("; ") if f]).value_counts()
    md += ["", "## Why strategies fail (all attempts)", ""] + [f"- {k}: {v} of {n}" for k, v in fails.items()]
    log_path = OUT / "vault_log.json"
    if log_path.exists():
        md += ["", "## Vault tests (one per strategy, final)", ""]
        md += [f"- `{k}` {v['label']}: **{v['result']}** (return {v['return']:+.1%}, avg R {v['avg_r']:+.2f}, "
               f"IC {v['ic']:+.3f}) on {v['date']}" for k, v in json.loads(log_path.read_text()).items()]
    path = OUT / "report.md"
    path.write_text("\n".join(md) + "\n")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("grid")
    sub.add_parser("report")
    v = sub.add_parser("vault")
    v.add_argument("id")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.cmd == "grid":
        reg = run(grid())
        print(f"{len(reg)} strategies in the registry; report: {OUT / 'report.md'}")
    elif args.cmd == "report":
        print(report(score(registry())))
    else:
        print(vault(args.id))


if __name__ == "__main__":
    main()
