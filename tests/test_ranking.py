import numpy as np
import pandas as pd

from algo.engine import Costs, ExitRule
from algo.journal import Verdict
from algo.portfolio import PortfolioConfig, Sleeve, run_portfolio


class ScoreLearner:
    """Gives each asset a fixed expected result, never skips."""
    def __init__(self, scores): self.scores = scores
    def keys(self, strategy, side, ctx, asset="", **_): return {"asset": asset, "pred": (0.5, self.scores[asset])}
    def judge(self, key): return Verdict(False, "")
    def record(self, key, r, when=None): pass


def test_budget_goes_to_the_best_candidate_first():
    idx = pd.date_range("2026-01-01", periods=60, freq="h")
    c = pd.Series(np.linspace(100, 101, 60), idx)
    df = pd.DataFrame({"Open": c, "High": c + 0.5, "Low": c - 0.5, "Close": c, "Volume": 1.0})
    sig = pd.Series(0, idx); sig.iloc[30] = 1  # both assets signal on the same bar
    sleeves = [Sleeve(a, "s", sig, ExitRule(stop_atr=2.0, rr=None), allow_short=False) for a in ("AAA", "BBB")]
    # room for only one position: max gross 1x, each trade sized at 100% of equity
    cfg = PortfolioConfig(risk_pct=0.5, max_gross=1.0, learner=ScoreLearner({"AAA": 0.05, "BBB": 0.30}))
    res = run_portfolio({"AAA": df, "BBB": df.copy()}, sleeves, {"AAA": Costs(), "BBB": Costs()}, cfg,
                        close_at_end=False)
    held = {p["asset"]: p["qty"] for p in res.open_positions if not p["shadow"]}
    assert held.get("BBB", 0) > held.get("AAA", 0)  # BBB (better expected result) was filled first
