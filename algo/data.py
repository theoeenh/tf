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

# Daily bars per year, used to annualise returns and volatility.
PERIODS_PER_YEAR = {n: 365 if n in CRYPTO else 252 for n in TICKERS}

# Yahoo only serves hourly bars for the last ~730 days.
INTRADAY_PERIOD = "730d"

COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def load(name: str, source: str = "auto", start: str = "2014-01-01", interval: str = "1d") -> pd.DataFrame:
    """Load OHLCV bars for `name` (a key of TICKERS). interval: "1d" or "1h".

    source: "yahoo" downloads (and refreshes the CSV cache), "csv" reads
    data/<name>[_1h].csv only, "auto" tries Yahoo then falls back to the CSV.
    Intraday timestamps are UTC.
    """
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
