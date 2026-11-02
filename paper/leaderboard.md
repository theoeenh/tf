# Leaderboard – 2026-11-02 15:37 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | -1.66% | -10.49% | 84 | 26% | -0.03 | 11 | 107 |
| long/short | -5.54% | -12.55% | 177 | 26% | -0.23 | 21 | 0 |
| long + trend + blackout + intraday + ML | -7.62% | -8.33% | 63 | 27% | -0.39 | 1 | 101 |
| L/S + news + trend + blackout + ML | -7.86% | -8.65% | 60 | 23% | -0.37 | 7 | 149 |
| long + trend + blackout + ML | -8.78% | -9.95% | 52 | 15% | -0.59 | 1 | 47 |
| long + trend + blackout + intraday + ML + global | -8.84% | -10.39% | 71 | 24% | -0.45 | 1 | 97 |
| long + trend + blackout + ML + insider | -8.84% | -10.02% | 54 | 17% | -0.60 | 1 | 44 |
| L/S + trend + blackout + intraday + ML | -8.84% | -10.36% | 73 | 27% | -0.25 | 5 | 304 |
| L/S + news + trend + blackout + ML sizing | -8.97% | -10.25% | 52 | 25% | -0.38 | 7 | 150 |
| long + trend + blackout + ML + global | -9.03% | -10.06% | 56 | 20% | -0.52 | 1 | 42 |
| long + trend + blackout + ML + brake 10% | -9.11% | -10.28% | 50 | 16% | -0.52 | 1 | 48 |
| long + trend + blackout + intraday + ML + insider | -9.56% | -10.76% | 67 | 22% | -0.46 | 1 | 98 |
| long/short + learner + news | -10.27% | -10.96% | 86 | 22% | -0.36 | 8 | 196 |
| L/S + news + blackout | -10.95% | -10.95% | 89 | 24% | -0.33 | 5 | 217 |
| L/S + news + ML | -11.08% | -12.15% | 64 | 22% | -0.41 | 5 | 214 |
| L/S + news + trend + blackout | -11.25% | -12.90% | 89 | 26% | -0.30 | 6 | 118 |
| long/short + learner | -13.20% | -13.88% | 90 | 21% | -0.42 | 8 | 188 |
| long only | -14.64% | -16.24% | 101 | 15% | -0.67 | 11 | 0 |
| long only + learner | -15.40% | -15.40% | 56 | 11% | -0.76 | 4 | 74 |
| random entries, long only (avg of 5) | -16.36% | -21.90% | 226 | 22% | -0.57 | 0 | 0 |
| random entries, long/short (avg of 5) | -23.64% | -23.76% | 366 | 32% | -0.32 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | XOM | +0.00 | +2.98 | +2.98 | 1 | 100% | +2.98 | 2 | +1.66 |
| donchian_trend | MSFT | +0.00 | +1.98 | +1.98 | 1 | 100% | +1.98 | 1 | -1.02 |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | TLT | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.42 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| squeeze_breakout | QQQ | +0.00 | -0.05 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | NVDA | +0.00 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| donchian_trend | USO | -2.41 | -0.42 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| squeeze_breakout | AMD | +0.00 | -0.44 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | -0.49 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | -0.50 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | -0.70 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | GOOGL | +0.00 | -0.96 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| donchian_trend | AMD | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | NVDA | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | AVGO | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | -1.02 | -1.56 | 2 | 0% | -0.78 | 0 | – |
| rsi2_reversion | MSFT | +0.00 | -1.02 | -1.44 | 2 | 0% | -0.72 | 1 | +1.18 |
| rsi2_reversion | QQQ | +0.00 | -1.02 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| rsi2_reversion | USO | -1.12 | -1.12 | -1.12 | 1 | 0% | -1.12 | 2 | +2.07 |
| rsi2_reversion | META | +0.00 | -1.16 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | -1.16 | -1.16 | 1 | 0% | -1.16 | 0 | – |
| rsi2_reversion | AAPL | -0.21 | -1.23 | -1.31 | 4 | 25% | -0.33 | 0 | – |
| donchian_trend | QQQ | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| squeeze_breakout | SOL | +0.00 | -1.33 | -1.33 | 1 | 0% | -1.33 | 3 | -0.55 |
| donchian_trend | TSLA | +0.00 | -1.39 | -1.39 | 1 | 0% | -1.39 | 1 | +0.62 |
| rsi2_reversion | SOL | +0.00 | -1.45 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| donchian_trend | BTC | +0.00 | -1.72 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| rsi2_reversion | TSLA | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 2 | -0.45 |
| rsi2_reversion | AMZN | +0.00 | -2.03 | -2.03 | 2 | 0% | -1.02 | 0 | – |
| donchian_trend | AAPL | +0.00 | -2.14 | -2.14 | 2 | 0% | -1.07 | 1 | -1.93 |
| rsi2_reversion | AMD | +0.00 | -3.04 | -3.04 | 3 | 0% | -1.01 | 1 | -1.72 |
| rsi2_reversion | NVDA | +0.00 | -3.05 | -2.62 | 4 | 25% | -0.66 | 0 | – |

## ML learner, out of sample

Refitted 45 times. 5241 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2354 trades, avg +0.04R. Skipped: 2887, avg -0.03R.

