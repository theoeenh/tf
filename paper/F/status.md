# F – Options

Updated 2026-11-06 18:11 UTC. **Equity $91,993** (-8.01% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 6 | $-4,420 | $+1,694 | 1 / 6 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 2 | 10 | $-6,466 | $-827 | 2 / 10 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 2 | 1 | $-491 | $-821 | 0 / 1 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)
- **spy_put_spread** SPY: sell 742 / buy 710 puts, 2026-12-04, credit 3.25 on width 32 (opened 2026-10-27 14:29, cost $-337, most it can lose $2,875)
- **spy_put_spread** SPY: sell 725 / buy 695 puts, 2026-12-11, credit 3.47 on width 30 (opened 2026-11-03 15:05, cost $-356, most it can lose $2,653)
- **bull_put_spread** BA: sell 170 / buy 160 puts, 2026-12-18, credit 1.91 on width 10 (opened 2026-11-04 14:59, cost $-582, most it can lose $2,427)
- **bull_put_spread** CAT: sell 530 / buy 500 puts, 2026-12-18, credit 5.77 on width 30 (opened 2026-11-05 16:58, cost $-605, most it can lose $2,423)
- **long_call** BA: BA Dec 11 2026 170 Call, delta +0.60 (opened 2026-11-06 16:58, cost $+1,890, most it can lose $1,896)

## Alpaca vs book

Alpaca values the positions at $4,457; at the quotes' mid they are worth $5,678 (difference $-1,220).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $1,790 | $1,837 | ok |
| BA261211C00170000 | 2 | $1,690 | $1,829 | ok |
| BA261218P00160000 | 3 | $846 | $886 | ok |
| BA261218P00170000 | -3 | $-1,905 | $-1,826 | ok |
| CAT261218P00500000 | 1 | $1,195 | $1,237 | ok |
| CAT261218P00530000 | -1 | $-2,210 | $-2,116 | ok |
| PEP261120C00133000 | 6 | $4,530 | $5,280 | ok |
| SPY261204P00710000 | 1 | $821 | $834 | ok |
| SPY261204P00742000 | -1 | $-1,717 | $-1,706 | ok |
| SPY261211P00695000 | 1 | $731 | $746 | ok |
| SPY261211P00725000 | -1 | $-1,314 | $-1,324 | ok |
