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
| Train: 10 years ago → 2022 | Tune the exit rule (stop width in ATR × reward:risk). Nothing else is tuned. |
| Test: 2023–2025 | Hold-out. Never used for tuning. |
| 2026 YTD | Second hold-out. |
| Last month | Shown only for context: too few trades to judge anything. Use paper trading instead. |
| Walk-forward 2020 → today | Re-tune every year on the previous 4 years, trade the next year. The most honest estimate. |

Benchmarks: the asset's own buy & hold, and the S&P 500 (`SPY`). Alpha is
Jensen's alpha vs the asset's buy & hold.

## Rules of the engine

- $100,000 per asset, 1% of equity risked per trade, long only, no leverage.
- Signal on the daily close → fill on the next open (no look-ahead).
- Stop = entry − k·ATR(14), target = entry + rr·k·ATR(14).
- Gaps through a level fill at the open; if a bar touches both levels the stop wins.
- Costs per side: BTC 10 bps fee + 5 bps slippage, GLD 1 bp + 2 bps.

## Strategies (`algo/strategies.py`)

1. **donchian_trend** – breakout above the 55-day high, above the 200-day MA.
2. **squeeze_breakout** – Bollinger band breakout after a volatility squeeze.
3. **rsi2_reversion** – RSI(2) < 10 dip inside a 200-day uptrend.

## Layout

```
algo/data.py        download, cache and validate prices
algo/indicators.py  ATR, RSI, Bollinger, SMA
algo/strategies.py  entry signals
algo/engine.py      backtester (bracket exits, costs, sizing)
algo/metrics.py     Sharpe, Sortino, drawdown, alpha/beta, trade stats
algo/research.py    periods, exit-rule grid search, walk-forward
algo/run.py         runs everything and writes the report
tests/              engine & no-look-ahead tests
```

Educational research project, not investment advice.
