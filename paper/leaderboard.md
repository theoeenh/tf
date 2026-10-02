# Leaderboard – 2026-10-02 13:24 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| random entries, long only (avg of 5) | +2.31% | -1.41% | 15 | 70% | +0.49 | 0 | 0 |
| L/S + news + trend | +0.13% | -0.99% | 1 | 0% | -1.02 | 9 | 3 |
| long only + learner | -0.16% | -1.28% | 1 | 0% | -1.01 | 8 | 0 |
| long only | -0.34% | -1.37% | 1 | 0% | -1.01 | 10 | 0 |
| long + trend + blackout + intraday + ML | -0.61% | -1.10% | 9 | 33% | -0.17 | 0 | 4 |
| long + trend + blackout + ML + brake 10% | -0.66% | -0.97% | 8 | 25% | -0.21 | 0 | 4 |
| long + trend + blackout + ML | -0.66% | -0.97% | 8 | 25% | -0.21 | 0 | 4 |
| long + trend + blackout + intraday + ML + global | -0.68% | -1.28% | 13 | 38% | -0.13 | 0 | 0 |
| L/S + trend + blackout + intraday + ML | -0.69% | -1.13% | 10 | 30% | -0.17 | 0 | 15 |
| random entries, long/short (avg of 5) | -0.69% | -1.37% | 22 | 41% | -0.08 | 0 | 0 |
| long + trend + blackout + ML + global | -0.74% | -1.28% | 12 | 33% | -0.15 | 0 | 0 |
| L/S + news + trend + blackout + ML | -0.82% | -1.02% | 10 | 20% | -0.21 | 0 | 12 |
| long/short + learner + news | -0.90% | -1.97% | 3 | 0% | -1.02 | 7 | 4 |
| L/S + news + trend + blackout + ML sizing | -0.98% | -1.41% | 10 | 20% | -0.21 | 0 | 12 |
| long/short + learner | -1.27% | -1.54% | 3 | 0% | -1.02 | 9 | 4 |
| L/S + news + ML | -1.35% | -1.60% | 2 | 0% | -1.15 | 10 | 5 |
| L/S + news + trend + blackout | -1.38% | -1.53% | 12 | 25% | -0.30 | 0 | 8 |
| long/short | -1.51% | -2.22% | 4 | 0% | -1.19 | 12 | 0 |
| L/S + news + blackout | -2.49% | -2.80% | 13 | 8% | -0.48 | 0 | 13 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

| strategy | asset | R 7d | R 30d | R all | trades | win % | avg R | skipped | skipped avg R |
|---|---|---|---|---|---|---|---|---|---|
| rsi2_reversion | NVDA | +0.43 | +0.43 | +0.43 | 1 | 100% | +0.43 | 0 | – |
| rsi2_reversion | QQQ | +0.10 | +0.10 | +0.10 | 1 | 100% | +0.10 | 0 | – |
| donchian_trend | BTC | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.60 |
| donchian_trend | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | -0.28 |
| squeeze_breakout | ETH | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +0.19 |
| squeeze_breakout | SOL | +0.00 | +0.00 | +0.00 | 0 | – | – | 1 | +0.51 |
| rsi2_reversion | META | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| rsi2_reversion | AAPL | -0.08 | -0.08 | -0.08 | 1 | 0% | -0.08 | 0 | – |
| squeeze_breakout | USO | -0.15 | -0.15 | -0.15 | 1 | 0% | -0.15 | 0 | – |
| rsi2_reversion | MSFT | -0.42 | -0.42 | -0.42 | 1 | 0% | -0.42 | 0 | – |
| rsi2_reversion | GOOGL | -0.55 | -0.55 | -0.55 | 1 | 0% | -0.55 | 0 | – |
| donchian_trend | SOL | -0.91 | -0.91 | -0.91 | 1 | 0% | -0.91 | 0 | – |

## ML learner, out of sample

Refitted 44 times. 5147 trades judged before their outcome was known.
AUC 0.54 (0.50 = no better than chance). Taken: 2296 trades, avg +0.05R. Skipped: 2851, avg -0.01R.

