# The test plan: 12 October to 6 December 2026 (8 weeks)

Agreed with the user on 2026-10-11, after the first live week.

## Freeze

The live accounts A, B, C, D, E and F keep their rules for 8 weeks. Allowed: bug fixes (a test first, and a
check that the accounts' decisions do not change unless the bug was in them). Not allowed: new features, new
filters, new data in the live accounts. The learner keeps learning from every closed trade, as designed (that is
part of the rules, not a change).

The finder keeps searching every night (new idea families each evening). It only changes an account through
the path below.

## A strategy that passes all 14 checks

1. Phone alert at once ("a strategy passed all 14 checks").
2. Its one vault test runs in the same nightly job (data from July 2025 never used for any choice); a second
   alert gives the result.
3. If it passes: 6 weeks of forward paper trading on new data only (paper/forward/).
4. Then the user decides whether it takes over account D (today: an early test of a 13/14 candidate).

## Success criteria, set before the results

After 3 months (early January 2027), an account counts as a success only if all of these hold:

- it beats **SPY buy & hold** over the same period on risk-adjusted return (Sharpe), and it beats its random-entry
  twin;
- at least ~100 closed trades (fewer is not enough to tell skill from luck);
- its worst drawdown stays within its backtest's range.

If A, B and C do not meet them: the hourly system is retired and the work goes to the insider strategies (D, E)
and the finder. F is a test of option mechanics, not of an edge: judged on execution (fills, spreads, assignment
handling), not on profit.

F also records the option market once a day from 12 October (data/options/), read-only, as future learner data.
After the freeze (from 7 December), F gets a fifth playbook that aims for profit: systematic SPY put spreads
(paper/research/2026-10-11-account-F-put-selling.md), judged against SPY from then on.

## Real money

Only after a strategy has passed all 14 checks, its vault test and 6 weeks of forward trading, and its live
account meets the criteria above. Then small, with the repository made private first.

## Changes agreed during the freeze

- **2026-10-24 (user's go):** from Monday 26 October, **A trades "insiders + SPY"** (D's insider rule
  `1591c2bcb6`, the money the trades leave idle held in SPY; reports/2026-10-20-insider-spy/) in paper/A2/, and
  **B trades asset-class trend + momentum** (each month the top 3 of 8 asset-class ETFs by 12-month return, only
  those above their 10-month average, else SHY; reports/2026-10-20-trend-momentum/) in paper/B2/. Both start from
  their paper equity at the switch (A $94,600, B $95,110); the hourly positions are sold at Monday's open. The
  hourly books stay as records: paper/ (updated each morning as the learner's research book) and paper/B/ (no
  longer updated). **C is unchanged** until 6 December, as the control for the hourly approach. The 5-minute
  shadow engine follows C only. Same day: **F sells the 9 option legs** Alpaca holds beyond its book (left by
  the order bugs fixed on 22 October), once, from the first run with the market open on 26 October
  (paper/F/config.json "close_leftovers").
- **2026-10-20 (user's go):** F starts the SPY put-spread playbook now instead of 7 December, and its call /
  put-spread playbooks follow account D's insider signals instead of A's (A's signals have no edge); F's long
  puts and bear call spreads pause until a bearish signal passes the finder. E renamed "E – Insider clusters
  (Industrials)"; its rule stays at 3+ insiders (the 2+ version is weaker: 12/14, its edge fades). Accounts A,
  B, C and D are unchanged.
- **2026-10-20 (user's go):** A, B and C send their orders one hour earlier. The paper booked an entry (or a
  signal exit) only once the bar after the signal had closed, so the Alpaca order went out about 80 minutes
  after the paper's price, and overnight signals at 10:20 New York instead of the 9:30 opening auction. Now
  each run also trades the open of the bar forming now (at the last close), so the order goes out at the first
  run after the signal bar (about 20 minutes after it), overnight signals queue for the opening auction. The
  strategies, the learner and the books are unchanged: replays of A on 13 and 20 October give the same
  equity, trades and decisions on every closed bar (reports/2026-10-20-entry-timing/README.md).
