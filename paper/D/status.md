# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-19. **Equity $93,166** (-6.83%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BBT** 179.42 shares, entry 30.77, stop 28.99, now 30.10 (-0.30R)
- **BKR** 60.68 shares, entry 46.28, stop 43.68, now 46.67 (+0.06R)
- **BX** 31.23 shares, entry 120.02, stop 108.52, now 115.99 (-0.32R)
- **CAT** 4.63 shares, entry 609.75, stop 524.80, now 537.37 (-0.84R)
- **CNH** 230.10 shares, entry 11.47, stop 9.83, now 11.07 (-0.24R)
- **COHR** 5.59 shares, entry 229.86, stop 162.31, now 214.94 (-0.21R)
- **CRH** 40.42 shares, entry 92.62, stop 88.45, now 90.54 (-0.21R)
- **CTVA** 193.49 shares, entry 9.26, stop 7.37, now 8.12 (-0.56R)
- **ECHO** 26.85 shares, entry 100.64, stop 90.43, now 92.31 (-0.56R)
- **ETN** 7.04 shares, entry 337.80, stop 285.95, now 330.57 (-0.13R)
- **FICO** 2.79 shares, entry 705.05, stop 619.42, now 677.64 (-0.19R)
- **FUN** 167.11 shares, entry 11.64, stop 9.40, now 11.88 (+0.10R)
- **HL** 155.45 shares, entry 12.49, stop 10.03, now 11.15 (-0.53R)
- **IBKR** 42.00 shares, entry 77.73, stop 72.77, now 75.65 (-0.22R)
- **IOSP** 44.82 shares, entry 79.10, stop 71.88, now 77.08 (-0.23R)
- **KTOS** 55.14 shares, entry 31.74, stop 24.97, now 29.65 (-0.30R)
- **LKFN** 81.64 shares, entry 62.29, stop 58.10, now 59.90 (-0.49R)
- **LKQ** 138.25 shares, entry 19.93, stop 18.16, now 18.81 (-0.39R)
- **LSCC** 19.27 shares, entry 102.00, stop 99.93, now 110.92 (+0.43R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.30, now 166.71 (-0.42R)
- **NVT** 14.39 shares, entry 120.20, stop 95.21, now 108.10 (-0.44R)
- **PEP** 48.93 shares, entry 130.94, stop 136.78, now 139.00 (+0.99R)
- **SANM** 9.86 shares, entry 157.19, stop 119.88, now 154.75 (-0.06R)
- **SHEN** 255.69 shares, entry 9.73, stop 9.07, now 9.40 (-0.22R)
- **SMCI** 53.09 shares, entry 29.63, stop 23.16, now 23.84 (-0.77R)
- **STWD** 332.64 shares, entry 11.76, stop 10.57, now 11.25 (-0.43R)
- **SYY** 58.59 shares, entry 75.11, stop 72.80, now 77.15 (+0.30R)
- **WCC** 6.81 shares, entry 319.31, stop 276.19, now 307.17 (-0.21R)
- **WY** 220.16 shares, entry 21.03, stop 19.26, now 19.54 (-0.83R)

## New signals (bought at the next open)

None.

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
- 2026-11-12 STC: -0.24R, $-95 (trail)
- 2026-11-16 ENPH: -0.53R, $-213 (trail)
- 2026-11-16 THRM: -0.24R, $-96 (trail)
- 2026-11-17 BANC: -1.02R, $-413 (stop)
- 2026-11-18 HBAN: -0.98R, $-392 (trail)
- 2026-11-19 BA: -0.90R, $-360 (trail)
- 2026-11-19 CVS: -0.39R, $-155 (trail)
- 2026-11-19 FFIN: -0.42R, $-168 (trail)
- 2026-11-19 TBBK: -0.67R, $-268 (trail)
