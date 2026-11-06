# F – Options

Updated 2026-11-06 17:56 UTC. **Equity $91,981** (-8.02% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 6 | $-4,420 | $+1,633 | 1 / 6 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 2 | 10 | $-6,466 | $-927 | 2 / 10 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 2 | 1 | $-491 | $-829 | 0 / 1 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)
- **spy_put_spread** SPY: sell 742 / buy 710 puts, 2026-12-04, credit 3.25 on width 32 (opened 2026-10-27 14:29, cost $-337, most it can lose $2,875)
- **spy_put_spread** SPY: sell 725 / buy 695 puts, 2026-12-11, credit 3.47 on width 30 (opened 2026-11-03 15:05, cost $-356, most it can lose $2,653)
- **bull_put_spread** BA: sell 170 / buy 160 puts, 2026-12-18, credit 1.91 on width 10 (opened 2026-11-04 14:59, cost $-582, most it can lose $2,427)
- **bull_put_spread** CAT: sell 530 / buy 500 puts, 2026-12-18, credit 5.77 on width 30 (opened 2026-11-05 16:58, cost $-605, most it can lose $2,423)
- **long_call** BA: BA Dec 11 2026 170 Call, delta +0.60 (opened 2026-11-06 16:58, cost $+1,890, most it can lose $1,896)

## Alpaca vs book

Alpaca values the positions at $4,450; at the quotes' mid they are worth $5,451 (difference $-1,001).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $1,815 | $1,828 | ok |
| BA261211C00170000 | 2 | $1,690 | $1,774 | ok |
| BA261218P00160000 | 3 | $888 | $920 | ok |
| BA261218P00170000 | -3 | $-1,950 | $-1,886 | ok |
| CAT261218P00500000 | 1 | $1,190 | $1,242 | ok |
| CAT261218P00530000 | -1 | $-2,210 | $-2,124 | ok |
| PEP261120C00133000 | 6 | $4,530 | $5,193 | ok |
| SPY261204P00710000 | 1 | $850 | $851 | ok |
| SPY261204P00742000 | -1 | $-1,759 | $-1,763 | ok |
| SPY261211P00695000 | 1 | $758 | $758 | ok |
| SPY261211P00725000 | -1 | $-1,352 | $-1,342 | ok |
