# Leaderboard – 2026-10-07 13:24 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| random entries, long only (avg of 5) | +1.70% | -3.37% | 45 | 53% | +0.03 | 0 | 0 |
| long + trend + blackout + intraday + ML + global | +1.51% | -1.28% | 18 | 39% | -0.11 | 11 | 21 |
| L/S + trend + blackout + intraday + ML | +0.64% | -1.20% | 15 | 33% | -0.21 | 12 | 48 |
| L/S + news + trend + blackout + ML sizing | +0.62% | -1.97% | 10 | 20% | -0.32 | 9 | 27 |
| long + trend + blackout + intraday + ML + insider | +0.60% | -1.23% | 17 | 29% | -0.36 | 11 | 23 |
| L/S + news + trend + blackout + ML | +0.57% | -1.62% | 11 | 18% | -0.31 | 12 | 26 |
| long + trend + blackout + intraday + ML | -0.14% | -2.03% | 14 | 29% | -0.46 | 11 | 25 |
| long + trend + blackout + ML + global | -0.18% | -1.98% | 14 | 29% | -0.33 | 10 | 10 |
| L/S + news + ML | -0.40% | -2.44% | 11 | 27% | -0.27 | 14 | 32 |
| long + trend + blackout + ML + brake 10% | -0.42% | -2.20% | 10 | 20% | -0.48 | 12 | 14 |
| long + trend + blackout + ML | -0.44% | -2.20% | 11 | 18% | -0.56 | 11 | 13 |
| long + trend + blackout + ML + insider | -0.79% | -2.55% | 13 | 15% | -0.54 | 11 | 11 |
| long only | -1.25% | -2.93% | 15 | 20% | -0.67 | 10 | 0 |
| long/short + learner | -2.64% | -3.91% | 18 | 11% | -0.92 | 12 | 20 |
| long/short | -2.95% | -3.88% | 25 | 12% | -0.82 | 14 | 0 |
| long only + learner | -2.96% | -4.04% | 13 | 15% | -0.82 | 10 | 11 |
| long/short + learner + news | -3.64% | -4.69% | 13 | 8% | -0.92 | 8 | 32 |
| random entries, long/short (avg of 5) | -3.73% | -5.02% | 72 | 39% | -0.26 | 0 | 0 |
| L/S + news + blackout | -4.52% | -4.89% | 20 | 10% | -0.60 | 2 | 31 |
| L/S + news + trend + blackout | -4.73% | -4.73% | 21 | 14% | -0.73 | 9 | 14 |
| L/S + news + trend | -4.90% | -5.34% | 17 | 6% | -1.10 | 9 | 15 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | NVDA | +0.43 | +0.43 | +0.43 | 1 | 100% | +0.43 | 0 | – |
| rsi2_reversion | QQQ | +0.10 | +0.10 | +0.10 | 1 | 100% | +0.10 | 0 | – |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.32 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +0.10 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | META | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| rsi2_reversion | AAPL | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | -0.42 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| rsi2_reversion | GOOGL | -0.55 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| donchian_trend | SOL | -0.91 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| squeeze_breakout | SOL | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 2 | -0.15 |
| rsi2_reversion | SOL | -1.45 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| donchian_trend | BTC | -1.72 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |

## ML learner, out of sample

Refitted 44 times. 5152 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2310 trades, avg +0.04R. Skipped: 2842, avg -0.03R.

