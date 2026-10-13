# Leaderboard – 2026-10-13 13:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + trend + blackout + intraday + ML | -0.88% | -4.35% | 36 | 25% | -0.17 | 15 | 96 |
| long + trend + blackout + intraday + ML + global | -1.63% | -4.45% | 37 | 27% | -0.36 | 13 | 34 |
| L/S + news + trend + blackout + ML | -1.91% | -4.17% | 28 | 18% | -0.28 | 15 | 49 |
| random entries, long only (avg of 5) | -2.11% | -7.69% | 84 | 34% | -0.28 | 0 | 0 |
| L/S + news + trend + blackout + ML sizing | -2.23% | -3.99% | 21 | 14% | -0.41 | 12 | 49 |
| long + trend + blackout + intraday + ML + insider | -2.27% | -5.10% | 35 | 23% | -0.31 | 15 | 38 |
| long only | -2.76% | -5.06% | 32 | 19% | -0.60 | 17 | 0 |
| long + trend + blackout + intraday + ML | -2.78% | -4.72% | 30 | 20% | -0.39 | 14 | 43 |
| long + trend + blackout + ML + brake 10% | -3.10% | -5.27% | 25 | 12% | -0.49 | 15 | 19 |
| long + trend + blackout + ML | -3.13% | -5.31% | 26 | 12% | -0.52 | 13 | 18 |
| L/S + news + ML | -3.35% | -4.33% | 30 | 23% | -0.31 | 16 | 71 |
| long + trend + blackout + ML + insider | -3.61% | -5.25% | 28 | 11% | -0.53 | 14 | 16 |
| long/short | -3.68% | -4.81% | 57 | 21% | -0.54 | 22 | 0 |
| long/short + learner + news | -4.38% | -5.25% | 30 | 17% | -0.43 | 8 | 78 |
| long + trend + blackout + ML + global | -4.60% | -6.60% | 30 | 13% | -0.59 | 12 | 15 |
| L/S + news + blackout | -5.69% | -6.66% | 29 | 10% | -0.59 | 14 | 86 |
| long/short + learner | -6.08% | -7.91% | 38 | 18% | -0.58 | 15 | 59 |
| long only + learner | -6.25% | -6.80% | 27 | 11% | -0.68 | 11 | 25 |
| random entries, long/short (avg of 5) | -6.92% | -7.90% | 141 | 35% | -0.25 | 0 | 0 |
| L/S + news + trend + blackout | -6.97% | -8.18% | 35 | 9% | -0.77 | 14 | 41 |
| L/S + news + trend | -8.79% | -9.07% | 30 | 3% | -0.90 | 10 | 42 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +2.98 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| rsi2_reversion | QQQ | +0.00 | +0.10 | +0.10 | 1 | 100% | +0.10 | 1 | -1.02 |
| donchian_trend | AAPL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.93 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.33 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.31 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| squeeze_breakout | QQQ | -0.05 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | NVDA | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| squeeze_breakout | AMD | -0.44 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | -0.49 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | -0.50 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| squeeze_breakout | META | -0.70 | -0.70 | -0.70 | 1 | 0% | -0.70 | 0 | – |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | AMD | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | META | -1.02 | -1.09 | -1.09 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | SOL | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| rsi2_reversion | SOL | -1.45 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | NVDA | -2.04 | -1.61 | -1.61 | 3 | 33% | -0.54 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |
| rsi2_reversion | AMD | -2.02 | -2.02 | -2.02 | 2 | 0% | -1.01 | 0 | – |

## ML learner, out of sample

Refitted 44 times. 5172 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2323 trades, avg +0.04R. Skipped: 2849, avg -0.03R.

