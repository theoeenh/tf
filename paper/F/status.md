# F – Options

Updated 2026-10-26 15:11 UTC. **Equity $101,999** (+2.00% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 2 | 5 | $-2,044 | $+668 | 1 / 5 |
| long_put | 3 | 3 | $-520 | $+730 | 1 / 3 |
| bull_put_spread | 2 | 7 | $-1,084 | $-205 | 1 / 7 |
| bear_call_spread | 1 | 5 | $-512 | $+73 | 3 / 5 |
| spy_put_spread | 1 | 0 | $+0 | $-20 | 0 / 0 |

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

## Alpaca vs book

Alpaca values the positions at $10,932; at the quotes' mid they are worth $11,479 (difference $-547).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261120P00310000 | 1 | $135 | $136 | ok |
| AAPL261120P00327500 | -1 | $-380 | $-370 | ok |
| AAPL261218C00335000 | 1 | $2,130 | $2,135 | ok |
| AVGO261120C00360000 | -1 | $-495 | $-485 | ok |
| AVGO261120C00380000 | 1 | $203 | $207 | ok |
| AVGO261120P00347500 | 1 | $2,340 | $2,388 | ok |
| FIS261120P00032500 | 14 | $420 | $497 | ok |
| FIS261120P00035000 | -14 | $-1,470 | $-1,323 | ok |
| IWM261218P00284000 | 2 | $2,176 | $2,194 | ok |
| NFLX261218P00075000 | 3 | $3,180 | $3,230 | ok |
| PEP261120C00133000 | 6 | $3,030 | $3,201 | ok |
| SPY261127P00715000 | 1 | $273 | $276 | ok |
| SPY261127P00746000 | -1 | $-610 | $-608 | ok |
