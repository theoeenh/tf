import json
from dataclasses import asdict

import numpy as np
import pandas as pd

from algo import finder as F
from algo import runner as RN


def _df(n=300, start="2025-01-02"):
    idx = pd.bdate_range(start, periods=n)
    c = 100 + np.cumsum(np.random.default_rng(1).normal(0, 1, n))
    return pd.DataFrame({"Open": c, "High": c + 1, "Low": c - 1, "Close": c, "Volume": 1e6}, idx)


def test_todays_bar_waits_for_the_close():
    df = _df(5, "2026-10-01")
    morning = pd.Timestamp("2026-10-07 09:05")
    evening = pd.Timestamp("2026-10-07 16:30")
    assert RN.complete_sessions(df, morning).index[-1] == pd.Timestamp("2026-10-06")
    assert RN.complete_sessions(df, evening).index[-1] == pd.Timestamp("2026-10-07")


def test_last_session_signal_becomes_an_entry_sized_by_risk():
    c = F.Candidate("insider_cluster", {"buyers": 3, "days": 90}, dict(F.DAILY_RULES["hold 20 days"]), data="daily500")
    df = _df()
    sig = {"X": pd.Series(0, df.index), "Y": pd.Series(0, df.index), "Z": pd.Series(0, df.index)}
    sig["X"].iloc[-1] = 1
    sig["Y"].iloc[-1] = 1
    sig["Z"].iloc[-2] = 1  # yesterday's: already in the replay
    out = RN.pending_entries(c, sig, {"X": df, "Y": df, "Z": df}, held={"Y"}, equity=100_000)
    assert [o["asset"] for o in out] == ["X"]
    o = out[0]
    risk = (o["mark"] - o["stop"]) * o["qty"]
    assert abs(risk - F.RISK * 100_000) < 1e-6 or o["qty"] * o["mark"] <= 2.0 * 100_000 / 4 + 1e-6
    assert o["pending"] and o["stop"] < o["mark"]


def test_insider_coverage_needs_the_whole_window():
    import pandas as pd
    from algo.runner import insider_coverage

    today = pd.Timestamp("2026-10-06")
    days = {d.strftime("%Y%m%d") for d in pd.bdate_range("2026-06-20", "2026-10-05")}
    assert insider_coverage(days, pd.Timestamp("2026-03-31"), today)[0]
    gap = {d for d in days if not "20260801" <= d <= "20260815"}
    ok, why = insider_coverage(gap, pd.Timestamp("2026-03-31"), today)
    assert not ok and "2026-07-31" in why
    stale = {d for d in days if d < "20260925"}
    assert not insider_coverage(stale, pd.Timestamp("2026-03-31"), today)[0]
