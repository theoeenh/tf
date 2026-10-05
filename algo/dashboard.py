"""Build the dashboard page (paper/dashboard.html) from the paper account's files.

    python -m algo.dashboard [--study reports/<run>/hourly_summary.json]

Reads paper/config.json, equity.csv, orders.json, trades.csv, race.csv,
board.csv, ml.json, study.json and the latest AI views, and embeds them as
data in one self-contained page (published as an Artifact).
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from .analyst import VIEWS_DIR
from .metrics import equity_stats
from .paper import PAPER_DIR, now_utc
from .system import bars_per_year

TEMPLATE = Path(__file__).with_name("dashboard_template.html")


def _read_csv(name: str) -> pd.DataFrame:
    path = PAPER_DIR / name
    try:
        return pd.read_csv(path)
    except (FileNotFoundError, pd.errors.EmptyDataError):  # missing, or no rows yet (no trades)
        return pd.DataFrame()


def _clean(x):
    """JSON-safe: NaN / inf -> None, numpy -> python."""
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return float(x) if np.isfinite(x) else None
    return x


ROOT_PAPER = Path(__file__).resolve().parent.parent / "paper"


def accounts() -> list[dict]:
    """One row per paper account folder (paper/, paper/B/, ...): name, version, equity, trades."""
    rows = []
    for d in [ROOT_PAPER] + sorted(x for x in ROOT_PAPER.iterdir() if x.is_dir() and (x / "config.json").exists()):
        cfg = json.loads((d / "config.json").read_text())
        eq_path, tr_path = d / "equity.csv", d / "trades.csv"
        equity = cfg["capital"]
        if eq_path.exists() and eq_path.stat().st_size:
            e = pd.read_csv(eq_path)
            if len(e):
                equity = float(e.iloc[-1, 1])
        trades = len(pd.read_csv(tr_path)) if tr_path.exists() and tr_path.stat().st_size else 0
        opened = json.loads((d / "orders.json").read_text()) if (d / "orders.json").exists() else []
        variant = cfg.get("variant") or cfg.get("plan", "")[:60]  # D / E / F: their own plan
        rows.append({"name": cfg.get("name", variant), "variant": variant,
                     "alpaca": cfg.get("alpaca_account", ""), "equity": equity,
                     "ret": equity / cfg["capital"] - 1, "trades": trades, "open": len(opened)})
    return rows


def _learner() -> dict | None:
    from .learner_report import OUT, PLAIN

    f = OUT / "latest.json"
    if not f.exists():
        return None
    rep = json.loads(f.read_text())
    rep["importance"] = [[PLAIN.get(n, n), v] for n, v in rep.get("importance", [])]
    return rep


def collect() -> dict:
    cfg = json.loads((PAPER_DIR / "config.json").read_text())
    start = pd.Timestamp(cfg["start"])
    eq = _read_csv("equity.csv")
    equity, status = [], {"equity": cfg["capital"], "ret": 0.0, "max_dd": 0.0, "trades": 0, "open": 0}
    if not eq.empty:
        s = pd.Series(eq.iloc[:, 1].to_numpy(), pd.to_datetime(eq.iloc[:, 0]))
        s = s[s.index >= start]
        if len(s):
            step = max(1, len(s) // 800)
            equity = [[t.strftime("%Y-%m-%d %H:%M"), float(v)] for t, v in s.iloc[::step].items()]
            if equity[-1][0] != s.index[-1].strftime("%Y-%m-%d %H:%M"):
                equity.append([s.index[-1].strftime("%Y-%m-%d %H:%M"), float(s.iloc[-1])])
            st = equity_stats(s, bars_per_year(s.index)) if len(s) > 2 else {}
            status |= {"equity": float(s.iloc[-1]), "ret": float(s.iloc[-1] / cfg["capital"] - 1),
                       "max_dd": st.get("max_drawdown", 0.0)}
    orders = json.loads((PAPER_DIR / "orders.json").read_text()) if (PAPER_DIR / "orders.json").exists() else []
    positions = [{"asset": o["asset"], "side": 1 if o["qty"] > 0 else -1, "strategy": o["strategy"],
                  "entry": o.get("entry"), "stop": o["stop"], "target": o["target"], "r": o.get("r")}
                 for o in orders]
    tr = _read_csv("trades.csv")
    trades = []
    if not tr.empty:
        tr = tr[pd.to_datetime(tr.exit_date) >= start]
        status["trades"] = len(tr)
        trades = [{"exit": str(t.exit_date), "asset": t.asset, "side": int(t.side), "strategy": t.strategy,
                   "reason": t.reason, "r": float(t.r_multiple)} for t in tr.tail(12).iloc[::-1].itertuples()]
    status["open"] = len(positions)
    race = _read_csv("race.csv").to_dict("records")
    board = _read_csv("board.csv").head(20).to_dict("records")
    ml = json.loads((PAPER_DIR / "ml.json").read_text()) if (PAPER_DIR / "ml.json").exists() else None
    if ml:
        ml["by_quintile"] = list(ml.get("by_quintile", {}).values())
        ml.setdefault("source", "Live paper account")
    study = json.loads((PAPER_DIR / "study.json").read_text()) if (PAPER_DIR / "study.json").exists() else None
    if study and not (ml and ml.get("judged")) and study.get("ml_reports"):
        # until the live account has its own predictions, show the backtest's
        reps = study["ml_reports"]
        name = cfg["variant"] if cfg["variant"] in reps else next(iter(reps))
        ml = dict(reps[name], by_quintile=list(reps[name].get("by_quintile", {}).values()),
                  source=f"Backtest of {name}, {study['window']}")
    views_files = sorted(VIEWS_DIR.glob("*.json"))
    ai = ({"date": views_files[-1].stem, "views": json.loads(views_files[-1].read_text())}
          if views_files else None)
    return _clean({"generated": now_utc().strftime("%Y-%m-%d %H:%M"), "config": cfg, "status": status,
                   "equity": equity, "positions": positions, "trades": trades, "race": race, "board": board,
                   "ml": ml, "study": study, "ai_views": ai, "accounts": accounts(),
                   "learner": _learner()})


def build(study: Path | None = None) -> Path:
    if study is not None:
        shutil.copy(study, PAPER_DIR / "study.json")
    data = json.dumps(collect(), separators=(",", ":")).replace("</", "<\\/")
    out = PAPER_DIR / "dashboard.html"
    out.write_text(TEMPLATE.read_text().replace("__DATA__", data))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--study", type=Path, default=None, help="a *_summary.json from algo.portfolio_run")
    print(f"Dashboard: {build(ap.parse_args().study)}")


if __name__ == "__main__":
    main()
