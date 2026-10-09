# Leaderboard – 2026-10-09 13:27 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| random entries, long only (avg of 5) | +0.96% | -4.16% | 61 | 42% | -0.19 | 0 | 0 |
| long + trend + blackout + intraday + ML + global | -1.09% | -4.02% | 30 | 27% | -0.31 | 12 | 27 |
| L/S + trend + blackout + intraday + ML | -1.54% | -3.85% | 27 | 22% | -0.31 | 13 | 65 |
| L/S + news + trend + blackout + ML | -1.69% | -3.82% | 22 | 14% | -0.38 | 13 | 34 |
| L/S + news + trend + blackout + ML sizing | -2.01% | -4.09% | 18 | 17% | -0.33 | 11 | 35 |
| long only | -2.83% | -5.06% | 25 | 12% | -0.83 | 15 | 0 |
| long/short | -2.85% | -3.88% | 38 | 18% | -0.59 | 19 | 0 |
| long + trend + blackout + intraday + ML + insider | -3.28% | -5.11% | 28 | 14% | -0.54 | 11 | 30 |
| random entries, long/short (avg of 5) | -3.35% | -6.70% | 98 | 39% | -0.19 | 0 | 0 |
| long + trend + blackout + ML + insider | -3.39% | -5.25% | 23 | 9% | -0.62 | 13 | 14 |
| L/S + news + ML | -3.39% | -4.50% | 22 | 18% | -0.47 | 15 | 50 |
| long + trend + blackout + ML + brake 10% | -3.46% | -5.27% | 21 | 10% | -0.61 | 13 | 16 |
| long + trend + blackout + ML | -3.50% | -5.31% | 22 | 9% | -0.64 | 12 | 15 |
| long + trend + blackout + intraday + ML | -3.54% | -5.24% | 24 | 8% | -0.65 | 12 | 34 |
| long + trend + blackout + ML + global | -4.38% | -6.80% | 26 | 15% | -0.52 | 12 | 11 |
| long/short + learner + news | -4.70% | -4.82% | 22 | 9% | -0.72 | 12 | 54 |
| long/short + learner | -5.51% | -5.60% | 28 | 14% | -0.70 | 15 | 37 |
| long only + learner | -6.23% | -6.80% | 24 | 8% | -0.77 | 9 | 16 |
| L/S + news + blackout | -6.69% | -7.03% | 26 | 8% | -0.69 | 11 | 58 |
| L/S + news + trend | -7.69% | -7.97% | 26 | 4% | -0.97 | 11 | 25 |
| L/S + news + trend + blackout | -7.75% | -7.75% | 30 | 10% | -0.73 | 13 | 25 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | QQQ | +0.00 | +0.10 | +0.10 | 1 | 100% | +0.10 | 1 | -1.02 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.31 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +0.10 |
| squeeze_breakout | QQQ | -0.05 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | NVDA | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| squeeze_breakout | AMD | -0.44 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
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
| squeeze_breakout | SOL | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 2 | -0.15 |
| rsi2_reversion | SOL | -1.45 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| donchian_trend | BTC | -1.72 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |

## ML learner, out of sample

Refitted 44 times. 5165 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2315 trades, avg +0.04R. Skipped: 2850, avg -0.03R.

