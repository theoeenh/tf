# F – Options

Updated 2026-11-25 14:08 UTC. **Equity $86,914** (-13.09% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 9 | $-3,048 | $-1,278 | 3 / 9 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 3 | 12 | $-8,089 | $-1,141 | 2 / 12 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 3 | 3 | $-1,031 | $-1,928 | 0 / 3 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **bull_put_spread** SYY: sell 75 / buy 72.5 puts, 2026-12-18, credit 0.46 on width 2.5 (opened 2026-11-06 20:01, cost $-650, most it can lose $2,652)
- **spy_put_spread** SPY: sell 720 / buy 690 puts, 2026-12-24, credit 3.62 on width 30 (opened 2026-11-10 15:24, cost $-369, most it can lose $2,638)
- **long_call** BKR: BKR Dec 18 2026 45 Call, delta +0.71 (opened 2026-11-10 16:24, cost $+2,520, most it can lose $2,556)
- **spy_put_spread** SPY: sell 707 / buy 676 puts, 2026-12-31, credit 3.91 on width 31 (opened 2026-11-17 14:54, cost $-391, most it can lose $2,709)
- **bull_put_spread** ETN: sell 290 / buy 260 puts, 2027-01-15, credit 5.92 on width 30 (opened 2026-11-20 16:24, cost $-610, most it can lose $2,408)
- **long_call** FUN: FUN Jan 15 2027 10 Call, delta +0.69 (opened 2026-11-23 16:53, cost $+2,590, most it can lose $2,618)
- **spy_put_spread** SPY: sell 679 / buy 649 puts, 2026-12-31, credit 3.96 on width 30 (opened 2026-11-24 15:23, cost $-424, most it can lose $2,604)
- **bull_put_spread** COHR: sell 175 / buy 165 puts, 2027-01-15, credit 2.06 on width 10 (opened 2026-11-24 17:23, cost $-690, most it can lose $2,382)

## Alpaca vs book

Alpaca values the positions at $-347; at the quotes' mid they are worth $1,411 (difference $-1,758).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $1,990 | $2,139 | ok |
| BKR261218C00045000 | 6 | $1,140 | $1,410 | ok |
| COHR270115P00165000 | 3 | $3,990 | $4,178 | ok |
| COHR270115P00175000 | -3 | $-5,550 | $-5,274 | ok |
| ETN270115P00260000 | 1 | $440 | $514 | ok |
| ETN270115P00290000 | -1 | $-1,310 | $-1,188 | ok |
| FUN270115C00010000 | 14 | $2,660 | $2,863 | ok |
| SPY261224P00690000 | 1 | $1,484 | $1,576 | ok |
| SPY261224P00720000 | -1 | $-2,880 | $-2,792 | ok |
| SPY261231P00649000 | 1 | $790 | $809 | ok |
| SPY261231P00676000 | 1 | $1,280 | $1,302 | ok |
| SPY261231P00679000 | -1 | $-1,401 | $-1,387 | ok |
| SPY261231P00707000 | -1 | $-2,330 | $-2,322 | ok |
| SYY261218P00072500 | 13 | $195 | $260 | ok |
| SYY261218P00075000 | -13 | $-845 | $-676 | Alpaca's price far from the quotes |
