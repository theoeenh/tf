import numpy as np
import pandas as pd

from algo.engine import Costs, ExitRule
from algo.portfolio import PortfolioConfig, Sleeve, run_portfolio


def test_brake_closes_everything_and_stays_flat_after_the_drawdown():
    idx = pd.date_range("2026-01-01", periods=200, freq="h")
    c = pd.Series(np.r_[np.full(50, 100.0), np.linspace(100, 60, 150)], idx)  # steady fall
    df = pd.DataFrame({"Open": c, "High": c + 0.2, "Low": c - 0.2, "Close": c, "Volume": 1.0})
    sig = pd.Series(1, idx)  # always wants to be long
    sleeve = Sleeve("X", "s", sig, ExitRule(stop_atr=50.0, rr=None), allow_short=False)
    base = dict(risk_pct=0.2, max_gross=1.0)
    free = run_portfolio({"X": df}, [sleeve], {"X": Costs()}, PortfolioConfig(**base), close_at_end=False)
    braked = run_portfolio({"X": df}, [sleeve], {"X": Costs()}, PortfolioConfig(**base, brake=0.10),
                           close_at_end=False)
    assert free.equity.iloc[-1] < 0.8 * 100_000  # without the brake it rides the fall
    assert braked.equity.iloc[-1] > 0.85 * 100_000  # the brake stops it near -10%
    assert any(t.reason == "brake" for t in braked.trades)
    assert not braked.open_positions  # and it never opens again
