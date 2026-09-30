import pandas as pd

from algo.data import regular_session_hours


def test_regular_session_hours_cut_on_the_clock_hour():
    # 2026-09-30 is summer time: the session is 13:30-20:00 UTC
    idx = pd.date_range("2026-09-30 13:00", "2026-09-30 20:30", freq="30min", tz="UTC")
    df = pd.DataFrame({"Open": range(len(idx)), "High": 100.0, "Low": 1.0, "Close": range(len(idx)),
                       "Volume": 1.0}, index=idx)
    h = regular_session_hours(df)
    assert h.index[0] == pd.Timestamp("2026-09-30 13:00") and h.index[-1] == pd.Timestamp("2026-09-30 19:00")
    assert len(h) == 7  # 9:30-10:00 then six full hours to 16:00
    assert h.Volume.iloc[0] == 1.0 and h.Volume.iloc[1] == 2.0  # first bar is the half hour 9:30-10:00
    assert h.Open.iloc[1] == df.Open.loc["2026-09-30 14:00"] and h.Close.iloc[1] == df.Close.loc["2026-09-30 14:30"]
