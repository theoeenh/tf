# Leaderboard – 2026-10-27 13:34 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend + blackout | -5.59% | -9.81% | 65 | 28% | -0.16 | 8 | 93 |
| L/S + news + blackout | -6.37% | -6.87% | 66 | 26% | -0.30 | 9 | 171 |
| L/S + trend + blackout + intraday + ML | -6.56% | -7.90% | 67 | 27% | -0.22 | 5 | 232 |
| L/S + news + trend | -6.71% | -13.51% | 57 | 18% | -0.50 | 12 | 98 |
| long + trend + blackout + ML + global | -6.77% | -7.92% | 49 | 18% | -0.49 | 3 | 39 |
| long + trend + blackout + ML | -6.79% | -8.08% | 47 | 15% | -0.55 | 3 | 40 |
| long + trend + blackout + ML + brake 10% | -6.89% | -8.18% | 48 | 15% | -0.55 | 3 | 39 |
| long + trend + blackout + ML + insider | -7.62% | -8.58% | 50 | 14% | -0.56 | 3 | 37 |
| long/short + learner | -7.66% | -11.56% | 88 | 22% | -0.44 | 17 | 119 |
| long + trend + blackout + intraday + ML + global | -7.67% | -9.31% | 65 | 26% | -0.42 | 4 | 77 |
| long/short + learner + news | -7.86% | -10.30% | 64 | 22% | -0.36 | 11 | 158 |
| L/S + news + trend + blackout + ML | -7.93% | -8.79% | 51 | 18% | -0.45 | 1 | 110 |
| L/S + news + trend + blackout + ML sizing | -8.13% | -9.56% | 46 | 20% | -0.43 | 5 | 113 |
| long/short | -8.47% | -12.55% | 139 | 22% | -0.40 | 26 | 0 |
| long + trend + blackout + intraday + ML | -8.58% | -9.59% | 59 | 19% | -0.51 | 2 | 84 |
| long + trend + blackout + intraday + ML + insider | -9.11% | -10.55% | 59 | 17% | -0.53 | 2 | 83 |
| L/S + news + ML | -10.02% | -10.76% | 58 | 22% | -0.41 | 6 | 162 |
| random entries, long only (avg of 5) | -11.68% | -16.38% | 173 | 24% | -0.51 | 0 | 0 |
| long only | -12.73% | -14.38% | 84 | 14% | -0.71 | 10 | 0 |
| long only + learner | -12.74% | -14.02% | 57 | 12% | -0.67 | 5 | 52 |
| random entries, long/short (avg of 5) | -15.13% | -15.66% | 286 | 33% | -0.25 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 1 | +2.86 |
| donchian_trend | USO | +0.00 | +1.99 | +1.99 | 1 | 100% | +1.99 | 1 | -1.01 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | XOM | +0.32 | +0.32 | +0.32 | 1 | 100% | +0.32 | 2 | +2.98 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| rsi2_reversion | USO | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +3.45 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 1 | +0.28 |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| rsi2_reversion | QQQ | +0.00 | -0.92 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -1.10 | -1.10 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | META | +0.00 | -1.23 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | MSFT | -1.02 | -1.44 | -1.44 | 2 | 0% | -0.72 | 1 | +1.28 |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | +0.00 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | AMD | +0.00 | -2.02 | -2.02 | 2 | 0% | -1.01 | 2 | -1.37 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 1 | -1.01 |
| rsi2_reversion | AMZN | -1.02 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | -1.12 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| rsi2_reversion | NVDA | +0.00 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |

## ML learner, out of sample

Refitted 44 times. 5215 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2348 trades, avg +0.03R. Skipped: 2867, avg -0.03R.

