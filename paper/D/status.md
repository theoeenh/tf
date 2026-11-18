# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-17. **Equity $95,370** (-4.63%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 161.33, now 163.91 (-0.77R)
- **BBT** 179.42 shares, entry 30.77, stop 28.95, now 30.52 (-0.11R)
- **BKR** 60.68 shares, entry 46.28, stop 43.52, now 47.46 (+0.18R)
- **BX** 31.23 shares, entry 120.02, stop 108.09, now 116.48 (-0.28R)
- **CAT** 4.63 shares, entry 609.75, stop 524.41, now 570.79 (-0.45R)
- **CNH** 230.10 shares, entry 11.47, stop 9.80, now 11.30 (-0.10R)
- **COHR** 5.59 shares, entry 229.86, stop 160.43, now 210.86 (-0.27R)
- **CRH** 40.42 shares, entry 92.62, stop 88.45, now 90.62 (-0.21R)
- **CTVA** 193.49 shares, entry 9.26, stop 7.27, now 8.82 (-0.22R)
- **CVS** 40.61 shares, entry 84.64, stop 80.87, now 85.81 (+0.12R)
- **ECHO** 26.85 shares, entry 100.64, stop 90.15, now 99.16 (-0.10R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.33, now 29.82 (-0.20R)
- **FICO** 2.79 shares, entry 705.05, stop 613.75, now 676.52 (-0.20R)
- **FUN** 167.11 shares, entry 11.64, stop 9.27, now 10.96 (-0.29R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.20 (-0.82R)
- **HL** 155.45 shares, entry 12.49, stop 10.03, now 12.50 (+0.00R)
- **IBKR** 42.00 shares, entry 77.73, stop 72.56, now 76.46 (-0.13R)
- **IOSP** 44.82 shares, entry 79.10, stop 71.56, now 78.01 (-0.12R)
- **KTOS** 55.14 shares, entry 31.74, stop 24.80, now 31.06 (-0.10R)
- **LKFN** 81.64 shares, entry 62.29, stop 57.95, now 60.89 (-0.29R)
- **LKQ** 136.21 shares, entry 20.25, stop 18.36, now 18.79 (-0.50R)
- **LSCC** 19.27 shares, entry 102.00, stop 99.28, now 109.80 (+0.38R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.07, now 172.35 (+0.06R)
- **NVT** 14.39 shares, entry 120.20, stop 94.02, now 109.19 (-0.40R)
- **PEP** 48.93 shares, entry 130.94, stop 136.78, now 142.02 (+1.35R)
- **SHEN** 255.68 shares, entry 9.73, stop 9.07, now 9.96 (+0.15R)
- **SMCI** 53.09 shares, entry 29.63, stop 22.81, now 24.14 (-0.73R)
- **STWD** 332.64 shares, entry 11.76, stop 10.57, now 11.32 (-0.37R)
- **SYY** 58.59 shares, entry 75.11, stop 72.57, now 77.99 (+0.43R)
- **TBBK** 75.36 shares, entry 48.49, stop 45.01, now 46.09 (-0.45R)
- **WCC** 6.81 shares, entry 319.31, stop 273.95, now 314.84 (-0.08R)
- **WY** 220.16 shares, entry 21.03, stop 19.26, now 20.09 (-0.52R)

## New signals (bought at the next open)

- **ETN** 7.04 shares around 337.11, stop 282.95
- **SANM** 9.86 shares around 152.67, stop 113.98

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
- 2026-11-12 STC: -0.24R, $-95 (trail)
- 2026-11-16 ENPH: -0.53R, $-213 (trail)
- 2026-11-16 THRM: -0.24R, $-96 (trail)
- 2026-11-17 BANC: -1.02R, $-413 (stop)
