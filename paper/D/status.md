# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-12. **Equity $98,950** (-1.05%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 160.62, now 171.55 (-0.32R)
- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 17.80 (-0.59R)
- **BBT** 179.42 shares, entry 30.77, stop 28.92, now 30.68 (-0.04R)
- **BKR** 60.68 shares, entry 46.28, stop 43.13, now 48.86 (+0.40R)
- **CAT** 4.63 shares, entry 609.75, stop 523.80, now 605.28 (-0.05R)
- **CRH** 40.28 shares, entry 92.91, stop 88.46, now 93.92 (+0.10R)
- **CVS** 40.61 shares, entry 84.64, stop 80.64, now 89.79 (+0.53R)
- **ECHO** 26.85 shares, entry 100.64, stop 89.55, now 98.13 (-0.17R)
- **ENPH** 66.37 shares, entry 28.32, stop 25.02, now 26.78 (-0.25R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.31, now 30.26 (+0.01R)
- **FICO** 2.79 shares, entry 705.05, stop 607.80, now 717.38 (+0.09R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.73 (-0.25R)
- **IBKR** 42.00 shares, entry 77.73, stop 72.17, now 81.33 (+0.38R)
- **LKFN** 81.64 shares, entry 62.29, stop 57.76, now 61.84 (-0.09R)
- **LKQ** 136.21 shares, entry 20.25, stop 18.19, now 19.71 (-0.18R)
- **LSCC** 19.27 shares, entry 102.00, stop 99.28, now 118.85 (+0.81R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.03, now 177.67 (+0.51R)
- **NVT** 14.39 shares, entry 120.20, stop 93.09, now 115.50 (-0.17R)
- **PEP** 48.93 shares, entry 130.94, stop 134.26, now 142.26 (+1.38R)
- **SHEN** 255.68 shares, entry 9.73, stop 8.93, now 10.26 (+0.34R)
- **SMCI** 53.09 shares, entry 29.63, stop 22.73, now 26.99 (-0.35R)
- **SYY** 58.59 shares, entry 75.11, stop 72.22, now 76.24 (+0.17R)
- **TBBK** 75.36 shares, entry 48.49, stop 44.79, now 48.40 (-0.02R)
- **THRM** 74.49 shares, entry 29.84, stop 28.41, now 28.79 (-0.20R)
- **WCC** 6.81 shares, entry 319.31, stop 270.91, now 327.22 (+0.13R)

## New signals (bought at the next open)

None.

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
- 2026-11-12 STC: -0.24R, $-95 (trail)
