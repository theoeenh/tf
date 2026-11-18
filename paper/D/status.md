# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-18. **Equity $94,784** (-5.22%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 161.64, now 162.91 (-0.82R)
- **BBT** 179.42 shares, entry 30.77, stop 28.98, now 30.20 (-0.25R)
- **BKR** 60.68 shares, entry 46.28, stop 43.65, now 47.30 (+0.16R)
- **BX** 31.23 shares, entry 120.02, stop 108.52, now 115.71 (-0.34R)
- **CAT** 4.63 shares, entry 609.75, stop 524.80, now 558.77 (-0.59R)
- **CNH** 230.10 shares, entry 11.47, stop 9.83, now 11.24 (-0.14R)
- **COHR** 5.59 shares, entry 229.86, stop 162.31, now 212.84 (-0.24R)
- **CRH** 40.42 shares, entry 92.62, stop 88.45, now 92.58 (-0.00R)
- **CTVA** 193.49 shares, entry 9.26, stop 7.31, now 8.36 (-0.45R)
- **CVS** 40.61 shares, entry 84.64, stop 80.87, now 81.35 (-0.34R)
- **ECHO** 26.85 shares, entry 100.64, stop 90.43, now 96.92 (-0.25R)
- **ETN** 7.04 shares, entry 337.80, stop 285.90, now 338.34 (+0.01R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.38, now 29.81 (-0.20R)
- **FICO** 2.79 shares, entry 705.05, stop 616.69, now 677.75 (-0.19R)
- **FUN** 167.11 shares, entry 11.64, stop 9.28, now 11.81 (+0.07R)
- **HL** 155.45 shares, entry 12.49, stop 10.03, now 11.67 (-0.33R)
- **IBKR** 42.00 shares, entry 77.73, stop 72.77, now 76.45 (-0.14R)
- **IOSP** 44.82 shares, entry 79.10, stop 71.79, now 78.86 (-0.03R)
- **KTOS** 55.14 shares, entry 31.74, stop 24.92, now 30.24 (-0.21R)
- **LKFN** 81.64 shares, entry 62.29, stop 58.10, now 60.74 (-0.32R)
- **LKQ** 136.21 shares, entry 20.25, stop 18.37, now 19.10 (-0.39R)
- **LSCC** 19.27 shares, entry 102.00, stop 99.93, now 111.61 (+0.46R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.30, now 171.56 (-0.01R)
- **NVT** 14.39 shares, entry 120.20, stop 95.10, now 109.89 (-0.37R)
- **PEP** 48.93 shares, entry 130.94, stop 136.78, now 141.87 (+1.34R)
- **SANM** 9.86 shares, entry 157.19, stop 119.88, now 157.57 (+0.01R)
- **SHEN** 255.68 shares, entry 9.73, stop 9.08, now 9.74 (+0.00R)
- **SMCI** 53.09 shares, entry 29.63, stop 23.09, now 24.37 (-0.70R)
- **STWD** 332.64 shares, entry 11.76, stop 10.57, now 11.28 (-0.40R)
- **SYY** 58.59 shares, entry 75.11, stop 72.61, now 77.92 (+0.42R)
- **TBBK** 75.36 shares, entry 48.49, stop 45.01, now 45.15 (-0.63R)
- **WCC** 6.81 shares, entry 319.31, stop 275.96, now 313.54 (-0.10R)
- **WY** 220.16 shares, entry 21.03, stop 19.26, now 20.05 (-0.55R)

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
