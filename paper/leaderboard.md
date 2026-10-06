# Leaderboard – 2026-10-06 15:21 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| random entries, long only (avg of 5) | +3.15% | -3.17% | 39 | 66% | +0.30 | 0 | 0 |
| long + trend + blackout + intraday + ML + global | +2.42% | -1.28% | 15 | 40% | -0.04 | 12 | 19 |
| long + trend + blackout + ML + global | +1.83% | -1.90% | 12 | 33% | -0.15 | 11 | 9 |
| long + trend + blackout + intraday + ML + insider | +1.79% | -1.08% | 14 | 29% | -0.24 | 12 | 20 |
| L/S + trend + blackout + intraday + ML | +1.64% | -1.06% | 14 | 29% | -0.22 | 12 | 44 |
| L/S + news + trend + blackout + ML | +1.55% | -1.62% | 10 | 20% | -0.21 | 12 | 24 |
| long only | +1.50% | -2.93% | 12 | 25% | -0.50 | 12 | 0 |
| L/S + news + trend + blackout + ML sizing | +1.39% | -1.97% | 9 | 22% | -0.21 | 9 | 25 |
| long + trend + blackout + ML | +1.31% | -2.20% | 9 | 22% | -0.38 | 12 | 12 |
| long + trend + blackout + ML + brake 10% | +1.31% | -2.20% | 9 | 22% | -0.38 | 12 | 12 |
| long + trend + blackout + ML + insider | +0.95% | -2.55% | 11 | 18% | -0.39 | 12 | 10 |
| long + trend + blackout + intraday + ML | +0.71% | -2.23% | 11 | 18% | -0.45 | 13 | 23 |
| L/S + news + ML | +0.56% | -2.44% | 9 | 22% | -0.39 | 15 | 28 |
| long/short + learner | -0.15% | -3.91% | 16 | 12% | -0.85 | 12 | 16 |
| long only + learner | -1.25% | -4.04% | 10 | 10% | -0.97 | 12 | 10 |
| long/short | -1.44% | -3.79% | 20 | 10% | -0.84 | 14 | 0 |
| long/short + learner + news | -1.87% | -4.69% | 10 | 0% | -1.11 | 10 | 28 |
| L/S + news + trend + blackout | -2.20% | -4.64% | 19 | 16% | -0.67 | 10 | 12 |
| L/S + news + trend | -2.37% | -5.34% | 15 | 7% | -1.07 | 11 | 12 |
| L/S + news + blackout | -2.87% | -4.89% | 17 | 6% | -0.64 | 5 | 28 |
| random entries, long/short (avg of 5) | -5.44% | -5.94% | 66 | 32% | -0.37 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | NVDA | +0.43 | +0.43 | +0.43 | 1 | 100% | +0.43 | 0 | – |
| rsi2_reversion | QQQ | +0.10 | +0.10 | +0.10 | 1 | 100% | +0.10 | 0 | – |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.00 |
| rsi2_reversion | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.32 |
| squeeze_breakout | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +0.10 |
| rsi2_reversion | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -1.41 |
| rsi2_reversion | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -1.28 |
| squeeze_breakout | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.15 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 2 | -0.19 |
| rsi2_reversion | META | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| rsi2_reversion | AAPL | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | -0.42 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| rsi2_reversion | GOOGL | -0.55 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| donchian_trend | SOL | -0.91 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |
| donchian_trend | BTC | -1.72 | -1.72 | -1.72 | 1 | 0% | -1.72 | 1 | -0.60 |

## ML learner, out of sample

Refitted 44 times. 5148 trades judged before their outcome was known.
AUC 0.53 (0.50 = no better than chance). Taken: 2307 trades, avg +0.04R. Skipped: 2841, avg -0.02R.

