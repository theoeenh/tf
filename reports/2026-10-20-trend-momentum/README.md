# Trend following + momentum across asset classes (market data only) – 2026-10-20

Question (user): a strategy for account B that uses market data only (no insider data): trend following
combined with momentum.

What was already tested and failed: trend and momentum **on single stocks and hourly bars** (donchian
breakouts 7/14 gates, 12-1 momentum on the S&P 500 6/14, cross-asset hourly momentum 6/14, 52-week highs
4/14). What had not been tested: the classic version **across asset classes, monthly** (Faber 2007,
"time-series momentum" Moskowitz-Ooi-Pedersen 2012, a century of evidence in Hurst-Ooi-Pedersen 2017).

Data: Yahoo daily adjusted closes of 9 ETFs: SPY (US stocks), EFA (developed ex-US), EEM (emerging), TLT
(long Treasuries), IEF (7-10y Treasuries), GLD (gold), DBC (commodities), VNQ (US real estate), SHY (cash
stand-in). March 2007 – 20 Oct 2026 (DBC starts 2006). Decided at each month's last close, held from the
next day; 5 bp cost per unit traded. Textbook rules, nothing tuned: 10-month average, 12-month momentum,
top 3. Note: Faber published in 2006-07, so the whole test period is after publication.

| strategy | 2007-2016 CAGR / Sharpe / max DD | 2017-2026 | whole period |
|---|---|---|---|
| SPY buy & hold | +7.0% / 0.43 / -55% | +15.3% / 0.88 / -34% | +11.1% / 0.63 / -55% |
| 60/40 (SPY/IEF) | +7.1% / 0.65 / -31% | +9.8% / 0.91 / -21% | +8.4% / 0.78 / -31% |
| 8 asset classes, equal weight | +5.1% / 0.42 / -37% | +8.5% / 0.84 / -20% | +6.8% / 0.59 / -37% |
| trend: each class only above its 10-month average (else cash) | +4.8% / 0.62 / -11% | +6.6% / 1.00 / -10% | +5.7% / 0.78 / -11% |
| **trend + momentum: top 3 by 12-month return, if above average** | +6.3% / 0.52 / -16% | +11.3% / 0.98 / -17% | +8.7% / 0.73 / -17% |
| trend + momentum: top 3 by 1/3/6/12-month average return, if above average | +9.4% / 0.70 / -19% | +13.2% / 1.08 / -13% | +11.3% / 0.87 / -19% |
| dual momentum (SPY vs EFA, else bonds) | +5.9% / 0.46 / -26% | +7.5% / 0.52 / -34% | +6.7% / 0.49 / -34% |

Calendar years, SPY vs trend + momentum (12-month): 2008 -37% vs +12%, 2018 -5% vs -7%, 2020 +18% vs +12%,
2022 -18% vs -9%, 2025 +18% vs +31%.

What it says:
1. Trend + momentum across asset classes **beats SPY risk-adjusted in both halves** (Sharpe 0.52-0.70 vs
   0.43, then 0.98-1.08 vs 0.88), with a worst fall of 13-19% instead of 34-55%. That is the plan's success
   test (beat SPY risk-adjusted).
2. It is not more return in a bull market: 2017-2026 it made 11-13% a year vs SPY's 15%. Its value is
   avoiding the big falls (2008, 2022), so it lags in years like 2017-2021.
3. Five versions were tried (all textbook); the best one (1/3/6/12 average) was not chosen in advance, so
   the pre-committed version is the plain 12-month one. Both beat SPY risk-adjusted; neither was tuned.
4. It trades once a month, 9 liquid ETFs: cheap and simple on Alpaca. An 8-week paper test only checks the
   mechanics (2 rebalances); the evidence is the 20 years above and the literature.

What the rules would hold on 20 October 2026 (12-month version): SPY, commodities (DBC), cash; (average
version): EFA, SPY, DBC.

Reproduce: download the 9 ETFs' adjusted closes to etf_daily.csv (yfinance), then
`python reports/2026-10-20-trend-momentum/trend_mom.py`.
