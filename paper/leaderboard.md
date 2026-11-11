# Leaderboard – 2026-11-11 14:25 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | +4.11% | -10.49% | 103 | 29% | +0.02 | 14 | 145 |
| long/short | -6.25% | -12.55% | 238 | 26% | -0.26 | 24 | 0 |
| long/short + learner + news | -8.01% | -11.92% | 108 | 24% | -0.33 | 17 | 256 |
| long + trend + blackout + ML + brake 10% | -9.20% | -10.37% | 53 | 19% | -0.49 | 0 | 50 |
| L/S + news + trend + blackout + ML | -9.84% | -11.15% | 78 | 24% | -0.42 | 3 | 208 |
| L/S + news + blackout | -9.86% | -11.42% | 114 | 29% | -0.24 | 8 | 298 |
| L/S + news + trend + blackout + ML sizing | -10.21% | -11.83% | 73 | 26% | -0.40 | 3 | 208 |
| long + trend + blackout + intraday + ML + global | -10.57% | -12.32% | 79 | 25% | -0.44 | 3 | 112 |
| long/short + learner | -10.70% | -15.08% | 124 | 23% | -0.36 | 17 | 237 |
| long + trend + blackout + ML | -10.73% | -12.09% | 59 | 15% | -0.61 | 3 | 61 |
| long + trend + blackout + ML + insider | -10.82% | -12.18% | 60 | 17% | -0.61 | 3 | 59 |
| long + trend + blackout + ML + global | -11.12% | -12.30% | 64 | 19% | -0.54 | 2 | 55 |
| L/S + news + trend + blackout | -11.74% | -14.44% | 112 | 27% | -0.28 | 6 | 173 |
| long + trend + blackout + intraday + ML | -12.69% | -13.88% | 78 | 22% | -0.50 | 4 | 113 |
| L/S + trend + blackout + intraday + ML | -13.44% | -15.04% | 92 | 25% | -0.35 | 4 | 400 |
| long + trend + blackout + intraday + ML + insider | -13.97% | -14.77% | 76 | 17% | -0.57 | 4 | 116 |
| L/S + news + ML | -15.30% | -16.40% | 76 | 20% | -0.52 | 1 | 286 |
| random entries, long/short (avg of 5) | -19.92% | -22.39% | 502 | 34% | -0.22 | 0 | 0 |
| long only + learner | -20.23% | -20.53% | 69 | 10% | -0.80 | 6 | 98 |
| long only | -22.11% | -23.64% | 134 | 13% | -0.72 | 8 | 0 |
| random entries, long only (avg of 5) | -25.50% | -29.65% | 288 | 23% | -0.57 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | TLT | +0.99 | +0.99 | +0.99 | 1 | 100% | +0.99 | 2 | -0.76 |
| donchian_trend | MSFT | -1.01 | +0.97 | +0.97 | 2 | 50% | +0.49 | 1 | -1.02 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | AMD | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | NVDA | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| rsi2_reversion | JPM | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | +1.82 |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | -0.55 | 1 | 0% | -0.55 | 1 | -1.02 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | AVGO | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| squeeze_breakout | SOL | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| squeeze_breakout | META | +0.00 | +0.00 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | SOL | +0.00 | +0.00 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| squeeze_breakout | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | +0.00 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| squeeze_breakout | QQQ | +0.00 | +0.00 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | AMD | +0.00 | +0.00 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | +0.00 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| rsi2_reversion | META | +0.00 | -0.14 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| donchian_trend | USO | +0.00 | -0.42 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| rsi2_reversion | XOM | +0.00 | -1.01 | +1.97 | 2 | 50% | +0.98 | 3 | +0.75 |
| rsi2_reversion | IWM | -1.01 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AMD | +0.00 | -1.01 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |
| rsi2_reversion | NVDA | +0.00 | -1.02 | -2.62 | 4 | 25% | -0.66 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -1.02 | -1.44 | 2 | 0% | -0.72 | 2 | +0.64 |
| rsi2_reversion | QQQ | +0.00 | -1.02 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| donchian_trend | TLT | +0.00 | -1.03 | -1.03 | 1 | 0% | -1.03 | 2 | -0.94 |
| rsi2_reversion | USO | +0.00 | -1.12 | -1.12 | 1 | 0% | -1.12 | 3 | +0.86 |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 1 | -1.95 |
| rsi2_reversion | AAPL | +0.00 | -1.23 | -1.31 | 4 | 25% | -0.33 | 1 | +0.22 |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| rsi2_reversion | AMZN | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 2 | -0.24 |
| donchian_trend | AAPL | +0.00 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| donchian_trend | TSLA | +0.00 | -2.40 | -2.40 | 2 | 0% | -1.20 | 1 | +0.62 |
| rsi2_reversion | TSLA | -1.01 | -4.49 | -4.49 | 4 | 0% | -1.12 | 2 | -0.45 |

## ML learner, out of sample

Refitted 45 times. 5261 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2352 trades, avg +0.04R. Skipped: 2909, avg -0.04R.

