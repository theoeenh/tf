# F – Options

Updated 2026-11-04 16:01 UTC. **Equity $97,897** (-2.10% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 5 | $-2,044 | $+2,194 | 1 / 5 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 3 | 8 | $-866 | $-4,724 | 2 / 8 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 3 | 0 | $+0 | $+246 | 0 / 0 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **bull_put_spread** FIS: sell 35 / buy 32.5 puts, 2026-11-20, credit 0.56 on width 2.5 (opened 2026-10-20 19:27, cost $-840, most it can lose $2,716)
- **spy_put_spread** SPY: sell 746 / buy 715 puts, 2026-11-27, credit 3.00 on width 31 (opened 2026-10-20 19:28, cost $-321, most it can lose $2,800)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)
- **bull_put_spread** CLF: sell 13 / buy 12 puts, 2026-12-18, credit 0.25 on width 1 (opened 2026-10-26 15:57, cost $-1,080, most it can lose $3,000)
- **long_call** CLF: CLF Dec 04 2026 13.5 Call, delta +0.59 (opened 2026-10-26 17:59, cost $+2,948, most it can lose $2,992)
- **spy_put_spread** SPY: sell 742 / buy 710 puts, 2026-12-04, credit 3.25 on width 32 (opened 2026-10-27 14:29, cost $-337, most it can lose $2,875)
- **spy_put_spread** SPY: sell 725 / buy 695 puts, 2026-12-11, credit 3.47 on width 30 (opened 2026-11-03 15:05, cost $-356, most it can lose $2,653)
- **bull_put_spread** BA: sell 170 / buy 160 puts, 2026-12-18, credit 1.91 on width 10 (opened 2026-11-04 14:59, cost $-582, most it can lose $2,427)

## Alpaca vs book

Alpaca values the positions at $1,317; at the quotes' mid they are worth $3,960 (difference $-2,643).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $2,465 | $2,514 | ok |
| BA261218P00160000 | 3 | $540 | $564 | ok |
| BA261218P00170000 | -3 | $-1,350 | $-1,307 | ok |
| CLF261204C00013500 | 22 | $1,430 | $1,716 | ok |
| CLF261218P00012000 | 40 | $2,120 | $2,460 | ok |
| CLF261218P00013000 | -40 | $-4,600 | $-4,320 | ok |
| FIS261120P00032500 | 14 | $3,710 | $4,186 | ok |
| FIS261120P00035000 | -14 | $-7,840 | $-7,448 | ok |
| PEP261120C00133000 | 6 | $5,610 | $6,348 | ok |
| SPY261127P00715000 | 1 | $168 | $171 | ok |
| SPY261127P00746000 | -1 | $-449 | $-449 | ok |
| SPY261204P00710000 | 1 | $216 | $220 | ok |
| SPY261204P00742000 | -1 | $-507 | $-503 | ok |
| SPY261211P00695000 | 1 | $217 | $220 | ok |
| SPY261211P00725000 | -1 | $-413 | $-412 | ok |
