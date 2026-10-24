"""Asset-class trend + momentum, monthly: account B from 26 October 2026 (user's go 2026-10-24).

    PAPER_ACCOUNT=B2 python -m algo.rotation update    # paper/B2/orders.json, status.md, trades.csv, equity.csv
    PAPER_ACCOUNT=B2 python -m algo.alpaca sync --send

At each month's last close, rank 8 asset-class ETFs by their 12-month return (month-end closes) and hold
the top 3, a third of the money each, but only those above their 10-month average; a slot that fails goes
to SHY (short Treasuries, the cash stand-in). Bought at the next session's open, held to the next month's
decision; no stops (the monthly trend filter is the exit). Textbook rules (Faber 2007, Moskowitz-Ooi-
Pedersen 2012), nothing tuned: reports/2026-10-20-trend-momentum/ (2007-2026: Sharpe 0.73 vs SPY 0.63,
worst fall -17% vs -55%). Market data only.
"""
from __future__ import annotations

import argparse
import json
import logging

import numpy as np
import pandas as pd

from .paper import PAPER_DIR

log = logging.getLogger(__name__)
RISKY = ["SPY", "EFA", "EEM", "TLT", "IEF", "GLD", "DBC", "VNQ"]
CASH = "SHY"
NAMES = {"SPY": "US stocks", "EFA": "developed stocks ex-US", "EEM": "emerging stocks", "TLT": "long Treasuries",
         "IEF": "7-10 year Treasuries", "GLD": "gold", "DBC": "commodities", "VNQ": "US real estate",
         "SHY": "short Treasuries (cash)"}
COST = 0.0005  # 5 bp per unit traded, as in the backtest


def completed_month_ends(close: pd.DataFrame, next_session: pd.Timestamp | None) -> pd.DataFrame:
    """Closes of the months that are over: the last session of each month, the current month only once
    its last session has closed (`next_session`, the next trading day, falls in another month)."""
    me = close.groupby(close.index.to_period("M")).tail(1)
    last = close.index[-1]
    if next_session is None or next_session.to_period("M") == last.to_period("M"):
        me = me[me.index.to_period("M") < last.to_period("M")]
    return me


def target_weights(me: pd.DataFrame, top: int = 3) -> dict[str, float]:
    """The decision at the last month-end of `me` (needs 13 month-ends): the backtest's topk()."""
    now = me.iloc[-1]
    mom12 = now / me.iloc[-13] - 1
    sma10 = me.iloc[-10:].mean()
    w: dict[str, float] = {}
    for a in mom12[RISKY].dropna().sort_values(ascending=False).index[:top]:
        k = a if now[a] > sma10[a] else CASH
        w[k] = w.get(k, 0.0) + 1 / top
    return w


def replay(open_: pd.DataFrame, close: pd.DataFrame, start: pd.Timestamp, capital: float,
           next_session: pd.Timestamp | None) -> dict:
    """The book from `start`: each completed month's decision (the one before `start` included) is
    traded at the next session's open at or after `start`. Returns equity, holdings (shares and entry),
    closed trades and the decision waiting for the next open, if any."""
    me = completed_month_ends(close, next_session)
    decisions = [(d, target_weights(me.loc[:d])) for d in me.index if len(me.loc[:d]) >= 13]
    first = max((i for i, (d, _) in enumerate(decisions) if d < start), default=0)
    decisions = decisions[first:]
    days = close.index[close.index >= start]
    cash, shares, entry, eq, trades = capital, {}, {}, {}, []
    todo = list(decisions)
    for day in days:
        while len(todo) > 1 and todo[1][0] < day:
            todo.pop(0)  # only the latest decision before this session counts
        if todo and todo[0][0] < day:
            d, w = todo.pop(0)
            px = open_.loc[day]
            value = cash + sum(q * px[a] for a, q in shares.items())
            new = {a: value * x / px[a] for a, x in w.items()}
            turnover = sum(abs(new.get(a, 0) - shares.get(a, 0)) * px[a] for a in set(new) | set(shares))
            for a, q in shares.items():
                if new.get(a, 0) < q - 1e-9:
                    sold = q - new.get(a, 0)
                    trades.append({"asset": a, "strategy": "trend_momentum", "side": 1, "entry_date": entry[a][0],
                                   "exit_date": str(day.date()), "entry": entry[a][1], "exit": float(px[a]),
                                   "qty": sold, "pnl": sold * (px[a] - entry[a][1]), "reason": "monthly rebalance"})
            for a, q in new.items():
                if q > shares.get(a, 0) + 1e-9 and a in shares:  # topped up: entry becomes the average price
                    old = shares[a]
                    entry[a] = (entry[a][0], (old * entry[a][1] + (q - old) * px[a]) / q)
                elif a not in shares:
                    entry[a] = (str(day.date()), float(px[a]))
            shares = {a: q for a, q in new.items() if q > 1e-9}
            entry = {a: entry[a] for a in shares}
            cash = value - sum(q * px[a] for a, q in shares.items()) - turnover * COST
        eq[day] = cash + sum(q * close.at[day, a] for a, q in shares.items())
    pending = todo[0] if todo and (not len(days) or todo[0][0] >= days[-1]) else None
    return {"equity": pd.Series(eq, dtype=float), "shares": shares, "entry": entry, "trades": trades,
            "pending": pending, "decision": decisions[-1] if decisions else None, "me": me}


def update() -> dict:
    from .paper import stock_sessions
    from .runner import load_bars

    cfg = json.loads((PAPER_DIR / "config.json").read_text())
    start, capital = pd.Timestamp(cfg["start"]), float(cfg["capital"])
    now_ny = pd.Timestamp.now(tz="America/New_York").tz_localize(None)
    bars = load_bars(RISKY + [CASH], now_ny, (start - pd.Timedelta(days=500)).strftime("%Y-%m-%d"))
    missing = [a for a in RISKY + [CASH] if a not in bars]
    if missing:
        raise RuntimeError(f"no daily bars for {', '.join(missing)}: nothing changed")
    close = pd.DataFrame({a: df["Close"] for a, df in bars.items()}).dropna()
    open_ = pd.DataFrame({a: df["Open"] for a, df in bars.items()}).reindex(close.index)
    nxt = [pd.Timestamp(o).tz_localize("UTC").tz_convert("America/New_York").tz_localize(None).normalize()
           for o, _ in stock_sessions(close.index[-1] + pd.Timedelta(days=1), days=10)]
    nxt = [d for d in nxt if d > close.index[-1]]
    book = replay(open_, close, start, capital, nxt[0] if nxt else None)
    last = close.iloc[-1]
    equity = float(book["equity"].iloc[-1]) if len(book["equity"]) else capital
    hold = book["shares"]
    if book["pending"] is not None:  # a decision waiting for the next open: the new shares, from today's equity
        hold = {a: equity * x / last[a] for a, x in book["pending"][1].items()}
    orders = [{"asset": a, "ticker": a, "strategy": "trend_momentum", "qty": float(q), "stop": None, "target": None,
               "mark": float(last[a]), "entry": float(book["entry"].get(a, (None, last[a]))[1]), "r": 0.0,
               "bar": f"{close.index[-1]:%Y-%m-%d}", **({"pending": True} if book["pending"] is not None else {})}
              for a, q in sorted(hold.items())]
    (PAPER_DIR / "orders.json").write_text(json.dumps(orders, indent=1, default=float))
    if len(book["equity"]):
        book["equity"].rename("equity").rename_axis("Date").to_csv(PAPER_DIR / "equity.csv")
    if book["trades"]:
        pd.DataFrame(book["trades"]).to_csv(PAPER_DIR / "trades.csv", index=False)
    write_status(cfg, book, close, equity, orders)
    print(f"{cfg.get('name')}: equity ${equity:,.0f}, holds {', '.join(o['asset'] for o in orders)}"
          + (" (bought at the next open)" if book["pending"] is not None else ""))
    return {"orders": orders, "equity": equity, "book": book}


def write_status(cfg: dict, book: dict, close: pd.DataFrame, equity: float, orders: list[dict]) -> None:
    me, cap = book["me"], float(cfg["capital"])
    d, w = book["decision"] if book["decision"] else (None, {})
    lines = [f"# {cfg.get('name', PAPER_DIR.name)}", "",
             f"Started {cfg['start'][:10]} with ${cap:,.0f}. Data through {close.index[-1].date()}. "
             f"**Equity ${equity:,.0f}** ({equity / cap - 1:+.2%}).", "", cfg.get("plan", ""), "",
             "## Holdings" + (" (bought at the next open)" if book["pending"] is not None else ""), ""]
    lines += [f"- **{o['asset']}** ({NAMES[o['asset']]}) {o['qty']:.2f} shares, now {o['mark']:.2f}"
              + ("" if o.get("pending") else f", bought at {o['entry']:.2f} ({o['mark'] / o['entry'] - 1:+.1%})")
              for o in orders] or ["None."]
    if d is not None and len(me.loc[:d]) >= 13:
        m = me.loc[:d]
        mom12, sma10 = m.iloc[-1] / m.iloc[-13] - 1, m.iloc[-10:].mean()
        lines += ["", f"## Decision of {d.date()} (12-month return, 10-month average)", "",
                  "| ETF | asset class | 12-month return | above its 10-month average | weight |", "|---|---|---|---|---|"]
        for a in mom12[RISKY].sort_values(ascending=False).index:
            lines.append(f"| {a} | {NAMES[a]} | {mom12[a]:+.1%} | {'yes' if m.iloc[-1][a] > sma10[a] else 'no'} "
                         f"| {w.get(a, 0):.0%} |")
        lines.append(f"| {CASH} | {NAMES[CASH]} | | | {w.get(CASH, 0):.0%} |")
    lines += ["", "Next decision: the last close of the month; traded at the next open (opening auction)."]
    if book["trades"]:
        lines += ["", "## Closed (monthly rebalances)", ""] + [
            f"- {t['exit_date']} {t['asset']}: {t['qty']:.2f} shares, {t['entry']:.2f} → {t['exit']:.2f}, ${t['pnl']:+,.0f}"
            for t in reversed(book["trades"])]
    (PAPER_DIR / "status.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["update"])
    ap.parse_args()
    update()


if __name__ == "__main__":
    main()
