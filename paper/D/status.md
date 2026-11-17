# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-16. **Equity $97,472** (-2.53%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 161.33, now 165.22 (-0.69R)
- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 17.66 (-0.69R)
- **BBT** 179.42 shares, entry 30.77, stop 28.92, now 30.81 (+0.02R)
- **BKR** 60.68 shares, entry 46.28, stop 43.44, now 47.94 (+0.26R)
- **BX** 31.23 shares, entry 120.02, stop 107.89, now 117.01 (-0.24R)
- **CAT** 4.63 shares, entry 609.75, stop 523.80, now 570.49 (-0.46R)
- **COHR** 5.59 shares, entry 229.86, stop 159.08, now 203.43 (-0.37R)
- **CRH** 40.42 shares, entry 92.62, stop 88.45, now 92.37 (-0.03R)
- **CVS** 40.61 shares, entry 84.64, stop 80.87, now 88.59 (+0.41R)
- **ECHO** 26.85 shares, entry 100.64, stop 89.95, now 99.47 (-0.08R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.31, now 30.18 (-0.03R)
- **FICO** 2.79 shares, entry 705.05, stop 613.75, now 717.28 (+0.09R)
- **FUN** 167.11 shares, entry 11.64, stop 9.27, now 11.61 (-0.01R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.63 (-0.35R)
- **IBKR** 42.00 shares, entry 77.73, stop 72.56, now 78.43 (+0.07R)
- **IOSP** 44.82 shares, entry 79.10, stop 71.22, now 78.23 (-0.10R)
- **LKFN** 81.64 shares, entry 62.29, stop 57.93, now 62.11 (-0.04R)
- **LKQ** 136.21 shares, entry 20.25, stop 18.33, now 19.27 (-0.34R)
- **LSCC** 19.27 shares, entry 102.00, stop 99.28, now 108.17 (+0.30R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.07, now 175.45 (+0.32R)
- **NVT** 14.39 shares, entry 120.20, stop 93.73, now 109.43 (-0.39R)
- **PEP** 48.93 shares, entry 130.94, stop 136.78, now 146.43 (+1.89R)
- **SHEN** 255.68 shares, entry 9.73, stop 9.03, now 10.11 (+0.24R)
- **SMCI** 53.09 shares, entry 29.63, stop 22.73, now 25.02 (-0.61R)
- **STWD** 332.64 shares, entry 11.76, stop 10.57, now 11.75 (-0.01R)
- **SYY** 58.59 shares, entry 75.11, stop 72.47, now 78.24 (+0.47R)
- **TBBK** 75.36 shares, entry 48.49, stop 45.01, now 48.13 (-0.07R)
- **WCC** 6.81 shares, entry 319.31, stop 272.80, now 311.60 (-0.13R)
- **WY** 220.16 shares, entry 21.03, stop 19.26, now 20.68 (-0.20R)

## New signals (bought at the next open)

- **CNH** 230.10 shares around 11.46, stop 9.77
- **CTVA** 193.49 shares around 9.04, stop 7.03
- **HL** 155.52 shares around 12.22, stop 9.71
- **KTOS** 55.19 shares around 31.66, stop 24.60

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
- 2026-11-12 STC: -0.24R, $-95 (trail)
- 2026-11-16 ENPH: -0.53R, $-213 (trail)
- 2026-11-16 THRM: -0.24R, $-96 (trail)
