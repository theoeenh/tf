"""Forward paper trading of the finder's graduates: strategies that passed every gate AND their one
vault test start here automatically, and are followed on new data from that day on.

    python -m algo.forward          # update every graduate (nightly, after the finder loop)

Each graduate trades only bars that did not exist when it graduated, with the finder's costs and
exit rules, and is compared with random entries over the same days. This is the "paper trade 4 to
8 weeks before real money" step: nothing here sends orders (a dedicated Alpaca paper account can
mirror a graduate later, once it holds up here).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from . import finder as F

log = logging.getLogger(__name__)
FWD = Path(__file__).resolve().parent.parent / "paper" / "forward"
MIN_WEEKS = 6  # weeks of forward trading before a graduate can be considered for real money


def graduates() -> dict:
    path = FWD / "strategies.json"
    return json.loads(path.read_text()) if path.exists() else {}


def start(cid: str, since: str | None = None) -> dict:
    """Add a graduate; it trades from the next session on (nothing it has seen counts)."""
    reg = F.registry()
    row = reg[reg["id"] == cid]
    if row.empty:
        raise SystemExit(f"{cid} is not in the registry")
    g = graduates()
    if cid not in g:
        day = pd.Timestamp(since) if since else pd.Timestamp.now().normalize() + pd.Timedelta(days=1)
        g[cid] = {"since": str(day.date()), "label": row.iloc[0]["label"], "candidate": row.iloc[0]["candidate"]}
        FWD.mkdir(parents=True, exist_ok=True)
        (FWD / "strategies.json").write_text(json.dumps(g, indent=1))
    return g[cid]


def update_one(cid: str, info: dict, data: dict) -> dict:
    c = F.Candidate(**json.loads(info["candidate"]))
    if c.data not in data:
        data[c.data] = F.load(include_vault=True, data=c.data)
    prices = data[c.data]
    sig = F.signals(c, prices)
    end = max(df.index[-1] for df in prices.values())
    since = pd.Timestamp(info["since"])
    out = {"id": cid, "label": info["label"], "since": info["since"], "through": str(end)[:16],
           "weeks": round((end - since).days / 7, 1)}
    if end <= since:
        return out | {"trades": 0, "note": "no new bars yet"}
    res = F.backtest(c, prices, sig, since, end)
    st = F.trading_stats(res)
    rnd = [F.trading_stats(F.backtest(c, prices, sig, since, end, seed=s)) for s in range(F.SEEDS)]
    folder = FWD / cid
    folder.mkdir(parents=True, exist_ok=True)
    res.trades_df.to_csv(folder / "trades.csv", index=False)
    res.equity.to_csv(folder / "equity.csv", header=["equity"])
    return out | {"trades": st["trades"], "return": st["return"], "avg_r": st["avg_r"], "max_dd": st["max_dd"],
                  "rand_avg_r": float(np.nanmean([r["avg_r"] for r in rnd])),
                  "rand_return": float(np.mean([r["return"] for r in rnd]))}


def update() -> list[dict]:
    rows, data = [], {}
    for cid, info in graduates().items():
        try:
            rows.append(update_one(cid, info, data))
        except (OSError, KeyError, ValueError) as exc:
            log.warning("forward %s: %r", cid, exc)
            rows.append({"id": cid, "label": info["label"], "since": info["since"], "note": f"error: {exc!r}"})
    write(rows)
    return rows


def write(rows: list[dict]) -> Path:
    md = ["# Forward paper trading (finder graduates)", "",
          "Strategies that passed every finder gate and their one vault test, traded on new data only from the "
          f"day they graduated. At least {MIN_WEEKS} weeks here before any real money is discussed.", ""]
    if not rows:
        md.append("No graduate yet: no strategy has passed every gate and its vault test.")
    else:
        md += ["| strategy | since | weeks | trades | return | avg R | random avg R | max drawdown | status |",
               "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            if "return" not in r:
                md.append(f"| `{r['id']}` {r['label']} | {r['since']} | {r.get('weeks', '')} | 0 | | | | | "
                          f"{r.get('note', '')} |")
                continue
            ok = r["return"] > 0 and r["avg_r"] > r["rand_avg_r"]
            status = ("holding up" if ok else "behind") + ("" if r["weeks"] >= MIN_WEEKS else " (too early to judge)")
            md.append(f"| `{r['id']}` {r['label'].replace('|', '·')} | {r['since']} | {r['weeks']} | {r['trades']} | "
                      f"{r['return']:+.1%} | {r['avg_r']:+.2f} | {r['rand_avg_r']:+.2f} | {r['max_dd']:.1%} | {status} |")
    FWD.mkdir(parents=True, exist_ok=True)
    path = FWD / "report.md"
    path.write_text("\n".join(md) + "\n")
    return path


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    rows = update()
    print(f"{len(rows)} graduate(s); report: {FWD / 'report.md'}")


if __name__ == "__main__":
    main()
