# Strategy finder – 2026-10-04

**553 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Hourly (live universe): search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30. S&P 500 daily: search 2017-01-01 → 2022-12-31, validation 2023-01-01 → 2025-06-30. Both: vault from 2025-07-01 (sealed). 12 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 9/12 | `22f2cf8089` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | +0.246 | +0.25 | +0.027 | -0.00 / -0.08 | +0.22 / +0.06 | +3.5% | 0.00 | 38% | 2/3 | 73% | search: deflated Sharpe >= 0.90 |
| 8/12 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 | +0.400 | +0.30 | -0.166 | -0.16 / -0.37 | -0.56 / -0.57 | -5.7% | 0.00 | 65% | 3/3 | 57% | search: deflated Sharpe >= 0.90 |
| 8/12 | `3aa989920a` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · S&P 400 (mid), daily | +0.196 | +0.21 | +0.115 | +0.05 / -0.06 | +0.18 / +0.15 | +1.6% | 0.00 | 47% | 2/3 | 70% | search: at least 100 signals |
| 8/12 | `69cd5d2779` insider_cluster(buyers=3, days=30) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | +0.107 | +0.12 | +0.219 | +0.01 / -0.03 | +0.40 / -0.03 | +5.3% | 0.00 | 41% | 2/3 | 64% | search: ICIR >= 0.2 (stable month to month) |
| 8/12 | `cbc6e766e6` reversal_5d(bottom=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily | -0.028 | -0.05 | +0.097 | +0.02 / +0.01 | +0.12 / +0.06 | +46.2% | 0.00 | 55% | 2/3 | 73% | search: positive edge (IC) |
| 7/12 | `23a0f56304` vwap(k=2.8, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 | +0.884 | +0.56 | +0.000 | -0.50 / -0.68 | -0.58 / -0.70 | -0.7% | 0.00 | 71% | 2/2 | 33% | search: at least 100 signals |
| 7/12 | `607b5bc2db` vwap(k=2.0, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 | +0.326 | +0.36 | -0.809 | -0.50 / -0.63 | -1.03 / -0.66 | -12.0% | 0.00 | 61% | 3/3 | 57% | search: deflated Sharpe >= 0.90 |
| 7/12 | `f1f39c6aa7` insider_cluster(buyers=2, days=30) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | +0.239 | +0.32 | -0.055 | +0.07 / -0.03 | +0.03 / +0.02 | +1.1% | 0.00 | 51% | 2/3 | 64% | search: deflated Sharpe >= 0.90 |
| 7/12 | `d32092b324` vwap(k=2.1, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 · no trend filter | +0.323 | +0.23 | -0.269 | -0.28 / -0.46 | -0.58 / -0.59 | -9.3% | 0.00 | 60% | 1/3 | 58% | search: deflated Sharpe >= 0.90 |
| 7/12 | `917deb29a5` insider_big_buy(min_value=500000, officer=True) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | +0.140 | +0.15 | +0.005 | +0.14 / -0.00 | +0.21 / -0.05 | +2.3% | 0.00 | 44% | 2/3 | 64% | search: ICIR >= 0.2 (stable month to month) |
| 7/12 | `ddc0764edf` insider_cluster(buyers=3, days=30) · stop_atr=2.0, rr=3.0, max_bars=20 · S&P 600 (small), daily | +0.203 | +0.12 | -0.019 | +0.02 / +0.00 | +0.40 / -0.17 | +5.2% | 0.00 | 42% | 1/3 | 73% | search: ICIR >= 0.2 (stable month to month) |
| 7/12 | `1f9ad8914f` vwap(k=2.0, trend_ma=280) · stop_atr=1.5, rr=2.0, max_bars=12 | +0.133 | +0.10 | +0.114 | -0.30 / -0.42 | -0.54 / -0.55 | -8.4% | 0.00 | 58% | 1/3 | 59% | search: ICIR >= 0.2 (stable month to month) |
| 7/12 | `008d44dc92` insider_big_buy(min_value=500000, officer=True) · stop_atr=3.0, rr=None, max_bars=20 · S&P 600 (small), daily | +0.041 | +0.02 | +0.297 | +0.26 / +0.12 | +0.30 / +0.04 | +3.3% | 0.00 | 38% | 2/3 | 36% | search: ICIR >= 0.2 (stable month to month) |
| 7/12 | `298f448fe4` insider_big_buy(min_value=500000, officer=True) · stop_atr=2.0, rr=3.0, max_bars=20 · S&P 600 (small), daily | +0.041 | +0.02 | +0.297 | +0.29 / +0.14 | +0.27 / +0.23 | +2.9% | 0.00 | 38% | 2/3 | 36% | search: ICIR >= 0.2 (stable month to month) |
| 7/12 | `64a0d58575` insider_big_buy(min_value=500000, officer=False) · stop_atr=2.5, rr=None, max_bars=5 · S&P 400 (mid), daily | +0.016 | +0.02 | -0.011 | +0.05 / +0.01 | +0.07 / +0.00 | +1.4% | 0.00 | 46% | 2/3 | 64% | search: ICIR >= 0.2 (stable month to month) |
| 7/12 | `1525a174b3` insider_big_buy(min_value=500000, officer=False) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily | +0.012 | +0.01 | +0.061 | +0.05 / -0.01 | +0.12 / -0.03 | +4.5% | 0.00 | 52% | 2/3 | 82% | search: ICIR >= 0.2 (stable month to month) |
| 7/12 | `d433c7b90c` reversal_5d(bottom=0.02) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily | -0.037 | -0.06 | +0.104 | +0.02 / -0.02 | +0.14 / +0.04 | +16.3% | 0.00 | 53% | 2/3 | 64% | search: positive edge (IC) |
| 6/12 | `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter | +0.038 | +0.54 | -0.050 | -0.02 / -0.04 | -0.07 / -0.06 | -24.0% | 0.00 | 60% | 2/3 | 79% | search: deflated Sharpe >= 0.90 |
| 6/12 | `053e9be7a4` opening_range(n_open=2) · stop_atr=1.5, rr=None, max_bars=1 | +0.037 | +0.48 | -0.095 | -0.03 / -0.04 | -0.07 / -0.05 | -11.7% | 0.00 | 61% | 2/3 | 74% | search: deflated Sharpe >= 0.90 |
| 6/12 | `b6a8af6fea` vwap(k=2.0, trend_ma=200) · stop_atr=1.5, rr=2.0, max_bars=12 · stocks | +0.530 | +0.44 | -0.000 | -0.01 / +0.19 | -0.37 / -0.14 | -0.3% | 0.00 | 60% | 3/3 | 62% | search: at least 100 signals |
| 6/12 | `7df7e5a192` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 | +0.039 | +0.42 | -0.065 | -0.02 / -0.03 | -0.07 / -0.06 | -14.4% | 0.00 | 64% | 2/3 | 79% | search: deflated Sharpe >= 0.90 |
| 6/12 | `e794ebe45f` opening_range(n_open=2) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter | +0.026 | +0.39 | -0.059 | -0.03 / -0.04 | -0.07 / -0.06 | -21.0% | 0.00 | 60% | 2/3 | 68% | search: deflated Sharpe >= 0.90 |
| 6/12 | `374a87c2f6` vwap(k=2.1, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 | +0.310 | +0.30 | -0.656 | -0.54 / -0.67 | -1.01 / -0.69 | -11.5% | 0.00 | 57% | 3/3 | 47% | search: deflated Sharpe >= 0.90 |
| 6/12 | `3f09832bb8` vwap(k=2.0, trend_ma=98) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter · crypto | +0.337 | +0.30 | -0.328 | -0.82 / -0.93 | -1.04 / -0.72 | -16.5% | 0.00 | 63% | 3/3 | 33% | search: deflated Sharpe >= 0.90 |
| 6/12 | `71d15de401` vwap(k=2.0, trend_ma=98) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter | +0.293 | +0.30 | -0.277 | -0.58 / -0.71 | -1.10 / -0.66 | -18.9% | 0.00 | 60% | 3/3 | 40% | search: deflated Sharpe >= 0.90 |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| insider_cluster | 48 | 9/12 | +0.25 | `22f2cf8089` insider_cluster(buyers=3, days=90) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily |
| vwap | 111 | 8/12 | +0.30 | `59e9efbbe7` vwap(k=2.0, trend_ma=140) · stop_atr=1.5, rr=2.0, max_bars=12 |
| reversal_5d | 24 | 8/12 | -0.05 | `cbc6e766e6` reversal_5d(bottom=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| insider_big_buy | 48 | 7/12 | +0.15 | `917deb29a5` insider_big_buy(min_value=500000, officer=True) · stop_atr=2.5, rr=None, max_bars=5 · S&P 600 (small), daily |
| opening_range | 22 | 6/12 | +0.54 | `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter |
| xs_reversal | 30 | 6/12 | +0.15 | `d2867573f6` xs_reversal(lookback=6, bottom=4) · stop_atr=1.5, rr=None, max_bars=1 |
| xs_momentum | 30 | 6/12 | +0.05 | `7ffb46fdcc` xs_momentum(lookback=120, top=4) · stop_atr=1.0, rr=1.5, max_bars=6 |
| momentum_12_1 | 24 | 6/12 | +0.04 | `9171f4b689` momentum_12_1(top=0.05) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| donchian | 52 | 6/12 | +0.01 | `4ff68d260a` donchian(n=120, trend_ma=100) · stop_atr=1.5, rr=None, max_bars=1 · crypto |
| rsi2 | 40 | 6/12 | -0.00 | `9dcb4f23b3` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=1 |
| intraday_momentum | 15 | 6/12 | -0.23 | `67dd67dd49` intraday_momentum(k=0.3) · stop_atr=1.5, rr=2.0, max_bars=12 |
| volume_breakout | 25 | 6/12 | -0.61 | `208497e0c2` volume_breakout(n=20, m=2.5) · stop_atr=2.0, rr=2.0 |
| gap_fade | 15 | 5/12 | -0.17 | `63e0bb1295` gap_fade(g=1.0) · stop_atr=1.5, rr=None, max_bars=1 |
| earnings_drift | 15 | 5/12 | -0.29 | `6493eb9de4` earnings_drift(x=2.0) · stop_atr=2.0, rr=2.0 |
| high_52w | 24 | 4/12 | -0.29 | `59732b89d7` high_52w(within=0.03) · stop_atr=2.5, rr=None, max_bars=5 · S&P 500, daily |
| btc_lead | 10 | 4/12 | -0.52 | `498531f181` btc_lead(k=0.75) · stop_atr=1.5, rr=None, max_bars=1 |
| squeeze | 20 | 2/12 | -0.52 | `626682875e` squeeze(n=20, k=2.0, lookback=60, pct=0.2) · stop_atr=1.5, rr=2.0, max_bars=12 |

## The loop: 135 children tried (improved versions aimed at a parent's failures)

- breadth failed: 36 tried, best 6/12 gates
- fails in some regime: 11 tried, best 7/12 gates
- no better than random: 39 tried, best 8/12 gates
- parameter neighbour: 32 tried, best 7/12 gates
- unstable / decaying: 17 tried, best 7/12 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 553 of 553
- shelf life: positive in every market regime seen: 540 of 553
- shelf life: positive in >= 55% of months: 481 of 553
- search: ICIR >= 0.2 (stable month to month): 474 of 553
- shelf life: no decay (2nd half >= half of 1st): 466 of 553
- shelf life: works on >= 55% of assets (S&P 500: of sectors): 457 of 553
- validation: positive edge: 429 of 553
- search: positive edge (IC): 366 of 553
- validation: makes money after costs: 349 of 553
- validation: beats random entries: 327 of 553
- search: beats random entries (avg R): 261 of 553
- search: at least 100 signals: 82 of 553
