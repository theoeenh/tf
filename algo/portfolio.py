"""Multi-asset, multi-strategy portfolio backtester.

One shared account trades many "sleeves". A sleeve is one strategy on one
asset and holds at most one position at a time, but several sleeves can trade
the same asset at once, and on hourly bars a sleeve can trade many times a
day. Execution rules are the same as `engine` (see its docstring):
signal on a bar's close -> fill at the next bar's open, ATR stops, targets
that can depend on the trend regime, trailing stops, gaps fill at the open,
stop first when a bar touches both levels, fees + slippage on every fill,
borrow cost on shorts.

Portfolio rules:
- Each trade risks `risk_pct` of current equity (open positions marked at the
  last close).
- Total notional is capped at `max_gross` x equity. Above 1.0 the account
  borrows cash and pays `financing_apr` on it.
- Total open risk (distance to stop x size, summed) is capped at
  `max_open_risk` x equity.
- An optional Learner can veto trades. Vetoed trades are still followed as
  "shadow" trades (no money) so the learner keeps getting feedback.
- Optional brake: once equity falls `brake` below its highest value, every
  position closes at the next bar's open and nothing opens again.
- Optional blackout bars per asset (scheduled events, known in advance): no
  position is held through them, so open trades close at the bar's open and
  no trade opens on it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import journal
from .engine import Costs, ExitRule, Trade
from .indicators import atr as atr_indicator


@dataclass
class Sleeve:
    asset: str
    strategy: str
    signals: pd.Series  # +1 long, -1 short, 0 nothing
    exit_rule: ExitRule
    allow_short: bool = True


@dataclass
class PortfolioConfig:
    initial_capital: float = 100_000.0
    risk_pct: float = 0.01
    max_gross: float = 1.0
    max_open_risk: float | None = None
    financing_apr: float = 0.06
    learner: journal.Learner | None = None
    brake: float | None = None  # stop for good once equity is this far below its peak (0.10 = -10%)


@dataclass
class PortfolioResult:
    equity: pd.Series
    trades: list[Trade] = field(default_factory=list)
    shadow_trades: list[Trade] = field(default_factory=list)
    gross: pd.Series | None = None  # total notional / equity
    net_side: pd.Series | None = None  # sign of the summed position (single-sleeve use)
    learner: journal.Learner | None = None
    open_positions: list[dict] = field(default_factory=list)  # when close_at_end=False

    @property
    def trades_df(self) -> pd.DataFrame:
        return pd.DataFrame([t.__dict__ for t in self.trades])


class _Position:
    __slots__ = ("side", "q", "entry_px", "stop", "initial_stop", "target", "dist", "extreme", "entry_row",
                 "entry_time", "fees", "best", "worst", "ctx", "key", "rationale", "shadow")


class _Asset:
    def __init__(self, df: pd.DataFrame, atr_n: int, extra: pd.DataFrame | None = None,
                 blocked: pd.Series | None = None):
        self.o, self.h, self.l, self.c = (df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
        self.atr = atr_indicator(df, atr_n).to_numpy()
        f = journal.compute_features(df)
        if extra is not None:  # news, events, AI views: must already be point-in-time per bar
            f = f.join(extra.reindex(df.index), rsuffix="_x")
        self.feats = {k: f[k].to_numpy() for k in f.columns}
        self.index = df.index
        self.blocked = (np.zeros(len(df), bool) if blocked is None
                        else blocked.reindex(df.index).fillna(False).to_numpy(dtype=bool))
        self.secs = df.index.to_numpy().astype("datetime64[s]").astype(np.int64)
        self.mark = np.nan
        self.seen = False  # had a bar inside the window already


def run_portfolio(
    prices: dict[str, pd.DataFrame],
    sleeves: list[Sleeve],
    costs: dict[str, Costs],
    cfg: PortfolioConfig = PortfolioConfig(),
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
    atr_n: int = 14,
    close_at_end: bool = True,
    context: dict[str, pd.DataFrame] | None = None,
    blocked: dict[str, pd.Series] | None = None,
) -> PortfolioResult:
    # Fixed processing order (sleeve order): a set's order changes between runs,
    # and the order matters when several assets trade on the same bar.
    context = context or {}
    blocked = blocked or {}
    assets = {name: _Asset(prices[name], atr_n, context.get(name), blocked.get(name))
              for name in dict.fromkeys(s.asset for s in sleeves)}
    timeline = pd.DatetimeIndex(sorted(set().union(*(prices[a].index for a in assets))))
    if start is not None:
        timeline = timeline[timeline >= pd.Timestamp(start)]
    if end is not None:
        end_ts = pd.Timestamp(end)
        if end_ts == end_ts.normalize():
            end_ts += pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # whole end day
        timeline = timeline[timeline <= end_ts]
    if len(timeline) < 2:
        raise ValueError("backtest window has fewer than 2 bars")
    rows = {a: pd.Series(np.arange(len(prices[a])), prices[a].index).reindex(timeline).fillna(-1)
            .astype(int).to_numpy() for a in assets}

    sig = {}
    for k, s in enumerate(sleeves):
        v = s.signals.reindex(prices[s.asset].index).fillna(0).astype(int).to_numpy()
        sig[k] = np.where(v < 0, 0, v) if not s.allow_short else v
    by_asset: dict[str, list[int]] = {a: [] for a in assets}
    for k, s in enumerate(sleeves):
        by_asset[s.asset].append(k)
    pos: dict[int, _Position | None] = {k: None for k in range(len(sleeves))}
    learner = cfg.learner

    cash = cfg.initial_capital
    trades: list[Trade] = []
    shadows: list[Trade] = []
    n = len(timeline)
    equity, gross, net_side = np.empty(n), np.zeros(n), np.zeros(n)
    tsecs = timeline.to_numpy().astype("datetime64[s]").astype(np.int64)

    def marked_value() -> tuple[float, float, float]:
        """(net position value, gross notional, open risk) at last marks."""
        net = grs = risk = 0.0
        for k, p in pos.items():
            if p is None or p.shadow:
                continue
            m = assets[sleeves[k].asset].mark
            m = p.entry_px if not np.isfinite(m) else m
            net += p.q * m
            grs += abs(p.q) * m
            risk += abs(p.q) * max(0.0, p.side * (m - p.stop))
        return net, grs, risk

    def close(k: int, A: _Asset, i: int, raw: float, reason: str) -> None:
        nonlocal cash
        p, s = pos[k], sleeves[k]
        c = costs[s.asset]
        px = raw * (1 - p.side * c.slippage_bps / 1e4)
        exit_fee = abs(p.q) * px * c.fee_bps / 1e4
        if not p.shadow:
            cash += p.q * px - exit_fee
        fees = p.fees + exit_fee
        gross_pnl = p.q * (px - p.entry_px)
        pnl = gross_pnl - fees
        risk = abs(p.q) * p.dist
        r, gross_r = pnl / risk, gross_pnl / risk
        mfe_r = (p.best - p.entry_px) * p.side / p.dist
        mae_r = (p.worst - p.entry_px) * p.side / p.dist
        err = journal.diagnose(r, gross_r, mfe_r, p.ctx, s.strategy)
        t = Trade(p.side, p.entry_time, A.index[i], p.entry_px, px, abs(p.q), p.initial_stop, p.target,
                  pnl, fees, r, reason, asset=s.asset, strategy=s.strategy, mfe_r=mfe_r, mae_r=mae_r,
                  regime=p.ctx["regime"], vol=p.ctx["vol"], aligned=p.ctx["aligned"], error=err,
                  rationale=p.rationale, lesson=journal.lesson(err, r, mfe_r, reason), shadow=p.shadow)
        (shadows if p.shadow else trades).append(t)
        if learner is not None:
            learner.record(p.key, r, when=A.index[i])
        pos[k] = None

    def candidate(k: int, A: _Asset, i: int, direction: int) -> dict:
        """Everything known before a trade opens, and the learner's verdict on it."""
        s = sleeves[k]
        feats = {name: arr[i - 1] for name, arr in A.feats.items()}
        ctx = journal.context(direction, A.c[i - 1], feats)
        key = (learner.keys(s.strategy, direction, ctx, asset=s.asset, time=A.index[i], feats=feats)
               if learner is not None else [])
        verdict = learner.judge(key) if learner is not None else journal.Verdict(False, "")
        pred = key.get("pred") if isinstance(key, dict) else None
        return {"k": k, "A": A, "i": i, "dir": direction, "feats": feats, "ctx": ctx, "key": key,
                "verdict": verdict, "score": pred[1] if pred else 0.0}

    def open_(c_: dict) -> None:
        nonlocal cash
        k, A, i, direction = c_["k"], c_["A"], c_["i"], c_["dir"]
        feats, ctx, key, verdict = c_["feats"], c_["ctx"], c_["key"], c_["verdict"]
        s = sleeves[k]
        c, rule = costs[s.asset], s.exit_rule
        slip, fee = c.slippage_bps / 1e4, c.fee_bps / 1e4
        px = A.o[i] * (1 + direction * slip)
        dist = rule.stop_atr * A.atr[i - 1]
        strong = rule.adaptive and np.isfinite(feats["adx"]) and feats["adx"] >= rule.adx_threshold
        rr = rule.rr_strong if strong else rule.rr

        net, grs, open_risk = marked_value()
        eq = cash + net
        size = cfg.risk_pct * eq / dist
        if not verdict.skip:
            size *= verdict.size
            size = min(size, max(0.0, cfg.max_gross * eq - grs) / (px * (1 + fee)))
            if cfg.max_open_risk is not None:
                size = min(size, max(0.0, cfg.max_open_risk * eq - open_risk) / dist)
            if size * px < 1e-6 * eq:
                return  # no room left in the account
        p = _Position()
        p.side, p.q, p.entry_px, p.dist = direction, direction * size, px, dist
        p.stop = p.initial_stop = px - direction * dist
        p.target = None if rr is None else px + direction * rr * dist
        p.extreme = p.best = p.worst = px
        p.entry_row, p.entry_time = i, A.index[i]
        p.fees = size * px * fee
        p.ctx, p.key, p.shadow = ctx, key, verdict.skip
        p.rationale = journal.rationale(s.asset, s.strategy, direction, ctx, px, p.stop, p.target,
                                        size * dist, rr)
        if verdict.skip:
            p.rationale = verdict.reason + " Would have been: " + p.rationale
        else:
            cash -= p.q * px + p.fees
        pos[k] = p

    halted, peak = False, cfg.initial_capital
    for j in range(n):
        if j > 0 and cash < 0:
            cash += cash * cfg.financing_apr * (tsecs[j] - tsecs[j - 1]) / (365 * 86400)
        live = [(a, A, rows[a][j]) for a, A in assets.items() if rows[a][j] >= 0]

        # 1) exits at the open: borrow cost, brake, events, reversals, gaps through stop / target
        wants: dict[int, int] = {}
        for a, A, i in live:
            for k in by_asset[a]:
                s, p = sleeves[k], pos[k]
                c = costs[a]
                if p is not None and p.side < 0 and A.seen:
                    cost = abs(p.q) * A.c[i - 1] * c.short_borrow_apr * (A.secs[i] - A.secs[i - 1]) / (365 * 86400)
                    if not p.shadow:
                        cash -= cost
                    p.fees += cost
                want = sig[k][i - 1] if A.seen else 0
                if halted:  # brake pulled: flat for good
                    want = 0
                    if p is not None:
                        close(k, A, i, A.o[i], "brake")
                        p = None
                if A.blocked[i]:  # scheduled event: be flat through this bar
                    want = 0
                    if p is not None:
                        close(k, A, i, A.o[i], "event")
                        p = None
                if p is not None and want == -p.side:
                    close(k, A, i, A.o[i], "reverse")
                    p = None
                if p is not None:
                    stop_reason = "stop" if p.stop == p.initial_stop else "trail"
                    if p.side * (A.o[i] - p.stop) <= 0:
                        close(k, A, i, A.o[i], stop_reason)
                    elif p.target is not None and p.side * (A.o[i] - p.target) >= 0:
                        close(k, A, i, A.o[i], "target")
                wants[k] = want

        # 2) entries: every candidate of this bar, best expected result first (a quant fund
        #    ranks its opportunities; the risk budget goes to the best ones)
        cands = [candidate(k, A, i, wants[k]) for a, A, i in live for k in by_asset[a]
                 if pos[k] is None and wants.get(k, 0) != 0 and np.isfinite(A.atr[i - 1]) and A.atr[i - 1] > 0]
        for c_ in sorted(cands, key=lambda c_: (c_["verdict"].skip, -c_["score"])):
            open_(c_)

        # 3) during the bar: stops, targets, time stops; then trailing stops on the close
        for a, A, i in live:
            for k in by_asset[a]:
                s, p = sleeves[k], pos[k]
                if p is not None:
                    sd = p.side
                    p.best = max(p.best, A.h[i]) if sd > 0 else min(p.best, A.l[i])
                    p.worst = min(p.worst, A.l[i]) if sd > 0 else max(p.worst, A.h[i])
                    adverse, favorable = (A.l[i], A.h[i]) if sd > 0 else (A.h[i], A.l[i])
                    stop_reason = "stop" if p.stop == p.initial_stop else "trail"
                    rule = s.exit_rule
                    if sd * (adverse - p.stop) <= 0:
                        close(k, A, i, p.stop, stop_reason)
                    elif p.target is not None and sd * (favorable - p.target) >= 0:
                        close(k, A, i, p.target, "target")
                    elif rule.max_bars is not None and i - p.entry_row + 1 >= rule.max_bars:
                        close(k, A, i, A.c[i], "time")
                p = pos[k]
                if p is not None and s.exit_rule.trail_atr is not None and np.isfinite(A.atr[i]):
                    p.extreme = max(p.extreme, A.c[i]) if p.side > 0 else min(p.extreme, A.c[i])
                    new_stop = p.extreme - p.side * s.exit_rule.trail_atr * A.atr[i]
                    p.stop = max(p.stop, new_stop) if p.side > 0 else min(p.stop, new_stop)
        for a, A, i in live:
            A.mark = A.c[i]
            A.seen = True
        if j == n - 1 and close_at_end:  # close everything at the end of the window
            for k, p in pos.items():
                if p is not None:
                    A = assets[sleeves[k].asset]
                    i = int(np.searchsorted(A.index, timeline[j], side="right")) - 1
                    close(k, A, i, A.c[i], "end")
        net, grs, _ = marked_value()
        equity[j] = cash + net
        peak = max(peak, equity[j])
        if cfg.brake is not None and equity[j] < peak * (1 - cfg.brake):
            halted = True
        gross[j] = grs / equity[j] if equity[j] > 0 else np.nan
        net_side[j] = np.sign(sum(p.q for p in pos.values() if p is not None and not p.shadow))

    open_positions = [
        {"asset": sleeves[k].asset, "strategy": sleeves[k].strategy, "side": p.side, "qty": abs(p.q),
         "entry_time": p.entry_time, "entry": p.entry_px, "stop": p.stop, "target": p.target,
         "mark": assets[sleeves[k].asset].mark, "shadow": p.shadow, "rationale": p.rationale,
         "unrealised_r": (assets[sleeves[k].asset].mark - p.entry_px) * p.side / p.dist}
        for k, p in pos.items() if p is not None
    ]
    return PortfolioResult(pd.Series(equity, timeline, name="equity"), trades, shadows,
                           pd.Series(gross, timeline, name="gross"), pd.Series(net_side, timeline), learner,
                           open_positions)
