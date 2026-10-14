# Leaderboard – 2026-10-14 13:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| random entries, long only (avg of 5) | -0.32% | -6.06% | 91 | 39% | -0.19 | 0 | 0 |
| long + trend + blackout + intraday + ML + global | -1.52% | -4.45% | 45 | 29% | -0.27 | 10 | 34 |
| L/S + trend + blackout + intraday + ML | -1.79% | -3.86% | 42 | 26% | -0.20 | 12 | 105 |
| L/S + news + trend + blackout + ML | -2.55% | -3.87% | 34 | 18% | -0.33 | 9 | 49 |
| long + trend + blackout + intraday + ML + insider | -2.64% | -5.10% | 42 | 24% | -0.31 | 14 | 39 |
| long + trend + blackout + intraday + ML | -2.85% | -4.72% | 37 | 22% | -0.37 | 12 | 44 |
| long + trend + blackout + ML + insider | -2.90% | -5.31% | 33 | 15% | -0.47 | 9 | 18 |
| long + trend + blackout + ML + brake 10% | -3.25% | -5.27% | 33 | 18% | -0.34 | 9 | 19 |
| L/S + news + trend + blackout + ML sizing | -3.28% | -4.69% | 29 | 21% | -0.31 | 8 | 50 |
| long + trend + blackout + ML | -3.61% | -5.31% | 33 | 15% | -0.47 | 9 | 19 |
| long only | -3.79% | -5.22% | 39 | 18% | -0.62 | 15 | 0 |
| L/S + news + ML | -4.03% | -4.64% | 35 | 23% | -0.35 | 12 | 72 |
| long/short | -4.29% | -5.24% | 63 | 21% | -0.56 | 21 | 0 |
| long + trend + blackout + ML + global | -5.05% | -6.64% | 35 | 23% | -0.33 | 9 | 18 |
| long/short + learner + news | -5.27% | -5.27% | 31 | 16% | -0.45 | 12 | 86 |
| long/short + learner | -5.41% | -7.91% | 42 | 19% | -0.58 | 13 | 64 |
| L/S + news + blackout | -5.77% | -6.66% | 32 | 12% | -0.55 | 14 | 93 |
| L/S + news + trend + blackout | -6.72% | -8.18% | 38 | 11% | -0.69 | 15 | 47 |
| random entries, long/short (avg of 5) | -7.30% | -7.74% | 151 | 36% | -0.22 | 0 | 0 |
| long only + learner | -7.49% | -7.52% | 32 | 12% | -0.66 | 10 | 28 |
| L/S + news + trend | -9.22% | -9.61% | 33 | 3% | -0.93 | 12 | 47 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +2.98 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| donchian_trend | MSFT | +1.98 | +1.98 | +1.98 | 1 | 100% | +1.98 | 0 | – |
| rsi2_reversion | META | +1.98 | +0.89 | +0.89 | 3 | 33% | +0.30 | 0 | – |
| rsi2_reversion | QQQ | +0.00 | +0.10 | +0.10 | 1 | 100% | +0.10 | 1 | -1.02 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| donchian_trend | AAPL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.93 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.31 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.98 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.33 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | NVDA | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| squeeze_breakout | AMD | -0.44 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | -0.49 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | -0.50 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 0 | – |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | AMD | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | TSLA | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| squeeze_breakout | TSLA | -1.16 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| donchian_trend | QQQ | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | -1.39 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | NVDA | -2.04 | -1.61 | -1.61 | 3 | 33% | -0.54 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |
| rsi2_reversion | AMD | -3.04 | -3.04 | -3.04 | 3 | 0% | -1.01 | 0 | – |

## ML learner, out of sample

Refitted 44 times. 5179 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2333 trades, avg +0.04R. Skipped: 2846, avg -0.03R.

