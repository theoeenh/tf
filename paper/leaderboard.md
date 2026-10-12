# Leaderboard – 2026-10-12 13:26 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| random entries, long only (avg of 5) | -0.57% | -6.33% | 71 | 44% | -0.11 | 0 | 0 |
| L/S + trend + blackout + intraday + ML | -1.33% | -3.86% | 29 | 21% | -0.31 | 15 | 89 |
| L/S + news + trend + blackout + ML | -1.45% | -4.17% | 25 | 16% | -0.35 | 14 | 45 |
| long + trend + blackout + intraday + ML + global | -2.09% | -4.94% | 33 | 24% | -0.37 | 13 | 34 |
| L/S + news + trend + blackout + ML sizing | -2.15% | -3.92% | 19 | 16% | -0.34 | 11 | 46 |
| long only | -2.73% | -5.06% | 28 | 14% | -0.76 | 16 | 0 |
| L/S + news + ML | -2.73% | -4.22% | 24 | 17% | -0.49 | 17 | 67 |
| long + trend + blackout + intraday + ML + insider | -3.26% | -5.17% | 28 | 11% | -0.56 | 15 | 39 |
| random entries, long/short (avg of 5) | -3.34% | -5.24% | 117 | 36% | -0.24 | 0 | 0 |
| long + trend + blackout + ML + brake 10% | -3.35% | -5.27% | 22 | 9% | -0.60 | 14 | 19 |
| long + trend + blackout + ML | -3.39% | -5.31% | 23 | 9% | -0.63 | 13 | 18 |
| long + trend + blackout + intraday + ML | -3.48% | -4.74% | 27 | 11% | -0.63 | 14 | 40 |
| long + trend + blackout + ML + insider | -3.74% | -5.25% | 25 | 8% | -0.62 | 13 | 16 |
| long/short | -4.19% | -4.81% | 48 | 17% | -0.69 | 18 | 0 |
| long + trend + blackout + ML + global | -4.73% | -6.60% | 28 | 14% | -0.56 | 11 | 14 |
| long/short + learner + news | -4.88% | -5.25% | 26 | 8% | -0.75 | 11 | 70 |
| long only + learner | -5.67% | -6.80% | 27 | 11% | -0.68 | 7 | 19 |
| L/S + news + blackout | -6.12% | -6.66% | 28 | 7% | -0.67 | 13 | 77 |
| long/short + learner | -7.55% | -7.91% | 35 | 11% | -0.82 | 13 | 50 |
| L/S + news + trend + blackout | -7.69% | -8.18% | 34 | 9% | -0.79 | 13 | 35 |
| L/S + news + trend | -8.42% | -8.99% | 28 | 0% | -1.01 | 11 | 35 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | QQQ | +0.00 | +0.10 | +0.10 | 1 | 100% | +0.10 | 1 | -1.02 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | AAPL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.93 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.31 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.33 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | QQQ | -0.05 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | NVDA | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| squeeze_breakout | AMD | -0.44 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | -0.49 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | -0.50 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| rsi2_reversion | NVDA | -1.02 | -0.59 | -0.59 | 2 | 50% | -0.30 | 0 | – |
| squeeze_breakout | META | -0.70 | -0.70 | -0.70 | 1 | 0% | -0.70 | 0 | – |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | AMD | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AMD | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | META | -1.02 | -1.09 | -1.09 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | SOL | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| rsi2_reversion | SOL | -1.45 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |

## ML learner, out of sample

Refitted 44 times. 5169 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2319 trades, avg +0.04R. Skipped: 2850, avg -0.03R.

