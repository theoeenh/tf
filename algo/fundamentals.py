"""Company fundamentals from the SEC's XBRL filings, point in time: a number is only used from the
session AFTER the 10-Q / 10-K that first reported it was filed (first-reported values: later
restatements never leak back).

    python -m algo.fundamentals          # download companyfacts.zip (~1.4 GB) and rebuild the table

Stored (data/wide/fundamentals.csv.gz), one row per (ticker, item, period end):
  discrete quarters  rev_q, ni_q, cfo_q, eps_q  (a Q4 or a year-to-date figure is turned into its
                     quarter by difference: FY - 9 months, 6 months - 3 months, ...)
  balance / shares   assets, equity, shares  (instants)
with `filed`, the date of the first filing that carried it. Features for the ranker: features().
"""
from __future__ import annotations

import json
import logging
import zipfile

import numpy as np
import pandas as pd

from . import wide

log = logging.getLogger(__name__)
PATH = wide.WIDE_DIR / "fundamentals.csv.gz"
URL = "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"
FIRST_END = "2013-01-01"  # a year before the prices start, for TTM and growth
DURATIONS = {  # item -> tags, by preference (companies switch tags over the years)
    "rev_q": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
              "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet",
              "RevenuesNetOfInterestExpense"],
    "ni_q": ["NetIncomeLoss", "ProfitLoss"],
    "cfo_q": ["NetCashProvidedByUsedInOperatingActivities",
              "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
    "eps_q": ["EarningsPerShareDiluted", "EarningsPerShareBasic"],
}
INSTANTS = {"assets": ["Assets"], "equity": ["StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]}
EMPTY = pd.DataFrame({"end": pd.to_datetime([]), "val": pd.Series(dtype=float), "filed": pd.to_datetime([])})
FEATURES = ["f_ey", "f_bm", "f_roa", "f_accr", "f_rev_g", "f_sue"]


def _facts(tags_facts: dict, tags: list[str]) -> pd.DataFrame:
    """All 10-Q / 10-K values of these tags (one unit each), the first-filed value per period."""
    rows = []
    for pref, tag in enumerate(tags):
        f = tags_facts.get(tag)
        if not f:
            continue
        for unit, vals in f["units"].items():
            for v in vals:
                if v.get("form", "").startswith("10-") and v.get("end", "") >= FIRST_END:
                    rows.append((pref, v.get("start"), v["end"], v["val"], v["filed"]))
    if not rows:
        return pd.DataFrame(columns=["start", "end", "val", "filed"])
    df = pd.DataFrame(rows, columns=["pref", "start", "end", "val", "filed"])
    for c in ("start", "end", "filed"):
        df[c] = pd.to_datetime(df[c])
    # first filed wins; on the same filing day the preferred tag
    df = df.sort_values(["filed", "pref"]).drop_duplicates(["start", "end"] if df["start"].notna().any() else ["end"])
    return df.drop(columns="pref")


def quarters(df: pd.DataFrame) -> pd.DataFrame:
    """Discrete quarters (end, val, filed) from durations: direct ~3-month values, plus differences of
    two values with the same start whose ends are ~3 months apart (Q4 = FY - 9M, Q2 = 6M - 3M)."""
    if df.empty:
        return pd.DataFrame(columns=["end", "val", "filed"])
    df = df.dropna(subset=["start"]).copy()
    df["days"] = (df["end"] - df["start"]).dt.days
    direct = df[df["days"].between(80, 100)][["end", "val", "filed"]]
    derived = []
    for _, g in df[df["days"] > 100].groupby("start"):
        g = g.sort_values("end")
        same = df[(df["start"] == g["start"].iloc[0])].sort_values("end")
        for _, long in g.iterrows():
            short = same[((long["end"] - same["end"]).dt.days.between(80, 100))]
            if len(short):
                s = short.iloc[-1]
                derived.append((long["end"], long["val"] - s["val"], max(long["filed"], s["filed"])))
    q = pd.concat([direct, pd.DataFrame(derived, columns=["end", "val", "filed"])], ignore_index=True)
    # the same quarter reported directly and derived (or with ends a few days apart): the first known
    if q.empty:
        return pd.DataFrame(columns=["end", "val", "filed"])
    q["end"], q["filed"] = pd.to_datetime(q["end"]), pd.to_datetime(q["filed"])
    q = q.sort_values(["filed"]).drop_duplicates("end")
    q = q.sort_values("end")
    keep = q["end"].diff().dt.days.fillna(999) > 20
    return q[keep].reset_index(drop=True)


def parse_company(raw: bytes) -> pd.DataFrame:
    d = json.loads(raw)
    gaap = d.get("facts", {}).get("us-gaap", {})
    parts = []
    for item, tags in DURATIONS.items():
        parts.append(quarters(_facts(gaap, tags)).assign(item=item))
    for item, tags in INSTANTS.items():
        f = _facts(gaap, tags)
        parts.append(f[["end", "val", "filed"]].drop_duplicates("end").assign(item=item))
    sh = _facts(d.get("facts", {}).get("dei", {}), ["EntityCommonStockSharesOutstanding"])
    parts.append(sh[["end", "val", "filed"]].drop_duplicates("end").assign(item="shares"))
    return pd.concat([p for p in parts if len(p)], ignore_index=True) if any(len(p) for p in parts) else pd.DataFrame()


def build(zip_path, tickers: list[str]) -> pd.DataFrame:
    from .insider import INSIDER_DIR, cik

    cik("AAPL")  # makes sure company_tickers.json is there
    want = {t.replace("-", "."): t for t in tickers} | {t: t for t in tickers}
    cik_of = {}
    for row in json.loads((INSIDER_DIR / "company_tickers.json").read_text()).values():
        t = want.get(row["ticker"])
        if t and t not in cik_of.values():
            cik_of[int(row["cik_str"])] = t
    out = []
    with zipfile.ZipFile(zip_path) as z:
        names = set(z.namelist())
        for n, (c, t) in enumerate(cik_of.items(), 1):
            name = f"CIK{c:010d}.json"
            if name in names:
                df = parse_company(z.read(name))
                if len(df):
                    out.append(df.assign(ticker=t))
            if n % 300 == 0:
                log.info("fundamentals %d/%d", n, len(cik_of))
    df = pd.concat(out, ignore_index=True)
    df["end"] = df["end"].dt.strftime("%Y-%m-%d")
    df["filed"] = df["filed"].dt.strftime("%Y-%m-%d")
    return df[["ticker", "item", "end", "filed", "val"]].sort_values(["ticker", "item", "end"])


def update(zip_path=None) -> pd.DataFrame:
    """Rebuild data/wide/fundamentals.csv.gz (downloads companyfacts.zip unless given a path)."""
    if zip_path is None:
        import shutil
        import tempfile
        import urllib.request

        from .insider import UA

        tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        with urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=60) as r, tmp:
            shutil.copyfileobj(r, tmp, 1 << 20)
        zip_path = tmp.name
        log.info("companyfacts.zip downloaded")
    df = build(zip_path, wide.members())
    wide.WIDE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PATH, index=False)
    log.info("fundamentals: %d rows, %d tickers", len(df), df["ticker"].nunique())
    return df


def load() -> pd.DataFrame:
    if not PATH.exists():
        return pd.DataFrame(columns=["ticker", "item", "end", "filed", "val"])
    df = pd.read_csv(PATH)
    df["end"] = pd.to_datetime(df["end"])
    df["filed"] = pd.to_datetime(df["filed"])
    return df


def _known(s: pd.DataFrame, dates: pd.DatetimeIndex) -> pd.Series:
    """The value with the latest period end among those filed before each date (filed < date: a
    filing of the day is used from the next session)."""
    s = s.dropna(subset=["val"]).sort_values(["filed", "end"])
    s = s[s["end"] > s["end"].cummax().shift(1).fillna(pd.Timestamp(0))]  # newest period known so far
    if s.empty:
        return pd.Series(np.nan, dates)
    pos = np.searchsorted(s["filed"].to_numpy(), dates.to_numpy(), side="left") - 1
    v = s["val"].to_numpy()
    return pd.Series(np.where(pos >= 0, v[np.clip(pos, 0, None)], np.nan), dates)


def _ttm(q: pd.DataFrame) -> pd.DataFrame:
    """Trailing 4 quarters (only when the 4 ends span about a year), filed when the last was."""
    q = q.sort_values("end").reset_index(drop=True)
    span = (q["end"] - q["end"].shift(3)).dt.days
    out = q.assign(val=q["val"].rolling(4).sum().where(span.between(250, 290)),
                   filed=pd.to_datetime(q["filed"].astype("int64").rolling(4).max()))
    return out.dropna(subset=["val"])


def _sue(q: pd.DataFrame) -> pd.DataFrame:
    """Standardised unexpected earnings: EPS minus the same quarter a year earlier, over the standard
    deviation of that change in the previous 8 quarters (at least 4)."""
    q = q.sort_values("end").reset_index(drop=True)
    yoy = (q["end"] - q["end"].shift(4)).dt.days.between(350, 380)
    d = (q["val"] - q["val"].shift(4)).where(yoy)
    sd = d.shift(1).rolling(8, min_periods=4).std()
    return q.assign(val=(d / sd.replace(0, np.nan)).clip(-10, 10)).dropna(subset=["val"])


def features(dates: pd.DatetimeIndex, close: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Point-in-time fundamental features per (date, stock), from `dates` (Fridays) and the closes
    of those dates: earnings yield, book to market, return on assets, accruals, revenue growth, SUE."""
    fd = load()
    stocks = list(close.columns)
    out = {k: pd.DataFrame(np.nan, dates, stocks) for k in FEATURES}
    if fd.empty:
        return out
    px = close.reindex(dates)
    for t, g in fd[fd["ticker"].isin(stocks)].groupby("ticker"):
        it = {k: v for k, v in g.groupby("item")}
        get = lambda k: it.get(k, EMPTY)
        ni = _known(_ttm(get("ni_q")), dates)
        cfo = _known(_ttm(get("cfo_q")), dates)
        rev_ttm = _ttm(get("rev_q"))
        assets = _known(get("assets"), dates)
        equity = _known(get("equity"), dates)
        mcap = _known(get("shares"), dates) * px[t]
        mcap = mcap.where(mcap > 0)
        assets = assets.where(assets > 0)
        out["f_ey"][t] = ni / mcap
        out["f_bm"][t] = equity / mcap
        out["f_roa"][t] = ni / assets
        out["f_accr"][t] = (ni - cfo) / assets
        if len(rev_ttm) > 4:
            r = rev_ttm.sort_values("end").reset_index(drop=True)
            yoy = (r["end"] - r["end"].shift(4)).dt.days.between(350, 380)
            prev = r["val"].shift(4).where(yoy)
            g_ = r.assign(val=(r["val"] / prev.where(prev > 0) - 1).clip(-1, 5),
                          filed=pd.to_datetime(np.maximum(r["filed"].astype("int64"), r["filed"].shift(4).fillna(r["filed"]).astype("int64"))))
            out["f_rev_g"][t] = _known(g_, dates)
        out["f_sue"][t] = _known(_sue(get("eps_q")), dates)
    return out


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zip", nargs="?", help="a companyfacts.zip already downloaded")
    ap.add_argument("--if-stale", type=int, metavar="DAYS", help="only when the newest filing stored is older")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.if_stale is not None:
        newest = load()["filed"].max()
        if pd.notna(newest) and newest >= pd.Timestamp.now() - pd.Timedelta(days=args.if_stale):
            print(f"fundamentals fresh (newest filing {newest.date()})")
            return
    df = update(args.zip)
    print(f"fundamentals: {len(df)} rows, {df['ticker'].nunique()} tickers, items {sorted(df['item'].unique())}")


if __name__ == "__main__":
    main()
