"""Asset-class trend following + momentum, textbook rules (no tuning), monthly. Market data only."""
import numpy as np, pandas as pd
px = pd.read_csv("etf_daily.csv", index_col=0, parse_dates=True)
px = px[px.index >= "2006-02-06"].ffill()
RISKY = ["SPY", "EFA", "EEM", "TLT", "IEF", "GLD", "DBC", "VNQ"]
ret = px.pct_change().fillna(0)
me = px.resample("ME").last()                        # month-end closes
sma10 = me.rolling(10).mean()
mom12 = me / me.shift(12) - 1
mom_avg = sum(me / me.shift(k) - 1 for k in (1, 3, 6, 12)) / 4
COST = 0.0005                                        # 5 bp per unit traded

def run(weights_me: pd.DataFrame) -> pd.Series:
    w = weights_me.reindex(px.index, method="ffill").shift(1).fillna(0)   # decided at the close, held from the next day
    w = w[w.index >= "2007-03-01"]
    turn = w.diff().abs().sum(axis=1).fillna(0)
    return (w * ret.reindex(w.index)).sum(axis=1) - turn * COST

def W(fn):
    rows = {}
    for t in me.index:
        rows[t] = fn(t)
    return pd.DataFrame(rows).T.fillna(0)

strats = {
    "SPY buy & hold": W(lambda t: {"SPY": 1.0}),
    "60/40 (SPY/IEF)": W(lambda t: {"SPY": 0.6, "IEF": 0.4}),
    "8 asset classes, equal": W(lambda t: {a: 1 / 8 for a in RISKY}),
    "trend: each class only above its 10-month average": W(lambda t: {**{a: 1 / 8 for a in RISKY if me.at[t, a] > sma10.at[t, a]},
                                                                  "SHY": sum(1 / 8 for a in RISKY if not me.at[t, a] > sma10.at[t, a])}),
    "trend + momentum: top 3 by 12-month return, if above average": None,
    "trend + momentum: top 3 by 1/3/6/12-month avg, if above average": None,
    "dual momentum (SPY vs EFA, else bonds)": None,
}
def topk(t, score, k=3):
    s = score.loc[t, RISKY].dropna().sort_values(ascending=False)[:k]
    w = {}
    for a in s.index:
        if me.at[t, a] > sma10.at[t, a]:
            w[a] = w.get(a, 0) + 1 / k
        else:
            w["SHY"] = w.get("SHY", 0) + 1 / k
    return w
strats["trend + momentum: top 3 by 12-month return, if above average"] = W(lambda t: topk(t, mom12))
strats["trend + momentum: top 3 by 1/3/6/12-month avg, if above average"] = W(lambda t: topk(t, mom_avg))
def gem(t):
    if pd.isna(mom12.at[t, "SPY"]): return {"SPY": 1.0}
    best = "SPY" if mom12.at[t, "SPY"] >= mom12.at[t, "EFA"] else "EFA"
    return {best: 1.0} if mom12.at[t, "SPY"] > mom12.at[t, "SHY"] else {"IEF": 1.0}
strats["dual momentum (SPY vs EFA, else bonds)"] = W(gem)

def stats(r):
    eq = (1 + r).cumprod(); yrs = len(r) / 252
    return (eq.iloc[-1] ** (1 / yrs) - 1, r.std() * np.sqrt(252), r.mean() / r.std() * np.sqrt(252), (eq / eq.cummax() - 1).min())
PER = {"2007-2016": ("2007-03-01", "2016-12-31"), "2017-2026": ("2017-01-01", "2026-12-31"), "all": ("2007-03-01", "2026-12-31")}
out = []
for name, w in strats.items():
    r = run(w)
    row = {"strategy": name}
    for p, (a, b) in PER.items():
        c, v, s, dd = stats(r[(r.index >= a) & (r.index <= b)])
        row[p] = f"{c:+.1%} / Sharpe {s:.2f} / DD {dd:.0%}"
    out.append(row)
    # what it holds now
    if "momentum" in name or "trend" in name:
        print(name, "holds now:", {k: round(v, 2) for k, v in w.iloc[-1].items() if v > 0})
pd.set_option("display.width", 250, "display.max_colwidth", 80)
print(pd.DataFrame(out).set_index("strategy").to_string())
# crisis years
for name in ("SPY buy & hold", "trend + momentum: top 3 by 12-month return, if above average", "trend: each class only above its 10-month average"):
    r = run(strats[name]); yr = (1 + r).groupby(r.index.year).prod() - 1
    print(name[:40], {y: f"{yr[y]:+.0%}" for y in (2008, 2018, 2020, 2022, 2025)})
