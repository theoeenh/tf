# F – Options

Updated 2026-11-05 20:40 UTC. **Equity $93,221** (-6.78% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 5 | $-2,044 | $+1,045 | 1 / 5 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 3 | 9 | $-4,226 | $-3,214 | 2 / 9 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 3 | 0 | $+0 | $-1,685 | 0 / 0 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **spy_put_spread** SPY: sell 746 / buy 715 puts, 2026-11-27, credit 3.00 on width 31 (opened 2026-10-20 19:28, cost $-321, most it can lose $2,800)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)
- **bull_put_spread** CLF: sell 13 / buy 12 puts, 2026-12-18, credit 0.25 on width 1 (opened 2026-10-26 15:57, cost $-1,080, most it can lose $3,000)
- **long_call** CLF: CLF Dec 04 2026 13.5 Call, delta +0.59 (opened 2026-10-26 17:59, cost $+2,948, most it can lose $2,992)
- **spy_put_spread** SPY: sell 742 / buy 710 puts, 2026-12-04, credit 3.25 on width 32 (opened 2026-10-27 14:29, cost $-337, most it can lose $2,875)
- **spy_put_spread** SPY: sell 725 / buy 695 puts, 2026-12-11, credit 3.47 on width 30 (opened 2026-11-03 15:05, cost $-356, most it can lose $2,653)
- **bull_put_spread** BA: sell 170 / buy 160 puts, 2026-12-18, credit 1.91 on width 10 (opened 2026-11-04 14:59, cost $-582, most it can lose $2,427)
- **bull_put_spread** CAT: sell 530 / buy 500 puts, 2026-12-18, credit 5.77 on width 30 (opened 2026-11-05 16:58, cost $-605, most it can lose $2,423)

## Alpaca vs book

Alpaca values the positions at $241; at the quotes' mid they are worth $2,010 (difference $-1,768).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $1,950 | $1,955 | ok |
| BA261218P00160000 | 3 | $915 | $966 | ok |
| BA261218P00170000 | -3 | $-1,980 | $-1,907 | ok |
| CAT261218P00500000 | 1 | $1,305 | $1,370 | ok |
| CAT261218P00530000 | -1 | $-2,340 | $-2,278 | ok |
| CLF261204C00013500 | 22 | $462 | $594 | Alpaca's price far from the quotes |
| CLF261218P00012000 | 40 | $5,400 | $5,660 | ok |
| CLF261218P00013000 | -40 | $-8,800 | $-8,440 | ok |
| PEP261120C00133000 | 6 | $5,970 | $6,684 | ok |
| SPY261127P00715000 | 1 | $888 | $898 | ok |
| SPY261127P00746000 | -1 | $-1,944 | $-1,913 | ok |
| SPY261204P00710000 | 1 | $943 | $939 | ok |
| SPY261204P00742000 | -1 | $-1,898 | $-1,914 | ok |
| SPY261211P00695000 | 1 | $831 | $845 | ok |
| SPY261211P00725000 | -1 | $-1,461 | $-1,450 | ok |
