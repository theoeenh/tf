"""Point-in-time membership of the research universe (S&P 500 / 400 / 600): who was in which index
when, including the companies that later left. Research only (the strategy finder).

    python -m algo.wide_pit build     # one-off: monthly snapshots from Wikipedia's page history
    python -m algo.wide_pit update    # nightly: today's lists close / open membership spells

Why: until 2026-11-12 the finder tested every strategy on TODAY's index members back to 2017. Companies
that went bankrupt, were bought or shrank out of the index were missing, and companies that only joined
later (after rising) were traded years before they qualified. Both flatter a long strategy, and "buy
after a big fall" most of all: the stocks that fell and never came back are exactly the missing ones.

- source      the three Wikipedia list pages as they stood at the start of each month (page history).
              S&P 500 and 400: from 2015-12. S&P 600: the page only exists from 2018-08-27, so small
              caps enter the universe in September 2018. Nothing is assumed about the months before:
              a stock we cannot place in an index on a day is not in the universe that day.
- table       data/wide/members_history.csv (committed): symbol, index, start, end, sector. A row is
              one unbroken spell in one index, [start, end): start is the first snapshot showing the
              stock (up to a month after it really joined, never before), end the first snapshot
              without it (empty = still a member).
- eligible    a signal counts only on days the stock is in the strategy's segment (mask()).
- prices      the finder loads every stock that was ever a member (wide.update_bars), each cut to
              [first start - WARMUP, last end + GRACE]: the indicators have their history, an open
              trade can run to its exit after the stock leaves, and a ticker later reused by another
              company (FB, BBBY) is not read as the same stock.
"""
from __future__ import annotations

import io
import logging
import re
import time
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd

from .wide import WIDE_DIR

log = logging.getLogger(__name__)
PATH = WIDE_DIR / "members_history.csv"
CACHE = WIDE_DIR / "pit_cache"  # downloaded pages (not committed)
WIKI = "https://en.wikipedia.org/w/index.php"
PAGES = {"sp500": "List of S&P 500 companies", "sp400": "List of S&P 400 companies",
         "sp600": "List of S&P 600 companies"}
SIZE = {"sp500": (480, 520), "sp400": (380, 420), "sp600": (560, 640)}  # a plausible list (else: a broken edit)
BOTH = (950, 1050)  # the S&P 600 page while it listed the S&P 1000 (400 + 600)
FIRST = "2015-12-01"  # first snapshot: the indicators of 2016 need the members of 2016
WARMUP = pd.Timedelta(days=550)  # price history kept before a stock's first day as a member
GRACE = 90  # sessions of prices kept after a stock leaves (an open trade runs to its exit: max 60 sessions)
MAX_GAP = pd.Timedelta(days=10)  # no trade for longer than this after leaving: the stock is gone
UA = {"User-Agent": "tf-research/1.0 (index membership history; research script)"}
PACE = 3.0  # seconds between requests: a few hundred page views, spread over twenty minutes
_last = [0.0]

SECTORS = {  # names used over the years -> today's GICS sector names (as in members.csv)
    "Consumer Discretionary": "Consumer Discretionary", "Consumer Staples": "Consumer Staples",
    "Energy": "Energy", "Financials": "Financials", "Health Care": "Health Care", "Healthcare": "Health Care",
    "Industrials": "Industrials", "Information Technology": "Information Technology",
    "Materials": "Materials", "Real Estate": "Real Estate", "Utilities": "Utilities",
    "Communication Services": "Communication Services",
    "Telecommunication Services": "Communication Services", "Telecommunications Services": "Communication Services",
}


# ------------------------------------------------------------------ Wikipedia page history

def _wiki(**params) -> str:
    """One page view, paced, with long waits when the site asks to slow down."""
    url = WIKI + "?" + urllib.parse.urlencode(params)
    for wait in (0, 30, 120, 300):
        time.sleep(max(wait, PACE - (time.time() - _last[0]), 0))
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except OSError as exc:
            log.info("wikipedia: %s (%s)", exc, url)
    raise OSError(f"wikipedia refused {url}")


def parse_history(html: str) -> list[tuple[pd.Timestamp, int]]:
    """(time, revision id) of every revision listed on a history page."""
    out = []
    for m in re.finditer(r'data-mw-revid="(\d+)".*?class="mw-changeslist-date"[^>]*>([^<]+)<', html, re.S):
        t = pd.to_datetime(m.group(2).strip(), format="%H:%M, %d %B %Y", errors="coerce")
        if not pd.isna(t):
            out.append((t, int(m.group(1))))
    return out


def revisions(index: str, since: str = FIRST, refresh: bool = False) -> list[tuple[pd.Timestamp, int]]:
    """Every revision of an index's list page from a month before `since`, oldest first (kept in the
    cache folder: a rebuild from the downloaded pages needs no network)."""
    path = CACHE / f"{index}_revisions.csv"
    if path.exists() and not refresh:
        r = pd.read_csv(path, parse_dates=["time"])
        return list(zip(r["time"], r["rid"].astype(int)))
    out: dict[int, pd.Timestamp] = {}
    offset = (pd.Timestamp(since) - pd.Timedelta(days=31)).strftime("%Y%m%d%H%M%S")
    while True:
        page = parse_history(_wiki(title=PAGES[index], action="history", dir="prev", offset=offset, limit=2000))
        new = {rid: t for t, rid in page if rid not in out}
        if not new:
            break
        out |= new
        offset = (max(new.values()) - pd.Timedelta(minutes=1)).strftime("%Y%m%d%H%M%S")  # shown to the minute
        if len(page) < 1500:
            break
    revs = sorted((t, rid) for rid, t in out.items())
    CACHE.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(revs, columns=["time", "rid"]).to_csv(path, index=False)
    return revs


def parse_members(html: str) -> pd.DataFrame:
    """symbol, sector from one revision of a list page: the big table with a ticker column."""
    best = pd.DataFrame(columns=["symbol", "sector"])
    try:
        tables = pd.read_html(io.StringIO(html))
    except ValueError:
        return best
    for t in tables:
        cols = [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in t.columns]
        sym = next((i for i, c in enumerate(cols) if re.search(r"ticker|symbol", c, re.I)), None)
        if sym is None or any(re.search(r"removed", c, re.I) for c in cols):
            continue  # no tickers, or the page's table of changes (it grew longer than the list itself)
        if len(t) <= len(best):
            continue
        sec = next((i for i, c in enumerate(cols) if re.search(r"sector", c, re.I)), None)
        s = t.iloc[:, sym].astype(str).str.strip().str.upper().str.replace(".", "-", regex=False)
        ok = s.str.fullmatch(r"[A-Z]{1,5}(-[A-Z]{1,2})?")
        sector = (t.iloc[:, sec].astype(str).str.strip().map(SECTORS) if sec is not None
                  else pd.Series(np.nan, t.index))
        best = pd.DataFrame({"symbol": s[ok], "sector": sector[ok]}).drop_duplicates("symbol")
    return best.reset_index(drop=True)


def fetch_snapshots(first: str = FIRST, last: str | None = None) -> pd.DataFrame:
    """date, index, symbol, sector: each list as it stood at the start of every month (the last revision
    before that day). A month whose page is broken (far too few or too many names) is skipped: the
    previous month's list stands. Pages are cached in data/wide/pit_cache/."""
    CACHE.mkdir(parents=True, exist_ok=True)
    months = pd.date_range(first, last or pd.Timestamp.now().normalize(), freq="MS")
    rows = []
    mid: dict[pd.Timestamp, set] = {}  # the S&P 400 of each month (latest good one)
    for index in PAGES:  # sp500, sp400, then sp600 (which needs the 400 of the month, see below)
        revs = revisions(index, first)
        times = np.array([t.to_datetime64() for t, _ in revs])
        last_mid: set = set()
        for d in months:
            if index == "sp600":
                last_mid = mid.get(d, last_mid)
            k = int(np.searchsorted(times, d.to_datetime64(), side="left")) - 1  # last revision before the day
            if k < 0:
                continue  # the page did not exist yet (S&P 600 before 2018-08-27)
            rid = revs[k][1]
            path = CACHE / f"{index}_{rid}.html"
            if not path.exists():
                path.write_text(_wiki(title=PAGES[index], oldid=rid))
            m = parse_members(path.read_text())
            if index == "sp600" and BOTH[0] <= len(m) <= BOTH[1] and last_mid:
                # until 2020 the page listed the S&P 1000 (the 400 and the 600 together): the small
                # caps are the names that are not in the S&P 400 of that month
                m = m[~m["symbol"].isin(last_mid)]
            lo, hi = SIZE[index]
            if not lo <= len(m) <= hi:
                log.warning("%s %s: %d names in revision %d, skipped", index, d.date(), len(m), rid)
                continue
            if index == "sp400":
                mid[d] = set(m["symbol"])
            rows.append(m.assign(date=d, index=index))
            log.info("%s %s: %d names (revision %d)", index, d.date(), len(m), rid)
    return pd.concat(rows, ignore_index=True)[["date", "index", "symbol", "sector"]]


# ------------------------------------------------------------------ snapshots -> spells

def spells(snaps: pd.DataFrame) -> pd.DataFrame:
    """One row per unbroken stay of a stock in an index: symbol, index, start, end, sector.
    [start, end): start = the first snapshot showing it, end = the first snapshot without it (NaT: in
    the latest one). A stock missing from a single snapshot between two that show it stays a member (a
    bad edit of the page, not a real exit and return within a month)."""
    rows = []
    for index, g in snaps.groupby("index"):
        dates = sorted(g["date"].unique())
        pos = {d: i for i, d in enumerate(dates)}
        sector = g.dropna(subset=["sector"]).sort_values("date").groupby("symbol")["sector"].last()
        for sym, s in g.groupby("symbol"):
            seen = sorted(pos[d] for d in s["date"])
            start = prev = seen[0]
            for i in seen[1:] + [None]:
                if i is not None and i - prev <= 2:  # next snapshot, or one missing in between
                    prev = i
                    continue
                rows.append({"symbol": sym, "index": index, "start": dates[start],
                             "end": dates[prev + 1] if prev + 1 < len(dates) else pd.NaT,
                             "sector": sector.get(sym, np.nan)})
                if i is not None:
                    start = prev = i
    out = pd.DataFrame(rows, columns=["symbol", "index", "start", "end", "sector"])
    return out.sort_values(["symbol", "start", "index"]).reset_index(drop=True)


def roll(history: pd.DataFrame, today_members: pd.DataFrame, day: pd.Timestamp) -> pd.DataFrame:
    """The table brought to `day` with today's lists (symbol, index, sector): a stock no longer in an
    index closes its spell that day, a new one opens a spell that day. Nothing in the past changes."""
    h = history.copy()
    day = pd.Timestamp(day).normalize()
    now = set(zip(today_members["symbol"], today_members["index"]))
    is_open = h["end"].isna()
    held = set(zip(h.loc[is_open, "symbol"], h.loc[is_open, "index"]))
    gone = is_open & ~pd.Series([k in now for k in zip(h["symbol"], h["index"])], h.index)
    h.loc[gone, "end"] = day
    sec = dict(zip(today_members["symbol"], today_members["sector"]))
    new = [{"symbol": s, "index": i, "start": day, "end": pd.NaT, "sector": sec.get(s, np.nan)}
           for s, i in sorted(now - held)]
    if new:
        h = pd.concat([h, pd.DataFrame(new)], ignore_index=True)
    return h.sort_values(["symbol", "start", "index"]).reset_index(drop=True)


# ------------------------------------------------------------------ reading the table

def available() -> bool:
    return PATH.exists()


_cache: dict = {}


def history() -> pd.DataFrame:
    mtime = PATH.stat().st_mtime
    if _cache.get("mtime") != (str(PATH), mtime):  # another file, or the file changed: forget everything
        _cache.clear()
        _cache["mtime"] = (str(PATH), mtime)
        _cache["h"] = pd.read_csv(PATH, parse_dates=["start", "end"])
    return _cache["h"]


def _memo(name: str, make):
    history()
    if name not in _cache:
        _cache[name] = make()
    return _cache[name]


def ever() -> list[str]:
    """Every symbol that was a member of any of the three indexes at some point."""
    return _memo("ever", lambda: sorted(history()["symbol"].unique()))


def sectors() -> dict[str, str]:
    """Sector of every stock ever a member (its last known one)."""
    def make():
        h = history().dropna(subset=["sector"]).sort_values("start")
        return dict(zip(h["symbol"], h["sector"]))
    return _memo("sectors", make)


def last_index() -> dict[str, str]:
    def make():
        h = history().sort_values("start")
        return dict(zip(h["symbol"], h["index"]))
    return _memo("last_index", make)


def _stays(name: str) -> dict[str, list[tuple]]:
    """symbol -> its stays [(start, end)] in a segment: "all" = S&P 500, sp400 / sp600, sp1500 = any of
    the three, "sector:X" = any of the three for the stocks of that sector."""
    def make():
        h = history()
        if name == "all":
            h = h[h["index"] == "sp500"]
        elif name.startswith("sector:"):
            h = h[h["symbol"].map(sectors()) == name[7:]]
        elif name != "sp1500":
            h = h[h["index"] == name]
        out: dict[str, list[tuple]] = {}
        far = np.datetime64("2262-01-01")
        for sym, start, end in zip(h["symbol"], h["start"], h["end"]):
            out.setdefault(sym, []).append((start.to_datetime64(), far if pd.isna(end) else end.to_datetime64()))
        return out
    return _memo("stays:" + name, make)


def segment_ever(name: str):
    """Which stocks a strategy on this segment may ever trade (the date decides the rest: mask())."""
    keep = _stays(name)
    return lambda a: a in keep


def mask(name: str, symbol: str, index: pd.DatetimeIndex) -> np.ndarray:
    """True on the days `symbol` is a member of the segment `name` (as known that day)."""
    days = index.values
    out = np.zeros(len(days), bool)
    for start, end in _stays(name).get(symbol, ()):
        out |= (days >= start) & (days < end)
    return out


def window(symbol: str) -> tuple[pd.Timestamp, pd.Timestamp | None]:
    """(first day as a member of any index, the day it left the last one or None if still a member)."""
    h = history()
    h = h[h["symbol"] == symbol]
    if h.empty:
        raise KeyError(symbol)
    return h["start"].min(), (None if h["end"].isna().any() else h["end"].max())


def cut(df: pd.DataFrame, first: pd.Timestamp, left: pd.Timestamp | None) -> pd.DataFrame:
    """A stock's bars as the research may use them: from WARMUP before its first day as a member, and
    after it left the universe only while it keeps trading (no pause over MAX_GAP: an acquired or
    delisted stock ends there, and a ticker reused later by another company is not read), for at most
    GRACE sessions."""
    df = df[df.index >= first - WARMUP]
    if left is None or df.empty:
        return df
    after = df.index[df.index >= left]
    keep_until = df.index[df.index < left][-1] if (df.index < left).any() else None
    prev = keep_until
    for n, d in enumerate(after):
        if n >= GRACE or (prev is not None and d - prev > MAX_GAP):
            break
        keep_until = prev = d
    return df[df.index <= keep_until] if keep_until is not None else df.iloc[:0]


def universe_returns(prices: dict, name: str) -> pd.Series:
    """Equal-weight daily return of a segment's members of the day: what being in those stocks earns
    with no skill at all (the benchmark the luck check takes out of a strategy's returns). Bars without
    volume (a vanished stock's closing bars) are not prices and do not count."""
    cols = {}
    for a, df in prices.items():
        if not segment_ever(name)(a):
            continue
        real = df["Volume"] > 0 if "Volume" in df else pd.Series(True, df.index)
        cols[a] = df["Close"].pct_change().where(mask(name, a, df.index) & real.to_numpy())
    if not cols:
        return pd.Series(dtype=float)
    return pd.DataFrame(cols).mean(axis=1).fillna(0.0)


# ------------------------------------------------------------------ command line

def build() -> pd.DataFrame:
    from . import wide

    snaps = fetch_snapshots()
    h = spells(snaps)
    today = wide._table()[["symbol", "index", "sector"]]
    h = roll(h, today, pd.Timestamp.now().normalize())
    WIDE_DIR.mkdir(parents=True, exist_ok=True)
    h.to_csv(PATH, index=False)
    return h


def update() -> pd.DataFrame:
    """Nightly: today's lists (already refreshed by algo.wide) against the open spells."""
    from . import wide

    h = roll(history(), wide._table()[["symbol", "index", "sector"]], pd.Timestamp.now().normalize())
    h.to_csv(PATH, index=False)
    return h


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build", "update"])
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    h = build() if args.cmd == "build" else update()
    print(f"{h['symbol'].nunique()} stocks ever members, {len(h)} spells, {int(h['end'].isna().sum())} open")


if __name__ == "__main__":
    main()
