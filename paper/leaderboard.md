# Leaderboard – 2026-11-20 14:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | +6.30% | -11.05% | 113 | 28% | -0.03 | 13 | 194 |
| long/short | +4.02% | -12.55% | 290 | 29% | -0.13 | 29 | 0 |
| long/short + learner + news | -2.82% | -10.22% | 121 | 26% | -0.23 | 11 | 311 |
| L/S + news + trend + blackout | -7.07% | -10.70% | 103 | 25% | -0.30 | 10 | 252 |
| long/short + learner | -7.23% | -14.71% | 158 | 26% | -0.21 | 16 | 269 |
| long + trend + blackout + ML + brake 10% | -9.56% | -10.41% | 47 | 13% | -0.62 | 0 | 45 |
| L/S + trend + blackout + intraday + ML | -12.73% | -15.30% | 111 | 28% | -0.31 | 3 | 507 |
| long + trend + blackout + intraday + ML + insider | -14.08% | -15.81% | 84 | 23% | -0.46 | 1 | 130 |
| L/S + news + trend + blackout + ML | -14.22% | -16.26% | 91 | 22% | -0.43 | 3 | 265 |
| long + trend + blackout + ML + global | -14.24% | -15.03% | 69 | 16% | -0.62 | 0 | 64 |
| L/S + news + blackout | -14.27% | -15.36% | 123 | 27% | -0.35 | 5 | 367 |
| long + trend + blackout + ML + insider | -14.49% | -14.79% | 63 | 14% | -0.68 | 1 | 72 |
| L/S + news + trend + blackout + ML sizing | -14.87% | -17.48% | 83 | 23% | -0.47 | 3 | 266 |
| long + trend + blackout + intraday + ML + global | -14.88% | -16.38% | 86 | 27% | -0.48 | 0 | 130 |
| long + trend + blackout + ML | -14.96% | -15.67% | 65 | 14% | -0.67 | 1 | 67 |
| long + trend + blackout + intraday + ML | -17.41% | -18.79% | 85 | 20% | -0.58 | 1 | 133 |
| L/S + news + ML | -17.71% | -18.67% | 83 | 17% | -0.60 | 3 | 349 |
| long only + learner | -25.13% | -25.13% | 99 | 10% | -0.75 | 1 | 87 |
| long only | -28.37% | -29.43% | 155 | 12% | -0.76 | 5 | 0 |
| random entries, long/short (avg of 5) | -28.48% | -29.04% | 613 | 34% | -0.23 | 0 | 0 |
| random entries, long only (avg of 5) | -36.50% | -39.69% | 368 | 16% | -0.67 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| donchian_trend | AMD | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 1 | -1.00 |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | NVDA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | QQQ | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| rsi2_reversion | AMD | +0.00 | +0.00 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| rsi2_reversion | SOL | +0.00 | +0.00 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | META | +0.00 | +0.00 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | AVGO | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.95 |
| squeeze_breakout | NVDA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.15 |
| squeeze_breakout | QQQ | +0.00 | +0.00 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.75 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | AMZN | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.16 |
| rsi2_reversion | QQQ | +0.00 | +0.00 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| rsi2_reversion | NVDA | +0.00 | +0.00 | -1.61 | 3 | 33% | -0.54 | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | +0.00 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | +0.00 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | GOOGL | +0.00 | +0.00 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| squeeze_breakout | AAPL | +0.00 | +0.00 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | AMD | +0.00 | +0.00 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| rsi2_reversion | TLT | +0.00 | -0.03 | -0.03 | 2 | 50% | -0.02 | 2 | -0.76 |
| squeeze_breakout | USO | +0.00 | -0.05 | -0.20 | 2 | 0% | -0.10 | 1 | +0.28 |
| rsi2_reversion | AAPL | +0.00 | -0.21 | -1.31 | 4 | 25% | -0.33 | 1 | +0.22 |
| donchian_trend | TSLA | +0.00 | -1.01 | -2.40 | 2 | 0% | -1.20 | 1 | +0.62 |
| donchian_trend | MSFT | +0.00 | -1.01 | +0.97 | 2 | 50% | +0.49 | 1 | -1.02 |
| rsi2_reversion | XOM | +0.00 | -1.01 | +1.97 | 2 | 50% | +0.98 | 3 | +0.75 |
| rsi2_reversion | IWM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 1 | -1.01 |
| rsi2_reversion | AMZN | +0.00 | -1.02 | -2.22 | 2 | 0% | -1.11 | 4 | +0.12 |
| squeeze_breakout | JPM | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| squeeze_breakout | TLT | +0.00 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| rsi2_reversion | USO | +0.00 | -1.12 | -1.12 | 1 | 0% | -1.12 | 3 | +0.86 |
| rsi2_reversion | MSFT | -1.01 | -2.09 | -2.51 | 3 | 0% | -0.84 | 2 | +0.84 |
| donchian_trend | AAPL | -1.02 | -2.14 | -3.16 | 3 | 0% | -1.05 | 1 | -1.93 |
| donchian_trend | USO | +0.00 | -2.41 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| rsi2_reversion | TSLA | +0.00 | -2.46 | -4.49 | 4 | 0% | -1.12 | 3 | -0.64 |
| donchian_trend | TLT | +0.00 | -2.67 | -2.67 | 2 | 0% | -1.34 | 1 | -0.23 |
| rsi2_reversion | JPM | -3.90 | -3.90 | -3.90 | 3 | 0% | -1.30 | 2 | +1.82 |

## ML learner, out of sample

Refitted 45 times. 5275 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2358 trades, avg +0.04R. Skipped: 2917, avg -0.03R.

