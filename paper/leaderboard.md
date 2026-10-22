# Leaderboard – 2026-10-22 13:28 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + trend + blackout + intraday + ML | -3.07% | -5.08% | 49 | 29% | -0.19 | 3 | 206 |
| random entries, long only (avg of 5) | -4.00% | -10.56% | 138 | 33% | -0.34 | 0 | 0 |
| long + trend + blackout + intraday + ML + insider | -4.95% | -6.31% | 54 | 22% | -0.38 | 4 | 70 |
| L/S + news + trend + blackout + ML | -5.19% | -6.45% | 46 | 20% | -0.38 | 3 | 92 |
| long + trend + blackout + intraday + ML + global | -5.52% | -7.13% | 59 | 27% | -0.36 | 3 | 62 |
| long + trend + blackout + ML | -5.87% | -7.49% | 43 | 14% | -0.53 | 3 | 34 |
| long + trend + blackout + intraday + ML | -5.87% | -7.15% | 50 | 20% | -0.44 | 4 | 75 |
| long + trend + blackout + ML + brake 10% | -5.91% | -7.52% | 44 | 16% | -0.44 | 3 | 33 |
| long + trend + blackout + ML + global | -6.20% | -7.65% | 46 | 17% | -0.49 | 2 | 33 |
| L/S + news + trend + blackout + ML sizing | -6.70% | -8.87% | 44 | 20% | -0.39 | 4 | 93 |
| long + trend + blackout + ML + insider | -7.46% | -8.51% | 47 | 13% | -0.57 | 3 | 30 |
| L/S + news + ML | -7.97% | -9.01% | 53 | 23% | -0.38 | 4 | 142 |
| L/S + news + blackout | -8.99% | -8.99% | 65 | 22% | -0.39 | 6 | 144 |
| L/S + news + trend + blackout | -10.47% | -10.74% | 58 | 14% | -0.62 | 12 | 76 |
| long/short + learner + news | -11.51% | -11.51% | 61 | 16% | -0.55 | 6 | 139 |
| long/short + learner | -11.56% | -11.56% | 82 | 20% | -0.51 | 10 | 103 |
| long/short | -12.33% | -12.55% | 121 | 20% | -0.53 | 15 | 0 |
| long only | -12.60% | -13.89% | 77 | 16% | -0.68 | 7 | 0 |
| long only + learner | -13.33% | -13.33% | 53 | 11% | -0.72 | 3 | 46 |
| random entries, long/short (avg of 5) | -13.36% | -14.40% | 250 | 35% | -0.26 | 0 | 0 |
| L/S + news + trend | -13.94% | -15.04% | 56 | 11% | -0.74 | 9 | 82 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| donchian_trend | USO | +1.99 | +1.99 | +1.99 | 1 | 100% | +1.99 | 1 | -1.01 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.98 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | USO | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 1 | +0.28 |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
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
| rsi2_reversion | AMZN | +0.00 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 1 | -1.93 |
| rsi2_reversion | AAPL | -1.02 | -1.10 | -1.10 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | META | -1.01 | -1.23 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | -1.02 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | AMD | +0.00 | -2.02 | -2.02 | 2 | 0% | -1.01 | 2 | -1.37 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| rsi2_reversion | NVDA | +0.00 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |

## ML learner, out of sample

Refitted 44 times. 5205 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2340 trades, avg +0.03R. Skipped: 2865, avg -0.03R.

