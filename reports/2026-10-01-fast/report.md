# Fast day trading study (5-minute bars) – 2026-10-01

Train (choose): 2025-01-02 → 2026-01-21. Test (untouched): 2026-01-21 → 2026-10-01. Each trade risks 0.2% of equity; stocks flat by 15:55 New York. *Random* = same strategies' exits and number of signals, random timing and side (average of 5). A strategy is only interesting if it beats random in **both** windows, after costs.

| market | strategy | window | return | random | trades/day | hold (min) | win | avg R | fees | max DD |
|---|---|---|---|---|---|---|---|---|---|---|
| stocks | orb15 | train | -17.53% | -35.19% | 8.1 | 76 | 36% | -0.06 | -3.25% | -26.45% |
| stocks | orb15 | test | -7.80% | -31.68% | 8.5 | 78 | 37% | -0.02 | -2.25% | -17.09% |
| stocks | vwap_fade | train | -82.44% | -97.63% | 46.3 | 31 | 41% | -0.12 | -9.08% | -82.53% |
| stocks | vwap_fade | test | -75.88% | -92.41% | 47.1 | 31 | 43% | -0.12 | -6.13% | -76.63% |
| stocks | range_break | train | -45.20% | -55.64% | 13.7 | 29 | 36% | -0.10 | -5.40% | -48.97% |
| stocks | range_break | test | -33.43% | -45.22% | 13.5 | 28 | 36% | -0.09 | -4.20% | -36.08% |
| stocks | rsi2_5m | train | -64.19% | -72.44% | 23.0 | 38 | 44% | -0.09 | -6.45% | -64.61% |
| stocks | rsi2_5m | test | -53.84% | -59.31% | 23.7 | 38 | 44% | -0.10 | -4.48% | -54.46% |
| stocks | all | train | -83.77% | -96.40% | 63.8 | 36 | 41% | -0.10 | -10.55% | -84.21% |
| stocks | all | test | -74.54% | -90.64% | 65.8 | 37 | 42% | -0.10 | -7.57% | -74.66% |
| crypto, taker fee | vwap_fade | train | -100.00% | -100.00% | 95.0 | 27 | 14% | -1.91 | -94.43% | -100.00% |
| crypto, taker fee | vwap_fade | test | -100.00% | -100.00% | 84.8 | 28 | 12% | -1.95 | -97.21% | -100.00% |
| crypto, taker fee | range_break | train | -100.00% | -100.00% | 13.7 | 33 | 19% | -1.86 | -89.61% | -100.00% |
| crypto, taker fee | range_break | test | -100.00% | -100.00% | 13.1 | 32 | 17% | -1.94 | -76.58% | -100.00% |
| crypto, taker fee | rsi2_5m | train | -100.00% | -100.00% | 25.9 | 38 | 14% | -1.49 | -98.83% | -100.00% |
| crypto, taker fee | rsi2_5m | test | -100.00% | -100.00% | 26.4 | 39 | 11% | -1.58 | -89.79% | -100.00% |
| crypto, taker fee | all | train | -100.00% | -100.00% | 122.8 | 30 | 14% | -1.82 | -93.83% | -100.00% |
| crypto, taker fee | all | test | -100.00% | -100.00% | 112.8 | 31 | 12% | -1.84 | -93.68% | -100.00% |
| crypto, maker fee | vwap_fade | train | -100.00% | -100.00% | 93.4 | 28 | 28% | -1.05 | -101.77% | -100.00% |
| crypto, maker fee | vwap_fade | test | -100.00% | -100.00% | 83.5 | 29 | 27% | -1.06 | -110.23% | -100.00% |
| crypto, maker fee | range_break | train | -100.00% | -100.00% | 13.8 | 34 | 28% | -1.06 | -95.16% | -100.00% |
| crypto, maker fee | range_break | test | -99.92% | -99.97% | 13.1 | 34 | 27% | -1.12 | -75.78% | -99.92% |
| crypto, maker fee | rsi2_5m | train | -100.00% | -100.00% | 25.6 | 39 | 27% | -0.83 | -108.11% | -100.00% |
| crypto, maker fee | rsi2_5m | test | -100.00% | -100.00% | 26.1 | 39 | 24% | -0.87 | -95.83% | -100.00% |
| crypto, maker fee | all | train | -100.00% | -100.00% | 122.5 | 30 | 28% | -1.00 | -101.55% | -100.00% |
| crypto, maker fee | all | test | -100.00% | -100.00% | 112.2 | 32 | 26% | -1.01 | -102.06% | -100.00% |

## Day trading or swing: stocks, all 5-minute strategies

| flat at the close | window | return | trades/day | avg R | max DD |
|---|---|---|---|---|---|
| yes | train | -83.77% | 63.8 | -0.10 | -84.21% |
| yes | test | -74.54% | 65.8 | -0.10 | -74.66% |
| no (hold overnight) | train | -89.56% | 64.6 | -0.11 | -89.80% |
| no (hold overnight) | test | -71.09% | 66.6 | -0.10 | -71.21% |

## Day trading or swing: the live hourly system (accounts A/B and C)

Same versions as the live accounts, hourly bars 2023-01 → today; "flat at close" adds the last hour of every session to the blackout (every stock position closed at 15:00 New York).

| version | mode | train CAGR | train Sharpe | test CAGR | test Sharpe | test max DD |
|---|---|---|---|---|---|---|
| A/B: long + trend + blackout + ML | swing (hold overnight) | +0.4% | 0.13 | +21.4% | 1.04 | -14.6% |
| A/B: long + trend + blackout + ML | flat at close | -20.7% | -1.88 | -16.5% | -1.59 | -30.4% |
| C: + intraday | swing (hold overnight) | -2.4% | 0.00 | +26.5% | 1.18 | -17.0% |
| C: + intraday | flat at close | -17.7% | -1.43 | -18.8% | -1.69 | -33.2% |

## Conclusions

- None of the four textbook 5-minute strategies makes money on stocks after costs, in either window. All of them lose less than random entries, so they are not pure noise, but "less bad than random" is not an edge.
- Crypto on 5-minute bars is impossible at Alpaca's fees (0.15-0.25% per side): fees alone take more than the account.
- Forcing every position flat at the close turns the hourly system from positive to strongly negative in both windows: the trades need time (hours to days) to reach their targets. Keep swing trading, with the exits before scheduled events (earnings, Fed, jobs).
