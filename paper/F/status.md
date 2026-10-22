# F – Options

Updated 2026-10-22 23:57 UTC. **Equity $104,014** (+4.01% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 4 | $-1,464 | $+534 | 1 / 4 |
| long_put | 3 | 3 | $-520 | $+986 | 1 / 3 |
| bull_put_spread | 3 | 6 | $-809 | $-163 | 1 / 6 |
| bear_call_spread | 2 | 4 | $-988 | $+692 | 2 / 4 |
| spy_put_spread | 1 | 0 | $+0 | $-95 | 0 / 0 |

## Open positions

- **long_call** MSFT: MSFT Nov 20 2026 520 Call, delta +0.58 (opened 2026-10-05 15:55, cost $+2,795, most it can lose $2,798)
- **bear_call_spread** IWM: sell 286 / buy 295 calls, 2026-11-20, credit 1.85 on width 9 (opened 2026-10-08 15:27, cost $-772, most it can lose $2,860)
- **long_put** IWM: IWM Dec 18 2026 284 Put, delta -0.60 (opened 2026-10-20 14:29, cost $+2,523, most it can lose $2,528)
- **bull_put_spread** MSFT: sell 505 / buy 470 puts, 2026-12-18, credit 6.91 on width 35 (opened 2026-10-20 14:29, cost $-710, most it can lose $2,809)
- **long_put** NFLX: NFLX Dec 18 2026 75 Put, delta -0.60 (opened 2026-10-20 15:00, cost $+2,190, most it can lose $2,214)
- **bear_call_spread** AVGO: sell 360 / buy 380 calls, 2026-11-20, credit 3.43 on width 20 (opened 2026-10-20 15:35, cost $-355, most it can lose $1,657)
- **long_put** AVGO: AVGO Nov 20 2026 347.5 Put, delta -0.59 (opened 2026-10-20 15:39, cost $+2,210, most it can lose $2,218)
- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **bull_put_spread** AAPL: sell 327.5 / buy 310 puts, 2026-11-20, credit 3.09 on width 17.5 (opened 2026-10-20 18:28, cost $-315, most it can lose $1,441)
- **bull_put_spread** FIS: sell 35 / buy 32.5 puts, 2026-11-20, credit 0.56 on width 2.5 (opened 2026-10-20 19:27, cost $-840, most it can lose $2,716)
- **spy_put_spread** SPY: sell 746 / buy 715 puts, 2026-11-27, credit 3.00 on width 31 (opened 2026-10-20 19:28, cost $-321, most it can lose $2,800)
- **long_call** PEP: PEP Nov 20 2026 133 Call, delta +0.59 (opened 2026-10-21 13:58, cost $+2,610, most it can lose $2,628)

## Alpaca vs book

Alpaca values the positions at $29,603; at the quotes' mid they are worth $31,536 (difference $-1,932).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261120P00310000 | 3 | $450 | $462 | book 1 |
| AAPL261120P00327500 | -1 | $-405 | $-394 | ok |
| AAPL261218C00335000 | 1 | $2,300 | $2,359 | ok |
| AMZN261113P00245000 | 4 | $3,420 | $3,542 | book 0 |
| AVGO261120C00360000 | -1 | $-440 | $-424 | ok |
| AVGO261120C00380000 | 1 | $184 | $189 | ok |
| AVGO261120P00347500 | 1 | $2,950 | $2,967 | ok |
| FIS261120P00032500 | 14 | $350 | $420 | ok |
| FIS261120P00035000 | -14 | $-1,050 | $-945 | ok |
| IWM261113C00294000 | 4 | $228 | $244 | book 0 |
| IWM261120C00295000 | 4 | $312 | $310 | ok |
| IWM261218P00284000 | 2 | $2,442 | $2,467 | ok |
| MSFT261106P00480000 | 1 | $325 | $354 | book 0 |
| MSFT261120C00520000 | 1 | $2,030 | $2,098 | ok |
| MSFT261218P00470000 | 1 | $650 | $688 | ok |
| MSFT261218P00505000 | -1 | $-1,700 | $-1,664 | ok |
| NFLX261218C00085000 | 4 | $84 | $78 | book 0 |
| NFLX261218P00075000 | 3 | $2,505 | $2,599 | ok |
| PEP261120C00133000 | 6 | $3,300 | $4,470 | Alpaca's price far from the quotes |
| QQQ261106P00704000 | 1 | $1,493 | $1,506 | book 0 |
| QQQ261113P00699000 | 3 | $4,497 | $4,458 | book 0 |
| QQQ261120P00691000 | 1 | $1,412 | $1,430 | book 0 |
| SPY261127P00715000 | 1 | $364 | $364 | ok |
| SPY261127P00746000 | -1 | $-773 | $-778 | ok |
| TLT261106C00079000 | 17 | $4,675 | $4,734 | book 0 |
