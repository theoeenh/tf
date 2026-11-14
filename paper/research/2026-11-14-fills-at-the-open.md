# What buying at the open costs at Alpaca (14 November 2026)

Measured on all 30 stock buys of account A since 23 October. **Nothing is changed yet** (see the end).

## Summary

- **A buy costs 0.054R on average against the opening price the paper account books** (62 bp of the
  price; 1.63R over 30 buys). The backtests assume 5 bp for S&P 500 stocks, 8 bp for mid caps and 15 bp
  for small caps.
- **The cause is the first minute of trading, not Alpaca's simulator.** The orders are market orders queued
  before the open. Alpaca fills them 30 to 190 seconds after 9:30, at the asking price of the whole market
  (not of one exchange). In the first minute that quote is very wide for less traded stocks: 6.0% wide for
  LKFN, 2.5% for IOSP, so the fill is far above the opening price.
- **Twenty minutes later the same buys would have cost 0.017R** (19 bp), a third as much. The quote is 21 bp
  wide at the median by then, against 43 bp five minutes after the open.

## The numbers

Each buy: Alpaca's fill against the day's official opening price, in R (the trade's risk: 3 ATR), and what
buying at the asking price a few minutes later would have cost.

| when | average | in bp | median | worst | total over 30 buys |
|---|---|---|---|---|---|
| as filled (queued before the open) | -0.054R | 62 | -0.034R | -0.41R | -1.63R |
| 5 minutes after the open | -0.030R | 31 | -0.021R | -0.26R | -0.87R |
| 10 minutes after | -0.017R | 23 | -0.017R | -0.19R | -0.52R |
| 20 minutes after | -0.017R | 19 | -0.015R | -0.19R | -0.50R |

- The five worst fills: LKFN -0.41R, TBBK -0.21R, IOSP -0.15R, THRM -0.13R, FFIN -0.11R. All small or
  mid-size stocks.
- Liquid stocks lose nothing by waiting (AAPL: -0.08R as filled, -0.02R twenty minutes later).
- 30 buys is a small sample, and waiting adds noise: the price moves in twenty minutes (COHR fell 4%, CAT
  fell 2.4%: both would have been bought cheaper, by luck). The average of that noise should be zero; the
  wide first quotes are a cost every time.

## Why the paper account does not show it

The paper account books every entry at the official opening price plus the assumed slippage, as the
backtests do. The opening price is set by the opening auction. Orders sent into that auction would get
exactly that price, but Alpaca's paper simulator let such orders expire unfilled on 26 October, so the
accounts use plain market orders since then.

## Proposed change (not made)

Send stock buys 15 to 20 minutes after the open (the 9:50 New York run) instead of queueing them before
it. Sales and stops unchanged.

- Expected gain: about 0.04R a buy at Alpaca. Nothing changes in the paper record.
- **Why it is not done today:** it changes when live orders are sent, and about ten tests describe today's
  queueing before the open. It deserves its own careful change with those tests rewritten first, not a
  late addition to a day of other changes. It can be made before Monday's open or at the 6 December
  review: the user's call.
