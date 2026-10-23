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
        except (urllib.error.URLError, TimeoutError, ConnectionError):
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


def through_stop(t: dict, live: dict[str, float] | None,
                 seen: dict[str, tuple[float, float]] | None = None) -> bool:
    """Has this trade's stop or target been reached since the last bar the paper account processed?
    Then the trade is over: its stop or target filled at Alpaca between two bars (the paper account only
    sees it when the bar closes, and will close it then) or the price gapped through it. Such a trade is
    neither bought back nor protected. `live`: last prices; `seen`: (low, high) per symbol since that
    bar (2026-10-13: AMD, QQQ, TSLA gapped through their stops at the open and MSFT reached its target,
    the price came back, and the 13:57 run bought them back because the last price alone looked fine)."""
    sym = SYMBOLS[t["asset"]]
    px = (live or {}).get(sym)
    lo, hi = (seen or {}).get(sym, (px, px))
    if px is not None:
        lo, hi = min(lo, px), max(hi, px)
    if lo is None or hi is None:
        return False
    long_ = float(t["qty"]) > 0
    stop, target = t.get("stop"), t.get("target")
    if stop is not None and (lo <= float(stop) if long_ else hi >= float(stop)):
        return True
    # the same for a target: the OCO's limit filled at Alpaca (2026-10-12: XOM sold at its target at
    # 13:49 UTC, bought back by the 13:55 run, sold again at 13:58)
    return target is not None and (hi >= float(target) if long_ else lo <= float(target))


def _regular_hours(t: str | None) -> bool:
    """Is this bar time (ISO, UTC) inside the regular US session, 9:30-16:00 New York? (No `t`: kept.)"""
    if not t:
        return True
    from datetime import datetime
    from zoneinfo import ZoneInfo

    ny = datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(ZoneInfo("America/New_York"))
    return (9, 30) <= (ny.hour, ny.minute) < (16, 0)


def bar_range(symbols) -> dict[str, tuple[float, float]]:
    """(low, high) of each stock since the end of the last bar the paper account processed for it (its
    "bar" in orders.json; else the last line of equity.csv, hourly accounts only): the prices its next
    bar will contain. IEX minute bars (the free real-time feed). Per stock because equity.csv already
    has the hour that just ended when only crypto's bar is final (stock data is 15 minutes late):
    2026-10-20 14:01 UTC, a range from 14:00 missed AAPL's stop at the 13:30 open (engine, shadow).
    A daily account's "bar" is a date (algo.runner): its range is the whole next session (2026-10-23:
    account D's PRIM stop filled at 9:45, the price came back above it and the 10:50 run bought PRIM back)."""
    path = PAPER_DIR / "equity.csv"
    stocks = sorted(s for s in symbols if "/" not in s)
    if not stocks:
        return {}
    from datetime import datetime, timedelta, timezone

    def end_of(bar: str) -> datetime:
        if len(bar) == 10:  # a daily bar: the session ends that day
            return datetime.fromisoformat(bar).replace(tzinfo=timezone.utc) + timedelta(days=1)
        return datetime.fromisoformat(bar[:19]).replace(tzinfo=timezone.utc) + timedelta(hours=1)

    last = path.read_text().strip().splitlines()[-1].split(",")[0] if path.exists() else ""
    starts = {s: end_of(last) for s in stocks} if len(last) >= 16 else {}  # hourly accounts
    orders = PAPER_DIR / "orders.json"
    for o in json.loads(orders.read_text()) if orders.exists() else []:
        sym = SYMBOLS.get(o.get("asset"), o.get("asset"))
        if sym in stocks and o.get("bar"):
            starts[sym] = min(starts.get(sym, end_of(str(o["bar"]))), end_of(str(o["bar"])))
    stocks = sorted(starts)
    if not stocks:
        return {}
    start = min(starts.values())
    if start > datetime.now(timezone.utc):
        return {}
    out: dict[str, tuple[float, float]] = {}
    params = {"symbols": ",".join(stocks), "timeframe": "1Min", "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
              "feed": "iex", "limit": 10000}
    for _ in range(20):
        d = get_data("/v2/stocks/bars", params)
        for s, bars in (d.get("bars") or {}).items():
            since = starts.get(s, start)
            bars = [b for b in bars if _regular_hours(b.get("t"))  # the paper's hourly bars: 9:30-16:00 only
                    and (not b.get("t") or datetime.fromisoformat(b["t"].replace("Z", "+00:00")) >= since)]
            if bars:
                lo, hi = min(b["l"] for b in bars), max(b["h"] for b in bars)
                o = out.get(s, (lo, hi))
                out[s] = (min(o[0], lo), max(o[1], hi))
        if not d.get("next_page_token"):
            break
        params["page_token"] = d["next_page_token"]
    return out


def wanted(live: dict[str, float] | None = None,
           seen: dict[str, tuple[float, float]] | None = None) -> dict[str, float]:
    """Net wanted quantity per Alpaca symbol, from paper/orders.json; with `live` prices (and `seen`
    ranges), without the trades whose stop or target the price has already reached."""
    orders = json.loads((PAPER_DIR / "orders.json").read_text())
    net: dict[str, float] = {}
    for o in orders:
        if through_stop(o, live, seen):
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


# minutes before the open: opening-auction orders (Alpaca accepts them until 9:28; 2026-10-22: one sent at
# 9:26 expired unfilled). From 9:25 a plain market order is sent instead: it fills at the open.
OPG_WINDOW = (30, 5)


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


def no_wash(protective: list[dict], pending: set[tuple[str, str]]) -> tuple[list[dict], list[dict]]:
    """Split the protective orders into those to send now and those that wait: Alpaca refuses a plain
    stop on a stock with an opposite-side order pending ("potential wash trade"; an OCO is accepted).
    `pending`: (symbol, side) of the market orders not filled yet. The stop goes out with the next run,
    once the order has filled (2026-10-23: A's AAPL buy queued for the opening auction made Alpaca refuse
    the stop of the AAPL shares already held, so the 9:12 run found its orders different from the plan
    and cancelled and re-sent all of them, the auction buy included)."""
    back = {"buy": "sell", "sell": "buy"}
    wait = [o for o in protective if o["type"] == "stop" and o.get("order_class") != "oco"
            and (o["symbol"], back[o["side"]]) in pending]
    return [o for o in protective if not any(o is w for w in wait)], wait


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
    if send and already_queued(trades, prices):
        print("Market closed and Alpaca's open orders already match the plan: left as they are.")
        return []
    if send:  # 1) cancel the stops and targets of the last run
        request("DELETE", "/v2/orders")
        _wait(lambda: not request("GET", "/v2/orders?status=open"))
    try:
        return _trade_and_protect(send, trades, prices)
    except Exception as exc:
        if send:  # the old stops are gone: never leave what is held unprotected
            emergency_protect(trades, exc)
        raise


def _order_key(o: dict) -> tuple:
    """What an order does, the same for an order we would send and one Alpaca lists as open."""
    r = lambda x: round(float(x), 4)  # noqa: E731
    sym, side, qty = o["symbol"].replace("/", ""), o["side"], round(float(o["qty"]), 6)
    if o.get("order_class") == "oco":
        if "take_profit" in o:  # ours
            return ("oco", sym, side, qty, r(o["take_profit"]["limit_price"]), r(o["stop_loss"]["stop_price"]))
        stop = next((x for x in o.get("legs") or [] if x.get("type") == "stop"), {})
        return ("oco", sym, side, qty, r(o.get("limit_price") or 0), r(stop.get("stop_price") or 0))
    if o["type"] == "market":
        return ("market", sym, side, qty, o["time_in_force"])
    if o["type"] == "stop":
        return ("stop", sym, side, qty, r(o["stop_price"]), o["time_in_force"])
    return ("other", sym, o.get("id"))  # never matches what we would send: the normal path runs


def already_queued(trades: list[dict], prices: dict[str, float]) -> bool:
    """While the market is closed the orders a run sends cannot fill, so a run that would send exactly
    the orders already open has nothing to do. Cancelling and re-sending them each hour (2026-10-17:
    account D's 3 weekend buys) only fills the order list with cancelled copies; in the opening-auction
    window the orders compared are the auction ones (2026-10-22: the 9:05, 9:12 and 9:20 runs each
    re-sent account C's auction sell, the last at 9:26, and it expired). Crypto trades 24/7: any crypto
    in play keeps the normal path. On any doubt (an error, an order we would not send) the answer is
    False and the run cancels and re-sends."""
    from collections import Counter

    try:
        clock = request("GET", "/v2/clock")
        if clock.get("is_open"):
            return False
        auction = opening_auction(clock)
        have = positions()
        syms = sorted({SYMBOLS[t["asset"]] for t in trades})
        if any("/" in s for s in list(have) + syms):
            return False
        live = live_prices(syms + [s for s in have if s not in syms])
        seen = bar_range(syms)
        todo = plan(wanted(live, seen), have, dict(prices))
        if auction:
            todo = at_the_open(todo)
        alive = [t for t in trades if not through_stop(t, live, seen)]
        protective = []
        for sym, q in sorted(have.items()):
            if abs(q) > 1e-9:
                protective += protect(sym, q, [t for t in alive if SYMBOLS[t["asset"]] == sym], live.get(sym))
        protective = no_wash(protective, {(o["symbol"], o["side"]) for o in todo})[0]
        want = Counter(_order_key(o) for o in todo + protective)
        open_ = Counter(_order_key(o) for o in request("GET", "/v2/orders?status=open&nested=true"))
    except (AlpacaError, OSError, KeyError, ValueError, TypeError):
        return False
    return bool(want) and want == open_


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
    syms = sorted({SYMBOLS[t["asset"]] for t in trades})
    try:
        live0 = live_prices(syms)
    except (AlpacaError, OSError) as e:
        print(f"No live prices ({e}); the plan is followed as it is.")
        live0 = {}
    try:
        seen0 = bar_range(syms)
    except (AlpacaError, OSError, ValueError) as e:
        print(f"No minute bars since the last bar ({e}); last prices only.")
        seen0 = {}
    over = [t for t in trades if through_stop(t, live0, seen0)]
    for t in over:
        sym = SYMBOLS[t["asset"]]
        print(f"{sym} {t.get('strategy', '')}: stop {t['stop']} or target {t.get('target')} reached since "
              f"the last bar (live {live0.get(sym)}, range {seen0.get(sym)}): over, not bought back")
    trades = [t for t in trades if not through_stop(t, live0, seen0)]
    todo = plan(wanted(live0, seen0), have, prices)
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
    unfilled, pending = [], set()
    if send:
        done = ("filled", "canceled", "rejected", "expired")
        _wait(lambda: all(request("GET", f"/v2/orders/{i}").get("status") in done for i in sent))
        held = positions()
        for i, sym in sent.items():
            r = request("GET", f"/v2/orders/{i}")
            if r.get("status") == "filled":
                continue
            unfilled.append(sym)
            if r.get("status") not in done:
                pending.add((sym, r.get("side")))
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
    protective, waiting = no_wash(protective, pending)
    for o in waiting:
        print(f"{o['side'].upper():4s} {o['qty']:>12,.6f} {o['symbol']:8s} stop {o['stop_price']} ({o['note']})  -> "
              f"waits for the pending {'buy' if o['side'] == 'sell' else 'sell'} to fill (Alpaca refuses it "
              f"next to one); sent by the next run")
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
    try:  # trades whose stop or target the price has reached are over (filled at Alpaca)
        live = live_prices(sorted(wanted()))
    except (AlpacaError, OSError):
        live = {}
    try:
        seen = bar_range(sorted(wanted()))
    except (AlpacaError, OSError, ValueError):
        seen = {}
    want = wanted(live, seen)
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
