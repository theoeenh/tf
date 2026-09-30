"""Mirror the paper account's positions on an Alpaca *paper* account.

    python -m algo.alpaca check      # test the keys, show the Alpaca paper account
    python -m algo.alpaca sync       # show the orders that would be sent (dry run)
    python -m algo.alpaca sync --send

Keys come from environment variables ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY
(Alpaca dashboard -> Paper account -> API Keys). Only the paper endpoint is
used; there is no switch to live trading in this file on purpose.

How it works: our system can hold several positions in the same asset (one per
strategy); Alpaca keeps one net position per symbol. `sync` adds up the wanted
positions from paper/orders.json per symbol and sends market orders for the
difference with what Alpaca holds. Stops and targets stay with our system,
which checks them on each daily update.
Limits: Alpaca cannot short crypto, so crypto shorts are skipped; stock shorts
are rounded down to whole shares (no fractional shorts).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import urllib.error
import urllib.request

from .data import CRYPTO
from .paper import PAPER_DIR

BASE_URL = "https://paper-api.alpaca.markets"
SYMBOLS = {"BTC": "BTC/USD", "ETH": "ETH/USD", "SOL": "SOL/USD", "NVDA": "NVDA", "TSLA": "TSLA",
           "GOLD": "GLD", "SILVER": "SLV"}
MIN_NOTIONAL = 5.0  # ignore differences smaller than $5


class AlpacaError(RuntimeError):
    pass


def _keys() -> tuple[str, str]:
    key, secret = os.environ.get("ALPACA_API_KEY_ID"), os.environ.get("ALPACA_API_SECRET_KEY")
    if not key or not secret:
        raise AlpacaError("Set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY in the environment settings.")
    return key, secret


def request(method: str, path: str, body: dict | None = None) -> dict | list:
    key, secret = _keys()
    req = urllib.request.Request(BASE_URL + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise AlpacaError(f"{method} {path} -> {e.code}: {e.read().decode(errors='replace')}") from None


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


def sync(send: bool = False) -> list[dict]:
    todo = plan(wanted(), positions(), last_prices())
    for o in todo:
        line = f"{o['side'].upper():4s} {o['qty']:>12,.6f} {o['symbol']:8s} {o['note']}"
        if send:
            body = {k: (str(v) if k == "qty" else v) for k, v in o.items() if k != "note"}
            r = request("POST", "/v2/orders", body)
            line += f"  -> sent, id {r.get('id', '?')}"
        print(line)
    if not todo:
        print("Alpaca already matches the paper account.")
    return todo


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
