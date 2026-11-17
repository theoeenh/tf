# Leaderboard – 2026-11-17 14:28 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | -0.92% | -11.21% | 107 | 26% | -0.11 | 12 | 177 |
| long/short | -2.19% | -12.55% | 274 | 28% | -0.14 | 25 | 0 |
| L/S + news + trend + blackout | -4.68% | -8.16% | 91 | 27% | -0.24 | 6 | 240 |
| long + trend + blackout + ML + brake 10% | -9.08% | -10.15% | 56 | 20% | -0.50 | 0 | 54 |
| L/S + news + blackout | -10.22% | -10.59% | 113 | 30% | -0.23 | 4 | 348 |
| long/short + learner + news | -10.66% | -13.95% | 119 | 25% | -0.26 | 11 | 289 |
| long/short + learner | -11.44% | -14.71% | 146 | 26% | -0.21 | 17 | 258 |
| long + trend + blackout + ML + insider | -12.12% | -13.11% | 63 | 17% | -0.53 | 2 | 66 |
| L/S + trend + blackout + intraday + ML | -12.42% | -14.52% | 107 | 30% | -0.28 | 4 | 462 |
| long + trend + blackout + intraday + ML + global | -13.99% | -15.45% | 81 | 25% | -0.50 | 2 | 127 |
| long + trend + blackout + intraday + ML | -14.10% | -14.66% | 77 | 22% | -0.53 | 4 | 131 |
| long + trend + blackout + ML | -14.20% | -14.78% | 61 | 15% | -0.66 | 2 | 70 |
| long + trend + blackout + intraday + ML + insider | -14.36% | -15.27% | 76 | 20% | -0.54 | 4 | 134 |
| L/S + news + trend + blackout + ML | -14.94% | -15.44% | 85 | 21% | -0.49 | 4 | 245 |
| long + trend + blackout + ML + global | -15.04% | -15.98% | 66 | 15% | -0.64 | 2 | 64 |
| L/S + news + ML | -15.32% | -16.08% | 85 | 19% | -0.51 | 0 | 322 |
| L/S + news + trend + blackout + ML sizing | -17.47% | -18.55% | 76 | 22% | -0.47 | 4 | 245 |
| long only + learner | -23.75% | -24.13% | 94 | 11% | -0.75 | 5 | 86 |
| random entries, long/short (avg of 5) | -25.09% | -26.00% | 575 | 35% | -0.22 | 0 | 0 |
| long only | -26.94% | -28.39% | 149 | 12% | -0.76 | 7 | 0 |
| random entries, long only (avg of 5) | -31.78% | -35.24% | 336 | 20% | -0.59 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| donchian_trend | AMD | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 1 | -1.00 |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | NVDA | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | QQQ | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| rsi2_reversion | AMD | +0.00 | +0.00 | -2.02 | 2 | 0% | -1.01 | 1 | -1.01 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| rsi2_reversion | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | -1.43 |
| rsi2_reversion | META | +0.00 | +0.00 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | +0.42 | 3 | 33% | +0.14 | 0 | – |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | AVGO | +0.00 | +0.00 | -2.03 | 2 | 0% | -1.01 | 0 | – |
| squeeze_breakout | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | NVDA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.15 |
| squeeze_breakout | QQQ | +0.00 | +0.00 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.75 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| squeeze_breakout | TSLA | +0.00 | +0.00 | -1.16 | 1 | 0% | -1.16 | 1 | -1.95 |
| rsi2_reversion | QQQ | +0.00 | +0.00 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| rsi2_reversion | NVDA | +0.00 | +0.00 | -1.60 | 3 | 33% | -0.53 | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | +0.00 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | +0.00 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | GOOGL | +0.00 | +0.00 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| squeeze_breakout | AMZN | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.16 |
| squeeze_breakout | AMD | +0.00 | +0.00 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | +0.00 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| rsi2_reversion | TLT | -1.03 | -0.03 | -0.03 | 2 | 50% | -0.02 | 2 | -0.76 |
| donchian_trend | TSLA | +0.00 | -1.01 | -2.40 | 2 | 0% | -1.20 | 1 | +0.62 |
| donchian_trend | MSFT | +0.00 | -1.01 | +0.97 | 2 | 50% | +0.49 | 1 | -1.02 |
| rsi2_reversion | XOM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 4 | +1.31 |
| rsi2_reversion | IWM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 1 | -1.01 |
| rsi2_reversion | AMZN | +0.00 | -1.02 | -2.03 | 2 | 0% | -1.02 | 3 | -0.50 |
| squeeze_breakout | JPM | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| rsi2_reversion | JPM | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 2 | +1.82 |
| rsi2_reversion | MSFT | +0.00 | -1.08 | -1.50 | 2 | 0% | -0.75 | 2 | +0.84 |
| rsi2_reversion | USO | +0.00 | -1.12 | -1.12 | 1 | 0% | -1.12 | 3 | +0.86 |
| rsi2_reversion | AAPL | +0.00 | -1.23 | -1.31 | 4 | 25% | -0.33 | 1 | +0.22 |
| donchian_trend | USO | +0.00 | -2.41 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| rsi2_reversion | TSLA | +0.00 | -2.46 | -4.49 | 4 | 0% | -1.12 | 4 | -0.73 |
| donchian_trend | TLT | +0.00 | -2.67 | -2.67 | 2 | 0% | -1.34 | 1 | -0.23 |
| donchian_trend | AAPL | -1.02 | -3.16 | -3.16 | 3 | 0% | -1.05 | 1 | -1.93 |

## ML learner, out of sample

Refitted 45 times. 5261 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2349 trades, avg +0.03R. Skipped: 2912, avg -0.02R.

