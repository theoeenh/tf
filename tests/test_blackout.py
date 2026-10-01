import pandas as pd

from algo.news import blackout
from algo.strategies import daily_trend, with_trend


def stock_hours(days):
    # summer time: regular-session bars start 13:00 (9:30-10:00) ... 19:00 UTC
    return pd.DatetimeIndex([pd.Timestamp(f"{d} {h}:00") for d in days for h in range(13, 20)])


def test_earnings_blocks_report_day_and_last_bar_before():
    idx = stock_hours(["2026-08-26", "2026-08-27", "2026-08-28"])
    b = blackout(idx, earnings=[pd.Timestamp("2026-08-27")], fomc=[], jobs=[], stock=True)
    assert b[pd.Timestamp("2026-08-26 19:00")] and not b[pd.Timestamp("2026-08-26 18:00")]
    assert b[b.index.normalize() == pd.Timestamp("2026-08-27")].all()
    assert not b[b.index.normalize() == pd.Timestamp("2026-08-28")].any()


def test_fed_blocks_the_afternoon_for_all_assets():
    idx = pd.date_range("2026-09-16 00:00", "2026-09-16 23:00", freq="h")  # crypto, 24 h
    b = blackout(idx, earnings=[], fomc=[pd.Timestamp("2026-09-16")], jobs=[], stock=False)
    # 13:00-16:00 New York = 17:00-20:00 UTC in September
    assert list(b[b].index.hour) == [17, 18, 19]


def test_jobs_report_and_far_future_events():
    idx = stock_hours(["2026-10-01", "2026-10-02"])  # Thu, Fri (jobs)
    b = blackout(idx, earnings=[pd.Timestamp("2027-01-28")], fomc=[], jobs=[pd.Timestamp("2026-10-02")], stock=True)
    assert b[pd.Timestamp("2026-10-01 19:00")]  # last bar before the report
    assert b.sum() == 1  # a far-away earnings date does not block the last bar of the data


def test_daily_trend_uses_only_finished_days():
    idx = pd.date_range("2026-01-01", periods=24 * 60, freq="h")
    close = pd.Series(range(len(idx)), idx, dtype=float)  # rising all the time
    df = pd.DataFrame({"Open": close, "High": close, "Low": close, "Close": close})
    tr = daily_trend(df, n=5)
    assert (tr.iloc[: 24 * 5] == 0).all()  # unknown until 5 finished days
    assert tr.iloc[-1] == 1
    sig = pd.Series(0, idx); sig.iloc[-1] = -1; sig.iloc[-2] = 1
    kept = with_trend(sig, tr)
    assert kept.iloc[-1] == 0 and kept.iloc[-2] == 1


def test_session_in_progress_is_not_blocked_before_its_last_bar():
    """The day before the jobs report: only the 15:00 New York bar is blocked, also while the
    day is still in progress (the newest bar available is not the session's last bar)."""
    import pandas as pd
    from algo.news import blackout

    # Thu 1 Oct 2026, jobs report Fri 2 Oct; New York is UTC-4: 13:00 UTC = 9:00 NY bar
    full = pd.DatetimeIndex([f"2026-09-30 {h}:00" for h in range(13, 20)]
                            + [f"2026-10-01 {h}:00" for h in range(13, 20)])
    jobs = ["2026-10-02"]
    so_far = full[full <= "2026-10-01 14:00"]  # live, at 11:20 New York
    b = blackout(so_far, [], [], jobs, stock=True)
    assert not b.any()
    b = blackout(full, [], [], jobs, stock=True)
    assert list(b[b].index) == [pd.Timestamp("2026-10-01 19:00")]  # 15:00 New York


def test_next_bar_blocked_before_the_jobs_report():
    import pandas as pd
    from algo.news import next_bar_blocked

    jobs = ["2026-10-02"]
    upto = lambda h: pd.DatetimeIndex([f"2026-10-01 {x}:00" for x in range(13, h + 1)])
    assert not next_bar_blocked(upto(17), [], [], jobs, stock=True)  # next: 14:00 New York
    assert next_bar_blocked(upto(18), [], [], jobs, stock=True)      # next: 15:00 New York, the last bar
    assert not next_bar_blocked(upto(19), [], [], jobs, stock=True)  # next session: other rule
    # crypto: flat through 8:00-9:00 New York on report day
    crypto = pd.DatetimeIndex([f"2026-10-02 {x:02d}:00" for x in range(0, 12)])  # next: 12:00 UTC = 8:00 New York
    assert next_bar_blocked(crypto, [], [], jobs, stock=False)
    assert not next_bar_blocked(crypto[:-1], [], [], jobs, stock=False)
