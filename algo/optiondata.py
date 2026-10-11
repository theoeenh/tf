"""Record the option market once a day, for the learner (account F's job; it never trades).

    PAPER_ACCOUNT=F python -m algo.optiondata record            # once a day, from 15:00 New York while open
    PAPER_ACCOUNT=F python -m algo.optiondata record --force    # now, whatever the time

Alpaca serves option prices for today only: a day not recorded is lost for good. So every trading day, for each
stock and ETF the system trades (plus SPY), this saves:

- data/options/chains/YYYY-MM-DD.csv.gz: every contract 5-100 days out with a strike within 15% of the price
  (quote, last price, the day's volume, implied volatility, delta, gamma, vega, theta);
- data/options/daily.csv: one row per stock and day, the numbers the learner can use as features:

| column | meaning |
|---|---|
| iv7, iv30, iv60, iv90 | implied volatility of the at-the-money options at 7 / 30 / 60 / 90 days (a year's %) |
| move30 | the 30-day at-the-money straddle (call + put) as a share of the price: the move the market expects |
| skew25 | 30 days: implied volatility of the 25-delta put minus the 25-delta call (fear of a fall) |
| pc_volume | puts traded / calls traded today (contracts in the saved range) |
| volume | option contracts traded today |

Implied volatility of different days is blended in variance (iv^2 x days), the usual way. Prices: Alpaca's free
'indicative' feed (delayed, but all the learner needs at a daily step).
"""
from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import pandas as pd

from .alpaca import get_data, request
from .data import ALPACA_SYMBOLS, CRYPTO

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "options"
DAILY = OUT / "daily.csv"
DTE_LO, DTE_HI, STRIKE_BAND = 5, 100, 0.15
TENORS = (7, 30, 60, 90)
FROM_HOUR = 15  # New York: the day's record is taken in the last hour of the session
OCC = re.compile(r"^([A-Z.]+)(\d{6})([CP])(\d{8})$")
COLUMNS = ["date", "underlying", "spot", "iv7", "iv30", "iv60", "iv90", "move30", "skew25", "pc_volume", "volume",
           "contracts"]


def underlyings() -> list[str]:
    return sorted({s for a, s in ALPACA_SYMBOLS.items() if a not in CRYPTO} | {"SPY"})


def parse_occ(sym: str) -> dict | None:
    m = OCC.match(sym)
    if not m:
        return None
    root, ymd, cp, k = m.groups()
    return {"root": root, "expiry": pd.Timestamp(f"20{ymd[:2]}-{ymd[2:4]}-{ymd[4:]}"),
            "type": "call" if cp == "C" else "put", "strike": int(k) / 1000}


def rows_from_snapshots(und: str, snaps: dict, today: pd.Timestamp) -> list[dict]:
    """Alpaca option snapshots -> one flat row per contract."""
    out = []
    for sym, s in snaps.items():
        o = parse_occ(sym)
        if o is None:
            continue
        q, t, g, bar = (s.get(k) or {} for k in ("latestQuote", "latestTrade", "greeks", "dailyBar"))
        out.append({"date": today.date().isoformat(), "underlying": und, "symbol": sym,
                    "expiry": o["expiry"].date().isoformat(), "dte": (o["expiry"] - today).days, "type": o["type"],
                    "strike": o["strike"], "bid": q.get("bp"), "ask": q.get("ap"), "last": t.get("p"),
                    "volume": bar.get("v") or 0, "iv": s.get("impliedVolatility"), "delta": g.get("delta"),
                    "gamma": g.get("gamma"), "vega": g.get("vega"), "theta": g.get("theta")})
    return out


def _atm_iv(e: pd.DataFrame, spot: float) -> float | None:
    """At-the-money implied volatility of one expiry: call and put at the strike nearest the price."""
    e = e.dropna(subset=["iv"])
    e = e[e["iv"] > 0]
    if e.empty:
        return None
    k = e.loc[(e["strike"] - spot).abs().idxmin(), "strike"]
    return float(e.loc[e["strike"] == k, "iv"].mean())


def _at_tenor(points: list[tuple[int, float]], days: int) -> float | None:
    """Implied volatility at `days`, linear in total variance between the two nearest expiries (flat outside)."""
    points = sorted(p for p in points if p[0] > 0 and p[1] is not None)
    if not points:
        return None
    if days <= points[0][0]:
        return points[0][1]
    if days >= points[-1][0]:
        return points[-1][1]
    for (d0, v0), (d1, v1) in zip(points, points[1:]):
        if d0 <= days <= d1:
            w0, w1 = v0 ** 2 * d0, v1 ** 2 * d1
            return math.sqrt((w0 + (w1 - w0) * (days - d0) / (d1 - d0)) / days)
    return None


def _mid(r) -> float | None:
    if r["bid"] and r["ask"] and r["bid"] > 0 and r["ask"] >= r["bid"]:
        return (r["bid"] + r["ask"]) / 2
    return r["last"] or None


def features(chain: pd.DataFrame, spot: float) -> dict:
    """The day's summary for one underlying (see the table at the top)."""
    out = dict.fromkeys(COLUMNS[3:], None) | {"spot": spot, "contracts": len(chain)}
    if chain.empty or not spot:
        return out
    by_exp = {d: e for d, e in chain.groupby("dte")}
    atm = [(d, _atm_iv(e, spot)) for d, e in by_exp.items()]
    for t in TENORS:
        v = _at_tenor(atm, t)
        out[f"iv{t}"] = round(v, 4) if v is not None else None
    d30 = min(by_exp, key=lambda d: abs(d - 30))
    e = by_exp[d30]
    k = e.loc[(e["strike"] - spot).abs().idxmin(), "strike"]
    legs = e[e["strike"] == k]
    mids = [_mid(r) for _, r in legs.iterrows()]
    if len(legs) == 2 and all(mids):
        out["move30"] = round(sum(mids) / spot, 4)
    g = e.dropna(subset=["delta", "iv"])
    puts, calls = g[g["type"] == "put"], g[g["type"] == "call"]
    if not puts.empty and not calls.empty:
        p = puts.loc[(puts["delta"] + 0.25).abs().idxmin()]
        c = calls.loc[(calls["delta"] - 0.25).abs().idxmin()]
        if abs(p["delta"] + 0.25) < 0.1 and abs(c["delta"] - 0.25) < 0.1:
            out["skew25"] = round(float(p["iv"] - c["iv"]), 4)
    vol = chain.groupby("type")["volume"].sum()
    out["volume"] = int(vol.sum())
    if vol.get("call", 0) > 0:
        out["pc_volume"] = round(float(vol.get("put", 0) / vol["call"]), 3)
    return out


def fetch_chain(und: str, spot: float, today: pd.Timestamp) -> list[dict]:
    params = {"feed": "indicative", "limit": 1000,
              "expiration_date_gte": (today + pd.Timedelta(days=DTE_LO)).date().isoformat(),
              "expiration_date_lte": (today + pd.Timedelta(days=DTE_HI)).date().isoformat(),
              "strike_price_gte": f"{spot * (1 - STRIKE_BAND):.2f}", "strike_price_lte": f"{spot * (1 + STRIKE_BAND):.2f}"}
    snaps: dict = {}
    for _ in range(50):
        r = get_data(f"/v1beta1/options/snapshots/{und}", params)
        snaps |= r.get("snapshots") or {}
        if not r.get("next_page_token"):
            break
        params["page_token"] = r["next_page_token"]
    return rows_from_snapshots(und, snaps, today)


def spots(symbols: list[str]) -> dict[str, float]:
    r = get_data("/v2/stocks/snapshots", {"symbols": ",".join(symbols), "feed": "iex"})
    r = r.get("snapshots", r)
    out = {}
    for s, v in r.items():
        p = ((v or {}).get("latestTrade") or {}).get("p") or ((v or {}).get("dailyBar") or {}).get("c")
        if p:
            out[s] = float(p)
    return out


def due(now_ny: pd.Timestamp, is_open: bool, recorded: set[str]) -> bool:
    return is_open and now_ny.hour >= FROM_HOUR and now_ny.date().isoformat() not in recorded


def recorded_days() -> set[str]:
    return set(pd.read_csv(DAILY, usecols=["date"])["date"]) if DAILY.exists() else set()


def record(force: bool = False) -> None:
    now_ny = pd.Timestamp.now(tz="America/New_York")
    if not force and not due(now_ny, bool(request("GET", "/v2/clock").get("is_open")), recorded_days()):
        print("Option record: not due (once a day, from 15:00 New York while the market is open).")
        return
    today = now_ny.tz_localize(None).normalize()
    unds = underlyings()
    px = spots(unds)
    rows, summary, missing = [], [], []
    for u in unds:
        if u not in px:
            missing.append(u)
            continue
        try:
            got = fetch_chain(u, px[u], today)
        except Exception as e:  # one underlying failing must not lose the others
            print(f"  {u}: no chain ({e})")
            missing.append(u)
            continue
        rows += got
        summary.append({"date": today.date().isoformat(), "underlying": u} | features(pd.DataFrame(got), px[u]))
    if not rows:
        raise SystemExit("Option record: nothing downloaded")
    (OUT / "chains").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "chains" / f"{today.date()}.csv.gz", index=False)
    new = pd.DataFrame(summary, columns=COLUMNS)
    old = pd.read_csv(DAILY) if DAILY.exists() else pd.DataFrame(columns=COLUMNS)
    old = old[old["date"] != today.date().isoformat()]
    pd.concat([old, new]).sort_values(["date", "underlying"]).to_csv(DAILY, index=False)
    print(f"Option record {today.date()}: {len(rows):,} contracts, {len(summary)} underlyings"
          + (f"; missing {missing}" if missing else ""))
    print(new[["underlying", "spot", "iv30", "move30", "skew25", "pc_volume"]].to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("--force", action="store_true")
    args = ap.parse_args()
    record(args.force)


if __name__ == "__main__":
    main()
