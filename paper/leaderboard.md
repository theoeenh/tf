# Leaderboard – 2026-10-05 14:06 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| random entries, long only (avg of 5) | +1.35% | -3.28% | 33 | 59% | +0.16 | 0 | 0 |
| long + trend + blackout + intraday + ML + global | -0.77% | -1.28% | 14 | 43% | -0.00 | 7 | 13 |
| L/S + trend + blackout + intraday + ML | -0.80% | -1.00% | 10 | 30% | -0.02 | 10 | 33 |
| long only | -1.23% | -2.93% | 9 | 11% | -1.02 | 11 | 0 |
| L/S + news + trend + blackout + ML | -1.23% | -1.23% | 10 | 20% | -0.21 | 8 | 20 |
| long + trend + blackout + intraday + ML + insider | -1.31% | -1.31% | 10 | 30% | -0.17 | 8 | 17 |
| long + trend + blackout + ML + global | -1.60% | -1.90% | 12 | 33% | -0.15 | 6 | 7 |
| L/S + news + trend + blackout + ML sizing | -1.84% | -1.88% | 10 | 20% | -0.21 | 6 | 20 |
| L/S + news + ML | -1.87% | -2.03% | 5 | 0% | -1.16 | 10 | 24 |
| long + trend + blackout + intraday + ML | -2.09% | -2.09% | 9 | 22% | -0.38 | 7 | 18 |
| long + trend + blackout + ML + brake 10% | -2.20% | -2.20% | 9 | 22% | -0.38 | 6 | 10 |
| long + trend + blackout + ML | -2.20% | -2.20% | 9 | 22% | -0.38 | 6 | 10 |
| long + trend + blackout + ML + insider | -2.31% | -2.31% | 10 | 20% | -0.37 | 6 | 9 |
| long/short + learner | -2.54% | -2.54% | 7 | 0% | -1.10 | 11 | 21 |
| random entries, long/short (avg of 5) | -2.78% | -3.44% | 50 | 38% | -0.26 | 0 | 0 |
| long/short | -3.21% | -3.79% | 16 | 0% | -1.18 | 11 | 0 |
| L/S + news + blackout | -3.66% | -4.19% | 15 | 7% | -0.59 | 3 | 25 |
| long only + learner | -3.70% | -4.09% | 10 | 10% | -0.94 | 9 | 6 |
| L/S + news + trend + blackout | -4.31% | -4.86% | 18 | 17% | -0.66 | 8 | 10 |
| long/short + learner + news | -4.46% | -4.72% | 12 | 8% | -0.87 | 7 | 18 |
| L/S + news + trend | -4.69% | -5.31% | 13 | 8% | -1.01 | 9 | 7 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | NVDA | +0.43 | +0.43 | +0.43 | 1 | 100% | +0.43 | 0 | – |
| rsi2_reversion | QQQ | +0.10 | +0.10 | +0.10 | 1 | 100% | +0.10 | 0 | – |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.32 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +0.10 |
| rsi2_reversion | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.25 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.28 |
| squeeze_breakout | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +0.51 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| rsi2_reversion | META | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| rsi2_reversion | AAPL | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | -0.42 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| rsi2_reversion | GOOGL | -0.55 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| donchian_trend | SOL | -0.91 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | BTC | -1.72 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |

## ML learner, out of sample

Refitted 44 times. 5154 trades judged before their outcome was known.
AUC 0.54 (0.50 = no better than chance). Taken: 2295 trades, avg +0.05R. Skipped: 2859, avg -0.02R.

