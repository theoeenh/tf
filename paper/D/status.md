# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-06. **Equity $98,350** (-1.65%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 159.89, now 173.40 (-0.21R)
- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 17.98 (-0.44R)
- **BBT** 179.42 shares, entry 30.77, stop 28.92, now 30.60 (-0.07R)
- **BKR** 60.38 shares, entry 46.50, stop 41.34, now 47.87 (+0.21R)
- **CAT** 4.63 shares, entry 609.75, stop 523.80, now 558.63 (-0.59R)
- **CRH** 40.28 shares, entry 92.91, stop 85.09, now 94.81 (+0.20R)
- **ENPH** 66.37 shares, entry 28.32, stop 24.89, now 28.46 (+0.02R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.31, now 30.41 (+0.08R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.47 (-0.53R)
- **IBKR** 42.00 shares, entry 77.73, stop 68.48, now 75.82 (-0.20R)
- **LKQ** 136.21 shares, entry 20.25, stop 17.84, now 20.05 (-0.07R)
- **LSCC** 19.27 shares, entry 102.00, stop 82.67, now 105.02 (+0.15R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.03, now 172.76 (+0.09R)
- **PEP** 48.93 shares, entry 130.94, stop 133.04, now 141.34 (+1.27R)
- **SHEN** 255.69 shares, entry 9.73, stop 8.22, now 9.65 (-0.06R)
- **STC** 57.21 shares, entry 43.95, stop 42.30, now 47.00 (+0.44R)
- **SYY** 58.59 shares, entry 75.11, stop 70.05, now 76.86 (+0.26R)
- **TBBK** 75.36 shares, entry 48.49, stop 43.27, now 48.25 (-0.05R)
- **THRM** 74.49 shares, entry 29.84, stop 27.88, now 29.47 (-0.07R)

## New signals (bought at the next open)

- **CVS** 40.61 shares around 83.85, stop 74.16
- **FICO** 2.79 shares around 704.55, stop 563.45

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
