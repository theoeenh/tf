"""Paper trading: run the system forward on live data, without real money.

    python -m algo.paper init                 # start a $100k paper account now
    python -m algo.paper init --interval 1h   # hourly version (many trades a day)
    python -m algo.paper init --interval 1h --source alpaca   # hourly, on the broker's own prices
    python -m algo.paper update               # fetch new bars, trade them, write paper/status.md

`update` is deterministic: it replays the system from the paper start date on
the latest bars, so running it once an hour or once a day gives the same
result as a backtest of the same period. Before the start date the learner is
trained on history, so the paper account starts with everything it has
learned so far. Only complete bars are used: a bar that is still forming
(today's daily candle, the current hour) is ignored until it closes.

Broker connection: `orders.json` lists the positions the system wants, with
their stops and targets. A broker adapter (for your paper account's API)
turns that into orders; see `Broker` below.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import pandas as pd

from . import data
from .metrics import equity_stats
from . import analyst, news
from .system import (
    ALL_VARIANTS, OPTIONS, TARGET_VOL, UNIVERSES, bars_per_year, build_context, calibrate_risk, load_prices,
    new_learner, run_variant,
)

log = logging.getLogger(__name__)
# One folder per paper account: paper/ (account A) or paper/<PAPER_ACCOUNT>/ (B, C...).
PAPER_DIR = Path(__file__).resolve().parent.parent / "paper" / os.environ.get("PAPER_ACCOUNT", "")

# Calibration windows, same as the backtest report.
DAILY_TRAIN = ("2016-09-29", "2022-12-31")


class Broker(Protocol):
    """What a broker adapter must provide to mirror the paper account."""

    def positions(self) -> dict[str, float]: ...  # asset -> signed quantity

    def submit(self, asset: str, qty: float, stop: float | None, target: float | None) -> None: ...


def now_utc() -> pd.Timestamp:
    return pd.Timestamp(datetime.now(timezone.utc)).tz_convert(None)


def complete_bars(df: pd.DataFrame, asset: str, interval: str, now: pd.Timestamp) -> pd.DataFrame:
    """Drop bars that have not closed yet."""
    if interval == "1h":
        length = pd.Timedelta(hours=1)
    elif asset in data.CRYPTO:
        length = pd.Timedelta(days=1)  # UTC day
    else:
        length = pd.Timedelta(hours=21)  # US close is 20:00-21:00 UTC
    return df[df.index + length <= now]


def bars_since(prices: dict, start: pd.Timestamp) -> int:
    """Distinct bar times at or after `start` across all assets."""
    return len(set().union(*(df.index[df.index >= start] for df in prices.values())))


def news_context(prices: dict, v: dict, interval: str = "1d") -> dict | None:
    """(the assets are those of `prices`)"""
    """News, events, AI views (and on hourly bars the daily trend, event blackout and
    Alpaca news) for the variants that use them. Fetches only what is missing."""
    if not (v.get("news") or v.get("ml") or v.get("blackout")):
        return None
    nd = news.load_all(list(prices), strict=True, alpaca_news=interval != "1d")
    return build_context(prices, nd, analyst.bias_frame(analyst.load_views()))


def init(capital: float, variant: str, interval: str, start: str | None = None, source: str = "auto",
         universe: str = "core", history_start: str | None = None, name: str | None = None) -> dict:
    v = ALL_VARIANTS[variant]
    prices = load_prices(source, interval, UNIVERSES[universe], history_start)
    if interval == "1d":
        train = DAILY_TRAIN
    else:
        idx = prices["BTC"].index
        train = (idx[0] + pd.Timedelta(days=10), idx[0] + (idx[-1] - idx[0]) * 0.6)
    risk = calibrate_risk(prices, v["allow_short"], v["learn"], *train, news=v.get("news", False),
                          context=news_context(prices, v, interval),
                          # sized like the same version without the brake (a pulled brake would fake low volatility)
                          **{o: v.get(o, False) for o in OPTIONS if o != "brake"})
    cfg = {"start": str(pd.Timestamp(start) if start else now_utc().floor("h")), "capital": capital, "variant": variant, "interval": interval,
           "source": source, "risk_pct": risk, "target_vol": TARGET_VOL, "universe": list(UNIVERSES[universe]),
           "history_start": history_start, "name": name or variant}
    PAPER_DIR.mkdir(exist_ok=True)
    (PAPER_DIR / "config.json").write_text(json.dumps(cfg, indent=2))
    return cfg


def update(source: str | None = None) -> Path:
    """source: None = the one the account was started with (config.json)."""
    cfg = json.loads((PAPER_DIR / "config.json").read_text())
    source = source or cfg.get("source", "auto")
    v, interval = ALL_VARIANTS[cfg["variant"]], cfg["interval"]
    start, now = pd.Timestamp(cfg["start"]), now_utc()
    prices = {a: complete_bars(df, a, interval, now)
              for a, df in load_prices(source, interval, cfg["universe"], cfg.get("history_start")).items()}

    ctx = news_context(prices, v, interval)

    # 1) Learn from history up to the start date.
    learner = new_learner(v["learn"], v.get("news", False), v.get("ml", False), v.get("sizing", False),
                          prices=prices, context=ctx)
    if learner is not None:
        hist_start = min(df.index[0] for df in prices.values())
        run_variant(prices, v, cfg["risk_pct"], hist_start, start - pd.Timedelta(seconds=1), ctx, learner=learner)

    # 2) Trade from the start date with the paper capital, keep positions open.
    lines = [f"# Paper account – {cfg['variant']}, {interval} bars", "",
             f"Started {start} UTC with ${cfg['capital']:,.0f}; risk {cfg['risk_pct']:.2%} per trade "
             f"(sized for ~{cfg['target_vol']:.0%} yearly volatility). Updated {now:%Y-%m-%d %H:%M} UTC.", ""]
    if bars_since(prices, start) < 2:  # the backtester needs two bar times
        lines += ["No complete bar since the start yet. Nothing to do."]
        res = None
    else:
        res = run_variant(prices, v, cfg["risk_pct"], start, None, ctx, initial_capital=cfg["capital"],
                          close_at_end=False, learner=learner)
        eq = res.equity
        st = equity_stats(eq, bars_per_year(eq.index)) if len(eq) > 2 else {}
        lines += [f"**Equity ${eq.iloc[-1]:,.0f}** ({eq.iloc[-1] / cfg['capital'] - 1:+.2%}) · "
                  f"max drawdown {st.get('max_drawdown', 0):.1%} · {len(res.trades)} closed trades · "
                  f"{len([p for p in res.open_positions if not p['shadow']])} open", ""]

    orders = []
    if res is not None:
        lines += ["## Open positions", ""]
        live = [p for p in res.open_positions if not p["shadow"]]
        if not live:
            lines += ["None.", ""]
        for p in live:
            tgt = "none (trailing)" if p["target"] is None else f"{p['target']:,.2f}"
            lines += [f"- **{'LONG' if p['side'] > 0 else 'SHORT'} {p['qty']:.4f} {p['asset']}** "
                      f"({p['strategy']}) since {p['entry_time']:%Y-%m-%d %H:%M}, entry {p['entry']:,.2f}, "
                      f"stop {p['stop']:,.2f}, target {tgt}, now {p['unrealised_r']:+.2f}R  \n"
                      f"  *Thinking:* {p['rationale']}"]
            orders.append({"asset": p["asset"], "ticker": data.TICKERS[p["asset"]], "strategy": p["strategy"],
                           "qty": p["side"] * p["qty"], "stop": p["stop"], "target": p["target"],
                           "mark": p["mark"], "entry": p["entry"], "r": p["unrealised_r"]})
        lines += ["", "## Closed trades (newest first)", ""]
        for t in reversed(res.trades):
            lines += [f"- **{t.exit_date:%Y-%m-%d %H:%M} · {'LONG' if t.side > 0 else 'SHORT'} {t.asset} · "
                      f"{t.strategy} · {t.r_multiple:+.2f}R · ${t.pnl:+,.0f}** (fees ${t.fees:,.0f}, {t.reason})  \n"
                      f"  *Thinking:* {t.rationale}  \n  *Lesson:* {t.lesson}"]
        skipped = [p for p in res.open_positions if p["shadow"]] + list(res.shadow_trades)
        if skipped:
            lines += ["", f"## Skipped by the learner ({len(skipped)})", ""]
            for s in res.shadow_trades[-10:]:
                lines += [f"- {s.entry_date:%Y-%m-%d %H:%M} {s.asset} {s.strategy}: would have made "
                          f"{s.r_multiple:+.2f}R. {s.rationale.split(' Would have been')[0]}"]
        if res.trades:
            res.trades_df.to_csv(PAPER_DIR / "trades.csv", index=False)
        res.equity.to_csv(PAPER_DIR / "equity.csv")
    (PAPER_DIR / "orders.json").write_text(json.dumps(orders, indent=2, default=str))
    out = PAPER_DIR / "status.md"
    out.write_text("\n".join(lines) + "\n")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_init = sub.add_parser("init", help="start a new paper account now")
    p_init.add_argument("--capital", type=float, default=100_000.0)
    p_init.add_argument("--variant", default="long/short + learner + news", choices=list(ALL_VARIANTS))
    p_init.add_argument("--interval", default="1d", choices=["1d", "1h"])
    p_init.add_argument("--start", default=None, help="backdate the start (replay), e.g. 2026-09-01")
    p_init.add_argument("--source", default="auto", choices=["auto", "yahoo", "csv", "alpaca"])
    p_init.add_argument("--universe", default="core", choices=list(UNIVERSES))
    p_init.add_argument("--history-start", default=None, help="first bar used (default: all cached data)")
    p_init.add_argument("--name", default=None, help="label shown in notifications and the dashboard")
    p_up = sub.add_parser("update", help="trade new bars and write paper/status.md")
    p_up.add_argument("--source", default=None, choices=["auto", "yahoo", "csv", "alpaca"],
                      help="default: the source the account was started with")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.cmd == "init":
        cfg = init(args.capital, args.variant, args.interval, args.start, args.source, args.universe,
                   args.history_start, args.name)
        print(f"Paper account started: {json.dumps(cfg)}")
    else:
        print(f"Status written to {update(args.source)}")


if __name__ == "__main__":
    main()
