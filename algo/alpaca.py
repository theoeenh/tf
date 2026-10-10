"""Mirror the paper account on an Alpaca *paper* account, with real stop and
target orders at the broker.

    python -m algo.alpaca check      # test the keys, show the Alpaca paper account
    python -m algo.alpaca sync       # show the orders that would be sent (dry run)
    python -m algo.alpaca sync --send

Keys come from environment variables ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY
(Alpaca dashboard -> Paper account -> API Keys). Only the paper endpoint is
used; there is no switch to live trading in this file on purpose.

How `sync` works, each run:
1. Cancel our open orders (the stops and targets of the last run).
2. Our system can hold several trades in the same asset (one per strategy);
   Alpaca keeps one net position per symbol. Add up the wanted positions from
   paper/orders.json per symbol and send market orders for the difference
   (crypto: a limit at the bid / ask first for the lower maker fee, the rest
   at market after 2 minutes; see crypto_limit_first).
3. Once filled, protect every trade at the broker, so a stop fires the moment
   the price gets there, not at our next run:
   - stocks / ETFs: stop + target as one OCO order (one cancels the other) for
     the whole shares, a plain stop for the fractional rest;
   - crypto: a stop-limit order (Alpaca has no plain stop for crypto); the
     target is taken by the next run once the system sees it hit.
   A trade whose price is already through its stop is closed at market.
   Stock orders queued while the market is closed are protected by the first
   run after they fill.
Limits: Alpaca cannot short crypto, so crypto shorts are skipped; stock shorts
are rounded down to whole shares (no fractional shorts).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from .data import ALPACA_SYMBOLS, CRYPTO
from .paper import PAPER_DIR

BASE_URL = "https://paper-api.alpaca.markets"
DATA_URL = "https://data.alpaca.markets"
class _Symbols(dict):
    """Our asset names -> Alpaca symbols; any other stock (the S&P 1500 accounts) is its own symbol."""

    def __missing__(self, key: str) -> str:
        return key


SYMBOLS = _Symbols({a: s for a, s in ALPACA_SYMBOLS.items() if a != "SPY"})
MIN_NOTIONAL = 5.0  # ignore differences smaller than $5
# ... and top-ups / trims under 1% of the position (fill rounding): a pending order on a held
# stock makes Alpaca refuse its stops ("potential wash trade"), so tiny adjustments cost protection
MIN_ADJUST = 0.01
CRYPTO_STOP_ROOM = 0.01  # crypto stop-limit: limit 1% past the stop, so it fills in a fast drop


class AlpacaError(RuntimeError):
    pass


def _keys() -> tuple[str, str]:
    key, secret = os.environ.get("ALPACA_API_KEY_ID"), os.environ.get("ALPACA_API_SECRET_KEY")
    if not key or not secret:
        raise AlpacaError("Set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY in the environment settings.")
    return key, secret


def request(method: str, path: str, body: dict | None = None, base: str = BASE_URL) -> dict | list:
    key, secret = _keys()
    req = urllib.request.Request(base + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret,
                                          "Content-Type": "application/json"})
    # a network hiccup (timeout, reset) on a read or a cancel is retried; an order (POST) is never
    # sent twice blindly: it may have reached Alpaca before the connection dropped
    tries = 3 if method in ("GET", "DELETE") else 1
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            raise AlpacaError(f"{method} {path} -> {e.code}: {e.read().decode(errors='replace')}") from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == tries - 1:
                raise
            time.sleep(5 * (attempt + 1))


def get_data(path: str, params: dict) -> dict:
    """GET from Alpaca's market data API. When rate-limited (200 requests a minute),
    wait and retry for up to ~5 minutes instead of failing."""
    for attempt in range(9):
        try:
            return request("GET", f"{path}?{urllib.parse.urlencode(params)}", base=DATA_URL)
        except AlpacaError as e:
            if " 429:" not in str(e) or attempt == 8:
                raise
            time.sleep(min(60, 2 ** (attempt + 1)))


def positions() -> dict[str, float]:
    """Alpaca symbol -> signed quantity."""
    out = {}
    for p in request("GET", "/v2/positions"):
        qty = float(p["qty"])
        out[p["symbol"].replace("USD", "/USD") if p.get("asset_class") == "crypto" and "/" not in p["symbol"]
            else p["symbol"]] = -abs(qty) if p.get("side") == "short" else qty
    return out


def through_stop(t: dict, live: dict[str, float] | None) -> bool:
    """Is the live price already through this trade's stop? Then the trade is over: a stop at Alpaca
    filled between two bars (the paper account only sees it when the bar closes) or the price
    gapped through it. Such a trade is neither bought back nor protected."""
    px = (live or {}).get(SYMBOLS[t["asset"]])
    if px is None or t.get("stop") is None:
        return False
    return (px - float(t["stop"])) * (1 if float(t["qty"]) > 0 else -1) <= 0


def wanted(live: dict[str, float] | None = None) -> dict[str, float]:
    """Net wanted quantity per Alpaca symbol, from paper/orders.json; with `live` prices, without
    the trades whose stop the price has already crossed."""
    orders = json.loads((PAPER_DIR / "orders.json").read_text())
    net: dict[str, float] = {}
    for o in orders:
        if through_stop(o, live):
            continue
        sym = SYMBOLS[o["asset"]]
        net[sym] = net.get(sym, 0.0) + float(o["qty"])
    return net


def plan(want: dict[str, float], have: dict[str, float], prices: dict[str, float]) -> list[dict]:
    """Orders that turn `have` into `want`, respecting Alpaca's limits."""
    crypto_syms = {SYMBOLS[a] for a in CRYPTO}
    orders = []
    for sym in sorted(set(want) | set(have)):
        target = want.get(sym, 0.0)
        note = ""
        if sym in crypto_syms and target < 0:
            target, note = 0.0, "crypto shorts not possible on Alpaca: held flat instead"
        if sym not in crypto_syms and target < 0:
            target = -math.floor(-target)  # whole shares for shorts
        diff = target - have.get(sym, 0.0)
        if abs(diff) * prices.get(sym, 0.0) < MIN_NOTIONAL:
            continue
        if target != 0 and have.get(sym, 0.0) * target > 0 and abs(diff) < MIN_ADJUST * abs(target):
            continue  # same side, almost the right size: keep it (and its stops)
        # round down (crypto to 9 decimals, Alpaca's precision): rounding up asks for more than is held
        qty = math.floor(abs(diff) * 1e9) / 1e9 if sym in crypto_syms else round(abs(diff), 6)
        if target == 0 and sym in have:
            qty = abs(have[sym])  # closing: exactly what is held
        orders.append({"symbol": sym, "side": "buy" if diff > 0 else "sell", "qty": qty,
                       "type": "market", "time_in_force": "gtc" if sym in crypto_syms else "day", "note": note})
    return orders


OPG_WINDOW = (30, 2)  # minutes before the open: opening-auction orders are accepted until 9:28


def opening_auction(clock: dict) -> bool:
    """True in the half hour before the US open (orders can join the opening auction)."""
    import datetime as dt

    if clock.get("is_open"):
        return False
    import re

    now = dt.datetime.fromisoformat(re.sub(r"(\.\d{6})\d+", r"\1", clock["timestamp"]))  # ns -> us
    nxt = dt.datetime.fromisoformat(clock["next_open"])
    mins = (nxt - now).total_seconds() / 60
    return OPG_WINDOW[1] <= mins <= OPG_WINDOW[0]


def at_the_open(orders: list[dict]) -> list[dict]:
    """Stock orders sent just before the open go to the opening auction (market-on-open:
    time_in_force 'opg', whole shares only); a fractional rest fills right after the open."""
    out = []
    for o in orders:
        if "/" in o["symbol"] or o["type"] != "market":
            out.append(o)
            continue
        whole = math.floor(o["qty"] + 1e-9)
        frac = round(o["qty"] - whole, 6)
        if whole >= 1:
            out.append(o | {"qty": whole, "time_in_force": "opg", "note": (o["note"] + " opening auction").strip()})
        if frac > 0:
            out.append(o | {"qty": frac, "time_in_force": "day", "note": (o["note"] + " fractional, at the open").strip()})
    return out


def last_prices() -> dict[str, float]:
    orders = json.loads((PAPER_DIR / "orders.json").read_text())
    status = {SYMBOLS[o["asset"]]: abs(o.get("mark") or o.get("stop") or 0.0) for o in orders}
    return {s: p for s, p in status.items() if p}


def live_prices(symbols) -> dict[str, float]:
    """Latest trade price per Alpaca symbol (market data API). Stocks use the
    IEX feed: the free plan has no real-time SIP (full market) data."""
    crypto = [s for s in symbols if "/" in s]
    stocks = [s for s in symbols if "/" not in s]
    out = {}
    if crypto:
        d = get_data("/v1beta3/crypto/us/latest/trades", {"symbols": ",".join(crypto)})
        out |= {s: float(t["p"]) for s, t in d.get("trades", {}).items()}
    if stocks:
        d = get_data("/v2/stocks/trades/latest", {"symbols": ",".join(stocks), "feed": "iex"})
        out |= {s: float(t["p"]) for s, t in d.get("trades", {}).items()}
    return out


def _px(x: float) -> float:
    """Alpaca accepts 2 decimals above $1, 4 below."""
    return round(x, 2 if x >= 1 else 4)


def protect(sym: str, held: float, trades: list[dict], price: float | None = None) -> list[dict]:
    """Stop / target orders that protect `held` (signed qty of `sym` at Alpaca),
    one set per trade of the system in that symbol, up to what is held.
    `trades`: the orders.json entries of that symbol (qty signed, stop, target)."""
    crypto = sym in {SYMBOLS[a] for a in CRYPTO}
    side = "sell" if held > 0 else "buy"
    left, out = abs(held), []
    for t in trades:
        q = min(abs(float(t["qty"])), left)
        if held * float(t["qty"]) <= 0 or q <= 0:
            continue
        left -= q
        stop, target = float(t["stop"]), t.get("target")
        tag = f"{t.get('strategy', '')}"
        # already through the stop (e.g. the price moved since the last bar): close at market
        if price is not None and (price - stop) * (1 if held > 0 else -1) <= 0:
            out.append({"symbol": sym, "side": side, "qty": round(q, 9), "type": "market",
                        "time_in_force": "gtc" if crypto else "day", "note": f"{tag}: price already through stop"})
            continue
        if crypto:
            q = math.floor(q * 1e9) / 1e9
            out.append({"symbol": sym, "side": side, "qty": q, "type": "stop_limit", "stop_price": _px(stop),
                        "limit_price": _px(stop * (1 - CRYPTO_STOP_ROOM)), "time_in_force": "gtc",
                        "note": f"{tag}: stop (target taken by the next run)"})
            continue
        whole = math.floor(q + 1e-9)
        frac = round(q - whole, 9)
        if whole >= 1 and target is not None:
            out.append({"symbol": sym, "side": side, "qty": whole, "type": "limit", "time_in_force": "gtc",
                        "order_class": "oco", "take_profit": {"limit_price": _px(float(target))},
                        "stop_loss": {"stop_price": _px(stop)}, "note": f"{tag}: stop + target (OCO)"})
        elif whole >= 1:
            out.append({"symbol": sym, "side": side, "qty": whole, "type": "stop", "stop_price": _px(stop),
                        "time_in_force": "gtc", "note": f"{tag}: trailing stop"})
        if frac >= 1e-4:  # fractional shares: stop only, day orders (Alpaca's rule), renewed each run
            out.append({"symbol": sym, "side": side, "qty": frac, "type": "stop", "stop_price": _px(stop),
                        "time_in_force": "day", "note": f"{tag}: stop for the fractional part"})
    return out


def _stop_of(o: dict) -> float:
    return float(o.get("stop_price") or o["stop_loss"]["stop_price"])


def _below_reference(o: dict, err: Exception) -> dict | None:
    """Before the open Alpaca checks a sell stop against its reference price (the last close): a
    trailing stop raised above it is refused ("stop price must be less than current price") although
    the stock trades higher pre-market. The same order with its stop just under that price (1 cent),
    so the position is never unprotected; the next run puts the planned stop back. None: another error."""
    msg = str(err)
    if o.get("side") != "sell" or "stop price must be less than current price" not in msg:
        return None
    try:
        ref = float(json.loads(msg[msg.index("{"):])["market_price"])
    except (ValueError, KeyError):
        return None
    new = {k: (dict(v) if isinstance(v, dict) else v) for k, v in o.items()}
    stop = _px(ref - 0.01)
    if "stop_loss" in new:
        new["stop_loss"]["stop_price"] = stop
    else:
        new["stop_price"] = stop
    new["note"] = o.get("note", "") + " (stop under Alpaca's reference price until the next run)"
    return new


def _send(o: dict) -> dict:
    """POST an order with its own client_order_id, retried once after a network timeout: if the first
    try did reach Alpaca, the retry is refused as a duplicate id and the order placed is returned, so
    an order is never sent twice (2026-10-10: a timeout left account B's stops out for 30 minutes)."""
    import uuid

    body = {k: (str(v) if k == "qty" else v) for k, v in o.items() if k != "note"}
    body.setdefault("client_order_id", f"tf-{uuid.uuid4().hex[:24]}")
    try:
        return request("POST", "/v2/orders", body)
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        time.sleep(5)
    try:
        return request("POST", "/v2/orders", body)
    except AlpacaError as e:
        if "client_order_id must be unique" not in str(e):
            raise
        q = urllib.parse.urlencode({"client_order_id": body["client_order_id"]})
        return request("GET", f"/v2/orders:by_client_order_id?{q}")


CRYPTO_LIMIT_WAIT = 120  # seconds a crypto order waits on the book before the rest goes at market


CASH_BUFFER = 0.97  # crypto buys use at most 97% of the cash available (fees, price moves)


def crypto_limit_first(o: dict, wait: float = CRYPTO_LIMIT_WAIT,
                       cash: float | None = None) -> tuple[str | None, str]:
    """Send a crypto order as a limit at the bid (buy) / ask (sell), so it rests on the
    book and pays the maker fee (0.15% vs 0.25% at market). Whatever has not filled
    after `wait` seconds is cancelled and sent at market. Every outcome goes to
    paper/fills.csv, to measure how often the cheaper fill happens.
    Returns (id of the last order sent, description)."""
    q = get_data("/v1beta3/crypto/us/latest/quotes", {"symbols": o["symbol"]})["quotes"][o["symbol"]]
    px = float(q["bp"] if o["side"] == "buy" else q["ap"])
    capped = ""
    if o["side"] == "buy" and cash is not None and o["qty"] * px > CASH_BUFFER * cash:
        # crypto cannot be bought on margin: only with the cash left after the stocks
        qty = math.floor(CASH_BUFFER * max(cash, 0.0) / px * 1e9) / 1e9
        if qty * px < MIN_NOTIONAL:
            return None, f"skipped: crypto needs cash, only ${cash:,.0f} available (no margin for crypto)"
        capped = f" (cut from {o['qty']:g} to {qty:g}: crypto needs cash, ${cash:,.0f} available)"
        o = o | {"qty": qty}
    r = _send(o | {"type": "limit", "limit_price": _px(px), "time_in_force": "gtc"})
    oid = r["id"]
    _wait(lambda: request("GET", f"/v2/orders/{oid}")["status"] in ("filled", "canceled", "rejected"), wait)
    st = request("GET", f"/v2/orders/{oid}")
    maker = float(st.get("filled_qty") or 0)
    taker, last, how = 0.0, oid, f"limit {px:,.2f} filled"
    if st["status"] != "filled":
        request("DELETE", f"/v2/orders/{oid}")
        _wait(lambda: request("GET", f"/v2/orders/{oid}")["status"] in ("canceled", "filled"), 20)
        st = request("GET", f"/v2/orders/{oid}")
        maker = float(st.get("filled_qty") or 0)
        rest = round(float(o["qty"]) - maker, 9)
        how = f"limit {px:,.2f}: {maker:g} filled"
        if rest * px >= MIN_NOTIONAL:
            last = _send(o | {"qty": rest}).get("id")
            taker = rest
            how += f", rest {rest:g} at market"
    line = f"{pd_now()},{o['symbol']},{o['side']},{o['qty']},{px},{maker},{taker}\n"
    f = PAPER_DIR / "fills.csv"
    if not f.exists():
        f.write_text("time,symbol,side,qty,limit_price,maker_qty,taker_qty\n")
    with f.open("a") as fh:
        fh.write(line)
    return last, how + capped


def pd_now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def _wait(check, seconds: float = 20.0) -> bool:
    end = time.time() + seconds
    while time.time() < end:
        if check():
            return True
        time.sleep(1)
    return check()


def check_account() -> str:
    """The keys must belong to the Alpaca account this folder is for (config
    'alpaca_account'), so one account's signals never trade on another."""
    acct = request("GET", "/v2/account").get("account_number", "?")
    cfg = json.loads((PAPER_DIR / "config.json").read_text())
    want = cfg.get("alpaca_account")
    if want and acct != want:
        raise AlpacaError(f"these keys are for Alpaca account {acct}, but {PAPER_DIR.name}/ is for {want}: "
                          "nothing sent. Check the GitHub secrets for this account.")
    return acct


def sync(send: bool = False) -> list[dict]:
    acct = check_account()
    print(f"Alpaca account {acct}: {json.loads((PAPER_DIR / 'config.json').read_text()).get('name', '')}")
    trades = json.loads((PAPER_DIR / "orders.json").read_text())
    prices = last_prices()
    if send:  # 1) cancel the stops and targets of the last run
        request("DELETE", "/v2/orders")
        _wait(lambda: not request("GET", "/v2/orders?status=open"))
    try:
        return _trade_and_protect(send, trades, prices)
    except Exception as exc:
        if send:  # the old stops are gone: never leave what is held unprotected
            emergency_protect(trades, exc)
        raise


def emergency_protect(trades: list[dict], exc: Exception) -> None:
    """After a failure, put stops back on everything held (the plan's levels), and alert."""
    from . import notify

    placed, failed = [], []
    try:
        held = positions()
        open_syms = {o["symbol"] for o in request("GET", "/v2/orders?status=open")}
    except AlpacaError as e:
        held, open_syms = {}, set()
        failed.append(f"positions unreadable ({e})")
    for sym, q in sorted(held.items()):
        if abs(q) < 1e-9 or sym.replace("/", "") in {s.replace("/", "") for s in open_syms}:
            continue
        mine = [t for t in trades if SYMBOLS.get(t["asset"]) == sym]
        if not mine:
            try:
                value = abs(q) * live_prices([sym]).get(sym, float("inf"))
            except AlpacaError:
                value = float("inf")
            if value >= 1.0:  # dust (< $1, left over from rounding) needs no stop, as in verify()
                failed.append(f"{sym}: no stop level in the plan (${value:,.0f} held)")
            continue
        for o in protect(sym, q, mine):
            try:
                _send(o)
                placed.append(sym)
            except AlpacaError as e:
                failed.append(f"{sym}: {e}")
    msg = (f"Run failed ({type(exc).__name__}: {str(exc)[:150]}). Stops put back on: "
           f"{', '.join(sorted(set(placed))) or 'nothing needed'}."
           + (f" NOT protected: {'; '.join(failed)}" if failed else ""))
    print("EMERGENCY: " + msg)
    acct = os.environ.get("PAPER_ACCOUNT_NAME", "")
    notify.send(f"[{acct}] trading run failed", msg, "warning", "high")


def _trade_and_protect(send: bool, trades: list[dict], prices: dict[str, float]) -> list[dict]:
    have = positions()
    missing = [s for s in have if s not in prices]  # held but no longer wanted: orders.json has no price for it
    if missing:
        try:
            prices |= live_prices(missing)
        except AlpacaError as e:
            print(f"No live prices for {', '.join(missing)} ({e}); closing them anyway.")
            prices |= {s: float("inf") for s in missing}

    # 2) market orders for the difference (just before the open: the opening auction). Trades whose
    # stop the live price has crossed are over (their stop filled at Alpaca since the last bar): not
    # bought back (2026-10-08: each run bought them back and sold them again at once)
    try:
        live0 = live_prices(sorted({SYMBOLS[t["asset"]] for t in trades}))
    except (AlpacaError, OSError) as e:
        print(f"No live prices ({e}); the plan is followed as it is.")
        live0 = {}
    over = [t for t in trades if through_stop(t, live0)]
    for t in over:
        print(f"{SYMBOLS[t['asset']]} {t.get('strategy', '')}: price already through its stop "
              f"{t['stop']} (live {live0[SYMBOLS[t['asset']]]}): over, not bought back")
    trades = [t for t in trades if not through_stop(t, live0)]
    todo = plan(wanted(live0), have, prices)
    try:
        if opening_auction(request("GET", "/v2/clock")):
            todo = at_the_open(todo)
    except (AlpacaError, KeyError, ValueError) as e:
        print(f"Market clock unavailable ({e}); normal orders.")
    sent, errors = {}, []
    todo = sorted(todo, key=lambda o: o["side"] != "sell")  # sells first: they free the cash buys need
    for o in todo:
        line = f"{o['side'].upper():4s} {o['qty']:>12,.6f} {o['symbol']:8s} market {o['note']}"
        try:
            if send and "/" in o["symbol"]:  # crypto: rest on the book first (maker fee)
                cash = float(request("GET", "/v2/account").get("non_marginable_buying_power") or 0.0)
                oid, how = crypto_limit_first(o, cash=cash)
                if oid:
                    sent[oid] = o["symbol"]
                line += f"  -> {how}"
            elif send:
                r = _send(o)
                sent[r.get("id")] = o["symbol"]
                line += f"  -> sent, id {r.get('id', '?')}"
        except AlpacaError as e:  # one refused order must not leave the others (and the stops) unsent
            errors.append(f"{o['side']} {o['symbol']}: {e}")
            line += f"  -> REFUSED: {e}"
        print(line)
    if not todo:
        print("Positions already match the paper account.")

    # 3) protect what is held once the market orders have filled
    unfilled = []
    if send:
        done = ("filled", "canceled", "rejected", "expired")
        _wait(lambda: all(request("GET", f"/v2/orders/{i}").get("status") in done for i in sent))
        held = positions()
        for i, sym in sent.items():
            r = request("GET", f"/v2/orders/{i}")
            if r.get("status") == "filled":
                continue
            unfilled.append(sym)
            rest = float(r.get("qty") or 0) - float(r.get("filled_qty") or 0)
            if r.get("status") not in done and held.get(sym, 0.0) * (1 if r.get("side") == "buy" else -1) < 0:
                # a pending order that shrinks the position has those shares reserved already
                q = held[sym]
                held[sym] = math.copysign(max(0.0, abs(q) - rest), q)
    else:  # dry run: assume the market orders filled
        held = dict(have)
        for o in todo:
            held[o["symbol"]] = held.get(o["symbol"], 0.0) + (o["qty"] if o["side"] == "buy" else -o["qty"])
    try:
        live = live_prices([s for s, q in held.items() if abs(q) > 1e-9])
    except AlpacaError as e:
        print(f"No live prices ({e}); stops are placed without the 'already through' check.")
        live = {}
    protective = []
    for sym, q in sorted(held.items()):
        if abs(q) < 1e-9:
            continue
        mine = [t for t in trades if SYMBOLS[t["asset"]] == sym]
        protective += protect(sym, q, mine, live.get(sym))
    for o in protective:
        lvl = (f"stop {o.get('stop_price') or o['stop_loss']['stop_price']}" if o["type"] != "market" else "")
        if o.get("order_class") == "oco":
            lvl += f", target {o['take_profit']['limit_price']}"
        line = f"{o['side'].upper():4s} {o['qty']:>12,.6f} {o['symbol']:8s} {o['type']} {lvl} ({o['note']})"
        if send:
            try:
                line += f"  -> sent, id {_send(o).get('id', '?')}"
            except AlpacaError as e:
                lower = _below_reference(o, e)
                if lower is None:
                    line += f"  -> REJECTED: {e}"
                else:  # before the open: Alpaca checks the stop against yesterday's close
                    try:
                        line += (f"  -> refused above Alpaca's reference price; stop put at "
                                 f"{_stop_of(lower)} until the next run, sent, id {_send(lower).get('id', '?')}")
                    except AlpacaError as e2:
                        line += f"  -> REJECTED: {e2}"
        print(line)
    if unfilled:
        print(f"Not filled yet (market closed?), protected once filled, on the next run: {', '.join(unfilled)}")
    if send and todo:  # phone notification (only when NTFY_TOPIC is set)
        from . import notify

        try:
            eq = float(request("GET", "/v2/account").get("equity", 0))
        except AlpacaError:
            eq = None
        done_syms = set(sent.values())
        for title, body, tags in notify.trade_messages([o for o in todo if o["symbol"] in done_syms], eq):
            notify.send(title, body, tags)
    if errors:  # the rest went through and everything held is protected; still report what was refused
        raise AlpacaError("orders refused: " + "; ".join(errors))
    return todo + protective


def verify(alert: bool = False) -> list[str]:
    """Does Alpaca hold what the plan wants, and is every position covered by a stop?
    Returns the problems (empty = all good); with `alert`, sends them to the phone."""
    problems = []
    try:  # trades whose stop the price has crossed are over (their stop filled at Alpaca)
        live = live_prices(sorted(wanted()))
    except (AlpacaError, OSError):
        live = {}
    want = wanted(live)
    have = positions()
    orders = request("GET", "/v2/orders?status=open&nested=true")
    norm = lambda s: s.replace("/", "")
    pending = {}  # market / limit entries not filled yet (e.g. queued while the market is closed)
    stops = {}
    for o in orders:
        legs = [o] + list(o.get("legs") or [])
        for x in legs:
            q = float(x.get("qty") or 0) - float(x.get("filled_qty") or 0)
            sign = 1 if x.get("side") == "buy" else -1
            if x.get("type") in ("stop", "stop_limit", "trailing_stop"):
                stops[norm(x["symbol"])] = stops.get(norm(x["symbol"]), 0.0) + q
            elif x is o and x.get("type") in ("market", "limit") and not o.get("order_class"):
                pending[norm(x["symbol"])] = pending.get(norm(x["symbol"]), 0.0) + sign * q
    prices = last_prices()
    try:
        cash = float(request("GET", "/v2/account").get("non_marginable_buying_power") or 0.0)
    except AlpacaError:
        cash = None
    crypto = {norm(SYMBOLS[a]) for a in CRYPTO}
    for sym in sorted({norm(s) for s in want} | {norm(s) for s in have}):
        w = sum(q for s, q in want.items() if norm(s) == sym)
        if "/" not in next((s for s in want if norm(s) == sym), "") and w < 0:
            w = -math.floor(-w)  # whole-share shorts
        if any(norm(SYMBOLS[a]) == sym for a in CRYPTO) and w < 0:
            w = 0.0  # crypto shorts are held flat
        h = sum(q for s, q in have.items() if norm(s) == sym) + pending.get(sym, 0.0)
        px = prices.get(next((s for s in want if norm(s) == sym), sym), 0.0) or 100.0
        short_of_cash = (sym in crypto and h < w and cash is not None
                         and (w - h) * px > CASH_BUFFER * cash - MIN_NOTIONAL)
        if short_of_cash:  # crypto cannot use margin: smaller than the plan when the cash is in stocks
            print(f"{sym}: plan wants {w:g}, Alpaca has {h:g} (crypto needs cash: ${cash:,.0f} left)")
        elif abs(w - h) * px > max(50.0, 0.02 * abs(w) * px):  # same 1-2% tolerance as plan()
            problems.append(f"{sym}: plan wants {w:g}, Alpaca has {h:g}")
        held = sum(q for s, q in have.items() if norm(s) == sym)
        # an exit decided after the close is a market order queued for the next open: those shares
        # are on their way out, they need no stop
        exiting = max(0.0, -math.copysign(1.0, held) * pending.get(sym, 0.0)) if held else 0.0
        covered = stops.get(sym, 0.0) + exiting
        # the fractional rest's stop is a day order (Alpaca's rule), gone after the close until the next
        # run renews it: whole shares covered is enough
        whole_covered = abs(held) - covered < 1.0 and covered >= math.floor(abs(held) + 1e-9) > 0
        if abs(held) * px >= 1.0 and covered < 0.98 * abs(held) and not whole_covered:  # dust (< $1): no stop
            problems.append(f"{sym}: {abs(held):g} held, only {covered:g} covered by a stop")
    if alert and problems:
        from . import notify

        acct = os.environ.get("PAPER_ACCOUNT_NAME", "")
        notify.send(f"[{acct}] Alpaca does not match the plan", "; ".join(problems), "warning", "high")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="test the keys and show the account")
    p = sub.add_parser("sync", help="match Alpaca to paper/orders.json")
    p.add_argument("--send", action="store_true", help="really send the orders (default: dry run)")
    v = sub.add_parser("verify", help="check Alpaca matches the plan and every position has a stop")
    v.add_argument("--alert", action="store_true", help="send problems to the phone (ntfy)")
    args = ap.parse_args()
    if args.cmd == "check":
        acct = request("GET", "/v2/account")
        print(f"Alpaca PAPER account {acct.get('account_number')}: status {acct.get('status')}, "
              f"equity ${float(acct.get('equity', 0)):,.2f}, buying power ${float(acct.get('buying_power', 0)):,.2f}")
        print(f"Options: approved level {acct.get('options_approved_level', '?')}, "
              f"trading level {acct.get('options_trading_level', '?')}")
        print(f"Positions: {positions() or 'none'}")
    elif args.cmd == "verify":
        problems = verify(args.alert)
        print("\n".join(problems) if problems else "Alpaca matches the plan; every position has its stop.")
        raise SystemExit(1 if problems else 0)
    else:
        sync(args.send)


if __name__ == "__main__":
    main()
