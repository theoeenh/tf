# F – Options

Updated 2026-11-06 17:27 UTC. **Equity $92,158** (-7.84% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 6 | $-4,420 | $+1,735 | 1 / 6 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 2 | 10 | $-6,466 | $-837 | 2 / 10 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 2 | 1 | $-491 | $-693 | 0 / 1 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)
- **spy_put_spread** SPY: sell 742 / buy 710 puts, 2026-12-04, credit 3.25 on width 32 (opened 2026-10-27 14:29, cost $-337, most it can lose $2,875)
- **spy_put_spread** SPY: sell 725 / buy 695 puts, 2026-12-11, credit 3.47 on width 30 (opened 2026-11-03 15:05, cost $-356, most it can lose $2,653)
- **bull_put_spread** BA: sell 170 / buy 160 puts, 2026-12-18, credit 1.91 on width 10 (opened 2026-11-04 14:59, cost $-582, most it can lose $2,427)
- **bull_put_spread** CAT: sell 530 / buy 500 puts, 2026-12-18, credit 5.77 on width 30 (opened 2026-11-05 16:58, cost $-605, most it can lose $2,423)
- **long_call** BA: BA Dec 11 2026 170 Call, delta +0.60 (opened 2026-11-06 16:58, cost $+1,890, most it can lose $1,896)

## Alpaca vs book

Alpaca values the positions at $4,638; at the quotes' mid they are worth $5,814 (difference $-1,176).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $1,825 | $1,824 | ok |
| BA261211C00170000 | 2 | $1,670 | $1,774 | ok |
| BA261218P00160000 | 3 | $849 | $893 | ok |
| BA261218P00170000 | -3 | $-1,905 | $-1,842 | ok |
| CAT261218P00500000 | 1 | $1,115 | $1,148 | ok |
| CAT261218P00530000 | -1 | $-2,090 | $-1,969 | ok |
| PEP261120C00133000 | 6 | $4,530 | $5,346 | ok |
| SPY261204P00710000 | 1 | $705 | $718 | ok |
| SPY261204P00742000 | -1 | $-1,531 | $-1,540 | ok |
| SPY261211P00695000 | 1 | $634 | $634 | ok |
| SPY261211P00725000 | -1 | $-1,164 | $-1,172 | ok |
