# Account A idea: insider buying + idle cash in SPY – 2026-10-20

Question: if A trades account D's insider rule (`1591c2bcb6`, insider_low_short: an insider buys, short
sellers are not against the stock; S&P 1500, 3 ATR trailing stop, 60 sessions, 0.4% risk a trade) and keeps
the cash the trades do not use in SPY, does it beat simply holding SPY?

Method: the finder's own engine, costs and sizing; daily. The SPY part is 1 minus the trades' gross exposure
(none when the trades use all the money), 1 bp per unit of SPY traded. Random twins: the same exits and the
same number of entries at random dates (average of 5). Periods: the finder's search (2017-2022) and
validation (2023 - June 2025). The vault (from July 2025) stays sealed.

| 2017-2022 | CAGR | volatility | Sharpe | max drawdown |
|---|---|---|---|---|
| SPY | +11.2% | 19.9% | 0.63 | -34% |
| insider trades alone (cash idle) | +10.2% | 18.8% | 0.61 | -32% |
| **insider trades + SPY** | **+15.3%** | 23.6% | **0.72** | -38% |
| random entries alone | +4.7% | 16.0% | 0.36 | -25% |
| random entries + SPY | +8.1% | 22.0% | 0.46 | -35% |

| 2023 - June 2025 | CAGR | volatility | Sharpe | max drawdown |
|---|---|---|---|---|
| SPY | +23.3% | 16.1% | 1.38 | -19% |
| insider trades alone | +15.5% | 16.4% | 0.96 | -13% |
| **insider trades + SPY** | **+27.1%** | 19.6% | **1.32** | -16% |
| random entries alone | +5.8% | 16.9% | 0.40 | -18% |
| random entries + SPY | +16.3% | 20.4% | 0.84 | -20% |

1,396 trades in 2017-2022, 545 in 2023-25H1; the trades use on average about all the money (gross 1.0-1.07),
so SPY fills the gaps (build-up, quiet months).

What it says:
1. **The insider selection is real**: the same exits with random entries make 5-6% a year; the insider
   entries 10-15%. That is the edge the finder measures (13/14 gates).
2. **Alone it does not beat SPY**: about SPY's Sharpe in 2017-2022, below it in 2023-25 (a market led by the
   largest companies, which equal-risk trades in mid and small caps miss).
3. **With the idle cash in SPY it makes about 4% a year more than SPY in both periods**, partly because it is
   more invested than SPY (about 1.2x on average). Per unit of risk: better in 2017-2022 (0.72 vs 0.63),
   about equal in 2023-25 (1.32 vs 1.38). A small, honest "SPY plus a little", not a clear win.

Reproduce: `python reports/2026-10-20-insider-spy/insider_spy.py` (needs the wide data: python -m algo.wide).
