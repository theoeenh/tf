# F – Options

Updated 2026-10-28 13:58 UTC. **Equity $96,609** (-3.39% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 5 | $-2,044 | $-1,774 | 1 / 5 |
| long_put | 3 | 3 | $-520 | $+115 | 1 / 3 |
| bull_put_spread | 3 | 7 | $-1,084 | $-2,082 | 1 / 7 |
| bear_call_spread | 1 | 5 | $-512 | $-201 | 3 / 5 |
| spy_put_spread | 2 | 0 | $+0 | $+82 | 0 / 0 |

## Open positions

- **long_put** IWM: IWM Dec 18 2026 284 Put, delta -0.60 (opened 2026-10-20 14:29, cost $+2,523, most it can lose $2,528)
- **long_put** NFLX: NFLX Dec 18 2026 75 Put, delta -0.60 (opened 2026-10-20 15:00, cost $+2,190, most it can lose $2,214)
- **bear_call_spread** AVGO: sell 360 / buy 380 calls, 2026-11-20, credit 3.43 on width 20 (opened 2026-10-20 15:35, cost $-355, most it can lose $1,657)
- **long_put** AVGO: AVGO Nov 20 2026 347.5 Put, delta -0.59 (opened 2026-10-20 15:39, cost $+2,210, most it can lose $2,218)
- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **bull_put_spread** AAPL: sell 327.5 / buy 310 puts, 2026-11-20, credit 3.09 on width 17.5 (opened 2026-10-20 18:28, cost $-315, most it can lose $1,441)
- **bull_put_spread** FIS: sell 35 / buy 32.5 puts, 2026-11-20, credit 0.56 on width 2.5 (opened 2026-10-20 19:27, cost $-840, most it can lose $2,716)
- **spy_put_spread** SPY: sell 746 / buy 715 puts, 2026-11-27, credit 3.00 on width 31 (opened 2026-10-20 19:28, cost $-321, most it can lose $2,800)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)
- **bull_put_spread** CLF: sell 13 / buy 12 puts, 2026-12-18, credit 0.25 on width 1 (opened 2026-10-26 15:57, cost $-1,080, most it can lose $3,000)
- **long_call** CLF: CLF Dec 04 2026 13.5 Call, delta +0.59 (opened 2026-10-26 17:59, cost $+2,948, most it can lose $2,992)
- **spy_put_spread** SPY: sell 742 / buy 710 puts, 2026-12-04, credit 3.25 on width 32 (opened 2026-10-27 14:29, cost $-337, most it can lose $2,875)

## Alpaca vs book

Alpaca values the positions at $7,089; at the quotes' mid they are worth $9,053 (difference $-1,964).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261120P00310000 | 1 | $134 | $138 | ok |
| AAPL261120P00327500 | -1 | $-390 | $-377 | ok |
| AAPL261218C00335000 | 1 | $1,975 | $2,020 | ok |
| AVGO261120C00360000 | -1 | $-990 | $-973 | ok |
| AVGO261120C00380000 | 1 | $435 | $443 | ok |
| AVGO261120P00347500 | 1 | $1,465 | $1,470 | ok |
| CLF261204C00013500 | 22 | $1,936 | $2,233 | ok |
| CLF261218P00012000 | 40 | $1,960 | $2,200 | ok |
| CLF261218P00013000 | -40 | $-4,000 | $-3,760 | ok |
| FIS261120P00032500 | 14 | $490 | $798 | Alpaca's price far from the quotes |
| FIS261120P00035000 | -14 | $-2,520 | $-2,058 | Alpaca's price far from the quotes |
| IWM261218P00284000 | 2 | $1,830 | $1,846 | ok |
| NFLX261218P00075000 | 3 | $3,720 | $3,862 | ok |
| PEP261120C00133000 | 6 | $1,620 | $1,776 | ok |
| SPY261127P00715000 | 1 | $228 | $233 | ok |
| SPY261127P00746000 | -1 | $-512 | $-518 | ok |
| SPY261204P00710000 | 1 | $274 | $279 | ok |
| SPY261204P00742000 | -1 | $-566 | $-558 | ok |
