# Strategy finder – 2026-10-13

**2138 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Hourly (live universe): search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30. S&P 500 daily: search 2017-01-01 → 2022-12-31, validation 2023-01-01 → 2025-06-30. Both: vault from 2025-07-01 (sealed). 14 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13/14 | `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.537 | +0.51 | +0.993 | +0.13 / +0.07 | +0.05 / +0.03 | +1.8% | 0.06 | 71% | 3/3 | 68% | search: deflated Sharpe >= 0.90 |
| 13/14 | `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.472 | +0.48 | +1.416 | +0.14 / +0.06 | +0.18 / +0.03 | +6.3% | 0.08 | 67% | 3/3 | 79% | search: deflated Sharpe >= 0.90 |
| 13/14 | `4c95df88f7` insider_sector_wave(buyers=3, companies=1) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +0.989 | +0.45 | +0.828 | +0.22 / +0.09 | +0.35 / -0.02 | +6.7% | 0.17 | 59% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 13/14 | `7ac445c110` insider_fresh(buyers=2, gap=178) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.372 | +0.44 | +1.076 | +0.11 / +0.05 | +0.15 / +0.14 | +5.0% | 0.05 | 65% | 3/3 | 71% | search: deflated Sharpe >= 0.90 |
| 13/14 | `421c1c271f` insider_fresh(buyers=2, gap=175) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.364 | +0.44 | +1.344 | +0.12 / +0.06 | +0.20 / +0.16 | +6.7% | 0.06 | 66% | 3/3 | 71% | search: deflated Sharpe >= 0.90 |
| 13/14 | `86755b6c71` insider_sector_wave(buyers=3, companies=4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.164 | +0.43 | +0.901 | +0.05 / +0.03 | +0.23 / +0.00 | +10.8% | 0.01 | 60% | 3/3 | 70% | search: deflated Sharpe >= 0.90 |
| 13/14 | `b2f8149f5f` insider_fresh(buyers=1, gap=1001) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily | +0.911 | +0.38 | +1.227 | +0.30 / +0.13 | +0.04 / -0.02 | +1.6% | 0.71 | 65% | 3/3 | 58% | search: deflated Sharpe >= 0.90 |
| 13/14 | `a445c81f44` insider_fresh(buyers=1, gap=730) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily | +0.882 | +0.37 | +1.313 | +0.29 / +0.13 | +0.04 / -0.03 | +1.9% | 0.70 | 64% | 3/3 | 60% | search: deflated Sharpe >= 0.90 |
| 13/14 | `328f6e08bf` insider_after_earnings(buyers=4, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.965 | +0.36 | +0.401 | +0.05 / -0.01 | +0.24 / -0.02 | +17.4% | 0.02 | 66% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `7ea781d068` insider_after_earnings(buyers=4, window=55) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.033 | +0.36 | +0.562 | +0.05 / +0.02 | +0.19 / -0.07 | +12.2% | 0.02 | 63% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `6931885bc6` insider_after_earnings(buyers=4, window=56) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.032 | +0.36 | +0.562 | +0.05 / +0.03 | +0.19 / -0.07 | +12.2% | 0.02 | 63% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `51028b78a0` insider_fresh(buyers=1, gap=701) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily | +0.841 | +0.35 | +1.313 | +0.29 / +0.13 | +0.04 / -0.03 | +1.9% | 0.70 | 64% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 13/14 | `64a39c60ff` insider_fresh(buyers=2, gap=125) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +0.871 | +0.34 | +0.902 | +0.14 / +0.07 | +0.17 / +0.06 | +6.0% | 0.09 | 66% | 3/3 | 67% | search: deflated Sharpe >= 0.90 |
| 13/14 | `fda4e627ca` insider_fresh(buyers=2, gap=255) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +0.956 | +0.34 | +0.806 | +0.15 / +0.02 | +0.20 / +0.10 | +6.0% | 0.09 | 62% | 3/3 | 77% | search: deflated Sharpe >= 0.90 |
| 13/14 | `5f890c249b` insider_fresh(buyers=1, gap=715) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Health Care, daily | +0.830 | +0.34 | +1.313 | +0.29 / +0.13 | +0.04 / -0.03 | +1.9% | 0.69 | 64% | 3/3 | 61% | search: deflated Sharpe >= 0.90 |
| 13/14 | `838f9f25fc` insider_after_earnings(buyers=4, window=39) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.813 | +0.32 | +0.577 | +0.02 / -0.01 | +0.17 / -0.06 | +9.6% | 0.01 | 57% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `bc7644d470` insider_sector_wave(buyers=3, companies=5) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.090 | +0.32 | +0.630 | +0.05 / +0.02 | +0.15 / -0.04 | +5.3% | 0.01 | 65% | 3/3 | 70% | search: deflated Sharpe >= 0.90 |
| 13/14 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +0.901 | +0.31 | +0.482 | +0.33 / +0.19 | +0.44 / +0.03 | +8.5% | 0.12 | 56% | 3/3 | 60% | search: deflated Sharpe >= 0.90 |
| 13/14 | `21e138e709` insider_sector_wave(buyers=3, companies=1) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +0.901 | +0.31 | +0.482 | +0.19 / +0.09 | +0.42 / +0.08 | +8.0% | 0.11 | 56% | 3/3 | 60% | search: deflated Sharpe >= 0.90 |
| 13/14 | `8e70310249` insider_after_earnings(buyers=3, window=56) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.849 | +0.31 | +0.403 | +0.06 / +0.04 | +0.14 / -0.09 | +13.6% | 0.02 | 67% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `44017edf7c` insider_after_earnings(buyers=4, window=40) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.792 | +0.31 | +0.577 | +0.01 / -0.01 | +0.17 / -0.06 | +9.6% | 0.01 | 59% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `09a08ad601` insider_low_short(buyers=3, max_rank=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.715 | +0.30 | +0.101 | +0.09 / +0.07 | +0.29 / -0.16 | +17.4% | 0.04 | 63% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `2620a78123` insider_fresh(buyers=2, gap=511) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +0.559 | +0.30 | +0.442 | +0.17 / +0.06 | +0.23 / +0.12 | +5.9% | 0.11 | 64% | 3/3 | 68% | search: deflated Sharpe >= 0.90 |
| 13/14 | `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.671 | +0.30 | +0.294 | +0.14 / +0.06 | +0.20 / +0.07 | +43.0% | 0.13 | 64% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `0326639ede` insider_sector_wave(buyers=3, companies=5) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily | +0.962 | +0.29 | +0.056 | +0.07 / +0.05 | +0.11 / -0.04 | +3.1% | 0.01 | 58% | 3/3 | 60% | search: deflated Sharpe >= 0.90 |

## Campaigns: each idea refined round by round (max 5 rounds)

849 ideas tried; **86 still improving** (search ICIR >= 0.2), 753 dropped below the bar, 10 finished their 5 rounds.

| idea → best version so far | rounds | tried | gates by round | ICIR | status |
|---|---|---|---|---|---|
| `12d0fbe88f` insider_sector_wave(buyers=2, companies=6) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 3 | 24 | 9 → 11 → 11 → 11 | +0.84 | improving |
| `f28ff156e8` insider_after_earnings(buyers=2, window=20) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 1 | 5 | 9 → 12 | +0.57 | improving |
| `f901b767fe` insider_after_earnings(buyers=2, window=20) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | 3 | 23 | 5 → 7 → 9 → 12 | +0.57 | improving |
| `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter | 2 | 7 | 6 → 6 → 6 | +0.54 | improving |
| `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 1 | 3 | 13 → 13 | +0.51 | improving |
| `4329d91d97` insider_conviction(buyers=2, min_bp=1.4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 2 | 11 | 11 → 11 → 11 | +0.48 | improving |
| `053e9be7a4` opening_range(n_open=2) · stop_atr=1.5, rr=None, max_bars=1 | 2 | 8 | 6 → 6 → 6 | +0.48 | improving |
| `24eb4c6a92` insider_sector_wave(buyers=3, companies=7) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 2 | 7 | 13 → 13 → 13 | +0.48 | improving |
| `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 4 | 16 | 11 → 13 → 13 → 13 → 13 | +0.48 | improving |
| `cdf979df11` vwap(k=1.4, trend_ma=200) · stop_atr=1.5, rr=2.0, max_bars=2 · no trend filter | 4 | 38 | 5 → 8 → 8 → 8 → 8 | +0.46 | improving |
| `174c50c147` insider_fresh_officer(buyers=1, gap=255) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 1500, daily | 3 | 20 | 11 → 11 → 11 → 11 | +0.46 | improving |
| `4c95df88f7` insider_sector_wave(buyers=3, companies=1) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | 3 | 10 | 11 → 12 → 13 → 13 | +0.45 | improving |
| `f0d3eb20d1` insider_sector_wave(buyers=1, companies=3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Utilities, daily | 3 | 24 | 9 → 10 → 10 → 10 | +0.44 | improving |
| `2a5e38599b` insider_sector_wave(buyers=2, companies=3) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | 1 | 3 | 11 → 11 | +0.43 | improving |
| `3c2af23c58` insider_fresh_officer(buyers=1, gap=1401) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | 4 | 9 | 12 → 12 → 12 → 12 → 12 | +0.42 | improving |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| insider_sector_wave | 162 | 13/14 | +0.51 | `1c8ea0c123` insider_sector_wave(buyers=2, companies=3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_fresh | 202 | 13/14 | +0.48 | `f917e075fd` insider_fresh(buyers=2, gap=125) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_after_earnings | 116 | 13/14 | +0.36 | `328f6e08bf` insider_after_earnings(buyers=4, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_cluster | 128 | 13/14 | +0.31 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_low_short | 120 | 13/14 | +0.30 | `09a08ad601` insider_low_short(buyers=3, max_rank=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_fresh_officer | 183 | 13/14 | +0.26 | `001247d2a3` insider_fresh_officer(buyers=1, gap=511) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily |
| insider_conviction | 121 | 12/14 | +0.15 | `bb35082f6c` insider_conviction(buyers=3, min_bp=3.92) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_fund | 91 | 10/14 | +0.55 | `49cfddaf78` insider_fund(buyers=3, feature=f_sue) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · sector Industrials, daily |
| vwap | 218 | 10/14 | +0.30 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 |
| insider_ml | 11 | 10/14 | +0.22 | `2b1fd2c3d8` insider_ml(model=ridge, keep=0.5) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily |
| ml_rank_short | 4 | 10/14 | +0.10 | `d39c850a7f` ml_rank_short(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| ml_rank_fund | 4 | 9/14 | +0.09 | `dbfedfaad8` ml_rank_fund(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| insider_confirm | 20 | 9/14 | +0.05 | `595f15ef1d` insider_confirm(buyers=3, wait=10) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · S&P 1500, daily |
| volume_breakout | 75 | 8/14 | +0.26 | `2f7b678096` volume_breakout(n=20, m=3.5) · stop_atr=1.5, rr=None, max_bars=3 |
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
| gap_fade | 15 | 5/14 | -0.17 | `63e0bb1295` gap_fade(g=1.0) · stop_atr=1.5, rr=None, max_bars=1 |
| earnings_drift | 15 | 5/14 | -0.29 | `6493eb9de4` earnings_drift(x=2.0) · stop_atr=2.0, rr=2.0 |
| high_52w | 36 | 4/14 | -0.29 | `59732b89d7` high_52w(within=0.03) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| btc_lead | 10 | 4/14 | -0.52 | `498531f181` btc_lead(k=0.75) · stop_atr=1.5, rr=None, max_bars=1 |
| insider_dip | 144 | 3/14 | +nan | `c2359d2a01` insider_dip(buyers=2, days=30, drop=0.1) · stop_atr=3.0, rr=None, max_bars=10 · S&P 500, daily |
| earnings_reaction | 27 | 2/14 | -0.17 | `77d24b85f6` earnings_reaction(z=1.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 500, daily |

## The loop: 1289 children tried (improved versions aimed at a parent's failures)

- breadth failed: 93 tried, best 9/14 gates
- edge peaks at 2 bars, exit at 1: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 12: 1 tried, best 6/14 gates
- edge peaks at 20 bars, exit at 5: 1 tried, best 6/14 gates
- edge peaks at 3 bars, exit at 1: 1 tried, best 8/14 gates
- edge peaks at 40 bars, exit at 10: 2 tried, best 5/14 gates
- edge peaks at 6 bars, exit at 1: 2 tried, best 6/14 gates
- edge peaks at 6 bars, exit at 2: 1 tried, best 4/14 gates
- edge peaks at 60 bars, exit at 10: 3 tried, best 7/14 gates
- edge peaks at 60 bars, exit at 20: 8 tried, best 12/14 gates
- edge peaks at 60 bars, exit at 5: 12 tried, best 13/14 gates
- fails in some regime: 66 tried, best 11/14 gates
- no better than random: 334 tried, best 12/14 gates
- parameter neighbour: 623 tried, best 13/14 gates
- unstable / decaying: 35 tried, best 8/14 gates
- works only in some sectors: 106 tried, best 13/14 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 2138 of 2138
- shelf life: positive in every market regime seen: 1602 of 2138
- shelf life: no decay (2nd half >= half of 1st): 1506 of 2138
- shelf life: positive in >= 55% of months: 1400 of 2138
- robust: parameter neighbours keep >= half the edge (2+ tested): 1374 of 2138
- decay: edge still >= half its peak at the exit, peak after the first bar: 1301 of 2138
- shelf life: works on >= 55% of assets (S&P 500: of sectors): 1245 of 2138
- search: ICIR >= 0.2 (stable month to month): 1238 of 2138
- validation: positive edge: 1215 of 2138
- validation: beats random entries: 1046 of 2138
- validation: makes money after costs: 887 of 2138
- search: beats random entries (avg R): 833 of 2138
- search: positive edge (IC): 734 of 2138
- search: at least 100 signals: 673 of 2138
