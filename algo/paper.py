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
    ALL_VARIANTS, OPTIONS, TARGET_VOL, UNIVERSES, bars_per_year, build_context, calibrate_risk, concentration_caps,
    load_prices,
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


def stock_sessions(first_day: pd.Timestamp, days: int = 10) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """(open, close) in UTC of the US stock sessions from `first_day` on: Alpaca's market calendar
    (holidays, half days), else every weekday 9:30-16:00 New York."""
    end = first_day + pd.Timedelta(days=days)
    try:
        from .alpaca import request

        rows = [(c["date"], c["open"], c["close"])
                for c in request("GET", f"/v2/calendar?start={first_day:%Y-%m-%d}&end={end:%Y-%m-%d}")]
    except Exception as e:  # no keys or no network: a holiday is then taken for a session
        log.warning("market calendar unavailable (%s): weekdays 9:30-16:00", e)
        rows = [(f"{d:%Y-%m-%d}", "09:30", "16:00") for d in pd.bdate_range(first_day, end)]

    def utc(day: str, hm: str) -> pd.Timestamp:
        return pd.Timestamp(f"{day} {hm}").tz_localize("America/New_York").tz_convert("UTC").tz_localize(None)

    return sorted((utc(d, o), utc(d, c)) for d, o, c in rows)


def next_stock_bar(last: pd.Timestamp, sessions: list) -> pd.Timestamp | None:
    """Start of the stock bar after `last` (bars cut on the clock hour inside the session: the first
    one 9:30-10:00 starts at 9:00 New York)."""
    nxt = last + pd.Timedelta(hours=1)
    for open_, close in sessions:
        if close <= last:
            continue
        first = open_.floor("h")
        if first <= nxt < close:
            return nxt
        if first > last:
            return first
    return None


def next_bars(prices: dict, interval: str, now: pd.Timestamp) -> dict[str, pd.Timestamp]:
    """Live, hourly bars: per asset, the start of the bar forming now. Its orders go out as soon as the
    bar before it has closed (the backtest's fill at the next bar's open), not once it has closed itself
    (2026-10-20: orders went out 80 minutes after the paper's entry price). Left out when the asset's
    data is behind (that bar is already over): nothing is guessed then."""
    if interval != "1h":
        return {}
    stocks = [df.index[-1] for a, df in prices.items() if a not in data.CRYPTO and len(df)]
    sessions = stock_sessions(min(stocks).normalize()) if stocks else []
    out = {}
    for a, df in prices.items():
        if df.empty:
            continue
        last = df.index[-1]
        if a in data.CRYPTO:
            nxt, ready = last + pd.Timedelta(hours=1), now
        else:
            nxt, ready = next_stock_bar(last, sessions), now - pd.Timedelta(minutes=data.SIP_DELAY_MIN)
        if nxt is not None and nxt + pd.Timedelta(hours=1) > ready:
            out[a] = nxt
    return out


def with_next_bar(prices: dict, nxt: dict) -> dict:
    """The prices with one more row per asset in `nxt`: the bar forming now, at the last close (only its
    open is used: the engine's next_open)."""
    out = dict(prices)
    for a, t in nxt.items():
        c = prices[a]["Close"].iloc[-1]
        row = pd.DataFrame({"Open": c, "High": c, "Low": c, "Close": c, "Volume": 0.0}, index=pd.DatetimeIndex([t]))
        out[a] = pd.concat([prices[a], row.reindex(columns=prices[a].columns)])
    return out


def bars_since(prices: dict, start: pd.Timestamp) -> int:
    """Distinct bar times at or after `start` across all assets."""
    return len(set().union(*(df.index[df.index >= start] for df in prices.values())))


def news_context(prices: dict, v: dict, interval: str = "1d") -> dict | None:
    """(the assets are those of `prices`)"""
    """News, events, AI views (and on hourly bars the daily trend, event blackout and
    Alpaca news) for the variants that use them. Fetches only what is missing."""
    if not (v.get("news") or v.get("ml") or v.get("blackout")):
        return None
    nd = news.load_all(list(prices), strict=True, alpaca_news=interval != "1d",
                       global_markets=v.get("global", False), insider=v.get("insider", False))
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


class FrozenDecisions:
    """A live decision is made once. The learner's verdict on every trade candidate from the start
    date on is stored (paper/<account>/decisions.json) and reused by every later replay: the
    replay must not re-decide the past when the model, the news features or the data are
    revised later (on 2026-10-06 a refit flipped a borderline skip of 2 days before and
    rewrote account C's history). Candidates before the start date are left to the learner."""

    def __init__(self, learner, start: pd.Timestamp, path: Path):
        self.learner, self.start, self.path = learner, start, path
        self.cache = json.loads(path.read_text()) if path.exists() else {}
        self.added = 0

    def __getattr__(self, name):
        return getattr(self.learner, name)

    @staticmethod
    def key_of(key: dict) -> str:
        side = "+" if key["x"][0] >= 0 else "-"  # the first feature is the side
        return f"{key['sleeve'][0]}|{key['strategy']}|{side}|{key['time']:%Y-%m-%d %H:%M}"

    def judge(self, key):
        from .journal import Verdict

        t = key.get("time") if isinstance(key, dict) else None
        if t is None or t < self.start:
            return self.learner.judge(key)
        k = self.key_of(key)
        if k in self.cache:
            d = self.cache[k]
            if d.get("pred") is not None:
                key["pred"] = tuple(d["pred"])
            return Verdict(d["skip"], d["reason"], d["size"])
        v = self.learner.judge(key)
        self.cache[k] = {"skip": v.skip, "reason": v.reason, "size": v.size,
                         "pred": list(key["pred"]) if key.get("pred") is not None else None}
        self.added += 1
        return v

    def save(self) -> None:
        self.path.write_text(json.dumps(dict(sorted(self.cache.items())), indent=0))


def update(source: str | None = None) -> Path:
    """source: None = the one the account was started with (config.json)."""
    cfg = json.loads((PAPER_DIR / "config.json").read_text())
    source = source or cfg.get("source", "auto")
    v, interval = ALL_VARIANTS[cfg["variant"]], cfg["interval"]
    start, now = pd.Timestamp(cfg["start"]), now_utc()
    real = {a: complete_bars(df, a, interval, now)
            for a, df in load_prices(source, interval, cfg["universe"], cfg.get("history_start")).items()}
    # the bar forming now: traded at its open as soon as the bar before it has closed (see next_bars)
    nxt = next_bars(real, interval, now)
    prices = with_next_bar(real, nxt)

    ctx = news_context(prices, v, interval)
    ctx_real = None if ctx is None else {a: c.reindex(real[a].index) if a in real else c for a, c in ctx.items()}

    # 1) Learn from history up to the start date.
    learner = new_learner(v["learn"], v.get("news", False), v.get("ml", False), v.get("sizing", False),
                          prices=real, context=ctx_real)
    if learner is not None:
        hist_start = min(df.index[0] for df in real.values())
        run_variant(real, v, cfg["risk_pct"], hist_start, start - pd.Timedelta(seconds=1), ctx_real, learner=learner)

    # 2) Trade from the start date with the paper capital, keep positions open.
    lines = [f"# Paper account – {cfg['variant']}, {interval} bars", "",
             f"Started {start} UTC with ${cfg['capital']:,.0f}; risk {cfg['risk_pct']:.2%} per trade "
             f"(sized for ~{cfg['target_vol']:.0%} yearly volatility). Updated {now:%Y-%m-%d %H:%M} UTC.", ""]
    if bars_since(real, start) < 2:  # the backtester needs two bar times
        lines += ["No complete bar since the start yet. Nothing to do."]
        res = None
    else:
        frozen = FrozenDecisions(learner, start, PAPER_DIR / "decisions.json") if learner is not None else None
        res = run_variant(prices, v, cfg["risk_pct"], start, None, ctx, initial_capital=cfg["capital"],
                          close_at_end=False, learner=frozen or learner, retired=cfg.get("retired"),
                          concentration=concentration_caps(cfg), next_open=frozenset(nxt))
        if frozen is not None:
            frozen.save()
        # the books hold the closed bars only; what happens at the open of the bar forming now is listed apart
        at_open = lambda asset, t: nxt.get(asset) == t  # noqa: E731
        eq = res.equity[res.equity.index <= max(df.index[-1] for df in real.values() if len(df))]
        done = [t for t in res.trades if not at_open(t.asset, t.exit_date)]
        leaving = [t for t in res.trades if at_open(t.asset, t.exit_date)]
        held = [p for p in res.open_positions if not p["shadow"] and not at_open(p["asset"], p["entry_time"])]
        st = equity_stats(eq, bars_per_year(eq.index)) if len(eq) > 2 else {}
        lines += [f"**Equity ${eq.iloc[-1]:,.0f}** ({eq.iloc[-1] / cfg['capital'] - 1:+.2%}) · "
                  f"max drawdown {st.get('max_drawdown', 0):.1%} · {len(done)} closed trades · "
                  f"{len(held) + len(leaving)} open", ""]

    orders = []
    if res is not None:
        lines += ["## Open positions", ""]
        live = [p for p in res.open_positions if not p["shadow"]]
        new = [p for p in live if at_open(p["asset"], p["entry_time"])]
        if not held and not leaving:
            lines += ["None.", ""]
        closing = set()
        if v.get("blackout") and interval == "1h":  # be flat before an event bar starts, not after it
            for p in live:
                a = p["asset"]
                if news.next_bar_blocked(real[a].index, news.earnings_dates(a) if a not in data.CRYPTO
                                         and news.ASSET_CLASS.get(a) == "stock" else [],
                                         news.fomc_dates(), news.jobs_report_dates(), stock=a not in data.CRYPTO):
                    closing.add(id(p))
        retired = {a: pd.Timestamp(t) for a, t in (cfg.get("retired") or {}).items()}
        for p in live:  # no longer traded by this account: out now, not once the next bar is final
            if p["asset"] in retired and now >= retired[p["asset"]]:
                closing.add(id(p))
        for p in held:
            tgt = "none (trailing)" if p["target"] is None else f"{p['target']:,.2f}"
            lines += [f"- **{'LONG' if p['side'] > 0 else 'SHORT'} {p['qty']:.4f} {p['asset']}** "
                      f"({p['strategy']}) since {p['entry_time']:%Y-%m-%d %H:%M}, entry {p['entry']:,.2f}, "
                      f"stop {p['stop']:,.2f}, target {tgt}, now {p['unrealised_r']:+.2f}R  \n"
                      f"  *Thinking:* {p['rationale']}"]
            if id(p) in closing:
                why = ("this account no longer trades it (retired)" if p["asset"] in retired
                       else "the next bar is a scheduled event (blackout); flat before it starts")
                lines += [f"  *Closing now:* {why}."]
        for t in leaving:
            lines += [f"- **{'LONG' if t.side > 0 else 'SHORT'} {t.qty:.4f} {t.asset}** ({t.strategy}) since "
                      f"{t.entry_date:%Y-%m-%d %H:%M}, entry {t.entry:,.2f}  \n"
                      f"  *Closing now* (at the open of the {t.exit_date:%Y-%m-%d %H:%M} bar): {t.reason}."]
        if new:
            lines += ["", "## Opening now (at the open of the bar forming now)", ""]
            for p in new:
                tgt = "none (trailing)" if p["target"] is None else f"{p['target']:,.2f}"
                lines += [f"- **{'LONG' if p['side'] > 0 else 'SHORT'} {p['qty']:.4f} {p['asset']}** "
                          f"({p['strategy']}) for the {p['entry_time']:%Y-%m-%d %H:%M} bar, at about "
                          f"{p['entry']:,.2f}, stop {p['stop']:,.2f}, target {tgt}  \n"
                          f"  *Thinking:* {p['rationale']}"]
        for p in live:
            if id(p) in closing:
                continue
            orders.append({"asset": p["asset"], "ticker": data.TICKERS[p["asset"]], "strategy": p["strategy"],
                           "qty": p["side"] * p["qty"], "stop": p["stop"], "target": p["target"],
                           "mark": p["mark"], "entry": p["entry"], "r": p["unrealised_r"],
                           # its last closed bar: the stop check in algo.alpaca starts after it
                           "bar": str(real[p["asset"]].index[-1]) if p["asset"] in real else None})
        lines += ["", "## Closed trades (newest first)", ""]
        for t in reversed(done):
            lines += [f"- **{t.exit_date:%Y-%m-%d %H:%M} · {'LONG' if t.side > 0 else 'SHORT'} {t.asset} · "
                      f"{t.strategy} · {t.r_multiple:+.2f}R · ${t.pnl:+,.0f}** (fees ${t.fees:,.0f}, {t.reason})  \n"
                      f"  *Thinking:* {t.rationale}  \n  *Lesson:* {t.lesson}"]
        shadows = [t for t in res.shadow_trades if not at_open(t.asset, t.exit_date)]
        skipped = [p for p in res.open_positions if p["shadow"]] + shadows
        if skipped:
            lines += ["", f"## Skipped by the learner ({len(skipped)})", ""]
            for s in shadows[-10:]:
                lines += [f"- {s.entry_date:%Y-%m-%d %H:%M} {s.asset} {s.strategy}: would have made "
                          f"{s.r_multiple:+.2f}R. {s.rationale.split(' Would have been')[0]}"]
        if done:
            pd.DataFrame([t.__dict__ for t in done]).to_csv(PAPER_DIR / "trades.csv", index=False)
        eq.to_csv(PAPER_DIR / "equity.csv")
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
