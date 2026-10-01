"""The multi-asset trading system: universe, costs, strategies and risk.

Shared by the portfolio backtest (`portfolio_run`) and paper trading
(`paper`), so both run exactly the same rules.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data, journal
from .engine import Costs, ExitRule
from .metrics import equity_stats
from .portfolio import PortfolioConfig, PortfolioResult, Sleeve, run_portfolio
from .strategies import INTRADAY_STRATEGIES, STRATEGIES, daily_trend, news_momentum, with_trend

# Higher-volatility universe: three cryptos, two high-beta tech stocks, and
# precious metals (silver is ~1.5x as volatile as gold) for diversification.
UNIVERSE = ("BTC", "ETH", "SOL", "NVDA", "TSLA", "GOLD", "SILVER")
# Wider universe: more candidate trades for the ML learner to choose from, and
# more trading during the day (liquid large caps, index / bond / oil ETFs).
UNIVERSE_WIDE = UNIVERSE + data.WIDE_STOCKS + data.WIDE_ETFS
# Global: plus Asia and Europe through New York (country ETFs, ADRs of TSMC, ASML, SAP...).
UNIVERSE_GLOBAL = UNIVERSE_WIDE + data.GLOBAL_ETFS + data.GLOBAL_ADRS
UNIVERSES = {"core": UNIVERSE, "wide": UNIVERSE_WIDE, "global": UNIVERSE_GLOBAL}

# Per side, on every fill, at the broker we trade on (Alpaca, lowest volume tier):
# crypto 0.25% taker fee (market and stop orders take liquidity), stocks and ETFs
# commission-free plus ~0.2 bp of regulatory fees (SEC / FINRA, on sells).
# Shorts pay a yearly borrow / funding rate.
COSTS = {
    "BTC": Costs(fee_bps=25, slippage_bps=5, short_borrow_apr=0.10),
    "ETH": Costs(fee_bps=25, slippage_bps=5, short_borrow_apr=0.10),
    "SOL": Costs(fee_bps=25, slippage_bps=10, short_borrow_apr=0.10),
    "NVDA": Costs(fee_bps=0.2, slippage_bps=3, short_borrow_apr=0.01),
    "TSLA": Costs(fee_bps=0.2, slippage_bps=3, short_borrow_apr=0.01),
    "GOLD": Costs(fee_bps=0.2, slippage_bps=2, short_borrow_apr=0.01),
    "SILVER": Costs(fee_bps=0.2, slippage_bps=3, short_borrow_apr=0.01),
    "SPY": Costs(fee_bps=0.2, slippage_bps=1),
} | {a: Costs(fee_bps=0.2, slippage_bps=3, short_borrow_apr=0.01) for a in data.WIDE_STOCKS} \
  | {a: Costs(fee_bps=0.2, slippage_bps=2, short_borrow_apr=0.01) for a in data.WIDE_ETFS} \
  | {a: Costs(fee_bps=0.2, slippage_bps=3, short_borrow_apr=0.01) for a in data.GLOBAL_ETFS} \
  | {a: Costs(fee_bps=0.2, slippage_bps=4, short_borrow_apr=0.02) for a in data.GLOBAL_ADRS}

# One exit rule per strategy, fixed in advance (from the BTC/gold study, so
# out-of-sample for every other asset). "4:2 normally, 6:2 in strong trends"
# for the two signal types with a natural target; the squeeze breakout lets
# winners run with a trailing stop.
SLEEVE_RULES = {
    "donchian_trend": ExitRule(stop_atr=2.5, rr=2.0, rr_strong=3.0, adaptive=True),
    "squeeze_breakout": ExitRule(stop_atr=3.0, rr=None, trail_atr=4.0),
    "rsi2_reversion": ExitRule(stop_atr=2.5, rr=2.0, rr_strong=3.0, adaptive=True),
    "news_momentum": ExitRule(stop_atr=2.5, rr=2.0, rr_strong=3.0, adaptive=True),
    # hourly-native: out by the end of the day (opening range) / within 6 hours (VWAP)
    "opening_range": ExitRule(stop_atr=1.5, rr=2.0, max_bars=5),
    "vwap_reversion": ExitRule(stop_atr=2.0, rr=1.5, max_bars=6),
}

TARGET_VOL = 0.20  # yearly volatility the account is sized for ("higher volatility")
MAX_GROSS = 2.0  # up to 2x notional / equity
MAX_OPEN_RISK = 0.15  # at most 15% of equity at risk across open trades
MAX_RISK_PCT = 0.03  # never more than 3% of equity on one trade

VARIANTS = {
    "long only": dict(allow_short=False, learn=False),
    "long only + learner": dict(allow_short=False, learn=True),
    "long/short": dict(allow_short=True, learn=False),
    "long/short + learner": dict(allow_short=True, learn=True),
    # News: the learner also judges news tone/coverage, upcoming events and AI views,
    # and a fourth strategy trades news bursts.
    "long/short + learner + news": dict(allow_short=True, learn=True, news=True),
}
# Upgrades, tested against the variants above. Options:
#   trend     intraday bars: only trade in the direction of the daily trend
#   blackout  intraday bars: be flat through scheduled events (earnings, Fed, jobs)
#   ml        the machine-learning learner (algo/ml.py) instead of the rule learner
#   sizing    ML only: bet more on trades with a higher expected result
#   brake     stop trading for good after this drawdown from the peak (e.g. 0.10)
#   intraday  add the hourly-native strategies (opening range breakout, VWAP reversion)
#   universe  "wide": 22 assets instead of 7 (set per account / study, see UNIVERSES)
UPGRADES = {
    "L/S + news + trend": dict(allow_short=True, learn=True, news=True, trend=True),
    "L/S + news + blackout": dict(allow_short=True, learn=True, news=True, blackout=True),
    "L/S + news + trend + blackout": dict(allow_short=True, learn=True, news=True, trend=True, blackout=True),
    "L/S + news + ML": dict(allow_short=True, learn=True, news=True, ml=True),
    "L/S + news + trend + blackout + ML": dict(allow_short=True, learn=True, news=True, trend=True, blackout=True,
                                              ml=True),
    "L/S + news + trend + blackout + ML sizing": dict(allow_short=True, learn=True, news=True, trend=True,
                                                     blackout=True, ml=True, sizing=True),
    "long + trend + blackout + intraday + ML": dict(allow_short=False, learn=True, news=True, trend=True,
                                                    blackout=True, intraday=True, ml=True),
    "L/S + trend + blackout + intraday + ML": dict(allow_short=True, learn=True, news=True, trend=True,
                                                   blackout=True, intraday=True, ml=True),
    "long + trend + blackout + ML + brake 10%": dict(allow_short=False, learn=True, news=True, trend=True,
                                                     blackout=True, ml=True, brake=0.10),
    "long + trend + blackout + ML + global": dict(allow_short=False, learn=True, news=True, trend=True,
                                                  blackout=True, ml=True, **{"global": True}),
    "long + trend + blackout + intraday + ML + global": dict(allow_short=False, learn=True, news=True, trend=True,
                                                             blackout=True, intraday=True, ml=True,
                                                             **{"global": True}),
    "long + trend + blackout + ML": dict(allow_short=False, learn=True, news=True, trend=True, blackout=True,
                                         ml=True),
}
ALL_VARIANTS = VARIANTS | UPGRADES
OPTIONS = ("trend", "blackout", "ml", "sizing", "intraday", "brake")
# Context options (what data the variant reads), not run_system arguments:
#   global    the ML also sees how Asia and Europe moved on their last finished day
NEWS_VIEWS = ("setup", "news", "event", "ai")


def load_prices(source: str = "auto", interval: str = "1d", assets=UNIVERSE,
                start: str | None = None) -> dict[str, pd.DataFrame]:
    """start: drop older bars (an account's fixed history start, so its replays stay the same)."""
    out = {a: data.load(a, source, interval=interval) for a in assets}
    if start is not None:
        out = {a: df[df.index >= pd.Timestamp(start)] for a, df in out.items()}
    return out


def intraday(prices: dict[str, pd.DataFrame]) -> bool:
    idx = next(iter(prices.values())).index
    return bool((idx != idx.normalize()).any())


def build_sleeves(prices: dict[str, pd.DataFrame], allow_short: bool, context: dict | None = None,
                  news: bool = False, trend: bool = False, intraday_strats: bool = False) -> list[Sleeve]:
    out = [Sleeve(asset, name, fn(prices[asset]), SLEEVE_RULES[name], allow_short)
           for asset in prices for name, fn in STRATEGIES.items()]
    if intraday_strats and intraday(prices):
        out += [Sleeve(asset, name, fn(prices[asset]), SLEEVE_RULES[name], allow_short)
                for asset in prices for name, fn in INTRADAY_STRATEGIES.items()
                if not (name == "opening_range" and asset in data.CRYPTO)]
    if news and context:
        out += [Sleeve(a, "news_momentum", news_momentum(prices[a], context[a]), SLEEVE_RULES["news_momentum"],
                       allow_short) for a in prices
                if a in context and "tone_z" in context[a] and context[a]["tone_z"].notna().any()]
    if trend and intraday(prices):
        tr = {a: daily_trend(df) for a, df in prices.items()}
        out = [Sleeve(s.asset, s.strategy, with_trend(s.signals, tr[s.asset]), s.exit_rule, s.allow_short)
               for s in out]
    return out


def build_context(prices: dict[str, pd.DataFrame], news_data: dict, ai_bias: pd.DataFrame | None = None) -> dict:
    """Point-in-time news, event and AI features for every bar of every asset."""
    from . import news as news_mod

    ctx = {}
    for a, df in prices.items():
        parts = [news_mod.event_features(df.index, news_data["earnings"].get(a, []), news_data["fomc"],
                                         news_data["jobs"])]
        if a in news_data["gdelt"]:
            parts.append(news_mod.news_features(news_data["gdelt"][a], df.index))
        if ai_bias is not None and a in ai_bias.columns:
            # a view written on day D is used from the next bar after D
            b = ai_bias[a].dropna()
            b.index = b.index + pd.Timedelta(days=1)
            # carried forward for up to 5 days (a count of bars would be 5 hours on hourly bars)
            parts.append(b.reindex(df.index, method="ffill", tolerance=pd.Timedelta(days=5))
                         .rename("ai_bias").to_frame())
        if (df.index != df.index.normalize()).any():  # intraday: daily trend and event blackout
            parts.append(daily_trend(df).rename("daily_trend").to_frame())
            if "global" in news_data:  # only when the 'global' option asked for it
                parts.append(news_mod.global_features(df.index, news_data["global"]))
            if a in news_data.get("alpaca_news", {}):
                parts.append(news_mod.alpaca_news_features(news_data["alpaca_news"][a], df.index,
                                                           pd.Timedelta(hours=1)))
            parts.append(news_mod.blackout(df.index, news_data["earnings"].get(a, []), news_data["fomc"],
                                           news_data["jobs"], stock=a not in data.CRYPTO).rename("blackout")
                         .to_frame())
        ctx[a] = pd.concat(parts, axis=1)
    return ctx


def bars_per_year(index: pd.DatetimeIndex) -> float:
    years = (index[-1] - index[0]).total_seconds() / (365.25 * 86400)
    return len(index) / years


def new_learner(learn: bool, news: bool = False, ml: bool = False, sizing: bool = False, prices=None,
                context=None, **_):
    """The rule learner, or the ML learner trained on the shared pool of every
    strategy's outcomes on these prices (the same pool for every account)."""
    if not learn:
        return None
    if ml:
        from .ml import MLLearner, build_pool

        return MLLearner(sizing=sizing, pool=build_pool(prices, context) if prices is not None else None)
    return journal.Learner(views=NEWS_VIEWS if news else ("setup",))


def blackout_masks(context: dict | None) -> dict | None:
    if not context:
        return None
    return {a: c["blackout"] for a, c in context.items() if "blackout" in c}


def run_system(prices, allow_short: bool, learn: bool, risk_pct: float, start=None, end=None,
               initial_capital: float = 100_000.0, close_at_end: bool = True,
               learner=None, news: bool = False, context: dict | None = None,
               trend: bool = False, blackout: bool = False, ml: bool = False,
               sizing: bool = False, intraday: bool = False, brake: float | None = None) -> PortfolioResult:
    if learner is None and learn:
        learner = new_learner(learn, news, ml, sizing, prices=prices, context=context)
    cfg = PortfolioConfig(initial_capital=initial_capital, risk_pct=risk_pct, max_gross=MAX_GROSS,
                          max_open_risk=MAX_OPEN_RISK, learner=learner if learn else None,
                          brake=brake or None)
    ctx = context if (news or ml) else None  # the ML learner uses news / event features too
    return run_portfolio(prices, build_sleeves(prices, allow_short, context if news else None, news, trend,
                                               intraday),
                         COSTS, cfg, start, end, close_at_end=close_at_end, context=ctx,
                         blocked=blackout_masks(context) if blackout else None)


def run_variant(prices, v: dict, risk_pct: float, start=None, end=None, context: dict | None = None,
                **kw) -> PortfolioResult:
    """run_system with a variant's settings (a dict from ALL_VARIANTS)."""
    return run_system(prices, v["allow_short"], v["learn"], risk_pct, start, end, news=v.get("news", False),
                      context=context, **{o: v.get(o, False) for o in OPTIONS}, **kw)


def calibrate_risk(prices, allow_short: bool, learn: bool, start, end, target_vol: float = TARGET_VOL,
                   news: bool = False, context: dict | None = None, **opts) -> float:
    """Risk per trade that gives `target_vol` yearly volatility on the
    calibration window (training data only). The brake is left out: once pulled it
    stops trading, which would fake low volatility and inflate the risk."""
    opts.pop("brake", None)
    risk = 0.01
    for _ in range(3):  # a few rounds because the leverage cap is not linear
        eq = run_system(prices, allow_short, learn, risk, start, end, news=news, context=context, **opts).equity
        vol = equity_stats(eq, bars_per_year(eq.index))["volatility"]
        if not np.isfinite(vol) or vol <= 0:
            break
        risk = float(np.clip(risk * target_vol / vol, 0.001, MAX_RISK_PCT))
    return risk


def random_sleeves(prices, allow_short: bool, seed: int, context: dict | None = None,
                   news: bool = False) -> list[Sleeve]:
    """Same sleeves, exits and signal frequency, but entries at random.
    The skill test: a real strategy must beat this, not just buy & hold."""
    rng = np.random.default_rng(seed)
    out = []
    for s in build_sleeves(prices, allow_short, context, news):
        real = s.signals.reindex(prices[s.asset].index).fillna(0)
        fire = rng.random(len(real)) < (real != 0).mean()
        side = np.where(rng.random(len(real)) < 0.5, 1, -1) if allow_short else 1
        out.append(Sleeve(s.asset, s.strategy, pd.Series(np.where(fire, side, 0), real.index), s.exit_rule,
                          allow_short))
    return out


def run_random(prices, allow_short: bool, risk_pct: float, seed: int, start=None, end=None,
               blocked: dict | None = None) -> PortfolioResult:
    cfg = PortfolioConfig(risk_pct=risk_pct, max_gross=MAX_GROSS, max_open_risk=MAX_OPEN_RISK)
    return run_portfolio(prices, random_sleeves(prices, allow_short, seed), COSTS, cfg, start, end, blocked=blocked)
