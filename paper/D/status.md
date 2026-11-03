# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-02. **Equity $101,149** (+1.15%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BBT** 177.39 shares, entry 31.10, stop 29.23, now 31.57 (+0.21R)
- **CLF** 156.37 shares, entry 13.87, stop 11.80, now 14.27 (+0.16R)
- **EME** 5.04 shares, entry 702.83, stop 623.52, now 682.76 (-0.25R)
- **FFIN** 191.17 shares, entry 30.23, stop 29.28, now 31.44 (+0.58R)
- **FIS** 125.93 shares, entry 35.76, stop 36.36, now 40.15 (+1.38R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.05, now 16.01 (+0.06R)
- **PEP** 48.93 shares, entry 130.94, stop 131.63, now 140.42 (+1.16R)
- **STC** 57.21 shares, entry 43.95, stop 39.09, now 45.73 (+0.26R)
- **THRM** 74.49 shares, entry 29.84, stop 27.47, now 31.38 (+0.29R)

## New signals (bought at the next open)

- **BANC** 316.56 shares around 18.50, stop 17.22
- **ENPH** 66.38 shares around 27.93, stop 21.83
- **NTRS** 34.11 shares around 170.66, stop 158.80

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
