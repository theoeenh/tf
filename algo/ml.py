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
               "strategy_recent_r", "asia_move", "europe_move",
               "insider_buyers_90d", "insider_buy_90d", "insider_sell_30d"])


def _num(x) -> float:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return np.nan
    return x if np.isfinite(x) else np.nan


class MLLearner:
    """Drop-in replacement for journal.Learner (same keys / judge / record calls)."""

    def __init__(self, min_trades: int = 300, refit_days: int = 30, threshold: float = 0.0,
                 max_train: int = 20000, seed: int = 0, sizing: bool = False, pool: "Pool | None" = None):
        self.pool = pool  # shared experience of every strategy on every asset (see Pool)
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
            # how Asia / Europe moved on their last finished day, in the trade's direction
            "asia_move": s * _num(f.get("asia_move")), "europe_move": s * _num(f.get("europe_move")),
            # insider buying supports a long, selling a short (NaN unless the 'insider' option is on)
            "insider_buyers_90d": s * _num(f.get("insider_buyers_90d")),
            "insider_buy_90d": s * _num(f.get("insider_buy_90d")),
            "insider_sell_30d": -s * _num(f.get("insider_sell_30d")),
            "hour": float(time.hour) if time is not None else np.nan,
            "weekday": float(time.weekday()) if time is not None else np.nan,
            **(self.pool.recent(asset, strategy, time) if self.pool is not None and time is not None else {
                "sleeve_recent_r": np.mean(self.sleeve_r[sleeve]) if self.sleeve_r[sleeve] else np.nan,
                "sleeve_trades": float(self.sleeve_n[sleeve]),
                "strategy_recent_r": np.mean(self.strategy_r[strategy]) if self.strategy_r[strategy] else np.nan}),
        }
        return {"x": [row[k] for k in FEATURES], "strategy": strategy, "sleeve": sleeve,
                "time": pd.Timestamp(time) if time is not None else None, "pred": None}

    def judge(self, key: dict) -> Verdict:
        t = key["time"]
        if t is not None and (self.next_fit is None or t >= self.next_fit):
            self._fit(t)
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
    def _fit(self, t: pd.Timestamp | None = None) -> None:
        if self.pool is not None and t is not None:
            X, r, strat = self.pool.before(t, self.max_train)  # every trade closed before t
        else:
            X = np.array(self.X[-self.max_train:], dtype=float)
            r = np.array(self.y[-self.max_train:])
            strat = np.array(self.strat[-self.max_train:])
        if len(r) < self.min_trades:
            return
        from sklearn.ensemble import HistGradientBoostingClassifier

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
        self.trained_on = len(r)
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


# ---------------------------------------------------------------- shared learning pool


class Pool:
    """The shared experience every account learns from: the outcome of every signal of
    every strategy on every asset, long and short, followed without money whether or
    not an account took it (see build_pool). Rows are only ever used once the trade had
    closed (exit time before the decision), so nothing leaks from the future."""

    def __init__(self, rows: pd.DataFrame):
        rows = rows.sort_values("exit_time").reset_index(drop=True)
        self.rows = rows
        self.X = rows[list(FEATURES)].to_numpy(dtype=float)
        self.r = rows["r"].to_numpy(dtype=float)
        self.strat = rows["strategy"].to_numpy()
        self.exit = rows["exit_time"].to_numpy(dtype="datetime64[ns]")
        self._sleeve = {k: (g["exit_time"].to_numpy(dtype="datetime64[ns]"), g["r"].to_numpy(dtype=float))
                        for k, g in rows.groupby(["asset", "strategy"])}
        self._strategy = {k: (g["exit_time"].to_numpy(dtype="datetime64[ns]"), g["r"].to_numpy(dtype=float))
                          for k, g in rows.groupby("strategy")}

    def __len__(self) -> int:
        return len(self.r)

    def before(self, t, n: int):
        k = int(np.searchsorted(self.exit, np.datetime64(pd.Timestamp(t)), side="left"))
        lo = max(0, k - n)
        return self.X[lo:k], self.r[lo:k], self.strat[lo:k]

    def recent(self, asset: str, strategy: str, t) -> dict:
        t64 = np.datetime64(pd.Timestamp(t))

        def last(d, key, n):
            if key not in d:
                return np.nan, 0
            ex, r = d[key]
            k = int(np.searchsorted(ex, t64, side="left"))
            return (float(r[max(0, k - n):k].mean()) if k else np.nan), k

        s_r, s_n = last(self._sleeve, (asset, strategy), 20)
        g_r, _ = last(self._strategy, strategy, 50)
        return {"sleeve_recent_r": s_r, "sleeve_trades": float(s_n), "strategy_recent_r": g_r}


class _Collector(MLLearner):
    """Follows every signal without money and writes down what happened."""

    def __init__(self):
        super().__init__()
        self.out: list[dict] = []

    def judge(self, key: dict) -> Verdict:
        return Verdict(True, "Followed without money for the shared learning pool.")

    def record(self, key: dict, r: float, when=None) -> None:
        super().record(key, r, when)
        self.out.append(dict(zip(FEATURES, key["x"])) | {
            "strategy": key["strategy"], "asset": key["sleeve"][0], "entry_time": key["time"],
            "exit_time": pd.Timestamp(when), "r": float(r)})


_POOLS: dict = {}


def build_pool(prices: dict, context: dict | None) -> Pool:
    """Run every strategy (daily, hourly-native, news) on every asset, long and short,
    all followed without money, and collect the outcomes. The same pool serves all
    accounts, so each learns from the strategies and assets of all of them."""
    key = (id(prices), id(context))
    if key in _POOLS:
        return _POOLS[key]
    from .portfolio import PortfolioConfig, run_portfolio
    from .system import COSTS, build_sleeves

    col = _Collector()
    sleeves = build_sleeves(prices, True, context, news=bool(context), trend=False, intraday_strats=True)
    run_portfolio(prices, sleeves, COSTS, PortfolioConfig(learner=col), close_at_end=False, context=context)
    pool = Pool(pd.DataFrame(col.out, columns=list(FEATURES) + ["strategy", "asset", "entry_time", "exit_time", "r"]))
    _POOLS.clear()  # keep only the latest (the same prices are reused by calibration runs)
    _POOLS[key] = pool
    return pool
