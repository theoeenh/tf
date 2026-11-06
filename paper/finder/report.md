# Strategy finder – 2026-11-06

**6020 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Hourly (live universe): search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30. S&P 500 daily: search 2017-01-01 → 2022-12-31, validation 2023-01-01 → 2025-06-30. Both: vault from 2025-07-01 (sealed). 14 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13/14 | `905e20704a` sector_washout_calm(drop=0.15, bounce=2, max_vol=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.603 | +1.03 | +1.300 | +0.28 / +0.13 | +0.56 / +0.11 | +34.0% | 0.06 | 95% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `0802f26683` sector_washout_calm(drop=0.15, bounce=2, max_vol=0.49) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.266 | +0.98 | +1.228 | +0.35 / +0.09 | +0.50 / +0.11 | +28.3% | 0.08 | 95% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `cdd29ca2d9` sector_washout_leaders(drop=0.15, bounce=2, within=0.5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.140 | +0.94 | +0.724 | +0.24 / +0.11 | +0.59 / +0.19 | +42.9% | 0.04 | 90% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `c956271ca3` sector_washout_leaders(drop=0.15, bounce=2, within=0.35) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.880 | +0.92 | +0.425 | +0.21 / +0.11 | +0.52 / +0.17 | +35.8% | 0.04 | 90% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `aa57e56309` sector_washout_leaders(drop=0.15, bounce=2, within=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.228 | +0.92 | +1.013 | +0.26 / +0.11 | +0.61 / +0.15 | +40.7% | 0.04 | 95% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `027735c1bb` sector_washout_calm(drop=0.15, bounce=3, max_vol=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.442 | +0.91 | +1.912 | +0.36 / +0.09 | +0.74 / +0.12 | +43.9% | 0.11 | 90% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `ec4ccdc2f8` sector_washout_calm(drop=0.15, bounce=2, max_vol=0.98) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.325 | +0.90 | +1.493 | +0.30 / +0.09 | +0.50 / +0.12 | +36.7% | 0.05 | 85% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `983a8040c1` sector_washout_calm(drop=0.15, bounce=3, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.194 | +0.89 | +1.331 | +0.34 / +0.10 | +0.53 / +0.12 | +26.8% | 0.06 | 85% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `5ba5cf7616` sector_washout_calm(drop=0.15, bounce=3, max_vol=0.3) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +2.194 | +0.89 | +1.331 | +0.38 / +0.23 | +0.66 / +0.23 | +28.7% | 0.04 | 85% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `fd053cba98` sector_washout_calm(drop=0.15, bounce=6, max_vol=0.49) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.991 | +0.87 | +0.110 | +0.75 / +0.13 | +0.67 / +0.15 | +21.3% | 0.25 | 82% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `65a23684af` sector_washout_leaders(drop=0.15, bounce=3, within=0.5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.974 | +0.85 | +0.696 | +0.31 / +0.11 | +0.55 / +0.19 | +33.7% | 0.09 | 80% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `289d114e66` sector_washout_leaders(drop=0.15, bounce=3, within=0.5) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +1.974 | +0.85 | +0.696 | +0.42 / +0.18 | +0.94 / +0.35 | +52.3% | 0.05 | 80% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `75e652680d` sector_washout_calm(drop=0.15, bounce=6, max_vol=0.5) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.968 | +0.85 | +0.196 | +0.73 / +0.15 | +0.66 / +0.13 | +21.4% | 0.26 | 82% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `ebaa754486` sector_washout_calm(drop=0.15, bounce=2, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.126 | +0.85 | +1.098 | +0.35 / +0.12 | +0.56 / +0.13 | +30.4% | 0.06 | 89% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `c246b7e4fc` sector_washout_calm(drop=0.15, bounce=6, max_vol=0.7) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.766 | +0.83 | +0.125 | +0.70 / +0.13 | +0.86 / +0.26 | +28.1% | 0.25 | 82% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `ad48fb01c4` sector_washout_calm(drop=0.15, bounce=3, max_vol=0.49) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.191 | +0.83 | +1.720 | +0.31 / +0.10 | +0.68 / +0.08 | +36.6% | 0.06 | 90% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f9ccddc802` sector_washout_calm(drop=0.15, bounce=4, max_vol=0.7) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +1.996 | +0.83 | +1.792 | +0.32 / +0.12 | +0.52 / +0.17 | +26.8% | 0.04 | 84% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `5157942508` sector_washout_leaders(drop=0.15, bounce=3, within=0.35) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.613 | +0.83 | +0.502 | +0.28 / +0.13 | +0.48 / +0.14 | +28.5% | 0.07 | 80% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `a9833ab7a8` sector_washout_leaders(drop=0.15, bounce=3, within=0.35) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +1.613 | +0.83 | +0.502 | +0.37 / +0.22 | +0.87 / +0.36 | +45.1% | 0.05 | 80% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `75a2614553` sector_washout_leaders(drop=0.15, bounce=3, within=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.076 | +0.82 | +1.206 | +0.33 / +0.10 | +0.73 / +0.16 | +45.3% | 0.08 | 80% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `1be15ee836` sector_washout_leaders(drop=0.15, bounce=3, within=0.7) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +2.076 | +0.82 | +1.206 | +0.40 / +0.23 | +1.06 / +0.28 | +60.9% | 0.03 | 80% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `46e0b923ab` sector_washout_leaders(drop=0.15, bounce=3, within=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.509 | +0.81 | +0.440 | +0.31 / +0.18 | +0.57 / +0.13 | +28.9% | 0.08 | 90% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `88bd6e546b` sector_washout_leaders(drop=0.15, bounce=3, within=0.3) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +1.509 | +0.81 | +0.440 | +0.35 / +0.25 | +0.90 / +0.35 | +44.6% | 0.04 | 90% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `9eca16f420` sector_washout_calm(drop=0.15, bounce=3, max_vol=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +2.067 | +0.80 | +1.792 | +0.35 / +0.13 | +0.65 / +0.09 | +33.2% | 0.06 | 90% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `3f1ca4d2c0` sector_washout_calm(drop=0.15, bounce=3, max_vol=0.42) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +2.067 | +0.80 | +1.792 | +0.47 / +0.21 | +0.77 / +0.23 | +35.2% | 0.05 | 90% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |

## Campaigns: each idea refined round by round (max 5 rounds)

1437 ideas tried; **310 still improving** (search ICIR >= 0.2), 1092 dropped below the bar, 35 finished their 5 rounds.

| idea → best version so far | rounds | tried | gates by round | ICIR | status |
|---|---|---|---|---|---|
| `905e20704a` sector_washout_calm(drop=0.15, bounce=2, max_vol=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 5 | 28 | 12 → 12 → 13 → 13 → 13 → 13 | +1.03 | finished: 5 rounds |
| `10ab70d758` sector_washout_calm(drop=0.15, bounce=6, max_vol=0.35) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | 5 | 30 | 13 → 13 → 13 → 13 → 13 → 13 | +0.99 | finished: 5 rounds |
| `8f25b93868` sector_washout_leaders(drop=0.15, bounce=2, within=0.5) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | 4 | 23 | 12 → 13 → 13 → 13 → 13 | +0.94 | improving |
| `cdd29ca2d9` sector_washout_leaders(drop=0.15, bounce=2, within=0.5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 4 | 22 | 12 → 12 → 13 → 13 → 13 | +0.94 | improving |
| `916b5053b5` sector_washout(drop=0.07, bounce=10) · stop_atr=3.0, rr=None, max_bars=10 · no trend filter · sector Materials, daily | 5 | 39 | 12 → 12 → 12 → 12 → 12 → 12 | +0.93 | finished: 5 rounds |
| `5ba5cf7616` sector_washout_calm(drop=0.15, bounce=3, max_vol=0.3) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | 4 | 24 | 12 → 13 → 13 → 13 → 13 | +0.89 | improving |
| `983a8040c1` sector_washout_calm(drop=0.15, bounce=3, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 3 | 16 | 12 → 12 → 13 → 13 | +0.89 | improving |
| `209193983b` insider_sector_stress(buyers=1, drop=0.11) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Industrials, daily | 3 | 11 | 12 → 12 → 12 → 12 | +0.84 | improving |
| `12d0fbe88f` insider_sector_wave(buyers=2, companies=6) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 3 | 24 | 9 → 11 → 11 → 11 | +0.84 | improving |
| `62703a6b8a` sector_washout_leaders(drop=0.15, bounce=4, within=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 2 | 12 | 12 → 12 → 13 | +0.82 | improving |
| `1dc565fe1c` sector_washout_leaders(drop=0.15, bounce=4, within=0.3) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | 3 | 18 | 11 → 12 → 12 → 13 | +0.82 | improving |
| `23650b32b9` calm_union(parts=1, gap=42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 3 | 9 | 12 → 12 → 12 → 12 | +0.80 | improving |
| `2791eaacdc` sector_washout(drop=0.07, bounce=10) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Materials, daily | 4 | 25 | 11 → 12 → 12 → 12 → 12 | +0.80 | improving |
| `eeb02c0e0a` sector_washout(drop=0.15, bounce=4) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | 3 | 14 | 13 → 13 → 13 → 13 | +0.79 | improving |
| `570b7f777f` sector_washout(drop=0.15, bounce=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 2 | 7 | 13 → 13 → 13 | +0.79 | improving |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| sector_washout_calm | 166 | 13/14 | +1.03 | `905e20704a` sector_washout_calm(drop=0.15, bounce=2, max_vol=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| sector_washout_leaders | 79 | 13/14 | +0.94 | `cdd29ca2d9` sector_washout_leaders(drop=0.15, bounce=2, within=0.5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| sector_washout | 117 | 13/14 | +0.78 | `e16835eaa0` sector_washout(drop=0.15, bounce=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_stress_low_short | 191 | 13/14 | +0.70 | `82b78b89e9` insider_stress_low_short(drop=0.15, max_rank=1.37) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_sector_stress | 124 | 13/14 | +0.70 | `f5de48861d` insider_sector_stress(buyers=1, drop=0.15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_opportunistic_wave | 138 | 13/14 | +0.57 | `e11f091ad3` insider_opportunistic_wave(companies=3, window=15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily |
| insider_sector_wave | 162 | 13/14 | +0.51 | `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_fresh | 202 | 13/14 | +0.48 | `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_calm_stress | 38 | 13/14 | +0.47 | `32a78ddef3` insider_calm_stress(buyers=1, drop=0.04, max_vol=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_wave_stress | 237 | 13/14 | +0.46 | `d4bee04c32` insider_wave_stress(companies=2, drop=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_sector_laggard | 135 | 13/14 | +0.44 | `68ca8b871d` insider_sector_laggard(buyers=1, lag=0.07) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_fresh_wave | 141 | 13/14 | +0.43 | `242358a81a` insider_fresh_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_underwater | 158 | 13/14 | +0.42 | `a5f89f69c7` insider_underwater(buyers=2, discount=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_deep_value | 123 | 13/14 | +0.40 | `2411fc93a1` insider_deep_value(buyers=4, below=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_after_earnings | 116 | 13/14 | +0.36 | `328f6e08bf` insider_after_earnings(buyers=4, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_consensus | 130 | 13/14 | +0.35 | `46bb8c1223` insider_consensus(votes=3, window=30) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_opportunistic | 87 | 13/14 | +0.35 | `139c078d63` insider_opportunistic(buyers=3, years=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_union | 82 | 13/14 | +0.32 | `b490d46d16` insider_union(parts=4, gap=42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_cluster | 128 | 13/14 | +0.31 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_wave_low_short | 207 | 13/14 | +0.31 | `4073a3fd7e` insider_wave_low_short(companies=5, max_rank=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_fresh_officer | 204 | 13/14 | +0.30 | `c297391e1c` insider_fresh_officer(buyers=1, gap=1401) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| insider_low_short | 120 | 13/14 | +0.30 | `09a08ad601` insider_low_short(buyers=3, max_rank=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| calm_union | 31 | 13/14 | +0.28 | `25a7884c1f` calm_union(parts=3, gap=42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_opportunistic_low_short | 155 | 13/14 | +0.27 | `08cac4815e` insider_opportunistic_low_short(buyers=1, max_rank=0.21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_low_vol | 64 | 13/14 | +0.27 | `3e085b793c` insider_low_vol(buyers=2, max_rank=0.21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_top_exec | 145 | 13/14 | +0.26 | `ddc1eb8b1b` insider_top_exec(min_value=140000, who=ceo_cfo) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_calm_fresh | 271 | 13/14 | +0.25 | `3cfdb091d7` insider_calm_fresh(gap=511, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_turn | 79 | 12/14 | +0.44 | `9f06c0dd75` insider_turn(buyers=2, window=14) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_market_stress | 145 | 12/14 | +0.43 | `f627a77d0f` insider_market_stress(buyers=1, drop=0.03) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_clean | 108 | 12/14 | +0.40 | `b36dede71a` insider_clean(buyers=2, quiet=88) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_accumulation | 84 | 12/14 | +0.39 | `81dd523126` insider_accumulation(buyers=4, volume=1.5) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_repeat | 139 | 12/14 | +0.36 | `266ed99685` insider_repeat(buys=2, window=29) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_opportunistic_exec | 77 | 12/14 | +0.31 | `4aad1266fc` insider_opportunistic_exec(who=ceo_cfo, years=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_high_short | 44 | 12/14 | +0.24 | `33183d91a6` insider_high_short(buyers=1, min_rank=0.7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_filing_lag | 52 | 12/14 | +0.21 | `a64d6715c7` insider_filing_lag(mode=prompt, buyers=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Health Care, daily |
| insider_conviction | 121 | 12/14 | +0.15 | `bb35082f6c` insider_conviction(buyers=3, min_bp=3.92) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| same_month_seasonality | 85 | 11/14 | +0.29 | `5c32eba42c` same_month_seasonality(top=0.05, years=5) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · sector Financials, daily |
| insider_calm_low_short | 44 | 11/14 | +0.16 | `e36694ad44` insider_calm_low_short(max_vol=0.5, max_rank=0.5) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_stress_leader | 37 | 10/14 | +0.58 | `6e33ef8692` insider_stress_leader(drop=0.15, lead=0.0) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_fund | 91 | 10/14 | +0.55 | `49cfddaf78` insider_fund(buyers=3, feature=f_sue) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · sector Industrials, daily |
| vwap | 218 | 10/14 | +0.30 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 |
| insider_ml | 11 | 10/14 | +0.22 | `2b1fd2c3d8` insider_ml(model=ridge, keep=0.5) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily |
| ml_rank_short | 4 | 10/14 | +0.10 | `d39c850a7f` ml_rank_short(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| stock_washout | 8 | 10/14 | +0.10 | `2eb2e5708d` stock_washout(drop=0.15, bounce=3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| ml_rank_fund | 4 | 9/14 | +0.09 | `dbfedfaad8` ml_rank_fund(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_confirm | 20 | 9/14 | +0.05 | `595f15ef1d` insider_confirm(buyers=3, wait=10) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| stress_calm_leaders | 8 | 9/14 | -0.06 | `3c6edd688c` stress_calm_leaders(drop=0.05, max_vol=0.4) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| volume_breakout | 75 | 8/14 | +0.26 | `2f7b678096` volume_breakout(n=20, m=3.5) · stop_atr=1.5, rr=None, max_bars=3 |
| insider_momentum | 32 | 8/14 | +0.23 | `1b4b882975` insider_momentum(buyers=2, min_rank=0.49) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| insider_big_buy | 72 | 8/14 | +0.15 | `917deb29a5` insider_big_buy(min_value=500000, officer=True) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily |
| sector_reversal | 8 | 8/14 | +0.11 | `29f76df1ba` sector_reversal(lookback=5, bottom=0.02) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily |
| ml_rank | 4 | 8/14 | +0.09 | `9757090abb` ml_rank(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| reversal_5d | 36 | 8/14 | -0.05 | `cbc6e766e6` reversal_5d(bottom=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| donchian | 100 | 7/14 | +0.33 | `e4dbf9e4e1` donchian(n=118, trend_ma=140) · stop_atr=1.5, rr=None, max_bars=2 · no trend filter |
| opening_range | 24 | 6/14 | +0.54 | `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter |
| xs_reversal | 30 | 6/14 | +0.15 | `d2867573f6` xs_reversal(lookback=6, bottom=4) · stop_atr=1.5, rr=None, max_bars=1 |
| lead_lag_sector | 8 | 6/14 | +0.06 | `b64cceebc6` lead_lag_sector(lead=0.05, days=5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| xs_momentum | 30 | 6/14 | +0.05 | `7ffb46fdcc` xs_momentum(lookback=120, top=4) · stop_atr=1.0, rr=1.5, max_bars=6 |
| earnings_overreaction | 27 | 6/14 | +0.04 | `9493c2c5f1` earnings_overreaction(z=3.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 600 (small), daily |
| momentum_12_1 | 36 | 6/14 | +0.04 | `9171f4b689` momentum_12_1(top=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| rsi2 | 41 | 6/14 | -0.00 | `9dcb4f23b3` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=1 |
| intraday_momentum | 15 | 6/14 | -0.22 | `52f33b3180` intraday_momentum(k=1.0) · stop_atr=2.0, rr=2.0 |
| squeeze | 21 | 6/14 | -0.36 | `5f107ac95d` squeeze() · stop_atr=3.0, rr=None, trail_atr=4.0, adx_threshold=25.0 · stocks+etfs |
| sector_momentum | 8 | 5/14 | +0.09 | `305c6e6e52` sector_momentum(top=2, ma=100) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| turn_of_month | 4 | 5/14 | +0.08 | `fd97fffe16` turn_of_month(days_before=0, max_vol=0.2) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily |
| momentum_low_vol | 8 | 5/14 | -0.02 | `cbfb01bd5f` momentum_low_vol(top=0.05, max_vol=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| momentum_pullback | 8 | 5/14 | -0.03 | `b158014923` momentum_pullback(top=0.2, bottom=0.1) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| gap_fade | 15 | 5/14 | -0.17 | `63e0bb1295` gap_fade(g=1.0) · stop_atr=1.5, rr=None, max_bars=1 |
| liquidity_sweep | 20 | 5/14 | -0.25 | `ad23174e9f` liquidity_sweep(n=35, k=0.25) · stop_atr=1.5, rr=None, max_bars=1 |
| earnings_drift | 15 | 5/14 | -0.29 | `6493eb9de4` earnings_drift(x=2.0) · stop_atr=2.0, rr=2.0 |
| high_52w | 36 | 4/14 | -0.29 | `59732b89d7` high_52w(within=0.03) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| btc_lead | 10 | 4/14 | -0.52 | `498531f181` btc_lead(k=0.75) · stop_atr=1.5, rr=None, max_bars=1 |
| low_vol_monthly | 8 | 3/14 | -0.03 | `4f6655c9c0` low_vol_monthly(bottom=0.1, trend=100) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| overnight_momentum | 8 | 3/14 | -0.12 | `346160c1e6` overnight_momentum(lookback=20, top=0.1) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_dip | 144 | 3/14 | +nan | `c2359d2a01` insider_dip(buyers=2, days=30, drop=0.1) · stop_atr=3.0, rr=None, max_bars=10 · S&P 500, daily |
| momentum_low_short | 8 | 2/14 | -0.13 | `5845cb17fa` momentum_low_short(top=0.05, max_rank=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| smooth_momentum | 8 | 2/14 | -0.14 | `66f87d0fbe` smooth_momentum(top=0.1, within=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| earnings_reaction | 27 | 2/14 | -0.17 | `77d24b85f6` earnings_reaction(z=1.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 500, daily |
| residual_momentum | 4 | 2/14 | -0.18 | `1ca63533a6` residual_momentum(top=0.05, lookback=252) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |

## The loop: 4583 children tried (improved versions aimed at a parent's failures)

- breadth failed: 93 tried, best 9/14 gates
- edge peaks at 2 bars, exit at 1: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 12: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 5: 1 tried, best 8/14 gates
- edge peaks at 20 bars, exit at 5: 1 tried, best 6/14 gates
- edge peaks at 20 bars, exit at 60: 1 tried, best 12/14 gates
- edge peaks at 3 bars, exit at 1: 1 tried, best 8/14 gates
- edge peaks at 40 bars, exit at 10: 2 tried, best 4/14 gates
- edge peaks at 40 bars, exit at 20: 6 tried, best 13/14 gates
- edge peaks at 6 bars, exit at 1: 2 tried, best 6/14 gates
- edge peaks at 6 bars, exit at 2: 1 tried, best 4/14 gates
- edge peaks at 60 bars, exit at 10: 10 tried, best 12/14 gates
- edge peaks at 60 bars, exit at 2: 1 tried, best 9/14 gates
- edge peaks at 60 bars, exit at 20: 32 tried, best 13/14 gates
- edge peaks at 60 bars, exit at 5: 48 tried, best 13/14 gates
- fails in some regime: 253 tried, best 11/14 gates
- no better than random: 1106 tried, best 12/14 gates
- parameter neighbour: 2368 tried, best 13/14 gates
- unstable / decaying: 35 tried, best 8/14 gates
- works only in some sectors: 620 tried, best 13/14 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 6020 of 6020
- shelf life: positive in every market regime seen: 4036 of 6020
- shelf life: no decay (2nd half >= half of 1st): 3425 of 6020
- robust: parameter neighbours keep >= half the edge (2+ tested): 3199 of 6020
- shelf life: positive in >= 55% of months: 3095 of 6020
- search: ICIR >= 0.2 (stable month to month): 2982 of 6020
- decay: edge still >= half its peak at the exit, peak after the first bar: 2893 of 6020
- validation: positive edge: 2831 of 6020
- shelf life: works on >= 55% of assets (S&P 500: of sectors): 2814 of 6020
- validation: beats random entries: 2413 of 6020
- search: beats random entries (avg R): 2089 of 6020
- validation: makes money after costs: 1836 of 6020
- search: at least 100 signals: 1794 of 6020
- search: positive edge (IC): 1129 of 6020
