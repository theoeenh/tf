# F – Options

Updated 2026-11-13 14:54 UTC. **Equity $93,839** (-6.16% since start). From 20 Oct: one SPY put spread a week (selling insurance on the S&P 500), plus calls and put spreads on account D's insider signals. Bearish playbooks paused (no tested bearish signal); positions opened before keep their own exit rules.

Active playbooks: spy_put_spread, long_call, bull_put_spread; stock signals from account D.

| playbook | open | closed | realised P&L | open P&L | wins / closed |
|---|---|---|---|---|---|
| long_call | 3 | 7 | $-1,900 | $+621 | 2 / 7 |
| long_put | 0 | 6 | $-1,046 | $+0 | 2 / 6 |
| bull_put_spread | 3 | 10 | $-6,466 | $-1,298 | 2 / 10 |
| bear_call_spread | 0 | 6 | $-317 | $+0 | 4 / 6 |
| spy_put_spread | 2 | 2 | $-548 | $+165 | 0 / 2 |

## Open positions

- **long_call** AAPL: AAPL Dec 18 2026 335 Call, delta +0.61 (opened 2026-10-20 16:56, cost $+1,805, most it can lose $1,807)
- **spy_put_spread** SPY: sell 725 / buy 695 puts, 2026-12-11, credit 3.47 on width 30 (opened 2026-11-03 15:05, cost $-356, most it can lose $2,653)
- **bull_put_spread** BA: sell 170 / buy 160 puts, 2026-12-18, credit 1.91 on width 10 (opened 2026-11-04 14:59, cost $-582, most it can lose $2,427)
- **bull_put_spread** CAT: sell 530 / buy 500 puts, 2026-12-18, credit 5.77 on width 30 (opened 2026-11-05 16:58, cost $-605, most it can lose $2,423)
- **long_call** BA: BA Dec 11 2026 170 Call, delta +0.60 (opened 2026-11-06 16:58, cost $+1,890, most it can lose $1,896)
- **bull_put_spread** SYY: sell 75 / buy 72.5 puts, 2026-12-18, credit 0.46 on width 2.5 (opened 2026-11-06 20:01, cost $-650, most it can lose $2,652)
- **spy_put_spread** SPY: sell 720 / buy 690 puts, 2026-12-24, credit 3.62 on width 30 (opened 2026-11-10 15:24, cost $-369, most it can lose $2,638)
- **long_call** BKR: BKR Dec 18 2026 45 Call, delta +0.71 (opened 2026-11-10 16:24, cost $+2,520, most it can lose $2,556)

## Alpaca vs book

Alpaca values the positions at $3,090; at the quotes' mid they are worth $4,466 (difference $-1,376).

| leg | Alpaca qty | Alpaca value | value at mid | check |
|---|---|---|---|---|
| AAPL261218C00335000 | 1 | $2,805 | $2,883 | ok |
| BA261211C00170000 | 2 | $1,210 | $1,330 | ok |
| BA261218P00160000 | 3 | $681 | $715 | ok |
| BA261218P00170000 | -3 | $-1,815 | $-1,743 | ok |
| BKR261218C00045000 | 6 | $2,820 | $3,054 | ok |
| CAT261218P00500000 | 1 | $282 | $318 | ok |
| CAT261218P00530000 | -1 | $-730 | $-659 | ok |
| SPY261211P00695000 | 1 | $222 | $224 | ok |
| SPY261211P00725000 | -1 | $-470 | $-478 | ok |
| SPY261224P00690000 | 1 | $319 | $319 | ok |
| SPY261224P00720000 | -1 | $-609 | $-612 | ok |
| SYY261218P00072500 | 13 | $715 | $1,034 | Alpaca's price far from the quotes |
| SYY261218P00075000 | -13 | $-2,340 | $-1,918 | Alpaca's price far from the quotes |
