# F – Options

Updated 2026-11-03 20:05 UTC. **Equity $101,041** (+1.04% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 5 | $-2,044 | $+143 | 1 / 5 |
| long_put | 3 | 3 | $-520 | $+798 | 1 / 3 |
| bull_put_spread | 3 | 7 | $-1,084 | $-146 | 1 / 7 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 3 | 0 | $+0 | $-506 | 0 / 0 |

## Open positions

- **long_put** IWM: IWM Dec 18 2026 284 Put, delta -0.60 (opened 2026-10-20 14:29, cost $+2,523, most it can lose $2,528)
- **long_put** NFLX: NFLX Dec 18 2026 75 Put, delta -0.60 (opened 2026-10-20 15:00, cost $+2,190, most it can lose $2,214)
- **long_put** AVGO: AVGO Nov 20 2026 347.5 Put, delta -0.59 (opened 2026-10-20 15:39, cost $+2,210, most it can lose $2,218)
- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **bull_put_spread** AAPL: sell 327.5 / buy 310 puts, 2026-11-20, credit 3.09 on width 17.5 (opened 2026-10-20 18:28, cost $-315, most it can lose $1,441)
- **bull_put_spread** FIS: sell 35 / buy 32.5 puts, 2026-11-20, credit 0.56 on width 2.5 (opened 2026-10-20 19:27, cost $-840, most it can lose $2,716)
- **spy_put_spread** SPY: sell 746 / buy 715 puts, 2026-11-27, credit 3.00 on width 31 (opened 2026-10-20 19:28, cost $-321, most it can lose $2,800)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)
- **bull_put_spread** CLF: sell 13 / buy 12 puts, 2026-12-18, credit 0.25 on width 1 (opened 2026-10-26 15:57, cost $-1,080, most it can lose $3,000)
- **long_call** CLF: CLF Dec 04 2026 13.5 Call, delta +0.59 (opened 2026-10-26 17:59, cost $+2,948, most it can lose $2,992)
- **spy_put_spread** SPY: sell 742 / buy 710 puts, 2026-12-04, credit 3.25 on width 32 (opened 2026-10-27 14:29, cost $-337, most it can lose $2,875)
- **spy_put_spread** SPY: sell 725 / buy 695 puts, 2026-12-11, credit 3.47 on width 30 (opened 2026-11-03 15:05, cost $-356, most it can lose $2,653)

## Alpaca vs book

Alpaca values the positions at $11,327; at the quotes' mid they are worth $12,489 (difference $-1,162).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261120P00310000 | 1 | $184 | $191 | ok |
| AAPL261120P00327500 | -1 | $-655 | $-638 | ok |
| AAPL261218C00335000 | 1 | $985 | $994 | ok |
| AVGO261120P00347500 | 1 | $2,295 | $2,290 | ok |
| CLF261204C00013500 | 22 | $2,948 | $3,146 | ok |
| CLF261218P00012000 | 40 | $1,520 | $1,640 | ok |
| CLF261218P00013000 | -40 | $-2,800 | $-2,840 | ok |
| FIS261120P00032500 | 14 | $140 | $448 | Alpaca's price far from the quotes |
| FIS261120P00035000 | -14 | $-840 | $-665 | Alpaca's price far from the quotes |
| IWM261218P00284000 | 2 | $1,950 | $1,976 | ok |
| NFLX261218P00075000 | 3 | $3,540 | $3,632 | ok |
| PEP261120C00133000 | 6 | $3,540 | $3,816 | ok |
| SPY261127P00715000 | 1 | $383 | $389 | ok |
| SPY261127P00746000 | -1 | $-960 | $-975 | ok |
| SPY261204P00710000 | 1 | $435 | $442 | ok |
| SPY261204P00742000 | -1 | $-984 | $-998 | ok |
| SPY261211P00695000 | 1 | $400 | $404 | ok |
| SPY261211P00725000 | -1 | $-754 | $-763 | ok |
