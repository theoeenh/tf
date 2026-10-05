"""ML insider scorer: which insider-buying clusters are worth following.

    python -m algo.insider_ml        # walk-forward report on the research data (vault sealed)

Events: every insider cluster on the S&P 1500 (2+ distinct insiders buying in the open market within
90 days; finder_families.insider_cluster), on the day it forms. For each, what was known that day:
  - the buying: distinct buyers, $ bought (log), the largest single purchase, $ bought relative to the
    stock's usual daily dollar volume, whether an officer (CEO, CFO, ...) bought, insiders' discretionary
    sales in the 90 days before (log $);
  - the stock: return over the last month and 6 months, distance to the 52-week high, 60-day
    volatility, dollar volume (size / liquidity), sessions since its last earnings release;
  - the market: the average stock's last month.
Target: the return from the next open over 60 sessions, minus the average stock over the same days.
Walk-forward: a refit each January on the clusters whose 60 sessions had ended, from 2018 on (two years
of clusters first); each score comes from a model that never saw that cluster or anything after it.
The cut-off for "keep" is a share of the training clusters' own scores (known at fit time).
The finder family 'insider_ml' trades the kept clusters.
"""
from __future__ import annotations

import hashlib
import logging

import numpy as np
import pandas as pd

from . import wide

log = logging.getLogger(__name__)
HORIZON = 60
FEATURES = ["buyers", "bought", "largest", "bought_vs_volume", "officer", "sold_before", "ret_1m", "ret_6m",
            "off_high", "vol_60", "dollar_vol", "since_earnings", "mkt_1m"]


def events(prices: dict) -> pd.DataFrame:
    """One row per cluster (the day it forms): features known that day and the 60-session target."""
    from .finder_families import insider_cluster

    t = wide.load_insider()
    buys, sells = t[t["code"] == "P"], t[(t["code"] == "S") & (t["plan"].fillna(0) == 0)]
    e = wide.load_earnings()
    close = pd.DataFrame({a: df["Close"] for a, df in prices.items()}).sort_index()
    fwd_all = None
    sig = insider_cluster(prices, buyers=2, days=90)
    mkt = close.pct_change(21, fill_method=None).mean(axis=1)
    rows = []
    for a, s in sig.items():
        if not s.any():
            continue
        df = prices[a]
        c, o, v = df["Close"], df["Open"], df["Volume"]
        dvol = (c * v).rolling(20, min_periods=10).mean()
        vol60 = np.log(c).diff().rolling(60, min_periods=40).std()
        hi = c.rolling(252, min_periods=120).max()
        ed = pd.DatetimeIndex(e.loc[e["ticker"] == a, "day"]).sort_values()
        b_a, s_a = buys[buys["ticker"] == a], sells[sells["ticker"] == a]
        for d in s.index[s.to_numpy() > 0]:
            p = df.index.get_loc(d)
            w = b_a[(b_a["filed"] > d - pd.Timedelta(days=90)) & (b_a["filed"] <= d)]
            if w.empty or p < 130:
                continue
            per = w.groupby("accession")["value"].sum()
            prior_e = ed[ed <= d]
            sold = s_a[(s_a["filed"] > d - pd.Timedelta(days=90)) & (s_a["filed"] <= d)]["value"].sum()
            target = np.nan
            if p + HORIZON < len(df):
                target = c.iloc[p + HORIZON] / o.iloc[p + 1] - 1
            rows.append({"date": d, "stock": a, "buyers": w["owner"].nunique(), "bought": np.log1p(w["value"].sum()),
                         "largest": np.log1p(per.max()), "bought_vs_volume": w["value"].sum() / max(dvol.iloc[p], 1.0),
                         "officer": float(w["role"].fillna("").str.contains("Officer", case=False).any()),
                         "sold_before": np.log1p(sold), "ret_1m": c.iloc[p] / c.iloc[p - 21] - 1,
                         "ret_6m": c.iloc[p] / c.iloc[p - 126] - 1, "off_high": c.iloc[p] / hi.iloc[p] - 1,
                         "vol_60": vol60.iloc[p], "dollar_vol": np.log1p(dvol.iloc[p]),
                         "since_earnings": float((d - prior_e[-1]).days) if len(prior_e) else 365.0,
                         "mkt_1m": mkt.get(d, np.nan), "target": target})
    ev = pd.DataFrame(rows)
    if ev.empty:
        return ev
    # relative to the average stock over the same 60 sessions
    if fwd_all is None:
        opn = pd.DataFrame({a: df["Open"] for a, df in prices.items()}).sort_index()
        fwd_all = (close.shift(-HORIZON) / opn.shift(-1) - 1).mean(axis=1)
    ev["target"] = ev["target"] - ev["date"].map(fwd_all)
    return ev.sort_values("date").reset_index(drop=True)


def _model(kind: str):
    if kind == "ridge":
        from sklearn.linear_model import Ridge
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        return make_pipeline(StandardScaler(), Ridge(alpha=30.0))
    from sklearn.ensemble import HistGradientBoostingRegressor

    return HistGradientBoostingRegressor(max_iter=150, learning_rate=0.03, max_leaf_nodes=7, min_samples_leaf=60,
                                         l2_regularization=5.0, random_state=0)


def walk_forward(ev: pd.DataFrame, kind: str, keep: float) -> pd.DataFrame:
    """Score and keep-flag of every cluster from 2018 on, each from a model fitted (each January) on the
    clusters whose 60 sessions were over (target end ~ 90 calendar days after the cluster)."""
    out = []
    X = ev[FEATURES].replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    years = sorted(ev["date"].dt.year.unique())
    for y in years:
        if y < 2018:
            continue
        fit_day = pd.Timestamp(f"{y}-01-01")
        train = ev[(ev["date"] < fit_day - pd.Timedelta(days=95)) & ev["target"].notna()]
        test = ev[ev["date"].dt.year == y]
        if len(train) < 300 or test.empty:
            continue
        y_tr = train["target"].clip(train["target"].quantile(0.02), train["target"].quantile(0.98))
        m = _model(kind).fit(X.loc[train.index], y_tr)
        cut = np.quantile(m.predict(X.loc[train.index]), 1 - keep)
        sc = m.predict(X.loc[test.index])
        out.append(pd.DataFrame({"date": test["date"], "stock": test["stock"], "score": sc, "keep": sc >= cut}))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=["date", "stock", "score", "keep"])


_CACHE: dict = {}


def kept(prices: dict, kind: str, keep: float) -> pd.DataFrame:
    key = hashlib.sha1(f"{kind}{keep}{max(df.index[-1] for df in prices.values())}{','.join(sorted(prices))}"
                       .encode()).hexdigest()[:12]
    if key not in _CACHE:
        path = wide.WIDE_DIR / f"ml_insider_{key}.pkl"
        if path.exists():
            _CACHE[key] = pd.read_pickle(path)
        else:
            _CACHE[key] = walk_forward(events(prices), kind, keep)
            _CACHE[key].to_pickle(path)
    return _CACHE[key]


def main() -> None:
    from .finder import load

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    prices = load(data="daily500")
    ev = events(prices)
    print(f"{len(ev)} clusters; average 60-session excess return {ev['target'].mean():+.2%}")
    for kind in ("ridge", "gbm"):
        wf = walk_forward(ev, kind, 0.3).merge(ev[["date", "stock", "target"]], on=["date", "stock"])
        yr = wf.groupby([wf["date"].dt.year, "keep"])["target"].mean().unstack()
        ic = wf.groupby(wf["date"].dt.year).apply(lambda g: g["score"].corr(g["target"], method="spearman"))
        print(f"\n{kind}: 60-session excess return of kept (True) vs dropped (False) clusters, and rank IC")
        print(pd.concat([yr, ic.rename("ic")], axis=1).round(4).to_string())


if __name__ == "__main__":
    main()
