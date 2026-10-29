# Strategy finder – 2026-10-29

**5066 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Hourly (live universe): search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30. S&P 500 daily: search 2017-01-01 → 2022-12-31, validation 2023-01-01 → 2025-06-30. Both: vault from 2025-07-01 (sealed). 14 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13/14 | `059577dcad` sector_washout(drop=0.1, bounce=10) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Materials, daily | +1.482 | +2.49 | +0.472 | +0.52 / +0.08 | +0.63 / -0.02 | +9.8% | 0.21 | 100% | 2/2 | 92% | search: deflated Sharpe >= 0.90 |
| 13/14 | `b83e8264c5` sector_washout(drop=0.1, bounce=10) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=20 · no trend filter · sector Materials, daily | +1.482 | +2.49 | +0.472 | +0.45 / +0.08 | +0.39 / -0.01 | +10.1% | 0.21 | 100% | 2/2 | 92% | search: deflated Sharpe >= 0.90 |
| 13/14 | `e16835eaa0` sector_washout(drop=0.15, bounce=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.152 | +0.78 | +2.074 | +0.35 / +0.09 | +0.69 / +0.14 | +49.7% | 0.12 | 85% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `0d7ffa1a66` sector_washout(drop=0.15, bounce=3) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +2.152 | +0.78 | +2.074 | +1.29 / +0.24 | +0.98 / +0.26 | +57.5% | 0.06 | 85% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `ea77cc276f` sector_washout(drop=0.15, bounce=5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.178 | +0.76 | +1.225 | +0.48 / +0.10 | +0.89 / +0.12 | +36.8% | 0.26 | 81% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `4696637404` sector_washout(drop=0.15, bounce=5) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +2.178 | +0.76 | +1.225 | +1.19 / +0.21 | +1.27 / +0.23 | +45.6% | 0.03 | 81% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f8a4373833` sector_washout(drop=0.15, bounce=10) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | +1.471 | +0.72 | +0.029 | +0.27 / +0.06 | +1.13 / +0.06 | +18.6% | 0.07 | 86% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `853d3e7180` sector_washout(drop=0.15, bounce=6) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.213 | +0.72 | +1.225 | +0.57 / +0.10 | +1.01 / +0.10 | +46.9% | 0.29 | 73% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `0c507d036f` sector_washout(drop=0.15, bounce=6) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +2.213 | +0.72 | +1.225 | +1.53 / +0.17 | +1.51 / +0.18 | +58.4% | 0.03 | 73% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `82b78b89e9` insider_stress_low_short(drop=0.15, max_rank=1.37) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.228 | +0.70 | +1.346 | +0.20 / +0.06 | +0.78 / +0.11 | +28.6% | 0.03 | 75% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f5de48861d` insider_sector_stress(buyers=1, drop=0.15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.228 | +0.70 | +1.346 | +0.20 / +0.06 | +0.78 / +0.11 | +28.6% | 0.03 | 75% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f3b8641630` insider_stress_low_short(drop=0.15, max_rank=0.98) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.329 | +0.70 | +1.346 | +0.21 / +0.10 | +0.77 / +0.01 | +27.5% | 0.03 | 75% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `05292fa1de` insider_stress_low_short(drop=0.15, max_rank=0.96) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.420 | +0.69 | +0.790 | +0.19 / +0.10 | +0.76 / -0.01 | +25.8% | 0.02 | 79% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `97cbbe1fa8` sector_washout(drop=0.15, bounce=5) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | +1.359 | +0.69 | +0.351 | +0.39 / +0.07 | +0.65 / +0.08 | +21.4% | 0.18 | 83% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `e44b07c08f` insider_stress_low_short(drop=0.15, max_rank=0.69) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.801 | +0.60 | +1.186 | +0.23 / +0.07 | +0.71 / -0.07 | +16.9% | 0.03 | 73% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 13/14 | `5884febd1b` insider_stress_low_short(drop=0.15, max_rank=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.800 | +0.60 | +1.186 | +0.23 / +0.07 | +0.68 / +0.03 | +16.8% | 0.03 | 73% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 13/14 | `e11f091ad3` insider_opportunistic_wave(companies=3, window=15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily | +1.536 | +0.57 | +0.823 | +0.19 / +0.01 | +0.08 / +0.03 | +1.2% | 0.06 | 70% | 3/3 | 86% | search: deflated Sharpe >= 0.90 |
| 13/14 | `1f9799f2a1` insider_sector_stress(buyers=2, drop=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.912 | +0.55 | +0.982 | +0.08 / +0.04 | +0.31 / +0.04 | +15.9% | 0.01 | 64% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.537 | +0.51 | +0.993 | +0.13 / +0.07 | +0.05 / +0.03 | +1.8% | 0.05 | 71% | 3/3 | 68% | search: deflated Sharpe >= 0.90 |
| 13/14 | `2e69337759` insider_sector_stress(buyers=4, drop=0.04) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.572 | +0.51 | +0.992 | +0.07 / -0.01 | +0.27 / -0.06 | +8.7% | 0.01 | 61% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `1284634ec6` insider_sector_stress(buyers=4, drop=0.06) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.661 | +0.48 | +0.853 | +0.09 / -0.03 | +0.35 / +0.10 | +8.9% | 0.01 | 62% | 3/3 | 64% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.472 | +0.48 | +1.416 | +0.14 / +0.06 | +0.18 / +0.03 | +6.3% | 0.06 | 67% | 3/3 | 79% | search: deflated Sharpe >= 0.90 |
| 13/14 | `d4bee04c32` insider_wave_stress(companies=2, drop=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.540 | +0.46 | +0.808 | +0.07 / -0.01 | +0.29 / -0.09 | +14.4% | 0.01 | 61% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 13/14 | `4c95df88f7` insider_sector_wave(buyers=3, companies=1) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +0.989 | +0.45 | +0.828 | +0.22 / +0.09 | +0.35 / -0.02 | +6.7% | 0.14 | 59% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 13/14 | `b80970d1f6` insider_opportunistic_wave(companies=3, window=21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily | +1.175 | +0.45 | +0.587 | +0.20 / -0.02 | +0.03 / +0.02 | +0.5% | 0.09 | 65% | 3/3 | 87% | search: deflated Sharpe >= 0.90 |

## Campaigns: each idea refined round by round (max 5 rounds)

1293 ideas tried; **272 still improving** (search ICIR >= 0.2), 993 dropped below the bar, 28 finished their 5 rounds.

| idea → best version so far | rounds | tried | gates by round | ICIR | status |
|---|---|---|---|---|---|
| `5c00329da5` sector_washout(drop=0.29, bounce=14) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Energy, daily | 4 | 25 | 11 → 12 → 12 → 12 → 12 | +10.32 | improving |
| `cbc011408a` sector_washout(drop=0.14, bounce=7) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · sector Materials, daily | 4 | 20 | 11 → 13 → 13 → 13 → 13 | +5.66 | improving |
| `c8d4d744f4` sector_washout(drop=0.14, bounce=10) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Materials, daily | 4 | 24 | 12 → 12 → 13 → 13 → 13 | +5.32 | improving |
| `dbef8b3b8e` insider_wave_stress(companies=10, drop=0.15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 3 | 14 | 11 → 11 → 11 → 11 | +0.88 | improving |
| `209193983b` insider_sector_stress(buyers=1, drop=0.11) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Industrials, daily | 3 | 11 | 12 → 12 → 12 → 12 | +0.84 | improving |
| `12d0fbe88f` insider_sector_wave(buyers=2, companies=6) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 3 | 24 | 9 → 11 → 11 → 11 | +0.84 | improving |
| `eeb02c0e0a` sector_washout(drop=0.15, bounce=4) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | 3 | 14 | 13 → 13 → 13 → 13 | +0.79 | improving |
| `570b7f777f` sector_washout(drop=0.15, bounce=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 2 | 7 | 13 → 13 → 13 | +0.79 | improving |
| `9e540ac7cc` insider_opportunistic_wave(companies=4, window=21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily | 4 | 30 | 10 → 11 → 13 → 13 → 13 | +0.77 | improving |
| `2fdc47e829` insider_sector_stress(buyers=2, drop=0.15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 1 | 4 | 12 → 13 | +0.74 | improving |
| `f8a4373833` sector_washout(drop=0.15, bounce=10) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 1 | 4 | 13 → 13 | +0.72 | improving |
| `d6f54acd12` insider_sector_stress(buyers=1, drop=0.1) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Industrials, daily | 3 | 23 | 8 → 8 → 11 → 11 | +0.72 | improving |
| `59c20c15c2` insider_sector_stress(buyers=1, drop=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 2 | 5 | 8 → 10 → 12 | +0.71 | improving |
| `82b78b89e9` insider_stress_low_short(drop=0.15, max_rank=1.37) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 4 | 17 | 13 → 13 → 13 → 13 → 13 | +0.70 | improving |
| `f5de48861d` insider_sector_stress(buyers=1, drop=0.15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 1 | 3 | 13 → 13 | +0.70 | improving |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| sector_washout | 96 | 13/14 | +2.49 | `059577dcad` sector_washout(drop=0.1, bounce=10) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Materials, daily |
| insider_stress_low_short | 181 | 13/14 | +0.70 | `82b78b89e9` insider_stress_low_short(drop=0.15, max_rank=1.37) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_sector_stress | 124 | 13/14 | +0.70 | `f5de48861d` insider_sector_stress(buyers=1, drop=0.15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_opportunistic_wave | 138 | 13/14 | +0.57 | `e11f091ad3` insider_opportunistic_wave(companies=3, window=15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily |
| insider_sector_wave | 162 | 13/14 | +0.51 | `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_fresh | 202 | 13/14 | +0.48 | `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_wave_stress | 210 | 13/14 | +0.46 | `d4bee04c32` insider_wave_stress(companies=2, drop=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_sector_laggard | 135 | 13/14 | +0.44 | `68ca8b871d` insider_sector_laggard(buyers=1, lag=0.07) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_fresh_wave | 141 | 13/14 | +0.43 | `242358a81a` insider_fresh_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_underwater | 158 | 13/14 | +0.42 | `a5f89f69c7` insider_underwater(buyers=2, discount=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_deep_value | 123 | 13/14 | +0.40 | `2411fc93a1` insider_deep_value(buyers=4, below=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_after_earnings | 116 | 13/14 | +0.36 | `328f6e08bf` insider_after_earnings(buyers=4, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_consensus | 130 | 13/14 | +0.35 | `46bb8c1223` insider_consensus(votes=3, window=30) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_opportunistic | 87 | 13/14 | +0.35 | `139c078d63` insider_opportunistic(buyers=3, years=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_cluster | 128 | 13/14 | +0.31 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_wave_low_short | 207 | 13/14 | +0.31 | `4073a3fd7e` insider_wave_low_short(companies=5, max_rank=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_fresh_officer | 204 | 13/14 | +0.30 | `c297391e1c` insider_fresh_officer(buyers=1, gap=1401) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| insider_low_short | 120 | 13/14 | +0.30 | `09a08ad601` insider_low_short(buyers=3, max_rank=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_opportunistic_low_short | 155 | 13/14 | +0.27 | `08cac4815e` insider_opportunistic_low_short(buyers=1, max_rank=0.21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_low_vol | 64 | 13/14 | +0.27 | `3e085b793c` insider_low_vol(buyers=2, max_rank=0.21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_top_exec | 145 | 13/14 | +0.26 | `ddc1eb8b1b` insider_top_exec(min_value=140000, who=ceo_cfo) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_turn | 79 | 12/14 | +0.44 | `9f06c0dd75` insider_turn(buyers=2, window=14) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_market_stress | 145 | 12/14 | +0.43 | `f627a77d0f` insider_market_stress(buyers=1, drop=0.03) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_clean | 108 | 12/14 | +0.40 | `b36dede71a` insider_clean(buyers=2, quiet=88) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_accumulation | 84 | 12/14 | +0.39 | `81dd523126` insider_accumulation(buyers=4, volume=1.5) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_repeat | 139 | 12/14 | +0.36 | `266ed99685` insider_repeat(buys=2, window=29) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_opportunistic_exec | 77 | 12/14 | +0.31 | `4aad1266fc` insider_opportunistic_exec(who=ceo_cfo, years=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_high_short | 44 | 12/14 | +0.24 | `33183d91a6` insider_high_short(buyers=1, min_rank=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_conviction | 121 | 12/14 | +0.15 | `bb35082f6c` insider_conviction(buyers=3, min_bp=3.92) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_stress_leader | 37 | 10/14 | +0.58 | `6e33ef8692` insider_stress_leader(drop=0.15, lead=0.0) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_fund | 91 | 10/14 | +0.55 | `49cfddaf78` insider_fund(buyers=3, feature=f_sue) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · sector Industrials, daily |
| vwap | 218 | 10/14 | +0.30 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 |
| insider_ml | 11 | 10/14 | +0.22 | `2b1fd2c3d8` insider_ml(model=ridge, keep=0.5) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily |
| ml_rank_short | 4 | 10/14 | +0.10 | `d39c850a7f` ml_rank_short(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| ml_rank_fund | 4 | 9/14 | +0.09 | `dbfedfaad8` ml_rank_fund(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_confirm | 20 | 9/14 | +0.05 | `595f15ef1d` insider_confirm(buyers=3, wait=10) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| volume_breakout | 75 | 8/14 | +0.26 | `2f7b678096` volume_breakout(n=20, m=3.5) · stop_atr=1.5, rr=None, max_bars=3 |
| insider_momentum | 32 | 8/14 | +0.23 | `1b4b882975` insider_momentum(buyers=2, min_rank=0.49) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| insider_big_buy | 72 | 8/14 | +0.15 | `917deb29a5` insider_big_buy(min_value=500000, officer=True) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily |
| sector_reversal | 8 | 8/14 | +0.11 | `29f76df1ba` sector_reversal(lookback=5, bottom=0.02) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily |
| ml_rank | 4 | 8/14 | +0.09 | `9757090abb` ml_rank(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| reversal_5d | 36 | 8/14 | -0.05 | `cbc6e766e6` reversal_5d(bottom=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| donchian | 100 | 7/14 | +0.33 | `e4dbf9e4e1` donchian(n=118, trend_ma=140) · stop_atr=1.5, rr=None, max_bars=2 · no trend filter |
| opening_range | 24 | 6/14 | +0.54 | `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter |
| xs_reversal | 30 | 6/14 | +0.15 | `d2867573f6` xs_reversal(lookback=6, bottom=4) · stop_atr=1.5, rr=None, max_bars=1 |
| xs_momentum | 30 | 6/14 | +0.05 | `7ffb46fdcc` xs_momentum(lookback=120, top=4) · stop_atr=1.0, rr=1.5, max_bars=6 |
| earnings_overreaction | 27 | 6/14 | +0.04 | `9493c2c5f1` earnings_overreaction(z=3.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 600 (small), daily |
| momentum_12_1 | 36 | 6/14 | +0.04 | `9171f4b689` momentum_12_1(top=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| rsi2 | 41 | 6/14 | -0.00 | `9dcb4f23b3` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=1 |
| intraday_momentum | 15 | 6/14 | -0.22 | `52f33b3180` intraday_momentum(k=1.0) · stop_atr=2.0, rr=2.0 |
| squeeze | 21 | 6/14 | -0.36 | `5f107ac95d` squeeze() · stop_atr=3.0, rr=None, trail_atr=4.0, adx_threshold=25.0 · stocks+etfs |
| sector_momentum | 8 | 5/14 | +0.09 | `305c6e6e52` sector_momentum(top=2, ma=100) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| momentum_low_vol | 8 | 5/14 | -0.02 | `cbfb01bd5f` momentum_low_vol(top=0.05, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| momentum_pullback | 8 | 5/14 | -0.03 | `b158014923` momentum_pullback(top=0.2, bottom=0.1) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| gap_fade | 15 | 5/14 | -0.17 | `63e0bb1295` gap_fade(g=1.0) · stop_atr=1.5, rr=None, max_bars=1 |
| liquidity_sweep | 20 | 5/14 | -0.25 | `ad23174e9f` liquidity_sweep(n=35, k=0.25) · stop_atr=1.5, rr=None, max_bars=1 |
| earnings_drift | 15 | 5/14 | -0.29 | `6493eb9de4` earnings_drift(x=2.0) · stop_atr=2.0, rr=2.0 |
| high_52w | 36 | 4/14 | -0.29 | `59732b89d7` high_52w(within=0.03) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| btc_lead | 10 | 4/14 | -0.52 | `498531f181` btc_lead(k=0.75) · stop_atr=1.5, rr=None, max_bars=1 |
| overnight_momentum | 8 | 3/14 | -0.12 | `346160c1e6` overnight_momentum(lookback=20, top=0.1) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_dip | 144 | 3/14 | +nan | `c2359d2a01` insider_dip(buyers=2, days=30, drop=0.1) · stop_atr=3.0, rr=None, max_bars=10 · S&P 500, daily |
| momentum_low_short | 8 | 2/14 | -0.13 | `5845cb17fa` momentum_low_short(top=0.05, max_rank=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| earnings_reaction | 27 | 2/14 | -0.17 | `77d24b85f6` earnings_reaction(z=1.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 500, daily |

## The loop: 3773 children tried (improved versions aimed at a parent's failures)

- breadth failed: 93 tried, best 9/14 gates
- edge peaks at 2 bars, exit at 1: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 12: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 5: 1 tried, best 8/14 gates
- edge peaks at 20 bars, exit at 5: 1 tried, best 6/14 gates
- edge peaks at 20 bars, exit at 60: 1 tried, best 12/14 gates
- edge peaks at 3 bars, exit at 1: 1 tried, best 8/14 gates
- edge peaks at 40 bars, exit at 10: 2 tried, best 5/14 gates
- edge peaks at 40 bars, exit at 20: 1 tried, best 7/14 gates
- edge peaks at 6 bars, exit at 1: 2 tried, best 6/14 gates
- edge peaks at 6 bars, exit at 2: 1 tried, best 4/14 gates
- edge peaks at 60 bars, exit at 10: 10 tried, best 12/14 gates
- edge peaks at 60 bars, exit at 2: 1 tried, best 9/14 gates
- edge peaks at 60 bars, exit at 20: 23 tried, best 13/14 gates
- edge peaks at 60 bars, exit at 5: 45 tried, best 13/14 gates
- fails in some regime: 205 tried, best 11/14 gates
- no better than random: 971 tried, best 12/14 gates
- parameter neighbour: 1865 tried, best 13/14 gates
- unstable / decaying: 35 tried, best 8/14 gates
- works only in some sectors: 513 tried, best 13/14 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 5066 of 5066
- shelf life: positive in every market regime seen: 3439 of 5066
- shelf life: no decay (2nd half >= half of 1st): 2947 of 5066
- robust: parameter neighbours keep >= half the edge (2+ tested): 2831 of 5066
- shelf life: positive in >= 55% of months: 2765 of 5066
- decay: edge still >= half its peak at the exit, peak after the first bar: 2593 of 5066
- shelf life: works on >= 55% of assets (S&P 500: of sectors): 2558 of 5066
- validation: positive edge: 2423 of 5066
- search: ICIR >= 0.2 (stable month to month): 2295 of 5066
- validation: beats random entries: 2100 of 5066
- search: beats random entries (avg R): 1810 of 5066
- search: at least 100 signals: 1656 of 5066
- validation: makes money after costs: 1633 of 5066
- search: positive edge (IC): 1036 of 5066
