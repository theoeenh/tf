# Leaderboard – 2026-11-03 14:24 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | -1.26% | -10.49% | 85 | 26% | -0.05 | 10 | 109 |
| long/short | -3.01% | -12.55% | 179 | 26% | -0.24 | 26 | 0 |
| L/S + news + trend + blackout + ML | -7.31% | -8.65% | 60 | 23% | -0.37 | 9 | 150 |
| L/S + news + trend + blackout + ML sizing | -8.13% | -10.25% | 52 | 25% | -0.38 | 9 | 151 |
| long + trend + blackout + intraday + ML | -8.15% | -9.00% | 62 | 26% | -0.40 | 3 | 104 |
| long + trend + blackout + ML | -8.66% | -9.84% | 51 | 16% | -0.58 | 3 | 48 |
| L/S + trend + blackout + intraday + ML | -8.80% | -10.36% | 73 | 26% | -0.27 | 8 | 308 |
| long + trend + blackout + ML + insider | -9.10% | -10.27% | 54 | 17% | -0.60 | 3 | 44 |
| long + trend + blackout + ML + brake 10% | -9.11% | -10.29% | 51 | 18% | -0.51 | 0 | 51 |
| long/short + learner + news | -9.25% | -10.96% | 86 | 22% | -0.36 | 10 | 200 |
| long + trend + blackout + ML + global | -9.28% | -10.31% | 56 | 20% | -0.52 | 3 | 42 |
| long + trend + blackout + intraday + ML + global | -9.53% | -11.07% | 72 | 24% | -0.46 | 3 | 97 |
| long + trend + blackout + intraday + ML + insider | -10.30% | -11.44% | 67 | 21% | -0.48 | 3 | 99 |
| L/S + news + blackout | -10.47% | -10.95% | 89 | 24% | -0.33 | 7 | 221 |
| L/S + news + trend + blackout | -10.58% | -12.90% | 89 | 26% | -0.30 | 10 | 119 |
| L/S + news + ML | -11.50% | -12.55% | 64 | 22% | -0.41 | 6 | 219 |
| long/short + learner | -12.75% | -13.88% | 91 | 21% | -0.42 | 11 | 192 |
| long only | -15.86% | -17.10% | 105 | 14% | -0.68 | 10 | 0 |
| long only + learner | -16.21% | -16.21% | 56 | 11% | -0.76 | 5 | 78 |
| random entries, long/short (avg of 5) | -17.75% | -17.94% | 383 | 34% | -0.26 | 0 | 0 |
| random entries, long only (avg of 5) | -19.26% | -22.90% | 224 | 21% | -0.59 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 2 | +1.66 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| rsi2_reversion | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.42 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | -0.55 | 1 | 0% | -0.55 | 1 | -1.02 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| donchian_trend | USO | -2.41 | -0.42 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -1.02 | -1.44 | 2 | 0% | -0.72 | 1 | +1.18 |
| rsi2_reversion | QQQ | +0.00 | -1.02 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| rsi2_reversion | USO | -1.12 | -1.12 | -1.12 | 1 | 0% | -1.12 | 2 | +2.07 |
| rsi2_reversion | META | +0.00 | -1.16 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | AAPL | -0.21 | -1.23 | -1.31 | 4 | 25% | -0.33 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 1 | +0.62 |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 2 | -0.45 |
| rsi2_reversion | AMZN | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | +0.00 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |
| rsi2_reversion | NVDA | +0.00 | -3.05 | -2.62 | 4 | 25% | -0.66 | 0 | – |

## ML learner, out of sample

Refitted 45 times. 5241 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2352 trades, avg +0.04R. Skipped: 2889, avg -0.03R.

