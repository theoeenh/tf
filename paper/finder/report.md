# Strategy finder – 2026-10-04

**69 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30, vault from 2025-07-01 (sealed). 12 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5/12 | `9fe189913e` vwap(k=1.5, trend_ma=200) | stop_atr=1.5, rr=2.0, max_bars=12 | +0.070 | +0.07 | -1.052 | -0.26 / -0.32 | -0.57 / -0.45 | -18.6% | 0.00 | 62% | 1/3 | 59% | search: ICIR >= 0.2 (stable month to month) |
| 5/12 | `c10c2ed2a1` rsi2(rsi_n=3, threshold=5.0, trend_ma=100) | stop_atr=2.0, rr=2.0 | -0.066 | -0.03 | +0.898 | +0.02 / +0.04 | +0.06 / +0.03 | +0.8% | 0.00 | 54% | 2/3 | 50% | search: positive edge (IC) |
| 5/12 | `9515df6876` rsi2(rsi_n=3, threshold=5.0, trend_ma=100) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.066 | -0.03 | +0.898 | +0.03 / +0.11 | +0.31 / -0.02 | +4.3% | 0.00 | 54% | 2/3 | 50% | search: positive edge (IC) |
| 5/12 | `ad240baf26` rsi2(rsi_n=3, threshold=10.0, trend_ma=100) | stop_atr=2.0, rr=2.0 | -0.116 | -0.08 | +0.311 | -0.01 / +0.08 | +0.10 / -0.07 | +5.1% | 0.00 | 54% | 1/3 | 59% | search: positive edge (IC) |
| 5/12 | `d7647d9d4c` rsi2(rsi_n=3, threshold=10.0, trend_ma=100) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.116 | -0.08 | +0.311 | +0.03 / +0.10 | +0.25 / -0.06 | +12.6% | 0.00 | 54% | 1/3 | 59% | search: positive edge (IC) |
| 5/12 | `76030bf7cb` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) | stop_atr=2.0, rr=2.0 | -0.349 | -0.19 | +1.121 | -0.08 / +0.09 | +0.05 / -0.02 | +1.2% | 0.00 | 48% | 1/3 | 41% | search: positive edge (IC) |
| 5/12 | `dad07c4a14` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.349 | -0.19 | +1.121 | -0.02 / +0.14 | +0.40 / -0.00 | +10.2% | 0.00 | 48% | 1/3 | 41% | search: positive edge (IC) |
| 4/12 | `a052cec00c` rsi2(rsi_n=3, threshold=10.0, trend_ma=200) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.129 | -0.10 | +0.410 | +0.04 / +0.09 | +0.18 / -0.07 | +12.1% | 0.00 | 48% | 1/3 | 50% | search: positive edge (IC) |
| 4/12 | `100e061510` rsi2(rsi_n=2, threshold=5.0, trend_ma=100) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.167 | -0.15 | +0.081 | +0.01 / +0.08 | +0.16 / -0.09 | +11.2% | 0.00 | 45% | 1/3 | 55% | search: positive edge (IC) |
| 4/12 | `8769385cbe` rsi2(rsi_n=2, threshold=5.0, trend_ma=200) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.170 | -0.16 | +0.119 | +0.02 / +0.07 | +0.13 / -0.07 | +12.2% | 0.00 | 41% | 1/3 | 41% | search: positive edge (IC) |
| 4/12 | `0486d5b4c8` rsi2(rsi_n=2, threshold=10.0, trend_ma=100) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.257 | -0.24 | -0.198 | +0.04 / +0.08 | +0.08 / -0.07 | +6.9% | 0.00 | 41% | 1/3 | 59% | search: positive edge (IC) |
| 3/12 | `f2a3fcc9bc` vwap(k=2.0, trend_ma=200) | stop_atr=1.5, rr=2.0, max_bars=12 | +0.247 | +0.18 | -0.246 | -0.21 / -0.42 | -0.65 / -0.54 | -9.1% | 0.00 | 54% | 1/3 | 55% | search: ICIR >= 0.2 (stable month to month) |
| 3/12 | `56ba383257` vwap(k=2.5, trend_ma=200) | stop_atr=1.5, rr=2.0, max_bars=12 | +0.461 | +0.17 | -0.056 | -0.32 / -0.41 | -0.90 / -0.45 | -6.0% | 0.00 | 48% | 2/3 | 8% | search: ICIR >= 0.2 (stable month to month) |
| 3/12 | `156198bd88` vwap(k=2.5, trend_ma=200) | stop_atr=2.0, rr=2.0 | +0.122 | +0.03 | +0.767 | -0.42 / -0.25 | -0.77 / -0.33 | -4.8% | 0.00 | 48% | 1/3 | 17% | search: ICIR >= 0.2 (stable month to month) |
| 3/12 | `4e82a08e6f` vwap(k=2.5, trend_ma=200) | stop_atr=2.5, rr=None, trail_atr=3.0 | +0.122 | +0.03 | +0.767 | -0.29 / -0.20 | -0.45 / -0.09 | -2.5% | 0.00 | 48% | 1/3 | 17% | search: ICIR >= 0.2 (stable month to month) |
| 3/12 | `7453c1be22` vwap(k=2.0, trend_ma=200) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.052 | -0.02 | -0.027 | -0.11 / -0.18 | -0.30 / -0.35 | -3.7% | 0.00 | 50% | 1/3 | 55% | search: positive edge (IC) |
| 3/12 | `d3de75154f` rsi2(rsi_n=3, threshold=5.0, trend_ma=100) | stop_atr=1.5, rr=2.0, max_bars=12 | -0.100 | -0.08 | +0.257 | -0.13 / -0.02 | -0.07 / +0.05 | -1.1% | 0.00 | 57% | 1/3 | 50% | search: positive edge (IC) |
| 3/12 | `ddf0895007` rsi2(rsi_n=3, threshold=10.0, trend_ma=200) | stop_atr=2.0, rr=2.0 | -0.129 | -0.10 | +0.410 | -0.02 / +0.07 | +0.00 / -0.05 | -1.6% | 0.00 | 48% | 1/3 | 50% | search: positive edge (IC) |
| 3/12 | `4d15a621d6` rsi2(rsi_n=2, threshold=5.0, trend_ma=100) | stop_atr=2.0, rr=2.0 | -0.167 | -0.15 | +0.081 | +0.00 / +0.05 | +0.02 / -0.08 | -0.7% | 0.00 | 45% | 1/3 | 55% | search: positive edge (IC) |
| 3/12 | `1065447e41` rsi2(rsi_n=2, threshold=5.0, trend_ma=200) | stop_atr=2.0, rr=2.0 | -0.170 | -0.16 | +0.119 | -0.02 / +0.04 | -0.05 / -0.06 | -5.3% | 0.00 | 41% | 1/3 | 41% | search: positive edge (IC) |
| 3/12 | `d4217e2e49` rsi2(rsi_n=2, threshold=10.0, trend_ma=100) | stop_atr=2.0, rr=2.0 | -0.257 | -0.24 | -0.198 | -0.01 / +0.03 | +0.01 / -0.03 | -2.2% | 0.00 | 41% | 1/3 | 59% | search: positive edge (IC) |
| 3/12 | `0eab9861e5` rsi2(rsi_n=2, threshold=10.0, trend_ma=200) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.297 | -0.28 | -0.083 | +0.05 / +0.08 | +0.13 / -0.06 | +13.8% | 0.00 | 41% | 1/3 | 55% | search: positive edge (IC) |
| 3/12 | `a58924136b` opening_range(n_open=1) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.308 | -0.31 | -0.297 | +0.20 / +0.23 | +0.12 / +0.04 | +11.8% | 0.12 | 43% | 1/3 | 26% | search: positive edge (IC) |
| 3/12 | `daf9e8cfae` opening_range(n_open=2) | stop_atr=2.0, rr=2.0 | -0.384 | -0.39 | -0.462 | +0.14 / +0.14 | +0.01 / +0.10 | +1.8% | 0.08 | 43% | 1/3 | 21% | search: positive edge (IC) |
| 3/12 | `08c304451f` opening_range(n_open=2) | stop_atr=2.5, rr=None, trail_atr=3.0 | -0.384 | -0.39 | -0.462 | +0.21 / +0.22 | +0.11 / +0.05 | +10.3% | 0.15 | 43% | 1/3 | 21% | search: positive edge (IC) |

## Why strategies fail (all attempts)

- search: ICIR >= 0.2 (stable month to month): 69 of 69
- search: deflated Sharpe >= 0.90: 69 of 69
- shelf life: positive in every market regime seen: 69 of 69
- shelf life: positive in >= 55% of months: 67 of 69
- search: positive edge (IC): 64 of 69
- shelf life: works on >= 55% of assets: 64 of 69
- search: beats random entries (avg R): 62 of 69
- shelf life: no decay (2nd half >= half of 1st): 61 of 69
- validation: positive edge: 53 of 69
- validation: makes money after costs: 48 of 69
- validation: beats random entries: 31 of 69
