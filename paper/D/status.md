# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-10-21. **Equity $100,158** (+0.16%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **EME** 5.04 shares, entry 702.83, stop 623.52, now 699.17 (-0.05R)
- **FIS** 125.93 shares, entry 35.76, stop 33.41, now 36.42 (+0.21R)
- **PEP** 48.93 shares, entry 130.94, stop 126.69, now 134.70 (+0.46R)
- **PRIM** 32.34 shares, entry 75.47, stop 63.76, now 72.67 (-0.23R)

## New signals (bought at the next open)

None.
