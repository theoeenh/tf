# Leaderboard – 2026-10-19 13:30 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + trend + blackout + intraday + ML | -4.55% | -6.28% | 50 | 24% | -0.30 | 4 | 171 |
| L/S + news + trend + blackout + ML | -5.45% | -6.45% | 44 | 18% | -0.38 | 4 | 80 |
| random entries, long only (avg of 5) | -5.59% | -10.44% | 122 | 26% | -0.48 | 0 | 0 |
| L/S + news + blackout | -5.60% | -6.66% | 52 | 19% | -0.46 | 11 | 125 |
| long + trend + blackout + ML + brake 10% | -5.71% | -7.25% | 42 | 17% | -0.42 | 3 | 27 |
| long + trend + blackout + ML | -5.77% | -7.30% | 42 | 14% | -0.52 | 3 | 27 |
| long + trend + blackout + intraday + ML + global | -6.11% | -7.98% | 54 | 26% | -0.40 | 2 | 59 |
| long + trend + blackout + ML + insider | -6.69% | -7.84% | 44 | 14% | -0.53 | 3 | 25 |
| long + trend + blackout + intraday + ML | -6.81% | -7.78% | 50 | 20% | -0.48 | 3 | 62 |
| long + trend + blackout + ML + global | -6.89% | -8.21% | 43 | 16% | -0.52 | 2 | 26 |
| long/short + learner + news | -7.15% | -7.45% | 49 | 16% | -0.53 | 11 | 119 |
| L/S + news + trend + blackout + ML sizing | -7.25% | -8.86% | 38 | 18% | -0.44 | 5 | 82 |
| long + trend + blackout + intraday + ML + insider | -7.74% | -8.62% | 51 | 18% | -0.48 | 3 | 61 |
| long/short + learner | -7.75% | -8.40% | 64 | 19% | -0.57 | 15 | 89 |
| L/S + news + ML | -8.14% | -9.11% | 46 | 20% | -0.46 | 7 | 116 |
| long/short | -8.16% | -8.48% | 96 | 23% | -0.44 | 20 | 0 |
| L/S + news + trend + blackout | -8.81% | -9.31% | 52 | 13% | -0.62 | 14 | 70 |
| long only | -9.79% | -11.27% | 61 | 18% | -0.60 | 12 | 0 |
| long only + learner | -10.65% | -10.81% | 44 | 11% | -0.72 | 8 | 36 |
| random entries, long/short (avg of 5) | -10.94% | -11.62% | 198 | 34% | -0.25 | 0 | 0 |
| L/S + news + trend | -12.25% | -13.89% | 50 | 8% | -0.85 | 9 | 71 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| donchian_trend | USO | +1.99 | +1.99 | +1.99 | 1 | 100% | +1.99 | 0 | – |
| donchian_trend | MSFT | +1.98 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | AAPL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.93 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.31 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.98 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| rsi2_reversion | QQQ | -1.02 | -0.92 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| squeeze_breakout | GOOGL | -0.96 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AMZN | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| squeeze_breakout | TSLA | -1.16 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | META | -0.14 | -1.23 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | QQQ | -1.33 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | -1.39 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | -1.02 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |
| rsi2_reversion | TSLA | -2.03 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| rsi2_reversion | NVDA | -2.03 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | -1.01 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |

## ML learner, out of sample

Refitted 44 times. 5196 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2336 trades, avg +0.04R. Skipped: 2860, avg -0.03R.

