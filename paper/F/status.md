# F – Options

Updated 2026-10-23 18:58 UTC. **Equity $102,892** (+2.89% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 2 | 5 | $-2,044 | $+502 | 1 / 5 |
| long_put | 3 | 3 | $-520 | $+1,304 | 1 / 3 |
| bull_put_spread | 2 | 7 | $-1,084 | $-108 | 1 / 7 |
| bear_call_spread | 1 | 5 | $-512 | $+117 | 3 / 5 |
| spy_put_spread | 1 | 0 | $+0 | $-126 | 0 / 0 |

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

Alpaca values the positions at $27,003; at the quotes' mid they are worth $27,862 (difference $-860).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261120P00310000 | 3 | $471 | $488 | book 1 |
| AAPL261120P00327500 | -1 | $-425 | $-413 | ok |
| AAPL261218C00335000 | 1 | $2,180 | $2,186 | ok |
| AMZN261113P00245000 | 4 | $3,780 | $3,810 | book 0 |
| AVGO261120C00360000 | -1 | $-405 | $-396 | ok |
| AVGO261120C00380000 | 1 | $167 | $170 | ok |
| AVGO261120P00347500 | 1 | $2,830 | $2,911 | ok |
| FIS261120P00032500 | 14 | $420 | $518 | ok |
| FIS261120P00035000 | -14 | $-1,470 | $-1,295 | ok |
| IWM261113C00294000 | 4 | $172 | $184 | book 0 |
| IWM261218P00284000 | 2 | $2,542 | $2,587 | ok |
| MSFT261106P00480000 | 1 | $297 | $312 | book 0 |
| NFLX261218C00085000 | 4 | $68 | $70 | book 0 |
| NFLX261218P00075000 | 3 | $2,775 | $2,847 | ok |
| PEP261120C00133000 | 6 | $2,820 | $2,928 | ok |
| QQQ261106P00704000 | 1 | $1,365 | $1,391 | book 0 |
| QQQ261113P00699000 | 3 | $4,221 | $4,227 | book 0 |
| QQQ261120P00691000 | 1 | $1,351 | $1,350 | book 0 |
| SPY261127P00715000 | 1 | $414 | $423 | ok |
| SPY261127P00746000 | -1 | $-871 | $-864 | ok |
| TLT261106C00079000 | 17 | $4,301 | $4,428 | book 0 |
