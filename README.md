# tf – a systematic trading research & paper-trading platform

An end-to-end quant pipeline, built and run like a small systematic fund: a strategy **finder** that
searches for trading edges under strict anti-overfitting rules, **machine-learning** models trained
walk-forward, and **six live paper-trading accounts** on [Alpaca](https://alpaca.markets) that execute
automatically every 30 minutes through GitHub Actions — with stops at the broker, reconciliation
checks and phone alerts.

> Paper money only. The goal is to find out, honestly, whether a retail-scale systematic edge exists —
> and to have the infrastructure that would trade it safely if it does.

## What it does

| Part | What | Where |
|---|---|---|
| **Data** | Hourly / 5-min bars (Alpaca), daily S&P 1500 (2016→), SEC Form 4 insider trades (bulk + daily index), SEC 8-K earnings release times, FINRA short-sale volume, news & GDELT tone | `algo/data.py`, `algo/wide.py`, `algo/insider.py`, `algo/news.py` |
| **Backtest engine** | Event-driven portfolio simulator: next-bar fills, ATR stops, OCO targets, trailing stops, real Alpaca fees and slippage, position sizing by risk, gross / open-risk limits | `algo/engine.py`, `algo/portfolio.py` |
| **Strategy finder** | Grid + mutation search over strategy families, scored through **14 gates**; ideas are refined in *campaigns* (each round's best versions are improved, not replaced) | `algo/finder.py`, `algo/finder_families.py` |
| **Machine learning** | Walk-forward meta-labeling learner on a shared pool of every signal's outcome (gradient boosting); cross-sectional stock ranker (ridge / GBM) on the S&P 1500; insider-cluster scorer | `algo/ml.py`, `algo/ranker.py`, `algo/insider_ml.py` |
| **Live paper trading** | Six Alpaca accounts, each locked to its own keys: three hourly ML systems (A/B/C), a slot for a graduated strategy (D), the finder's best candidate on the S&P 1500 (E), and an options book — calls, puts and credit spreads (F) | `algo/paper.py`, `algo/runner.py`, `algo/options.py`, `algo/alpaca.py` |
| **Operations** | GitHub Actions every 30 min, an all-day engine in shadow mode, nightly finder, twice-daily data jobs; reports, dashboard, ntfy phone alerts | `.github/workflows/`, `algo/daily.py`, `algo/dashboard.py` |

## How a strategy earns real (paper) money

Most backtested "edges" are luck found by trying many ideas. The finder is built to reject them:

1. **Locked time splits** – a search period, a validation period, and a **vault** (the most recent
   data) that no search ever loads. A candidate gets one vault test, ever.
2. **14 gates** – at least 100 signals; positive information coefficient (IC) and stable ICIR;
   beats *random entries* on the same assets; **deflated Sharpe ratio ≥ 0.90** (corrected for the
   number of strategies tried — every attempt is counted in a registry); positive and profitable
   after costs in validation; positive in ≥ 55% of months and in every market regime; works on most
   assets / sectors; no decay; its parameter neighbours keep the edge (a plateau, not a spike).
3. **Vault test**, then **6 weeks of forward paper trading** on data that did not exist at search
   time — only then a live paper account.

## Results so far (honest)

- ~900 strategies tried. **None has passed all 14 gates yet.** The best — insider buying clusters
  (3+ insiders buying in the open market within 90 days) in Industrials, held 60 sessions — passes
  13/14 and fails only the deflated-Sharpe test. It trades in account E as a clearly labelled
  early test.
- The original hourly trend rules have **no edge** on a fair test (random stocks, ≈0R per trade);
  crypto lost money after fees and was switched off. Kept running in A/B/C as a live baseline.
- Adding FINRA short-sale data lifted the ML ranker from 8/14 to 10/14 gates: more data helped
  more than more models.

## Engineering practices

- **No look-ahead**, enforced by tests: features use only data published before the decision
  (e.g. short volume and insider filings from the next session; walk-forward refits only on
  outcomes already known).
- **Live decisions are never re-decided**: every ML verdict is stored, so replays can't rewrite
  history when models or data are revised.
- **Broker safety**: stops at the broker for every position, a reconciliation check after every
  run, automatic stop restoration if a run fails, orders never re-sent blindly.
- **Each account can only use its own API keys** (checked against the account number).
- 135+ unit tests (`python -m pytest`).

## Run it

```bash
pip install -r requirements.txt
python -m pytest                       # tests
python -m algo.finder report           # finder leaderboard → paper/finder/report.md
python -m algo.ranker                  # ML ranker walk-forward report
PAPER_ACCOUNT=E python -m algo.runner update --no-fetch   # an account's plan, no orders sent
```

Live trading needs Alpaca paper keys in the environment (`ALPACA_API_KEY_ID`,
`ALPACA_API_SECRET_KEY`); in this repository they live only in GitHub secrets.

## Repository map

```
algo/        the code (engine, finder, ML, accounts, broker adapter, reports)
tests/       unit tests, incl. no-look-ahead tests
paper/       live account state (status.md per account), finder registry & reports, daily reports
.github/     the automation (hourly trading, nightly finder, data jobs)
docs/        the first version of the project: a BTC & gold backtester
```
