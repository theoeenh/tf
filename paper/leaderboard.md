# Leaderboard – 2026-10-29 13:49 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend + blackout + ML | -6.89% | -7.96% | 53 | 21% | -0.37 | 0 | 144 |
| long + trend + blackout + ML + brake 10% | -6.91% | -8.50% | 50 | 18% | -0.43 | 0 | 44 |
| long + trend + blackout + ML | -6.97% | -8.84% | 51 | 16% | -0.51 | 0 | 43 |
| long + trend + blackout + ML + global | -7.78% | -9.49% | 51 | 20% | -0.49 | 0 | 44 |
| L/S + trend + blackout + intraday + ML | -7.96% | -9.54% | 71 | 28% | -0.25 | 0 | 279 |
| long + trend + blackout + ML + insider | -8.21% | -9.75% | 54 | 15% | -0.53 | 0 | 40 |
| long + trend + blackout + intraday + ML + global | -8.42% | -10.36% | 65 | 26% | -0.43 | 0 | 94 |
| long + trend + blackout + intraday + ML + insider | -8.74% | -10.01% | 62 | 21% | -0.46 | 0 | 95 |
| L/S + news + trend + blackout + ML sizing | -8.81% | -10.34% | 54 | 22% | -0.37 | 0 | 143 |
| L/S + news + trend + blackout | -8.84% | -10.74% | 80 | 26% | -0.20 | 0 | 114 |
| long/short + learner + news | -9.06% | -11.51% | 77 | 22% | -0.36 | 8 | 168 |
| long + trend + blackout + intraday + ML | -9.10% | -10.18% | 62 | 23% | -0.50 | 0 | 95 |
| long/short + learner | -9.58% | -11.56% | 95 | 22% | -0.43 | 15 | 133 |
| L/S + news + blackout | -10.17% | -10.22% | 84 | 26% | -0.32 | 0 | 204 |
| long/short | -11.87% | -12.55% | 156 | 22% | -0.40 | 20 | 0 |
| random entries, long only (avg of 5) | -11.91% | -17.25% | 186 | 24% | -0.48 | 0 | 0 |
| L/S + news + ML | -11.94% | -12.43% | 60 | 18% | -0.48 | 6 | 178 |
| L/S + news + trend | -12.10% | -15.04% | 67 | 18% | -0.49 | 11 | 102 |
| long only + learner | -12.27% | -14.02% | 59 | 14% | -0.60 | 5 | 55 |
| long only | -12.85% | -14.38% | 89 | 15% | -0.67 | 12 | 0 |
| random entries, long/short (avg of 5) | -15.35% | -15.74% | 313 | 33% | -0.27 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 2 | +1.66 |
| donchian_trend | USO | +0.21 | +2.20 | +2.20 | 2 | 100% | +1.10 | 1 | -1.01 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.42 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | USO | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | +2.07 |
| donchian_trend | XOM | -0.01 | -0.01 | -0.01 | 1 | 0% | -0.01 | 2 | +2.98 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | USO | -0.05 | -0.20 | -0.20 | 2 | 0% | -0.10 | 1 | +0.28 |
| rsi2_reversion | AAPL | +0.82 | -0.28 | -0.28 | 3 | 33% | -0.09 | 0 | – |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| rsi2_reversion | QQQ | +0.00 | -0.92 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | META | +0.00 | -1.23 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 1 | +0.62 |
| rsi2_reversion | MSFT | -1.02 | -1.44 | -1.44 | 2 | 0% | -0.72 | 1 | +1.18 |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | +0.00 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 2 | -0.45 |
| rsi2_reversion | AMZN | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | -1.12 | -2.14 | -2.14 | 2 | 0% | -1.07 | 0 | – |
| rsi2_reversion | NVDA | +0.00 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |

## ML learner, out of sample

Refitted 44 times. 5221 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2338 trades, avg +0.04R. Skipped: 2883, avg -0.03R.

