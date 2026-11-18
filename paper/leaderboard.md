# Leaderboard – 2026-11-18 14:29 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| L/S + news + trend | +0.23% | -11.21% | 108 | 26% | -0.12 | 16 | 180 |
| long/short | -1.15% | -12.55% | 276 | 28% | -0.15 | 27 | 0 |
| L/S + news + trend + blackout | -4.81% | -8.16% | 92 | 27% | -0.25 | 9 | 244 |
| long + trend + blackout + ML + brake 10% | -9.08% | -10.15% | 56 | 20% | -0.50 | 0 | 54 |
| L/S + news + blackout | -10.28% | -10.79% | 116 | 30% | -0.22 | 5 | 350 |
| long/short + learner + news | -10.44% | -13.95% | 120 | 25% | -0.26 | 13 | 292 |
| long/short + learner | -10.93% | -14.71% | 148 | 26% | -0.22 | 19 | 260 |
| L/S + trend + blackout + intraday + ML | -14.07% | -15.37% | 108 | 29% | -0.32 | 4 | 474 |
| long + trend + blackout + intraday + ML | -14.32% | -15.32% | 78 | 22% | -0.51 | 3 | 132 |
| long + trend + blackout + intraday + ML + global | -14.38% | -15.76% | 85 | 27% | -0.43 | 1 | 125 |
| long + trend + blackout + ML + insider | -14.87% | -15.77% | 62 | 13% | -0.70 | 2 | 70 |
| L/S + news + ML | -14.91% | -15.76% | 85 | 20% | -0.50 | 1 | 326 |
| long + trend + blackout + intraday + ML + insider | -15.28% | -16.15% | 77 | 18% | -0.56 | 3 | 135 |
| long + trend + blackout + ML + global | -15.64% | -16.45% | 68 | 15% | -0.67 | 1 | 65 |
| L/S + news + trend + blackout + ML | -15.70% | -16.27% | 87 | 21% | -0.50 | 4 | 248 |
| long + trend + blackout + ML | -16.30% | -17.20% | 66 | 14% | -0.69 | 2 | 67 |
| L/S + news + trend + blackout + ML sizing | -18.72% | -19.86% | 78 | 22% | -0.50 | 4 | 248 |
| random entries, long/short (avg of 5) | -20.97% | -22.68% | 564 | 35% | -0.20 | 0 | 0 |
| long only + learner | -24.23% | -24.53% | 95 | 11% | -0.75 | 4 | 86 |
| long only | -27.28% | -28.78% | 150 | 12% | -0.76 | 6 | 0 |
| random entries, long only (avg of 5) | -36.01% | -39.20% | 343 | 17% | -0.68 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| donchian_trend | AMD | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 1 | -1.00 |
| donchian_trend | BTC | +0.00 | +0.00 | -1.72 | 1 | 0% | -1.72 | 3 | -1.17 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| donchian_trend | GOOGL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.02 |
| donchian_trend | NVDA | +0.00 | +0.00 | -1.01 | 1 | 0% | -1.01 | 0 | – |
| donchian_trend | META | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.01 |
| donchian_trend | SOL | +0.00 | +0.00 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | QQQ | +0.00 | +0.00 | -1.33 | 1 | 0% | -1.33 | 0 | – |
| rsi2_reversion | AMD | +0.00 | +0.00 | -2.02 | 2 | 0% | -1.01 | 1 | -1.01 |
| donchian_trend | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 3 | +2.02 |
| rsi2_reversion | SOL | +0.00 | +0.00 | -1.45 | 1 | 0% | -1.45 | 2 | -1.41 |
| rsi2_reversion | META | +0.00 | +0.00 | -1.23 | 5 | 20% | -0.25 | 0 | – |
| rsi2_reversion | GOOGL | +0.00 | +0.00 | +0.42 | 3 | 33% | +0.14 | 0 | – |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.43 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -1.38 |
| rsi2_reversion | AVGO | +0.00 | +0.00 | -2.03 | 2 | 0% | -1.01 | 0 | – |
| squeeze_breakout | TSLA | +0.00 | +0.00 | -1.16 | 1 | 0% | -1.16 | 1 | -1.95 |
| squeeze_breakout | NVDA | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.15 |
| squeeze_breakout | QQQ | +0.00 | +0.00 | -0.05 | 1 | 0% | -0.05 | 0 | – |
| squeeze_breakout | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.75 |
| squeeze_breakout | XOM | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +2.91 |
| squeeze_breakout | USO | +0.00 | +0.00 | -0.15 | 1 | 0% | -0.15 | 2 | +0.11 |
| rsi2_reversion | QQQ | +0.00 | +0.00 | -0.92 | 2 | 50% | -0.46 | 2 | -1.02 |
| rsi2_reversion | NVDA | +0.00 | +0.00 | -1.60 | 3 | 33% | -0.53 | 1 | -1.02 |
| squeeze_breakout | MSFT | +0.00 | +0.00 | -0.50 | 1 | 0% | -0.50 | 0 | – |
| squeeze_breakout | META | +0.00 | +0.00 | -0.70 | 1 | 0% | -0.70 | 1 | -0.36 |
| squeeze_breakout | GOOGL | +0.00 | +0.00 | -0.96 | 1 | 0% | -0.96 | 0 | – |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 4 | -0.88 |
| squeeze_breakout | AMZN | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.16 |
| squeeze_breakout | AMD | +0.00 | +0.00 | -0.44 | 1 | 0% | -0.44 | 0 | – |
| squeeze_breakout | AAPL | +0.00 | +0.00 | -0.49 | 1 | 0% | -0.49 | 1 | -1.02 |
| rsi2_reversion | TLT | -1.03 | -0.03 | -0.03 | 2 | 50% | -0.02 | 2 | -0.76 |
| donchian_trend | TSLA | +0.00 | -1.01 | -2.40 | 2 | 0% | -1.20 | 1 | +0.62 |
| donchian_trend | MSFT | +0.00 | -1.01 | +0.97 | 2 | 50% | +0.49 | 1 | -1.02 |
| rsi2_reversion | XOM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 4 | +1.31 |
| rsi2_reversion | IWM | +0.00 | -1.01 | -1.01 | 1 | 0% | -1.01 | 1 | -1.01 |
| rsi2_reversion | AMZN | +0.00 | -1.02 | -2.03 | 2 | 0% | -1.02 | 3 | -0.50 |
| squeeze_breakout | JPM | -1.02 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| squeeze_breakout | TLT | +0.00 | -1.02 | -1.02 | 1 | 0% | -1.02 | 0 | – |
| rsi2_reversion | USO | +0.00 | -1.12 | -1.12 | 1 | 0% | -1.12 | 3 | +0.86 |
| rsi2_reversion | AAPL | +0.00 | -1.23 | -1.31 | 4 | 25% | -0.33 | 1 | +0.22 |
| rsi2_reversion | MSFT | -1.01 | -2.09 | -2.51 | 3 | 0% | -0.84 | 2 | +0.84 |
| donchian_trend | USO | +0.00 | -2.41 | -0.42 | 3 | 67% | -0.14 | 1 | -1.01 |
| rsi2_reversion | TSLA | +0.00 | -2.46 | -4.49 | 4 | 0% | -1.12 | 4 | -0.73 |
| rsi2_reversion | JPM | -2.67 | -2.67 | -2.67 | 2 | 0% | -1.33 | 2 | +1.82 |
| donchian_trend | TLT | +0.00 | -2.90 | -2.90 | 3 | 0% | -0.97 | 0 | – |
| donchian_trend | AAPL | -1.02 | -3.16 | -3.16 | 3 | 0% | -1.05 | 1 | -1.93 |

## ML learner, out of sample

Refitted 45 times. 5270 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2353 trades, avg +0.03R. Skipped: 2917, avg -0.03R.

