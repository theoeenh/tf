# Leaderboard – 2026-10-08 13:24 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| long + trend + blackout + intraday + ML + global | +0.29% | -2.84% | 24 | 33% | -0.20 | 14 | 23 |
| L/S + trend + blackout + intraday + ML | +0.09% | -2.12% | 19 | 26% | -0.23 | 13 | 55 |
| L/S + news + trend + blackout + ML sizing | +0.04% | -2.01% | 13 | 15% | -0.34 | 10 | 30 |
| L/S + news + trend + blackout + ML | -0.09% | -2.12% | 15 | 13% | -0.35 | 13 | 29 |
| random entries, long only (avg of 5) | -0.11% | -3.77% | 53 | 37% | -0.27 | 0 | 0 |
| L/S + news + ML | -0.29% | -2.44% | 15 | 20% | -0.42 | 16 | 38 |
| long + trend + blackout + intraday + ML | -1.00% | -3.23% | 19 | 21% | -0.41 | 13 | 29 |
| long only | -1.07% | -3.86% | 17 | 18% | -0.74 | 16 | 0 |
| long + trend + blackout + ML + global | -1.10% | -3.63% | 18 | 22% | -0.36 | 12 | 11 |
| long + trend + blackout + intraday + ML + insider | -1.15% | -3.14% | 20 | 20% | -0.40 | 13 | 27 |
| long + trend + blackout + ML + brake 10% | -1.27% | -3.22% | 14 | 14% | -0.48 | 14 | 15 |
| long + trend + blackout + ML | -1.28% | -3.23% | 15 | 13% | -0.54 | 13 | 14 |
| long/short | -1.65% | -3.88% | 28 | 18% | -0.67 | 17 | 0 |
| long + trend + blackout + ML + insider | -1.68% | -3.29% | 17 | 12% | -0.53 | 12 | 12 |
| long/short + learner | -2.81% | -3.91% | 21 | 14% | -0.76 | 14 | 25 |
| long only + learner | -3.41% | -4.45% | 17 | 12% | -0.74 | 11 | 14 |
| long/short + learner + news | -3.42% | -4.69% | 16 | 6% | -0.86 | 11 | 40 |
| L/S + news + blackout | -3.79% | -5.19% | 21 | 10% | -0.62 | 9 | 42 |
| random entries, long/short (avg of 5) | -3.95% | -4.89% | 73 | 37% | -0.26 | 0 | 0 |
| L/S + news + trend | -5.28% | -5.78% | 20 | 5% | -1.01 | 10 | 18 |
| L/S + news + trend + blackout | -5.90% | -5.92% | 24 | 12% | -0.70 | 10 | 18 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | NVDA | +0.43 | +0.43 | +0.43 | 1 | 100% | +0.43 | 0 | – |
| rsi2_reversion | QQQ | +0.10 | +0.10 | +0.10 | 1 | 100% | +0.10 | 0 | – |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +0.10 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.31 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| squeeze_breakout | QQQ | -0.05 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| rsi2_reversion | AAPL | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | NVDA | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | -0.42 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| rsi2_reversion | GOOGL | -0.55 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| squeeze_breakout | META | -0.70 | -0.70 | -0.70 | 1 | 0% | -0.70 | 0 | – |
| donchian_trend | SOL | -0.91 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| rsi2_reversion | META | -1.09 | -1.09 | -1.09 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | SOL | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 2 | -0.15 |
| rsi2_reversion | SOL | -1.45 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| donchian_trend | BTC | -1.72 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |

## ML learner, out of sample

Refitted 44 times. 5157 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2306 trades, avg +0.04R. Skipped: 2851, avg -0.03R.

