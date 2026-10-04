# Strategy finder – 2026-10-04

**330 strategies tried so far** (every attempt counts: the deflated Sharpe bar rises with N). Search 2023-01-11 → 2024-12-31, validation 2025-01-01 → 2025-06-30, vault from 2025-07-01 (sealed). 12 gates; only a candidate passing all of them may take its one vault test.

| gates | strategy | IC search | ICIR | IC valid. | avg R s / random | avg R v / random | return v | DSR | months + | regimes + | breadth | first failed gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7/12 | `1f9ad8914f` vwap(k=2.0, trend_ma=280) · stop_atr=1.5, rr=2.0, max_bars=12 | +0.133 | +0.10 | +0.114 | -0.30 / -0.42 | -0.54 / -0.55 | -8.4% | 0.00 | 58% | 1/3 | 59% | search: ICIR >= 0.2 (stable month to month) |
| 6/12 | `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter | +0.038 | +0.54 | -0.050 | -0.02 / -0.04 | -0.07 / -0.06 | -24.0% | 0.00 | 60% | 2/3 | 79% | search: deflated Sharpe >= 0.90 |
| 6/12 | `053e9be7a4` opening_range(n_open=2) · stop_atr=1.5, rr=None, max_bars=1 | +0.037 | +0.48 | -0.095 | -0.03 / -0.04 | -0.07 / -0.05 | -11.7% | 0.00 | 61% | 2/3 | 74% | search: deflated Sharpe >= 0.90 |
| 6/12 | `b6a8af6fea` vwap(k=2.0, trend_ma=200) · stop_atr=1.5, rr=2.0, max_bars=12 · stocks | +0.530 | +0.44 | -0.000 | -0.01 / +0.19 | -0.37 / -0.14 | -0.3% | 0.00 | 60% | 3/3 | 62% | search: at least 100 signals |
| 6/12 | `7df7e5a192` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 | +0.039 | +0.42 | -0.065 | -0.02 / -0.03 | -0.07 / -0.06 | -14.4% | 0.00 | 64% | 2/3 | 79% | search: deflated Sharpe >= 0.90 |
| 6/12 | `e794ebe45f` opening_range(n_open=2) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter | +0.026 | +0.39 | -0.059 | -0.03 / -0.04 | -0.07 / -0.06 | -21.0% | 0.00 | 60% | 2/3 | 68% | search: deflated Sharpe >= 0.90 |
| 6/12 | `aaf134e18d` vwap(k=1.5, trend_ma=200) · stop_atr=1.0, rr=1.5, max_bars=6 | +0.144 | +0.23 | -0.691 | -0.50 / -0.54 | -0.70 / -0.55 | -27.1% | 0.00 | 55% | 2/3 | 64% | search: deflated Sharpe >= 0.90 |
| 6/12 | `d2867573f6` xs_reversal(lookback=6, bottom=4) · stop_atr=1.5, rr=None, max_bars=1 | +0.026 | +0.15 | +0.052 | -0.20 / -0.22 | -0.19 / -0.22 | -21.3% | 0.00 | 52% | 3/3 | 52% | search: ICIR >= 0.2 (stable month to month) |
| 6/12 | `7ffb46fdcc` xs_momentum(lookback=120, top=4) · stop_atr=1.0, rr=1.5, max_bars=6 | +0.018 | +0.05 | +0.017 | -0.14 / -0.19 | -0.08 / -0.26 | -10.7% | 0.00 | 52% | 1/3 | 68% | search: ICIR >= 0.2 (stable month to month) |
| 6/12 | `4ff68d260a` donchian(n=120, trend_ma=100) · stop_atr=1.5, rr=None, max_bars=1 · crypto | +0.004 | +0.01 | +0.042 | -0.50 / -0.60 | -0.52 / -0.50 | -24.6% | 0.00 | 58% | 1/3 | 33% | search: ICIR >= 0.2 (stable month to month) |
| 6/12 | `e543334e63` donchian(n=120, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=1 · crypto | +0.004 | +0.01 | +0.042 | -0.50 / -0.60 | -0.52 / -0.50 | -24.6% | 0.00 | 58% | 1/3 | 33% | search: ICIR >= 0.2 (stable month to month) |
| 6/12 | `9dcb4f23b3` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=1 | -0.001 | -0.00 | +0.087 | -0.15 / -0.17 | -0.08 / -0.13 | -3.6% | 0.00 | 59% | 2/3 | 64% | search: positive edge (IC) |
| 6/12 | `99e472ea29` rsi2(rsi_n=3, threshold=5.0, trend_ma=100) · stop_atr=1.5, rr=None, max_bars=1 | -0.021 | -0.10 | +0.047 | -0.12 / -0.15 | -0.07 / -0.10 | -1.4% | 0.00 | 50% | 2/3 | 59% | search: positive edge (IC) |
| 6/12 | `67dd67dd49` intraday_momentum(k=0.3) · stop_atr=1.5, rr=2.0, max_bars=12 | -0.093 | -0.23 | +0.081 | +0.12 / +0.08 | +0.06 / +0.04 | +4.0% | 0.00 | 43% | 1/3 | 63% | search: positive edge (IC) |
| 6/12 | `3fd752fe43` intraday_momentum(k=0.6) · stop_atr=2.0, rr=2.0 | -0.283 | -0.28 | +0.295 | +0.09 / +0.16 | +0.23 / +0.11 | +14.2% | 0.00 | 50% | 1/3 | 63% | search: positive edge (IC) |
| 6/12 | `ec32709a97` intraday_momentum(k=0.6) · stop_atr=2.5, rr=None, trail_atr=3.0 | -0.283 | -0.28 | +0.295 | +0.19 / +0.23 | +0.25 / +0.04 | +15.0% | 0.00 | 50% | 1/3 | 63% | search: positive edge (IC) |
| 6/12 | `2792b8fd4b` intraday_momentum(k=0.6) · stop_atr=1.5, rr=2.0, max_bars=12 | -0.161 | -0.32 | +0.213 | +0.09 / +0.09 | +0.08 / -0.00 | +5.9% | 0.00 | 50% | 1/3 | 63% | search: positive edge (IC) |
| 6/12 | `208497e0c2` volume_breakout(n=20, m=2.5) · stop_atr=2.0, rr=2.0 | -0.777 | -0.61 | +1.157 | -0.07 / -0.13 | +0.05 / -0.26 | +1.9% | 0.00 | 36% | 1/3 | 45% | search: positive edge (IC) |
| 6/12 | `8e2da38920` volume_breakout(n=10, m=2.5) · stop_atr=2.0, rr=2.0 | -0.754 | -0.61 | +1.063 | -0.05 / -0.16 | +0.06 / -0.23 | +2.3% | 0.00 | 43% | 1/3 | 45% | search: positive edge (IC) |
| 5/12 | `fc7c4c5e67` vwap(k=2.94, trend_ma=200) · stop_atr=1.0, rr=1.5, max_bars=6 | +0.905 | +0.52 | -0.377 | -0.51 / -0.87 | -1.64 / -0.60 | -2.6% | 0.00 | 81% | 3/3 | 50% | search: at least 100 signals |
| 5/12 | `0acb648030` vwap(k=2.1, trend_ma=200) · stop_atr=1.0, rr=1.5, max_bars=6 · etfs | +0.871 | +0.43 | -0.000 | +0.15 / -0.39 | -1.03 / -0.47 | -1.2% | 0.00 | 62% | 1/3 | 60% | search: at least 100 signals |
| 5/12 | `950db9dff5` vwap(k=2.0, trend_ma=140) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter | +0.359 | +0.42 | -0.519 | -0.55 / -0.73 | -0.97 / -0.60 | -20.2% | 0.00 | 57% | 2/3 | 52% | search: deflated Sharpe >= 0.90 |
| 5/12 | `9ac3dce108` vwap(k=2.0, trend_ma=200) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter · stocks+etfs | +0.298 | +0.35 | -0.000 | +0.04 / -0.02 | -1.42 / +0.19 | -2.8% | 0.00 | 47% | 2/3 | 58% | search: at least 100 signals |
| 5/12 | `ed9dd92747` vwap(k=2.1, trend_ma=200) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter | +0.334 | +0.33 | -0.618 | -0.66 / -0.75 | -1.11 / -0.62 | -21.7% | 0.00 | 57% | 1/3 | 43% | search: deflated Sharpe >= 0.90 |
| 5/12 | `d84547266f` vwap(k=2.0, trend_ma=200) · stop_atr=1.0, rr=1.5, max_bars=6 · no trend filter | +0.267 | +0.28 | -0.752 | -0.63 / -0.73 | -1.11 / -0.63 | -25.1% | 0.00 | 57% | 1/3 | 55% | search: deflated Sharpe >= 0.90 |

## Best of each family

| family | tried | best gates | its ICIR (search) | strategy |
|---|---|---|---|---|
| vwap | 56 | 7/12 | +0.10 | `1f9ad8914f` vwap(k=2.0, trend_ma=280) · stop_atr=1.5, rr=2.0, max_bars=12 |
| opening_range | 22 | 6/12 | +0.54 | `a406807eaa` opening_range(n_open=1) · stop_atr=1.5, rr=None, max_bars=1 · no trend filter |
| xs_reversal | 30 | 6/12 | +0.15 | `d2867573f6` xs_reversal(lookback=6, bottom=4) · stop_atr=1.5, rr=None, max_bars=1 |
| xs_momentum | 30 | 6/12 | +0.05 | `7ffb46fdcc` xs_momentum(lookback=120, top=4) · stop_atr=1.0, rr=1.5, max_bars=6 |
| donchian | 52 | 6/12 | +0.01 | `4ff68d260a` donchian(n=120, trend_ma=100) · stop_atr=1.5, rr=None, max_bars=1 · crypto |
| rsi2 | 40 | 6/12 | -0.00 | `9dcb4f23b3` rsi2(rsi_n=3, threshold=5.0, trend_ma=200) · stop_atr=1.5, rr=None, max_bars=1 |
| intraday_momentum | 15 | 6/12 | -0.23 | `67dd67dd49` intraday_momentum(k=0.3) · stop_atr=1.5, rr=2.0, max_bars=12 |
| volume_breakout | 25 | 6/12 | -0.61 | `208497e0c2` volume_breakout(n=20, m=2.5) · stop_atr=2.0, rr=2.0 |
| gap_fade | 15 | 5/12 | -0.17 | `63e0bb1295` gap_fade(g=1.0) · stop_atr=1.5, rr=None, max_bars=1 |
| earnings_drift | 15 | 5/12 | -0.29 | `6493eb9de4` earnings_drift(x=2.0) · stop_atr=2.0, rr=2.0 |
| btc_lead | 10 | 4/12 | -0.52 | `498531f181` btc_lead(k=0.75) · stop_atr=1.5, rr=None, max_bars=1 |
| squeeze | 20 | 2/12 | -0.52 | `626682875e` squeeze(n=20, k=2.0, lookback=60, pct=0.2) · stop_atr=1.5, rr=2.0, max_bars=12 |

## The loop: 80 children tried (improved versions aimed at a parent's failures)

- breadth failed: 24 tried, best 6/12 gates
- fails in some regime: 9 tried, best 6/12 gates
- no better than random: 19 tried, best 5/12 gates
- parameter neighbour: 16 tried, best 5/12 gates
- unstable / decaying: 12 tried, best 7/12 gates

## Why strategies fail (all attempts)

- search: deflated Sharpe >= 0.90: 330 of 330
- shelf life: positive in every market regime seen: 325 of 330
- search: ICIR >= 0.2 (stable month to month): 291 of 330
- shelf life: positive in >= 55% of months: 287 of 330
- shelf life: no decay (2nd half >= half of 1st): 283 of 330
- shelf life: works on >= 55% of assets: 276 of 330
- validation: makes money after costs: 260 of 330
- validation: positive edge: 242 of 330
- search: positive edge (IC): 237 of 330
- validation: beats random entries: 190 of 330
- search: beats random entries (avg R): 180 of 330
- search: at least 100 signals: 44 of 330
