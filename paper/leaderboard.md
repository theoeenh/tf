# Leaderboard – 2026-10-16 13:28 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| random entries, long only (avg of 5) | -2.83% | -9.47% | 115 | 35% | -0.25 | 0 | 0 |
| L/S + trend + blackout + intraday + ML | -4.15% | -5.82% | 46 | 22% | -0.37 | 5 | 145 |
| L/S + news + trend + blackout + ML | -5.02% | -6.02% | 42 | 17% | -0.42 | 5 | 67 |
| long + trend + blackout + ML + brake 10% | -5.17% | -6.58% | 39 | 15% | -0.45 | 5 | 25 |
| long + trend + blackout + ML | -5.23% | -6.64% | 39 | 13% | -0.56 | 5 | 25 |
| L/S + news + blackout | -5.31% | -6.66% | 46 | 20% | -0.45 | 12 | 111 |
| long + trend + blackout + intraday + ML + global | -5.43% | -7.04% | 51 | 25% | -0.42 | 4 | 50 |
| long + trend + blackout + ML + insider | -6.15% | -7.04% | 41 | 12% | -0.56 | 5 | 23 |
| long + trend + blackout + ML + global | -6.21% | -7.27% | 41 | 17% | -0.49 | 3 | 23 |
| L/S + news + ML | -6.36% | -6.94% | 43 | 21% | -0.40 | 8 | 97 |
| long + trend + blackout + intraday + ML | -6.58% | -7.23% | 48 | 19% | -0.52 | 4 | 53 |
| L/S + news + trend + blackout + ML sizing | -6.66% | -7.93% | 36 | 17% | -0.49 | 6 | 69 |
| random entries, long/short (avg of 5) | -6.69% | -7.54% | 179 | 35% | -0.21 | 0 | 0 |
| long/short | -6.73% | -7.18% | 83 | 24% | -0.40 | 18 | 0 |
| long + trend + blackout + intraday + ML + insider | -7.02% | -7.59% | 48 | 17% | -0.51 | 5 | 52 |
| long/short + learner | -7.14% | -7.91% | 56 | 20% | -0.57 | 15 | 78 |
| long/short + learner + news | -7.17% | -7.17% | 41 | 17% | -0.52 | 13 | 105 |
| long only | -8.17% | -9.53% | 54 | 19% | -0.57 | 13 | 0 |
| L/S + news + trend + blackout | -9.31% | -9.31% | 47 | 11% | -0.70 | 13 | 60 |
| long only + learner | -9.46% | -9.59% | 39 | 10% | -0.72 | 10 | 34 |
| L/S + news + trend | -13.63% | -13.89% | 46 | 7% | -0.89 | 10 | 61 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +2.98 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| donchian_trend | MSFT | +1.98 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | AAPL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.93 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.33 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.31 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.98 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | META | +0.87 | -0.22 | -0.22 | 4 | 25% | -0.06 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| rsi2_reversion | QQQ | -1.02 | -0.92 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| squeeze_breakout | GOOGL | -0.96 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AMZN | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| squeeze_breakout | TSLA | -1.16 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| donchian_trend | QQQ | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | -1.39 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |
| rsi2_reversion | TSLA | -2.03 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| rsi2_reversion | NVDA | -2.03 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | -2.02 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |

## ML learner, out of sample

Refitted 44 times. 5190 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2334 trades, avg +0.04R. Skipped: 2856, avg -0.03R.

