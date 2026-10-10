"""Wide research universe: the S&P 1500 (large, mid and small companies) on daily bars, plus every
insider trade the SEC published.

    python -m algo.wide            # download / update members, daily bars and insider trades

Research only (the strategy finder): nothing here trades. The live accounts keep their own
universe; a strategy found here would first go through the finder's gates and the vault.

- members      today's S&P 500, 400 and 600 lists (Wikipedia), with sector and index. Survivorship bias: companies that fell out of
               the index since 2016 are missing, which flatters any long strategy. The finder
               measures every signal against the same stocks' ordinary drift and against random
               entries on the same stocks, which removes most of that bias from the comparison.
- daily bars   Alpaca, split- and dividend-adjusted, 2016 -> now, data/wide/daily.csv.gz
               (not committed: about 30 MB; GitHub caches it between runs)
- insider      SEC "Insider Transactions Data Sets" (every Form 4 of every company, one zip per
               quarter): open-market purchases (P) and sales (S) of common stock, by filing date.
               data/wide/insider.csv.gz (not committed; GitHub caches it, a full download takes ~5 min).
               Point in time: the filing date. A Form 4 can be accepted up to 22:00 New York, so
               a strategy may only act on it from the NEXT session (the finder's signals fire on
               the filing day's close and fill at the next open, which is exactly that).
"""
from __future__ import annotations

import io
import json
import logging
import os
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

INDEXES = ("500", "400", "600")  # large, mid and small companies (S&P 1500)


def _members_table(index: str) -> pd.DataFrame:
    html = _get(f"https://en.wikipedia.org/wiki/List_of_S%26P_{index}_companies").decode()
    t = next(t for t in pd.read_html(io.StringIO(html)) if {"Symbol", "GICS Sector"} <= set(t.columns) and len(t) > 300)
    return pd.DataFrame({"symbol": t["Symbol"].astype(str).str.replace(".", "-", regex=False),
                         "sector": t["GICS Sector"], "index": f"sp{index}"})


def _table() -> pd.DataFrame:
    m = pd.read_csv(WIDE_DIR / "members.csv")
    if "index" not in m:  # file from before the S&P 400 / 600 were added
        m["index"] = "sp500"
    return m


def members(refresh: bool = False) -> list[str]:
    path = WIDE_DIR / "members.csv"
    if path.exists() and not refresh:
        return _table()["symbol"].tolist()
    out = pd.concat([_members_table(i) for i in INDEXES]).drop_duplicates("symbol")
    WIDE_DIR.mkdir(parents=True, exist_ok=True)
    out.sort_values("symbol").to_csv(path, index=False)
    return out["symbol"].tolist()


def sectors() -> dict[str, str]:
    m = _table()
    return dict(zip(m["symbol"], m["sector"]))


def index_of() -> dict[str, str]:
    m = _table()
    return dict(zip(m["symbol"], m["index"]))


def segment(name: str):
    """Which stocks a strategy trades: "all" = the S&P 500 (the first research universe, kept so
    earlier results keep their meaning), sp400 / sp600 / sp1500, or one sector ("sector:Energy")."""
    idx, sec = index_of(), sectors()
    if name == "all":
        return lambda a: idx.get(a) == "sp500"
    if name == "sp1500":
        return lambda a: a in idx
    if name.startswith("sector:"):
        return lambda a: sec.get(a) == name[7:]
    return lambda a: idx.get(a) == name


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
        # days without a single trade (e.g. SMCI while delisted in 2018-2020: a frozen quote) could not
        # be traded, and their zero range would make the volatility, hence 1R, close to nothing
        g = g[g["Volume"] > 0]
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
    import hashlib

    stamp = "members:" + hashlib.sha1(",".join(sorted(tickers)).encode()).hexdigest()[:12]
    if stamp not in done:  # the stock list changed: every quarter again, for the new list
        old, done = pd.DataFrame(), set()
    done.add(stamp)
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


def _read_trades(path) -> pd.DataFrame:
    """A stored trades file with real dates (older files can mix '2026-05-22' and '2026-05-22 00:00:00')."""
    df = pd.read_csv(path)
    for col in ("filed", "traded"):
        if col in df:
            df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")
    return df


def recent_paths(name: str = "insider_recent"):
    """The recent-filings file and its days-read file. Each universe has its own pair (insider_recent:
    Industrials, account E; insider_recent_all: the S&P 1500, account D): a day read for one universe
    is not read for another."""
    return WIDE_DIR / f"{name}.csv.gz", WIDE_DIR / f"{name}_days.txt"


def merge_insider_recent(other_csv, other_days, name: str = "insider_recent") -> int:
    """Union of another copy of the recent filings (e.g. a backfill run's) with ours: rows and days
    read. Used when two runs saved the file at the same time (a binary file git cannot merge)."""
    path, done_path = recent_paths(name)
    parts = [_read_trades(p) for p in (path, other_csv) if os.path.exists(p)]
    df = pd.concat(parts, ignore_index=True).drop_duplicates(["accession", "owner", "code", "shares", "price"])
    df.sort_values("filed").to_csv(path, index=False)
    days = set()
    for p in (done_path, other_days):
        if os.path.exists(p):
            days |= set(open(p).read().split())
    done_path.write_text("\n".join(sorted(days)) + "\n")
    return len(df)


def load_insider() -> pd.DataFrame:
    """Quarterly SEC data sets plus the recent filings not in a published quarter yet."""
    files = [WIDE_DIR / "insider.csv.gz"] + sorted(WIDE_DIR.glob("insider_recent*.csv.gz"))
    parts = [_read_trades(p) for p in files if p.exists()]
    if not parts:
        return pd.DataFrame()
    df = pd.concat(parts, ignore_index=True)
    return df.drop_duplicates(["accession", "owner", "code", "shares", "price"])


def _bulk_end() -> pd.Timestamp:
    done_path = WIDE_DIR / "insider_quarters.txt"
    qs = [q for q in (done_path.read_text().split() if done_path.exists() else []) if "q" in q]
    if not qs:
        return pd.Timestamp(START)
    return pd.Period(max(qs).replace("q", "Q"), freq="Q").end_time.normalize()


def _sec(url: str) -> bytes:
    """The SEC blocks bursts (HTTP 403 for a few minutes): slower pace, long waits on a refusal."""
    from . import insider as ins

    # SEC_PATIENT=1 (the backfill workflow): keep waiting out the blocks (they last ~10 minutes)
    waits = (0, 60, 180, 600) + ((600,) * 12 if os.environ.get("SEC_PATIENT") else ())
    for wait in waits:
        if wait:
            log.info("SEC asks to slow down: waiting %ds", wait)
            time.sleep(wait)
        try:
            time.sleep(float(os.environ.get("SEC_PACE", "0.25")))  # the SEC blocks sustained bursts for minutes
            return ins._get(url)
        except OSError as exc:
            if "403" not in str(exc) and "429" not in str(exc):
                raise
    raise OSError(f"SEC refused {url}")


def update_insider_recent(days: int | None = None, tickers=None, name: str = "insider_recent") -> pd.DataFrame:
    """Form 4 filings since the last published quarter, from the SEC's daily indexes: the filings of
    our companies (issuer CIK), parsed like the insider module (open-market P / S). Days already read
    are kept in data/wide/<name>_days.txt (see recent_paths)."""
    from . import insider as ins

    path, done_path = recent_paths(name)
    old = _read_trades(path) if path.exists() else pd.DataFrame()
    done = set(done_path.read_text().split()) if done_path.exists() else set()
    cik_to_ticker = {}
    ins.cik("AAPL")  # makes sure company_tickers.json is there
    for row in json.loads((ins.INSIDER_DIR / "company_tickers.json").read_text()).values():
        cik_to_ticker.setdefault(int(row["cik_str"]), row["ticker"].replace(".", "-"))
    ours = set(tickers) if tickers is not None else set(members())
    start = _bulk_end() + pd.Timedelta(days=1)
    today = pd.Timestamp.now(tz="America/New_York").tz_localize(None).normalize()
    days_ = pd.bdate_range(start if days is None else today - pd.Timedelta(days=days), today)
    rows = []

    def save():
        new = pd.DataFrame(rows)
        df = pd.concat([old, new], ignore_index=True) if len(new) else old
        if len(df):
            df = df.drop_duplicates(["accession", "owner", "code", "shares", "price"])
            df["filed"] = pd.to_datetime(df["filed"], format="mixed")
            df = df[df["filed"] > _bulk_end()]  # covered by a published quarter now
            WIDE_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
        done_path.write_text("\n".join(sorted(done)) + "\n")
        return df

    listed: dict[tuple, set | None] = {}

    def published(d) -> bool | None:
        """Is the day's index on the SEC's quarter listing? (a missing day, e.g. a holiday, answers
        403 like a block would). None when the listing itself cannot be read."""
        yq = (d.year, (d.month - 1) // 3 + 1)
        if yq not in listed:
            try:
                items = json.loads(_sec(f"https://www.sec.gov/Archives/edgar/daily-index/{yq[0]}/QTR{yq[1]}/index.json"))
                listed[yq] = {i["name"] for i in items["directory"]["item"]}
            except (OSError, ValueError, KeyError):
                listed[yq] = None
        return None if listed[yq] is None else f"form.{d:%Y%m%d}.idx" in listed[yq]

    for d in days_:
        key = d.strftime("%Y%m%d")
        if key in done and d < today - pd.Timedelta(days=3):  # the last days are read again (late index)
            continue
        q = (d.month - 1) // 3 + 1
        if published(d) is False:
            if d < today - pd.Timedelta(days=5):
                done.add(key)  # a holiday: no index will come
            continue
        try:
            raw = _sec(f"https://www.sec.gov/Archives/edgar/daily-index/{d.year}/QTR{q}/form.{key}.idx")
        except OSError as exc:
            if "refused" in str(exc):  # still blocked after the long waits: keep what we have, next run goes on
                log.warning("SEC keeps refusing: stopping at %s, progress saved", key)
                return save()
            continue  # holiday / not published yet
        seen = set()
        for line in raw.decode("latin-1").splitlines():
            if not line.startswith("4 "):
                continue
            parts = line.split()
            fname = parts[-1]
            try:
                cik = int(parts[-3])
            except ValueError:
                continue
            tick = cik_to_ticker.get(cik)
            acc = fname.rsplit("/", 1)[-1].replace(".txt", "")
            if tick not in ours or acc in seen:
                continue
            seen.add(acc)
            try:
                xml = _sec(f"https://www.sec.gov/Archives/{fname}").decode("utf-8", "replace")
            except OSError as exc:
                if "refused" in str(exc):
                    log.warning("SEC keeps refusing: stopping in %s, progress saved", key)
                    return save()  # this day is not marked done: read again next run
                continue
            issuer = (ins._tag(xml, "issuerTradingSymbol") or tick).upper().replace(".", "-")
            role = "Officer" if ins._tag(xml, "isOfficer") in ("1", "true") else (
                "Director" if ins._tag(xml, "isDirector") in ("1", "true") else "")
            for r in ins.parse(xml):
                rows.append({"accession": acc, "filed": d, "traded": pd.NaT, "ticker": issuer, "owner": r["owner"],
                             "role": role, "title": ins._tag(xml, "officerTitle"), "code": r["code"],
                             "shares": r["shares"], "price": r["price"], "value": r["value"], "plan": r["plan"]})
        done.add(key)
        log.info("Form 4 %s: %d of our companies' filings", key, len(seen))
        save()  # after every day: an interruption loses nothing
    return save()


SLIPPAGE_BPS = {"sp500": 5, "sp400": 8, "sp600": 15}  # smaller companies: wider spreads at the open


# ------------------------------------------------------------------ earnings dates (SEC 8-K item 2.02)

def _earnings_of(ticker: str) -> list[str]:
    """Acceptance times (UTC) of every earnings release (8-K with item 2.02) since START."""
    from .insider import _get, cik

    try:
        c = cik(ticker)  # the SEC writes BRK-B like us
    except KeyError:
        c = cik(ticker.replace("-", "."))
    d = json.loads(_get(f"https://data.sec.gov/submissions/CIK{c:010d}.json"))
    parts = [d["filings"]["recent"]]
    for f in d["filings"].get("files", []):
        if f.get("filingTo", "9999") >= START:
            parts.append(json.loads(_get(f"https://data.sec.gov/submissions/{f['name']}")))
    out = []
    for p in parts:
        for i, form in enumerate(p["form"]):
            if form in ("8-K", "8-K/A") and "2.02" in (p["items"][i] or "") and p["filingDate"][i] >= START:
                out.append(p["acceptanceDateTime"][i])
    return out


def update_earnings(refresh: bool = False) -> pd.DataFrame:
    """data/wide/earnings.csv.gz: one row per earnings release (ticker, accepted UTC). Tickers already
    done are only refreshed when the file is a week old (a quarter brings one new date each)."""
    path = WIDE_DIR / "earnings.csv.gz"
    old = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=["ticker", "accepted"])
    stale = refresh or not path.exists() or time.time() - path.stat().st_mtime > 7 * 86400
    todo = members() if stale else [t for t in members() if t not in set(old["ticker"])]
    rows, failed = [], 0
    for n, t in enumerate(todo, 1):
        try:
            rows += [{"ticker": t, "accepted": a} for a in _earnings_of(t)]
        except (KeyError, OSError, ValueError) as exc:
            failed += 1
            log.debug("no earnings for %s (%s)", t, exc)
        if n % 200 == 0:
            log.info("earnings dates %d/%d", n, len(todo))
    new = pd.DataFrame(rows, columns=["ticker", "accepted"])
    df = pd.concat([old[~old["ticker"].isin(todo)], new], ignore_index=True).drop_duplicates()
    WIDE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    log.info("earnings: %d releases, %d tickers (%d without SEC filings)", len(df), df["ticker"].nunique(), failed)
    return df


def load_earnings() -> pd.DataFrame:
    path = WIDE_DIR / "earnings.csv.gz"
    if not path.exists():
        return pd.DataFrame(columns=["ticker", "accepted", "day"])
    df = pd.read_csv(path)
    ny = pd.to_datetime(df["accepted"], utc=True).dt.tz_convert("America/New_York")
    # the first session that can react: the same day if released before the 9:30 open, else the next
    before_open = (ny.dt.hour < 9) | ((ny.dt.hour == 9) & (ny.dt.minute < 30))
    day = ny.dt.tz_localize(None).dt.normalize()
    df["day"] = day.where(before_open, day + pd.Timedelta(days=1))
    return df


# ------------------------------------------------------------------ short selling (FINRA, free)

FINRA_SHORT = "https://cdn.finra.org/equity/regsho/daily/{feed}shvol{day}.txt"
SHORT_FEEDS = ("FNSQ", "FNYX")  # the Nasdaq and NYSE trade reporting facilities: off-exchange volume, from 2016


def _short_day(day: str, tickers: set[str]) -> pd.DataFrame | None:
    """Short and total volume per stock reported that day (None: no file, e.g. a holiday)."""
    parts = []
    for feed in SHORT_FEEDS:
        try:
            raw = _get(FINRA_SHORT.format(feed=feed, day=day), tries=2).decode("utf-8", "replace")
        except OSError:
            return None
        df = pd.read_csv(io.StringIO(raw), sep="|", usecols=["Symbol", "ShortVolume", "TotalVolume"],
                         dtype={"Symbol": str})
        parts.append(df[df["Symbol"].isin(tickers)])
    df = pd.concat(parts).groupby("Symbol")[["ShortVolume", "TotalVolume"]].sum().reset_index()
    if df.empty:
        return None
    return df.rename(columns={"Symbol": "ticker", "ShortVolume": "short", "TotalVolume": "total"}).assign(date=day)


def update_short_volume(start: str = START, name: str = "short_volume", keep_days: int | None = None) -> pd.DataFrame:
    """FINRA daily short sale volume of the S&P 1500 (published each evening for that day): one row per
    stock and day. Downloads only the days not stored yet. name="short_volume_recent", keep_days=150:
    the small rolling copy kept in git for the trading jobs (the full history lives in the finder's cache)."""
    from concurrent.futures import ThreadPoolExecutor

    path, done_path = WIDE_DIR / f"{name}.csv.gz", WIDE_DIR / f"{name}_days.txt"
    old = pd.read_csv(path, dtype={"date": str}) if path.exists() else pd.DataFrame()
    done = set(done_path.read_text().split()) if done_path.exists() else set()
    tickers = set(members())
    days = [d.strftime("%Y%m%d") for d in pd.bdate_range(start, pd.Timestamp.now(tz="America/New_York").tz_localize(None))]
    todo = [d for d in days if d not in done]
    recent = (pd.Timestamp.now() - pd.Timedelta(days=5)).strftime("%Y%m%d")
    rows = []
    with ThreadPoolExecutor(6) as ex:
        for d, df in zip(todo, ex.map(lambda d: _short_day(d, tickers), todo)):
            if df is not None:
                rows.append(df)
                done.add(d)
            elif d < recent:
                done.add(d)  # holiday: no file will come
    if keep_days is not None:
        cut = (pd.Timestamp.now() - pd.Timedelta(days=keep_days)).strftime("%Y%m%d")
        done = {d for d in done if d >= cut}
        if len(old):
            old = old[old["date"].astype(str) >= cut]
    if rows or (keep_days is not None and len(old)):
        old = pd.concat([old, *rows], ignore_index=True).drop_duplicates(["date", "ticker"], keep="last")
        WIDE_DIR.mkdir(parents=True, exist_ok=True)
        old.sort_values(["date", "ticker"]).to_csv(path, index=False)
    done_path.write_text("\n".join(sorted(done)) + "\n")
    log.info("short volume: %d new days, %d rows", len(rows), len(old))
    return old


def load_short_volume() -> pd.DataFrame:
    """Short share of off-exchange volume per (day, stock) as a wide table, usable from the NEXT session
    (FINRA publishes it after the close)."""
    parts = [pd.read_csv(p, dtype={"date": str}) for p in (WIDE_DIR / "short_volume.csv.gz",
                                                          WIDE_DIR / "short_volume_recent.csv.gz") if p.exists()]
    if not parts:
        return pd.DataFrame()
    df = pd.concat(parts, ignore_index=True).drop_duplicates(["date", "ticker"], keep="last")
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["total"] > 0]
    return (df.assign(ratio=df["short"] / df["total"]).pivot(index="date", columns="ticker", values="ratio")
            .sort_index())


def costs(symbols) -> dict:
    """US stocks: no commission at Alpaca, regulatory fees on sales, slippage by company size."""
    from .engine import Costs

    idx = index_of()
    return {s: Costs(fee_bps=0.2, slippage_bps=SLIPPAGE_BPS.get(idx.get(s), 15), short_borrow_apr=0.01)
            for s in symbols}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    m = members(refresh=True)
    print(f"{len(m)} members")
    ins = update_insider()
    print(f"insider: {len(ins)} trades, {int((ins['code'] == 'P').sum()) if len(ins) else 0} open-market purchases")
    d = update_bars()
    print(f"daily bars: {d['symbol'].nunique()} symbols, {len(d)} rows")
    r = update_insider_recent()
    print(f"recent insider filings (after the last published quarter): {len(r)} trades")
    sv = update_short_volume()
    print(f"short volume: {len(sv)} rows")
    e = update_earnings()
    print(f"earnings releases: {len(e)} for {e['ticker'].nunique()} tickers")


if __name__ == "__main__":
    main()
