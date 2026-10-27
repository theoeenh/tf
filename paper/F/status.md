# F – Options

Updated 2026-10-27 16:56 UTC. **Equity $98,963** (-1.04% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 5 | $-2,044 | $-832 | 1 / 5 |
| long_put | 3 | 3 | $-520 | $+471 | 1 / 3 |
| bull_put_spread | 3 | 7 | $-1,084 | $-1,400 | 1 / 7 |
| bear_call_spread | 1 | 5 | $-512 | $-113 | 3 / 5 |
| spy_put_spread | 2 | 0 | $+0 | $+27 | 0 / 0 |

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

Alpaca values the positions at $9,394; at the quotes' mid they are worth $10,690 (difference $-1,296).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261120P00310000 | 1 | $132 | $134 | ok |
| AAPL261120P00327500 | -1 | $-375 | $-362 | ok |
| AAPL261218C00335000 | 1 | $2,110 | $2,096 | ok |
| AVGO261120C00360000 | -1 | $-840 | $-822 | ok |
| AVGO261120C00380000 | 1 | $365 | $377 | ok |
| AVGO261120P00347500 | 1 | $1,680 | $1,669 | ok |
| CLF261204C00013500 | 22 | $2,596 | $2,926 | ok |
| CLF261218P00012000 | 40 | $1,520 | $1,620 | ok |
| CLF261218P00013000 | -40 | $-3,160 | $-3,040 | ok |
| FIS261120P00032500 | 14 | $630 | $770 | ok |
| FIS261120P00035000 | -14 | $-2,240 | $-1,988 | ok |
| IWM261218P00284000 | 2 | $1,990 | $2,014 | ok |
| NFLX261218P00075000 | 3 | $3,675 | $3,753 | ok |
| PEP261120C00133000 | 6 | $1,920 | $2,160 | ok |
| SPY261127P00715000 | 1 | $245 | $246 | ok |
| SPY261127P00746000 | -1 | $-547 | $-551 | ok |
| SPY261204P00710000 | 1 | $290 | $294 | ok |
| SPY261204P00742000 | -1 | $-597 | $-606 | ok |
