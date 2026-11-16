# Leaderboard – 2026-11-16 14:29 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| long/short | -1.81% | -12.55% | 262 | 28% | -0.17 | 28 | 0 |
| L/S + news + trend | -1.93% | -11.21% | 105 | 26% | -0.14 | 13 | 171 |
| L/S + news + trend + blackout | -4.76% | -8.16% | 89 | 27% | -0.25 | 8 | 229 |
| long + trend + blackout + ML + brake 10% | -9.08% | -10.15% | 56 | 20% | -0.50 | 0 | 54 |
| L/S + news + blackout | -9.17% | -10.36% | 107 | 31% | -0.21 | 9 | 337 |
| long/short + learner + news | -10.01% | -13.95% | 108 | 25% | -0.27 | 19 | 286 |
| long + trend + blackout + ML + insider | -10.80% | -11.94% | 60 | 18% | -0.50 | 4 | 62 |
| long/short + learner | -10.85% | -14.71% | 138 | 26% | -0.22 | 22 | 253 |
| long + trend + blackout + intraday + ML + global | -12.69% | -14.27% | 78 | 26% | -0.48 | 3 | 122 |
| long + trend + blackout + intraday + ML | -12.71% | -13.42% | 75 | 23% | -0.50 | 5 | 126 |
| long + trend + blackout + intraday + ML + insider | -12.87% | -13.95% | 74 | 20% | -0.53 | 4 | 127 |
| long + trend + blackout + ML | -12.91% | -13.63% | 58 | 16% | -0.64 | 4 | 66 |
| long + trend + blackout + ML + global | -13.76% | -14.80% | 63 | 16% | -0.62 | 3 | 60 |
| L/S + trend + blackout + intraday + ML | -13.84% | -15.44% | 101 | 28% | -0.36 | 8 | 450 |
| L/S + news + trend + blackout + ML | -14.42% | -15.44% | 80 | 20% | -0.53 | 7 | 237 |
| L/S + news + ML | -15.24% | -16.08% | 82 | 18% | -0.54 | 2 | 312 |
| L/S + news + trend + blackout + ML sizing | -16.89% | -18.55% | 71 | 21% | -0.52 | 7 | 237 |
| long only + learner | -22.00% | -22.35% | 89 | 11% | -0.73 | 8 | 83 |
| random entries, long/short (avg of 5) | -23.09% | -25.01% | 557 | 35% | -0.23 | 0 | 0 |
| long only | -23.89% | -25.51% | 141 | 13% | -0.74 | 12 | 0 |
| random entries, long only (avg of 5) | -26.43% | -29.12% | 322 | 22% | -0.56 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| donchian_trend | AMD | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 1 | -1.00 |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | NVDA | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | QQQ | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | +0.42 | 3 | 33% | +0.14 | 0 | – |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | AVGO | +0.00 | +0.00 | -2.03 | 2 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AMD | +0.00 | +0.00 | -2.02 | 2 | 0% | -1.01 | 1 | -1.01 |
| squeeze_breakout | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | TSLA | +0.00 | +0.00 | -1.16 | 1 | 0% | -1.16 | 1 | -1.95 |
| squeeze_breakout | QQQ | +0.00 | +0.00 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.75 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| rsi2_reversion | NVDA | +0.00 | +0.00 | -1.60 | 3 | 33% | -0.53 | 1 | -1.02 |
| rsi2_reversion | META | +0.00 | +0.00 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| rsi2_reversion | JPM | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | +1.82 |
| rsi2_reversion | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | -1.43 |
| rsi2_reversion | QQQ | +0.00 | +0.00 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| squeeze_breakout | META | +0.00 | +0.00 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | GOOGL | +0.00 | +0.00 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | AAPL | +0.00 | +0.00 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | AMD | +0.00 | +0.00 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.15 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | MSFT | +0.00 | +0.00 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| rsi2_reversion | TLT | -1.03 | -0.03 | -0.03 | 2 | 50% | -0.02 | 2 | -0.76 |
| donchian_trend | TSLA | +0.00 | -1.01 | -2.40 | 2 | 0% | -1.20 | 1 | +0.62 |
| donchian_trend | MSFT | +0.00 | -1.01 | +0.97 | 2 | 50% | +0.49 | 1 | -1.02 |
| rsi2_reversion | XOM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 4 | +1.31 |
| rsi2_reversion | IWM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AMZN | +0.00 | -1.02 | -2.03 | 2 | 0% | -1.02 | 2 | -0.24 |
| rsi2_reversion | MSFT | +0.00 | -1.08 | -1.50 | 2 | 0% | -0.75 | 2 | +0.84 |
| rsi2_reversion | USO | +0.00 | -1.12 | -1.12 | 1 | 0% | -1.12 | 3 | +0.86 |
| rsi2_reversion | AAPL | +0.00 | -1.23 | -1.31 | 4 | 25% | -0.33 | 1 | +0.22 |
| donchian_trend | AAPL | +0.00 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| donchian_trend | USO | +0.00 | -2.41 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| rsi2_reversion | TSLA | +0.00 | -2.46 | -4.49 | 4 | 0% | -1.12 | 3 | -0.64 |
| donchian_trend | TLT | -1.65 | -2.67 | -2.67 | 2 | 0% | -1.34 | 1 | -0.23 |

## ML learner, out of sample

Refitted 45 times. 5254 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2342 trades, avg +0.04R. Skipped: 2912, avg -0.02R.

