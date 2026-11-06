# F – Options

Updated 2026-11-06 14:58 UTC. **Equity $91,186** (-8.81% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 2 | 6 | $-4,420 | $+1,268 | 1 / 6 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 3 | 9 | $-4,226 | $-3,302 | 2 / 9 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 3 | 0 | $+0 | $-1,265 | 0 / 0 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **spy_put_spread** SPY: sell 746 / buy 715 puts, 2026-11-27, credit 3.00 on width 31 (opened 2026-10-20 19:28, cost $-321, most it can lose $2,800)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)
- **bull_put_spread** CLF: sell 13 / buy 12 puts, 2026-12-18, credit 0.25 on width 1 (opened 2026-10-26 15:57, cost $-1,080, most it can lose $3,000)
- **spy_put_spread** SPY: sell 742 / buy 710 puts, 2026-12-04, credit 3.25 on width 32 (opened 2026-10-27 14:29, cost $-337, most it can lose $2,875)
- **spy_put_spread** SPY: sell 725 / buy 695 puts, 2026-12-11, credit 3.47 on width 30 (opened 2026-11-03 15:05, cost $-356, most it can lose $2,653)
- **bull_put_spread** BA: sell 170 / buy 160 puts, 2026-12-18, credit 1.91 on width 10 (opened 2026-11-04 14:59, cost $-582, most it can lose $2,427)
- **bull_put_spread** CAT: sell 530 / buy 500 puts, 2026-12-18, credit 5.77 on width 30 (opened 2026-11-05 16:58, cost $-605, most it can lose $2,423)

## Alpaca vs book

Alpaca values the positions at $7,157; at the quotes' mid they are worth $8,652 (difference $-1,496).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $1,750 | $1,774 | ok |
| BA261218P00160000 | 3 | $864 | $928 | ok |
| BA261218P00170000 | -3 | $-1,965 | $-1,858 | ok |
| CAT261218P00500000 | 1 | $930 | $1,030 | ok |
| CAT261218P00530000 | -1 | $-1,945 | $-1,812 | ok |
| CLF261218P00012000 | 40 | $4,360 | $4,780 | ok |
| PEP261120C00133000 | 6 | $3,870 | $4,512 | ok |
| SPY261127P00715000 | 1 | $632 | $638 | ok |
| SPY261204P00710000 | 1 | $695 | $698 | ok |
| SPY261204P00742000 | -1 | $-1,511 | $-1,508 | ok |
| SPY261211P00695000 | 1 | $622 | $622 | ok |
| SPY261211P00725000 | -1 | $-1,145 | $-1,152 | ok |
