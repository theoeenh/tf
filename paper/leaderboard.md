# Leaderboard – 2026-11-25 14:26 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | +5.53% | -11.05% | 129 | 28% | -0.05 | 21 | 217 |
| long/short | -0.14% | -14.77% | 335 | 31% | -0.06 | 28 | 0 |
| long/short + learner + news | -5.18% | -10.22% | 141 | 26% | -0.17 | 14 | 348 |
| long/short + learner | -7.14% | -14.71% | 185 | 29% | -0.11 | 18 | 298 |
| L/S + news + trend + blackout | -7.97% | -10.70% | 117 | 25% | -0.30 | 18 | 272 |
| long + trend + blackout + ML + brake 10% | -9.56% | -10.41% | 47 | 13% | -0.62 | 0 | 45 |
| L/S + trend + blackout + intraday + ML | -12.74% | -15.64% | 115 | 28% | -0.30 | 2 | 578 |
| long + trend + blackout + intraday + ML + insider | -13.43% | -15.39% | 87 | 23% | -0.44 | 1 | 131 |
| long + trend + blackout + ML + insider | -13.70% | -14.47% | 62 | 15% | -0.67 | 1 | 75 |
| long + trend + blackout + ML | -14.38% | -15.55% | 64 | 14% | -0.66 | 1 | 70 |
| L/S + news + ML | -14.73% | -15.57% | 85 | 21% | -0.47 | 2 | 400 |
| L/S + news + trend + blackout + ML | -14.85% | -16.60% | 91 | 23% | -0.44 | 2 | 301 |
| long + trend + blackout + ML + global | -14.85% | -15.63% | 70 | 16% | -0.64 | 0 | 65 |
| long + trend + blackout + intraday + ML + global | -14.88% | -16.38% | 86 | 27% | -0.48 | 0 | 134 |
| L/S + news + trend + blackout + ML sizing | -15.09% | -17.32% | 83 | 24% | -0.46 | 2 | 301 |
| L/S + news + blackout | -16.64% | -18.06% | 134 | 25% | -0.39 | 18 | 406 |
| long + trend + blackout + intraday + ML | -17.21% | -18.79% | 85 | 20% | -0.58 | 1 | 137 |
| long only + learner | -25.05% | -25.26% | 102 | 11% | -0.74 | 2 | 95 |
| random entries, long/short (avg of 5) | -28.23% | -28.53% | 694 | 34% | -0.22 | 0 | 0 |
| long only | -28.56% | -30.03% | 166 | 13% | -0.73 | 5 | 0 |
| random entries, long only (avg of 5) | -38.58% | -42.75% | 398 | 18% | -0.64 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| donchian_trend | AMD | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 1 | -1.00 |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | NVDA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | QQQ | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| rsi2_reversion | AMD | +0.00 | +0.00 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| rsi2_reversion | META | +0.00 | +0.00 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | AVGO | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 1 | -1.01 |
| rsi2_reversion | AMZN | +0.00 | +0.00 | -2.22 | 2 | 0% | -1.11 | 5 | -0.12 |
| squeeze_breakout | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | NVDA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.15 |
| squeeze_breakout | QQQ | +0.00 | +0.00 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.75 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | TSLA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.95 |
| rsi2_reversion | QQQ | +0.00 | +0.00 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| rsi2_reversion | NVDA | +0.00 | +0.00 | -1.61 | 3 | 33% | -0.54 | 1 | -1.02 |
| rsi2_reversion | SOL | +0.00 | +0.00 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| squeeze_breakout | META | +0.00 | +0.00 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | GOOGL | +0.00 | +0.00 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| squeeze_breakout | AMZN | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.16 |
| squeeze_breakout | AMD | +0.00 | +0.00 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | +0.00 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | +0.00 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| rsi2_reversion | TLT | +0.00 | -0.03 | -0.03 | 2 | 50% | -0.02 | 2 | -0.76 |
| squeeze_breakout | USO | +0.00 | -0.05 | -0.20 | 2 | 0% | -0.10 | 1 | +0.28 |
| rsi2_reversion | AAPL | +0.00 | -0.21 | -1.31 | 4 | 25% | -0.33 | 1 | +0.22 |
| donchian_trend | TSLA | +0.00 | -1.01 | -2.40 | 2 | 0% | -1.20 | 1 | +0.62 |
| rsi2_reversion | MSFT | +0.00 | -1.01 | -2.51 | 3 | 0% | -0.84 | 2 | +0.84 |
| donchian_trend | MSFT | +0.00 | -1.01 | +0.97 | 2 | 50% | +0.49 | 1 | -1.02 |
| rsi2_reversion | XOM | +0.00 | -1.01 | +1.97 | 2 | 50% | +0.98 | 3 | +0.75 |
| rsi2_reversion | IWM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 1 | -1.01 |
| squeeze_breakout | JPM | +0.00 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | +0.00 | -1.02 | -3.16 | 3 | 0% | -1.05 | 1 | -1.93 |
| rsi2_reversion | USO | +0.00 | -1.12 | -1.12 | 1 | 0% | -1.12 | 3 | +0.86 |
| donchian_trend | USO | +0.00 | -2.41 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| rsi2_reversion | TSLA | +0.00 | -2.46 | -4.49 | 4 | 0% | -1.12 | 3 | -0.64 |
| donchian_trend | TLT | +0.00 | -2.67 | -2.67 | 2 | 0% | -1.34 | 1 | -0.23 |
| rsi2_reversion | JPM | +0.00 | -3.90 | -3.90 | 3 | 0% | -1.30 | 2 | +1.82 |

## ML learner, out of sample

Refitted 45 times. 5277 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2357 trades, avg +0.04R. Skipped: 2920, avg -0.03R.

