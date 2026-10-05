import numpy as np
import pandas as pd

from algo import insider_ml


class Recorder:
    seen: list = []

    def fit(self, X, y):
        Recorder.seen.append(X.index)
        return self

    def predict(self, X):
        return np.zeros(len(X))


def test_walk_forward_trains_only_on_finished_clusters(monkeypatch):
    rng = np.random.default_rng(0)
    dates = pd.to_datetime(rng.integers(pd.Timestamp("2015-01-01").value // 10**9,
                                        pd.Timestamp("2021-12-31").value // 10**9, 3000), unit="s").normalize()
    ev = pd.DataFrame({k: rng.normal(size=len(dates)) for k in insider_ml.FEATURES})
    ev["date"], ev["stock"], ev["target"] = dates, "X", rng.normal(size=len(dates))
    ev = ev.sort_values("date").reset_index(drop=True)
    Recorder.seen = []
    monkeypatch.setattr(insider_ml, "_model", lambda kind: Recorder())
    wf = insider_ml.walk_forward(ev, "ridge", 0.3)
    assert wf["date"].dt.year.min() == 2018 and len(Recorder.seen) == 4
    for y, idx in zip(range(2018, 2022), Recorder.seen):
        # every training cluster's 60 sessions were over before the January refit
        assert ev.loc[idx, "date"].max() < pd.Timestamp(f"{y}-01-01") - pd.Timedelta(days=95)
