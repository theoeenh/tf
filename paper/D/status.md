# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-24. **Equity $92,951** (-7.05%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BBT** 179.42 shares, entry 30.77, stop 28.99, now 30.27 (-0.22R)
- **BKR** 60.68 shares, entry 46.28, stop 43.75, now 45.89 (-0.06R)
- **BX** 31.23 shares, entry 120.02, stop 108.52, now 119.35 (-0.05R)
- **CNH** 230.10 shares, entry 11.47, stop 9.84, now 11.00 (-0.28R)
- **COHR** 5.59 shares, entry 229.86, stop 162.31, now 196.24 (-0.48R)
- **CTVA** 193.49 shares, entry 9.26, stop 7.58, now 8.16 (-0.54R)
- **ELV** 8.00 shares, entry 386.22, stop 344.75, now 391.17 (+0.11R)
- **ETN** 7.04 shares, entry 337.80, stop 285.95, now 319.27 (-0.34R)
- **FICO** 2.79 shares, entry 705.05, stop 619.42, now 703.33 (-0.01R)
- **FUN** 167.11 shares, entry 11.64, stop 9.42, now 11.39 (-0.10R)
- **HL** 155.83 shares, entry 12.49, stop 10.04, now 10.90 (-0.64R)
- **IOSP** 44.82 shares, entry 79.10, stop 72.15, now 77.94 (-0.13R)
- **KTOS** 55.14 shares, entry 31.74, stop 24.97, now 28.21 (-0.50R)
- **LKFN** 81.64 shares, entry 62.29, stop 58.17, now 60.96 (-0.27R)
- **LKQ** 138.25 shares, entry 19.93, stop 18.24, now 19.08 (-0.30R)
- **NVT** 14.39 shares, entry 120.20, stop 95.32, now 104.58 (-0.56R)
- **PEP** 48.93 shares, entry 130.94, stop 136.78, now 142.68 (+1.44R)
- **PLD** 51.06 shares, entry 123.71, stop 119.34, now 127.32 (+0.49R)
- **SANM** 9.86 shares, entry 157.19, stop 119.88, now 138.28 (-0.49R)
- **STWD** 332.64 shares, entry 11.76, stop 10.57, now 11.38 (-0.32R)
- **SYY** 58.59 shares, entry 75.11, stop 74.49, now 80.22 (+0.76R)
- **TJX** 28.65 shares, entry 140.85, stop 131.07, now 143.86 (+0.24R)
- **WCC** 6.81 shares, entry 319.31, stop 276.19, now 289.47 (-0.51R)
- **WMB** 52.88 shares, entry 65.86, stop 59.16, now 66.00 (+0.02R)
- **WY** 220.16 shares, entry 21.03, stop 19.31, now 20.21 (-0.46R)

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
- 2026-11-20 SMCI: -0.87R, $-348 (trail)
- 2026-11-20 CAT: -0.99R, $-395 (trail)
- 2026-11-20 CRH: -0.43R, $-170 (trail)
- 2026-11-20 ECHO: -0.69R, $-275 (trail)
- 2026-11-20 IBKR: -0.53R, $-210 (trail)
- 2026-11-20 LSCC: -0.10R, $-42 (trail)
- 2026-11-20 NTRS: -0.46R, $-186 (trail)
- 2026-11-23 SHEN: -0.44R, $-173 (trail)
