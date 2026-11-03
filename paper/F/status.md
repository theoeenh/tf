# F – Options

Updated 2026-11-03 15:24 UTC. **Equity $101,496** (+1.50% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 5 | $-2,044 | $+162 | 1 / 5 |
| long_put | 3 | 3 | $-520 | $+1,014 | 1 / 3 |
| bull_put_spread | 3 | 7 | $-1,084 | $-47 | 1 / 7 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 3 | 0 | $+0 | $-440 | 0 / 0 |

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

Alpaca values the positions at $11,664; at the quotes' mid they are worth $13,353 (difference $-1,689).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261120P00310000 | 1 | $185 | $189 | ok |
| AAPL261120P00327500 | -1 | $-615 | $-600 | ok |
| AAPL261218C00335000 | 1 | $1,060 | $1,090 | ok |
| AVGO261120P00347500 | 1 | $2,260 | $2,303 | ok |
| CLF261204C00013500 | 22 | $2,970 | $3,168 | ok |
| CLF261218P00012000 | 40 | $1,360 | $1,540 | ok |
| CLF261218P00013000 | -40 | $-2,720 | $-2,620 | ok |
| FIS261120P00032500 | 14 | $210 | $483 | Alpaca's price far from the quotes |
| FIS261120P00035000 | -14 | $-770 | $-637 | Alpaca's price far from the quotes |
| IWM261218P00284000 | 2 | $1,864 | $1,893 | ok |
| NFLX261218P00075000 | 3 | $3,750 | $3,837 | ok |
| PEP261120C00133000 | 6 | $3,570 | $4,149 | ok |
| SPY261127P00715000 | 1 | $371 | $374 | ok |
| SPY261127P00746000 | -1 | $-940 | $-935 | ok |
| SPY261204P00710000 | 1 | $424 | $428 | ok |
| SPY261204P00742000 | -1 | $-966 | $-959 | ok |
| SPY261211P00695000 | 1 | $393 | $402 | ok |
| SPY261211P00725000 | -1 | $-742 | $-753 | ok |
