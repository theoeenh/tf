# Entry timing: is "later cheaper"? (2026-10-20)

Question: Alpaca fills of account A were on average 0.135R better than the paper book's entry prices
(40 entries, 29 Sep – 16 Oct). Is the system buying too early, and should it wait or use limit orders?

## 1. Where the live gap comes from

Each of the 40 entries split into three parts (1-minute SIP bars; R = the trade's stop distance;
negative = better for us):

| part | mean |
|---|---|
| paper entry vs the market price at the paper's entry time (the paper's own slippage cost) | +0.021R |
| market move between the paper's entry time and the Alpaca fill | **-0.118R** |
| Alpaca fill vs the market price at that minute | +0.005R |
| total | -0.135R |

By strategy, total: donchian_trend -0.23R, squeeze_breakout -0.18R, rsi2_reversion -0.08R.

**The fills come 80–85 minutes after the paper's entry price, not 20–25.** The paper book enters at
the open of the bar after the signal (as the backtest does), but the replay (`algo/paper.py`, only
complete bars) can only book that entry once that next bar is complete itself. So orders.json, and the
Alpaca order, appear one bar late: signal on the 9:30–10:00 bar → paper entry price at 10:00 → order
sent by the 11:20 run. Overnight signals (last bar of the day) are sent at 10:20 New York, not to the
9:30 opening auction. Execution itself costs nothing measurable (+0.005R).

## 2. Does waiting pay on average? (history)

All signal onsets of the three live hourly strategies on the 22 assets with 5-minute data
(Jan 2025 – Sep 2026, 12,482 signals): price change after the signal bar's close, in R.

| delay | 5 min | 20 min | 60 min | 120 min |
|---|---|---|---|---|
| all | +0.002 | +0.002 | +0.006 | +0.004 |
| stocks only | | 0.000 | +0.002 | -0.002 |

t-statistics below 1.7 everywhere. Waiting changes nothing on average (standard deviation of the
2-hour move: 0.5R per trade, so 40 correlated trades in one falling tech market can easily show -0.12R).

## 3. Limit orders below the price?

Limit k×ATR better than the signal price, valid 1 hour or 1 day:

| k | fill rate (1 h / 1 day) | value vs market, 5-day horizon (1 h) | missed trades' result |
|---|---|---|---|
| 0.10 | 89% / 96% | +0.023R vs +0.031R | +0.39R |
| 0.25 | 75% / 91% | +0.019R vs +0.031R | +0.34R |
| 0.50 | 54% / 82% | +0.009R vs +0.031R | +0.27R |

The trades a limit misses are the ones that run away at once (the winners). Limits are never better
than buying at market.

## Conclusion

- Not the learner (it only says take / skip) and not "buying too early": on average the timing doesn't
  matter. The 3 weeks' gain is market luck from buying 1 hour late in a falling tape.
- The real issue is the one-bar delay between the paper book and the orders. Fix (proposal): send the
  order at the first run after the signal bar, as designed; overnight signals would then go to the
  opening auction. Expected return effect: none on average; benefit: paper and Alpaca agree to ~20 minutes.

Reproduce: `python reports/2026-10-20-entry-timing/entry_timing.py` (needs data/*_5m_alpaca.csv).

## Follow-up (same evening)

- **A model that learns when to enter?** Trained on 2025's signals (7,257) to predict whether waiting 20 or 60
  minutes gives a better price (features: the last 1/5/20 bars' move, distance from the 20-bar average, RSI-2,
  volatility, bar range, volume, hour, weekday, QQQ's last 5 bars, strategy), tested on 2026's (5,225):
  AUC 0.50-0.52, a coin flip; following it loses 0.001-0.008R per signal. The next hour's price is not
  predictable from what the system sees (15-minute-late data, hourly bars).
- **Overnight signals:** entering at the open vs an hour later: +0.013R for the open (1,011 signals), vs
  +0.001R intraday. Small, but in the open's favour.
- **The fix (user's go):** orders now go out at the first run after the signal bar; see paper/PLAN.md.
