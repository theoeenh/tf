# Leaderboard – 2026-11-04 14:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | -0.63% | -10.49% | 87 | 28% | -0.00 | 8 | 117 |
| long/short | -4.76% | -12.55% | 184 | 26% | -0.25 | 24 | 0 |
| long/short + learner + news | -8.79% | -10.40% | 87 | 23% | -0.34 | 13 | 209 |
| L/S + news + trend + blackout + ML | -8.83% | -10.30% | 65 | 23% | -0.35 | 5 | 154 |
| long + trend + blackout + ML + brake 10% | -9.20% | -10.37% | 53 | 19% | -0.49 | 0 | 50 |
| long + trend + blackout + ML + global | -9.36% | -10.39% | 59 | 20% | -0.51 | 3 | 45 |
| long + trend + blackout + ML + insider | -9.41% | -10.58% | 53 | 19% | -0.45 | 3 | 50 |
| long + trend + blackout + ML | -9.72% | -10.89% | 54 | 15% | -0.61 | 3 | 49 |
| long + trend + blackout + intraday + ML | -9.85% | -10.85% | 69 | 25% | -0.43 | 4 | 100 |
| L/S + news + blackout | -9.99% | -10.75% | 90 | 26% | -0.28 | 7 | 231 |
| long + trend + blackout + intraday + ML + insider | -10.15% | -11.34% | 69 | 23% | -0.44 | 3 | 100 |
| L/S + trend + blackout + intraday + ML | -10.24% | -11.97% | 82 | 27% | -0.28 | 4 | 320 |
| long + trend + blackout + intraday + ML + global | -10.36% | -11.88% | 73 | 23% | -0.47 | 4 | 99 |
| L/S + news + trend + blackout + ML sizing | -10.43% | -12.70% | 58 | 22% | -0.43 | 5 | 157 |
| L/S + news + trend + blackout | -10.78% | -12.90% | 94 | 27% | -0.29 | 7 | 126 |
| L/S + news + ML | -11.31% | -13.23% | 64 | 20% | -0.46 | 7 | 228 |
| long/short + learner | -13.73% | -13.88% | 95 | 21% | -0.43 | 14 | 198 |
| long only + learner | -16.74% | -16.74% | 58 | 10% | -0.77 | 6 | 80 |
| long only | -17.05% | -18.31% | 108 | 14% | -0.69 | 11 | 0 |
| random entries, long/short (avg of 5) | -18.03% | -18.57% | 386 | 32% | -0.29 | 0 | 0 |
| random entries, long only (avg of 5) | -20.72% | -24.86% | 224 | 21% | -0.60 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 3 | +0.75 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| squeeze_breakout | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.42 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| donchian_trend | USO | -2.41 | -0.42 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | -1.02 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -1.02 | -1.44 | 2 | 0% | -0.72 | 1 | +1.18 |
| rsi2_reversion | QQQ | +0.00 | -1.02 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| donchian_trend | TLT | -1.03 | -1.03 | -1.03 | 1 | 0% | -1.03 | 0 | – |
| rsi2_reversion | USO | -1.12 | -1.12 | -1.12 | 1 | 0% | -1.12 | 2 | +2.07 |
| rsi2_reversion | META | +0.00 | -1.16 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | AAPL | -0.21 | -1.23 | -1.31 | 4 | 25% | -0.33 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 2 | -0.45 |
| rsi2_reversion | AMZN | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | +0.00 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| donchian_trend | TSLA | -1.01 | -2.40 | -2.40 | 2 | 0% | -1.20 | 1 | +0.62 |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |
| rsi2_reversion | NVDA | +0.00 | -3.05 | -2.62 | 4 | 25% | -0.66 | 0 | – |

## ML learner, out of sample

Refitted 45 times. 5247 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2355 trades, avg +0.04R. Skipped: 2892, avg -0.03R.

