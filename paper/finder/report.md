# Strategy finder – 2026-10-09

**1563 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Hourly (live universe): search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30. S&P 500 daily: search 2017-01-01 → 2022-12-31, validation 2023-01-01 → 2025-06-30. Both: vault from 2025-07-01 (sealed). 14 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13/14 | `328f6e08bf` insider_after_earnings(buyers=4, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.965 | +0.36 | +0.401 | +0.05 / -0.01 | +0.24 / -0.02 | +17.4% | 0.02 | 66% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `7ea781d068` insider_after_earnings(buyers=4, window=55) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.033 | +0.36 | +0.562 | +0.05 / +0.02 | +0.19 / -0.07 | +12.2% | 0.02 | 63% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `6931885bc6` insider_after_earnings(buyers=4, window=56) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +1.032 | +0.36 | +0.562 | +0.05 / +0.03 | +0.19 / -0.07 | +12.2% | 0.02 | 63% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `838f9f25fc` insider_after_earnings(buyers=4, window=39) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.813 | +0.32 | +0.577 | +0.02 / -0.01 | +0.17 / -0.06 | +9.6% | 0.01 | 57% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +0.901 | +0.31 | +0.482 | +0.33 / +0.19 | +0.44 / +0.03 | +8.5% | 0.13 | 56% | 3/3 | 60% | search: deflated Sharpe >= 0.90 |
| 13/14 | `8e70310249` insider_after_earnings(buyers=3, window=56) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.849 | +0.31 | +0.403 | +0.06 / +0.04 | +0.14 / -0.09 | +13.6% | 0.02 | 67% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `44017edf7c` insider_after_earnings(buyers=4, window=40) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.792 | +0.31 | +0.577 | +0.01 / -0.01 | +0.17 / -0.06 | +9.6% | 0.01 | 59% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `09a08ad601` insider_low_short(buyers=3, max_rank=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.715 | +0.30 | +0.101 | +0.09 / +0.07 | +0.29 / -0.16 | +17.4% | 0.04 | 63% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 13/14 | `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.671 | +0.30 | +0.294 | +0.14 / +0.06 | +0.20 / +0.07 | +43.0% | 0.14 | 64% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 13/14 | `e6600973ed` insider_after_earnings(buyers=3, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.735 | +0.27 | +0.503 | +0.06 / +0.04 | +0.15 / -0.12 | +15.7% | 0.03 | 67% | 3/3 | 91% | search: deflated Sharpe >= 0.90 |
| 13/14 | `952f218d64` insider_cluster(buyers=3, days=63) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +0.789 | +0.26 | +0.508 | +0.29 / +0.15 | +0.64 / -0.14 | +11.9% | 0.09 | 56% | 3/3 | 56% | search: deflated Sharpe >= 0.90 |
| 12/14 | `e49d2c667b` insider_low_short(buyers=3, max_rank=0.7) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | +0.812 | +0.42 | +1.007 | +0.25 / +0.10 | +0.41 / +0.08 | +6.0% | 0.20 | 55% | 3/3 | 75% | search: at least 100 signals |
| 12/14 | `c52a8de961` insider_after_earnings(buyers=3, window=40) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | +0.343 | +0.37 | +0.358 | +0.04 / +0.04 | +0.20 / +0.02 | +18.0% | 0.02 | 61% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 12/14 | `c52a8de961` insider_after_earnings(buyers=3, window=40) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | +0.343 | +0.37 | +0.358 | +0.04 / +0.04 | +0.20 / +0.02 | +18.0% | 0.02 | 61% | 3/3 | 73% | search: deflated Sharpe >= 0.90 |
| 12/14 | `8019fffec4` insider_after_earnings(buyers=2, window=28) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.077 | +0.37 | +0.646 | +0.14 / +0.08 | +0.10 / -0.12 | +2.3% | 0.07 | 64% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 12/14 | `8019fffec4` insider_after_earnings(buyers=2, window=28) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.077 | +0.37 | +0.646 | +0.14 / +0.08 | +0.10 / -0.12 | +2.3% | 0.07 | 64% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 12/14 | `dc5e50c65b` insider_after_earnings(buyers=2, window=28) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +1.077 | +0.37 | +0.646 | +0.28 / +0.16 | +0.11 / -0.10 | +2.4% | 0.15 | 64% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 12/14 | `dc5e50c65b` insider_after_earnings(buyers=2, window=28) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +1.077 | +0.37 | +0.646 | +0.28 / +0.16 | +0.11 / -0.10 | +2.4% | 0.15 | 64% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 12/14 | `f263e18180` insider_after_earnings(buyers=3, window=39) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.776 | +0.36 | +0.555 | +0.02 / +0.05 | +0.15 / -0.00 | +13.8% | 0.01 | 63% | 3/3 | 82% | search: beats random entries (avg R) |
| 12/14 | `3f8fedf1fd` insider_after_earnings(buyers=3, window=40) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily | +0.770 | +0.36 | +0.555 | +0.02 / +0.05 | +0.15 / -0.00 | +13.8% | 0.01 | 63% | 3/3 | 82% | search: beats random entries (avg R) |
| 12/14 | `4dc52b042f` insider_after_earnings(buyers=3, window=40) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +0.770 | +0.36 | +0.555 | +0.18 / +0.14 | +0.29 / -0.02 | +22.9% | 0.08 | 63% | 3/3 | 82% | search: deflated Sharpe >= 0.90 |
| 12/14 | `5ae36d18d1` insider_cluster(buyers=2, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +1.100 | +0.36 | +0.829 | +0.33 / +0.20 | +0.16 / -0.02 | +6.1% | 0.20 | 69% | 3/3 | 69% | search: deflated Sharpe >= 0.90 |
| 12/14 | `8f5265ea70` insider_after_earnings(buyers=2, window=40) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.082 | +0.36 | +0.668 | +0.12 / +0.10 | +0.05 / -0.04 | +1.2% | 0.05 | 65% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 12/14 | `fe65146e81` insider_after_earnings(buyers=2, window=40) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +1.082 | +0.36 | +0.668 | +0.26 / +0.17 | +0.09 / -0.01 | +2.1% | 0.13 | 65% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 12/14 | `34896ac0ab` insider_low_short(buyers=2, max_rank=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | +1.284 | +0.34 | +0.167 | +0.30 / +0.13 | +0.24 / -0.02 | +4.6% | 0.28 | 59% | 3/3 | 69% | search: deflated Sharpe >= 0.90 |

## Campaigns: each idea refined round by round (max 5 rounds)

785 ideas tried; **45 still improving** (search ICIR >= 0.2), 733 dropped below the bar, 7 finished their 5 rounds.

| idea → best version so far | rounds | tried | gates by round | ICIR | status |
|---|---|---|---|---|---|
| `f901b767fe` insider_after_earnings(buyers=2, window=20) · stop_atr=3.0, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | 3 | 23 | 5 → 7 → 9 → 12 | +0.57 | improving |
| `f28ff156e8` insider_after_earnings(buyers=2, window=20) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 1 | 5 | 9 → 12 | +0.57 | improving |
| `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter | 2 | 7 | 6 → 6 → 6 | +0.54 | improving |
| `4329d91d97` insider_conviction(buyers=2, min_bp=1.4) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 2 | 11 | 11 → 11 → 11 | +0.48 | improving |
| `053e9be7a4` opening_range(n_open=2) · stop_atr=1.5, rr=None, max_bars=1 | 2 | 8 | 6 → 6 → 6 | +0.48 | improving |
| `cdf979df11` vwap(k=1.4, trend_ma=200) · stop_atr=1.5, rr=2.0, max_bars=2 · no trend filter | 4 | 38 | 5 → 8 → 8 → 8 → 8 | +0.46 | improving |
| `950db9dff5` vwap(k=2.0, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter | 5 | 76 | 5 → 6 → 6 → 9 → 10 → 10 | +0.42 | finished: 5 rounds |
| `7f766ee2f4` insider_low_short(buyers=3, max_rank=0.3) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 2 | 22 | 11 → 11 → 11 | +0.40 | improving |
| `4180a0110d` insider_fund(buyers=2, feature=f_sue) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · sector Industrials, daily | 1 | 2 | 9 → 9 | +0.39 | improving |
| `5a5d0b719f` insider_low_short(buyers=2, max_rank=0.35) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | 2 | 7 | 11 → 11 → 11 | +0.39 | improving |
| `d06da1513b` insider_low_short(buyers=2, max_rank=0.42) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | 2 | 7 | 9 → 10 → 11 | +0.39 | improving |
| `02c6d2bd91` insider_conviction(buyers=2, min_bp=1.4) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | 2 | 12 | 8 → 11 → 11 | +0.38 | improving |
| `5608c2ae05` insider_fund(buyers=2, feature=f_sue) · stop_atr=4.0, rr=None, max_bars=40 · no trend filter · sector Industrials, daily | 1 | 3 | 7 → 7 | +0.38 | improving |
| `c52a8de961` insider_after_earnings(buyers=3, window=40) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily | 2 | 14 | 11 → 12 → 12 | +0.37 | improving |
| `1569ac03d0` volume_breakout(n=14, m=2.45) · stop_atr=1.5, rr=None, max_bars=3 · no trend filter | 5 | 56 | 6 → 6 → 8 → 8 → 8 → 8 | +0.37 | finished: 5 rounds |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| insider_after_earnings | 116 | 13/14 | +0.36 | `328f6e08bf` insider_after_earnings(buyers=4, window=78) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_cluster | 128 | 13/14 | +0.31 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily |
| insider_low_short | 120 | 13/14 | +0.30 | `09a08ad601` insider_low_short(buyers=3, max_rank=0.42) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_conviction | 113 | 12/14 | +0.15 | `bb35082f6c` insider_conviction(buyers=3, min_bp=3.92) · stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 · no trend filter · S&P 1500, daily |
| insider_fund | 91 | 10/14 | +0.55 | `49cfddaf78` insider_fund(buyers=3, feature=f_sue) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · sector Industrials, daily |
| vwap | 218 | 10/14 | +0.30 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 |
| insider_ml | 11 | 10/14 | +0.22 | `2b1fd2c3d8` insider_ml(model=ridge, keep=0.5) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily |
| ml_rank_short | 4 | 10/14 | +0.10 | `d39c850a7f` ml_rank_short(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| ml_rank_fund | 4 | 9/14 | +0.09 | `dbfedfaad8` ml_rank_fund(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
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

## The loop: 778 children tried (improved versions aimed at a parent's failures)

- breadth failed: 93 tried, best 9/14 gates
- edge peaks at 2 bars, exit at 1: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 12: 1 tried, best 6/14 gates
- edge peaks at 20 bars, exit at 5: 1 tried, best 6/14 gates
- edge peaks at 3 bars, exit at 1: 1 tried, best 8/14 gates
- edge peaks at 40 bars, exit at 10: 2 tried, best 5/14 gates
- edge peaks at 6 bars, exit at 1: 2 tried, best 6/14 gates
- edge peaks at 6 bars, exit at 2: 1 tried, best 4/14 gates
- edge peaks at 60 bars, exit at 10: 3 tried, best 7/14 gates
- edge peaks at 60 bars, exit at 20: 4 tried, best 12/14 gates
- edge peaks at 60 bars, exit at 5: 4 tried, best 13/14 gates
- fails in some regime: 49 tried, best 11/14 gates
- no better than random: 182 tried, best 12/14 gates
- parameter neighbour: 355 tried, best 13/14 gates
- unstable / decaying: 35 tried, best 8/14 gates
- works only in some sectors: 44 tried, best 12/14 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 1563 of 1563
- shelf life: positive in every market regime seen: 1298 of 1563
- shelf life: positive in >= 55% of months: 1217 of 1563
- shelf life: no decay (2nd half >= half of 1st): 1206 of 1563
- shelf life: works on >= 55% of assets (S&P 500: of sectors): 1094 of 1563
- robust: parameter neighbours keep >= half the edge (2+ tested): 1086 of 1563
- search: ICIR >= 0.2 (stable month to month): 1066 of 1563
- decay: edge still >= half its peak at the exit, peak after the first bar: 1042 of 1563
- validation: positive edge: 1040 of 1563
- validation: beats random entries: 841 of 1563
- validation: makes money after costs: 784 of 1563
- search: positive edge (IC): 697 of 1563
- search: beats random entries (avg R): 676 of 1563
- search: at least 100 signals: 506 of 1563
