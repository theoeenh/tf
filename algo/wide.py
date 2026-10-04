"""Wide research universe: the S&P 500 on daily bars, plus every insider trade the SEC published.

    python -m algo.wide            # download / update members, daily bars and insider trades

Research only (the strategy finder): nothing here trades. The live accounts keep their own
universe; a strategy found here would first go through the finder's gates and the vault.

- members      today's S&P 500 list (Wikipedia). Survivorship bias: companies that fell out of
               the index since 2016 are missing, which flatters any long strategy. The finder
               measures every signal against the same stocks' ordinary drift and against random
               entries on the same stocks, which removes most of that bias from the comparison.
- daily bars   Alpaca, split- and dividend-adjusted, 2016 -> now, data/wide/daily.csv.gz
               (not committed: about 30 MB; GitHub caches it between runs)
- insider      SEC "Insider Transactions Data Sets" (every Form 4 of every company, one zip per
               quarter): open-market purchases (P) and sales (S) of common stock, by filing date.
               data/wide/insider.csv.gz (committed: small, and re-downloading takes a while).
               Point in time: the filing date. A Form 4 can be accepted up to 22:00 New York, so
               a strategy may only act on it from the NEXT session (the finder's signals fire on
               the filing day's close and fill at the next open, which is exactly that).
"""
from __future__ import annotations

import io
import logging
import time
import urllib.request
import zipfile

import numpy as np
import pandas as pd

from .data import COLUMNS, DATA_DIR

log = logging.getLogger(__name__)
WIDE_DIR = DATA_DIR / "wide"
START = "2016-01-01"
UA = {"User-Agent": "tf-research theoeenhoorn@gmail.com"}
SEC_BULK = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{q}_form345.zip"


def _get(url: str, headers=None, tries: int = 4) -> bytes:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0 tf-research"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except OSError as exc:
            if attempt == tries - 1:
                raise
            log.info("retry %d %s (%s)", attempt + 1, url, exc)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


# ------------------------------------------------------------------ members

def members(refresh: bool = False) -> list[str]:
    path = WIDE_DIR / "members.csv"
    if path.exists() and not refresh:
        return pd.read_csv(path)["symbol"].tolist()
    html = _get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies").decode()
    t = pd.read_html(io.StringIO(html), attrs={"id": "constituents"})[0]
    out = pd.DataFrame({"symbol": t["Symbol"].str.replace(".", "-", regex=False), "sector": t["GICS Sector"]})
    WIDE_DIR.mkdir(parents=True, exist_ok=True)
    out.sort_values("symbol").to_csv(path, index=False)
    return out["symbol"].tolist()


def sectors() -> dict[str, str]:
    m = pd.read_csv(WIDE_DIR / "members.csv")
    return dict(zip(m["symbol"], m["sector"]))


# ------------------------------------------------------------------ daily bars

def _bars(symbols: list[str], start: str) -> pd.DataFrame:
    from .alpaca import get_data

    end = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows, token = [], None
    while True:
        q = {"symbols": ",".join(s.replace("-", ".") for s in symbols), "timeframe": "1Day",
             "start": f"{start}T00:00:00Z", "end": end, "limit": 10000, "feed": "sip", "adjustment": "all",
             **({"page_token": token} if token else {})}
        d = get_data("/v2/stocks/bars", q)
        for sym, bars in (d.get("bars") or {}).items():
            rows += [{"symbol": sym.replace(".", "-"), **b} for b in bars]
        token = d.get("next_page_token")
        if not token:
            break
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["t"], utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})
    return df[["symbol", "date"] + COLUMNS]


def update_bars() -> pd.DataFrame:
    """Everything again each time (one request per 50 symbols): adjusted prices change with
    every split and dividend, so appending would mix two adjustments."""
    syms = members()
    parts = []
    for i in range(0, len(syms), 50):
        parts.append(_bars(syms[i:i + 50], START))
        log.info("daily bars %d/%d", min(i + 50, len(syms)), len(syms))
    df = pd.concat(parts, ignore_index=True)
    WIDE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(WIDE_DIR / "daily.csv.gz", index=False)
    return df


def load_daily(min_days: int = 500) -> dict[str, pd.DataFrame]:
    df = pd.read_csv(WIDE_DIR / "daily.csv.gz", parse_dates=["date"])
    out = {}
    for sym, g in df.groupby("symbol"):
        g = g.set_index("date").sort_index()[COLUMNS]
        g.index.name = "Date"
        if len(g) >= min_days and (g["Close"] > 0).all():
            out[sym] = g
    return out


# ------------------------------------------------------------------ SEC insider trades (bulk)

def quarters(start: str = START) -> list[str]:
    q = pd.period_range(start, pd.Timestamp.now(), freq="Q")
    return [f"{p.year}q{p.quarter}" for p in q]


def _read(z: zipfile.ZipFile, name: str, cols: list[str]) -> pd.DataFrame:
    with z.open(name) as f:
        return pd.read_csv(f, sep="\t", usecols=lambda c: c in cols, dtype=str, quoting=3, on_bad_lines="skip")


def parse_quarter(raw: bytes, tickers: set[str]) -> pd.DataFrame:
    """Open-market purchases / sales of common stock in one quarterly zip, for our tickers."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    sub = _read(z, "SUBMISSION.tsv", ["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE",
                                      "ISSUERTRADINGSYMBOL", "AFF10B5ONE"])
    sub = sub[sub["DOCUMENT_TYPE"].isin(["4", "4/A"])]
    sub["ticker"] = sub["ISSUERTRADINGSYMBOL"].fillna("").str.upper().str.strip().str.replace(".", "-", regex=False)
    sub = sub[sub["ticker"].isin(tickers)]
    tr = _read(z, "NONDERIV_TRANS.tsv", ["ACCESSION_NUMBER", "TRANS_CODE", "TRANS_SHARES",
                                         "TRANS_PRICEPERSHARE", "SECURITY_TITLE", "TRANS_DATE"])
    tr = tr[tr["TRANS_CODE"].isin(["P", "S"])]
    own = _read(z, "REPORTINGOWNER.tsv", ["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNER_RELATIONSHIP",
                                          "RPTOWNER_TITLE"])
    own = own.drop_duplicates("ACCESSION_NUMBER")  # first reporting owner of the filing
    df = tr.merge(sub, on="ACCESSION_NUMBER").merge(own, on="ACCESSION_NUMBER", how="left")
    if df.empty:
        return pd.DataFrame()
    shares = pd.to_numeric(df["TRANS_SHARES"], errors="coerce")
    price = pd.to_numeric(df["TRANS_PRICEPERSHARE"], errors="coerce")
    return pd.DataFrame({
        "accession": df["ACCESSION_NUMBER"],
        "filed": pd.to_datetime(df["FILING_DATE"], format="%d-%b-%Y", errors="coerce"),
        "traded": pd.to_datetime(df["TRANS_DATE"], format="%d-%b-%Y", errors="coerce"),
        "ticker": df["ticker"], "owner": df["RPTOWNERCIK"], "role": df["RPTOWNER_RELATIONSHIP"],
        "title": df["RPTOWNER_TITLE"], "code": df["TRANS_CODE"], "shares": shares, "price": price,
        "value": shares * price, "plan": (df.get("AFF10B5ONE", pd.Series("0", df.index)).fillna("0")  # flag exists since 2023
                 .isin(["1", "true", "True"])).astype(int),
    }).dropna(subset=["filed"])


def update_insider() -> pd.DataFrame:
    """Each quarter's zip once (the SEC publishes a quarter a few weeks after it ends; the
    latest quarters are re-tried until they appear)."""
    path = WIDE_DIR / "insider.csv.gz"
    old = pd.read_csv(path, parse_dates=["filed", "traded"]) if path.exists() else pd.DataFrame()
    done_path = WIDE_DIR / "insider_quarters.txt"
    done = set(done_path.read_text().split()) if done_path.exists() else set()
    tickers = set(members())
    new = []
    for q in quarters():
        if q in done:
            continue
        try:
            raw = _get(SEC_BULK.format(q=q), UA)
        except OSError as exc:
            log.info("%s not published yet (%s)", q, exc)
            continue
        part = parse_quarter(raw, tickers)
        log.info("%s: %d open-market trades", q, len(part))
        new.append(part)
        done.add(q)
        time.sleep(0.5)
    if new:
        df = pd.concat([old] + new, ignore_index=True).drop_duplicates()
        WIDE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        done_path.write_text("\n".join(sorted(done)) + "\n")
        return df
    return old


def load_insider() -> pd.DataFrame:
    path = WIDE_DIR / "insider.csv.gz"
    return pd.read_csv(path, parse_dates=["filed", "traded"]) if path.exists() else pd.DataFrame()


def costs(symbols) -> dict:
    """Large US stocks: no commission at Alpaca, regulatory fees on sales, ~5 bps slippage at the open."""
    from .engine import Costs

    return {s: Costs(fee_bps=0.2, slippage_bps=5, short_borrow_apr=0.01) for s in symbols}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    m = members(refresh=True)
    print(f"{len(m)} members")
    ins = update_insider()
    print(f"insider: {len(ins)} trades, {int((ins['code'] == 'P').sum()) if len(ins) else 0} open-market purchases")
    d = update_bars()
    print(f"daily bars: {d['symbol'].nunique()} symbols, {len(d)} rows")


if __name__ == "__main__":
    main()
