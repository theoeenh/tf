# Account F: selling insurance (put writing) on SPY – first backtest, 11 October 2026

Question (user's idea #3 for F): does selling S&P 500 puts pay, and is it better to sell only when insurance is
"expensive"?

Data: Cboe's own indexes, real option prices: **PUT** (sells a one-month at-the-money S&P 500 put every month,
cash in T-bills), SPX, VIX (30-day implied volatility), VIX3M (93-day). Daily, 2010 to 9 Oct 2026 (VIX3M starts
Sept 2009; a first run from 2007 looked better only because the filter was "out" in 2008 for lack of data).
Rules chosen on 2010-2018, checked on 2019-2026. "In" = holding PUT's daily return, "out" = cash at 0%.

| | 2010-2018 Sharpe | CAGR | max DD | 2019-2026 Sharpe | CAGR | max DD |
|---|---|---|---|---|---|---|
| S&P 500 (price only) | 0.66 | +9.2% | -20% | 0.85 | +15.8% | -34% |
| **PUT, always selling** | **0.67** | +6.6% | -16% | **0.79** | +10.2% | -29% |
| PUT when VIX > 20-day realised vol + 4 ("expensive") | 0.50 | +3.9% | -13% | 0.99 | +9.7% | -13% |
| PUT when VIX > its 1-year median ("high") | 0.57 | +4.8% | -15% | 0.43 | +4.9% | -29% |
| PUT when VIX < VIX3M (calm market, "contango") | 0.76 | +5.6% | -12% | 1.20 | +10.1% | -18% |
| same, with 0.3% cost per switch (~11 a year) | 0.20 | +1.2% | -16% | 0.82 | +6.7% | -22% |
| same, switch only after 2 days (~5 a year) | 0.31 | +2.2% | -18% | 0.99 | +8.4% | -20% |

What it says:

1. **Selling puts is roughly "owning the market with less swing"**: about the same Sharpe as the S&P 500, two
   thirds of its volatility, less return. The insurance premium is real, but on this data it is not an edge over
   simply holding SPY risk-adjusted (the plan's success test).
2. **"Sell when insurance is expensive" does not work in its plain form**: VIX high (vs its own past) is worse in
   both periods; VIX vs realised volatility helps in one period and hurts in the other (luck).
3. The only filter that helped in both periods is the **calm-market one (VIX below VIX3M)**, and it loses its
   advantage once realistic switching costs are counted.
4. F trades defined-risk spreads, not cash-secured at-the-money puts: the protective put costs some of the premium,
   so a spread should do somewhat worse than PUT. Paper fills at Alpaca's indicative prices flatter it too.

Plan (after the freeze, from 7 December): a fifth F playbook, `spy_put_spread`, always on, small: sell a SPY put
spread 30-45 days out (short ~0.25 delta, long ~0.10), take profit at 50% of the credit, close at 21 days, at most
~3% of F's equity at risk each, one new spread a week. Judged against SPY like the other accounts. Any timing filter
(calm market, skew, term structure) is tested first on the option data F records from 12 October
(data/options/daily.csv), not on VIX alone.

Reproduce: Cboe CSVs from cdn.cboe.com/api/global/us_indices/daily_prices/{PUT,SPX,VIX,VIX3M}_History.csv.
