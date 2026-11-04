# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-03. **Equity $100,663** (+0.66%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 18.37 (-0.14R)
- **BBT** 177.39 shares, entry 31.10, stop 29.23, now 30.85 (-0.11R)
- **CLF** 156.37 shares, entry 13.87, stop 11.86, now 14.14 (+0.11R)
- **EME** 5.04 shares, entry 702.83, stop 624.40, now 707.43 (+0.06R)
- **ENPH** 66.37 shares, entry 28.32, stop 24.14, now 30.42 (+0.34R)
- **FFIN** 191.17 shares, entry 30.23, stop 29.31, now 31.04 (+0.39R)
- **FIS** 125.93 shares, entry 35.76, stop 36.36, now 38.99 (+1.02R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.86 (-0.11R)
- **NTRS** 34.09 shares, entry 171.66, stop 160.97, now 172.60 (+0.08R)
- **PEP** 48.93 shares, entry 130.94, stop 131.63, now 137.27 (+0.77R)
- **STC** 57.21 shares, entry 43.95, stop 39.14, now 44.76 (+0.12R)
- **THRM** 74.49 shares, entry 29.84, stop 27.52, now 30.30 (+0.09R)

## New signals (bought at the next open)

- **BA** 23.41 shares around 173.31, stop 156.11
- **CAT** 4.68 shares around 623.94, stop 537.99
- **IBKR** 42.46 shares around 77.46, stop 67.98
- **LKQ** 137.71 shares around 19.26, stop 16.34

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
