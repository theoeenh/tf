# Leaderboard – 2026-10-01 13:38 UTC

All versions paper-traded side by side since 2026-09-30 19:00:00 UTC (1h bars), same bars, same $100,000 and 0.40% risk per trade. The live account trades **long + trend + blackout + ML**. Early days are noise: look for a version that stays ahead for weeks, and that beats the random-entry twins.

## The race

| version | return | max_dd | trades | win_rate | avg_r | open | skipped |
|---|---|---|---|---|---|---|---|
| long/short | +0.16% | -0.36% | 0 | – | – | 2 | 0 |
| L/S + news + ML | +0.13% | -0.19% | 0 | – | – | 1 | 0 |
| L/S + news + blackout | +0.03% | -0.21% | 0 | – | – | 1 | 0 |
| long only + learner | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| long only | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| long/short + learner + news | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| long/short + learner | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| L/S + news + trend | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| L/S + news + trend + blackout | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| L/S + news + trend + blackout + ML | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| L/S + news + trend + blackout + ML sizing | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| long + trend + blackout + intraday + ML | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| L/S + trend + blackout + intraday + ML | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| long + trend + blackout + ML + brake 10% | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| long + trend + blackout + ML + global | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| long + trend + blackout + intraday + ML + global | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| long + trend + blackout + ML | +0.00% | +0.00% | 0 | – | – | 0 | 0 |
| random entries, long only (avg of 5) | -0.70% | -1.35% | 5 | 5% | -0.36 | 0 | 0 |
| random entries, long/short (avg of 5) | -0.88% | -1.08% | 6 | 15% | -0.36 | 0 | 0 |

## Strategy leaderboard (long + trend + blackout + ML)

Sum of R (1R = the planned loss) per strategy and asset. *Skipped* = trades the learner refused, followed without money: a negative average means skipping them was right.

No closed trades yet.

## ML learner, out of sample

Refitted 44 times. 5135 trades judged before their outcome was known.
AUC 0.54 (0.50 = no better than chance). Taken: 2288 trades, avg +0.05R. Skipped: 2847, avg -0.01R.

