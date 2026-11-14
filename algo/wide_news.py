"""News per stock and day for the S&P 1500 research: Alpaca's news archive (Benzinga), 2015 -> now.

    python -m algo.wide_news                 # download the months that are missing
    python -m algo.wide_news --minutes 300   # stop after that long; the next run goes on where it stopped
    python -m algo.wide_news --pace 0.34     # seconds between requests (default 0.6: half of Alpaca's limit,
                                             # so the trading runs that share the key are never held up)

Why (2026-11-14): the only news inputs so far were a daily tone for 8 hand-picked assets (GDELT, which
refuses most requests and has holes) and headline scores for the 22 assets of the hourly system. On
those, over 18,000 to 20,000 asset-days, neither predicted the next day; headlines describe the move
that already happened. Whether news says anything about what comes NEXT can only be tested on many
stocks, with the members of each day, through the finder's checks: this file is the data for that.

Per stock and day, no text kept:
  n      articles about the company (tagged with at most MAX_TAGS stocks)
  pos    of those, headlines the word list of algo.news reads as good news
  neg    of those, headlines it reads as bad news
  score  sum of those headlines' scores (-1 .. +1 each)
  wide   round-ups that mention the stock among more than MAX_TAGS others (market wraps, movers lists)
A "day" is what a strategy deciding at the 16:00 New York close can know: an article published after
the close counts for the next day (day_of); weekend and holiday days move to the next session when
the table is laid on a stock's bars (by_stock).

Files: data/wide/news/YYYY-MM.csv.gz, one per month of publication (kept in the Actions cache, not in
git). A month that was downloaded after it ended is listed in done.txt and never read again; the
running month is downloaded again from its first day at every run. Nothing may use the table before
every month from FIRST on is there (load): a missing month would read as "no news".
"""
from __future__ import annotations

import argparse
import logging
import time

import numpy as np
import pandas as pd

from . import news
from .wide import WIDE_DIR

log = logging.getLogger(__name__)
NEWS_DIR = WIDE_DIR / "news"
FIRST = "2015-01-01"  # Alpaca's archive starts in 2015
MAX_TAGS = 3  # an article tagged with more stocks is a round-up, not news about one company
PACE = 0.6  # seconds between requests: half of Alpaca's 200 a minute (the trading runs share the key)
COLUMNS = ["day", "symbol", "n", "pos", "neg", "score", "wide"]
NY = "America/New_York"


def day_of(created) -> pd.Timestamp:
    """The first day whose 16:00 New York close knows an article published at `created` (UTC)."""
    t = pd.Timestamp(created)
    t = t.tz_localize("UTC") if t.tzinfo is None else t
    return (t.tz_convert(NY) + pd.Timedelta(hours=8)).tz_localize(None).normalize()


def tally(articles, keep: set[str]) -> pd.DataFrame:
    """Articles (Alpaca's JSON) -> one row per day and stock of `keep`. An article seen twice counts once."""
    rows: dict[tuple, list] = {}
    seen = set()
    for a in articles:
        if a["id"] in seen:
            continue
        seen.add(a["id"])
        tags = [s.replace(".", "-") for s in a.get("symbols") or []]
        ours = [s for s in tags if s in keep]
        if not ours:
            continue
        day = day_of(a["created_at"])
        focused = len(tags) <= MAX_TAGS
        score = news.headline_score(f"{a.get('headline', '')} {a.get('summary', '')}") if focused else 0.0
        for s in ours:
            r = rows.setdefault((day, s), [0, 0, 0, 0.0, 0])
            if focused:
                r[0] += 1
                r[1] += score > 0
                r[2] += score < 0
                r[3] += score
            else:
                r[4] += 1
    out = pd.DataFrame([[d, s, *v] for (d, s), v in rows.items()], columns=COLUMNS)
    return out.sort_values(["day", "symbol"]).reset_index(drop=True)


def _articles(start: pd.Timestamp, end: pd.Timestamp, pace: float = PACE):
    """Every article published in [start, end), oldest first."""
    from .alpaca import get_data

    token, last = None, 0.0
    while True:
        wait = pace - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        last = time.time()
        d = get_data("/v1beta1/news", {"start": f"{start:%Y-%m-%dT%H:%M:%SZ}", "end": f"{end:%Y-%m-%dT%H:%M:%SZ}",
                                      "limit": 50, "sort": "asc", "include_content": "false",
                                      **({"page_token": token} if token else {})})
        yield from d.get("news", [])
        token = d.get("next_page_token")
        if not token:
            return


def _done() -> list[str]:
    path = NEWS_DIR / "done.txt"
    return path.read_text().split() if path.exists() else []


def months(until: pd.Timestamp | None = None) -> list[str]:
    until = until or pd.Timestamp.now(tz="UTC").tz_localize(None)
    return [str(m) for m in pd.period_range(FIRST, until, freq="M")]


def download(minutes: float | None = None, pace: float = PACE) -> list[str]:
    """Download the months not finished yet, oldest first; returns those still missing."""
    from . import wide

    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    keep = set(wide.research_symbols())
    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    stop = time.time() + 60 * minutes if minutes else None
    todo = [m for m in months(now) if m not in _done()]
    for n, m in enumerate(todo):
        if stop and time.time() > stop:
            log.info("time is up: %d months left", len(todo) - n)
            return todo[n:]
        start = pd.Timestamp(m + "-01")
        end = min(start + pd.offsets.MonthBegin(1), now - pd.Timedelta(minutes=20))
        t = tally(_articles(start, end, pace), keep)
        t.to_csv(NEWS_DIR / f"{m}.csv.gz", index=False)
        if start + pd.offsets.MonthBegin(1) <= end:  # the month is over: never read again
            with (NEWS_DIR / "done.txt").open("a") as f:
                f.write(m + "\n")
        else:  # the running month: known through the last close before this download
            (NEWS_DIR / "through.txt").write_text(f"{day_of(end) - pd.Timedelta(days=1):%Y-%m-%d}\n")
        log.info("%s: %d stock-days, %d articles about a company", m, len(t), int(t["n"].sum()))
    return []


_cache: dict = {}


def load() -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    """(table, first day, last day the news is known through). Raises while a month is missing."""
    stamp = tuple(sorted((p.name, p.stat().st_size) for p in NEWS_DIR.glob("*.csv.gz"))) if NEWS_DIR.exists() else ()
    if _cache.get("stamp") == (str(NEWS_DIR), stamp) and "table" in _cache:
        return _cache["table"]
    done = set(_done())
    have = sorted(p.name[:7] for p in NEWS_DIR.glob("*.csv.gz")) if NEWS_DIR.exists() else []
    if not have:
        raise FileNotFoundError("no news downloaded (python -m algo.wide_news)")
    want = [str(m) for m in pd.period_range(FIRST, have[-1], freq="M")]
    missing = [m for m in want if m not in have or (m not in done and m != have[-1])]
    if missing:
        raise FileNotFoundError(f"news download not finished: {missing[0]} is missing ({len(missing)} months to go)")
    t = pd.concat([pd.read_csv(NEWS_DIR / f"{m}.csv.gz", parse_dates=["day"]) for m in want], ignore_index=True)
    t = t.groupby(["day", "symbol"], as_index=False)[COLUMNS[2:]].sum()  # an evening article: the next month's first day
    last = pd.Timestamp(have[-1] + "-01") + pd.offsets.MonthEnd(0)
    through = NEWS_DIR / "through.txt"
    if have[-1] not in done:  # the running month: only through the last close before its download
        last = pd.Timestamp(through.read_text().strip()) if through.exists() else pd.Timestamp(have[-1] + "-01") - pd.Timedelta(days=1)
    _cache.clear()
    _cache["stamp"] = (str(NEWS_DIR), stamp)
    _cache["table"] = (t, pd.Timestamp(FIRST), last.normalize())
    return _cache["table"]


def by_stock(prices: dict) -> tuple[dict[str, pd.DataFrame], pd.Timestamp, pd.Timestamp]:
    """The table laid on each stock's own sessions: {stock: n, pos, neg, score, wide per bar}. A day
    without a session (weekend, holiday) moves to the next one; days after the last bar are dropped.
    Also the first and last day the news covers (outside them, no row means no data, not no news)."""
    t, first, last = load()
    if "groups" not in _cache:
        _cache["groups"] = {s: g for s, g in t.groupby("symbol")}
    out = {}
    for a, df in prices.items():
        vals = np.zeros((len(df), len(COLUMNS) - 2))
        g = _cache["groups"].get(a)
        if g is not None:
            pos = df.index.searchsorted(g["day"].to_numpy(), side="left")
            ok = pos < len(df)
            np.add.at(vals, pos[ok], g[COLUMNS[2:]].to_numpy(float)[ok])
        out[a] = pd.DataFrame(vals, index=df.index, columns=COLUMNS[2:])
    return out, first, last


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--minutes", type=float, default=None, help="stop after this many minutes")
    ap.add_argument("--pace", type=float, default=PACE, help="seconds between requests")
    args = ap.parse_args()
    left = download(args.minutes, args.pace)
    have = len(months()) - len(left)
    print(f"news: {have} of {len(months())} months downloaded" + (f"; next: {left[0]}" if left else ""))


if __name__ == "__main__":
    main()
