import numpy as np
import pandas as pd

from algo import journal, news


def fake_gdelt(days=400, spike_day=300):
    idx = pd.date_range("2020-01-01", periods=days, freq="D")
    rng = np.random.default_rng(0)
    g = pd.DataFrame({"articles": 100 + rng.normal(0, 5, days), "tone": rng.normal(0, 0.1, days)}, index=idx)
    g.iloc[spike_day, :] = [2000.0, 5.0]  # huge, very positive news day
    return g


def test_news_of_day_d_is_only_used_from_day_d_plus_1():
    g = fake_gdelt()
    idx = pd.date_range("2020-01-01", periods=400, freq="D")
    f = news.news_features(g, idx)
    spike = g.index[300]
    assert f.loc[spike, "attention_z"] < 1.5  # not visible on the day itself
    assert f.loc[spike + pd.Timedelta(days=1), "attention_z"] > 3
    assert f.loc[spike + pd.Timedelta(days=1), "tone_z"] > 1


def test_future_news_does_not_change_past_features():
    g = fake_gdelt()
    idx = pd.date_range("2020-01-01", periods=400, freq="D")
    base = news.news_features(g, idx)
    g2 = g.copy()
    g2.iloc[350:, :] *= 10
    after = news.news_features(g2, idx)
    pd.testing.assert_frame_equal(base.iloc[:351], after.iloc[:351])


def test_intraday_bars_get_the_previous_days_news():
    g = fake_gdelt()
    hours = pd.date_range("2020-10-26", periods=72, freq="h")  # spike day 300 = 2020-10-27
    f = news.news_features(g, hours)
    assert (f.loc["2020-10-27", "attention_z"] < 1.5).all()
    assert (f.loc["2020-10-28", "attention_z"] > 3).all()


def test_days_to_next_event():
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    f = news.event_features(idx, [pd.Timestamp("2024-01-05")], [pd.Timestamp("2024-01-03")], [])
    assert list(f.days_to_earnings[:6]) == [4, 3, 2, 1, 0, np.inf]
    assert f.days_to_fomc.iloc[2] == 0 and np.isinf(f.days_to_jobs).all()


def test_jobs_report_is_first_friday():
    d = news.jobs_report_dates("2024-01-01", "2024-03-31")
    assert [x.strftime("%Y-%m-%d") for x in d] == ["2024-01-05", "2024-02-02", "2024-03-01"]


def test_context_buckets():
    feats = {"adx": 30, "sma200": 90.0, "atr_pct": 0.02, "vol_rank": 0.5, "tone_z": -1.4,
             "attention_z": 2.0, "days_to_earnings": 2, "ai_bias": -1}
    ctx = journal.context(1, 100.0, feats)
    assert ctx["news"] == "negative" and ctx["buzz"] == "spike" and ctx["event"] == "earnings"
    assert ctx["ai"] == "disagree"


def test_learner_views_block_independently():
    learner = journal.Learner(min_trades=3, views=journal.Learner.ALL_VIEWS)
    base = {"adx": 25, "sma200": 90.0, "atr_pct": 0.02, "vol_rank": 0.5}
    bad_news = journal.context(1, 100.0, base | {"tone_z": -2.0, "attention_z": 0.0})
    for _ in range(3):
        learner.record(learner.keys("s", 1, bad_news), -1.0)
    # same setup, neutral news: allowed (the setup view has 3 losses too, so use a new regime)
    ok = journal.context(1, 100.0, base | {"adx": 35, "tone_z": 0.0, "attention_z": 0.0})
    assert not learner.judge(learner.keys("s", 1, ok)).skip
    other_setup_bad_news = journal.context(1, 100.0, base | {"adx": 35, "tone_z": -2.0, "attention_z": 0.0})
    v = learner.judge(learner.keys("s", 1, other_setup_bad_news))
    assert v.skip and "negative news" in v.reason


def test_news_system_runs_end_to_end_on_synthetic_data():
    from algo import system
    from algo.research import synthetic_prices

    prices = {a: synthetic_prices("BTC" if a in ("BTC", "ETH", "SOL") else "GOLD", seed=i)
              for i, a in enumerate(system.UNIVERSE)}
    g = fake_gdelt(days=5000, spike_day=4000)
    g.index = pd.date_range("2014-01-01", periods=5000, freq="D")
    news_data = {"gdelt": {a: g for a in system.UNIVERSE}, "fomc": [pd.Timestamp("2020-03-18")],
                 "jobs": news.jobs_report_dates("2014-01-01", "2026-12-31"),
                 "earnings": {"NVDA": [pd.Timestamp("2020-05-21")]}}
    ai = pd.DataFrame({"BTC": [1.0]}, index=[pd.Timestamp("2020-06-01")])
    ctx = system.build_context(prices, news_data, ai)
    assert ctx["BTC"].loc["2020-06-02", "ai_bias"] == 1.0  # used from the next day
    assert pd.isna(ctx["BTC"].loc["2020-06-01", "ai_bias"])
    res = system.run_system(prices, True, True, 0.005, "2016-01-01", news=True, context=ctx)
    assert res.trades
    views = {k[0] for k in res.learner.history}
    assert {"setup", "news", "event"} <= views
    assert all(t.rationale for t in res.trades)
