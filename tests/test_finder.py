import numpy as np
import pandas as pd

from algo import finder as F


def test_deflated_sharpe_bar_rises_with_the_number_of_tries():
    one = F.deflated_sharpe(0.05, 500, 0.0, 3.0, [0.05])
    many = F.deflated_sharpe(0.05, 500, 0.0, 3.0, list(np.random.default_rng(0).normal(0, 0.04, 300)))
    assert one > 0.8 and many < one


def test_edge_removes_the_drift():
    idx = pd.date_range("2024-01-01", periods=400, freq="h")
    c = np.linspace(100, 140, 400)  # steady rise: every long looks good before the drift is removed
    df = pd.DataFrame({"Open": c, "High": c + 1, "Low": c - 1, "Close": c, "Volume": 1.0}, idx)
    sig = pd.Series(0, idx)
    sig.iloc[100:300:10] = 1
    ev = F.edge_events({"X": sig}, {"X": df}, 12)
    assert abs(ev["edge"].mean()) < 1e-6


def test_vault_is_sealed_by_default(monkeypatch):
    idx = pd.date_range("2025-06-25", "2025-07-05", freq="h")
    df = pd.DataFrame({"Open": 1.0, "High": 1.0, "Low": 1.0, "Close": 1.0, "Volume": 1.0}, idx)
    monkeypatch.setattr(F, "load_prices", lambda *a, **k: {"X": df})
    assert F.load()["X"].index.max() < pd.Timestamp(F.VAULT_START)
    assert F.load(include_vault=True)["X"].index.max() > pd.Timestamp(F.VAULT_START)
