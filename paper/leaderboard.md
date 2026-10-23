# Leaderboard – 2026-10-23 13:27 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + trend + blackout + intraday + ML | -5.05% | -6.66% | 54 | 28% | -0.21 | 4 | 208 |
| L/S + news + trend + blackout + ML | -5.90% | -6.71% | 48 | 21% | -0.32 | 3 | 93 |
| long + trend + blackout + ML + brake 10% | -6.37% | -7.71% | 45 | 16% | -0.46 | 3 | 33 |
| long + trend + blackout + ML | -6.43% | -7.77% | 45 | 13% | -0.55 | 3 | 33 |
| long + trend + blackout + intraday + ML + global | -6.52% | -8.12% | 61 | 26% | -0.39 | 2 | 65 |
| long + trend + blackout + intraday + ML + insider | -6.75% | -8.06% | 58 | 21% | -0.44 | 2 | 70 |
| L/S + news + trend + blackout + ML sizing | -7.09% | -8.87% | 46 | 22% | -0.35 | 5 | 95 |
| long + trend + blackout + intraday + ML | -7.17% | -8.22% | 53 | 19% | -0.49 | 3 | 77 |
| long + trend + blackout + ML + global | -7.42% | -8.66% | 46 | 15% | -0.55 | 2 | 34 |
| long + trend + blackout + ML + insider | -7.74% | -8.81% | 48 | 12% | -0.58 | 3 | 30 |
| L/S + news + blackout | -8.39% | -9.01% | 66 | 21% | -0.40 | 11 | 148 |
| L/S + news + trend + blackout | -8.48% | -10.74% | 60 | 17% | -0.51 | 11 | 78 |
| long/short + learner | -8.67% | -11.56% | 84 | 20% | -0.47 | 15 | 108 |
| random entries, long only (avg of 5) | -9.16% | -12.55% | 149 | 27% | -0.42 | 0 | 0 |
| long/short + learner + news | -9.65% | -11.51% | 63 | 17% | -0.50 | 12 | 144 |
| long/short | -9.77% | -12.55% | 125 | 21% | -0.49 | 24 | 0 |
| L/S + news + trend | -10.13% | -15.04% | 57 | 12% | -0.69 | 9 | 85 |
| L/S + news + ML | -10.13% | -10.76% | 54 | 20% | -0.45 | 4 | 147 |
| long only | -12.59% | -14.38% | 80 | 15% | -0.69 | 7 | 0 |
| random entries, long/short (avg of 5) | -13.29% | -13.85% | 257 | 35% | -0.22 | 0 | 0 |
| long only + learner | -13.83% | -14.02% | 54 | 11% | -0.73 | 4 | 49 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 0 | – |
| donchian_trend | USO | +1.99 | +1.99 | +1.99 | 1 | 100% | +1.99 | 1 | -1.01 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.98 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
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
| donchian_trend | AAPL | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| rsi2_reversion | AAPL | -1.02 | -1.10 | -1.10 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | META | -1.01 | -1.23 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | -1.02 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| rsi2_reversion | AMZN | -1.02 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| rsi2_reversion | NVDA | +0.00 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |

## ML learner, out of sample

Refitted 44 times. 5206 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2341 trades, avg +0.03R. Skipped: 2865, avg -0.03R.

