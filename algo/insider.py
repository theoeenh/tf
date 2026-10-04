"""Insider trades from the SEC (Form 4): free, official, filed within two business days.

    python -m algo.insider          # download / update data/insider/<asset>.csv for the stocks

Executives, directors and 10% owners must report every trade in their company's
stock. Open-market purchases (code P) are the classic signal: insiders sell for
many reasons (taxes, diversification, planned 10b5-1 sales) but buy for one.

Point in time: a trade is only known once the filing is accepted by the SEC
(`accepted`, UTC), often days after the trade itself. Features use that time.

Features per bar (only for the stocks; ETFs, crypto and foreign ADRs have none):
  insider_buyers_90d   distinct insiders who bought in the open market, last 90 days
  insider_buy_90d      log(1 + $ bought in the open market), last 90 days
  insider_sell_30d     log(1 + $ of discretionary sales, i.e. not under a 10b5-1 plan), last 30 days
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.request

import numpy as np
import pandas as pd

from .data import ASSET_CLASS, DATA_DIR

log = logging.getLogger(__name__)
INSIDER_DIR = DATA_DIR / "insider"
START = "2022-10-01"  # 90 days before the hourly history starts
UA = {"User-Agent": "tf-research theoeenhoorn@gmail.com"}  # the SEC asks for a contact in the user agent
FOREIGN = {"TSM", "ASML", "SAP", "NVO", "TM", "BABA"}  # file 20-F / 6-K, no Form 4
_last = [0.0]
EXTRA_CIKS = {"XOM": [34088]}  # filed under its former registrant until mid-2026


def _get(url: str) -> bytes:
    wait = 0.15 - (time.time() - _last[0])  # SEC limit: 10 requests a second
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read()
        except OSError as exc:
            if attempt == 3:
                raise
            log.info("SEC retry %d (%s)", attempt + 1, exc)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def stocks(assets) -> list[str]:
    return [a for a in assets if ASSET_CLASS.get(a) == "stock" and a not in FOREIGN]


def cik(ticker: str) -> int:
    path = INSIDER_DIR / "company_tickers.json"
    if not path.exists():
        INSIDER_DIR.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_get("https://www.sec.gov/files/company_tickers.json"))
    for row in json.loads(path.read_text()).values():
        if row["ticker"] == ticker:
            return int(row["cik_str"])
    raise KeyError(ticker)


def _filings(c: int) -> pd.DataFrame:
    """Every Form 4 of the company since START: accession, accepted time, document."""
    d = json.loads(_get(f"https://data.sec.gov/submissions/CIK{c:010d}.json"))
    parts = [d["filings"]["recent"]]
    for f in d["filings"].get("files", []):
        if f.get("filingTo", "9999") >= START:
            parts.append(json.loads(_get(f"https://data.sec.gov/submissions/{f['name']}")))
    rows = []
    for p in parts:
        for i, form in enumerate(p["form"]):
            if form == "4" and p["filingDate"][i] >= START:
                rows.append({"accession": p["accessionNumber"][i], "accepted": p["acceptanceDateTime"][i],
                             "doc": p["primaryDocument"][i].split("/")[-1]})
    return pd.DataFrame(rows, columns=["accession", "accepted", "doc"])


def _tag(block: str, name: str) -> str | None:
    m = re.search(rf"<{name}>\s*(?:<value>)?\s*([^<\s][^<]*?)\s*(?:</value>)?\s*</{name}>", block, re.S)
    return m.group(1) if m else None


def parse(xml: str) -> list[dict]:
    """Open-market non-derivative transactions of one Form 4."""
    owner = _tag(xml, "rptOwnerCik")
    plan = _tag(xml, "aff10b5One") in ("1", "true")
    out = []
    for block in re.findall(r"<nonDerivativeTransaction>(.*?)</nonDerivativeTransaction>", xml, re.S):
        code = _tag(block, "transactionCode")
        if code not in ("P", "S"):
            continue
        try:
            shares = float(_tag(block, "transactionShares") or 0)
            price = float(_tag(block, "transactionPricePerShare") or 0)
        except ValueError:
            continue
        foot_plan = "10b5-1" in block
        out.append({"owner": owner, "code": code, "shares": shares, "price": price, "value": shares * price,
                    "plan": int(plan or foot_plan)})
    return out


def update(asset: str) -> pd.DataFrame:
    """Download the Form 4s not seen yet; data/insider/<asset>.csv holds one row per transaction
    (and one empty row per filing without open-market trades, so it is not fetched again)."""
    INSIDER_DIR.mkdir(parents=True, exist_ok=True)
    path = INSIDER_DIR / f"{asset}.csv"
    old = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=["accession"])
    seen = set(old["accession"])
    new = []
    for c, f in [(c, f) for c in [cik(asset)] + EXTRA_CIKS.get(asset, []) for _, f in _filings(c).iterrows()]:
        if f.accession in seen:
            continue
        url = f"https://www.sec.gov/Archives/edgar/data/{c}/{f.accession.replace('-', '')}/{f.doc}"
        try:
            rows = parse(_get(url).decode("utf-8", "replace"))
        except Exception as exc:
            log.warning("Form 4 %s unreadable (%s)", f.accession, exc)
            continue
        base = {"accession": f.accession, "accepted": f.accepted}
        new += [base | r for r in rows] or [base | {"code": "-"}]
    df = pd.concat([old, pd.DataFrame(new)], ignore_index=True) if new else old
    if new:
        df.to_csv(path, index=False)
    log.info("%s: %d new Form 4 filings", asset, len({r['accession'] for r in new}))
    return df


def load(asset: str, refresh: bool = True) -> pd.DataFrame:
    path = INSIDER_DIR / f"{asset}.csv"
    if refresh:
        try:
            return update(asset)
        except Exception as exc:  # the SEC being slow never blocks anything: use what is cached
            log.warning("SEC unavailable for %s (%s); using the cache", asset, exc)
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def features(index: pd.DatetimeIndex, tx: pd.DataFrame) -> pd.DataFrame:
    """Per bar (UTC start time): insider activity known before the bar started."""
    cols = ["insider_buyers_90d", "insider_buy_90d", "insider_sell_30d"]
    out = pd.DataFrame(0.0, index=index, columns=cols)
    if tx.empty or "code" not in tx:
        return out
    t = tx[tx["code"].isin(["P", "S"])].copy()
    if t.empty:
        return out
    t["at"] = pd.to_datetime(t["accepted"], utc=True).dt.tz_convert(None)
    t = t.sort_values("at")
    bars = index.to_numpy()

    def window(sel: pd.DataFrame, days: int, how) -> np.ndarray:
        at = sel["at"].to_numpy()
        lo = np.searchsorted(at, bars - np.timedelta64(days, "D"), side="left")
        hi = np.searchsorted(at, bars, side="left")  # filings accepted before the bar started
        return np.array([how(sel.iloc[a:b]) if b > a else 0.0 for a, b in zip(lo, hi)])

    buys = t[t["code"] == "P"]
    sells = t[(t["code"] == "S") & (t["plan"].fillna(0) == 0)]
    if len(buys):
        out["insider_buyers_90d"] = window(buys, 90, lambda g: g["owner"].nunique())
        out["insider_buy_90d"] = np.log1p(window(buys, 90, lambda g: g["value"].sum()))
    if len(sells):
        out["insider_sell_30d"] = np.log1p(window(sells, 30, lambda g: g["value"].sum()))
    return out


def main() -> None:
    from .system import UNIVERSE_WIDE

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    for a in stocks(UNIVERSE_WIDE):
        df = load(a)
        p = df[df.get("code", pd.Series(dtype=str)) == "P"] if len(df) else df
        print(f"{a}: {df['accession'].nunique() if len(df) else 0} filings, {len(p)} open-market purchases")


if __name__ == "__main__":
    main()
