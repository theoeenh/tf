"""Research: does waiting after an hourly signal give a cheaper entry?
For every signal onset of the three live hourly strategies, compare the price at the bar close
(what the paper books assume) with the price 5..120 minutes later (5-minute bars), and test limit
orders placed k ATR below. Units: R = stop distance (stop_atr x ATR)."""
import sys
sys.path.insert(0, "/home/user/tf")
import numpy as np, pandas as pd
from algo.strategies import STRATEGIES
from algo.indicators import atr
from algo.system import SLEEVE_RULES

ASSETS = "AAPL AMD AMZN AVGO BTC COIN ETH GOLD GOOGL IWM JPM META MSFT NFLX NVDA QQQ SILVER SOL TLT TSLA USO XOM".split()
DELAYS = [1, 2, 4, 6, 12, 24]          # in 5-minute bars: 5, 10, 20, 30, 60, 120 min
HORIZON = {"1d": 78, "5d": 390}        # 5m bars for stocks; crypto scaled below
rows = []
for a in ASSETS:
    h = pd.read_csv(f"/home/user/tf/data/{a}_1h_alpaca.csv", index_col=0, parse_dates=True)
    m = pd.read_csv(f"/home/user/tf/data/{a}_5m_alpaca.csv", index_col=0, parse_dates=True)
    crypto = a in ("BTC", "ETH", "SOL")
    scale = 288 / 78 if crypto else 1
    A = atr(h, 14)
    mt = m.index.values
    for name, fn in STRATEGIES.items():
        s = fn(h)
        on = s[(s != 0) & (s.shift(1) == 0)]
        R_mult = SLEEVE_RULES[name].stop_atr
        for t, d in on.items():
            T = t + pd.Timedelta(hours=1)
            if T < m.index[0]:
                continue
            i = np.searchsorted(mt, np.datetime64(T))
            hmax = int(HORIZON["5d"] * scale)
            if i + hmax >= len(m):
                continue
            atr_t = A.loc[t]
            if not np.isfinite(atr_t) or atr_t <= 0:
                continue
            R = R_mult * atr_t
            p0 = m["Open"].iat[i]
            r = {"asset": a, "strat": name, "dir": d, "t": T, "R": R, "atr": atr_t, "p0": p0, "crypto": crypto}
            for k in DELAYS:
                r[f"d{k*5}"] = d * (m["Open"].iat[i + k] - p0) / R
            for hn, hb in HORIZON.items():
                r[f"fwd{hn}"] = d * (m["Close"].iat[i + int(hb * scale)] - p0) / R
            # limit k*ATR better than p0, valid 12 bars (1h) or 78 bars (1 day)
            for kk in (0.1, 0.25, 0.5):
                lim = p0 - d * kk * atr_t
                for win in (12, 78):
                    w = m.iloc[i:i + int(win * scale)]
                    hit = (w["Low"] <= lim).any() if d > 0 else (w["High"] >= lim).any()
                    r[f"fill_{kk}_{win}"] = bool(hit)
            rows.append(r)
df = pd.DataFrame(rows)
df.to_pickle("/tmp/entry_timing.pkl")
print(len(df), "signals")
cols = [f"d{k*5}" for k in DELAYS]
def summ(g):
    return pd.Series({**{c: g[c].mean() for c in cols}, "n": len(g), "fwd1d": g["fwd1d"].mean(), "fwd5d": g["fwd5d"].mean()})
pd.set_option("display.width", 200, "display.precision", 3)
print("\nDrift after the bar close (R, + = price moved our way = waiting costs; - = later is cheaper)")
print(df.groupby("strat").apply(summ))
print(df.groupby(["strat", "crypto"]).apply(summ))
print("all", summ(df).round(3).to_dict())
# t-stats of 20-min drift
for sname, g in df.groupby("strat"):
    x = g["d20"]; print(sname, "d20 t-stat", round(x.mean() / x.std() * np.sqrt(len(x)), 2), "d60 t", round(g["d60"].mean() / g["d60"].std() * np.sqrt(len(g)), 2))
print("\nLimit orders: fill rate, and value vs market at p0 (R per signal, 1-day and 5-day horizon)")
for kk in (0.1, 0.25, 0.5):
    for win in (12, 78):
        f = df[f"fill_{kk}_{win}"]
        gain = kk / (df["R"] / df["atr"])        # extra R when filled
        for hn in ("fwd1d", "fwd5d"):
            limit_val = np.where(f, df[hn] + gain, 0.0)
            print(f"k={kk} win={win:>2} fill={f.mean():.0%} {hn}: market {df[hn].mean():+.3f}R  limit {limit_val.mean():+.3f}R  "
                  f"missed trades' market result {df.loc[~f, hn].mean():+.3f}R  filled trades' {df.loc[f, hn].mean():+.3f}R")
