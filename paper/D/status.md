# D – Insider + low short (early test)

Strategy: `1591c2bcb6` insider_low_short(buyers=1, max_rank=0.3) | stop_atr=3.0, rr=None, trail_atr=3.0, max_bars=60 | no trend filter | S&P 1500, daily
Started 2026-10-12 with $100,000. Data through 2026-11-05. **Equity $98,058** (-1.94%).

Early test of the finder's most active 13/14 candidate (`1591c2bcb6`, NOT graduated: it fails only the luck check): buy an S&P 1500 stock the day an insider buys it in the open market (first purchase in 90 days) while short sellers are not betting against it (20-day short share of off-exchange volume, FINRA, in the lowest 30% of the S&P 1500). Stop 3 ATR trailing, out after 60 sessions, 0.4% of equity at risk per trade. About 230 trades a year in the backtest (search avg +0.14R, validation +0.20R). User's go 2026-10-10; a finder graduate would take this account over.

## Open positions

- **BA** 23.16 shares, entry 177.09, stop 159.89, now 172.50 (-0.27R)
- **BANC** 316.56 shares, entry 18.55, stop 17.27, now 17.96 (-0.46R)
- **BBT** 179.42 shares, entry 30.77, stop 28.92, now 30.28 (-0.22R)
- **CAT** 4.63 shares, entry 609.75, stop 523.80, now 553.64 (-0.65R)
- **ENPH** 66.37 shares, entry 28.32, stop 24.89, now 28.97 (+0.11R)
- **FFIN** 191.18 shares, entry 30.23, stop 29.31, now 30.68 (+0.21R)
- **HBAN** 430.71 shares, entry 15.96, stop 15.06, now 15.61 (-0.38R)
- **IBKR** 42.00 shares, entry 77.73, stop 68.48, now 72.73 (-0.53R)
- **LKQ** 136.21 shares, entry 20.25, stop 17.82, now 20.54 (+0.10R)
- **LSCC** 19.27 shares, entry 102.00, stop 81.25, now 98.03 (-0.19R)
- **NTRS** 34.09 shares, entry 171.66, stop 166.03, now 171.39 (-0.02R)
- **PEP** 48.93 shares, entry 130.94, stop 133.04, now 142.71 (+1.44R)
- **STC** 57.21 shares, entry 43.95, stop 42.30, now 48.99 (+0.72R)
- **TBBK** 75.36 shares, entry 48.49, stop 43.18, now 47.74 (-0.14R)
- **THRM** 74.49 shares, entry 29.84, stop 27.67, now 29.62 (-0.04R)

## New signals (bought at the next open)

- **BKR** 60.38 shares around 46.20, stop 39.70
- **CRH** 40.29 shares around 95.45, stop 85.71
- **SHEN** 255.47 shares around 9.72, stop 8.18
- **SYY** 58.55 shares around 75.24, stop 68.54

## Closed trades

- 2026-10-23 PRIM: -0.95R, $-382 (trail)
- 2026-11-04 FIS: -1.64R, $-654 (trail)
- 2026-11-05 EME: -1.16R, $-464 (trail)
- 2026-11-05 CLF: -0.79R, $-316 (trail)
