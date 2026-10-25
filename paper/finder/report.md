# Strategy finder – 2026-10-25

**4379 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Hourly (live universe): search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30. S&P 500 daily: search 2017-01-01 → 2022-12-31, validation 2023-01-01 → 2025-06-30. Both: vault from 2025-07-01 (sealed). 14 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13/14 | `e11f091ad3` insider_opportunistic_wave(companies=3, window=15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily | +1.536 | +0.57 | +0.823 | +0.19 / +0.01 | +0.08 / +0.03 | +1.2% | 0.07 | 70% | 3/3 | 86% | search: deflated Sharpe >= 0.90 |
| 13/14 | `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.537 | +0.51 | +0.993 | +0.13 / +0.07 | +0.05 / +0.03 | +1.8% | 0.05 | 71% | 3/3 | 68% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.472 | +0.48 | +1.416 | +0.14 / +0.06 | +0.18 / +0.03 | +6.3% | 0.06 | 67% | 3/3 | 79% | search: deflated Sharpe >= 0.90 |
| 13/14 | `4c95df88f7` insider_sector_wave(buyers=3, companies=1) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +0.989 | +0.45 | +0.828 | +0.22 / +0.09 | +0.35 / -0.02 | +6.7% | 0.15 | 59% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 13/14 | `b80970d1f6` insider_opportunistic_wave(companies=3, window=21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily | +1.175 | +0.45 | +0.587 | +0.20 / -0.02 | +0.03 / +0.02 | +0.5% | 0.09 | 65% | 3/3 | 87% | search: deflated Sharpe >= 0.90 |
| 13/14 | `68ca8b871d` insider_sector_laggard(buyers=1, lag=0.07) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.065 | +0.44 | +1.205 | +0.04 / -0.01 | +0.10 / +0.04 | +5.9% | 0.01 | 63% | 3/3 | 67% | search: deflated Sharpe >= 0.90 |
| 13/14 | `7ac445c110` insider_fresh(buyers=2, gap=178) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.372 | +0.44 | +1.076 | +0.11 / +0.05 | +0.15 / +0.14 | +5.0% | 0.04 | 65% | 3/3 | 71% | search: deflated Sharpe >= 0.90 |
| 13/14 | `421c1c271f` insider_fresh(buyers=2, gap=175) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.364 | +0.44 | +1.344 | +0.12 / +0.06 | +0.20 / +0.16 | +6.7% | 0.04 | 66% | 3/3 | 71% | search: deflated Sharpe >= 0.90 |
| 13/14 | `242358a81a` insider_fresh_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.278 | +0.43 | +1.063 | +0.10 / -0.04 | +0.10 / +0.09 | +2.6% | 0.03 | 68% | 3/3 | 78% | search: deflated Sharpe >= 0.90 |
| 13/14 | `86755b6c71` insider_sector_wave(buyers=3, companies=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.164 | +0.43 | +0.901 | +0.05 / +0.03 | +0.23 / +0.00 | +10.8% | 0.01 | 60% | 3/3 | 70% | search: deflated Sharpe >= 0.90 |
| 13/14 | `a5f89f69c7` insider_underwater(buyers=2, discount=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.617 | +0.42 | +1.170 | +0.15 / +0.03 | +0.18 / -0.16 | +3.3% | 0.06 | 71% | 3/3 | 88% | search: deflated Sharpe >= 0.90 |
| 13/14 | `2411fc93a1` insider_deep_value(buyers=4, below=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +0.765 | +0.40 | +0.653 | +0.06 / -0.02 | +0.21 / -0.15 | +7.5% | 0.01 | 56% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `ffe01894f9` insider_sector_laggard(buyers=3, lag=0.07) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +0.793 | +0.39 | +0.818 | +0.04 / +0.03 | +0.17 / -0.09 | +12.0% | 0.01 | 66% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `b2f8149f5f` insider_fresh(buyers=1, gap=1001) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily | +0.911 | +0.38 | +1.227 | +0.30 / +0.13 | +0.04 / -0.02 | +1.6% | 0.68 | 65% | 3/3 | 58% | search: deflated Sharpe >= 0.90 |
| 13/14 | `08e32d08a0` insider_underwater(buyers=4, discount=0.15) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +0.837 | +0.37 | +0.840 | +0.10 / +0.05 | +0.26 / +0.03 | +9.4% | 0.03 | 65% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `a445c81f44` insider_fresh(buyers=1, gap=730) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily | +0.882 | +0.37 | +1.313 | +0.29 / +0.13 | +0.04 / -0.03 | +1.9% | 0.67 | 64% | 3/3 | 60% | search: deflated Sharpe >= 0.90 |
| 13/14 | `328f6e08bf` insider_after_earnings(buyers=4, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.965 | +0.36 | +0.401 | +0.05 / -0.01 | +0.24 / -0.02 | +17.4% | 0.01 | 66% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `7ea781d068` insider_after_earnings(buyers=4, window=55) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.033 | +0.36 | +0.562 | +0.05 / +0.02 | +0.19 / -0.07 | +12.2% | 0.01 | 63% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `6931885bc6` insider_after_earnings(buyers=4, window=56) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.032 | +0.36 | +0.562 | +0.05 / +0.03 | +0.19 / -0.07 | +12.2% | 0.01 | 63% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `46bb8c1223` insider_consensus(votes=3, window=30) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.056 | +0.35 | +1.433 | +0.14 / +0.02 | +0.12 / -0.17 | +2.2% | 0.04 | 55% | 3/3 | 71% | search: deflated Sharpe >= 0.90 |
| 13/14 | `139c078d63` insider_opportunistic(buyers=3, years=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.883 | +0.35 | +0.624 | +0.05 / +0.03 | +0.20 / +0.00 | +22.8% | 0.01 | 71% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `5171bc830e` insider_underwater(buyers=3, discount=0.21) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +0.774 | +0.35 | +0.628 | +0.05 / +0.04 | +0.19 / +0.10 | +7.7% | 0.01 | 63% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 13/14 | `51028b78a0` insider_fresh(buyers=1, gap=701) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily | +0.841 | +0.35 | +1.313 | +0.29 / +0.13 | +0.04 / -0.03 | +1.9% | 0.67 | 64% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 13/14 | `64a39c60ff` insider_fresh(buyers=2, gap=125) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +0.871 | +0.34 | +0.902 | +0.14 / +0.07 | +0.17 / +0.06 | +6.0% | 0.07 | 66% | 3/3 | 67% | search: deflated Sharpe >= 0.90 |
| 13/14 | `fda4e627ca` insider_fresh(buyers=2, gap=255) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +0.956 | +0.34 | +0.806 | +0.15 / +0.02 | +0.20 / +0.10 | +6.0% | 0.07 | 62% | 3/3 | 77% | search: deflated Sharpe >= 0.90 |

## Campaigns: each idea refined round by round (max 5 rounds)

1197 ideas tried; **241 still improving** (search ICIR >= 0.2), 936 dropped below the bar, 20 finished their 5 rounds.

| idea → best version so far | rounds | tried | gates by round | ICIR | status |
|---|---|---|---|---|---|
| `12d0fbe88f` insider_sector_wave(buyers=2, companies=6) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 3 | 24 | 9 → 11 → 11 → 11 | +0.84 | improving |
| `9e540ac7cc` insider_opportunistic_wave(companies=4, window=21) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily | 4 | 30 | 10 → 11 → 13 → 13 → 13 | +0.77 | improving |
| `9724ab3ad8` insider_market_stress(buyers=3, drop=0.08) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 4 | 27 | 7 → 8 → 9 → 11 → 11 | +0.67 | improving |
| `504771a862` insider_accumulation(buyers=4, volume=2.1) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | 4 | 26 | 9 → 11 → 12 → 12 → 12 | +0.60 | improving |
| `f28ff156e8` insider_after_earnings(buyers=2, window=20) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 1 | 5 | 9 → 12 | +0.57 | improving |
| `f901b767fe` insider_after_earnings(buyers=2, window=20) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | 3 | 23 | 5 → 7 → 9 → 12 | +0.57 | improving |
| `1d6bb94d20` insider_deep_value(buyers=1, below=0.29) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily | 4 | 29 | 12 → 12 → 13 → 13 → 13 | +0.54 | improving |
| `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter | 2 | 7 | 6 → 6 → 6 | +0.54 | improving |
| `6b34a9f9a2` insider_market_stress(buyers=3, drop=0.03) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 2 | 6 | 9 → 11 → 11 | +0.54 | improving |
| `9451193926` insider_market_stress(buyers=1, drop=0.03) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily | 2 | 12 | 12 → 12 → 12 | +0.54 | improving |
| `519ba6bcf9` insider_opportunistic_exec(who=ceo_cfo, years=1) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · sector Information Technology, daily | 4 | 22 | 10 → 11 → 11 → 11 → 11 | +0.51 | improving |
| `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 1 | 3 | 13 → 13 | +0.51 | improving |
| `20f53c2639` insider_opportunistic_wave(companies=5, window=29) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily | 4 | 30 | 10 → 12 → 12 → 12 → 12 | +0.51 | improving |
| `83a2f39ef5` insider_high_short(buyers=1, min_rank=0.69) · stop_atr=2.5, rr=None, max_bars=2 · no trend filter · sector Industrials, daily | 5 | 27 | 9 → 9 → 9 → 9 → 9 → 9 | +0.50 | finished: 5 rounds |
| `d1991e7084` insider_underwater(buyers=1, discount=0.21) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily | 3 | 23 | 12 → 13 → 13 → 13 | +0.50 | improving |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| insider_opportunistic_wave | 138 | 13/14 | +0.57 | `e11f091ad3` insider_opportunistic_wave(companies=3, window=15) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Utilities, daily |
| insider_sector_wave | 162 | 13/14 | +0.51 | `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_fresh | 202 | 13/14 | +0.48 | `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_sector_laggard | 135 | 13/14 | +0.44 | `68ca8b871d` insider_sector_laggard(buyers=1, lag=0.07) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_fresh_wave | 141 | 13/14 | +0.43 | `242358a81a` insider_fresh_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_underwater | 158 | 13/14 | +0.42 | `a5f89f69c7` insider_underwater(buyers=2, discount=0.1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_deep_value | 123 | 13/14 | +0.40 | `2411fc93a1` insider_deep_value(buyers=4, below=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| insider_after_earnings | 116 | 13/14 | +0.36 | `328f6e08bf` insider_after_earnings(buyers=4, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_consensus | 130 | 13/14 | +0.35 | `46bb8c1223` insider_consensus(votes=3, window=30) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_opportunistic | 87 | 13/14 | +0.35 | `139c078d63` insider_opportunistic(buyers=3, years=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_cluster | 128 | 13/14 | +0.31 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_wave_low_short | 192 | 13/14 | +0.31 | `4073a3fd7e` insider_wave_low_short(companies=5, max_rank=0.3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
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
| insider_fund | 91 | 10/14 | +0.55 | `49cfddaf78` insider_fund(buyers=3, feature=f_sue) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · sector Industrials, daily |
| vwap | 218 | 10/14 | +0.30 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 |
| insider_ml | 11 | 10/14 | +0.22 | `2b1fd2c3d8` insider_ml(model=ridge, keep=0.5) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily |
| ml_rank_short | 4 | 10/14 | +0.10 | `d39c850a7f` ml_rank_short(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| ml_rank_fund | 4 | 9/14 | +0.09 | `dbfedfaad8` ml_rank_fund(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_confirm | 20 | 9/14 | +0.05 | `595f15ef1d` insider_confirm(buyers=3, wait=10) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| volume_breakout | 75 | 8/14 | +0.26 | `2f7b678096` volume_breakout(n=20, m=3.5) · stop_atr=1.5, rr=None, max_bars=3 |
| insider_momentum | 32 | 8/14 | +0.23 | `1b4b882975` insider_momentum(buyers=2, min_rank=0.49) · stop_atr=3.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| insider_big_buy | 72 | 8/14 | +0.15 | `917deb29a5` insider_big_buy(min_value=500000, officer=True) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily |
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
| gap_fade | 15 | 5/14 | -0.17 | `63e0bb1295` gap_fade(g=1.0) · stop_atr=1.5, rr=None, max_bars=1 |
| liquidity_sweep | 20 | 5/14 | -0.25 | `ad23174e9f` liquidity_sweep(n=35, k=0.25) · stop_atr=1.5, rr=None, max_bars=1 |
| earnings_drift | 15 | 5/14 | -0.29 | `6493eb9de4` earnings_drift(x=2.0) · stop_atr=2.0, rr=2.0 |
| high_52w | 36 | 4/14 | -0.29 | `59732b89d7` high_52w(within=0.03) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| btc_lead | 10 | 4/14 | -0.52 | `498531f181` btc_lead(k=0.75) · stop_atr=1.5, rr=None, max_bars=1 |
| overnight_momentum | 8 | 3/14 | -0.12 | `346160c1e6` overnight_momentum(lookback=20, top=0.1) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_dip | 144 | 3/14 | +nan | `c2359d2a01` insider_dip(buyers=2, days=30, drop=0.1) · stop_atr=3.0, rr=None, max_bars=10 · S&P 500, daily |
| momentum_low_short | 8 | 2/14 | -0.13 | `5845cb17fa` momentum_low_short(top=0.05, max_rank=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| earnings_reaction | 27 | 2/14 | -0.17 | `77d24b85f6` earnings_reaction(z=1.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 500, daily |

## The loop: 3182 children tried (improved versions aimed at a parent's failures)

- breadth failed: 93 tried, best 9/14 gates
- edge peaks at 2 bars, exit at 1: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 12: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 5: 1 tried, best 8/14 gates
- edge peaks at 20 bars, exit at 5: 1 tried, best 6/14 gates
- edge peaks at 3 bars, exit at 1: 1 tried, best 8/14 gates
- edge peaks at 40 bars, exit at 10: 2 tried, best 5/14 gates
- edge peaks at 40 bars, exit at 20: 1 tried, best 7/14 gates
- edge peaks at 6 bars, exit at 1: 2 tried, best 6/14 gates
- edge peaks at 6 bars, exit at 2: 1 tried, best 4/14 gates
- edge peaks at 60 bars, exit at 10: 9 tried, best 12/14 gates
- edge peaks at 60 bars, exit at 2: 1 tried, best 9/14 gates
- edge peaks at 60 bars, exit at 20: 17 tried, best 13/14 gates
- edge peaks at 60 bars, exit at 5: 42 tried, best 13/14 gates
- fails in some regime: 175 tried, best 11/14 gates
- no better than random: 790 tried, best 12/14 gates
- parameter neighbour: 1563 tried, best 13/14 gates
- unstable / decaying: 35 tried, best 8/14 gates
- works only in some sectors: 446 tried, best 13/14 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 4379 of 4379
- shelf life: positive in every market regime seen: 2996 of 4379
- shelf life: no decay (2nd half >= half of 1st): 2651 of 4379
- robust: parameter neighbours keep >= half the edge (2+ tested): 2553 of 4379
- shelf life: positive in >= 55% of months: 2379 of 4379
- decay: edge still >= half its peak at the exit, peak after the first bar: 2272 of 4379
- search: ICIR >= 0.2 (stable month to month): 2086 of 4379
- shelf life: works on >= 55% of assets (S&P 500: of sectors): 2065 of 4379
- validation: positive edge: 1984 of 4379
- validation: beats random entries: 1788 of 4379
- search: beats random entries (avg R): 1575 of 4379
- validation: makes money after costs: 1399 of 4379
- search: at least 100 signals: 1335 of 4379
- search: positive edge (IC): 922 of 4379
