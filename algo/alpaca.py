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
SYMBOLS = {a: s for a, s in ALPACA_SYMBOLS.items() if a != "SPY"}
MIN_NOTIONAL = 5.0  # ignore differences smaller than $5
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
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise AlpacaError(f"{method} {path} -> {e.code}: {e.read().decode(errors='replace')}") from None


def get_data(path: str, params: dict) -> dict:
    """GET from Alpaca's market data API, retrying when rate-limited."""
    for attempt in range(5):
        try:
            return request("GET", f"{path}?{urllib.parse.urlencode(params)}", base=DATA_URL)
        except AlpacaError as e:
            if " 429:" not in str(e) or attempt == 4:
                raise
            time.sleep(2 ** attempt)


def positions() -> dict[str, float]:
    """Alpaca symbol -> signed quantity."""
    out = {}
    for p in request("GET", "/v2/positions"):
        qty = float(p["qty"])
        out[p["symbol"].replace("USD", "/USD") if p.get("asset_class") == "crypto" and "/" not in p["symbol"]
            else p["symbol"]] = -abs(qty) if p.get("side") == "short" else qty
    return out


def wanted() -> dict[str, float]:
    """Net wanted quantity per Alpaca symbol, from paper/orders.json."""
    orders = json.loads((PAPER_DIR / "orders.json").read_text())
    net: dict[str, float] = {}
    for o in orders:
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
        orders.append({"symbol": sym, "side": "buy" if diff > 0 else "sell", "qty": round(abs(diff), 6),
                       "type": "market", "time_in_force": "gtc" if sym in crypto_syms else "day", "note": note})
    return orders


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


def _send(o: dict) -> dict:
    body = {k: (str(v) if k == "qty" else v) for k, v in o.items() if k != "note"}
    return request("POST", "/v2/orders", body)


CRYPTO_LIMIT_WAIT = 120  # seconds a crypto order waits on the book before the rest goes at market


def crypto_limit_first(o: dict, wait: float = CRYPTO_LIMIT_WAIT) -> tuple[str | None, str]:
    """Send a crypto order as a limit at the bid (buy) / ask (sell), so it rests on the
    book and pays the maker fee (0.15% vs 0.25% at market). Whatever has not filled
    after `wait` seconds is cancelled and sent at market. Every outcome goes to
    paper/fills.csv, to measure how often the cheaper fill happens.
    Returns (id of the last order sent, description)."""
    q = get_data("/v1beta3/crypto/us/latest/quotes", {"symbols": o["symbol"]})["quotes"][o["symbol"]]
    px = float(q["bp"] if o["side"] == "buy" else q["ap"])
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
    return last, how


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
    have = positions()

    # 2) market orders for the difference
    todo = plan(wanted(), have, prices)
    sent = {}
    for o in todo:
        line = f"{o['side'].upper():4s} {o['qty']:>12,.6f} {o['symbol']:8s} market {o['note']}"
        if send and "/" in o["symbol"]:  # crypto: rest on the book first (maker fee)
            oid, how = crypto_limit_first(o)
            if oid:
                sent[oid] = o["symbol"]
            line += f"  -> {how}"
        elif send:
            r = _send(o)
            sent[r.get("id")] = o["symbol"]
            line += f"  -> sent, id {r.get('id', '?')}"
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
                line += f"  -> REJECTED: {e}"
        print(line)
    if unfilled:
        print(f"Not filled yet (market closed?), protected once filled, on the next run: {', '.join(unfilled)}")
    if send and todo:  # phone notification (only when NTFY_TOPIC is set)
        from . import notify

        try:
            eq = float(request("GET", "/v2/account").get("equity", 0))
        except AlpacaError:
            eq = None
        for title, body, tags in notify.trade_messages(todo, eq):
            notify.send(title, body, tags)
    return todo + protective


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="test the keys and show the account")
    p = sub.add_parser("sync", help="match Alpaca to paper/orders.json")
    p.add_argument("--send", action="store_true", help="really send the orders (default: dry run)")
    args = ap.parse_args()
    if args.cmd == "check":
        acct = request("GET", "/v2/account")
        print(f"Alpaca PAPER account {acct.get('account_number')}: status {acct.get('status')}, "
              f"equity ${float(acct.get('equity', 0)):,.2f}, buying power ${float(acct.get('buying_power', 0)):,.2f}")
        print(f"Positions: {positions() or 'none'}")
    else:
        sync(args.send)


if __name__ == "__main__":
    main()
