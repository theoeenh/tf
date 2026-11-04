# F – Options

Updated 2026-11-04 18:58 UTC. **Equity $97,676** (-2.32% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 5 | $-2,044 | $+2,099 | 1 / 5 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 3 | 8 | $-866 | $-5,130 | 2 / 8 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 3 | 0 | $+0 | $+277 | 0 / 0 |

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

Alpaca values the positions at $1,097; at the quotes' mid they are worth $3,795 (difference $-2,698).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $2,380 | $2,378 | ok |
| BA261218P00160000 | 3 | $585 | $612 | ok |
| BA261218P00170000 | -3 | $-1,410 | $-1,366 | ok |
| CLF261204C00013500 | 22 | $1,496 | $1,650 | ok |
| CLF261218P00012000 | 40 | $2,600 | $2,760 | ok |
| CLF261218P00013000 | -40 | $-4,760 | $-4,680 | ok |
| FIS261120P00032500 | 14 | $3,710 | $4,459 | ok |
| FIS261120P00035000 | -14 | $-8,400 | $-7,679 | ok |
| PEP261120C00133000 | 6 | $5,610 | $6,378 | ok |
| SPY261127P00715000 | 1 | $152 | $150 | ok |
| SPY261127P00746000 | -1 | $-410 | $-410 | ok |
| SPY261204P00710000 | 1 | $197 | $196 | ok |
| SPY261204P00742000 | -1 | $-470 | $-470 | ok |
| SPY261211P00695000 | 1 | $200 | $205 | ok |
| SPY261211P00725000 | -1 | $-383 | $-388 | ok |
