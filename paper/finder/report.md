# Strategy finder – 2026-11-12

**6528 strategies tried so far** (every attempt counts in the luck check, below). Hourly (live universe): search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30. S&P 500 daily: search 2017-01-01 → 2022-12-31, validation 2023-01-01 → 2025-06-30. Both: vault from 2025-07-01 (sealed). 14 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13/14 | `fd8a0ed44d` insider_sector_laggard(buyers=1, lag=0.2) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.271 | +0.70 | +1.308 | +0.35 / +0.02 | +0.14 / -0.14 | +21.2% | 0.00 | 75% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `67eb95bdc3` insider_sector_wave(buyers=2, companies=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.904 | +0.67 | +1.191 | +0.12 / -0.11 | +0.06 / -0.01 | +1.8% | 0.00 | 65% | 3/3 | 81% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f9ccddc802` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.7) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.687 | +0.65 | +1.241 | +0.24 / +0.08 | +0.57 / +0.15 | +29.0% | 0.00 | 77% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `8916c925de` insider_deep_value(buyers=3, below=0.42) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.713 | +0.64 | +0.587 | +0.08 / +0.01 | +0.13 / -0.18 | +5.7% | 0.00 | 67% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `fa544cc8ce` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.35) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.881 | +0.64 | +0.489 | +0.39 / +0.11 | +0.60 / +0.13 | +29.1% | 0.00 | 67% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `0c7113d1ab` insider_sector_laggard(buyers=1, lag=0.2) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +0.974 | +0.64 | +0.876 | +0.26 / +0.01 | +0.06 / -0.10 | +7.7% | 0.00 | 72% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `ca8c628ca0` sector_washout_calm(drop=0.14, bounce=2, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.102 | +0.63 | +0.571 | +0.27 / +0.09 | +0.37 / +0.02 | +23.9% | 0.00 | 74% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `ce023528e4` sector_washout_calm(drop=0.14, bounce=4, max_vol=0.3) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +2.039 | +0.62 | +1.169 | +0.30 / +0.14 | +0.46 / +0.08 | +21.7% | 0.00 | 67% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `99d3a04982` insider_fresh_wave(buyers=2, companies=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.742 | +0.61 | +2.179 | +0.04 / +0.04 | +0.04 / -0.03 | +1.1% | 0.00 | 71% | 3/3 | 81% | search: deflated Sharpe >= 0.90 |
| 13/14 | `52e69f2b97` insider_stress_low_short(drop=0.1, max_rank=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.640 | +0.60 | +0.713 | +0.40 / +0.02 | +0.33 / +0.03 | +30.6% | 0.00 | 62% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `6f40333ad9` sector_washout_calm(drop=0.14, bounce=4, max_vol=0.21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.888 | +0.60 | +1.695 | +0.17 / +0.09 | +0.42 / +0.07 | +19.3% | 0.00 | 85% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `17f8874c25` insider_sector_laggard(buyers=1, lag=0.05) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.450 | +0.59 | +1.632 | +0.08 / -0.05 | +0.07 / -0.03 | +4.8% | 0.00 | 68% | 3/3 | 70% | search: deflated Sharpe >= 0.90 |
| 13/14 | `aaf65c5351` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.300 | +0.59 | +1.245 | +0.37 / +0.09 | +0.35 / +0.10 | +19.6% | 0.00 | 86% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `4ee26e6dda` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.3) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +2.300 | +0.59 | +1.245 | +0.26 / +0.21 | +0.59 / +0.28 | +27.2% | 0.00 | 86% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `83ec2e8ba0` sector_washout_calm(drop=0.14, bounce=4, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.115 | +0.58 | +1.859 | +0.29 / +0.10 | +0.39 / +0.04 | +23.1% | 0.00 | 79% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `e24c15fd2c` insider_deep_value(buyers=3, below=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.171 | +0.58 | +0.619 | +0.02 / -0.03 | +0.15 / -0.15 | +11.1% | 0.00 | 64% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `e04023c4d4` insider_deep_value(buyers=1, below=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +1.415 | +0.58 | +0.562 | +0.14 / +0.04 | +0.33 / +0.03 | +11.9% | 0.00 | 67% | 3/3 | 65% | search: deflated Sharpe >= 0.90 |
| 13/14 | `5b907a23fc` insider_deep_value(buyers=4, below=0.21) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.209 | +0.58 | +0.663 | +0.02 / -0.01 | +0.19 / -0.08 | +11.5% | 0.00 | 59% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `21bd44a5ff` insider_deep_value(buyers=1, below=0.29) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +1.373 | +0.58 | +0.343 | +0.14 / +0.04 | +0.30 / +0.01 | +11.5% | 0.00 | 66% | 3/3 | 67% | search: deflated Sharpe >= 0.90 |
| 13/14 | `68ca8b871d` insider_sector_laggard(buyers=1, lag=0.07) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.533 | +0.57 | +1.573 | +0.09 / -0.01 | +0.03 / -0.06 | +1.9% | 0.00 | 70% | 3/3 | 70% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f562cba6d6` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.801 | +0.57 | +2.310 | +0.24 / +0.06 | +0.62 / +0.10 | +36.1% | 0.00 | 86% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `56814bb4c7` sector_washout_calmest(drop=0.15, bounce=4, k=14) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.383 | +0.56 | +0.405 | +0.29 / +0.11 | +0.76 / +0.18 | +29.8% | 0.00 | 70% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `56f63f893b` sector_washout_calmest(drop=0.15, bounce=4, k=10) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.349 | +0.56 | +0.466 | +0.16 / +0.10 | +0.71 / +0.13 | +25.9% | 0.00 | 67% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `cdd7bc6c72` insider_underwater(buyers=1, discount=0.21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily | +1.848 | +0.56 | +2.561 | +0.34 / +0.11 | +0.40 / -0.03 | +1.9% | 0.00 | 74% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `eed17f8ff3` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.5) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.501 | +0.56 | +0.722 | +0.32 / +0.11 | +0.69 / +0.17 | +36.4% | 0.00 | 70% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |

## The luck check (deflated Sharpe)

- **6528 tries count.** Replaying history with no skill in any of them, the luckiest one reaches a t-statistic of **5.28** on average: that is the bar.
- The same bar as **8886111 independent tries** would set: most tries are versions of the same few ideas and move together.
- A strategy is judged on the part of its weekly returns that the stocks it may trade do not explain (being invested in a rising market is not skill).
- **0 strategies clear the bar** (deflated Sharpe >= 0.90).
- 12 tries have no weekly returns stored: each counts as one more independent try, and cannot pass until it is scored again.
- Highest t-statistic: 3.12, `1320c0ce23` insider_consensus(votes=3, window=10) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Utilities, daily (deflated Sharpe 0.01).
- Stocks each try was tested on: members of the day: 5915, fixed list: 601, not scored again: 12.
- **Vault tests are on hold:** every strategy was scored again on 2026-11-12 with a corrected universe and luck check; the user looks at the result before any one-shot vault test runs

## Campaigns: each idea refined round by round (max 5 rounds)

1509 ideas tried; **493 still improving** (search ICIR >= 0.2), 976 dropped below the bar, 40 finished their 5 rounds.

| idea → best version so far | rounds | tried | gates by round | ICIR | status |
|---|---|---|---|---|---|
| `916b5053b5` sector_washout(drop=0.07, bounce=10) · stop_atr=3.0, rr=None, max_bars=10 · no trend filter · sector Materials, daily | 5 | 35 | 11 → 13 → 13 → 13 → 13 → 13 | +0.91 | finished: 5 rounds |
| `9724ab3ad8` insider_market_stress(buyers=3, drop=0.08) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 4 | 27 | 9 → 9 → 9 → 10 → 10 | +0.84 | improving |
| `cd40ac4978` sector_washout(drop=0.15, bounce=14) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 1 | 4 | 12 → 13 | +0.83 | improving |
| `2791eaacdc` sector_washout(drop=0.07, bounce=10) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Materials, daily | 4 | 24 | 9 → 12 → 12 → 12 → 12 | +0.78 | improving |
| `0026dae54e` insider_wave_stress(companies=10, drop=0.14) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 4 | 20 | 8 → 10 → 11 → 11 → 11 | +0.76 | improving |
| `59c16248a4` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.7) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 5 | 30 | 12 → 13 → 13 → 13 → 13 → 13 | +0.72 | finished: 5 rounds |
| `4973def76d` sector_size_washout(drop=0.15, bounce=7, groups=1) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 4 | 23 | 9 → 12 → 13 → 13 → 13 | +0.72 | improving |
| `aba88232f8` sector_washout(drop=0.15, bounce=7) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 3 | 13 | 12 → 13 → 13 → 13 | +0.72 | improving |
| `fe25ab1ee8` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 4 | 24 | 12 → 13 → 13 → 13 → 13 | +0.71 | improving |
| `fd8a0ed44d` insider_sector_laggard(buyers=1, lag=0.2) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 2 | 3 | 13 → 13 → 13 | +0.70 | improving |
| `593407bed8` sector_washout_calm(drop=0.14, bounce=4, max_vol=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 4 | 31 | 12 → 12 → 12 → 13 → 13 | +0.70 | improving |
| `0b74ac87ec` sector_washout_leaders(drop=0.15, bounce=7, within=0.5) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 5 | 28 | 11 → 13 → 13 → 13 → 13 → 13 | +0.69 | finished: 5 rounds |
| `67eb95bdc3` insider_sector_wave(buyers=2, companies=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 3 | 20 | 10 → 13 → 13 → 13 | +0.67 | improving |
| `cba12a7c55` insider_market_stress(buyers=2, drop=0.02) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 2 | 14 | 9 → 11 → 11 | +0.65 | improving |
| `8916c925de` insider_deep_value(buyers=3, below=0.42) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | 3 | 12 | 12 → 13 → 13 → 13 | +0.64 | improving |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| insider_sector_laggard | 131 | 13/14 | +0.70 | `fd8a0ed44d` insider_sector_laggard(buyers=1, lag=0.2) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_sector_wave | 154 | 13/14 | +0.67 | `67eb95bdc3` insider_sector_wave(buyers=2, companies=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| sector_washout_calm | 166 | 13/14 | +0.65 | `f9ccddc802` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.7) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_deep_value | 123 | 13/14 | +0.64 | `8916c925de` insider_deep_value(buyers=3, below=0.42) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_fresh_wave | 129 | 13/14 | +0.61 | `99d3a04982` insider_fresh_wave(buyers=2, companies=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_stress_low_short | 179 | 13/14 | +0.60 | `52e69f2b97` insider_stress_low_short(drop=0.1, max_rank=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| sector_washout_calmest | 109 | 13/14 | +0.56 | `56814bb4c7` sector_washout_calmest(drop=0.15, bounce=4, k=14) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_underwater | 157 | 13/14 | +0.56 | `cdd7bc6c72` insider_underwater(buyers=1, discount=0.21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily |
| insider_fresh | 192 | 13/14 | +0.52 | `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_sector_stress | 117 | 13/14 | +0.51 | `7a1f0745d5` insider_sector_stress(buyers=1, drop=0.08) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| sector_washout | 110 | 13/14 | +0.50 | `853d3e7180` sector_washout(drop=0.15, bounce=6) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| sector_size_washout | 65 | 13/14 | +0.50 | `bba4dfeb0a` sector_size_washout(drop=0.15, bounce=7, groups=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_calm_stress | 38 | 13/14 | +0.48 | `b92239de9e` insider_calm_stress(buyers=1, drop=0.11, max_vol=0.5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| sector_washout_leaders | 84 | 13/14 | +0.47 | `ab4da6fbde` sector_washout_leaders(drop=0.15, bounce=4, within=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_calm_underwater | 87 | 13/14 | +0.46 | `06b0e5e622` insider_calm_underwater(buyers=1, discount=0.28, max_vol=0.98) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_underwater_z | 92 | 13/14 | +0.46 | `5a610d27de` insider_underwater_z(buyers=1, z=4.2) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily |
| insider_opportunistic | 85 | 13/14 | +0.46 | `8197fb6c89` insider_opportunistic(buyers=3, years=2) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_underwater_turn | 107 | 13/14 | +0.45 | `6ec2490782` insider_underwater_turn(discount=0.29, confirm=stock, bounce=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_turn | 71 | 13/14 | +0.45 | `9f06c0dd75` insider_turn(buyers=2, window=14) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_wave_stress | 217 | 13/14 | +0.45 | `d4bee04c32` insider_wave_stress(companies=2, drop=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_defensive | 103 | 13/14 | +0.38 | `8596775757` insider_defensive(gap=730, which=three) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_calm_low_short | 44 | 13/14 | +0.36 | `82a33db827` insider_calm_low_short(max_vol=0.5, max_rank=0.5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_calm_fresh | 267 | 13/14 | +0.35 | `3cfdb091d7` insider_calm_fresh(gap=511, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_repeat | 132 | 13/14 | +0.34 | `88cd34b3d7` insider_repeat(buys=2, window=42) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| insider_opportunistic_low_short | 152 | 13/14 | +0.33 | `131bbe7bb6` insider_opportunistic_low_short(buyers=1, max_rank=0.29) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_union | 80 | 13/14 | +0.32 | `925dfd221c` insider_union(parts=2, gap=42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_clean | 108 | 13/14 | +0.31 | `e493d0f7f7` insider_clean(buyers=2, quiet=365) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_low_short | 120 | 13/14 | +0.30 | `333e20853e` insider_low_short(buyers=3, max_rank=0.42) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_consensus | 130 | 13/14 | +0.30 | `bcefa43baf` insider_consensus(votes=2, window=42) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| insider_after_earnings | 106 | 13/14 | +0.27 | `e6600973ed` insider_after_earnings(buyers=3, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| calm_union | 31 | 13/14 | +0.26 | `23650b32b9` calm_union(parts=1, gap=42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_stress_leader | 37 | 13/14 | +0.25 | `23b1f31b59` insider_stress_leader(drop=0.1, lead=0.0) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_conviction | 121 | 13/14 | +0.22 | `bb35082f6c` insider_conviction(buyers=3, min_bp=3.92) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_low_vol | 64 | 12/14 | +0.57 | `b82346dab7` insider_low_vol(buyers=2, max_rank=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_accumulation | 84 | 12/14 | +0.55 | `3c0740aef5` insider_accumulation(buyers=4, volume=1.47) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_cluster | 127 | 12/14 | +0.52 | `0cd9aea7bb` insider_cluster(buyers=2, days=126) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_top_union | 50 | 12/14 | +0.46 | `4557e9e8f6` insider_top_union(parts=4, gap=20) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily |
| insider_market_stress | 142 | 12/14 | +0.44 | `82270504af` insider_market_stress(buyers=1, drop=0.03) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_top_exec | 145 | 12/14 | +0.42 | `076c384abb` insider_top_exec(min_value=34300, who=ceo) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_wave_low_short | 195 | 12/14 | +0.37 | `9ced48cd35` insider_wave_low_short(companies=1, max_rank=0.35) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_fresh_officer | 203 | 12/14 | +0.36 | `4bc09e288b` insider_fresh_officer(buyers=1, gap=353) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_calm_fresh_turn | 52 | 12/14 | +0.30 | `3ac1db6d41` insider_calm_fresh_turn(max_vol=0.3, confirm=stock, wait=10) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_opportunistic_exec | 77 | 12/14 | +0.28 | `72695c5770` insider_opportunistic_exec(who=ceo_cfo, years=2) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Information Technology, daily |
| insider_opportunistic_wave | 133 | 12/14 | +0.21 | `db1836a625` insider_opportunistic_wave(companies=5, window=60) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Health Care, daily |
| insider_filing_lag | 52 | 11/14 | +0.45 | `b1a2116e9d` insider_filing_lag(mode=prompt, buyers=2) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily |
| insider_ml | 11 | 11/14 | +0.24 | `458df83e04` insider_ml(model=ridge, keep=0.7) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_fund | 79 | 11/14 | +0.23 | `356351f553` insider_fund(buyers=2, feature=f_sue) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| vwap | 214 | 10/14 | +0.30 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 |
| insider_high_short | 44 | 10/14 | +0.25 | `33183d91a6` insider_high_short(buyers=1, min_rank=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| stock_washout | 8 | 10/14 | +0.13 | `2eb2e5708d` stock_washout(drop=0.15, bounce=3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_reclaim | 8 | 10/14 | +0.01 | `0cd1e753e2` insider_reclaim(dip=0.2, within=20) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_confirm | 20 | 9/14 | +0.32 | `49f5df1e88` insider_confirm(buyers=2, wait=42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| sector_reversal | 8 | 9/14 | +0.26 | `29f76df1ba` sector_reversal(lookback=5, bottom=0.02) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily |
| ml_rank_short | 4 | 9/14 | +0.16 | `1d6baf4151` ml_rank_short(model=ridge, top=0.02) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| ml_rank | 4 | 9/14 | +0.14 | `9757090abb` ml_rank(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| ml_rank_fund | 4 | 9/14 | +0.12 | `2bf8b0521a` ml_rank_fund(model=ridge, top=0.02) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| stress_calm_leaders | 8 | 9/14 | -0.02 | `3c6edd688c` stress_calm_leaders(drop=0.05, max_vol=0.4) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_momentum | 32 | 8/14 | +0.30 | `1b4b882975` insider_momentum(buyers=2, min_rank=0.49) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| same_month_seasonality | 79 | 8/14 | +0.26 | `b17b28b608` same_month_seasonality(top=0.05, years=5) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Information Technology, daily |
| volume_breakout | 72 | 8/14 | +0.26 | `2f7b678096` volume_breakout(n=20, m=3.5) · stop_atr=1.5, rr=None, max_bars=3 |
| donchian | 94 | 7/14 | +0.34 | `e4dbf9e4e1` donchian(n=118, trend_ma=140) · stop_atr=1.5, rr=None, max_bars=2 · no trend filter |
| insider_big_buy | 72 | 7/14 | +0.18 | `468c8ed48c` insider_big_buy(min_value=500000, officer=False) · stop_atr=4.0, rr=None, max_bars=40 · S&P 400 (mid), daily |
| lead_lag_sector | 8 | 7/14 | +0.06 | `b64cceebc6` lead_lag_sector(lead=0.05, days=5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| opening_range | 24 | 6/14 | +0.53 | `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter |
| xs_reversal | 30 | 6/14 | +0.15 | `d2867573f6` xs_reversal(lookback=6, bottom=4) · stop_atr=1.5, rr=None, max_bars=1 |
| momentum_pullback | 8 | 6/14 | +0.10 | `bc0058b8bb` momentum_pullback(top=0.1, bottom=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| reversal_5d | 36 | 6/14 | +0.08 | `71c1696dd3` reversal_5d(bottom=0.02) · stop_atr=2.5, rr=None, max_bars=5 · S&P 400 (mid), daily |
| xs_momentum | 30 | 6/14 | +0.05 | `7ffb46fdcc` xs_momentum(lookback=120, top=4) · stop_atr=1.0, rr=1.5, max_bars=6 |
| rsi2 | 41 | 6/14 | -0.00 | `9dcb4f23b3` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=1 |
| momentum_12_1 | 36 | 6/14 | -0.19 | `a78793293b` momentum_12_1(top=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 400 (mid), daily |
| intraday_momentum | 15 | 6/14 | -0.21 | `67dfe34cd4` intraday_momentum(k=1.0) · stop_atr=2.5, rr=None, trail_atr=3.0 |
| squeeze | 21 | 6/14 | -0.36 | `5f107ac95d` squeeze() · stop_atr=3.0, rr=None, trail_atr=4.0, adx_threshold=25.0 · stocks+etfs |
| earnings_overreaction | 27 | 5/14 | +0.19 | `9895a359e5` earnings_overreaction(z=2.5, volume=1.5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · S&P 500, daily |
| gap_fade | 15 | 5/14 | -0.17 | `63e0bb1295` gap_fade(g=1.0) · stop_atr=1.5, rr=None, max_bars=1 |
| liquidity_sweep | 20 | 5/14 | -0.25 | `ad23174e9f` liquidity_sweep(n=35, k=0.25) · stop_atr=1.5, rr=None, max_bars=1 |
| turn_of_month | 4 | 4/14 | +0.16 | `7fe97d96af` turn_of_month(days_before=1, max_vol=0.4) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily |
| low_vol_monthly | 8 | 4/14 | -0.05 | `e547e7de94` low_vol_monthly(bottom=0.1, trend=200) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| earnings_drift | 15 | 4/14 | -0.24 | `820a1f2904` earnings_drift(x=0.5) · stop_atr=2.0, rr=2.0 |
| btc_lead | 10 | 4/14 | -0.52 | `498531f181` btc_lead(k=0.75) · stop_atr=1.5, rr=None, max_bars=1 |
| sector_momentum | 8 | 3/14 | -0.06 | `bf459ffb74` sector_momentum(top=2, ma=200) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| momentum_low_vol | 8 | 3/14 | -0.07 | `cbfb01bd5f` momentum_low_vol(top=0.05, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| earnings_reaction | 27 | 3/14 | -0.10 | `b1a0e34302` earnings_reaction(z=2.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 500, daily |
| high_52w | 36 | 3/14 | -0.32 | `59732b89d7` high_52w(within=0.03) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| momentum_low_short | 8 | 2/14 | -0.09 | `742a275317` momentum_low_short(top=0.1, max_rank=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| overnight_momentum | 8 | 2/14 | -0.09 | `26b90594bc` overnight_momentum(lookback=60, top=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| smooth_momentum | 8 | 2/14 | -0.13 | `66f87d0fbe` smooth_momentum(top=0.1, within=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| residual_momentum | 4 | 2/14 | -0.15 | `1ca63533a6` residual_momentum(top=0.05, lookback=252) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_dip | 144 | 1/14 | +nan | `4ee8edec35` insider_dip(buyers=2, days=30, drop=0.1) · stop_atr=3.0, rr=None, max_bars=10 · S&P 600 (small), daily |

## The loop: 5019 children tried (improved versions aimed at a parent's failures)

- breadth failed: 93 tried, best 9/14 gates
- edge peaks at 2 bars, exit at 1: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 12: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 5: 1 tried, best 7/14 gates
- edge peaks at 20 bars, exit at 5: 1 tried, best 5/14 gates
- edge peaks at 20 bars, exit at 60: 1 tried, best 9/14 gates
- edge peaks at 3 bars, exit at 1: 1 tried, best 8/14 gates
- edge peaks at 40 bars, exit at 10: 2 tried, best 2/14 gates
- edge peaks at 40 bars, exit at 20: 12 tried, best 13/14 gates
- edge peaks at 6 bars, exit at 1: 2 tried, best 6/14 gates
- edge peaks at 6 bars, exit at 2: 1 tried, best 4/14 gates
- edge peaks at 60 bars, exit at 10: 10 tried, best 11/14 gates
- edge peaks at 60 bars, exit at 2: 1 tried, best 9/14 gates
- edge peaks at 60 bars, exit at 20: 34 tried, best 13/14 gates
- edge peaks at 60 bars, exit at 5: 48 tried, best 13/14 gates
- fails in some regime: 272 tried, best 11/14 gates
- no better than random: 1064 tried, best 13/14 gates
- parameter neighbour: 2699 tried, best 13/14 gates
- unstable / decaying: 35 tried, best 8/14 gates
- works only in some sectors: 740 tried, best 13/14 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 6528 of 6528
- shelf life: positive in every market regime seen: 4285 of 6528
- shelf life: no decay (2nd half >= half of 1st): 3603 of 6528
- robust: parameter neighbours keep >= half the edge (2+ tested): 3405 of 6528
- shelf life: positive in >= 55% of months: 3315 of 6528
- search: ICIR >= 0.2 (stable month to month): 3053 of 6528
- decay: edge still >= half its peak at the exit, peak after the first bar: 2855 of 6528
- shelf life: works on >= 55% of assets (S&P 500: of sectors): 2825 of 6528
- validation: positive edge: 2723 of 6528
- validation: makes money after costs: 2427 of 6528
- validation: beats random entries: 2333 of 6528
- search: beats random entries (avg R): 2131 of 6528
- search: at least 100 signals: 1869 of 6528
- search: positive edge (IC): 1225 of 6528
