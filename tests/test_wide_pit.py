"""Point-in-time index membership: a stock counts only on the days it was known to be a member."""
import numpy as np
import pandas as pd
import pytest

from algo import wide_pit as P


def snaps(rows):
    return pd.DataFrame([{"date": pd.Timestamp(d), "index": i, "symbol": s, "sector": sec}
                         for d, i, s, sec in rows])


@pytest.fixture
def table(tmp_path, monkeypatch):
    """A small history on disk: AAA always in the S&P 500; GONE left on 1 March 2020; LATE joined the
    S&P 600 on 1 June 2020 and moved up to the S&P 400 on 1 February 2021."""
    h = pd.DataFrame([
        dict(symbol="AAA", index="sp500", start="2015-12-01", end=None, sector="Energy"),
        dict(symbol="GONE", index="sp500", start="2015-12-01", end="2020-03-01", sector="Financials"),
        dict(symbol="LATE", index="sp600", start="2020-06-01", end="2021-02-01", sector="Energy"),
        dict(symbol="LATE", index="sp400", start="2021-02-01", end=None, sector="Energy"),
    ])
    path = tmp_path / "members_history.csv"
    h.to_csv(path, index=False)
    monkeypatch.setattr(P, "PATH", path)
    P._cache.clear()
    yield h
    P._cache.clear()


def test_history_page_gives_each_revision_once_with_its_time():
    html = ('<li data-mw-revid="111" class="x"><a class="mw-changeslist-date" title="t">06:51, 27 August 2018</a></li>'
            '<li data-mw-revid="222" class="x"><a class="mw-changeslist-date" title="t">20:47, 1 January 2011</a></li>')
    assert P.parse_history(html) == [(pd.Timestamp("2018-08-27 06:51"), 111), (pd.Timestamp("2011-01-01 20:47"), 222)]


def test_members_table_is_read_whatever_the_columns_were_called():
    rows = "".join(f"<tr><td>Co {i}</td><td>T{chr(65 + i // 26)}{chr(65 + i % 26)}</td><td>Energy</td></tr>"
                   for i in range(30))
    old = ("<table><tr><th>Company</th><th>Ticker symbol</th><th>GICS Economic Sector</th></tr>" + rows
           + "<tr><td>Berkshire</td><td>BRK.B</td><td>Telecommunication Services</td></tr>"
           + "<tr><td>note</td><td>see the footnote below</td><td>x</td></tr></table>"
           + "<table><tr><th>Date</th><th>Added</th></tr><tr><td>2019</td><td>X</td></tr></table>")
    m = P.parse_members(old)
    assert len(m) == 31 and "BRK-B" in set(m["symbol"])                # the footnote row is not a ticker
    assert m.set_index("symbol").loc["BRK-B", "sector"] == "Communication Services"   # old sector name


def test_spells_open_on_the_first_snapshot_showing_a_stock_and_close_on_the_first_without():
    s = snaps([("2020-01-01", "sp500", "AAA", "Energy"), ("2020-02-01", "sp500", "AAA", "Energy"),
               ("2020-03-01", "sp500", "AAA", "Energy"), ("2020-04-01", "sp500", "AAA", "Energy"),
               ("2020-01-01", "sp500", "GONE", "Financials"), ("2020-02-01", "sp500", "GONE", "Financials"),
               ("2020-03-01", "sp500", "NEW", None), ("2020-04-01", "sp500", "NEW", "Utilities")])
    h = P.spells(s).set_index("symbol")
    assert h.loc["AAA", "start"] == pd.Timestamp("2020-01-01") and pd.isna(h.loc["AAA", "end"])
    assert h.loc["GONE", "end"] == pd.Timestamp("2020-03-01")          # still eligible in February, not after
    assert h.loc["NEW", "start"] == pd.Timestamp("2020-03-01")         # never before the list showed it
    assert h.loc["NEW", "sector"] == "Utilities"


def test_one_missing_snapshot_is_a_bad_edit_two_are_an_exit_and_a_return():
    months = pd.date_range("2020-01-01", periods=8, freq="MS")
    s = snaps([(d, "sp400", "KEEP", "Energy") for d in months]
              + [(d, "sp400", "BLIP", "Energy") for k, d in enumerate(months) if k != 3]
              + [(d, "sp400", "BACK", "Energy") for k, d in enumerate(months) if k not in (3, 4)])
    h = P.spells(s)
    assert len(h[h["symbol"] == "BLIP"]) == 1
    back = h[h["symbol"] == "BACK"].sort_values("start")
    assert back["start"].tolist() == [months[0], months[5]] and back["end"].iloc[0] == months[3]


def test_roll_closes_and_opens_spells_today_and_leaves_the_past_alone(table):
    today = pd.DataFrame([dict(symbol="AAA", index="sp500", sector="Energy"),
                          dict(symbol="LATE", index="sp500", sector="Energy"),      # moved up from the 400
                          dict(symbol="FRESH", index="sp600", sector="Materials")])
    before = P.history()
    h = P.roll(before, today, pd.Timestamp("2026-11-12"))
    late = h[h["symbol"] == "LATE"].sort_values("start")
    assert late["index"].tolist() == ["sp600", "sp400", "sp500"]
    assert late["end"].iloc[1] == pd.Timestamp("2026-11-12") and pd.isna(late["end"].iloc[2])
    assert h[h["symbol"] == "FRESH"]["start"].iloc[0] == pd.Timestamp("2026-11-12")
    old = h.merge(before, on=["symbol", "index", "start"], suffixes=("", "_was"))
    closed = old[old["end_was"].notna()]
    assert (closed["end"] == closed["end_was"]).all()                   # a closed spell never changes
    again = P.roll(h, today, pd.Timestamp("2026-11-13"))
    assert len(again) == len(h)                                         # the same lists the next day: nothing new


def test_mask_follows_the_segment_and_the_day(table):
    days = pd.bdate_range("2020-01-01", "2021-06-30")
    gone = P.mask("all", "GONE", days)
    assert gone[days < "2020-03-01"].all() and not gone[days >= "2020-03-01"].any()
    late600, late400 = P.mask("sp600", "LATE", days), P.mask("sp400", "LATE", days)
    assert not late600[days < "2020-06-01"].any() and late600[(days >= "2020-06-01") & (days < "2021-02-01")].all()
    assert not late600[days >= "2021-02-01"].any() and late400[days >= "2021-02-01"].all()
    both = P.mask("sp1500", "LATE", days)
    assert (both == (days >= "2020-06-01")).all()                       # any of the three indexes
    assert not P.mask("all", "LATE", days).any()                        # never in the S&P 500
    assert P.mask("sector:Energy", "LATE", days).sum() == both.sum()
    assert not P.mask("sector:Energy", "GONE", days).any()              # a Financials stock
    assert P.segment_ever("sp600")("LATE") and not P.segment_ever("sp600")("AAA")
    assert set(P.ever()) == {"AAA", "GONE", "LATE"}


def bars(days, price=10.0):
    return pd.DataFrame({"Open": price, "High": price, "Low": price, "Close": price, "Volume": 100.0}, index=days)


def test_cut_keeps_the_warmup_and_stops_when_the_stock_stops_trading():
    days = pd.bdate_range("2015-01-01", "2020-02-14")                    # bought out: last bar 14 Feb 2020
    df = P.cut(bars(days), pd.Timestamp("2018-01-01"), pd.Timestamp("2020-03-01"))
    assert df.index[0] >= pd.Timestamp("2018-01-01") - P.WARMUP and df.index[0] <= pd.Timestamp("2016-07-05")
    assert df.index[-1] == pd.Timestamp("2020-02-14")
    current = P.cut(bars(days), pd.Timestamp("2018-01-01"), None)
    assert current.index[-1] == days[-1]


def test_cut_does_not_read_a_ticker_reused_by_another_company():
    old = pd.bdate_range("2016-01-01", "2022-06-08")                     # the company under its old ticker
    reused = pd.bdate_range("2025-03-03", "2026-11-10")                  # another company, same ticker, later
    df = P.cut(bars(old.append(reused)), pd.Timestamp("2015-12-01"), pd.Timestamp("2022-07-01"))
    assert df.index[-1] == pd.Timestamp("2022-06-08")


def test_cut_gives_a_stock_that_left_but_still_trades_time_to_close_its_trades():
    days = pd.bdate_range("2016-01-01", "2026-11-10")                    # dropped from the index, still listed
    df = P.cut(bars(days), pd.Timestamp("2015-12-01"), pd.Timestamp("2020-03-01"))
    after = df.index[df.index >= "2020-03-01"]
    assert len(after) == P.GRACE and df.index[-1] < pd.Timestamp("2020-08-01")


def test_universe_return_counts_a_stock_only_while_it_is_a_member(table):
    days = pd.bdate_range("2020-02-24", "2020-03-06")
    up = pd.DataFrame({"Close": 100 * 1.01 ** np.arange(len(days))}, index=days)     # +1% a day
    flat = pd.DataFrame({"Close": 50.0}, index=days)
    r = P.universe_returns({"AAA": flat, "GONE": up, "LATE": up}, "all")             # LATE: not in the S&P 500
    assert r[days[1]] == pytest.approx(0.005)                           # both members: (0% + 1%) / 2
    assert r[pd.Timestamp("2020-03-02")] == pytest.approx(0.0)          # GONE has left: AAA alone
