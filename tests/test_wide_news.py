"""News per stock and day for the S&P 1500 research (algo/wide_news.py) and the news families."""
import numpy as np
import pandas as pd
import pytest

from algo import finder_families as FF
from algo import wide_news as N


def art(i, created, symbols, headline):
    return {"id": i, "created_at": created, "symbols": symbols, "headline": headline, "summary": ""}


def test_an_article_counts_for_the_first_close_that_knows_it():
    """Signals are decided at the 16:00 New York close: an article published after it is the next
    day's news (a Friday evening article: Saturday's, which becomes Monday's once mapped to sessions)."""
    assert N.day_of("2026-11-12T20:59:00Z") == pd.Timestamp("2026-11-12")   # 15:59 New York
    assert N.day_of("2026-11-12T21:00:00Z") == pd.Timestamp("2026-11-13")   # 16:00: after the close
    assert N.day_of("2026-07-10T19:59:00Z") == pd.Timestamp("2026-07-10")   # summer time: 15:59
    assert N.day_of("2026-07-10T20:00:00Z") == pd.Timestamp("2026-07-11")


def test_tally_counts_company_news_and_keeps_round_ups_apart():
    rows = N.tally([
        art(1, "2026-11-12T15:00:00Z", ["NVDA"], "Nvidia shares plunge after chief executive leaves"),
        art(2, "2026-11-12T16:00:00Z", ["NVDA", "AMD"], "Nvidia wins record order"),
        art(3, "2026-11-12T17:00:00Z", ["NVDA", "AMD", "INTC", "AVGO", "MU"], "Chip stocks fall"),   # a round-up
        art(4, "2026-11-12T18:00:00Z", ["BRK.B"], "Berkshire annual letter"),
        art(5, "2026-11-12T18:30:00Z", ["XYZ"], "Not a stock we follow surges"),
        art(2, "2026-11-12T16:00:00Z", ["NVDA", "AMD"], "Nvidia wins record order"),                 # the same article again
    ], keep={"NVDA", "AMD", "BRK-B", "INTC"}).set_index("symbol")
    assert rows.loc["NVDA", ["n", "pos", "neg", "wide"]].tolist() == [2, 1, 1, 1]
    assert rows.loc["NVDA", "score"] == 0.0                     # one clearly bad headline, one clearly good
    assert rows.loc["AMD", ["n", "pos", "neg", "wide"]].tolist() == [1, 1, 0, 1]
    assert rows.loc["BRK-B", "n"] == 1 and rows.loc["BRK-B", "pos"] == 0   # Alpaca's BRK.B is our BRK-B
    assert rows.loc["INTC", ["n", "wide"]].tolist() == [0, 1]   # only in the round-up
    assert "XYZ" not in rows.index and (rows["day"] == pd.Timestamp("2026-11-12")).all()


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "NEWS_DIR", tmp_path)
    N._cache.clear()

    def put(month, rows, done=True):
        pd.DataFrame(rows, columns=["day", "symbol", "n", "pos", "neg", "score", "wide"]).to_csv(
            tmp_path / f"{month}.csv.gz", index=False)
        if done:
            with (tmp_path / "done.txt").open("a") as f:
                f.write(month + "\n")

    yield put
    N._cache.clear()


def test_news_is_not_used_before_every_month_is_there(store, monkeypatch):
    """A missing month would read as 'no news': the families must not run on a partial download."""
    monkeypatch.setattr(N, "FIRST", "2020-01-01")
    store("2020-01", [("2020-01-10", "AAA", 1, 0, 0, 0.0, 0)])
    store("2020-03", [("2020-03-10", "AAA", 1, 0, 0, 0.0, 0)])
    with pytest.raises(FileNotFoundError, match="2020-02"):
        N.load()
    store("2020-02", [("2020-02-10", "AAA", 2, 1, 0, 1.0, 0), ("2020-03-01", "AAA", 1, 0, 1, -1.0, 0)])
    N._cache.clear()
    t, first, last = N.load()
    assert first == pd.Timestamp("2020-01-01") and last == pd.Timestamp("2020-03-31")
    assert len(t) == 4 and t["n"].sum() == 5


def test_weekend_news_lands_on_the_next_session_and_a_month_s_spill_is_added(store, monkeypatch):
    monkeypatch.setattr(N, "FIRST", "2020-01-01")
    store("2020-01", [("2020-01-10", "AAA", 1, 0, 1, -1.0, 0), ("2020-01-11", "AAA", 2, 2, 0, 2.0, 1),   # a Saturday
                      ("2020-02-01", "AAA", 1, 1, 0, 1.0, 0)])       # published on 31 Jan after the close
    store("2020-02", [("2020-02-01", "AAA", 1, 0, 0, 0.0, 0), ("2020-02-28", "ZZZ", 1, 0, 0, 0.0, 0)])
    idx = pd.bdate_range("2020-01-06", "2020-02-14")
    px = {"AAA": pd.DataFrame({"Close": 1.0}, idx), "BBB": pd.DataFrame({"Close": 1.0}, idx)}
    by, first, last = N.by_stock(px)
    a = by["AAA"]
    assert list(a.index) == list(idx) and a.loc["2020-01-10", "neg"] == 1
    assert a.loc["2020-01-13", ["n", "pos", "wide"]].tolist() == [2, 2, 1]          # Saturday's news: Monday
    assert a.loc["2020-02-03", "n"] == 2                                            # Saturday 1 Feb, both files
    assert a["n"].sum() == 5 and by["BBB"]["n"].sum() == 0 and last == pd.Timestamp("2020-02-29")


def _world(store, monkeypatch, news_rows, moves):
    """Flat stocks at 100 with a 1% daily wiggle; `moves`: {stock: {session number: return}}."""
    monkeypatch.setattr(N, "FIRST", "2020-01-01")
    idx = pd.bdate_range("2020-01-01", "2021-06-30")
    for m in pd.period_range("2020-01", "2021-06", freq="M"):
        store(str(m), [r for r in news_rows if str(r[0])[:7] == str(m)])
    from algo import wide

    monkeypatch.setattr(wide, "load_earnings", lambda: pd.DataFrame({"ticker": ["EARN"], "day": [idx[300]]}))
    prices = {}
    for a in ("QUIET", "LOUD", "BAD", "GOOD", "NEVER", "EARN"):
        r = np.where(np.arange(len(idx)) % 2 == 0, 0.01, -0.01).astype(float)
        for k, v in moves.get(a, {}).items():
            r[k] = v
        c = 100 * np.cumprod(1 + r)
        prices[a] = pd.DataFrame({"Open": c, "High": c * 1.01, "Low": c * 0.99, "Close": c, "Volume": 1e6}, idx)
    return prices, idx


def test_news_families_buy_what_they_say(store, monkeypatch):
    idx = pd.bdate_range("2020-01-01", "2021-06-30")
    day = lambda k: f"{idx[k]:%Y-%m-%d}"
    rows = [(day(100), s, 1, 0, 0, 0.0, 0) for s in ("QUIET", "LOUD", "BAD", "GOOD", "EARN")]  # all are covered
    rows += [(day(299), "LOUD", 1, 0, 0, 0.0, 0),                       # an article two sessions before its drop
             (day(300), "BAD", 3, 0, 2, -2.0, 0), (day(300), "GOOD", 3, 2, 0, 2.0, 0),
             (day(300), "EARN", 3, 0, 2, -2.0, 0)]
    drop = {300: -0.08}
    prices, _ = _world(store, monkeypatch, rows, {"QUIET": drop, "LOUD": drop, "BAD": drop, "NEVER": drop,
                                                  "EARN": drop, "GOOD": {300: 0.08}})
    hits = lambda sig: {a: [f"{d:%Y-%m-%d}" for d in s.index[s > 0]] for a, s in sig.items() if s.sum()}
    # a big drop nobody wrote about: QUIET. LOUD had news, NEVER has never had an article (not covered:
    # no news cannot be told from no data), BAD and EARN fell on news.
    assert hits(FF.news_quiet_drop(prices, drop=3.0, quiet=3)) == {"QUIET": [day(300)]}
    # a big drop on bad headlines, outside earnings: BAD (EARN released its results that day)
    assert hits(FF.news_bad_day(prices, drop=3.0, articles=2)) == {"BAD": [day(300)]}
    assert hits(FF.news_bad_day(prices, drop=3.0, articles=5)) == {}
    assert hits(FF.news_good_day(prices, rise=3.0, articles=2)) == {"GOOD": [day(300)]}


def test_news_families_stay_inside_the_downloaded_days(store, monkeypatch):
    """Past the last downloaded month there is no news file: silence there is not 'no news'."""
    idx = pd.bdate_range("2020-01-01", "2021-06-30")
    rows = [(f"{idx[100]:%Y-%m-%d}", "QUIET", 1, 0, 0, 0.0, 0)]
    prices, _ = _world(store, monkeypatch, rows, {"QUIET": {300: -0.08}})
    longer = pd.bdate_range("2020-01-01", "2021-09-30")
    r = np.where(np.arange(len(longer)) % 2 == 0, 0.01, -0.01).astype(float)
    r[300], r[len(idx) + 20] = -0.08, -0.08                        # the second drop: after the last file
    c = 100 * np.cumprod(1 + r)
    prices = {"QUIET": pd.DataFrame({"Open": c, "High": c, "Low": c, "Close": c, "Volume": 1e6}, longer)}
    s = FF.news_quiet_drop(prices, drop=3.0, quiet=3)["QUIET"]
    assert [f"{d:%Y-%m-%d}" for d in s.index[s > 0]] == [f"{idx[300]:%Y-%m-%d}"]
