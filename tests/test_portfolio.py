import pandas as pd
import pytest

from algo import journal
from algo.engine import Costs, ExitRule
from algo.portfolio import PortfolioConfig, Sleeve, run_portfolio
from tests.test_engine import flat_bars, signal_at


def two_assets():
    a, b = flat_bars(n=40), flat_bars(n=40, px=50.0, rng=1.0)
    return {"A": a, "B": b}


def test_two_assets_share_one_account():
    prices = two_assets()
    prices["A"].iloc[21, prices["A"].columns.get_loc("High")] = 200.0  # A hits target (+3R)
    prices["B"].iloc[21, prices["B"].columns.get_loc("Low")] = 10.0  # B hits stop (-1R)
    sleeves = [Sleeve("A", "s", signal_at(prices["A"], 19), ExitRule(1.0, 3.0)),
               Sleeve("B", "s", signal_at(prices["B"], 19), ExitRule(1.0, 3.0))]
    res = run_portfolio(prices, sleeves, {"A": Costs(), "B": Costs()}, PortfolioConfig(risk_pct=0.01, max_gross=2.0))
    assert sorted(t.r_multiple for t in res.trades) == pytest.approx([-1.0, 3.0])
    # both sized on the same 100k equity at the same open
    assert res.equity.iloc[-1] == pytest.approx(100_000 + 3_000 - 1_000)


def test_two_strategies_on_same_asset_trade_at_once():
    prices = {"A": flat_bars(n=40)}
    sleeves = [Sleeve("A", "one", signal_at(prices["A"], 19), ExitRule(10.0, 10.0)),
               Sleeve("A", "two", signal_at(prices["A"], 20), ExitRule(10.0, 10.0))]
    res = run_portfolio(prices, sleeves, {"A": Costs()}, PortfolioConfig(risk_pct=0.001))
    assert len(res.trades) == 2 and res.gross.max() > 0


def test_gross_exposure_cap():
    prices = {"A": flat_bars(n=40, rng=0.01)}  # tiny ATR: risk sizing wants a huge position
    sleeves = [Sleeve("A", "s", signal_at(prices["A"], 19), ExitRule(1.0, 3.0))]
    res = run_portfolio(prices, sleeves, {"A": Costs()}, PortfolioConfig(max_gross=2.0, financing_apr=0.0))
    assert res.gross.max() == pytest.approx(2.0, rel=1e-9)


def test_financing_charged_on_borrowed_cash():
    prices = {"A": flat_bars(n=40, rng=0.01)}
    sleeves = [Sleeve("A", "s", signal_at(prices["A"], 19), ExitRule(1.0, 1000.0))]  # 2x gross, never exits
    free = run_portfolio(prices, sleeves, {"A": Costs()}, PortfolioConfig(max_gross=2.0, financing_apr=0.0))
    paid = run_portfolio(prices, sleeves, {"A": Costs()}, PortfolioConfig(max_gross=2.0, financing_apr=0.10))
    borrowed_days = (prices["A"].index[-1] - prices["A"].index[20]).days
    assert free.equity.iloc[-1] - paid.equity.iloc[-1] == pytest.approx(100_000 * 0.10 * borrowed_days / 365, rel=0.01)


def test_intraday_many_trades_per_day():
    idx = pd.date_range("2024-01-01", periods=24 * 5, freq="h")
    df = pd.DataFrame({"Open": 100.0, "High": 101.0, "Low": 99.0, "Close": 100.0, "Volume": 0.0}, index=idx)
    sig = pd.Series(0, index=idx)
    sig.iloc[30::3] = 1  # signal every 3 hours
    res = run_portfolio({"A": df}, [Sleeve("A", "s", sig, ExitRule(1.0, 3.0, max_bars=2))], {"A": Costs()})
    per_day = res.trades_df.groupby(res.trades_df.entry_date.dt.date).size()
    assert per_day.max() >= 5


def losing_setup_prices(n_trades=30):
    """Each signal is followed by a bar that hits the stop."""
    n = 20 + n_trades * 3 + 5
    df = flat_bars(n=n)
    sig = pd.Series(0, index=df.index)
    for k in range(n_trades):
        i = 19 + 3 * k
        sig.iloc[i] = 1
        df.iloc[i + 2, df.columns.get_loc("Low")] = 50.0
    return df, sig


def test_learner_blocks_a_losing_setup_and_keeps_shadow_trades():
    df, sig = losing_setup_prices()
    class OneSetupLearner(journal.Learner):  # every trade counts as the same setup
        @staticmethod
        def key(strategy, side, ctx):
            return ("s", "long", "trend", "mid", True)

    learner = OneSetupLearner(min_trades=5, min_avg_r=-0.1)
    res = run_portfolio({"A": df}, [Sleeve("A", "s", sig, ExitRule(1.0, 3.0))], {"A": Costs()},
                        PortfolioConfig(learner=learner))
    assert len(res.trades) == 5  # learned after 5 straight losses
    assert len(res.shadow_trades) == 25 and all(t.r_multiple < 0 for t in res.shadow_trades)
    assert res.equity.iloc[-1] == pytest.approx(100_000 * 0.99 ** 5, rel=1e-6)
    assert res.shadow_trades[0].rationale.startswith("SKIPPED by learner")


def test_journal_records_reasoning_and_diagnosis():
    df, sig = losing_setup_prices(3)
    res = run_portfolio({"A": df}, [Sleeve("A", "donchian_trend", sig, ExitRule(1.0, 3.0))], {"A": Costs()})
    t = res.trades[0]
    assert t.rationale.startswith("LONG A") and "risking $1,000" in t.rationale
    assert t.error in journal.ERRORS and t.lesson


def test_diagnosis_rules():
    ctx = {"aligned": True, "regime": "trend"}
    assert journal.diagnose(2.0, 2.1, 2.5, ctx, "x") == "none"
    assert journal.diagnose(-0.05, 0.02, 0.5, ctx, "x") == "fees_ate_edge"
    assert journal.diagnose(-1.6, -1.5, 0.1, ctx, "x") == "gap_through_stop"
    assert journal.diagnose(-1.0, -0.98, 1.4, ctx, "x") == "gave_back_profit"
    assert journal.diagnose(-1.0, -0.98, 0.5, {"aligned": False, "regime": "trend"}, "x") == "counter_trend"
    assert journal.diagnose(-1.0, -0.98, 0.5, {"aligned": True, "regime": "chop"}, "x") == "choppy_market"
    assert journal.diagnose(-1.0, -0.98, 0.1, ctx, "x") == "wrong_immediately"


def test_results_do_not_depend_on_hash_seed():
    import subprocess
    import sys

    code = ("from algo.research import synthetic_prices as s; from algo import system; "
            "p={a: s(a if a in ('BTC','GOLD','SPY') else 'BTC', seed=i) for i, a in enumerate(system.UNIVERSE)}; "
            "print(round(system.run_system(p, True, True, 0.01).equity.iloc[-1], 6))")
    outs = {subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env={"PYTHONHASHSEED": str(k),
            "PATH": ""}, cwd=str(__import__("pathlib").Path(__file__).parent.parent)).stdout for k in (1, 2, 3)}
    assert len(outs) == 1 and outs.pop().strip()


def test_concentration_caps_limit_risk_per_asset_and_per_group():
    """Off by default; with a cap, a second trade in the same asset (or group) only gets the risk
    left under the cap."""
    prices = two_assets()
    sleeves = [Sleeve("A", "one", signal_at(prices["A"], 19), ExitRule(10.0, 10.0)),
               Sleeve("A", "two", signal_at(prices["A"], 20), ExitRule(10.0, 10.0)),
               Sleeve("B", "one", signal_at(prices["B"], 20), ExitRule(10.0, 10.0))]
    costs = {"A": Costs(), "B": Costs()}

    def qty(cfg):
        res = run_portfolio(prices, sleeves, costs, cfg)
        return {(t.asset, t.strategy): t.qty for t in res.trades}

    free = qty(PortfolioConfig(risk_pct=0.001, max_gross=5.0))
    per_asset = qty(PortfolioConfig(risk_pct=0.001, max_gross=5.0, max_asset_risk=0.0015))
    assert per_asset[("A", "one")] == pytest.approx(free[("A", "one")])
    assert per_asset[("A", "two")] == pytest.approx(free[("A", "two")] / 2, rel=0.02)  # 0.5R left under 1.5R
    assert per_asset[("B", "one")] == pytest.approx(free[("B", "one")])  # another asset: untouched
    group = qty(PortfolioConfig(risk_pct=0.001, max_gross=5.0, max_group_risk=0.0015, group_of={"A": "g", "B": "g"}))
    assert group[("A", "two")] == pytest.approx(free[("A", "two")] / 2, rel=0.02)
    assert ("B", "one") not in group  # the group is full (1R + 0.5R): no room left for B
