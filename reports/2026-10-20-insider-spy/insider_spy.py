"""Account A idea: D's insider rule, idle cash in SPY. 2017-01 .. 2025-06 (the vault stays sealed)."""
import json, sys, time
sys.path.insert(0, "/home/user/tf")
import numpy as np, pandas as pd
from algo import finder as F, data

t0 = time.time()
cfg = json.load(open("/home/user/tf/paper/D/config.json"))
c = F.Candidate(**json.loads(cfg["candidate"]))
prices = F.load(data="daily500")
sig = F.signals(c, prices)
print("signals ready", round(time.time() - t0), "s")
spy = data.load("SPY", "auto", interval="1d")["Close"]
spy = spy[spy.index < F.VAULT_START]
PERIODS = {"search 2017-2022": ("2017-01-01", "2022-12-31 23:59"), "validation 2023-2025H1": ("2023-01-01", "2025-06-30 23:59")}

def stats(r):
    r = r.dropna()
    eq = (1 + r).cumprod()
    yrs = len(r) / 252
    return {"CAGR": eq.iloc[-1] ** (1 / yrs) - 1, "vol": r.std() * np.sqrt(252),
            "Sharpe": r.mean() / r.std() * np.sqrt(252), "maxDD": (eq / eq.cummax() - 1).min()}

rows = []
for pname, (a, b) in PERIODS.items():
    for label, seed in [("insider", None)] + [(f"random{k}", k) for k in range(5)]:
        res = F.backtest(c, prices, sig, a, b, seed=seed)
        eq = res.equity.groupby(res.equity.index.normalize()).last()
        g = res.gross.groupby(res.gross.index.normalize()).last().reindex(eq.index).fillna(0)
        r_book = eq.pct_change()
        s = spy.reindex(eq.index).ffill()
        r_spy = s.pct_change()
        w_spy = (1 - g.shift(1)).clip(lower=0)
        cost = (w_spy.diff().abs() * 1e-4).fillna(0)          # 1 bp per unit of SPY traded
        comb = r_book + w_spy * r_spy - cost
        rows.append({"period": pname, "who": label, "trades": len(res.trades),
                     "avg invested in stocks": g.mean(),
                     **{f"book {k}": v for k, v in stats(r_book).items()},
                     **{f"+SPY {k}": v for k, v in stats(comb).items()},
                     **{f"SPY {k}": v for k, v in stats(r_spy).items()}})
        print(pname, label, "done", round(time.time() - t0), "s")
d = pd.DataFrame(rows)
pd.set_option("display.width", 250, "display.max_columns", 30)
d.to_csv("/tmp/insider_spy.csv", index=False)
for pname, g in d.groupby("period", sort=False):
    print("\n==", pname)
    ins = g[g.who == "insider"].iloc[0]; rnd = g[g.who != "insider"].mean(numeric_only=True)
    for k in ("CAGR", "vol", "Sharpe", "maxDD"):
        print(f"{k:7s} SPY {ins['SPY ' + k]:+.3f} | insider book {ins['book ' + k]:+.3f} | insider+SPY {ins['+SPY ' + k]:+.3f} "
              f"| random book {rnd['book ' + k]:+.3f} | random+SPY {rnd['+SPY ' + k]:+.3f}")
    print("trades", int(ins.trades), "avg invested in stocks", round(ins["avg invested in stocks"], 2))
