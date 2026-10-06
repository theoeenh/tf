"""The ML ranker: every week, score the S&P 1500 on the next month's return relative to the average
stock, from what is known that day. Walk-forward: each model only ever trains on the past.

    python -m algo.ranker            # IC report of the ranker on the research data (vault sealed)

Features, all as of the Friday close (cross-sectional percentile ranks, so a model trained in one
market regime reads the same scale in another):
  momentum 12-1 and 6-1 months, last month's and last week's return (reversal), 60-day volatility,
  distance to the 52-week high, distance to the 200-day average, dollar volume (liquidity / size),
  insider buying (distinct buyers in 90 days, $ bought) and discretionary
  selling (30 days) from Form 4 filings filed by that day, the short share of off-exchange volume
  (FINRA, 20-day average and its change vs 120 days, from the day after), fundamentals from the SEC's
  XBRL filings (from the session after the filing: algo/fundamentals.py), plus the market's last month.
Target: the return from the next session's open over the next 20 sessions, minus the average of all
stocks over the same days (so survivorship and the market's rise are taken out), as a percentile rank.
Walk-forward: a refit every 13 weeks on every week whose target was fully known by then (no overlap
with the future), from 2 years of data on. Models: ridge (linear) and gradient boosting.
The finder uses the scores as the family 'ml_rank' (finder_families.py): buy the top of the ranking.
"""
from __future__ import annotations

import hashlib
import logging

import numpy as np
import pandas as pd

from . import wide

log = logging.getLogger(__name__)
HORIZON = 20
REFIT_WEEKS = 13
MIN_TRAIN_WEEKS = 104
MIN_TRAIN_ROWS = 5000
# No index membership: the S&P 500 / 400 / 600 lists are today's, so "in the S&P 500" tells the model
# which small companies of 2019 grew into big ones (alone it had the highest IC of all: a leak).
FEATURES = ["mom_12_1", "mom_6_1", "ret_1m", "ret_1w", "vol_60", "off_high", "trend_200", "dollar_vol",
            "ins_buyers", "ins_buy", "ins_sell", "mkt_1m"]
SHORT_FEATURES = ["short_20", "short_chg"]  # added 2026-10-05 (FINRA data): a separate version, counted
# added 2026-10-06 (SEC XBRL, algo/fundamentals.py): earnings yield, book to market, ROA, accruals,
# revenue growth, SUE, each from the session after the filing. Again its own counted version.
FUND_FEATURES = ["f_ey", "f_bm", "f_roa", "f_accr", "f_rev_g", "f_sue"]


def panel(prices: dict, col: str) -> pd.DataFrame:
    return pd.DataFrame({a: df[col] for a, df in prices.items()}).sort_index()


def fridays(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """The last session of every week."""
    s = pd.Series(index, index)
    return pd.DatetimeIndex(s.groupby(index.to_period("W-FRI")).max().to_numpy())


def insider_panel(dates: pd.DatetimeIndex, stocks: list[str]) -> dict[str, pd.DataFrame]:
    """Insider activity known at each date (filing date <= date): buyers / $ bought in 90 days,
    discretionary $ sold in 30 days."""
    t = wide.load_insider()
    out = {k: pd.DataFrame(0.0, dates, stocks) for k in ("ins_buyers", "ins_buy", "ins_sell")}
    if t.empty:
        return out
    t = t[t["ticker"].isin(stocks)]
    for (tick, code), g in t.groupby(["ticker", "code"]):
        g = g.sort_values("filed")
        filed = g["filed"].to_numpy()
        if code == "P":
            for k, days, fn in (("ins_buyers", 90, lambda x: x["owner"].nunique()),
                                ("ins_buy", 90, lambda x: np.log1p(x["value"].sum()))):
                lo = np.searchsorted(filed, (dates - pd.Timedelta(days=days)).to_numpy(), side="right")
                hi = np.searchsorted(filed, dates.to_numpy(), side="right")
                out[k][tick] = [fn(g.iloc[a:b]) if b > a else 0.0 for a, b in zip(lo, hi)]
        elif code == "S":
            g = g[g["plan"].fillna(0) == 0]
            filed = g["filed"].to_numpy()
            lo = np.searchsorted(filed, (dates - pd.Timedelta(days=30)).to_numpy(), side="right")
            hi = np.searchsorted(filed, dates.to_numpy(), side="right")
            out["ins_sell"][tick] = [np.log1p(g["value"].iloc[a:b].sum()) if b > a else 0.0 for a, b in zip(lo, hi)]
    return out


def dataset(prices: dict) -> pd.DataFrame:
    """One row per (Friday, stock): features known that day and the target (NaN when not yet known)."""
    close, opn, vol = panel(prices, "Close"), panel(prices, "Open"), panel(prices, "Volume")
    days = close.index
    f = {
        "mom_12_1": close.shift(21) / close.shift(252) - 1,
        "mom_6_1": close.shift(21) / close.shift(126) - 1,
        "ret_1m": close / close.shift(21) - 1,
        "ret_1w": close / close.shift(5) - 1,
        "vol_60": np.log(close).diff().rolling(60, min_periods=40).std(),
        "off_high": close / close.rolling(252, min_periods=200).max() - 1,
        "trend_200": close / close.rolling(200, min_periods=150).mean() - 1,
        "dollar_vol": np.log1p((close * vol).rolling(20, min_periods=10).mean()),
    }
    # FINRA short share of off-exchange volume, published after the close: known from the next session
    sv = wide.load_short_volume().reindex(index=days, columns=close.columns).shift(1)
    f["short_20"] = sv.rolling(20, min_periods=10).mean()
    f["short_chg"] = f["short_20"] - sv.rolling(120, min_periods=60).mean()
    mkt = close.pct_change(21, fill_method=None).mean(axis=1)
    f["mkt_1m"] = pd.DataFrame(np.repeat(mkt.to_numpy()[:, None], close.shape[1], axis=1), days, close.columns)
    # target: next open -> 20 sessions later, minus the average stock over the same days
    fwd = close.shift(-HORIZON) / opn.shift(-1) - 1
    f["target"] = fwd.sub(fwd.mean(axis=1), axis=0)
    weeks = fridays(days)
    weeks = weeks[weeks >= days[0] + pd.Timedelta(days=380)]
    rows = {k: v.reindex(weeks) for k, v in f.items()}
    rows |= {k: v for k, v in insider_panel(weeks, list(close.columns)).items()}
    from . import fundamentals

    rows |= fundamentals.features(weeks, close)
    long = pd.concat({k: v.stack(future_stack=True) for k, v in rows.items()}, axis=1)
    long.index.names = ["date", "stock"]
    long = long[long["mom_12_1"].notna() & np.isfinite(long["vol_60"])]
    # percentile ranks within each date for the stock-specific features
    for k in FEATURES + SHORT_FEATURES + FUND_FEATURES:
        if k != "mkt_1m":
            long[k] = long.groupby(level="date")[k].rank(pct=True)
    long["target_rank"] = long.groupby(level="date")["target"].rank(pct=True)
    return long


def _model(kind: str):
    if kind == "ridge":
        from sklearn.linear_model import Ridge

        return Ridge(alpha=10.0)
    from sklearn.ensemble import HistGradientBoostingRegressor

    return HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                                         min_samples_leaf=500, l2_regularization=1.0, random_state=0)


def walk_forward(ds: pd.DataFrame, kind: str, features: list[str] | None = None) -> pd.Series:
    """Score of every (date, stock), each from a model fitted only on weeks whose target was known
    (target end = date + HORIZON sessions) before that date. NaN for the first MIN_TRAIN_WEEKS."""
    features = features or FEATURES
    dates = ds.index.get_level_values("date").unique().sort_values()
    out = []
    for k in range(MIN_TRAIN_WEEKS, len(dates), REFIT_WEEKS):
        refit = dates[k]
        known_until = refit - pd.Timedelta(days=HORIZON * 7 / 5 + 3)  # 20 sessions ~ 28 calendar days
        train = ds[(ds.index.get_level_values("date") <= known_until) & ds["target_rank"].notna()]
        test_dates = dates[k:k + REFIT_WEEKS]
        test = ds[ds.index.get_level_values("date").isin(test_dates)]
        if len(train) < MIN_TRAIN_ROWS or test.empty:
            continue
        m = _model(kind).fit(train[features].fillna(0.5), train["target_rank"])
        out.append(pd.Series(m.predict(test[features].fillna(0.5)), test.index))
        log.info("ranker %s: fitted on %d rows up to %s, scored %s -> %s", kind, len(train), known_until.date(),
                 test_dates[0].date(), test_dates[-1].date())
    return pd.concat(out) if out else pd.Series(dtype=float)


_CACHE: dict = {}


def scores(prices: dict, kind: str, short: bool = False, fund: bool = False) -> pd.Series:
    """Cached walk-forward scores for this universe and data end."""
    feats = FEATURES + (SHORT_FEATURES if short else []) + (FUND_FEATURES if fund else [])
    key = hashlib.sha1((kind + ("+short" if short else "") + ("+fund" if fund else "") + str(max(df.index[-1] for df in prices.values())) + ",".join(sorted(prices)))
                       .encode()).hexdigest()[:12]
    if key in _CACHE:
        return _CACHE[key]
    path = wide.WIDE_DIR / f"ml_scores_{key}.pkl"
    if path.exists():
        s = pd.read_pickle(path)
    else:
        s = walk_forward(dataset(prices), kind, feats)
        wide.WIDE_DIR.mkdir(parents=True, exist_ok=True)
        s.to_pickle(path)
    _CACHE[key] = s
    return s


def ic_report(ds: pd.DataFrame, s: pd.Series) -> pd.DataFrame:
    """Weekly rank correlation between the score and the realised excess return (the IC), and the
    top-decile minus average return, by year."""
    d = ds.loc[s.index].assign(score=s)
    d = d[d["target"].notna()]
    wk = d.groupby(level="date").apply(lambda g: pd.Series({
        "ic": g["score"].corr(g["target"], method="spearman"),
        "top10": g.loc[g["score"] >= g["score"].quantile(0.9), "target"].mean()}))
    yr = wk.groupby(wk.index.year).agg(ic=("ic", "mean"), ic_sd=("ic", "std"), top10=("top10", "mean"), weeks=("ic", "size"))
    yr["icir"] = yr["ic"] / yr["ic_sd"]
    return yr


def main() -> None:
    from .finder import load

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    prices = load(data="daily500")  # vault sealed
    ds = dataset(prices)
    print(f"{len(ds):,} stock-weeks, {ds.index.get_level_values('date').nunique()} weeks")
    for kind, short, fund in (("ridge", False, False), ("gbm", False, False), ("ridge", True, False),
                              ("gbm", True, False), ("ridge", True, True), ("gbm", True, True)):
        s = scores(prices, kind, short, fund)
        print(f"\n{kind}{' + short selling' if short else ''}{' + fundamentals' if fund else ''}: IC by year (20-session excess return; top10 = best decile minus average, per 20 sessions)")
        print(ic_report(ds, s).round(4).to_string())


if __name__ == "__main__":
    main()
