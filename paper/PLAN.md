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
