# Leaderboard – 2026-11-10 14:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | +2.10% | -10.49% | 100 | 28% | -0.04 | 16 | 141 |
| long/short | -7.69% | -12.55% | 231 | 26% | -0.26 | 24 | 0 |
| long/short + learner + news | -8.71% | -12.85% | 106 | 25% | -0.32 | 17 | 250 |
| long + trend + blackout + ML + brake 10% | -9.20% | -10.37% | 53 | 19% | -0.49 | 0 | 49 |
| L/S + news + blackout | -9.23% | -12.29% | 113 | 28% | -0.26 | 7 | 290 |
| L/S + trend + blackout + intraday + ML | -9.88% | -11.72% | 98 | 30% | -0.24 | 2 | 384 |
| long + trend + blackout + ML | -10.51% | -12.07% | 59 | 15% | -0.61 | 1 | 58 |
| long + trend + blackout + ML + insider | -10.73% | -12.30% | 60 | 17% | -0.61 | 1 | 56 |
| long/short + learner | -10.85% | -15.08% | 120 | 23% | -0.36 | 18 | 233 |
| long + trend + blackout + ML + global | -10.99% | -12.33% | 64 | 19% | -0.54 | 2 | 53 |
| L/S + news + trend + blackout | -11.00% | -14.90% | 112 | 27% | -0.29 | 5 | 164 |
| long + trend + blackout + intraday + ML | -11.61% | -12.69% | 75 | 24% | -0.48 | 1 | 115 |
| long + trend + blackout + intraday + ML + global | -11.72% | -13.63% | 80 | 22% | -0.51 | 1 | 112 |
| long + trend + blackout + intraday + ML + insider | -11.85% | -13.42% | 76 | 24% | -0.46 | 1 | 111 |
| L/S + news + trend + blackout + ML | -12.04% | -13.12% | 80 | 24% | -0.40 | 2 | 198 |
| L/S + news + trend + blackout + ML sizing | -14.51% | -16.22% | 73 | 23% | -0.47 | 2 | 201 |
| L/S + news + ML | -16.43% | -17.44% | 79 | 18% | -0.57 | 1 | 275 |
| long only + learner | -18.70% | -19.50% | 67 | 10% | -0.79 | 6 | 98 |
| long only | -20.53% | -22.69% | 132 | 14% | -0.71 | 8 | 0 |
| random entries, long/short (avg of 5) | -21.35% | -22.63% | 486 | 34% | -0.23 | 0 | 0 |
| random entries, long only (avg of 5) | -21.81% | -26.63% | 288 | 23% | -0.55 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | -1.01 | +1.97 | +1.97 | 2 | 50% | +0.98 | 3 | +0.75 |
| rsi2_reversion | TLT | +0.99 | +0.99 | +0.99 | 1 | 100% | +0.99 | 1 | -0.42 |
| donchian_trend | MSFT | -1.01 | +0.97 | +0.97 | 2 | 50% | +0.49 | 1 | -1.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | AMD | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | NVDA | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| rsi2_reversion | JPM | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | +1.82 |
| rsi2_reversion | AVGO | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| squeeze_breakout | QQQ | +0.00 | +0.00 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | SOL | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | SOL | +0.00 | +0.00 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | -0.55 | 1 | 0% | -0.55 | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | +0.00 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | META | +0.00 | +0.00 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | AAPL | +0.00 | +0.00 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | AMD | +0.00 | +0.00 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| rsi2_reversion | META | +0.00 | -0.14 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | USO | +0.00 | -0.42 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| rsi2_reversion | IWM | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -1.02 | -1.44 | 2 | 0% | -0.72 | 2 | +0.64 |
| rsi2_reversion | QQQ | +0.00 | -1.02 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| donchian_trend | TLT | +0.00 | -1.03 | -1.03 | 1 | 0% | -1.03 | 1 | -0.23 |
| rsi2_reversion | USO | +0.00 | -1.12 | -1.12 | 1 | 0% | -1.12 | 3 | +0.86 |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 1 | -1.95 |
| rsi2_reversion | AAPL | +0.00 | -1.23 | -1.31 | 4 | 25% | -0.33 | 1 | +0.22 |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| rsi2_reversion | AMD | +0.00 | -2.02 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |
| rsi2_reversion | NVDA | +0.00 | -2.03 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMZN | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 2 | -0.24 |
| donchian_trend | AAPL | +0.00 | -2.14 | -2.14 | 2 | 0% | -1.07 | 0 | – |
| donchian_trend | TSLA | -1.01 | -2.40 | -2.40 | 2 | 0% | -1.20 | 1 | +0.62 |
| rsi2_reversion | TSLA | -2.46 | -4.49 | -4.49 | 4 | 0% | -1.12 | 2 | -0.45 |

## ML learner, out of sample

Refitted 45 times. 5260 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2357 trades, avg +0.04R. Skipped: 2903, avg -0.03R.

