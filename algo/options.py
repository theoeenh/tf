"""Account F: calls instead of shares, on the stock signals account A takes.

    PAPER_ACCOUNT=F python -m algo.options sync          # show what it would do (dry run)
    PAPER_ACCOUNT=F python -m algo.options sync --send   # trade (US market hours only)

The idea: more reward for the same signal with the loss capped in advance. Each time account A
(paper/orders.json) opens a long position on a stock or ETF, F buys calls on it instead:
- contract: expiry 30-60 days away (time decay is slow there), delta closest to 0.60 (slightly in
  the money: moves with the stock, cheaper than the shares), bid-ask spread at most 10%;
- size: premium of about 3% of F's equity per stock (the most F can lose on that trade), at most
  6 stocks at once (18% of equity in premiums); whole contracts only, none if one is too dear;
- entry: only while A's trade is fresh (between -0.3R and +0.5R), never chasing an old move;
- exit: when A closes its position (stop, target, time, event), or 10 days before expiry (the next
  run buys a new 30-60 day call if A still holds the stock).
Options cannot carry stop orders at Alpaca, so exits are made by these runs (every 30 minutes);
the premium paid is the loss limit. Orders are limit orders at the ask (buy) / bid (sell), day
orders, sent only while the market is open. Prices: Alpaca's free 'indicative' option feed.
Everything F does is logged in paper/F/fills.csv and paper/F/status.md.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import pandas as pd

from .alpaca import AlpacaError, check_account, get_data, request
from .data import ALPACA_SYMBOLS, CRYPTO
from .paper import PAPER_DIR

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "paper" / "orders.json"  # account A's plan
DTE_MIN, DTE_MAX, DTE_EXIT = 30, 60, 10
TARGET_DELTA = 0.60
MAX_SPREAD = 0.10
BUDGET = 0.03  # premium per stock, share of equity
MAX_NAMES = 6
FRESH_R = (-0.3, 0.5)


def wanted_underlyings(plan: list[dict]) -> dict[str, float]:
    """Stocks / ETFs account A holds long, with the trade's current R (best one per stock)."""
    out: dict[str, float] = {}
    for t in plan:
        if t["asset"] in CRYPTO or t["qty"] <= 0:
            continue
        sym = ALPACA_SYMBOLS.get(t["asset"], t["asset"])
        out[sym] = max(out.get(sym, -9.0), float(t.get("r") or 0.0))
    return out


def choose(contracts: list[dict], snaps: dict, today: pd.Timestamp) -> dict | None:
    """The call nearest to TARGET_DELTA among liquid 30-60 day contracts (None if none fits)."""
    best, best_gap = None, 9.0
    for c in contracts:
        s = snaps.get(c["symbol"]) or {}
        q, g = s.get("latestQuote") or {}, s.get("greeks") or {}
        bid, ask, delta = float(q.get("bp") or 0), float(q.get("ap") or 0), g.get("delta")
        dte = (pd.Timestamp(c["expiration_date"]) - today).days
        if delta is None or ask <= 0 or bid <= 0 or not DTE_MIN <= dte <= DTE_MAX:
            continue
        if (ask - bid) / ((ask + bid) / 2) > MAX_SPREAD:
            continue
        gap = abs(float(delta) - TARGET_DELTA)
        if gap < best_gap:
            best, best_gap = c | {"bid": bid, "ask": ask, "delta": float(delta), "dte": dte}, gap
    return best


def contracts_for(underlying: str, spot: float, today: pd.Timestamp) -> tuple[list[dict], dict]:
    q = (f"/v2/options/contracts?underlying_symbols={underlying}&type=call&status=active"
         f"&expiration_date_gte={(today + pd.Timedelta(days=DTE_MIN)).date()}"
         f"&expiration_date_lte={(today + pd.Timedelta(days=DTE_MAX)).date()}"
         f"&strike_price_gte={spot * 0.80:.2f}&strike_price_lte={spot * 1.10:.2f}&limit=200")
    cs = request("GET", q).get("option_contracts", [])
    snaps = {}
    for i in range(0, len(cs), 100):
        syms = ",".join(c["symbol"] for c in cs[i:i + 100])
        snaps |= get_data("/v1beta1/options/snapshots", {"symbols": syms, "feed": "indicative"}).get("snapshots", {})
    return cs, snaps


def held_options() -> list[dict]:
    return [p for p in request("GET", "/v2/positions") if p.get("asset_class") == "us_option"]


def underlying_of(occ: str) -> str:
    """OCC symbol NVDA261106C00220000 -> NVDA."""
    return occ[:-15]


def expiry_of(occ: str) -> pd.Timestamp:
    return pd.Timestamp("20" + occ[-15:-9])


def plan_orders(plan: list[dict], held: list[dict], equity: float, today: pd.Timestamp,
                pick=None) -> list[dict]:
    """Sells first (A closed the stock, or expiry is near), then buys for fresh signals."""
    want = wanted_underlyings(plan)
    orders, keep = [], set()
    for p in held:
        und, qty = underlying_of(p["symbol"]), int(float(p["qty"]))
        near = (expiry_of(p["symbol"]) - today).days <= DTE_EXIT
        if und not in want or near:
            orders.append({"symbol": p["symbol"], "side": "sell", "qty": qty, "underlying": und,
                           "why": "A closed the stock" if und not in want else f"{DTE_EXIT} days to expiry"})
        else:
            keep.add(und)
    slots = MAX_NAMES - len(keep)
    for und, r in sorted(want.items(), key=lambda kv: kv[1]):  # the freshest first
        if und in keep or slots <= 0 or not FRESH_R[0] <= r <= FRESH_R[1]:
            continue
        c = pick(und) if pick else None
        if c is None:
            continue
        n = math.floor(BUDGET * equity / (c["ask"] * 100))
        if n < 1:
            continue
        orders.append({"symbol": c["symbol"], "side": "buy", "qty": n, "underlying": und, "limit": c["ask"],
                       "why": f"A holds {und} ({r:+.2f}R): {c.get('name', c['symbol'])}, delta {c['delta']:.2f}, "
                              f"{c['dte']} days, ${c['ask'] * 100 * n:,.0f} premium"})
        slots -= 1
    return orders


def log_fill(o: dict, status: dict) -> None:
    f = PAPER_DIR / "fills.csv"
    if not f.exists():
        f.write_text("time,symbol,underlying,side,qty,filled_qty,avg_price,why\n")
    with f.open("a") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())},{o['symbol']},{o['underlying']},{o['side']},"
                 f"{o['qty']},{status.get('filled_qty', 0)},{status.get('filled_avg_price') or ''},"
                 f"\"{o['why']}\"\n")


def write_status(acct: dict, held: list[dict]) -> None:
    eq = float(acct.get("equity", 0))
    lines = [f"# {json.loads((PAPER_DIR / 'config.json').read_text()).get('name', 'F')}", "",
             f"Updated {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC. **Equity ${eq:,.0f}** "
             f"({eq / 100_000 - 1:+.2%} since start).", "", "## Calls held", ""]
    if not held:
        lines.append("None.")
    for p in held:
        lines.append(f"- {p['symbol']} ({underlying_of(p['symbol'])}, expires {expiry_of(p['symbol']).date()}): "
                     f"{p['qty']} contracts, cost ${float(p['cost_basis']):,.0f}, now ${float(p['market_value']):,.0f} "
                     f"({float(p['unrealized_plpc']):+.0%})")
    (PAPER_DIR / "status.md").write_text("\n".join(lines) + "\n")


def sync(send: bool = False) -> list[dict]:
    num = check_account()
    acct = request("GET", "/v2/account")
    plan = json.loads(SIGNALS.read_text())
    held = held_options()
    today = pd.Timestamp.now(tz="America/New_York").tz_localize(None).normalize()
    spots = {}

    def pick(und):
        spot = next((t["mark"] for t in plan if ALPACA_SYMBOLS.get(t["asset"], t["asset"]) == und), None)
        if not spot:
            return None
        spots[und] = spot
        cs, snaps = contracts_for(und, float(spot), today)
        return choose(cs, snaps, today)

    orders = plan_orders(plan, held, float(acct["equity"]), today, pick)
    print(f"Alpaca account {num}: F – Options, equity ${float(acct['equity']):,.0f}, "
          f"{len(held)} call position(s)")
    for o in orders:
        print(f"{o['side'].upper():4s} {o['qty']:>4d} {o['symbol']:22s} {o['why']}")
    if not orders:
        print("Nothing to do.")
    if send and orders:
        if not request("GET", "/v2/clock").get("is_open"):
            print("Market closed: option orders wait for the next run during market hours.")
        else:
            from . import notify

            for o in orders:
                try:
                    if o["side"] == "sell":
                        snap = get_data("/v1beta1/options/snapshots", {"symbols": o["symbol"], "feed": "indicative"})
                        bid = float(snap["snapshots"][o["symbol"]]["latestQuote"]["bp"])
                        px = max(bid, 0.01)
                    else:
                        px = o["limit"]
                    r = request("POST", "/v2/orders", {"symbol": o["symbol"], "qty": str(o["qty"]), "side": o["side"],
                                                       "type": "limit", "limit_price": f"{px:.2f}",
                                                       "time_in_force": "day"})
                    time.sleep(5)
                    st = request("GET", f"/v2/orders/{r['id']}")
                    log_fill(o, st)
                    print(f"  -> {st.get('status')}, filled {st.get('filled_qty')} at {st.get('filled_avg_price')}")
                    notify.send(f"[F – Options] {o['side'].upper()} {o['qty']} {o['underlying']} calls", o["why"])
                except AlpacaError as e:
                    print(f"  -> REFUSED: {e}")
                    log_fill(o, {"filled_qty": 0})
    write_status(acct, held_options() if send else held)
    return orders


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync")
    s.add_argument("--send", action="store_true")
    args = ap.parse_args()
    if args.cmd == "sync":
        sync(args.send)


if __name__ == "__main__":
    main()
