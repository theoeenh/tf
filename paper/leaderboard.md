# Leaderboard – 2026-10-15 13:23 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| long/short | -3.44% | -5.27% | 77 | 25% | -0.37 | 17 | 0 |
| L/S + trend + blackout + intraday + ML | -3.67% | -5.16% | 44 | 23% | -0.30 | 6 | 120 |
| long/short + learner | -3.87% | -7.91% | 48 | 21% | -0.47 | 14 | 72 |
| long + trend + blackout + intraday + ML + global | -3.87% | -5.64% | 51 | 27% | -0.34 | 5 | 42 |
| L/S + news + trend + blackout + ML | -4.09% | -4.96% | 38 | 18% | -0.32 | 8 | 56 |
| L/S + news + blackout | -4.23% | -6.66% | 39 | 18% | -0.38 | 14 | 102 |
| long/short + learner + news | -4.63% | -5.35% | 36 | 14% | -0.52 | 12 | 95 |
| long + trend + blackout + ML + brake 10% | -5.47% | -6.64% | 38 | 13% | -0.52 | 7 | 23 |
| long + trend + blackout + intraday + ML | -5.56% | -6.70% | 45 | 20% | -0.44 | 7 | 50 |
| L/S + news + trend + blackout + ML sizing | -5.66% | -7.00% | 32 | 19% | -0.37 | 9 | 58 |
| long + trend + blackout + ML | -5.69% | -6.98% | 37 | 14% | -0.53 | 7 | 24 |
| random entries, long only (avg of 5) | -5.70% | -9.62% | 100 | 27% | -0.39 | 0 | 0 |
| long + trend + blackout + ML + insider | -5.82% | -7.01% | 38 | 13% | -0.54 | 7 | 23 |
| long + trend + blackout + ML + global | -5.89% | -7.02% | 41 | 20% | -0.43 | 4 | 20 |
| L/S + news + ML | -6.24% | -6.94% | 40 | 22% | -0.35 | 9 | 84 |
| long + trend + blackout + intraday + ML + insider | -6.63% | -7.27% | 44 | 16% | -0.50 | 6 | 50 |
| long only | -7.20% | -8.71% | 51 | 20% | -0.53 | 10 | 0 |
| L/S + news + trend + blackout | -7.49% | -8.18% | 43 | 12% | -0.64 | 13 | 52 |
| random entries, long/short (avg of 5) | -8.70% | -9.63% | 157 | 35% | -0.24 | 0 | 0 |
| long only + learner | -9.57% | -9.59% | 39 | 10% | -0.72 | 5 | 32 |
| L/S + news + trend | -9.84% | -10.32% | 40 | 5% | -0.84 | 11 | 54 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +2.98 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| donchian_trend | MSFT | +1.98 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| rsi2_reversion | META | +1.98 | +0.89 | +0.89 | 3 | 33% | +0.30 | 0 | – |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | AAPL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.93 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.33 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.31 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.98 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| squeeze_breakout | AMD | -0.44 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | -0.49 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | -0.50 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| rsi2_reversion | QQQ | -1.02 | -0.92 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| squeeze_breakout | GOOGL | -0.96 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| squeeze_breakout | TSLA | -1.16 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| donchian_trend | QQQ | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | -1.39 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |
| rsi2_reversion | TSLA | -2.03 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| rsi2_reversion | NVDA | -3.05 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | -3.04 | -3.04 | -3.04 | 3 | 0% | -1.01 | 0 | – |

## ML learner, out of sample

Refitted 44 times. 5190 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2335 trades, avg +0.04R. Skipped: 2855, avg -0.03R.

