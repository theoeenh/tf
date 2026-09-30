"""Machine-learning learner: meta-labelling of the strategies' trades.

The strategies still propose every trade (the "primary model"). This learner
is the "secondary model": before a trade opens, it estimates the probability
that the trade ends in profit, from what is known at that moment, and only
lets it through when the expected result is positive.

    features  market regime (ADX), volatility, distance to the 50/200-bar
              averages, momentum and RSI (in the trade's direction), the daily
              trend, news tone and coverage (daily GDELT and hourly Alpaca /
              Benzinga headlines), days to earnings / Fed / jobs, the
              AI analyst's view, hour and weekday, and how the same strategy
              has done lately (on this asset and on all assets)
    label     the trade made money after fees (R > 0)
    model     gradient-boosted trees (scikit-learn), settings fixed in advance
    training  walk-forward: refitted every `refit_days` on the trades that had
              already *closed* by then (skipped trades are followed without
              money, so it keeps learning from them). Nothing from the future.

Expected result of a trade = p * (average win in R) - (1 - p) * (average loss
in R), with the averages taken per strategy from the same training trades.
With `sizing`, the position is also scaled with it (1x at 0R, up to 2x at
+0.25R): money goes to whichever strategy works in the current conditions.
Until `min_trades` trades have closed, every trade is allowed.
"""
from __future__ import annotations

from collections import defaultdict, deque

import numpy as np
import pandas as pd

from . import data
from .journal import Verdict

STRATEGY_NAMES = ("donchian_trend", "squeeze_breakout", "rsi2_reversion", "news_momentum", "opening_range",
                  "vwap_reversion")
ASSET_CLASS = data.ASSET_CLASS
FEATURES = (["side"] + [f"is_{s}" for s in STRATEGY_NAMES] + ["is_crypto", "is_stock", "is_metal", "is_etf"]
            + ["adx", "atr_pct", "vol_rank", "dist200", "dist50", "ret5", "ret20", "rsi14", "daily_trend",
               "tone_z", "attention_z", "days_to_earnings", "days_to_fomc", "days_to_jobs", "ai_bias",
               "news_1h", "news_24h_z", "news_tone", "hour", "weekday", "sleeve_recent_r", "sleeve_trades",
               "strategy_recent_r"])


def _num(x) -> float:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return np.nan
    return x if np.isfinite(x) else np.nan


class MLLearner:
    """Drop-in replacement for journal.Learner (same keys / judge / record calls)."""

    def __init__(self, min_trades: int = 300, refit_days: int = 30, threshold: float = 0.0,
                 max_train: int = 20000, seed: int = 0, sizing: bool = False):
        self.min_trades, self.refit_days, self.threshold = min_trades, refit_days, threshold
        self.sizing = sizing  # scale the position with the expected result
        self.max_train, self.seed = max_train, seed
        self.X: list[list[float]] = []  # closed trades: features
        self.y: list[float] = []  # closed trades: R
        self.strat: list[str] = []
        self.sleeve_r: dict[tuple, deque] = defaultdict(lambda: deque(maxlen=20))
        self.sleeve_n: dict[tuple, int] = defaultdict(int)
        self.strategy_r: dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.model = None
        self.payoff: dict[str, tuple[float, float]] = {}
        self.next_fit: pd.Timestamp | None = None
        self.fits = 0
        self.decisions: list[dict] = []  # out-of-sample predictions, for the report

    # ------------------------------------------------------------ interface
    def keys(self, strategy: str, side: int, ctx: dict, asset: str = "", time=None, feats=None, **_) -> dict:
        f = feats or {}
        sleeve = (asset, strategy)
        s = float(side)
        row = {
            "side": s, **{f"is_{n}": float(strategy == n) for n in STRATEGY_NAMES},
            **{f"is_{c}": float(ASSET_CLASS.get(asset) == c) for c in ("crypto", "stock", "metal", "etf")},
            "adx": _num(f.get("adx")), "atr_pct": _num(f.get("atr_pct")), "vol_rank": _num(f.get("vol_rank")),
            # direction-aware: positive = the market already moves the trade's way
            "dist200": s * _num(f.get("dist200")), "dist50": s * _num(f.get("dist50")),
            "ret5": s * _num(f.get("ret5")), "ret20": s * _num(f.get("ret20")),
            "rsi14": s * (_num(f.get("rsi14")) - 50), "daily_trend": s * _num(f.get("daily_trend")),
            "tone_z": s * _num(f.get("tone_z")), "attention_z": _num(f.get("attention_z")),
            "days_to_earnings": min(_num(f.get("days_to_earnings")), 30.0),
            "days_to_fomc": min(_num(f.get("days_to_fomc")), 30.0),
            "days_to_jobs": min(_num(f.get("days_to_jobs")), 30.0),
            "ai_bias": s * np.nan_to_num(_num(f.get("ai_bias"))),
            "news_1h": _num(f.get("news_1h")), "news_24h_z": _num(f.get("news_24h_z")),
            "news_tone": s * _num(f.get("news_tone")),
            "hour": float(time.hour) if time is not None else np.nan,
            "weekday": float(time.weekday()) if time is not None else np.nan,
            "sleeve_recent_r": np.mean(self.sleeve_r[sleeve]) if self.sleeve_r[sleeve] else np.nan,
            "sleeve_trades": float(self.sleeve_n[sleeve]),
            "strategy_recent_r": np.mean(self.strategy_r[strategy]) if self.strategy_r[strategy] else np.nan,
        }
        return {"x": [row[k] for k in FEATURES], "strategy": strategy, "sleeve": sleeve,
                "time": pd.Timestamp(time) if time is not None else None, "pred": None}

    def judge(self, key: dict) -> Verdict:
        t = key["time"]
        if t is not None and (self.next_fit is None or t >= self.next_fit):
            self._fit()
            self.next_fit = t + pd.Timedelta(days=self.refit_days)
        if self.model is None:
            return Verdict(False, "")
        p = float(self.model.predict_proba(np.array([key["x"]], dtype=float)[:, self.cols])[0, 1])
        win, loss = self.payoff.get(key["strategy"], self.payoff["_all"])
        ev = p * win - (1 - p) * loss
        key["pred"] = (p, ev)
        if ev < self.threshold:
            return Verdict(True, f"SKIPPED by the ML learner: {p:.0%} estimated chance of profit, "
                                 f"expected {ev:+.2f}R (avg win {win:+.2f}R, avg loss -{loss:.2f}R).")
        if self.sizing:  # 1x at 0R expected, 2x from +0.25R, never below 0.5x
            return Verdict(False, "", size=float(np.clip(1 + ev / 0.25, 0.5, 2.0)))
        return Verdict(False, "")

    def record(self, key: dict, r: float, when=None) -> None:
        self.X.append(key["x"])
        self.y.append(float(r))
        self.strat.append(key["strategy"])
        self.sleeve_r[key["sleeve"]].append(float(r))
        self.sleeve_n[key["sleeve"]] += 1
        self.strategy_r[key["strategy"]].append(float(r))
        if key.get("pred") is not None:
            p, ev = key["pred"]
            self.decisions.append({"time": key["time"], "strategy": key["strategy"], "p": p, "ev": ev,
                                   "taken": ev >= self.threshold, "r": float(r)})

    # ------------------------------------------------------------ model
    def _fit(self) -> None:
        if len(self.y) < self.min_trades:
            return
        from sklearn.ensemble import HistGradientBoostingClassifier

        X = np.array(self.X[-self.max_train:], dtype=float)
        r = np.array(self.y[-self.max_train:])
        y = (r > 0).astype(int)
        if y.min() == y.max():
            return
        model = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=150,
                                               min_samples_leaf=50, l2_regularization=1.0,
                                               early_stopping=False, random_state=self.seed)
        # features never seen in training (e.g. hourly news in a daily run) are left out
        self.cols = ~np.all(np.isnan(X), axis=0)
        model.fit(X[:, self.cols], y)
        self.model = model
        self.fits += 1
        strat = np.array(self.strat[-self.max_train:])
        self.payoff = {"_all": _payoff(r)} | {s: _payoff(r[strat == s]) for s in set(strat) if (strat == s).sum() >= 30}

    # ------------------------------------------------------------ reporting
    def lessons(self, min_trades: int = 10) -> pd.DataFrame:
        return pd.DataFrame()  # the rule view does not apply; see report()

    def report(self) -> dict:
        """Out-of-sample quality of the predictions (each made before the trade's outcome was known)."""
        d = pd.DataFrame(self.decisions)
        if d.empty:
            return {"fits": self.fits, "judged": 0}
        from sklearn.metrics import roc_auc_score

        won = (d.r > 0).astype(int)
        auc = roc_auc_score(won, d.p) if won.nunique() == 2 else np.nan
        return {"fits": self.fits, "judged": len(d), "auc": auc,
                "taken": int(d.taken.sum()), "taken_avg_r": d.r[d.taken].mean(),
                "skipped": int((~d.taken).sum()), "skipped_avg_r": d.r[~d.taken].mean(),
                "by_quintile": d.groupby(pd.qcut(d.ev, 5, labels=False, duplicates="drop")).r.mean().to_dict()}


def _payoff(r: np.ndarray) -> tuple[float, float]:
    wins, losses = r[r > 0], r[r <= 0]
    return (float(wins.mean()) if len(wins) else 0.0, float(-losses.mean()) if len(losses) else 1.0)
