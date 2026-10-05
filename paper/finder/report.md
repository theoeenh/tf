# Strategy finder – 2026-10-05

**881 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Hourly (live universe): search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30. S&P 500 daily: search 2017-01-01 → 2022-12-31, validation 2023-01-01 → 2025-06-30. Both: vault from 2025-07-01 (sealed). 14 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13/14 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +0.901 | +0.31 | +0.482 | +0.33 / +0.19 | +0.44 / +0.03 | +8.5% | 0.14 | 56% | 3/3 | 60% | search: deflated Sharpe >= 0.90 |
| 13/14 | `952f218d64` insider_cluster(buyers=3, days=63) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +0.789 | +0.26 | +0.508 | +0.29 / +0.15 | +0.64 / -0.14 | +11.9% | 0.10 | 56% | 3/3 | 56% | search: deflated Sharpe >= 0.90 |
| 12/14 | `5ae36d18d1` insider_cluster(buyers=2, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +1.100 | +0.36 | +0.829 | +0.33 / +0.20 | +0.16 / -0.02 | +6.1% | 0.21 | 69% | 3/3 | 69% | search: deflated Sharpe >= 0.90 |
| 12/14 | `0cd9aea7bb` insider_cluster(buyers=2, days=126) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +1.045 | +0.33 | +0.962 | +0.35 / +0.11 | +0.27 / +0.03 | +10.3% | 0.24 | 60% | 3/3 | 67% | search: deflated Sharpe >= 0.90 |
| 12/14 | `8f2d51923b` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · sector Industrials, daily | +0.290 | +0.30 | +0.272 | +0.03 / -0.01 | +0.25 / -0.06 | +4.8% | 0.02 | 60% | 3/3 | 69% | search: deflated Sharpe >= 0.90 |
| 12/14 | `61bbcae60c` insider_cluster(buyers=2, days=63) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +0.736 | +0.21 | +0.766 | +0.26 / +0.03 | +0.21 / +0.08 | +7.9% | 0.12 | 65% | 3/3 | 62% | search: deflated Sharpe >= 0.90 |
| 11/14 | `8b323c3fd9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 400 (mid), daily | +0.299 | +0.29 | +0.209 | +0.02 / -0.05 | +0.07 / -0.06 | +2.7% | 0.02 | 59% | 2/3 | 60% | search: deflated Sharpe >= 0.90 |
| 10/14 | `fc4e415d3e` insider_cluster(buyers=4, days=90) · stop_atr=2.5, rr=None, max_bars=5 · S&P 400 (mid), daily | +0.464 | +0.40 | +0.564 | +0.24 / -0.02 | +0.22 / -0.10 | +1.2% | 0.38 | 56% | 3/3 | 56% | search: at least 100 signals |
| 10/14 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 | +0.400 | +0.30 | -0.166 | -0.16 / -0.37 | -0.56 / -0.57 | -5.7% | 0.00 | 65% | 3/3 | 57% | search: deflated Sharpe >= 0.90 |
| 10/14 | `4e73785ef8` insider_cluster(buyers=3, days=63) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · sector Industrials, daily | +0.258 | +0.30 | +0.259 | +0.00 / -0.02 | +0.25 / -0.08 | +4.8% | 0.01 | 62% | 3/3 | 53% | search: deflated Sharpe >= 0.90 |
| 10/14 | `5465a6617d` insider_cluster(buyers=3, days=63) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 400 (mid), daily | +0.261 | +0.29 | +0.334 | +0.03 / -0.00 | +0.07 / -0.02 | +2.7% | 0.02 | 59% | 2/3 | 60% | search: deflated Sharpe >= 0.90 |
| 10/14 | `22f2cf8089` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | +0.246 | +0.25 | +0.027 | -0.00 / -0.08 | +0.22 / +0.06 | +3.5% | 0.01 | 38% | 2/3 | 73% | search: deflated Sharpe >= 0.90 |
| 10/14 | `fc61d538d1` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 600 (small), daily | +0.180 | +0.25 | +0.397 | -0.04 / -0.02 | +0.07 / -0.03 | +5.9% | 0.00 | 62% | 3/3 | 64% | search: beats random entries (avg R) |
| 10/14 | `9e6d2690bf` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · S&P 400 (mid), daily | +0.535 | +0.15 | +0.112 | +0.16 / +0.02 | +0.32 / +0.07 | +11.0% | 0.04 | 60% | 2/3 | 70% | search: ICIR >= 0.2 (stable month to month) |
| 9/14 | `607b5bc2db` vwap(k=2.0, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 | +0.326 | +0.36 | -0.809 | -0.50 / -0.63 | -1.03 / -0.66 | -12.0% | 0.00 | 61% | 3/3 | 57% | search: deflated Sharpe >= 0.90 |
| 9/14 | `168c792129` vwap(k=1.4, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 · crypto | +0.247 | +0.34 | -0.620 | -0.74 / -0.87 | -1.05 / -0.75 | -25.0% | 0.00 | 56% | 3/3 | 100% | search: deflated Sharpe >= 0.90 |
| 9/14 | `c1954764eb` insider_cluster(buyers=4, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +1.168 | +0.30 | +0.495 | +0.30 / -0.02 | +0.54 / +0.21 | +7.8% | 0.07 | 54% | 3/3 | 73% | search: at least 100 signals |
| 9/14 | `b6da4084f1` insider_cluster(buyers=2, days=30) · stop_atr=2.5, rr=None, max_bars=5 · no trend filter · S&P 600 (small), daily | +0.155 | +0.26 | +0.288 | -0.03 / -0.02 | +0.03 / -0.04 | +5.1% | 0.00 | 62% | 2/3 | 64% | search: beats random entries (avg R) |
| 9/14 | `848685498b` vwap(k=2.1, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 | +0.353 | +0.24 | -0.033 | -0.20 / -0.39 | -0.46 / -0.56 | -4.6% | 0.00 | 61% | 3/3 | 57% | search: deflated Sharpe >= 0.90 |
| 9/14 | `2b1fd2c3d8` insider_ml(model=ridge, keep=0.5) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | +0.574 | +0.22 | -0.109 | +0.20 / +0.13 | +0.20 / +0.16 | +20.6% | 0.09 | 60% | 2/3 | 91% | search: deflated Sharpe >= 0.90 |
| 9/14 | `3aa989920a` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · S&P 400 (mid), daily | +0.196 | +0.21 | +0.115 | +0.05 / -0.06 | +0.18 / +0.15 | +1.6% | 0.02 | 47% | 2/3 | 70% | search: at least 100 signals |
| 9/14 | `10dd566f33` insider_cluster(buyers=3, days=63) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | +0.181 | +0.20 | +0.067 | +0.03 / -0.00 | +0.38 / -0.16 | +4.9% | 0.02 | 41% | 2/3 | 64% | search: deflated Sharpe >= 0.90 |
| 9/14 | `2825440182` vwap(k=1.4, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter · etfs | +0.128 | +0.08 | +1.210 | -0.01 / -0.09 | +0.74 / +0.15 | +6.4% | 0.00 | 64% | 2/3 | 83% | search: at least 100 signals |
| 9/14 | `e0a30c37a4` insider_cluster(buyers=3, days=126) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | +0.219 | +0.08 | +0.027 | +0.23 / +0.02 | +0.49 / +0.22 | +8.6% | 0.06 | 48% | 2/3 | 54% | search: ICIR >= 0.2 (stable month to month) |
| 8/14 | `e9c5ab5b0c` vwap(k=2.8, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 · crypto | +1.007 | +0.62 | +0.000 | -0.53 / -0.76 | -0.58 / -0.70 | -0.7% | 0.00 | 77% | 2/2 | 67% | search: at least 100 signals |

## Campaigns: each idea refined round by round (max 5 rounds)

505 ideas tried; **9 still improving** (search ICIR >= 0.2), 491 dropped below the bar, 5 finished their 5 rounds.

| idea → best version so far | rounds | tried | gates by round | ICIR | status |
|---|---|---|---|---|---|
| `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter | 2 | 7 | 6 → 6 → 6 | +0.54 | improving |
| `053e9be7a4` opening_range(n_open=2) · stop_atr=1.5, rr=None, max_bars=1 | 2 | 8 | 6 → 6 → 6 | +0.48 | improving |
| `cdf979df11` vwap(k=1.4, trend_ma=200) · stop_atr=1.5, rr=2.0, max_bars=2 · no trend filter | 4 | 38 | 5 → 8 → 8 → 8 → 8 | +0.46 | improving |
| `950db9dff5` vwap(k=2.0, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter | 5 | 76 | 5 → 6 → 6 → 9 → 10 → 10 | +0.42 | finished: 5 rounds |
| `1569ac03d0` volume_breakout(n=14, m=2.45) · stop_atr=1.5, rr=None, max_bars=3 · no trend filter | 5 | 56 | 6 → 6 → 8 → 8 → 8 → 8 | +0.37 | finished: 5 rounds |
| `dd6ad11159` vwap(k=2.1, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter | 6 | 91 | 8 → 8 → 8 → 9 → 9 → 9 → 9 | +0.37 | finished: 5 rounds |
| `5ae36d18d1` insider_cluster(buyers=2, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily | 5 | 27 | 9 → 11 → 12 → 13 → 13 → 13 | +0.36 | finished: 5 rounds |
| `7e029ba100` donchian(n=118, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=2 · no trend filter | 5 | 60 | 7 → 7 → 7 → 7 → 7 → 7 | +0.34 | finished: 5 rounds |
| `f1f39c6aa7` insider_cluster(buyers=2, days=30) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | 1 | 7 | 8 → 9 | +0.32 | improving |
| `ca7bd50459` insider_cluster(buyers=2, days=30) · stop_atr=3.0, rr=None, max_bars=10 · S&P 600 (small), daily | 0 | 1 | 8 | +0.26 | improving |
| `904de204f7` insider_cluster(buyers=3, days=90) · stop_atr=3.0, rr=None, max_bars=10 · S&P 600 (small), daily | 0 | 1 | 8 | +0.26 | improving |
| `22f2cf8089` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | 1 | 6 | 10 → 10 | +0.25 | improving |
| `49c6823bad` donchian(n=120, trend_ma=100) · stop_atr=1.5, rr=None, max_bars=1 | 1 | 11 | 7 → 7 | +0.23 | improving |
| `2b1fd2c3d8` insider_ml(model=ridge, keep=0.5) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily | 0 | 1 | 9 | +0.22 | improving |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| insider_cluster | 101 | 13/14 | +0.31 | `5aca4825d9` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=60 · no trend filter · sector Industrials, daily |
| vwap | 218 | 10/14 | +0.30 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 |
| insider_ml | 4 | 9/14 | +0.22 | `2b1fd2c3d8` insider_ml(model=ridge, keep=0.5) · stop_atr=4.0, rr=None, max_bars=60 · no trend filter · S&P 1500, daily |
| volume_breakout | 75 | 8/14 | +0.26 | `2f7b678096` volume_breakout(n=20, m=3.5) · stop_atr=1.5, rr=None, max_bars=3 |
| insider_big_buy | 48 | 8/14 | +0.15 | `917deb29a5` insider_big_buy(min_value=500000, officer=True) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily |
| ml_rank | 4 | 8/14 | +0.09 | `9757090abb` ml_rank(model=ridge, top=0.05) · stop_atr=3.0, rr=None, max_bars=20 · no trend filter · S&P 1500, daily |
| reversal_5d | 24 | 8/14 | -0.05 | `cbc6e766e6` reversal_5d(bottom=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| donchian | 100 | 7/14 | +0.33 | `e4dbf9e4e1` donchian(n=118, trend_ma=140) · stop_atr=1.5, rr=None, max_bars=2 · no trend filter |
| opening_range | 24 | 6/14 | +0.54 | `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter |
| xs_reversal | 30 | 6/14 | +0.15 | `d2867573f6` xs_reversal(lookback=6, bottom=4) · stop_atr=1.5, rr=None, max_bars=1 |
| xs_momentum | 30 | 6/14 | +0.05 | `7ffb46fdcc` xs_momentum(lookback=120, top=4) · stop_atr=1.0, rr=1.5, max_bars=6 |
| earnings_overreaction | 27 | 6/14 | +0.04 | `9493c2c5f1` earnings_overreaction(z=3.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 600 (small), daily |
| momentum_12_1 | 24 | 6/14 | +0.04 | `9171f4b689` momentum_12_1(top=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| rsi2 | 41 | 6/14 | -0.00 | `9dcb4f23b3` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=1 |
| intraday_momentum | 15 | 6/14 | -0.22 | `52f33b3180` intraday_momentum(k=1.0) · stop_atr=2.0, rr=2.0 |
| squeeze | 21 | 6/14 | -0.36 | `5f107ac95d` squeeze() · stop_atr=3.0, rr=None, trail_atr=4.0, adx_threshold=25.0 · stocks+etfs |
| gap_fade | 15 | 5/14 | -0.17 | `63e0bb1295` gap_fade(g=1.0) · stop_atr=1.5, rr=None, max_bars=1 |
| earnings_drift | 15 | 5/14 | -0.29 | `6493eb9de4` earnings_drift(x=2.0) · stop_atr=2.0, rr=2.0 |
| high_52w | 24 | 4/14 | -0.29 | `59732b89d7` high_52w(within=0.03) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| btc_lead | 10 | 4/14 | -0.52 | `498531f181` btc_lead(k=0.75) · stop_atr=1.5, rr=None, max_bars=1 |
| earnings_reaction | 27 | 2/14 | -0.17 | `77d24b85f6` earnings_reaction(z=1.5, volume=1.5) · stop_atr=3.0, rr=None, max_bars=20 · S&P 500, daily |
| insider_dip | 4 | 1/14 | +nan | `a2df72a395` insider_dip(buyers=2, days=30, drop=0.1) · stop_atr=4.0, rr=None, max_bars=40 · S&P 600 (small), daily |

## The loop: 376 children tried (improved versions aimed at a parent's failures)

- breadth failed: 93 tried, best 9/14 gates
- edge peaks at 2 bars, exit at 1: 1 tried, best 6/14 gates
- edge peaks at 2 bars, exit at 12: 1 tried, best 6/14 gates
- edge peaks at 20 bars, exit at 5: 1 tried, best 6/14 gates
- edge peaks at 3 bars, exit at 1: 1 tried, best 8/14 gates
- edge peaks at 6 bars, exit at 1: 2 tried, best 6/14 gates
- edge peaks at 6 bars, exit at 2: 1 tried, best 4/14 gates
- edge peaks at 60 bars, exit at 5: 4 tried, best 13/14 gates
- fails in some regime: 22 tried, best 11/14 gates
- no better than random: 95 tried, best 10/14 gates
- parameter neighbour: 115 tried, best 13/14 gates
- unstable / decaying: 35 tried, best 8/14 gates
- works only in some sectors: 5 tried, best 12/14 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 881 of 881
- shelf life: positive in every market regime seen: 837 of 881
- shelf life: no decay (2nd half >= half of 1st): 737 of 881
- shelf life: positive in >= 55% of months: 719 of 881
- search: ICIR >= 0.2 (stable month to month): 690 of 881
- shelf life: works on >= 55% of assets (S&P 500: of sectors): 688 of 881
- validation: positive edge: 683 of 881
- decay: edge still >= half its peak at the exit, peak after the first bar: 660 of 881
- robust: parameter neighbours keep >= half the edge (2+ tested): 652 of 881
- validation: makes money after costs: 591 of 881
- validation: beats random entries: 571 of 881
- search: positive edge (IC): 459 of 881
- search: beats random entries (avg R): 363 of 881
- search: at least 100 signals: 130 of 881
