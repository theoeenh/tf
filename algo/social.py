"""Record crowd mood from StockTwits (free, no account) — data only, no trading.

    python -m algo.social        # fetch new messages for every asset, update data/social/

Every run, for each asset: how many messages were posted per hour (attention),
and how many authors tagged their own message Bullish or Bearish (mood). Only
these counts are kept, never the text. There is no history to test against,
so the counts build up from now on; once there are a few weeks, we check
whether they predict anything before any strategy is allowed to use them.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.request
from pathlib import Path

import pandas as pd

from .data import CRYPTO, DATA_DIR

log = logging.getLogger(__name__)
SOCIAL_DIR = DATA_DIR / "social"
URL = "https://api.stocktwits.com/api/2/streams/symbol/{sym}.json"
NAMES = {"GOLD": "GLD", "SILVER": "SLV"}
MAX_PAGES = 6  # 30 messages a page; enough for 30 minutes of even the busiest names


def symbol(asset: str) -> str:
    return f"{asset}.X" if asset in CRYPTO else NAMES.get(asset, asset)


def _get(sym: str, max_id: int | None = None) -> dict:
    url = URL.format(sym=sym) + (f"?max={max_id}" if max_id else "")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research; paper trading)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def fetch_new(asset: str, since_id: int) -> list[dict]:
    """Messages newer than `since_id` (newest first), paging back until reaching it."""
    out, max_id = [], None
    for _ in range(MAX_PAGES):
        d = _get(symbol(asset), max_id)
        msgs = d.get("messages", [])
        new = [m for m in msgs if m["id"] > since_id]
        out += new
        if len(new) < len(msgs) or not d.get("cursor", {}).get("more") or not since_id:
            break  # reached what we already had (or first run: one page is enough)
        max_id = d["cursor"]["max"]
        time.sleep(0.5)
    return out


def hourly_counts(msgs: list[dict]) -> pd.DataFrame:
    rows = []
    for m in msgs:
        mood = ((m.get("entities") or {}).get("sentiment") or {}).get("basic")
        rows.append({"hour": pd.Timestamp(m["created_at"]).tz_convert(None).floor("h"),
                     "messages": 1, "bullish": int(mood == "Bullish"), "bearish": int(mood == "Bearish")})
    if not rows:
        return pd.DataFrame(columns=["messages", "bullish", "bearish"], index=pd.DatetimeIndex([], name="hour"))
    return pd.DataFrame(rows).groupby("hour").sum()


def record(assets) -> dict:
    SOCIAL_DIR.mkdir(parents=True, exist_ok=True)
    state_path = SOCIAL_DIR / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    summary = {}
    for a in assets:
        try:
            msgs = fetch_new(a, state.get(a, 0))
        except Exception as exc:  # one asset failing never stops the others
            log.warning("StockTwits unavailable for %s (%s)", a, exc)
            continue
        if msgs:
            state[a] = max(m["id"] for m in msgs)
            path = SOCIAL_DIR / f"{a}.csv"
            new = hourly_counts(msgs)
            old = pd.read_csv(path, index_col=0, parse_dates=True) if path.exists() else None
            merged = new if old is None else old.add(new, fill_value=0)
            merged.astype(int).sort_index().to_csv(path)
        summary[a] = len(msgs)
        time.sleep(0.3)
    state_path.write_text(json.dumps(state, indent=1))
    return summary


def main() -> None:
    from .system import UNIVERSE_GLOBAL

    logging.basicConfig(level=logging.WARNING)
    s = record(UNIVERSE_GLOBAL)
    print(f"StockTwits: {sum(s.values())} new messages for {len(s)} assets")


if __name__ == "__main__":
    main()
