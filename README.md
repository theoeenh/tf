# tf – trading strategy research (BTC & Gold)

Backtesting toolkit to find a strategy that beats buy & hold on a
risk-adjusted basis, for bitcoin (`BTC-USD`) and gold (`GLD`).

## Quick start

```bash
pip install -r requirements.txt
python -m pytest              # engine correctness tests
python -m algo.run            # downloads data from Yahoo, writes reports/<date>-auto/report.md
```

No internet / Yahoo blocked? Put daily CSVs (`Date,Open,High,Low,Close,Volume`)
in `data/BTC.csv`, `data/GOLD.csv`, `data/SPY.csv` and run `python -m algo.run --source csv`.
`--source synthetic` runs on fake prices to check the pipeline only.

## Test plan

| Window | Use |
|---|---|
| Train: 10 years ago → 2022 | Tune the exit rule inside each exit family. |
| Test: 2023–2025, 2026 YTD | Hold-out, never used for tuning. |
| Last month | Context only: too few trades to judge anything. Use paper trading instead. |
| Walk-forward 2020–2022 | Re-tune every January on the previous 4 years; used to **pick the finalist** per asset. |
| Walk-forward 2023 → today | Same procedure, never used for any choice: **the real out-of-sample score**. |

Benchmarks: the asset's own buy & hold, a 50/50 BTC + gold buy & hold for the
portfolio, and the S&P 500 (`SPY`). Alpha is Jensen's alpha vs buy & hold.

## Rules of the engine

- $100,000 per asset (portfolio: $50k per asset), 1% of equity risked per trade, no leverage.
- Signal on the daily close → fill on the next open (no look-ahead).
- BTC is tested long-only and long/short; gold long-only. An opposite signal reverses the position.
- Initial stop = entry ∓ k·ATR(14) (= 1R). Exit families:
  - **fixed** – target at rr·R (2 ATR stop + 3:1 = "6:2").
  - **trailing** – no target, stop trails the best close by t·ATR.
  - **adaptive** – ~2:1 ("4:2") normally, 3:1 / 4:1 ("6:2" / "8:2") or no target + trailing
    when ADX(14) ≥ 25 (strong trend) at entry.
- Gaps through a level fill at the open; if a bar touches both levels the stop wins.
- Costs on every fill: BTC 10 bps fee + 5 bps slippage, GLD 1 bp + 2 bps.
  BTC shorts also pay 10%/yr borrow. Fees are reported in $ per strategy.

## Strategies (`algo/strategies.py`)

1. **donchian_trend** – breakout of the 55-day high/low, in the direction of the 200-day MA.
2. **squeeze_breakout** – Bollinger band breakout (up or down) after a volatility squeeze.
3. **rsi2_reversion** – RSI(2) < 10 in an uptrend (buy) / > 90 in a downtrend (sell).

## Multi-asset system (`algo/system.py`, `algo/portfolio.py`)

```bash
python -m algo.portfolio_run   # daily (10 years) + hourly (2 years) study -> reports/<date>-portfolio/
```

- Universe: BTC, ETH, SOL, NVDA, TSLA, gold (GLD), silver (SLV).
- One shared account; every asset runs all three strategies at once (21 "sleeves"), and on
  hourly bars a strategy can trade many times a day.
- Sized for ~20% yearly volatility (calibrated on training data), up to 2x leverage
  (6%/yr on borrowed cash), max 15% of equity at risk across open trades.
- **Skill test:** every result is compared with the same system using *random* entries.
  Beating buy & hold in a bull market proves nothing; beating the random twin does.

## Journal and learning (`algo/journal.py`)

- Every trade records its **thinking** at entry (setup, trend, ADX regime, volatility, plan, $ at risk)
  and a **diagnosis** at exit: `wrong_immediately`, `gave_back_profit`, `choppy_market`,
  `counter_trend`, `gap_through_stop`, `fees_ate_edge`, `stop_too_tight`, `normal_loss`, or `none`.
- The **learner** files each result under its setup (strategy, direction, regime, volatility,
  trend alignment). If a setup's recent trades average below -0.1R, new trades with that setup
  are skipped, but still followed without money, so a setup that starts working again is unblocked.
  It only ever uses trades that had already closed: no look-ahead.

## Paper trading (`algo/paper.py`)

```bash
python -m algo.paper init      # start a $100k paper account now (--interval 1h for hourly)
python -m algo.paper update    # fetch new bars, trade them -> paper/status.md, trades.csv, orders.json
```

Deterministic replay from the start date on complete bars only, with the learner pre-trained on
history. `paper/orders.json` holds the wanted positions with stops and targets, for a broker adapter.

## News, events and the AI analyst

- `algo/news.py`: point-in-time news for backtests. GDELT daily news tone and coverage per asset since 2017
  (day D only used from D+1), Fed decision dates (federalreserve.gov), earnings dates (Yahoo),
  jobs-report dates; live Yahoo headlines for the brief.
- The **news variant** (`long/short + learner + news`) adds a news-momentum strategy and lets the learner
  judge news tone/coverage, upcoming events and AI views, each as its own "view".
- `python -m algo.brief` writes `paper/brief.md`: events in the next 7 days, core holdings, per-asset
  prices, signals, news and headlines, and the task for the AI analyst.
- The **AI analyst** (a Claude session) reads the brief and writes `paper/ai_views/<date>.json`.
  Views are scored against what the market did next (`algo/analyst.py`) and enter the learner.
  They are **forward-only**: a language model already knows what happened after past headlines,
  so a backtest of its past calls would be fake.
- `python -m algo.daily` runs everything in order: paper update, then the brief.

## Core holdings (`algo/core.py`)

Momentum: each month hold the 5 strongest of a fixed list (big tech of end-2016, crypto, metals) by
12-month return, above their 200-day average, weighted by inverse volatility. The rule-based,
hindsight-free way of "owning NVDA in 2017". Compared with 5 random picks under the same rules.

## Layout

```
algo/data.py        download, cache and validate prices
algo/indicators.py  ATR, RSI, Bollinger, SMA
algo/strategies.py  entry signals
algo/engine.py      backtester (bracket exits, costs, sizing)
algo/metrics.py     Sharpe, Sortino, drawdown, alpha/beta, trade stats
algo/research.py    periods, exit-rule grid search, walk-forward
algo/run.py         single-asset study (BTC & gold) and its report
algo/portfolio.py   multi-asset, multi-strategy portfolio engine
algo/journal.py     trade reasoning, error diagnosis, learner
algo/system.py      universe, costs, exit rules, risk settings
algo/portfolio_run.py  multi-asset study and its report
algo/paper.py       paper trading
algo/news.py        GDELT news, Fed / earnings / jobs calendars, headlines
algo/analyst.py     AI analyst views: storage, scoring, learner input
algo/brief.py       daily brief (events ahead, news, signals, AI task)
algo/core.py        momentum core holdings
algo/daily.py       daily routine
tests/              engine & no-look-ahead tests
```

Educational research project, not investment advice.
