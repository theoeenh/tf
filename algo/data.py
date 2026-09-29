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
    "GOLD": "GLD",
    "SPY": "SPY",
}

# Bars per year, used to annualise returns and volatility.
PERIODS_PER_YEAR = {"BTC": 365, "GOLD": 252, "SPY": 252}

COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def load(name: str, source: str = "auto", start: str = "2014-01-01") -> pd.DataFrame:
    """Load daily OHLCV for `name` ("BTC", "GOLD", "SPY").

    source: "yahoo" downloads (and refreshes the CSV cache), "csv" reads
    data/<name>.csv only, "auto" tries Yahoo then falls back to the CSV.
    """
    path = DATA_DIR / f"{name}.csv"
    if source in ("auto", "yahoo"):
        try:
            df = _download(TICKERS[name], start)
            DATA_DIR.mkdir(exist_ok=True)
            df.to_csv(path)
            return validate(df, name)
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
    return validate(df, name)


def _download(ticker: str, start: str) -> pd.DataFrame:
    import yfinance as yf

    df = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"empty download for {ticker}")
    if isinstance(df.columns, pd.MultiIndex):  # newer yfinance returns (field, ticker)
        df.columns = df.columns.get_level_values(0)
    return df[COLUMNS]


def validate(df: pd.DataFrame, name: str = "") -> pd.DataFrame:
    """Sort, de-duplicate, drop bad rows and fix inconsistent OHLC."""
    df = df.copy()
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
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
    if (gaps > 5).any():
        log.warning("%s: %d gaps longer than 5 days in the data", name, (gaps > 5).sum())
    return df
