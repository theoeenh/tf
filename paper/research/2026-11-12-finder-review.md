# Finder review – 12 November 2026

The user's go, 12 November: "Fix both please." Two faults in how the strategy finder judged its
candidates. This note fixes the method **before** any strategy is scored with it, so the method cannot
be bent towards a result. The numbers the new method gives are added at the end, as they come.

## What was wrong

1. **Today's index members were tested on the past.** Every S&P 1500 backtest (2017 to mid-2025) ran on
   the companies that are in the S&P 500, 400 and 600 *today*.
   - Companies that went bankrupt, were bought or shrank out of the indexes were missing.
   - Companies that joined later, after rising, were traded years before they qualified.
   - Both flatter a strategy that buys stocks. "Buy after a big fall" is flattered most: the stocks that
     fell and never came back are exactly the missing ones. That is account C's rule and the sector
     washouts.
   - The comparison with random entries on the same stocks removed only part of it.
2. **The luck check could not be passed.** The check (deflated Sharpe) asks whether a strategy's Sharpe is
   above the best score that all the tries would reach by chance.
   - It counted each of the 6,620 tries as independent. Most are the same few ideas with another exit,
     parameter or sector: 86 families, and thousands of versions that rise and fall together.
   - Every new idea tested raised the bar for all: the best score fell from 0.705 to 0.642 in a week.
   - It also measured the raw Sharpe. A strategy that only buys stocks earns something in a rising
     market with no skill, so being invested counted as skill. The two errors pull in opposite
     directions, so the old score was neither clearly too strict nor clearly too lenient.

## Fix 1: the members of each day

- **Source:** the three Wikipedia list pages (S&P 500, 400, 600) as they stood at the start of every
  month, from the pages' public history. One snapshot a month from December 2015.
- **Table:** `data/wide/members_history.csv`: symbol, index, start, end, sector. One row per unbroken stay.
  - A stock counts from the first monthly list that shows it, never before (so up to a month late).
  - It stops counting at the first monthly list without it.
  - From now on, each night's lists extend the table. The past never changes.
- **A signal counts only on days the stock is a member of the strategy's segment.**
- **Prices:** every stock that was ever a member, from Alpaca (delisted stocks included).
  - Each is kept from 550 days before it first joined (history for the indicators) until it leaves, plus
    90 sessions so an open trade can run to its exit.
  - A stock that stops trading ends there. A ticker later reused by another company is not read.
- **A stock that vanishes:** the engine needs bars to close a trade, so a vanished stock gets flat closing
  bars, which no strategy can read as prices.
  - Ends at a steady price: bought out, paid at its last price.
  - Ends under $1, or after a collapse into the end (down 40% or more in its last 20 sessions and 70% or
    more in a year): failed, booked as worthless. (SVB was halted at $106 the day after closing at $268,
    down from $500 a year before; its holders got nothing.)
  - A stock that only left the indexes and still trades is never written off: a trade still open after
    90 sessions is closed at its last price.
- **Insider filings and short-selling data** are downloaded again for every member ever.

Known limits, stated now:

- **Small caps enter in September 2018.** Wikipedia's S&P 600 list only exists from 27 August 2018.
  Before that, the S&P 600 is not in the universe at all: the "S&P 1500" is the S&P 500 and 400 until
  then. Nothing is guessed.
- Until 2020 the small-cap page listed the S&P 400 and 600 together; the 600 is that list minus the 400
  of the same month.
- Monthly lists: a change inside a month is seen at the next month's start.
- A renamed company is two stocks, one per ticker (Facebook's FB until June 2022, META after).
- Earnings dates and company fundamentals exist only for today's companies. The few families that need
  them still cannot signal on a company that left.
- Wikipedia is edited by hand. A list that is far too short or long is skipped, and a stock missing from
  one list between two that show it stays a member.

## Fix 2: a measured luck bar

Same formula, same pass mark (deflated Sharpe of 0.90 or more). Two inputs change.

1. **What is judged: the part of the returns the strategy's own universe does not explain.**
   - Benchmark: the equal-weight daily return of the stocks the strategy may trade that day.
   - The strategy's daily returns minus beta times that benchmark, summed by week.
   - These weekly returns are stored for every try (`paper/finder/returns/`).
2. **The bar: measured, not assumed.**
   - History is replayed 1,000 times with every try's average set to zero (no skill anywhere).
   - The weeks stay together across tries, so tries that move together still move together. Blocks of
     4 weeks on average keep any short-term momentum.
   - Each replay gives the best t-statistic among all tries. The average of those is the bar.
   - Every try counts, the old hourly ones too. A new idea raises the bar. A near-copy of an old try
     raises it by almost nothing. *(Amended after the first run to "every try that could pass": see
     "Two corrections" at the end.)*
   - A try whose returns are not stored counts as one more fully independent try, and cannot pass.

Set in advance and not to be tuned on results: weekly returns, the benchmark above, 1,000 replays,
4-week blocks, a fixed random seed, the 0.90 pass mark.

The report also says how many independent tries would set the same bar. That number is a translation
for the reader, not an input.

## What does not change

- The 14 checks, their order and their pass marks.
- The sealed vault (data from July 2025) and its one test per strategy.
- Six weeks of forward paper trading after a vault pass.
- The trading accounts. A, C, D and E trade today's index members, as before: their code path is
  untouched and tested to be so.

## Two process changes, to be confirmed by the user

- **Vault tests are on hold** (`paper/finder/hold.json`) until the user has seen the re-scored registry.
  The vault can be used once per strategy. If thirty near-identical versions of one idea pass at once,
  testing all thirty would spend it thirty times on one idea.
- **No new strategy families during the review.** Each one raises the bar, and the old ones must be
  re-scored first.

## Every old try is scored again

All 6,620 tries are scored again from scratch on the new data (`python -m algo.finder rescore`, run on
GitHub in 17 slices). Nothing new is tried. Old and new numbers of every try are kept side by side in
`paper/finder/rescore_compare.csv`.

What I expect, written before the run: fewer and weaker results for "buy after a fall" ideas, and no
clear guess for the luck check, because the two corrections pull in opposite directions.

## Results

### First check, before the full run: six price-only strategies on real prices (12 November)

Run here on the search and validation years only (the vault stays sealed). The research universe now
holds 2,378 companies that were members at some point since December 2015, against 1,502 today: **876
were missing from the old tests.** 623 of them left or stopped trading before July 2025, and 27 of those are
booked as total losses (SVB, First Republic, Signature Bank, J.C. Penney, Frontier, Dean Foods, ...).

| strategy (search years 2017-2022) | stability (ICIR) old → new | average R old → new (random entries) | return old → new | t-statistic without the market |
|---|---|---|---|---|
| sector_washout_calm (the best campaign) | +1.03 → +0.41 | +0.28 → +0.11 (+0.08) | +56% → +45% | 0.29 |
| sector_washout_calmest | +0.91 → +0.38 | +0.26 → +0.11 (+0.07) | +46% → +38% | 0.25 |
| sector_washout_leaders | +0.94 → +0.29 | +0.24 → +0.14 (+0.09) | +47% → +38% | 0.10 |
| momentum_12_1 | +0.04 → +0.01 | +0.06 → +0.03 (+0.02) | +28% → +9% | 0.26 |
| high_52w | -0.29 → -0.32 | +0.03 → +0.01 (+0.01) | +36% → +13% | -0.02 |
| reversal_5d | -0.05 → -0.13 | +0.02 → -0.01 (-0.01) | +15% → -6% | -0.88 |

- Every one of the six is weaker on the members of each day. The sector washouts lose more than half
  of their stability score and most of their lead over random entries in the search years.
- Their raw Sharpe was mostly market exposure: once the return of the stocks they may trade is taken
  out, the t-statistics are between -0.9 and +0.3. A t-statistic near 3 is what the luck check asks.
- The insider strategies could not be checked here (their data is only on GitHub). The full run covers
  them.

### Full run: every try scored again (12 November, finished 21:13 UTC)

**The verdict: no strategy clears the luck check, and none is close.**

- **6,516 of 6,528 tries were scored again.** The old registry counted 6,728, but 200 rows were the same
  strategy listed twice. 12 tries (all insider_dip) could not be scored again and keep their old row;
  they cannot pass.
- **The bar is a t-statistic of 3.28.** 4,659 tries have the 100 signals a strategy needs to be judged at
  all; replaying history with no skill in any of them, the luckiest reaches 3.28 on average. That is the
  bar about 1,100 independent tries would set.
- **The best strategy that could pass has 3.05** (a calm_union version; deflated Sharpe 0.37, pass mark
  0.90). To pass, a strategy needs about 4.6.
- **Taken together, the 5,915 S&P strategies look like chance.** Once the return of the stocks each may
  trade is taken out, their t-statistics average -0.2 with a spread of 1.0: what thousands of strategies
  with no skill would show. The best single one is at 3.1.
- 405 strategies pass 13 of the 14 checks (370 before; only 170 are the same ones). All 405 fail the luck
  check and nothing else.

**What the real universe changed (S&P strategies, medians of all tries):**

| measure | old | new | share of tries that got worse |
|---|---|---|---|
| average R a trade, search years | +0.11 | +0.09 | 67% |
| average R a trade, validation years | +0.12 | +0.08 | 70% |
| return, validation years | +3.3% | +1.6% | 68% |
| average R minus random entries, search | +0.05 | +0.05 | 48% |
| stability (ICIR), search | +0.24 | +0.26 | 38% |

- Returns and average R fell for two tries in three. The lead over random entries on the same stocks did
  not: that comparison had been absorbing much of the bias, as the old code comment claimed.
- **The sector washouts lost the most:** median stability +0.58 → +0.38, lead over random entries
  +0.27R → +0.20R. The best campaign (sector_washout_calm) went from +1.03 to +0.41.
- **The insider ideas kept their per-trade lead over random entries** (+0.04R → +0.05R, median of 5,001
  tries) but their returns shrank.

**The rules the accounts trade:**

| rule | checks passed | validation average R | validation return | t-statistic without the market | market exposure (beta) |
|---|---|---|---|---|---|
| C: insiders under water `3ce4f83a88` | 13 → 13 | +0.38 → +0.20 | +43% → +23% | 0.69 | 1.02 |
| A and D: insider + low short `1591c2bcb6` | 13 → 12 | +0.20 → +0.10 | +43% → +16% | -0.07 | 0.63 |
| E: insider clusters, Industrials `5aca4825d9` | 13 → 12 | +0.44 → +0.25 | +8.5% → +5.2% | -0.04 | 0.12 |

- All three still beat random entries per trade, in search and validation.
- Their validation returns roughly halve on the real universe.
- **Once market exposure is taken out, none shows a return of its own in 2017-2022** (t-statistics between
  -0.1 and +0.7). The backtests that put them in the accounts were flattered by the missing companies and
  by being invested in a rising market.
- A and D's rule now also fails "positive in every market regime"; E's fails "positive in 55% of months".

**What this does and does not say:**

- It does not say insider buying carries no information: the per-trade lead over random entries is
  still there, for thousands of versions.
- It says the lead is too small, at the sizes these rules trade, to stand out from luck in a portfolio's
  weekly returns over six years. The live accounts are the test that remains.

### Two corrections made after the first run, and why

Written here because they were made after seeing a result. Neither changes the verdict: under every
version below, the best strategy is far from passing.

1. **The first version of the measured bar was broken.** It measured each replay's average against that
   replay's own spread. A strategy whose variance sits in a few extreme weeks has almost no spread in a
   replay that misses them, and the ratio explodes: on the real registry the bar came out at 100. No
   number of tries can explain that. The fix is the standard method (Hansen 2005): each try's replayed
   average is measured against the try's own spread over the whole history. A test now fails on the old
   version (bar 33 on a small made-up case, where 4 is the most that makes sense).
2. **"Every try counts" became "every try that could pass counts".** With the fix above and all 6,516
   tries, the bar is 3.54. The tries that set it were mostly strategies with 1 to 30 trades: one lucky
   week counted several times in a replay looks like a t-statistic of 5, which no strategy can show in
   real data. Such tries fail the first check (at least 100 signals) whatever they earn, and that check
   depends on how often a rule trades, not on how it did. Leaving them out gives 3.28. The 3.54 is kept
   here so the difference is visible.

One claim of mine did not hold up. I said the old check could not be passed mainly because it counted
every try as independent. Measured, the tries' similarity lowers the bar only a little: 3.28 against
the 3.76 that 6,500 independent tries would set. The larger fault of the old check was the other one:
it counted market exposure as skill, and so made the best strategies look closer to passing than they
are (the best old score was 0.64; the same strategy now scores 0.18).
