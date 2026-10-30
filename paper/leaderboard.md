# Leaderboard – 2026-10-30 13:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + trend + blackout + intraday + ML | -5.83% | -8.13% | 73 | 30% | -0.23 | 5 | 289 |
| long + trend + blackout + ML | -6.52% | -8.84% | 52 | 17% | -0.49 | 1 | 45 |
| long + trend + blackout + ML + global | -6.58% | -8.74% | 53 | 23% | -0.43 | 1 | 44 |
| L/S + news + trend + blackout + ML | -6.68% | -8.44% | 56 | 23% | -0.32 | 4 | 146 |
| long/short + learner + news | -6.70% | -11.51% | 81 | 25% | -0.26 | 9 | 174 |
| long/short | -7.08% | -12.55% | 162 | 25% | -0.30 | 24 | 0 |
| long + trend + blackout + intraday + ML + insider | -7.12% | -9.15% | 62 | 24% | -0.43 | 1 | 98 |
| long + trend + blackout + ML + insider | -7.38% | -9.36% | 55 | 20% | -0.45 | 1 | 42 |
| L/S + news + trend + blackout + ML sizing | -7.58% | -10.09% | 52 | 25% | -0.33 | 4 | 147 |
| long/short + learner | -7.69% | -11.56% | 101 | 25% | -0.36 | 14 | 137 |
| L/S + news + trend + blackout | -7.96% | -10.74% | 81 | 27% | -0.17 | 2 | 117 |
| long + trend + blackout + intraday + ML | -8.25% | -10.49% | 61 | 25% | -0.44 | 1 | 103 |
| long + trend + blackout + intraday + ML + global | -8.78% | -11.41% | 70 | 27% | -0.39 | 1 | 90 |
| L/S + news + trend | -8.88% | -15.04% | 70 | 20% | -0.35 | 12 | 107 |
| long + trend + blackout + ML + brake 10% | -8.93% | -10.04% | 50 | 16% | -0.58 | 0 | 41 |
| L/S + news + blackout | -10.13% | -10.25% | 84 | 26% | -0.32 | 3 | 208 |
| L/S + news + ML | -10.87% | -12.12% | 62 | 18% | -0.49 | 6 | 188 |
| long only + learner | -12.08% | -14.02% | 60 | 13% | -0.60 | 6 | 56 |
| long only | -12.24% | -14.38% | 90 | 14% | -0.68 | 14 | 0 |
| random entries, long only (avg of 5) | -15.99% | -19.32% | 185 | 22% | -0.51 | 0 | 0 |
| random entries, long/short (avg of 5) | -20.12% | -20.38% | 339 | 33% | -0.30 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 2 | +1.66 |
| donchian_trend | USO | +0.21 | +2.20 | +2.20 | 2 | 100% | +1.10 | 1 | -1.01 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| rsi2_reversion | AAPL | +1.23 | +0.12 | +0.12 | 4 | 50% | +0.03 | 0 | – |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| rsi2_reversion | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.42 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| rsi2_reversion | USO | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | +2.07 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| donchian_trend | XOM | -0.01 | -0.01 | -0.01 | 1 | 0% | -0.01 | 2 | +2.98 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | USO | -0.05 | -0.20 | -0.20 | 2 | 0% | -0.10 | 1 | +0.28 |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 1 | +0.02 |
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
| rsi2_reversion | MSFT | +0.00 | -1.44 | -1.44 | 2 | 0% | -0.72 | 1 | +1.18 |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | GOOGL | +0.00 | -1.56 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 2 | -0.45 |
| rsi2_reversion | AMZN | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | -1.12 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| rsi2_reversion | NVDA | +0.00 | -2.62 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |

## ML learner, out of sample

Refitted 44 times. 5224 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2339 trades, avg +0.04R. Skipped: 2885, avg -0.03R.

