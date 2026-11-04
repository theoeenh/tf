# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-04. **Equity $100,079** (+0.08%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 159.89, now 177.00 (-0.01R)
- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 18.56 (+0.01R)
- **BBT** 177.39 shares, entry 31.10, stop 29.23, now 31.34 (+0.11R)
- **CAT** 4.63 shares, entry 609.75, stop 523.80, now 591.30 (-0.21R)
- **CLF** 156.37 shares, entry 13.87, stop 11.86, now 12.84 (-0.40R)
- **EME** 5.04 shares, entry 702.83, stop 624.40, now 639.25 (-0.80R)
- **ENPH** 66.37 shares, entry 28.32, stop 24.89, now 31.55 (+0.53R)
- **FFIN** 191.17 shares, entry 30.23, stop 29.31, now 31.42 (+0.57R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 16.06 (+0.11R)
- **IBKR** 42.00 shares, entry 77.73, stop 68.48, now 77.88 (+0.02R)
- **LKQ** 136.21 shares, entry 20.25, stop 17.82, now 20.94 (+0.24R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.03, now 178.02 (+0.54R)
- **PEP** 48.93 shares, entry 130.94, stop 132.74, now 142.42 (+1.40R)
- **STC** 57.21 shares, entry 43.95, stop 40.38, now 47.10 (+0.45R)
- **THRM** 74.49 shares, entry 29.84, stop 27.67, now 31.11 (+0.24R)

## New signals (bought at the next open)

None.

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
