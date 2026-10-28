# Leaderboard – 2026-10-28 13:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend + blackout + ML | -6.65% | -7.54% | 50 | 20% | -0.35 | 2 | 119 |
| long + trend + blackout + intraday + ML + global | -7.06% | -8.83% | 65 | 26% | -0.40 | 2 | 81 |
| L/S + trend + blackout + intraday + ML | -7.36% | -8.51% | 71 | 27% | -0.23 | 3 | 245 |
| long + trend + blackout + ML | -7.58% | -8.84% | 49 | 12% | -0.57 | 2 | 40 |
| long + trend + blackout + ML + brake 10% | -7.69% | -8.84% | 50 | 12% | -0.56 | 2 | 39 |
| long + trend + blackout + ML + global | -8.39% | -9.49% | 49 | 14% | -0.55 | 2 | 40 |
| long + trend + blackout + intraday + ML + insider | -8.49% | -10.05% | 58 | 19% | -0.50 | 1 | 89 |
| long + trend + blackout + ML + insider | -8.82% | -9.75% | 52 | 12% | -0.59 | 2 | 37 |
| long/short + learner + news | -8.85% | -11.51% | 75 | 23% | -0.34 | 10 | 160 |
| L/S + news + trend + blackout | -8.94% | -10.74% | 72 | 25% | -0.22 | 8 | 94 |
| L/S + news + trend + blackout + ML sizing | -9.36% | -10.90% | 48 | 19% | -0.42 | 4 | 121 |
| long/short + learner | -9.59% | -11.56% | 92 | 23% | -0.42 | 17 | 127 |
| long + trend + blackout + intraday + ML | -9.80% | -10.88% | 61 | 18% | -0.53 | 2 | 88 |
| L/S + news + blackout | -9.86% | -9.86% | 77 | 25% | -0.35 | 7 | 174 |
| L/S + news + ML | -10.07% | -10.92% | 59 | 22% | -0.39 | 7 | 173 |
| long/short | -10.93% | -12.55% | 150 | 23% | -0.40 | 20 | 0 |
| L/S + news + trend | -11.02% | -15.04% | 64 | 19% | -0.46 | 13 | 99 |
| long only | -12.52% | -14.38% | 86 | 15% | -0.66 | 14 | 0 |
| long only + learner | -12.79% | -14.02% | 59 | 14% | -0.60 | 5 | 52 |
| random entries, long only (avg of 5) | -14.21% | -18.53% | 186 | 26% | -0.48 | 0 | 0 |
| random entries, long/short (avg of 5) | -14.80% | -15.30% | 308 | 34% | -0.25 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 2 | +1.15 |
| donchian_trend | USO | +0.00 | +1.99 | +1.99 | 1 | 100% | +1.99 | 1 | -1.01 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | USO | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +3.45 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | USO | -0.05 | -0.20 | -0.20 | 2 | 0% | -0.10 | 1 | +0.28 |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 0 | – |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| donchian_trend | SOL | +0.00 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | XOM | -0.91 | -0.91 | -0.91 | 1 | 0% | -0.91 | 2 | +2.98 |
| rsi2_reversion | QQQ | +0.00 | -0.92 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AAPL | +0.00 | -1.10 | -1.10 | 2 | 0% | -0.55 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | META | +0.00 | -1.23 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 0 | – |
| rsi2_reversion | MSFT | -1.02 | -1.44 | -1.44 | 2 | 0% | -0.72 | 1 | +1.18 |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | +0.00 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 1 | -1.01 |
| rsi2_reversion | AMZN | -1.02 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | -1.12 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| rsi2_reversion | NVDA | +0.00 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |

## ML learner, out of sample

Refitted 44 times. 5217 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2350 trades, avg +0.03R. Skipped: 2867, avg -0.03R.

