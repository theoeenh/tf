"""Price data: download from Yahoo Finance, cache as CSV, validate."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Name used in the project -> Yahoo ticker.
# GLD (SPDR Gold Shares) is used for gold rather than GC=F: continuous futures
# on Yahoo have roll jumps that create fake breakouts.
TICKERS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "NVDA": "NVDA",
    "TSLA": "TSLA",
    "GOLD": "GLD",
    "SILVER": "SLV",
    "SPY": "SPY",
}
CRYPTO = {"BTC", "ETH", "SOL"}

# Name used in the project -> Alpaca symbol (the broker's own price data).
ALPACA_SYMBOLS = {"BTC": "BTC/USD", "ETH": "ETH/USD", "SOL": "SOL/USD", "NVDA": "NVDA", "TSLA": "TSLA",
                  "GOLD": "GLD", "SILVER": "SLV", "SPY": "SPY"}
ALPACA_START = "2023-01-01"  # fixed, so replays from it are repeatable
SIP_DELAY_MIN = 16  # Alpaca's free plan: full-market stock data from 15 minutes ago only

# Daily bars per year, used to annualise returns and volatility.
PERIODS_PER_YEAR = {n: 365 if n in CRYPTO else 252 for n in TICKERS}

# Yahoo only serves hourly bars for the last ~730 days.
INTRADAY_PERIOD = "730d"

COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def load(name: str, source: str = "auto", start: str = "2014-01-01", interval: str = "1d") -> pd.DataFrame:
    """Load OHLCV bars for `name` (a key of TICKERS). interval: "1d" or "1h".

    source: "yahoo" downloads (and refreshes the CSV cache), "csv" reads
    data/<name>[_1h].csv only, "auto" tries Yahoo then falls back to the CSV,
    "alpaca" uses Alpaca's market data (see load_alpaca).
    Intraday timestamps are UTC.
    """
    if source == "alpaca":
        return load_alpaca(name, interval)
    intraday = interval != "1d"
    path = DATA_DIR / (f"{name}_{interval}.csv" if intraday else f"{name}.csv")
    if source in ("auto", "yahoo"):
        try:
            df = _download(TICKERS[name], start, interval)
            DATA_DIR.mkdir(exist_ok=True)
            df = validate(df, name, intraday)
            df.to_csv(path)
            return df
        except Exception as exc:  # network errors, empty responses
            if source == "yahoo":
                raise
            log.warning("Yahoo download failed for %s (%s); using %s", name, exc, path)
    if not path.exists():
        raise FileNotFoundError(
            f"No data for {name}: Yahoo unreachable and {path} missing. "
            f"Place a CSV with columns Date,{','.join(COLUMNS)} there."
        )
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return validate(df, name, intraday)


def load_alpaca(name: str, interval: str = "1h", start: str = ALPACA_START, refresh: bool = False) -> pd.DataFrame:
    """Bars from Alpaca's market data (the broker we trade on), cached in
    data/<name>_<interval>_alpaca.csv; only the missing recent bars are fetched.

    Hourly stock bars are regular-session only (9:30-16:00 New York), cut on the
    clock hour: 9:30-10:00, 10:00-11:00, ... 15:00-16:00, so every asset's bars
    end on the hour. Crypto trades around the clock (UTC hours). Prices are
    split- and dividend-adjusted. Timestamps are the bar's start, in UTC.
    """
    path = DATA_DIR / f"{name}_{interval}_alpaca.csv"
    old = None if refresh or not path.exists() else pd.read_csv(path, index_col=0, parse_dates=True)
    fetch_from = pd.Timestamp(start) if old is None or old.empty else old.index[-1] - pd.Timedelta(days=3)
    new = _alpaca_bars(name, interval, fetch_from)
    if old is not None and not old.empty:
        both = old.index.intersection(new.index)
        # a split or dividend re-adjusts past prices: download everything again
        if len(both) and (new.loc[both, "Close"] / old.loc[both, "Close"] - 1).abs().max() > 1e-3:
            return load_alpaca(name, interval, start, refresh=True)
        new = pd.concat([old[old.index < new.index[0]], new]) if len(new) else old
    df = validate(new, name, intraday=interval != "1d")
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(path)
    return df


def _alpaca_bars(name: str, interval: str, start: pd.Timestamp) -> pd.DataFrame:
    from .alpaca import get_data

    sym = ALPACA_SYMBOLS[name]
    crypto = name in CRYPTO
    if crypto:
        path, tf = "/v1beta3/crypto/us/bars", {"1h": "1Hour", "1d": "1Day"}[interval]
        params = {}
    else:
        path, tf = "/v2/stocks/bars", {"1h": "30Min", "1d": "1Day"}[interval]
        params = {"feed": "sip", "adjustment": "all"}
    # The free plan serves full-market (SIP) stock data from 15 minutes ago only.
    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    cutoff = now if crypto else now - pd.Timedelta(minutes=SIP_DELAY_MIN)
    rows, token = [], None
    while True:
        q = {"symbols": sym, "timeframe": tf, "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
             "end": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"), "limit": 10000,
             **params, **({"page_token": token} if token else {})}
        d = get_data(path, q)
        rows += d.get("bars", {}).get(sym, [])
        token = d.get("next_page_token")
        if not token:
            break
    if not rows:
        return pd.DataFrame(columns=COLUMNS, index=pd.DatetimeIndex([], name="Date"))
    df = pd.DataFrame(rows)
    df.index = pd.to_datetime(df["t"], utc=True)
    df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})[COLUMNS]
    if interval == "1d":
        df.index = df.index.tz_convert("America/New_York").tz_localize(None).normalize()
    else:
        # keep only bars that had fully ended at the cutoff: a bar still forming
        # (or cut by the data delay) must never be traded or cached
        if not crypto:
            df = df[df.index.tz_convert(None) + pd.Timedelta(minutes=30) <= cutoff]
            df = regular_session_hours(df)
        else:
            df.index = df.index.tz_convert(None)
        df = df[df.index + pd.Timedelta(hours=1) <= cutoff]
    df.index.name = "Date"
    return df


def regular_session_hours(df30: pd.DataFrame) -> pd.DataFrame:
    """30-minute bars (UTC index) -> regular-session bars cut on the clock hour."""
    ny = df30.index.tz_convert("America/New_York")
    mins = ny.hour * 60 + ny.minute
    df30 = df30[(mins >= 9 * 60 + 30) & (mins < 16 * 60)]
    hour = df30.index.floor("h")
    out = df30.groupby(hour).agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"})
    out.index = out.index.tz_convert(None)
    return out


def _download(ticker: str, start: str, interval: str = "1d") -> pd.DataFrame:
    import yfinance as yf

    if interval == "1d":
        df = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    else:
        df = yf.download(ticker, period=INTRADAY_PERIOD, interval=interval, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"empty download for {ticker}")
    if isinstance(df.columns, pd.MultiIndex):  # newer yfinance returns (field, ticker)
        df.columns = df.columns.get_level_values(0)
    return df[COLUMNS]


def validate(df: pd.DataFrame, name: str = "", intraday: bool = False) -> pd.DataFrame:
    """Sort, de-duplicate, drop bad rows and fix inconsistent OHLC."""
    df = df.copy()
    idx = pd.to_datetime(df.index, utc=intraday)
    idx = idx.tz_convert(None) if idx.tz is not None else idx
    df.index = idx if intraday else idx.normalize()
    df.index.name = "Date"
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df[[c for c in COLUMNS if c in df.columns]]
    if "Volume" not in df.columns:
        df["Volume"] = 0.0

    bad = df[["Open", "High", "Low", "Close"]].isna().any(axis=1) | (df[["Open", "High", "Low", "Close"]] <= 0).any(axis=1)
    if bad.any():
        log.warning("%s: dropping %d rows with missing/non-positive prices", name, bad.sum())
        df = df[~bad]

    # High must be the bar's maximum and Low its minimum.
    df["High"] = df[["Open", "High", "Low", "Close"]].max(axis=1)
    df["Low"] = df[["Open", "High", "Low", "Close"]].min(axis=1)

    gaps = df.index.to_series().diff().dt.days
    if not intraday and (gaps > 5).any():
        log.warning("%s: %d gaps longer than 5 days in the data", name, (gaps > 5).sum())
    return df
