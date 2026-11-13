# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-13. **Equity $99,041** (-0.96%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 161.33, now 171.50 (-0.32R)
- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 17.83 (-0.56R)
- **BBT** 179.42 shares, entry 30.77, stop 28.92, now 30.76 (-0.00R)
- **BKR** 60.68 shares, entry 46.28, stop 43.37, now 49.44 (+0.49R)
- **BX** 31.23 shares, entry 120.02, stop 107.89, now 120.19 (+0.01R)
- **CAT** 4.63 shares, entry 609.75, stop 523.80, now 600.20 (-0.11R)
- **COHR** 5.59 shares, entry 229.86, stop 159.08, now 218.15 (-0.17R)
- **CRH** 40.42 shares, entry 92.62, stop 88.45, now 93.16 (+0.06R)
- **CVS** 40.61 shares, entry 84.64, stop 80.80, now 89.35 (+0.49R)
- **ECHO** 26.85 shares, entry 100.64, stop 89.55, now 100.00 (-0.04R)
- **ENPH** 66.37 shares, entry 28.32, stop 25.19, now 26.07 (-0.37R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.31, now 30.28 (+0.02R)
- **FICO** 2.79 shares, entry 705.05, stop 610.96, now 720.19 (+0.11R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.82 (-0.15R)
- **IBKR** 42.00 shares, entry 77.73, stop 72.56, now 81.79 (+0.43R)
- **IOSP** 44.28 shares, entry 80.05, stop 71.80, now 80.39 (+0.04R)
- **LKFN** 81.64 shares, entry 62.29, stop 57.93, now 62.31 (+0.00R)
- **LKQ** 136.21 shares, entry 20.25, stop 18.25, now 19.47 (-0.27R)
- **LSCC** 19.27 shares, entry 102.00, stop 99.28, now 112.35 (+0.50R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.05, now 178.24 (+0.56R)
- **NVT** 14.39 shares, entry 120.20, stop 93.18, now 114.69 (-0.20R)
- **PEP** 48.93 shares, entry 130.94, stop 135.70, now 145.44 (+1.77R)
- **SHEN** 255.68 shares, entry 9.73, stop 8.99, now 10.17 (+0.28R)
- **SMCI** 53.09 shares, entry 29.63, stop 22.73, now 26.86 (-0.37R)
- **SYY** 58.59 shares, entry 75.11, stop 72.47, now 77.10 (+0.30R)
- **TBBK** 75.36 shares, entry 48.49, stop 44.88, now 48.62 (+0.02R)
- **THRM** 74.49 shares, entry 29.84, stop 28.60, now 29.08 (-0.14R)
- **WCC** 6.81 shares, entry 319.31, stop 271.49, now 321.79 (+0.04R)

## New signals (bought at the next open)

None.

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
- 2026-11-12 STC: -0.24R, $-95 (trail)
