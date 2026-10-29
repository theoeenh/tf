# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-10-29. **Equity $100,231** (+0.23%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BBT** 177.39 shares, entry 31.10, stop 28.89, now 30.66 (-0.19R)
- **CLF** 156.37 shares, entry 13.87, stop 11.72, now 14.26 (+0.15R)
- **EME** 5.04 shares, entry 702.83, stop 623.52, now 689.32 (-0.17R)
- **FFIN** 191.17 shares, entry 30.23, stop 28.72, now 30.75 (+0.25R)
- **FIS** 125.93 shares, entry 35.76, stop 34.89, now 37.28 (+0.48R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.03, now 15.97 (+0.01R)
- **PEP** 48.93 shares, entry 130.94, stop 130.57, now 133.79 (+0.35R)
- **STC** 57.21 shares, entry 43.95, stop 38.76, now 45.48 (+0.22R)
- **THRM** 74.49 shares, entry 29.84, stop 27.47, now 32.20 (+0.44R)

## New signals (bought at the next open)

None.

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
