"""The luck check: the bar is what the best of all the tries reaches by chance, with the tries kept as
alike as they really are; a strategy is judged on the part of its returns its universe does not explain."""
import numpy as np
import pandas as pd
import pytest

from algo import luck


def test_hedging_takes_out_what_the_universe_earned_and_keeps_the_skill():
    rng = np.random.default_rng(1)
    days = pd.bdate_range("2017-01-02", periods=1500)
    market = pd.Series(rng.normal(0.0012, 0.01, len(days)), days)            # a rising market
    rider = (1 + 0.5 * market).cumprod()                                  # half invested, no skill
    skilled = (1 + 0.5 * market + rng.normal(0.0004, 0.002, len(days))).cumprod()
    w, beta = luck.hedged(rider, market)
    assert beta == pytest.approx(0.5, abs=0.01)
    assert abs(w).max() < 1e-12                                           # nothing left without the market
    assert luck.stats(w.to_numpy()[:, None])["t"][0] == 0.0               # and rounding is not a Sharpe
    raw_t = rider.pct_change().dropna().mean() / rider.pct_change().dropna().std() * np.sqrt(1499)
    assert raw_t > 1.5                                                    # yet its raw Sharpe looked like skill
    w, _ = luck.hedged(skilled, market)
    assert luck.stats(w.to_numpy()[:, None])["t"][0] > 4
    assert w.index.freqstr == luck.WEEK and len(w) in (300, 301)


def test_the_bar_counts_ideas_not_copies():
    rng = np.random.default_rng(2)
    ideas = rng.normal(0, 0.01, (300, 20))
    one = luck.null_max([ideas], replays=300).mean()
    copies = np.repeat(ideas, 50, axis=1) + rng.normal(0, 0.0005, (300, 1000))   # 1,000 tries, 20 ideas
    many = luck.null_max([copies], replays=300).mean()
    fresh = luck.null_max([rng.normal(0, 0.01, (300, 1000))], replays=300).mean()
    assert many == pytest.approx(one, abs=0.15)                           # near-copies barely raise the bar
    assert fresh > one + 1.0                                              # 1,000 different ideas do
    assert 15 < luck.effective_n(one) < 40 and luck.effective_n(fresh) > 400
    assert luck.effective_n(many) < 60


def test_every_try_counts_a_new_idea_can_only_raise_the_bar():
    rng = np.random.default_rng(3)
    x = rng.normal(0, 0.01, (300, 60))
    bars = [luck.null_max([x[:, :k]], replays=300).mean() for k in (5, 20, 60)]
    assert bars[0] < bars[1] < bars[2]
    two_sets = luck.null_max([x[:, :30], rng.normal(0, 0.02, (100, 30))], replays=300).mean()
    assert two_sets > luck.null_max([x[:, :30]], replays=300).mean()      # tries on another data set count too


def test_independent_tries_give_the_bar_of_the_old_formula():
    rng = np.random.default_rng(4)
    for n in (10, 200):
        bar = luck.null_max([rng.normal(0, 0.01, (400, n))], replays=400).mean()
        assert bar == pytest.approx(luck.expected_max(n), abs=0.2)
        assert luck.effective_n(luck.expected_max(n)) == pytest.approx(n, rel=0.02)


def test_real_skill_passes_and_the_luckiest_of_many_does_not():
    rng = np.random.default_rng(5)
    x = rng.normal(0, 0.01, (313, 400))
    x[:, 0] += 0.0032                                                     # one try with a real edge
    st = luck.stats(x)
    bar = luck.null_max([x], replays=400).mean()
    score = [luck.deflated(st["sr"][i], st["n"], st["skew"][i], st["kurt"][i], bar) for i in range(400)]
    assert st["t"][0] > 4.5 and score[0] >= 0.90
    assert max(score[1:]) < 0.90                                          # the best of 399 lucky tries fails
    assert luck.deflated(st["sr"][0], st["n"], st["skew"][0], st["kurt"][0], bar + 1.0) < score[0]


def test_a_try_that_never_traded_cannot_set_the_bar_and_the_result_is_reproducible():
    rng = np.random.default_rng(6)
    x = rng.normal(0, 0.01, (200, 30))
    with_flat = np.hstack([x, np.zeros((200, 5))])
    a, b = luck.null_max([x], replays=200), luck.null_max([with_flat], replays=200)
    assert np.allclose(a, b)
    assert np.allclose(a, luck.null_max([x], replays=200))                # same tries, same bar, every night


def test_weekly_returns_survive_the_disk_and_a_later_file_wins(tmp_path):
    weeks = pd.date_range("2017-01-06", periods=5, freq=luck.WEEK)
    a = pd.Series([0.01, -0.02, 0.0, 0.03, 0.01], weeks)
    luck.save(tmp_path, "daily500", "run1", {"aaa": a, "bbb": a * 2})
    luck.save(tmp_path, "daily500", "run2", {"bbb": a * 3, "ccc": a.iloc[:3]})
    luck.save(tmp_path, "hourly", "run1", {"zzz": a})
    got = luck.load(tmp_path, "daily500")
    assert list(got.columns) == ["aaa", "bbb", "ccc"] and len(got) == 5
    assert np.allclose(got["bbb"], a * 3, rtol=1e-3) and got["ccc"].iloc[-1] == 0.0   # stored to 3 digits
    assert luck.load(tmp_path, "none").empty and luck.save(tmp_path, "daily500", "x", {}) is None
