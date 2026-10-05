"""Account F: four option playbooks on the stock signals, each with its loss capped in advance.

    PAPER_ACCOUNT=F python -m algo.options sync          # show what it would do (dry run)
    PAPER_ACCOUNT=F python -m algo.options sync --send   # trade (US market hours only)

A test of the machinery (the stock signals have no proven edge yet, see paper/research): the point
is to learn how option entries, fills, exits and expiries behave, so a real edge can be put behind
them later. Four playbooks run side by side and are scored separately:

| playbook | when | position | most it can lose |
|---|---|---|---|
| long_call | account A opens a long (fresh) | buy a call, delta ~0.60 | the premium |
| long_put | a fresh short signal of the same strategies (daily downtrend) | buy a put, delta ~-0.60 | the premium |
| bull_put_spread | account A opens a long | sell a put (delta ~-0.30), buy a put below (~-0.15) | width - credit |
| bear_call_spread | a fresh short signal | sell a call (delta ~0.30), buy a call above (~0.15) | width - credit |

All: expiry 30-60 days, bid-ask spread at most 15% per leg, at most ~3% of F's equity at risk per
position, at most 3 positions per playbook and one per stock. Exits, checked every run:
- bullish playbooks: when A no longer holds the stock; bearish ones: when the stock's daily trend
  turns up or after 15 days;
- spreads: once 50% of the credit is earned (buying the spread back costs half what it brought);
- everything: 10 days before expiry.
Alpaca allows no naked short options: a spread buys its protective leg first, then sells the other
(closing: buys back the short leg first). Limit orders at the ask (buying) / bid (selling), day
orders, only while the market is open. Prices: Alpaca's free 'indicative' option feed.
The book of positions (which playbook each contract belongs to) is paper/F/book.json; every order
goes to paper/F/fills.csv; paper/F/status.md has the score per playbook.
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
MAX_SPREAD = 0.15
RISK = 0.03  # most a position can lose, share of equity
MAX_PER_BOOK = 3
FRESH_R = (-0.3, 0.5)
BEAR_DAYS = 15
TAKE_PROFIT = 0.5  # spreads: close once half the credit is earned
PLAYBOOKS = {
    "long_call": {"bias": 1, "type": "call", "legs": [(+1, 0.60)]},
    "long_put": {"bias": -1, "type": "put", "legs": [(+1, -0.60)]},
    "bull_put_spread": {"bias": 1, "type": "put", "legs": [(-1, -0.30), (+1, -0.15)]},
    "bear_call_spread": {"bias": -1, "type": "call", "legs": [(-1, 0.30), (+1, 0.15)]},
}


# ------------------------------------------------------------------ signals

def bullish(plan: list[dict]) -> dict[str, dict]:
    """Stocks / ETFs account A holds long: symbol -> {r, spot} (the best trade per stock)."""
    out: dict[str, dict] = {}
    for t in plan:
        if t["asset"] in CRYPTO or t["qty"] <= 0:
            continue
        sym = ALPACA_SYMBOLS.get(t["asset"], t["asset"])
        r = float(t.get("r") or 0.0)
        if sym not in out or r > out[sym]["r"]:
            out[sym] = {"r": r, "spot": float(t["mark"])}
    return out


def bearish(prices: dict) -> dict[str, dict]:
    """Fresh short signals on the last complete bar (the accounts' strategies, daily downtrend only):
    symbol -> {spot, trend}; also returns the daily trend of every stock for the bearish exits."""
    from .system import build_sleeves

    out = {}
    for s in build_sleeves(prices, True, None, news=False, trend=True, intraday_strats=False):
        sig = s.signals.reindex(prices[s.asset].index).fillna(0)
        if len(sig) >= 2 and sig.iloc[-1] < 0 <= sig.iloc[-2]:
            sym = ALPACA_SYMBOLS.get(s.asset, s.asset)
            out[sym] = {"spot": float(prices[s.asset]["Close"].iloc[-1]), "strategy": s.strategy}
    return out


def trends(prices: dict) -> dict[str, int]:
    from .strategies import daily_trend

    return {ALPACA_SYMBOLS.get(a, a): int(daily_trend(df).iloc[-1]) for a, df in prices.items() if len(df)}


# ------------------------------------------------------------------ contracts

def chain(und: str, kind: str, spot: float, today: pd.Timestamp) -> list[dict]:
    """Option contracts 30-60 days out around the price, with their quote and delta."""
    q = (f"/v2/options/contracts?underlying_symbols={und}&type={kind}&status=active"
         f"&expiration_date_gte={(today + pd.Timedelta(days=DTE_MIN)).date()}"
         f"&expiration_date_lte={(today + pd.Timedelta(days=DTE_MAX)).date()}"
         f"&strike_price_gte={spot * 0.75:.2f}&strike_price_lte={spot * 1.25:.2f}&limit=500")
    cs = request("GET", q).get("option_contracts", [])
    snaps = {}
    for i in range(0, len(cs), 100):
        syms = ",".join(c["symbol"] for c in cs[i:i + 100])
        snaps |= get_data("/v1beta1/options/snapshots", {"symbols": syms, "feed": "indicative"}).get("snapshots", {})
    out = []
    for c in cs:
        s = snaps.get(c["symbol"]) or {}
        q_, g = s.get("latestQuote") or {}, s.get("greeks") or {}
        bid, ask, delta = float(q_.get("bp") or 0), float(q_.get("ap") or 0), g.get("delta")
        if delta is None or bid <= 0 or ask <= 0 or (ask - bid) / ((ask + bid) / 2) > MAX_SPREAD:
            continue
        out.append({"symbol": c["symbol"], "expiry": c["expiration_date"], "strike": float(c["strike_price"]),
                    "bid": bid, "ask": ask, "delta": float(delta), "name": c.get("name", c["symbol"])})
    return out


def nearest(cs: list[dict], delta: float, expiry: str | None = None) -> dict | None:
    pool = [c for c in cs if expiry is None or c["expiry"] == expiry]
    return min(pool, key=lambda c: abs(c["delta"] - delta), default=None)


def design(playbook: str, cs: list[dict], equity: float) -> dict | None:
    """The position a playbook would open from a chain: legs, quantity, cost and most it can lose."""
    pb = PLAYBOOKS[playbook]
    if len(pb["legs"]) == 1:
        c = nearest(cs, pb["legs"][0][1])
        if c is None or abs(c["delta"] - pb["legs"][0][1]) > 0.15:
            return None
        n = math.floor(RISK * equity / (c["ask"] * 100))
        if n < 1:
            return None
        return {"legs": [{"symbol": c["symbol"], "qty": n, "price": c["ask"]}], "expiry": c["expiry"],
                "cost": c["ask"] * 100 * n, "max_loss": c["ask"] * 100 * n,
                "desc": f"{c['name']}, delta {c['delta']:+.2f}"}
    (s_side, s_delta), (l_side, l_delta) = pb["legs"]
    short = nearest(cs, s_delta)
    if short is None or abs(short["delta"] - s_delta) > 0.12:
        return None
    longs = [c for c in cs if c["expiry"] == short["expiry"]
             and (c["strike"] < short["strike"] if pb["type"] == "put" else c["strike"] > short["strike"])]
    long = nearest(longs, l_delta)
    if long is None:
        return None
    credit = short["bid"] - long["ask"]
    width = abs(short["strike"] - long["strike"])
    if credit < 0.15 * width:  # too little reward for the risk (a fair 0.30/0.15 spread brings ~18%)
        return None
    loss_each = (width - credit) * 100
    n = math.floor(RISK * equity / loss_each)
    if n < 1:
        return None
    return {"legs": [{"symbol": long["symbol"], "qty": n, "price": long["ask"]},
                     {"symbol": short["symbol"], "qty": -n, "price": short["bid"]}],
            "expiry": short["expiry"], "cost": -credit * 100 * n, "max_loss": loss_each * n,
            "desc": f"sell {short['strike']:g} / buy {long['strike']:g} {pb['type']}s, {short['expiry']}, "
                    f"credit {credit:.2f} on width {width:g}"}


# ------------------------------------------------------------------ the book

def load_book() -> dict:
    p = PAPER_DIR / "book.json"
    return json.loads(p.read_text()) if p.exists() else {"open": [], "closed": []}


def save_book(book: dict) -> None:
    (PAPER_DIR / "book.json").write_text(json.dumps(book, indent=1))


def exits(book: dict, bull: dict, trend: dict, today: pd.Timestamp, close_cost) -> list[tuple[dict, str]]:
    """Open positions to close now, with the reason. close_cost(pos) -> what closing costs now ($)."""
    out = []
    for p in book["open"]:
        pb = PLAYBOOKS[p["playbook"]]
        dte = (pd.Timestamp(p["expiry"]) - today).days
        why = None
        if dte <= DTE_EXIT:
            why = f"{dte} days to expiry"
        elif pb["bias"] > 0 and p["underlying"] not in bull:
            why = "account A closed the stock"
        elif pb["bias"] < 0 and (trend.get(p["underlying"], 0) > 0
                                 or (today - pd.Timestamp(p["opened"]).normalize()).days >= BEAR_DAYS):
            why = "daily trend turned up" if trend.get(p["underlying"], 0) > 0 else f"{BEAR_DAYS} days held"
        elif len(pb["legs"]) == 2:
            cost_now = close_cost(p)
            if cost_now is not None and cost_now <= TAKE_PROFIT * -p["cost"]:
                why = f"half the credit earned (buy back ${cost_now:,.0f} vs ${-p['cost']:,.0f} received)"
        if why:
            out.append((p, why))
    return out


def entries(book: dict, bull: dict, bear: dict, equity: float, chain_for) -> list[dict]:
    """New positions: fresh signals, playbook limits, one position per stock and playbook."""
    out = []
    for name, pb in PLAYBOOKS.items():
        held = [p for p in book["open"] if p["playbook"] == name]
        busy = {p["underlying"] for p in held}
        room = MAX_PER_BOOK - len(held)
        signals = ({u: v for u, v in bull.items() if FRESH_R[0] <= v["r"] <= FRESH_R[1]} if pb["bias"] > 0 else bear)
        for und, v in sorted(signals.items()):
            if room <= 0:
                break
            if und in busy:
                continue
            d = design(name, chain_for(und, pb["type"], v["spot"]), equity)
            if d is None:
                continue
            out.append({"playbook": name, "underlying": und, **d})
            room -= 1
    return out


# ------------------------------------------------------------------ orders

def _log(sym: str, und: str, playbook: str, side: str, qty: int, st: dict, why: str) -> None:
    f = PAPER_DIR / "fills.csv"
    if not f.exists():
        f.write_text("time,playbook,underlying,symbol,side,qty,filled_qty,avg_price,status,why\n")
    with f.open("a") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())},{playbook},{und},{sym},{side},{qty},"
                 f"{st.get('filled_qty', 0)},{st.get('filled_avg_price') or ''},{st.get('status', '')},\"{why}\"\n")


def _order(sym: str, side: str, qty: int, price: float) -> dict:
    r = request("POST", "/v2/orders", {"symbol": sym, "qty": str(qty), "side": side, "type": "limit",
                                       "limit_price": f"{max(price, 0.01):.2f}", "time_in_force": "day"})
    for _ in range(10):
        time.sleep(2)
        st = request("GET", f"/v2/orders/{r['id']}")
        if st.get("status") in ("filled", "canceled", "rejected", "expired"):
            return st
    request("DELETE", f"/v2/orders/{r['id']}")  # not filled at our price: no chase
    time.sleep(2)
    return request("GET", f"/v2/orders/{r['id']}")


def quotes(symbols: list[str]) -> dict[str, dict]:
    out = {}
    for i in range(0, len(symbols), 100):
        s = get_data("/v1beta1/options/snapshots", {"symbols": ",".join(symbols[i:i + 100]), "feed": "indicative"})
        out |= {k: v.get("latestQuote") or {} for k, v in s.get("snapshots", {}).items()}
    return out


def close_cost(p: dict, q: dict) -> float | None:
    """$ it takes to close a position now: buy back short legs at the ask, sell long legs at the bid."""
    total = 0.0
    for leg in p["legs"]:
        qq = q.get(leg["symbol"]) or {}
        px = float((qq.get("ap") if leg["qty"] < 0 else qq.get("bp")) or 0)
        if px <= 0:
            return None
        total += -leg["qty"] * px * 100
    return total


def open_position(pos: dict, today: pd.Timestamp) -> dict | None:
    """Long legs first (protection), then short legs; undo the first if the second fails."""
    done = []
    for leg in sorted(pos["legs"], key=lambda leg: leg["qty"] < 0):
        side = "buy" if leg["qty"] > 0 else "sell"
        st = _order(leg["symbol"], side, abs(leg["qty"]), leg["price"])
        _log(leg["symbol"], pos["underlying"], pos["playbook"], side, abs(leg["qty"]), st, "open: " + pos["desc"])
        if st.get("status") != "filled":
            for d in done:  # unwind what was opened
                back = "sell" if d["qty"] > 0 else "buy"
                q = quotes([d["symbol"]]).get(d["symbol"], {})
                px = float((q.get("bp") if back == "sell" else q.get("ap")) or d["price"])
                st2 = _order(d["symbol"], back, abs(d["qty"]), px)
                _log(d["symbol"], pos["underlying"], pos["playbook"], back, abs(d["qty"]), st2, "unwind")
            return None
        done.append(leg | {"price": float(st["filled_avg_price"])})
    cost = sum(leg["qty"] * leg["price"] * 100 for leg in done)
    return pos | {"legs": done, "cost": cost, "opened": str(pd.Timestamp.now(tz="UTC").tz_localize(None))[:16],
                  "id": f"{pos['playbook']}-{pos['underlying']}-{today.date()}"}


def close_position(p: dict, why: str) -> float | None:
    """Short legs first (no naked short in between), then long legs. Returns the $ received (net)."""
    q = quotes([leg["symbol"] for leg in p["legs"]])
    got = 0.0
    for leg in sorted(p["legs"], key=lambda leg: leg["qty"] > 0):
        side = "buy" if leg["qty"] < 0 else "sell"
        qq = q.get(leg["symbol"]) or {}
        px = float((qq.get("ap") if side == "buy" else qq.get("bp")) or 0.01)
        st = _order(leg["symbol"], side, abs(leg["qty"]), px)
        _log(leg["symbol"], p["underlying"], p["playbook"], side, abs(leg["qty"]), st, "close: " + why)
        if st.get("status") != "filled":
            return None
        got += (1 if side == "sell" else -1) * abs(leg["qty"]) * float(st["filled_avg_price"]) * 100
    return got


# ------------------------------------------------------------------ run

def write_status(acct: dict, book: dict, q: dict) -> None:
    eq = float(acct.get("equity", 0))
    lines = [f"# {json.loads((PAPER_DIR / 'config.json').read_text()).get('name', 'F')}", "",
             f"Updated {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC. **Equity ${eq:,.0f}** "
             f"({eq / 100_000 - 1:+.2%} since start). A test of option mechanics on signals with no proven edge.",
             "", "| playbook | open | closed | realised P&L | open P&L | wins / closed |", "|---|---|---|---|---|---|"]
    for name in PLAYBOOKS:
        op = [p for p in book["open"] if p["playbook"] == name]
        cl = [p for p in book["closed"] if p["playbook"] == name]
        real = sum(p.get("pnl", 0) for p in cl)
        unreal = sum(-(close_cost(p, q) or 0) - p["cost"] for p in op if close_cost(p, q) is not None)
        wins = sum(p.get("pnl", 0) > 0 for p in cl)
        lines.append(f"| {name} | {len(op)} | {len(cl)} | ${real:+,.0f} | ${unreal:+,.0f} | {wins} / {len(cl)} |")
    lines += ["", "## Open positions", ""] + ([f"- **{p['playbook']}** {p['underlying']}: {p['desc']} (opened "
                                              f"{p['opened']}, cost ${p['cost']:+,.0f}, most it can lose "
                                              f"${p['max_loss']:,.0f})" for p in book["open"]] or ["None."])
    (PAPER_DIR / "status.md").write_text("\n".join(lines) + "\n")


def sync(send: bool = False) -> None:
    from .paper import complete_bars
    from .system import UNIVERSE_WIDE, load_prices

    num = check_account()
    acct = request("GET", "/v2/account")
    equity = float(acct["equity"])
    today = pd.Timestamp.now(tz="America/New_York").tz_localize(None).normalize()
    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    plan = json.loads(SIGNALS.read_text())
    prices = {a: complete_bars(df, a, "1h", now) for a, df in
              load_prices("alpaca", "1h", [a for a in UNIVERSE_WIDE if a not in CRYPTO]).items()}
    bull, bear, trend = bullish(plan), bearish(prices), trends(prices)
    book = load_book()
    q = quotes(sorted({leg["symbol"] for p in book["open"] for leg in p["legs"]})) if book["open"] else {}
    print(f"Alpaca account {num}: F – Options, equity ${equity:,.0f}; bullish {sorted(bull)}, "
          f"bearish {sorted(bear)}; {len(book['open'])} open position(s)")
    is_open = request("GET", "/v2/clock").get("is_open")
    if send and not is_open:
        print("Market closed: option orders wait for a run during market hours.")
    trade = send and is_open

    for p, why in exits(book, bull, trend, today, lambda p: close_cost(p, q)):
        print(f"CLOSE {p['playbook']} {p['underlying']}: {why}")
        if trade:
            got = close_position(p, why)
            if got is not None:
                book["open"].remove(p)
                book["closed"].append(p | {"closed": str(now)[:16], "why_closed": why, "pnl": got - p["cost"]})
                save_book(book)

    def chain_for(und, kind, spot):
        try:
            return chain(und, kind, spot, today)
        except AlpacaError as e:
            print(f"  no option chain for {und} ({e})")
            return []

    for pos in entries(book, bull, bear, equity, chain_for):
        print(f"OPEN  {pos['playbook']} {pos['underlying']}: {pos['desc']}, cost ${pos['cost']:+,.0f}, "
              f"most it can lose ${pos['max_loss']:,.0f}")
        if trade:
            done = open_position(pos, today)
            if done:
                book["open"].append(done)
                save_book(book)
                from . import notify

                notify.send(f"[F – Options] {pos['playbook']} {pos['underlying']}",
                            f"{pos['desc']}; most it can lose ${pos['max_loss']:,.0f}")
    q = quotes(sorted({leg["symbol"] for p in book["open"] for leg in p["legs"]})) if book["open"] else {}
    save_book(book)
    write_status(acct, book, q)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync")
    s.add_argument("--send", action="store_true")
    args = ap.parse_args()
    sync(args.send)


if __name__ == "__main__":
    main()
