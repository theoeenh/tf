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

From 2026-10-20 (user's go): a fifth playbook, `spy_put_spread`, the income idea of
paper/research/2026-10-11-account-F-put-selling.md: one new SPY put spread a week (sell ~0.25 delta,
buy ~0.10 delta below, or nearer if one spread would risk more than ~3% of equity; 30-45 days
out), at most 4 open, ~3% of equity at risk each, out at half the
credit earned or 21 days before expiry. The account's config.json chooses the active playbooks
("playbooks") and whose stock signals the others follow ("signals": "A" = account A, "D" = account D,
the insider candidate). Positions opened before a switch keep the source they were opened on.
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
SOURCES = {"A": ROOT / "paper" / "orders.json", "D": ROOT / "paper" / "D" / "orders.json"}
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
    # selling insurance on the S&P 500 on a timetable, no stock signal (see the docstring)
    "spy_put_spread": {"bias": 1, "type": "put", "legs": [(-1, -0.25), (+1, -0.10)], "underlying": "SPY",
                       "dte": (30, 45), "exit_dte": 21, "min_credit": 0.08, "short_tol": 0.10, "fit_width": True,
                       "max_open": 4, "every_days": 7},
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

def chain(und: str, kind: str, spot: float, today: pd.Timestamp, dte: tuple[int, int] | None = None) -> list[dict]:
    """Option contracts 30-60 days out (or `dte`) around the price, with their quote and delta."""
    lo, hi = dte or (DTE_MIN, DTE_MAX)
    q = (f"/v2/options/contracts?underlying_symbols={und}&type={kind}&status=active"
         f"&expiration_date_gte={(today + pd.Timedelta(days=lo)).date()}"
         f"&expiration_date_lte={(today + pd.Timedelta(days=hi)).date()}"
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
    if short is None or abs(short["delta"] - s_delta) > pb.get("short_tol", 0.12):
        return None
    longs = [c for c in cs if c["expiry"] == short["expiry"]
             and (c["strike"] < short["strike"] if pb["type"] == "put" else c["strike"] > short["strike"])]
    if pb.get("fit_width"):  # the protective leg nearest its delta among those where one spread fits the budget
        longs = [c for c in longs
                 if (abs(short["strike"] - c["strike"]) - (short["bid"] - c["ask"])) * 100 <= RISK * equity]
    long = nearest(longs, l_delta)
    if long is None:
        return None
    credit = short["bid"] - long["ask"]
    width = abs(short["strike"] - long["strike"])
    if credit < pb.get("min_credit", 0.15) * width:  # too little reward for the risk (a fair 0.30/0.15
        return None                                     # spread brings ~18%, a 0.25/0.10 one ~12-15%)
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


def exits(book: dict, bull: dict, trend: dict, today: pd.Timestamp, close_cost,
          bulls: dict[str, dict] | None = None) -> list[tuple[dict, str]]:
    """Open positions to close now, with the reason. close_cost(pos) -> what closing costs now ($).
    `bulls`: the bullish signals of each source account; a position follows the source it was opened on
    (positions from before the switch: account A, i.e. `bull`)."""
    out = []
    for p in book["open"]:
        pb = PLAYBOOKS[p["playbook"]]
        dte = (pd.Timestamp(p["expiry"]) - today).days
        src = p.get("source", "A")
        held = (bulls or {}).get(src, bull)
        why = None
        if dte <= pb.get("exit_dte", DTE_EXIT):
            why = f"{dte} days to expiry"
        elif pb.get("underlying"):  # a timetable playbook: no stock signal to follow
            pass
        elif pb["bias"] > 0 and p["underlying"] not in held:
            why = f"account {src} closed the stock"
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


def entries(book: dict, bull: dict, bear: dict, equity: float, chain_for, active=None,
            today: pd.Timestamp | None = None, spots: dict | None = None, source: str = "A") -> list[dict]:
    """New positions: fresh signals, playbook limits, one position per stock and playbook; timetable
    playbooks (a fixed underlying) open one position every `every_days` days, up to `max_open`."""
    out = []
    for name, pb in PLAYBOOKS.items():
        if active is not None and name not in active:
            continue
        held = [p for p in book["open"] if p["playbook"] == name]
        if pb.get("underlying"):
            und, spot = pb["underlying"], (spots or {}).get(pb["underlying"])
            mine = held + [p for p in book["closed"] if p["playbook"] == name]
            last = max((pd.Timestamp(p["opened"]).normalize() for p in mine), default=None)
            if (spot and today is not None and len(held) < pb["max_open"]
                    and (last is None or (today - last).days >= pb["every_days"])):
                d = design(name, chain_for(und, pb["type"], spot, pb["dte"]), equity)
                if d is not None:
                    out.append({"playbook": name, "underlying": und, **d})
            continue
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
            out.append({"playbook": name, "underlying": und, "source": source, **d})
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


def _market(sym: str, side: str, qty: int) -> dict:
    """A market order (an unwind that must not stay open), waited for like _order."""
    r = request("POST", "/v2/orders", {"symbol": sym, "qty": str(qty), "side": side, "type": "market",
                                       "time_in_force": "day"})
    for _ in range(10):
        time.sleep(2)
        st = request("GET", f"/v2/orders/{r['id']}")
        if st.get("status") in ("filled", "canceled", "rejected", "expired"):
            return st
    return request("GET", f"/v2/orders/{r['id']}")


def open_legs(p: dict) -> list[dict]:
    """The legs of a position still held (a close that stopped half-way has closed the others)."""
    done = set(p.get("done_legs", []))
    return [leg for leg in p["legs"] if leg["symbol"] not in done]


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
    total = -p.get("partial", 0.0)  # cash already received from legs closed by an earlier attempt
    for leg in open_legs(p):
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
            part = int(float(st.get("filled_qty") or 0))
            if part:  # a leg that filled in part is unwound too
                done.append(leg | {"qty": part if leg["qty"] > 0 else -part})
            for d in done:  # unwind what was opened
                back = "sell" if d["qty"] > 0 else "buy"
                q = quotes([d["symbol"]]).get(d["symbol"], {})
                px = float((q.get("bp") if back == "sell" else q.get("ap")) or d["price"])
                st2 = _order(d["symbol"], back, abs(d["qty"]), px)
                _log(d["symbol"], pos["underlying"], pos["playbook"], back, abs(d["qty"]), st2, "unwind")
                if st2.get("status") != "filled":  # 2026-10-22: 8 legs were left at Alpaca this way
                    left = abs(d["qty"]) - int(float(st2.get("filled_qty") or 0))
                    st3 = _market(d["symbol"], back, left)
                    _log(d["symbol"], pos["underlying"], pos["playbook"], back, left, st3, "unwind at market")
            return None
        done.append(leg | {"price": float(st["filled_avg_price"])})
    cost = sum(leg["qty"] * leg["price"] * 100 for leg in done)
    return pos | {"legs": done, "cost": cost, "opened": str(pd.Timestamp.now(tz="UTC").tz_localize(None))[:16],
                  "id": f"{pos['playbook']}-{pos['underlying']}-{today.date()}"}


def close_position(p: dict, why: str) -> float | None:
    """Short legs first (no naked short in between), then long legs. Returns the $ received (net), or
    None when a leg did not fill: the legs already closed are remembered in the position (done_legs,
    partial cash) so the next attempt closes only the rest (2026-10-22: a retry would have bought back
    an IWM short call already bought back, opening a new long call)."""
    legs = open_legs(p)
    q = quotes([leg["symbol"] for leg in legs])
    got = p.get("partial", 0.0)
    for leg in sorted(legs, key=lambda leg: leg["qty"] > 0):
        side = "buy" if leg["qty"] < 0 else "sell"
        qq = q.get(leg["symbol"]) or {}
        px = float((qq.get("ap") if side == "buy" else qq.get("bp")) or 0.01)
        st = _order(leg["symbol"], side, abs(leg["qty"]), px)
        _log(leg["symbol"], p["underlying"], p["playbook"], side, abs(leg["qty"]), st, "close: " + why)
        if st.get("status") != "filled":
            part = int(float(st.get("filled_qty") or 0))
            if part:  # the rest of this leg stays open
                got += (1 if side == "sell" else -1) * part * float(st["filled_avg_price"]) * 100
                leg["qty"] += part if leg["qty"] < 0 else -part
            p["partial"] = got
            return None
        got += (1 if side == "sell" else -1) * abs(leg["qty"]) * float(st["filled_avg_price"]) * 100
        p["done_legs"] = p.get("done_legs", []) + [leg["symbol"]]
    return got


# ------------------------------------------------------------------ run

def config() -> dict:
    p = PAPER_DIR / "config.json"
    return json.loads(p.read_text()) if p.exists() else {}


def book_qty(book: dict) -> dict[str, float]:
    """Contracts per option symbol the book holds (legs a half-done close has closed left out)."""
    want: dict[str, float] = {}
    for p in book["open"]:
        for leg in open_legs(p):
            want[leg["symbol"]] = want.get(leg["symbol"], 0) + leg["qty"]
    return want


def close_leftovers(book: dict, approved: dict, positions: list[dict], today: pd.Timestamp,
                    trade: bool) -> list[tuple[str, dict]]:
    """Sell the long option legs Alpaca holds beyond the book (left by the order bugs fixed on 22 Oct),
    only those the user approved: config "close_leftovers" = {"until": date, "legs": {symbol: contracts}}
    (user's go 2026-10-24). Never more than Alpaca holds beyond the book, so the book's own legs stay.
    Limit at the bid first, then at market for what is left. Returns (symbol, order) per leg sold."""
    if not trade or not approved or today > pd.Timestamp(approved.get("until", "1900-01-01")):
        return []
    want = book_qty(book)
    have = {p["symbol"]: float(p["qty"]) for p in positions}
    todo = {s: int(min(n, have.get(s, 0) - want.get(s, 0))) for s, n in approved.get("legs", {}).items()}
    todo = {s: n for s, n in todo.items() if n > 0}
    q = quotes(sorted(todo)) if todo else {}
    out = []
    for sym, n in sorted(todo.items()):
        und = sym[:-15]  # OCC symbol: root + YYMMDD + C/P + 8-digit strike
        bid = float((q.get(sym) or {}).get("bp") or 0.01)
        st = _order(sym, "sell", n, bid)
        why = "leftover leg (not in the book), sold with the user's go of 2026-10-24"
        _log(sym, und, "leftover", "sell", n, st, why)
        if st.get("status") != "filled":
            left = n - int(float(st.get("filled_qty") or 0))
            st = _market(sym, "sell", left)
            _log(sym, und, "leftover", "sell", left, st, why + ", at market")
        out.append((sym, st))
    return out


def reconcile(book: dict, q: dict, positions: list[dict]) -> list[str]:
    """Alpaca's positions next to the book's legs: the legs only one side has, and each leg's value at
    Alpaca against its value at the quotes' mid. F's equity is Alpaca's, so a leg Alpaca prices far from
    the quotes, or one the book does not know, moves it without any trade (2026-10-22: Alpaca's equity
    rose $9,450 while the book's positions gained about $1,650 on the day's moves)."""
    want = book_qty(book)
    have = {p["symbol"]: p for p in positions}
    rows, at_alpaca, at_mid = [], 0.0, 0.0
    for sym in sorted(set(want) | set(have)):
        qty, value = float(have.get(sym, {}).get("qty", 0)), float(have.get(sym, {}).get("market_value", 0))
        bid, ask = (float((q.get(sym) or {}).get(k) or 0) for k in ("bp", "ap"))
        mid = qty * (bid + ask) / 2 * 100 if bid > 0 and ask > 0 else None
        flags = [f"book {want.get(sym, 0):g}"] if qty != want.get(sym, 0) else []
        if mid is None and qty:
            flags.append("no quote")
        elif mid is not None and abs(value - mid) > max(100.0, 0.2 * abs(mid)):
            flags.append("Alpaca's price far from the quotes")
        at_alpaca += value
        at_mid += mid or 0.0
        rows.append(f"| {sym} | {qty:g} | ${value:,.0f} | {'-' if mid is None else f'${mid:,.0f}'} | "
                    f"{', '.join(flags) or 'ok'} |")
    return ["", "## Alpaca vs book", "",
            f"Alpaca values the positions at ${at_alpaca:,.0f}; at the quotes' mid they are worth ${at_mid:,.0f} "
            f"(difference ${at_alpaca - at_mid:+,.0f}).", "",
            "| leg | Alpaca qty | Alpaca value | value at mid | check |", "|---|---|---|---|---|", *rows]


def write_status(acct: dict, book: dict, q: dict, positions: list[dict] | None = None) -> None:
    eq = float(acct.get("equity", 0))
    cfg = config()
    active = cfg.get("playbooks", list(PLAYBOOKS))
    lines = [f"# {cfg.get('name', 'F')}", "",
             f"Updated {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC. **Equity ${eq:,.0f}** "
             f"({eq / 100_000 - 1:+.2%} since start). {cfg.get('summary', '')}".rstrip(),
             "", f"Active playbooks: {', '.join(active)}; stock signals from account {cfg.get('signals', 'A')}.",
             "", "| playbook | open | closed | realised P&L | open P&L | wins / closed |", "|---|---|---|---|---|---|"]
    shown = [n for n in PLAYBOOKS if n in active or any(p["playbook"] == n for p in book["open"] + book["closed"])]
    for name in shown:
        op = [p for p in book["open"] if p["playbook"] == name]
        cl = [p for p in book["closed"] if p["playbook"] == name]
        real = sum(p.get("pnl", 0) for p in cl)
        unreal = sum(-(close_cost(p, q) or 0) - p["cost"] for p in op if close_cost(p, q) is not None)
        wins = sum(p.get("pnl", 0) > 0 for p in cl)
        lines.append(f"| {name} | {len(op)} | {len(cl)} | ${real:+,.0f} | ${unreal:+,.0f} | {wins} / {len(cl)} |")
    lines += ["", "## Open positions", ""] + ([f"- **{p['playbook']}** {p['underlying']}: {p['desc']} (opened "
                                              f"{p['opened']}, cost ${p['cost']:+,.0f}, most it can lose "
                                              f"${p['max_loss']:,.0f})" for p in book["open"]] or ["None."])
    if positions is not None:
        lines += reconcile(book, q, positions)
    (PAPER_DIR / "status.md").write_text("\n".join(lines) + "\n")


def sync(send: bool = False) -> None:
    from .paper import complete_bars
    from .system import UNIVERSE_WIDE, load_prices

    from .alpaca import live_prices

    num = check_account()
    acct = request("GET", "/v2/account")
    equity = float(acct["equity"])
    today = pd.Timestamp.now(tz="America/New_York").tz_localize(None).normalize()
    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    cfg = config()
    active = cfg.get("playbooks", list(PLAYBOOKS))
    source = cfg.get("signals", "A")
    bulls = {k: bullish(json.loads(f.read_text())) if f.exists() else {} for k, f in SOURCES.items()}
    bull = bulls.get(source, {})
    book = load_book()
    bear_play = any(PLAYBOOKS[n]["bias"] < 0 for n in active) or any(
        PLAYBOOKS[p["playbook"]]["bias"] < 0 for p in book["open"])
    bear, trend = {}, {}
    if bear_play:  # the bearish playbooks (signals and daily-trend exits) need the hourly prices
        prices = {a: complete_bars(df, a, "1h", now) for a, df in
                  load_prices("alpaca", "1h", [a for a in UNIVERSE_WIDE if a not in CRYPTO]).items()}
        bear, trend = bearish(prices), trends(prices)
    fixed = sorted({PLAYBOOKS[n]["underlying"] for n in active if PLAYBOOKS[n].get("underlying")})
    try:
        spots = live_prices(fixed) if fixed else {}
    except AlpacaError as e:
        print(f"No price for {', '.join(fixed)} ({e}); timetable playbooks wait.")
        spots = {}
    q = quotes(sorted({leg["symbol"] for p in book["open"] for leg in p["legs"]})) if book["open"] else {}
    print(f"Alpaca account {num}: {cfg.get('name', 'F')}, equity ${equity:,.0f}; active {active}; "
          f"bullish ({source}) {sorted(bull)}, bearish {sorted(bear)}; {len(book['open'])} open position(s)")
    is_open = request("GET", "/v2/clock").get("is_open")
    if send and not is_open:
        print("Market closed: option orders wait for a run during market hours.")
    trade = send and is_open

    for p, why in exits(book, bulls.get("A", {}), trend, today, lambda p: close_cost(p, q), bulls):
        print(f"CLOSE {p['playbook']} {p['underlying']}: {why}")
        if trade:
            got = close_position(p, why)
            if got is not None:
                book["open"].remove(p)
                book["closed"].append(p | {"closed": str(now)[:16], "why_closed": why, "pnl": got - p["cost"]})
                save_book(book)

    leftovers = cfg.get("close_leftovers")
    if leftovers and trade:
        try:
            held = request("GET", "/v2/positions")
        except (AlpacaError, OSError) as e:
            print(f"No Alpaca positions for the leftover legs ({e}): the next run sells them.")
            held = []
        for sym, st in close_leftovers(book, leftovers, held, today, trade):
            print(f"SOLD  leftover {sym}: {st.get('status')}, {st.get('filled_qty')} at {st.get('filled_avg_price')}")
    elif leftovers:
        print("Leftover legs approved for sale: sold by the first run during market hours.")

    def chain_for(und, kind, spot, dte=None):
        try:
            return chain(und, kind, spot, today, dte)
        except AlpacaError as e:
            print(f"  no option chain for {und} ({e})")
            return []

    for pos in entries(book, bull, bear, equity, chain_for, active, today, spots, source):
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
    try:  # what Alpaca holds, for the check against the book (status.md only: nothing is traded on it)
        positions = request("GET", "/v2/positions")
        extra = sorted(p["symbol"] for p in positions if p["symbol"] not in q and any(c.isdigit() for c in p["symbol"]))
        q = q | (quotes(extra) if extra else {})
    except (AlpacaError, OSError) as e:
        print(f"No Alpaca positions for the check against the book ({e}).")
        positions = None
    write_status(acct, book, q, positions)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync")
    s.add_argument("--send", action="store_true")
    args = ap.parse_args()
    sync(args.send)


if __name__ == "__main__":
    main()
