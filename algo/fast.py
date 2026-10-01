"""Fast day trading on 5-minute bars: research only, no account trades it yet.

    python -m algo.fast            # download 5-minute bars, run the study, write reports/<date>-fast/report.md

Many short trades a day (minutes to a couple of hours), every stock position
flat by the close. The question it answers before any money goes near it:
after fees and slippage, does any of these strategies beat random entries with
the same exits, in a test window it was never tuned on?

Data: Alpaca 5-minute bars. Stocks: regular session only (9:30-16:00 New York),
full-market (SIP) feed. Crypto: around the clock. Timestamps are bar starts, UTC.

Costs matter far more here than on hourly bars: a 5-minute move is often a few
basis points. Stocks pay ~0 commission but a spread (slippage below); crypto pays
Alpaca's fee on every fill (0.25% taker, 0.15% maker), which a 5-minute edge
almost never covers, so crypto is tested with both fees to show it.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from . import data
from .engine import Costs, ExitRule
from .indicators import atr, rsi, sma
from .metrics import equity_stats
from .portfolio import PortfolioConfig, Sleeve, run_portfolio
from .strategies import _combine

log = logging.getLogger(__name__)
START = "2025-01-01"
STOCKS = ("QQQ", "NVDA", "TSLA", "AAPL", "MSFT", "AMD", "META", "AMZN", "GOOGL", "COIN", "IWM")
CRYPTO = ("BTC", "ETH", "SOL")
SPLIT = 0.6  # first 60% of the period: choose; last 40%: test, untouched

# Per side. Stocks: commission-free, ~1-2 bp half-spread on these liquid names at 5-minute size.
STOCK_COST = Costs(fee_bps=0.2, slippage_bps=1.5, short_borrow_apr=0.01)
CRYPTO_TAKER = Costs(fee_bps=25, slippage_bps=2, short_borrow_apr=0.10)
CRYPTO_MAKER = Costs(fee_bps=15, slippage_bps=0, short_borrow_apr=0.10)

RULES = {  # time stops in 5-minute bars
    "orb15": ExitRule(stop_atr=1.5, rr=2.0, max_bars=48),       # out within 4 h (and by the close)
    "vwap_fade": ExitRule(stop_atr=1.5, rr=1.5, max_bars=12),   # 1 h
    "range_break": ExitRule(stop_atr=1.5, rr=2.0, max_bars=24),  # 2 h
    "rsi2_5m": ExitRule(stop_atr=2.0, rr=1.5, max_bars=12),      # 1 h
}


# ----------------------------------------------------------------- data

def load_5m(name: str, refresh: bool = False) -> pd.DataFrame:
    """5-minute bars, cached in data/<name>_5m_alpaca.csv (only new bars are fetched)."""
    from .alpaca import get_data

    path = data.DATA_DIR / f"{name}_5m_alpaca.csv"
    old = None if refresh or not path.exists() else pd.read_csv(path, index_col=0, parse_dates=True)
    start = pd.Timestamp(START) if old is None or old.empty else old.index[-1] - pd.Timedelta(days=2)
    crypto = name in data.CRYPTO
    sym = data.ALPACA_SYMBOLS[name]
    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    cutoff = now if crypto else now - pd.Timedelta(minutes=data.SIP_DELAY_MIN)
    p = "/v1beta3/crypto/us/bars" if crypto else "/v2/stocks/bars"
    extra = {} if crypto else {"feed": "sip", "adjustment": "all"}
    rows, token = [], None
    while True:
        d = get_data(p, {"symbols": sym, "timeframe": "5Min", "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "end": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"), "limit": 10000, **extra,
                         **({"page_token": token} if token else {})})
        rows += d.get("bars", {}).get(sym, [])
        token = d.get("next_page_token")
        if not token:
            break
    new = pd.DataFrame(rows)
    if len(new):
        new.index = pd.to_datetime(new["t"], utc=True)
        new = new.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})[data.COLUMNS]
        if not crypto:
            ny = new.index.tz_convert("America/New_York")
            m = ny.hour * 60 + ny.minute
            new = new[(m >= 9 * 60 + 30) & (m < 16 * 60)]
        new.index = new.index.tz_convert(None)
        new = new[new.index + pd.Timedelta(minutes=5) <= cutoff]  # complete bars only
        new.index.name = "Date"
    df = new if old is None or old.empty else pd.concat([old[old.index < new.index[0]], new]) if len(new) else old
    data.DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(path)
    return df


def session(df: pd.DataFrame) -> pd.Index:
    """Trading day of each bar (New York date; crypto: UTC date)."""
    return df.index.normalize()


def last_bar_of_session(df: pd.DataFrame) -> pd.Series:
    """Stocks: the 15:55 bar of each session. Blocking it closes every position at its
    open (15:55 New York): flat before the close, no overnight risk."""
    day = session(df)
    last = pd.Series(np.arange(len(df)), df.index).groupby(day).transform("max")
    return pd.Series(np.arange(len(df)) == last.to_numpy(), df.index)


# ----------------------------------------------------------------- strategies (5-minute)

def orb15(df: pd.DataFrame) -> pd.Series:
    """Opening-range breakout: the 9:30-9:45 range (3 bars); first close beyond it, before 12:00."""
    day = session(df)
    k = df.groupby(day).cumcount()
    first = k < 3
    hi = df["High"].where(first).groupby(day).transform("max")
    lo = df["Low"].where(first).groupby(day).transform("min")
    ok = (k >= 3) & (k < 30)  # until 12:00 New York
    up, dn = ok & (df["Close"] > hi), ok & (df["Close"] < lo)
    n = (up | dn).astype(int).groupby(day).cumsum()
    return _combine(up & (n == 1), dn & (n == 1))


def vwap_fade(df: pd.DataFrame, k: float = 2.0) -> pd.Series:
    """Stretch of k ATRs from the day's VWAP: fade it, back toward VWAP (not in the first 30 min)."""
    day = session(df)
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    vol = df["Volume"].where(df["Volume"] > 0, 1.0)
    vwap = (tp * vol).groupby(day).cumsum() / vol.groupby(day).cumsum()
    z = (df["Close"] - vwap) / atr(df)
    late = df.groupby(day).cumcount() >= 6
    return _combine(late & (z < -k), late & (z > k))


def range_break(df: pd.DataFrame, n: int = 24, vol_k: float = 2.0) -> pd.Series:
    """Close beyond the last 2 hours' range on volume at least vol_k x its 2-hour average."""
    hi = df["High"].rolling(n).max().shift(1)
    lo = df["Low"].rolling(n).min().shift(1)
    loud = df["Volume"] > vol_k * df["Volume"].rolling(n).mean().shift(1)
    return _combine((df["Close"] > hi) & loud, (df["Close"] < lo) & loud)


def rsi2_5m(df: pd.DataFrame) -> pd.Series:
    """RSI(2) extreme in the direction of the 1-hour trend (12-bar average above the 48-bar one)."""
    r = rsi(df["Close"], 2)
    up = sma(df["Close"], 12) > sma(df["Close"], 48)
    return _combine((r < 5) & up, (r > 95) & ~up)


STRATEGIES = {"orb15": orb15, "vwap_fade": vwap_fade, "range_break": range_break, "rsi2_5m": rsi2_5m}
STOCK_ONLY = {"orb15"}


# ----------------------------------------------------------------- study

def sleeves(prices, strats, allow_short=True, random_seed=None):
    rng = np.random.default_rng(random_seed) if random_seed is not None else None
    out = []
    for a, df in prices.items():
        for name in strats:
            if name in STOCK_ONLY and a in data.CRYPTO:
                continue
            s = STRATEGIES[name](df).reindex(df.index).fillna(0)
            if rng is not None:  # same frequency, random timing and side
                fire = rng.random(len(s)) < (s != 0).mean()
                s = pd.Series(np.where(fire, np.where(rng.random(len(s)) < 0.5, 1, -1), 0), s.index)
            out.append(Sleeve(a, name, s, RULES[name], allow_short))
    return out


def run(prices, strats, costs, start, end, risk=0.002, seed=None, flat_at_close=True):
    blocked = {a: last_bar_of_session(df) for a, df in prices.items() if a not in data.CRYPTO} \
        if flat_at_close else None
    cfg = PortfolioConfig(risk_pct=risk, max_gross=2.0, max_open_risk=0.10)
    return run_portfolio(prices, sleeves(prices, strats, random_seed=seed), costs, cfg, start, end, blocked=blocked)


def summary(res, days: float) -> dict:
    t = res.trades_df
    eq = res.equity
    st = equity_stats(eq, len(eq) / max(days / 365.25, 1e-9)) if len(eq) > 2 else {}
    return {"return": eq.iloc[-1] / eq.iloc[0] - 1, "sharpe": st.get("sharpe", np.nan),
            "max_dd": st.get("max_drawdown", np.nan), "trades": len(t), "per_day": len(t) / max(days, 1),
            "win": (t.pnl > 0).mean() if len(t) else np.nan, "avg_r": t.r_multiple.mean() if len(t) else np.nan,
            "fees_pct": t.fees.sum() / 100_000 if len(t) else 0.0,
            "hold_min": (pd.to_datetime(t.exit_date) - pd.to_datetime(t.entry_date)).dt.total_seconds().mean() / 60
            if len(t) else np.nan}


def study(assets_stocks=STOCKS, assets_crypto=CRYPTO, seeds=5) -> str:
    stocks = {a: load_5m(a) for a in assets_stocks}
    crypto = {a: load_5m(a) for a in assets_crypto}
    idx = pd.DatetimeIndex(sorted(set().union(*(df.index for df in stocks.values()))))
    cut = idx[int(len(idx) * SPLIT)]
    windows = {"train": (idx[0], cut), "test": (cut, idx[-1])}
    days = {w: np.busday_count(a.date(), b.date()) for w, (a, b) in windows.items()}
    rows = []
    cases = [("stocks", stocks, {a: STOCK_COST for a in stocks}),
             ("crypto, taker fee", crypto, {a: CRYPTO_TAKER for a in crypto}),
             ("crypto, maker fee", crypto, {a: CRYPTO_MAKER for a in crypto})]
    for label, prices, costs in cases:
        for strat in list(STRATEGIES) + ["all"]:
            strats = list(STRATEGIES) if strat == "all" else [strat]
            if label != "stocks" and strats == ["orb15"]:
                continue
            for w, (a, b) in windows.items():
                d = days[w] if label == "stocks" else (b - a).days
                real = summary(run(prices, strats, costs, a, b), d)
                rnd = pd.DataFrame([summary(run(prices, strats, costs, a, b, seed=s), d)
                                    for s in range(seeds)]).mean(numeric_only=True)
                rows.append({"market": label, "strategy": strat, "window": w} | real
                            | {"random_return": rnd["return"], "random_avg_r": rnd["avg_r"]})
                log.info("%s %s %s: %+.2f%% (random %+.2f%%), %d trades", label, strat, w,
                         100 * real["return"], 100 * rnd["return"], real["trades"])
    out = pd.DataFrame(rows)

    # swing vs day trading on stocks: the same 5-minute strategies, flat at the close or not
    hold = []
    for flat in (True, False):
        for w, (a, b) in windows.items():
            hold.append({"flat_at_close": flat, "window": w}
                        | summary(run(stocks, list(STRATEGIES), {x: STOCK_COST for x in stocks}, a, b,
                                      flat_at_close=flat), days[w]))
    return report(out, pd.DataFrame(hold), windows)


def report(df: pd.DataFrame, hold: pd.DataFrame, windows) -> str:
    def pct(x):
        return "–" if pd.isna(x) else f"{x:+.2%}"

    md = [f"# Fast day trading study (5-minute bars) – {pd.Timestamp.now():%Y-%m-%d}", "",
          f"Train (choose): {windows['train'][0]:%Y-%m-%d} → {windows['train'][1]:%Y-%m-%d}. "
          f"Test (untouched): {windows['test'][0]:%Y-%m-%d} → {windows['test'][1]:%Y-%m-%d}. "
          "Each trade risks 0.2% of equity; stocks flat by 15:55 New York. *Random* = same strategies' "
          "exits and number of signals, random timing and side (average of 5). A strategy is only "
          "interesting if it beats random in **both** windows, after costs.", "",
          "| market | strategy | window | return | random | trades/day | hold (min) | win | avg R | fees | max DD |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        md.append(f"| {r.market} | {r.strategy} | {r.window} | {pct(r['return'])} | {pct(r.random_return)} | "
                  f"{r.per_day:.1f} | {r.hold_min:.0f} | {r.win:.0%} | {r.avg_r:+.2f} | {pct(-r.fees_pct)} | "
                  f"{pct(r.max_dd)} |")
    md += ["", "## Day trading or swing: stocks, all 5-minute strategies", "",
           "| flat at the close | window | return | trades/day | avg R | max DD |", "|---|---|---|---|---|---|"]
    for _, r in hold.iterrows():
        md.append(f"| {'yes' if r.flat_at_close else 'no (hold overnight)'} | {r.window} | {pct(r['return'])} | "
                  f"{r.per_day:.1f} | {r.avg_r:+.2f} | {pct(r.max_dd)} |")
    out = Path(__file__).resolve().parent.parent / "reports" / f"{pd.Timestamp.now():%Y-%m-%d}-fast"
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text("\n".join(md) + "\n")
    df.to_csv(out / "results.csv", index=False)
    hold.to_csv(out / "flat_vs_hold.csv", index=False)
    return str(out / "report.md")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(f"Report: {study()}")


if __name__ == "__main__":
    main()
