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

from .data import ALPACA_SYMBOLS, ASSET_CLASS, DATA_DIR, TICKERS

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
    if ASSET_CLASS.get(name) != "stock":
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


def blackout(index: pd.DatetimeIndex, earnings: list, fomc: list, jobs: list, stock: bool) -> pd.Series:
    """Intraday bars (UTC start times) to be flat through, because a scheduled
    event can gap the price through a stop. Dates are public in advance, so
    this uses no future information.

    - Earnings (stocks): the whole report day and the last bar of the session before
      (reports come before the open or after the close).
    - Fed decision (all assets): 13:00-16:00 New York on decision day (14:00 statement,
      press conference after).
    - Jobs report (8:30 New York): crypto 8:00-9:00; stocks the last bar of the session
      before (the gap is at the open).
    """
    ny = index.tz_localize("UTC").tz_convert("America/New_York")
    day = pd.DatetimeIndex(ny.date)
    hour = ny.hour
    out = np.zeros(len(index), bool)

    def last_bar_before(days) -> np.ndarray:
        """Mask of the last bar of each session that comes right before one of `days`."""
        m = np.zeros(len(index), bool)
        uniq = pd.DatetimeIndex(sorted(set(day)))
        days = pd.DatetimeIndex(days)
        pos = np.searchsorted(uniq, days)
        # the session right before (a weekend or holiday in between at most)
        prev = {uniq[p - 1] for p, d in zip(pos, days) if 0 < p and (d - uniq[p - 1]).days <= 4}
        if prev:
            last = pd.Series(np.arange(len(index))).groupby(day).max()
            for d in prev:
                m[last[d]] = True
        return m

    ev = pd.DatetimeIndex(earnings).normalize() if earnings else pd.DatetimeIndex([])
    if stock and len(ev):
        out |= day.isin(ev)
        out |= last_bar_before(ev)
    fed = pd.DatetimeIndex(fomc).normalize()
    out |= day.isin(fed) & (hour >= 13) & (hour < 16)
    jb = pd.DatetimeIndex(jobs).normalize()
    out |= last_bar_before(jb) if stock else (day.isin(jb) & (hour == 8))
    return pd.Series(out, index)


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


def load_all(assets, refresh: bool = False, strict: bool = False, alpaca_news: bool = False) -> dict:
    """Everything the system needs, per asset, cached.
    strict: raise if an asset's news is missing, instead of going on without it
    (live trading: a missing input must not silently change the positions)."""
    fomc = fomc_dates(refresh)
    jobs = jobs_report_dates()
    out = {"fomc": fomc, "jobs": jobs, "gdelt": {}, "earnings": {}}
    for a in [x for x in assets if x in QUERIES] + ["MACRO"]:  # daily tone exists for the core assets only
        try:
            out["gdelt"][a] = load_gdelt(a, refresh)
        except Exception as exc:
            if strict:
                raise RuntimeError(f"no GDELT news for {a}; not trading on incomplete inputs") from exc
            log.warning("no GDELT data for %s (%s)", a, exc)
    for a in assets:
        out["earnings"][a] = earnings_dates(a, refresh) if ASSET_CLASS.get(a) == "stock" else []
    if alpaca_news:  # hourly: Alpaca / Benzinga articles with exact times
        out["alpaca_news"] = {}
        for a in assets:
            try:
                out["alpaca_news"][a] = load_alpaca_news(a)
            except Exception as exc:
                if strict:
                    raise RuntimeError(f"no Alpaca news for {a}; not trading on incomplete inputs") from exc
                log.warning("no Alpaca news for %s (%s)", a, exc)
    return out


def cached(path: Path) -> bool:
    return path.exists()


# ---------------------------------------------------------------- Alpaca (Benzinga) news, hourly

ALPACA_NEWS_SYMBOLS = {a: sym.replace("/", "") for a, sym in ALPACA_SYMBOLS.items() if a != "SPY"}
# A small finance word list (in the spirit of Loughran-McDonald): headline tone = (pos - neg) / words hit.
POSITIVE = set("""beat beats surge surges soar soars jump jumps rally rallies gain gains record upgrade upgraded
upgrades bullish outperform strong stronger growth boost boosts rise rises rising higher approval approved
wins win profit profitable exceed exceeds exceeded raise raises raised buy breakout expands expansion
optimistic tops top rebound rebounds recovery inflows partnership launch launches accelerate""".split())
NEGATIVE = set("""miss misses plunge plunges drop drops fall falls falling sink sinks slump slumps tumble tumbles
crash crashes downgrade downgraded downgrades bearish underperform weak weaker loss losses lawsuit probe
investigation recall recalls cut cuts cutting lower decline declines warning warns fraud risk risks selloff
sell-off outflows ban bans delay delays halt halts fine fined layoffs slowdown fear fears concern concerns
default hack hacked exploit liquidation liquidations""".split())


def headline_score(text: str) -> float:
    words = re.findall(r"[a-z\-]+", (text or "").lower())
    pos = sum(w in POSITIVE for w in words)
    neg = sum(w in NEGATIVE for w in words)
    return (pos - neg) / (pos + neg) if pos + neg else 0.0


def load_alpaca_news(name: str, start: str = "2023-01-01", refresh: bool = False) -> pd.DataFrame:
    """Every Alpaca/Benzinga article tagged with the asset: time (UTC) and tone
    score (no text is kept). Cached in data/news/<name>_alpaca_news.csv (not in
    git), only new articles fetched."""
    from .alpaca import get_data

    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    path = NEWS_DIR / f"{name}_alpaca_news.csv"
    old = None if refresh or not path.exists() else pd.read_csv(path, parse_dates=["time"])
    since = pd.Timestamp(start) if old is None or old.empty else old["time"].max() - pd.Timedelta(hours=1)
    rows, token = [], None
    while True:
        q = {"symbols": ALPACA_NEWS_SYMBOLS[name], "start": since.strftime("%Y-%m-%dT%H:%M:%SZ"), "limit": 50,
             "sort": "asc", **({"page_token": token} if token else {})}
        d = get_data("/v1beta1/news", q)
        rows += [{"id": int(n["id"]), "time": pd.Timestamp(n["created_at"]).tz_convert(None),
                  "score": headline_score(f"{n.get('headline', '')} {n.get('summary', '')}")}
                 for n in d.get("news", [])]
        token = d.get("next_page_token")
        if not token:
            break
    new = pd.DataFrame(rows, columns=["id", "time", "score"])
    df = new if old is None else pd.concat([old[["id", "time", "score"]], new])
    df = df.drop_duplicates("id").sort_values("time").reset_index(drop=True)
    df.to_csv(path, index=False)
    return df


def alpaca_news_features(articles: pd.DataFrame, index: pd.DatetimeIndex, bar: pd.Timedelta) -> pd.DataFrame:
    """Per bar, from articles published before the bar *ended* (the trade opens after that):
    news_1h      articles in the last hour
    news_24h_z   articles in the last 24 h vs the last 30 days (z-score, log scale)
    news_tone    average headline tone over the last 24 h (-1 .. +1, 0 = none / neutral)"""
    t = pd.DatetimeIndex(articles["time"]) if len(articles) else pd.DatetimeIndex([])
    cum = np.arange(1, len(t) + 1)
    cum_score = np.cumsum(articles["score"].to_numpy()) if len(t) else np.array([])
    ends = index + bar

    def count_before(x):
        return np.searchsorted(t, x, side="left")

    def score_before(x):
        k = count_before(x)
        return np.where(k > 0, cum_score[np.maximum(k - 1, 0)] if len(t) else 0.0, 0.0)

    n1 = count_before(ends) - count_before(ends - pd.Timedelta(hours=1))
    n24 = count_before(ends) - count_before(ends - pd.Timedelta(hours=24))
    s24 = score_before(ends) - score_before(ends - pd.Timedelta(hours=24))
    daily = pd.Series(np.log1p(n24), index)
    # 30 days of history, sampled at every bar: mean and spread of the 24 h count
    hist = daily.rolling(pd.Timedelta(days=30), min_periods=100)
    z = (daily - hist.mean()) / hist.std()
    tone = np.where(n24 > 0, s24 / np.maximum(n24, 1), 0.0)
    return pd.DataFrame({"news_1h": n1.astype(float), "news_24h_z": z.to_numpy(), "news_tone": tone}, index=index)
