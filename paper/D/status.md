# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-10-27. **Equity $99,597** (-0.40%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BBT** 177.39 shares, entry 31.10, stop 28.89, now 30.71 (-0.17R)
- **CLF** 156.37 shares, entry 13.87, stop 11.32, now 13.90 (+0.01R)
- **EME** 5.04 shares, entry 702.83, stop 623.52, now 666.36 (-0.46R)
- **FIS** 125.93 shares, entry 35.76, stop 34.89, now 35.61 (-0.05R)
- **PEP** 48.93 shares, entry 130.94, stop 130.47, now 133.50 (+0.31R)
- **STC** 57.21 shares, entry 43.95, stop 37.19, now 43.48 (-0.07R)
- **THRM** 74.49 shares, entry 29.84, stop 26.13, now 31.82 (+0.37R)

## New signals (bought at the next open)

None.

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
