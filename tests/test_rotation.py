import numpy as np
import pandas as pd

from algo import rotation as R

ASSETS = R.RISKY + [R.CASH]


def _closes(days, growth):
    """Daily closes per ETF growing at a steady daily rate (`growth`: ETF -> daily return)."""
    t = np.arange(len(days))
    return pd.DataFrame({a: 100 * (1 + growth.get(a, 0.0)) ** t for a in ASSETS}, index=days)


def test_top_three_by_twelve_month_return_and_only_above_the_average():
    me = pd.DataFrame({a: np.linspace(100, 100, 13) for a in ASSETS})
    me["SPY"] = np.linspace(100, 130, 13)                     # best, rising: held
    me["GLD"] = np.linspace(100, 125, 13)                     # second: held
    me["DBC"] = np.r_[np.linspace(100, 140, 12), 112]         # third by 12 months, but below its average now
    w = R.target_weights(me)
    assert w == {"SPY": 1 / 3, "GLD": 1 / 3, "SHY": 1 / 3}


def test_a_month_counts_only_once_its_last_session_has_closed():
    days = pd.bdate_range("2026-08-03", "2026-10-29")
    close = _closes(days, {})
    me = R.completed_month_ends(close, next_session=pd.Timestamp("2026-10-30"))
    assert [d.strftime("%Y-%m-%d") for d in me.index] == ["2026-08-31", "2026-09-30"]
    full = _closes(pd.bdate_range("2026-08-03", "2026-10-30"), {})
    me = R.completed_month_ends(full, next_session=pd.Timestamp("2026-11-02"))
    assert me.index[-1] == pd.Timestamp("2026-10-30")


def test_replay_buys_at_the_next_open_and_rebalances_after_each_month_end():
    days = pd.bdate_range("2025-06-02", "2026-11-04")
    close = _closes(days, {"SPY": 0.001, "GLD": 0.0008, "EFA": 0.0006})
    open_ = close * 0.999
    # before the start's first session: September's decision waits for the next open
    pre = R.replay(open_.loc[:"2026-10-23"], close.loc[:"2026-10-23"], pd.Timestamp("2026-10-26"), 95_000.0,
                   next_session=pd.Timestamp("2026-10-26"))
    assert pre["pending"][0] == pd.Timestamp("2026-09-30") and set(pre["pending"][1]) == {"SPY", "GLD", "EFA"}
    assert not len(pre["equity"]) and not pre["shares"]
    book = R.replay(open_, close, pd.Timestamp("2026-10-26"), 95_000.0, next_session=pd.Timestamp("2026-11-05"))
    assert book["pending"] is None and set(book["shares"]) == {"SPY", "GLD", "EFA"}
    first = book["equity"].index[0]
    assert first == pd.Timestamp("2026-10-26")
    spent = sum(q * open_.at[first, a] for a, q in book["shares"].items())
    assert abs(spent - 95_000) < 95_000 * 0.002                                    # all in, minus costs
    # October's decision (30 Oct close) is traded at the 2 Nov open: the same three, re-weighted
    assert all(t["exit_date"] == "2026-11-02" for t in book["trades"])
    # no future data: the book up to 30 Oct is the same with or without November's prices
    cut = R.replay(open_.loc[:"2026-10-30"], close.loc[:"2026-10-30"], pd.Timestamp("2026-10-26"), 95_000.0,
                   next_session=pd.Timestamp("2026-11-02"))
    assert cut["equity"].equals(book["equity"].loc[:"2026-10-30"])
    assert cut["pending"][0] == pd.Timestamp("2026-10-30")
