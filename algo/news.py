"""News and scheduled events, all point-in-time.

Three sources, each usable in a backtest without hindsight:
- GDELT (global news database): daily article count and average tone for
  each asset since 2017. Tone is computed when articles are published, so it
  never knows what happened next. Values for day D are only used from D+1.
- Earnings dates (Yahoo): announced weeks in advance.
- FOMC meeting dates (federalreserve.gov): published a year in advance.
  US jobs report: first Friday of the month (rule, may be off on holidays).

Live headlines for the daily brief come from Yahoo Finance RSS.
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

from .data import DATA_DIR, TICKERS

log = logging.getLogger(__name__)
NEWS_DIR = DATA_DIR / "news"
UA = {"User-Agent": "Mozilla/5.0 (research backtest)"}

# GDELT search terms. Kept specific so "solana" or "gold" do not match unrelated stories.
QUERIES = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": '"solana" crypto',
    "NVDA": "nvidia",
    "TSLA": "tesla",
    "GOLD": '"gold price"',
    "SILVER": '"silver price"',
    "MACRO": '"federal reserve"',
}
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_START = "2017-01-01"
_last_call = [0.0]


def _get(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _gdelt(query: str, mode: str, start: str, end: str) -> pd.Series:
    params = {"query": query, "mode": mode, "format": "json",
              "startdatetime": pd.Timestamp(start).strftime("%Y%m%d%H%M%S"),
              "enddatetime": pd.Timestamp(end).strftime("%Y%m%d%H%M%S")}
    url = GDELT_URL + "?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        wait = 6.0 - (time.time() - _last_call[0])  # GDELT allows one request per 5 s
        if wait > 0:
            time.sleep(wait)
        _last_call[0] = time.time()
        try:
            body = json.loads(_get(url))
            data = body["timeline"][0]["data"] if body.get("timeline") else []
            return pd.Series({pd.Timestamp(d["date"][:8]): float(d["value"]) for d in data}, dtype=float)
        except (json.JSONDecodeError, OSError) as exc:
            log.info("GDELT retry %d for %s (%s)", attempt + 1, query, exc)
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"GDELT unavailable for {query}")


def load_gdelt(name: str, refresh: bool = False, end: str | None = None) -> pd.DataFrame:
    """Daily article count and average tone for one asset, cached in data/news/.
    With a cache present, only the missing recent days are fetched."""
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    path = NEWS_DIR / f"{name}_gdelt.csv"
    end = end or str(pd.Timestamp.utcnow().tz_localize(None).normalize())
    old = pd.read_csv(path, index_col=0, parse_dates=True) if path.exists() else None
    if old is not None and not refresh:
        if old.index[-1] >= pd.Timestamp(end) - pd.Timedelta(days=1):
            return old
        start = str(old.index[-1] - pd.Timedelta(days=3))
    else:
        start = GDELT_START
    q = QUERIES[name]
    df = pd.DataFrame({"articles": _gdelt(q, "timelinevolraw", start, end),
                       "tone": _gdelt(q, "timelinetone", start, end)})
    if old is not None and not refresh:
        df = pd.concat([old[old.index < df.index.min()], df]) if len(df) else old
    df.index.name = "Date"
    df.to_csv(path)
    return df


def news_features(gd: pd.DataFrame, index: pd.DatetimeIndex) -> pd.DataFrame:
    """Per-bar news features, lagged one day so a bar only sees finished news days.

    tone_z:      7-day average tone vs its last 180 days (z-score)
    attention_z: 3-day article count vs its last 90 days (z-score, log scale)
    """
    g = gd.sort_index().asfreq("D")
    tone7 = g["tone"].rolling(7, min_periods=4).mean()
    tone_z = (tone7 - tone7.rolling(180, min_periods=60).mean()) / tone7.rolling(180, min_periods=60).std()
    vol = np.log1p(g["articles"].fillna(0)).rolling(3, min_periods=2).mean()
    att_z = (vol - vol.rolling(90, min_periods=30).mean()) / vol.rolling(90, min_periods=30).std()
    f = pd.DataFrame({"tone_z": tone_z, "attention_z": att_z}).shift(1)  # day D usable from D+1
    day = index.normalize()
    out = f.reindex(day)
    out.index = index
    return out


# ---------------------------------------------------------------- events


def fomc_dates(refresh: bool = False) -> list[pd.Timestamp]:
    """Scheduled FOMC decision days (the last day of each meeting), 2016 onwards."""
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    path = NEWS_DIR / "fomc.csv"
    if path.exists() and not refresh:
        return list(pd.to_datetime(pd.read_csv(path)["date"]))
    months = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                          "September", "October", "November", "December"], 1)}
    short = {k[:3]: v for k, v in months.items()}

    def decision_day(year: int, month_txt: str, days_txt: str) -> pd.Timestamp | None:
        if "(" in days_txt or "unscheduled" in days_txt.lower():
            return None  # notation votes and emergency calls are not scheduled events
        last_month = month_txt.split("/")[-1].strip()
        m = months.get(last_month) or short.get(last_month[:3])
        d = re.findall(r"\d+", days_txt)
        return pd.Timestamp(year, m, int(d[-1])) if m and d else None

    dates = []
    html = _get("https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm")
    for mm in re.finditer(r"(\d{4}) FOMC Meetings(.*?)(?=\d{4} FOMC Meetings|$)", html, re.S):
        y, body = int(mm.group(1)), mm.group(2)
        ms = re.findall(r"fomc-meeting__month[^>]*>\s*<strong>([^<]+)</strong>", body)
        ds = re.findall(r"fomc-meeting__date[^>]*>([^<]+)<", body)
        dates += [decision_day(y, m, d) for m, d in zip(ms, ds)]
    for y in range(2016, 2021):
        html = _get(f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm")
        for m, d in re.findall(r"<h5[^>]*>\s*([A-Za-z/]+)\s+([\d\-]+)\s+Meeting - \d{4}", html):
            dates.append(decision_day(y, m, d))
    dates = sorted({d for d in dates if d is not None})
    pd.DataFrame({"date": dates}).to_csv(path, index=False)
    return dates


def jobs_report_dates(start="2016-01-01", end="2027-12-31") -> list[pd.Timestamp]:
    """US employment report: first Friday of each month (approximation)."""
    fridays = pd.date_range(start, end, freq="W-FRI")
    return list(pd.Series(fridays).groupby([fridays.year, fridays.month]).min())


def earnings_dates(name: str, refresh: bool = False) -> list[pd.Timestamp]:
    """Past and next scheduled earnings dates for a stock (empty for crypto/metals)."""
    if name not in ("NVDA", "TSLA") and not name.isalpha():
        return []
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    path = NEWS_DIR / f"{name}_earnings.csv"
    if path.exists() and not refresh:
        return list(pd.to_datetime(pd.read_csv(path)["date"]))
    import yfinance as yf

    try:
        e = yf.Ticker(TICKERS.get(name, name)).get_earnings_dates(limit=60)
    except Exception as exc:  # no earnings for ETFs / crypto
        log.info("no earnings dates for %s (%s)", name, exc)
        return []
    if e is None or e.empty:
        return []
    dates = sorted({pd.Timestamp(d).tz_convert("America/New_York").tz_localize(None).normalize() for d in e.index})
    pd.DataFrame({"date": dates}).to_csv(path, index=False)
    return dates


def event_features(index: pd.DatetimeIndex, earnings: list, fomc: list, jobs: list) -> pd.DataFrame:
    """Days until the next scheduled event, as known at each bar (dates are public in advance)."""
    day = index.normalize()

    def days_to_next(events) -> np.ndarray:
        if not events:
            return np.full(len(day), np.inf)
        ev = np.array(sorted(pd.DatetimeIndex(events).normalize()), dtype="datetime64[D]")
        d = day.to_numpy().astype("datetime64[D]")
        pos = np.searchsorted(ev, d)  # next event on or after today
        out = np.full(len(d), np.inf)
        ok = pos < len(ev)
        out[ok] = (ev[pos[ok]] - d[ok]).astype(int)
        return out

    return pd.DataFrame({"days_to_earnings": days_to_next(earnings), "days_to_fomc": days_to_next(fomc),
                         "days_to_jobs": days_to_next(jobs)}, index=index)


# ---------------------------------------------------------------- live headlines


def headlines(name: str, limit: int = 8) -> list[dict]:
    """Latest headlines for an asset from Yahoo Finance RSS."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={urllib.parse.quote(TICKERS.get(name, name))}"
    try:
        root = ET.fromstring(_get(url, timeout=20))
    except Exception as exc:
        log.warning("headlines unavailable for %s (%s)", name, exc)
        return []
    items = []
    for it in root.iter("item"):
        items.append({"title": (it.findtext("title") or "").strip(), "link": it.findtext("link"),
                      "published": it.findtext("pubDate")})
    return items[:limit]


def load_all(assets, refresh: bool = False, strict: bool = False) -> dict:
    """Everything the system needs, per asset, cached.
    strict: raise if an asset's news is missing, instead of going on without it
    (live trading: a missing input must not silently change the positions)."""
    fomc = fomc_dates(refresh)
    jobs = jobs_report_dates()
    out = {"fomc": fomc, "jobs": jobs, "gdelt": {}, "earnings": {}}
    for a in list(assets) + ["MACRO"]:
        try:
            out["gdelt"][a] = load_gdelt(a, refresh)
        except Exception as exc:
            if strict:
                raise RuntimeError(f"no GDELT news for {a}; not trading on incomplete inputs") from exc
            log.warning("no GDELT data for %s (%s)", a, exc)
    for a in assets:
        out["earnings"][a] = earnings_dates(a, refresh) if a in ("NVDA", "TSLA") else []
    return out


def cached(path: Path) -> bool:
    return path.exists()
