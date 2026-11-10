# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-10. **Equity $99,753** (-0.25%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 159.89, now 173.38 (-0.22R)
- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 18.00 (-0.43R)
- **BBT** 179.42 shares, entry 30.77, stop 28.92, now 31.01 (+0.11R)
- **BKR** 60.68 shares, entry 46.28, stop 41.88, now 47.77 (+0.23R)
- **CAT** 4.63 shares, entry 609.75, stop 523.80, now 584.57 (-0.29R)
- **CRH** 40.28 shares, entry 92.91, stop 88.00, now 96.86 (+0.41R)
- **CVS** 40.61 shares, entry 84.64, stop 79.41, now 89.01 (+0.45R)
- **ECHO** 26.85 shares, entry 100.64, stop 89.18, now 104.16 (+0.24R)
- **ENPH** 66.37 shares, entry 28.32, stop 24.89, now 27.64 (-0.11R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.31, now 30.59 (+0.17R)
- **FICO** 2.79 shares, entry 705.05, stop 598.08, now 730.66 (+0.18R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.84 (-0.13R)
- **IBKR** 42.00 shares, entry 77.73, stop 68.48, now 77.59 (-0.02R)
- **LKFN** 81.64 shares, entry 62.29, stop 57.48, now 62.09 (-0.04R)
- **LKQ** 136.21 shares, entry 20.25, stop 18.06, now 20.19 (-0.02R)
- **LSCC** 19.27 shares, entry 102.00, stop 91.19, now 111.25 (+0.45R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.03, now 177.89 (+0.53R)
- **PEP** 48.93 shares, entry 130.94, stop 133.80, now 143.61 (+1.55R)
- **SHEN** 255.68 shares, entry 9.73, stop 8.88, now 10.40 (+0.43R)
- **STC** 57.21 shares, entry 43.95, stop 42.32, now 44.81 (+0.12R)
- **SYY** 58.59 shares, entry 75.11, stop 71.85, now 77.63 (+0.38R)
- **TBBK** 75.36 shares, entry 48.49, stop 44.46, now 48.67 (+0.03R)
- **THRM** 74.49 shares, entry 29.84, stop 28.02, now 29.78 (-0.01R)
- **WCC** 6.81 shares, entry 319.31, stop 262.01, now 316.70 (-0.04R)

## New signals (bought at the next open)

None.

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
