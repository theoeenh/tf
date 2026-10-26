# Leaderboard – 2026-10-26 13:49 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + trend + blackout + intraday + ML | -4.06% | -6.20% | 55 | 27% | -0.22 | 7 | 227 |
| L/S + news + trend + blackout + ML | -5.66% | -6.80% | 50 | 20% | -0.35 | 3 | 99 |
| long + trend + blackout + ML + brake 10% | -5.93% | -7.71% | 46 | 15% | -0.47 | 4 | 37 |
| long + trend + blackout + ML | -5.98% | -7.77% | 46 | 13% | -0.56 | 5 | 37 |
| long + trend + blackout + intraday + ML + global | -6.11% | -8.25% | 62 | 26% | -0.40 | 5 | 71 |
| long/short + learner | -6.55% | -11.56% | 87 | 22% | -0.44 | 17 | 113 |
| long/short + learner + news | -6.78% | -11.51% | 68 | 21% | -0.40 | 12 | 148 |
| long + trend + blackout + ML + global | -6.80% | -8.66% | 46 | 15% | -0.55 | 5 | 37 |
| L/S + news + trend + blackout | -6.84% | -10.74% | 65 | 22% | -0.34 | 12 | 81 |
| L/S + news + trend + blackout + ML sizing | -6.86% | -8.87% | 48 | 21% | -0.38 | 6 | 101 |
| long + trend + blackout + ML + insider | -7.23% | -8.81% | 49 | 12% | -0.58 | 5 | 34 |
| long + trend + blackout + intraday + ML + insider | -7.30% | -8.37% | 57 | 19% | -0.47 | 5 | 79 |
| long + trend + blackout + intraday + ML | -7.46% | -9.02% | 55 | 18% | -0.51 | 5 | 82 |
| L/S + news + blackout | -7.57% | -9.01% | 69 | 22% | -0.41 | 12 | 154 |
| long/short | -7.59% | -12.55% | 132 | 23% | -0.39 | 29 | 0 |
| L/S + news + trend | -8.13% | -15.04% | 60 | 17% | -0.54 | 12 | 90 |
| L/S + news + ML | -9.71% | -10.76% | 55 | 20% | -0.46 | 7 | 156 |
| random entries, long only (avg of 5) | -11.59% | -15.25% | 159 | 20% | -0.56 | 0 | 0 |
| long only + learner | -12.68% | -14.02% | 57 | 12% | -0.67 | 4 | 51 |
| long only | -12.68% | -14.38% | 83 | 14% | -0.71 | 8 | 0 |
| random entries, long/short (avg of 5) | -13.03% | -13.89% | 286 | 36% | -0.22 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| donchian_trend | USO | +0.00 | +1.99 | +1.99 | 1 | 100% | +1.99 | 1 | -1.01 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | +2.98 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
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
| donchian_trend | AAPL | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 1 | -1.93 |
| rsi2_reversion | AAPL | -1.02 | -1.10 | -1.10 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | META | +0.00 | -1.23 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | MSFT | -1.02 | -1.44 | -1.44 | 2 | 0% | -0.72 | 0 | – |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | +0.00 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 1 | -1.01 |
| rsi2_reversion | AMZN | -1.02 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| rsi2_reversion | NVDA | +0.00 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |

## ML learner, out of sample

Refitted 44 times. 5210 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2340 trades, avg +0.03R. Skipped: 2870, avg -0.03R.

