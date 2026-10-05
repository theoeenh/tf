"""Daily runner: an account that trades one finder strategy on the S&P 1500, mirrored on Alpaca.

    PAPER_ACCOUNT=E python -m algo.runner update     # replay + plan (paper/E/orders.json, status.md)
    PAPER_ACCOUNT=E python -m algo.alpaca sync --send

paper/<X>/config.json holds the strategy (a finder candidate, as in the registry), the start date and
the capital. Each run:
1. downloads the daily bars of the strategy's stocks (complete sessions only) and the insider filings
   of the last days (SEC daily index; wide.update_insider_recent), for the families that need them;
2. replays the strategy from the start date with the finder's own engine, costs, sizing and exits
   (positions stay open at the end), exactly as it was scored;
3. adds the entries of the last session's signals (they fill at the next open, so they are not in
   the replay yet): size and stop from that session's ATR, like the engine;
4. writes orders.json in the hourly accounts' format, so algo.alpaca mirrors it (market-on-open
   orders before the open, stops at the broker, the same checks and alerts).
"""
from __future__ import annotations

import argparse
import json
import logging

import numpy as np
import pandas as pd

from . import finder as F
from . import wide
from .engine import ExitRule
from .indicators import atr
from .paper import PAPER_DIR
from .portfolio import PortfolioConfig, Sleeve, run_portfolio
from .system import MAX_GROSS, MAX_OPEN_RISK

log = logging.getLogger(__name__)
INSIDER_FAMILIES = {"insider_cluster", "insider_big_buy", "insider_dip", "insider_ml"}


def complete_sessions(df: pd.DataFrame, now_ny: pd.Timestamp) -> pd.DataFrame:
    """Drop today's bar until the session is over (16:15 New York, so the close is final)."""
    today = now_ny.normalize()
    done = now_ny >= today + pd.Timedelta(hours=16, minutes=15)
    return df if done else df[df.index < today]


def load_bars(symbols: list[str], now_ny: pd.Timestamp) -> dict[str, pd.DataFrame]:
    raw = pd.concat([wide._bars(symbols[i:i + 50], wide.START) for i in range(0, len(symbols), 50)],
                    ignore_index=True)
    out = {}
    for sym, g in raw.groupby("symbol"):
        g = g.set_index("date").sort_index()[["Open", "High", "Low", "Close", "Volume"]]
        g.index.name = "Date"
        g = complete_sessions(g[g["Volume"] > 0], now_ny)
        if len(g) >= 250:
            out[sym] = g
    return out


def pending_entries(c: F.Candidate, sig: dict, prices: dict, held: set, equity: float) -> list[dict]:
    """Signals on the last complete session, not in the replay yet (they fill at the next open)."""
    rule = ExitRule(**c.rule)
    out = []
    for a, s in sig.items():
        if a in held or not len(s) or s.iloc[-1] <= 0 or s.index[-1] != prices[a].index[-1]:
            continue
        df = prices[a]
        a_atr = float(atr(df).iloc[-1])
        close = float(df["Close"].iloc[-1])
        if not np.isfinite(a_atr) or a_atr <= 0:
            continue
        risk_each = rule.stop_atr * a_atr
        qty = F.RISK * equity / risk_each
        qty = min(qty, MAX_GROSS * equity / close / 4)  # never more than half the gross limit on one stock
        out.append({"asset": a, "ticker": a, "strategy": c.family, "qty": float(qty),
                    "stop": close - risk_each, "target": None, "mark": close, "entry": close, "r": 0.0,
                    "pending": True})
    return out


def update(fetch_insider: bool = True) -> dict:
    cfg = json.loads((PAPER_DIR / "config.json").read_text())
    c = F.Candidate(**json.loads(cfg["candidate"]))
    start = pd.Timestamp(cfg["start"])
    now_ny = pd.Timestamp.now(tz="America/New_York").tz_localize(None)
    universe = [a for a in wide.members() if wide.segment(c.assets)(a)]
    if fetch_insider and c.family in INSIDER_FAMILIES:
        wide.update_insider_recent(days=10, tickers=universe)
    prices = load_bars(universe, now_ny)
    sig = F.signals(c, prices)
    lo = start - pd.Timedelta(days=400)
    active = {a: s for a, s in sig.items() if (s[s.index >= lo] != 0).any()}
    sleeves = [Sleeve(a, c.family, s.reindex(prices[a].index).fillna(0).astype(int), ExitRule(**c.rule), c.short)
               for a, s in active.items()]
    cfg_pf = PortfolioConfig(initial_capital=cfg["capital"], risk_pct=F.RISK, max_gross=MAX_GROSS,
                             max_open_risk=MAX_OPEN_RISK)
    last = max(df.index[-1] for df in prices.values())
    if sleeves and last > start:
        res = run_portfolio({a: prices[a] for a in active}, sleeves, wide.costs(active), cfg_pf, start, None,
                            close_at_end=False)
        equity = float(res.equity.iloc[-1])
        live = [p for p in res.open_positions if not p["shadow"]]
        trades = res.trades_df
    else:
        equity, live, trades = float(cfg["capital"]), [], pd.DataFrame()
    orders = [{"asset": p["asset"], "ticker": p["asset"], "strategy": p["strategy"], "qty": p["side"] * p["qty"],
               "stop": p["stop"], "target": p["target"], "mark": p["mark"], "entry": p["entry"],
               "r": p.get("unrealised_r", 0.0)} for p in live]
    pend = pending_entries(c, sig, prices, {o["asset"] for o in orders}, equity)
    (PAPER_DIR / "orders.json").write_text(json.dumps(orders + pend, indent=1, default=float))
    if len(trades):
        trades.to_csv(PAPER_DIR / "trades.csv", index=False)
    lines = [f"# {cfg.get('name', PAPER_DIR.name)}", "",
             f"Strategy: `{c.id}` {c.label()}", f"Started {start.date()} with ${cfg['capital']:,.0f}. "
             f"Data through {last.date()}. **Equity ${equity:,.0f}** ({equity / cfg['capital'] - 1:+.2%}).", "",
             cfg.get("plan", ""), "", "## Open positions", ""]
    lines += [f"- **{o['asset']}** {o['qty']:.2f} shares, entry {o['entry']:.2f}, stop {o['stop']:.2f}, "
              f"now {o['mark']:.2f} ({o['r']:+.2f}R)" for o in orders] or ["None."]
    lines += ["", "## New signals (bought at the next open)", ""]
    lines += [f"- **{o['asset']}** {o['qty']:.2f} shares around {o['mark']:.2f}, stop {o['stop']:.2f}" for o in pend] or ["None."]
    if len(trades):
        lines += ["", "## Closed trades", ""] + [
            f"- {t.exit_date:%Y-%m-%d} {t.asset}: {t.r_multiple:+.2f}R, ${t.pnl:+,.0f} ({t.reason})"
            for t in trades.itertuples()]
    (PAPER_DIR / "status.md").write_text("\n".join(lines) + "\n")
    print(f"{cfg.get('name')}: equity ${equity:,.0f}, {len(orders)} open, {len(pend)} new at the next open")
    return {"orders": orders, "pending": pend, "equity": equity}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["update"])
    ap.add_argument("--no-fetch", action="store_true", help="use the insider filings already downloaded")
    args = ap.parse_args()
    update(fetch_insider=not args.no_fetch)


if __name__ == "__main__":
    main()
