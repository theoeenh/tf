# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-09. **Equity $99,943** (-0.06%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 159.89, now 172.38 (-0.27R)
- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 18.12 (-0.33R)
- **BBT** 179.42 shares, entry 30.77, stop 28.92, now 30.67 (-0.04R)
- **BKR** 60.38 shares, entry 46.50, stop 42.08, now 48.45 (+0.30R)
- **CAT** 4.63 shares, entry 609.75, stop 523.80, now 598.88 (-0.13R)
- **CRH** 40.28 shares, entry 92.91, stop 87.81, now 97.73 (+0.50R)
- **CVS** 40.61 shares, entry 84.64, stop 75.84, now 85.25 (+0.06R)
- **ENPH** 66.37 shares, entry 28.32, stop 24.89, now 29.08 (+0.13R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.31, now 30.76 (+0.25R)
- **FICO** 2.79 shares, entry 705.05, stop 586.52, now 723.76 (+0.13R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.92 (-0.04R)
- **IBKR** 42.00 shares, entry 77.73, stop 68.48, now 77.57 (-0.02R)
- **LKQ** 136.21 shares, entry 20.25, stop 17.92, now 20.41 (+0.05R)
- **LSCC** 19.27 shares, entry 102.00, stop 91.06, now 113.89 (+0.57R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.03, now 177.65 (+0.51R)
- **PEP** 48.93 shares, entry 130.94, stop 133.04, now 141.88 (+1.34R)
- **SHEN** 255.69 shares, entry 9.73, stop 8.67, now 10.21 (+0.31R)
- **STC** 57.21 shares, entry 43.95, stop 42.30, now 45.94 (+0.29R)
- **SYY** 58.59 shares, entry 75.11, stop 71.63, now 78.38 (+0.49R)
- **TBBK** 75.36 shares, entry 48.49, stop 44.46, now 49.79 (+0.24R)
- **THRM** 74.49 shares, entry 29.84, stop 27.91, now 30.38 (+0.10R)

## New signals (bought at the next open)

None.

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
