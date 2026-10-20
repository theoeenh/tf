import json

import numpy as np
import pandas as pd


def _sessions(days, open_="09:30", close="16:00"):
    from algo import paper

    def utc(d, hm):
        return pd.Timestamp(f"{d} {hm}").tz_localize("America/New_York").tz_convert("UTC").tz_localize(None)

    return [(utc(d, open_), utc(d, close if d != "2026-11-27" else "13:00")) for d in days]


def test_next_stock_bar_inside_the_session_then_the_next_session():
    from algo.paper import next_stock_bar

    s = _sessions(["2026-10-20", "2026-10-21"])
    T = pd.Timestamp
    assert next_stock_bar(T("2026-10-20 14:00"), s) == T("2026-10-20 15:00")
    assert next_stock_bar(T("2026-10-20 13:00"), s) == T("2026-10-20 14:00")       # after 9:30-10:00
    assert next_stock_bar(T("2026-10-20 19:00"), s) == T("2026-10-21 13:00")       # after the close
    # Friday -> Monday; a holiday is simply not in the calendar
    s = _sessions(["2026-10-23", "2026-10-27"])
    assert next_stock_bar(T("2026-10-23 19:00"), s) == T("2026-10-27 13:00")
    # half day (close 13:00 New York): its last bar is 12:00-13:00
    s = _sessions(["2026-11-27", "2026-11-30"])
    assert next_stock_bar(T("2026-11-27 17:00"), s) == T("2026-11-30 14:00")      # winter time: 9:30 = 14:30 UTC


def test_next_bars_only_when_the_data_is_current(monkeypatch):
    from algo import paper

    T = pd.Timestamp
    monkeypatch.setattr(paper, "stock_sessions", lambda day, days=10: _sessions(["2026-10-20", "2026-10-21"]))
    bars = lambda last: pd.DataFrame({"Close": [1.0]}, index=pd.DatetimeIndex([T(last)]))  # noqa: E731
    prices = {"BTC": bars("2026-10-20 12:00"), "AAPL": bars("2026-10-20 14:00")}
    assert paper.next_bars(prices, "1h", T("2026-10-20 15:20")) == {"AAPL": T("2026-10-20 15:00")}  # BTC behind
    assert paper.next_bars(prices, "1h", T("2026-10-20 16:20")) == {}             # AAPL's 15:00 bar is over
    prices = {"BTC": bars("2026-10-20 19:00"), "AAPL": bars("2026-10-20 19:00")}
    assert paper.next_bars(prices, "1h", T("2026-10-20 20:20")) == {"BTC": T("2026-10-20 20:00"),
                                                                   "AAPL": T("2026-10-21 13:00")}
    assert paper.next_bars(prices, "1d", T("2026-10-20 20:20")) == {}


def test_update_sends_the_entry_of_the_last_closed_bar_at_once(monkeypatch, tmp_path):
    """2026-10-20: the paper booked an entry only once the bar after the signal had closed, so the order
    went out an hour late. Now it is in orders.json at the first run after the signal bar, and the books
    (equity, trades) still hold the closed bars only."""
    from algo import paper

    idx = pd.date_range("2026-09-01", periods=600, freq="h")
    close = pd.Series(100.0, index=idx)
    close.iloc[-1] = 120.0                                    # a breakout on the last closed bar
    df = pd.DataFrame({"Open": close.shift(1).fillna(100.0), "High": close + 0.5, "Low": close - 0.5,
                       "Close": close, "Volume": 1000.0})
    (tmp_path / "config.json").write_text(json.dumps({
        "start": str(idx[300]), "capital": 100000.0, "variant": "long only", "interval": "1h",
        "source": "alpaca", "risk_pct": 0.004, "target_vol": 0.2, "universe": ["BTC"], "history_start": None}))
    monkeypatch.setattr(paper, "PAPER_DIR", tmp_path)
    monkeypatch.setattr(paper, "load_prices", lambda *a, **k: {"BTC": df})
    now = idx[-1] + pd.Timedelta(hours=1, minutes=20)
    monkeypatch.setattr(paper, "now_utc", lambda: now)
    paper.update()
    orders = json.loads((tmp_path / "orders.json").read_text())
    assert orders and all(o["bar"] == str(idx[-1]) for o in orders)
    assert all(abs(o["entry"] / 120.0 - 1) < 0.01 for o in orders)          # at the last close
    status = (tmp_path / "status.md").read_text()
    assert "## Opening now" in status
    eq = pd.read_csv(tmp_path / "equity.csv", index_col=0, parse_dates=True)
    assert eq.index[-1] == idx[-1]                             # no row for the bar forming now
    # an hour later the bar is closed: the same trade, now in the books at that bar's real open
    monkeypatch.setattr(paper, "now_utc", lambda: now + pd.Timedelta(days=3))  # data behind: no new bar
    paper.update()
    assert json.loads((tmp_path / "orders.json").read_text()) == []
    assert np.isfinite(pd.read_csv(tmp_path / "equity.csv").iloc[-1, 1])
