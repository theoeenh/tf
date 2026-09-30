"""Phone notifications through ntfy (https://ntfy.sh): free app, no account.

Set the environment variable NTFY_TOPIC (a GitHub secret for the hourly job)
to a long random channel name and subscribe to it in the ntfy app. Without
it, nothing is sent. Messages only describe paper trades.
"""
from __future__ import annotations

import logging
import os
import urllib.request

log = logging.getLogger(__name__)
NTFY_URL = "https://ntfy.sh/"


def send(title: str, body: str, tags: str = "chart_with_upwards_trend", priority: str = "default") -> bool:
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        return False
    req = urllib.request.Request(NTFY_URL + topic, data=body.encode(), method="POST",
                                 headers={"Title": title, "Tags": tags, "Priority": priority})
    try:
        with urllib.request.urlopen(req, timeout=15):
            return True
    except Exception as exc:  # a notification must never stop the trading run
        log.warning("notification not sent (%s)", exc)
        return False


def trade_messages(orders: list[dict], equity: float | None = None) -> list[tuple[str, str, str]]:
    """(title, body, tags) for each order the sync sent: entries, exits, stops placed."""
    out = []
    for o in orders:
        if o.get("type") != "market":
            continue  # stops / targets being (re)placed each run are not news
        side = o["side"].upper()
        note = f" · {o['note']}" if o.get("note") else ""
        acct = os.environ.get("PAPER_ACCOUNT_NAME")
        title = (f"[{acct}] " if acct else "") + f"{side} {o['qty']:g} {o['symbol']}"
        body = f"Paper account{note}" + (f" · equity ${equity:,.0f}" if equity is not None else "")
        out.append((title, body, "green_circle" if o["side"] == "buy" else "red_circle"))
    return out
