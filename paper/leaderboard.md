# Leaderboard – 2026-11-12 16:57 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | +2.14% | -10.49% | 109 | 29% | +0.03 | 14 | 149 |
| long/short | -5.43% | -12.55% | 248 | 26% | -0.23 | 23 | 0 |
| long/short + learner + news | -9.16% | -12.85% | 116 | 24% | -0.33 | 18 | 260 |
| long + trend + blackout + ML + brake 10% | -9.20% | -10.37% | 53 | 19% | -0.49 | 0 | 50 |
| long + trend + blackout + ML | -9.28% | -10.72% | 59 | 19% | -0.53 | 4 | 60 |
| long + trend + blackout + ML + insider | -9.33% | -10.77% | 58 | 19% | -0.47 | 4 | 62 |
| L/S + news + trend + blackout + ML | -9.55% | -11.67% | 81 | 25% | -0.40 | 7 | 214 |
| L/S + news + trend + blackout + ML sizing | -9.98% | -12.43% | 75 | 27% | -0.36 | 7 | 215 |
| long + trend + blackout + intraday + ML + insider | -10.38% | -12.53% | 75 | 25% | -0.41 | 4 | 120 |
| long/short + learner | -10.46% | -15.08% | 132 | 23% | -0.35 | 16 | 241 |
| L/S + news + blackout | -10.89% | -12.29% | 123 | 28% | -0.25 | 11 | 301 |
| long + trend + blackout + ML + global | -11.24% | -12.28% | 64 | 19% | -0.56 | 3 | 55 |
| L/S + news + trend + blackout | -11.44% | -14.90% | 117 | 28% | -0.24 | 8 | 176 |
| long + trend + blackout + intraday + ML | -11.58% | -13.52% | 78 | 24% | -0.45 | 4 | 117 |
| long + trend + blackout + intraday + ML + global | -11.61% | -13.59% | 81 | 23% | -0.47 | 3 | 116 |
| L/S + trend + blackout + intraday + ML | -12.09% | -13.98% | 95 | 27% | -0.30 | 7 | 420 |
| L/S + news + ML | -17.12% | -18.07% | 78 | 18% | -0.57 | 3 | 296 |
| long only + learner | -20.11% | -20.58% | 72 | 10% | -0.81 | 8 | 98 |
| random entries, long/short (avg of 5) | -21.20% | -23.68% | 505 | 34% | -0.23 | 0 | 0 |
| random entries, long only (avg of 5) | -22.21% | -26.73% | 291 | 22% | -0.56 | 0 | 0 |
| long only | -22.23% | -23.65% | 137 | 13% | -0.73 | 13 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| donchian_trend | XOM | +0.00 | +2.27 | +2.27 | 2 | 100% | +1.14 | 2 | -1.02 |
| rsi2_reversion | TLT | +0.99 | +0.99 | +0.99 | 1 | 100% | +0.99 | 2 | -0.76 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | AMD | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | NVDA | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | QQQ | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | -0.55 | 1 | 0% | -0.55 | 1 | -1.02 |
| rsi2_reversion | AVGO | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | AMD | +0.00 | +0.00 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| squeeze_breakout | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | TSLA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.95 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| squeeze_breakout | SOL | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| rsi2_reversion | SOL | +0.00 | +0.00 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | JPM | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | +1.82 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| squeeze_breakout | MSFT | +0.00 | +0.00 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | QQQ | +0.00 | +0.00 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | META | +0.00 | +0.00 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | AAPL | +0.00 | +0.00 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | AMD | +0.00 | +0.00 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| donchian_trend | USO | +0.00 | -0.42 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | TSLA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 1 | +0.62 |
| donchian_trend | MSFT | +0.00 | -1.01 | +0.97 | 2 | 50% | +0.49 | 1 | -1.02 |
| rsi2_reversion | XOM | +0.00 | -1.01 | +1.97 | 2 | 50% | +0.98 | 3 | +0.75 |
| rsi2_reversion | IWM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | NVDA | +0.00 | -1.02 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -1.02 | -1.44 | 2 | 0% | -0.72 | 2 | +0.64 |
| rsi2_reversion | QQQ | +0.00 | -1.02 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| donchian_trend | TLT | +0.00 | -1.03 | -1.03 | 1 | 0% | -1.03 | 2 | -0.94 |
| rsi2_reversion | USO | +0.00 | -1.12 | -1.12 | 1 | 0% | -1.12 | 3 | +0.86 |
| rsi2_reversion | AAPL | +0.00 | -1.23 | -1.31 | 4 | 25% | -0.33 | 1 | +0.22 |
| rsi2_reversion | AMZN | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 2 | -0.24 |
| rsi2_reversion | META | +0.00 | -2.12 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | AAPL | +0.00 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| rsi2_reversion | TSLA | +0.00 | -3.47 | -4.49 | 4 | 0% | -1.12 | 2 | -0.45 |

## ML learner, out of sample

Refitted 45 times. 5260 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2363 trades, avg +0.04R. Skipped: 2897, avg -0.04R.

