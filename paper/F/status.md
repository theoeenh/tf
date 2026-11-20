# F – Options

Updated 2026-11-20 19:24 UTC. **Equity $86,358** (-13.64% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 8 | $-3,408 | $-1,759 | 2 / 8 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 3 | 11 | $-7,654 | $-1,265 | 2 / 11 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 2 | 3 | $-1,031 | $-1,822 | 0 / 3 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **bull_put_spread** CAT: sell 530 / buy 500 puts, 2026-12-18, credit 5.77 on width 30 (opened 2026-11-05 16:58, cost $-605, most it can lose $2,423)
- **bull_put_spread** SYY: sell 75 / buy 72.5 puts, 2026-12-18, credit 0.46 on width 2.5 (opened 2026-11-06 20:01, cost $-650, most it can lose $2,652)
- **spy_put_spread** SPY: sell 720 / buy 690 puts, 2026-12-24, credit 3.62 on width 30 (opened 2026-11-10 15:24, cost $-369, most it can lose $2,638)
- **long_call** BKR: BKR Dec 18 2026 45 Call, delta +0.71 (opened 2026-11-10 16:24, cost $+2,520, most it can lose $2,556)
- **spy_put_spread** SPY: sell 707 / buy 676 puts, 2026-12-31, credit 3.91 on width 31 (opened 2026-11-17 14:54, cost $-391, most it can lose $2,709)
- **long_call** IBKR: IBKR Jan 15 2027 70 Call, delta +0.63 (opened 2026-11-20 16:24, cost $+2,310, most it can lose $2,352)
- **bull_put_spread** ETN: sell 290 / buy 260 puts, 2027-01-15, credit 5.92 on width 30 (opened 2026-11-20 16:24, cost $-610, most it can lose $2,408)

## Alpaca vs book

Alpaca values the positions at $-839; at the quotes' mid they are worth $58 (difference $-897).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $1,715 | $1,734 | ok |
| BKR261218C00045000 | 6 | $1,260 | $1,380 | ok |
| CAT261218P00500000 | 1 | $2,155 | $2,215 | ok |
| CAT261218P00530000 | -1 | $-3,785 | $-3,592 | ok |
| ETN270115P00260000 | 1 | $750 | $793 | ok |
| ETN270115P00290000 | -1 | $-1,640 | $-1,564 | ok |
| IBKR270115C00070000 | 3 | $1,890 | $1,980 | ok |
| SPY261224P00690000 | 1 | $1,976 | $2,010 | ok |
| SPY261224P00720000 | -1 | $-3,373 | $-3,360 | ok |
| SPY261231P00676000 | 1 | $1,669 | $1,662 | ok |
| SPY261231P00707000 | -1 | $-2,806 | $-2,811 | ok |
| SYY261218P00072500 | 13 | $325 | $462 | Alpaca's price far from the quotes |
| SYY261218P00075000 | -13 | $-975 | $-852 | ok |
