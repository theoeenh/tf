# Leaderboard – 2026-10-21 13:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + trend + blackout + intraday + ML | -4.30% | -6.28% | 53 | 26% | -0.28 | 2 | 191 |
| L/S + news + trend + blackout + ML | -6.08% | -6.99% | 48 | 19% | -0.41 | 1 | 85 |
| long + trend + blackout + ML + brake 10% | -6.31% | -7.52% | 44 | 16% | -0.44 | 2 | 31 |
| random entries, long only (avg of 5) | -6.42% | -11.83% | 136 | 31% | -0.35 | 0 | 0 |
| long + trend + blackout + intraday + ML + insider | -6.85% | -8.08% | 54 | 20% | -0.44 | 2 | 67 |
| long + trend + blackout + intraday + ML | -6.99% | -8.49% | 55 | 20% | -0.47 | 2 | 69 |
| long + trend + blackout + ML | -7.05% | -8.25% | 44 | 14% | -0.54 | 2 | 31 |
| long + trend + blackout + ML + global | -7.18% | -8.03% | 44 | 20% | -0.40 | 1 | 31 |
| long + trend + blackout + ML + insider | -7.42% | -8.62% | 44 | 14% | -0.54 | 2 | 32 |
| L/S + news + trend + blackout + ML sizing | -7.44% | -8.86% | 41 | 20% | -0.42 | 3 | 89 |
| L/S + news + blackout | -7.87% | -8.40% | 60 | 20% | -0.44 | 8 | 137 |
| long + trend + blackout + intraday + ML + global | -8.13% | -9.98% | 60 | 27% | -0.38 | 2 | 60 |
| L/S + news + ML | -9.31% | -9.85% | 51 | 22% | -0.41 | 3 | 132 |
| long/short + learner + news | -9.91% | -10.47% | 55 | 16% | -0.55 | 8 | 133 |
| L/S + news + trend + blackout | -9.96% | -10.74% | 57 | 14% | -0.60 | 10 | 73 |
| long/short + learner | -10.39% | -11.33% | 75 | 19% | -0.57 | 13 | 98 |
| long/short | -11.13% | -12.38% | 112 | 21% | -0.50 | 20 | 0 |
| long only | -11.27% | -13.41% | 69 | 17% | -0.62 | 9 | 0 |
| long only + learner | -12.29% | -12.84% | 49 | 12% | -0.70 | 5 | 41 |
| random entries, long/short (avg of 5) | -12.46% | -12.86% | 229 | 33% | -0.27 | 0 | 0 |
| L/S + news + trend | -13.51% | -15.04% | 52 | 10% | -0.81 | 10 | 79 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| donchian_trend | USO | +1.99 | +1.99 | +1.99 | 1 | 100% | +1.99 | 1 | -1.01 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | -1.36 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.98 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 1 | +0.28 |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| rsi2_reversion | QQQ | +0.00 | -0.92 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| squeeze_breakout | GOOGL | -0.96 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AMZN | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 1 | -1.93 |
| rsi2_reversion | AAPL | -1.02 | -1.10 | -1.10 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | META | -2.12 | -1.23 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | -1.02 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 2 | -1.06 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| rsi2_reversion | NVDA | -1.02 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |

## ML learner, out of sample

Refitted 44 times. 5203 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2337 trades, avg +0.03R. Skipped: 2866, avg -0.03R.

