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
