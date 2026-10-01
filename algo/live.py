"""The all-day engine: one program that stays on through the US session and acts
the moment new data is ready, instead of waiting for the half-hourly timer.

    python -m algo.live                      # shadow: decides, logs, sends nothing
    python -m algo.live --minutes 5          # stop after 5 minutes (test)

Each account's keys come from ALPACA_<X>_API_KEY_ID / ALPACA_<X>_API_SECRET_KEY
(account A: ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY), like the hourly workflow.

Every minute it looks at the clock:
- right after an hour's bars are final (crypto at :01, stocks at :17 because the
  free data plan is 15 minutes late) it downloads them once and runs every
  account's decision, exactly the code the hourly workflow runs;
- every minute it reads live prices of what the accounts hold and notes when a
  stop or target is touched (the broker's own stop / target orders act on it).

Shadow mode (the only mode for now): the decisions are a dry run against the
real Alpaca account, so we see the orders it would send and when. Everything goes
to paper/engine/<date>.md. At the end it lists the orders the hourly system
really sent today on each account, so both can be compared side by side.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "paper" / "engine"
# The shadow decisions run in a copy of the code and accounts (prices shared), so they
# never touch the real paper/ files: only the engine log is written to the repo.
WORK = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "engine-workspace"
ACCOUNTS = {"A": "", "B": "B", "C": "C"}  # account -> folder under paper/
DECIDE_AT = (1, 17)  # minutes past the hour: crypto bars are final at once, stocks 16 minutes late
STOP_AFTER_CLOSE_MIN = 25  # the last stock bar (15:00-16:00) is final at 16:16


def now() -> datetime:
    return datetime.now(timezone.utc)


def keys(account: str) -> dict[str, str]:
    p = "" if account == "A" else f"{account}_"
    return {"ALPACA_API_KEY_ID": os.environ.get(f"ALPACA_{p}API_KEY_ID", ""),
            "ALPACA_API_SECRET_KEY": os.environ.get(f"ALPACA_{p}API_SECRET_KEY", "")}


def account_env(account: str) -> dict[str, str]:
    env = dict(os.environ) | keys(account) | {"PAPER_ACCOUNT": ACCOUNTS[account]}
    env.pop("NTFY_TOPIC", None)  # shadow: never notify the phone
    return env


def run(args: list[str], env: dict | None = None, timeout: int = 1200) -> tuple[int, str]:
    try:
        p = subprocess.run([sys.executable, "-m", *args], cwd=WORK if (WORK / "algo").exists() else ROOT, env=env, capture_output=True, text=True,
                           timeout=timeout)
        return p.returncode, (p.stdout + ("\n" + p.stderr.strip().splitlines()[-1] if p.returncode and p.stderr.strip()
                                          else "")).strip()
    except subprocess.TimeoutExpired:
        return 1, f"timed out after {timeout}s"


def due(t: datetime, done: set) -> str | None:
    """The decision slot that is due at `t` and not done yet, e.g. '2026-10-01 14:17'."""
    for m in sorted(DECIDE_AT, reverse=True):
        if t.minute >= m:
            slot = t.strftime(f"%Y-%m-%d %H:{m:02d}")
            return None if slot in done else slot
    return None


def held(account: str) -> list[dict]:
    """The paper account's open trades (from its orders.json, refreshed at each decision)."""
    f = WORK / "paper" / ACCOUNTS[account] / "orders.json"
    try:
        return json.loads(f.read_text())
    except (OSError, ValueError):
        return []


def touched(trades: list[dict], prices: dict[str, float]) -> list[str]:
    """Stops / targets the live price has reached (long and short)."""
    from .alpaca import SYMBOLS

    out = []
    for t in trades:
        px = prices.get(SYMBOLS[t["asset"]])
        if px is None:
            continue
        side = 1 if t["qty"] > 0 else -1
        if t.get("stop") is not None and (px - t["stop"]) * side <= 0:
            out.append(f"{t['asset']} {t['strategy']}: price {px:,.2f} at / through the stop {t['stop']:,.2f}")
        elif t.get("target") is not None and (px - t["target"]) * side >= 0:
            out.append(f"{t['asset']} {t['strategy']}: price {px:,.2f} at / through the target {t['target']:,.2f}")
    return out


class Log:
    def __init__(self, day: str):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.path = LOG_DIR / f"{day}.md"
        if not self.path.exists():
            self.path.write_text(f"# All-day engine (shadow) – {day}\n\nTimes in UTC. Shadow mode: nothing is sent; "
                                 "'would send' is what it would have done at that minute.\n")

    def write(self, *lines: str) -> None:
        text = "\n".join(lines)
        print(text, flush=True)
        with self.path.open("a") as f:
            f.write(text + "\n")


def workspace() -> None:
    import shutil

    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    shutil.copytree(ROOT / "algo", WORK / "algo", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "paper", WORK / "paper", ignore=shutil.ignore_patterns("engine"))
    (ROOT / "data").mkdir(exist_ok=True)
    (WORK / "data").symlink_to(ROOT / "data")


def save(log: Log) -> None:
    """Push the log to the repo (on GitHub only), so it can be read during the day."""
    if not os.environ.get("GITHUB_ACTIONS"):
        return
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).returncode
    git("add", str(log.path.relative_to(ROOT)))
    if git("diff", "--cached", "--quiet") == 0:
        return
    git("-c", "user.name=paper-bot", "-c", "user.email=paper-bot@users.noreply.github.com",
        "commit", "-q", "-m", f"Engine log {now():%Y-%m-%d %H:%M} UTC")
    for _ in range(6):
        if git("pull", "--rebase", "-X", "theirs", "-q") == 0 and git("push", "-q") == 0:
            return
        git("rebase", "--abort")
        time.sleep(5)
    print("engine log not saved this time (next decision retries)", flush=True)


def decide(slot: str, log: Log, accounts) -> None:
    t0 = time.time()
    code, out = run(["algo.fetch"], dict(os.environ) | keys("A"))
    log.write("", f"## {slot} – new bars", "", f"Data: {'ok' if code == 0 else 'FAILED: ' + out[-300:]} "
              f"({time.time() - t0:.0f}s)")
    for a in accounts:
        env = account_env(a)
        t1 = time.time()
        code, out = run(["algo.paper", "update"], env)
        if code:
            log.write(f"- **{a}**: paper update FAILED: {out[-300:]}")
            continue
        status = (WORK / "paper" / ACCOUNTS[a] / "status.md").read_text().splitlines()
        eq = next((s for s in status if s.startswith("**Equity")), "").split("·")[0].replace("**", "").strip()
        code, out = run(["algo.alpaca", "sync"], env, timeout=300)  # dry run: no --send
        orders = [s for s in out.splitlines() if s[:4] in ("BUY ", "SELL")]
        log.write(f"- **{a}** {eq} – decided at {now():%H:%M:%S} ({time.time() - t1:.0f}s): "
                  + ("sync FAILED: " + out[-300:] if code else
                     "no order" if not orders else "would send:"))
        log.write(*[f"  - `{o.strip()}`" for o in orders])


def watch(log: Log, accounts, seen: set) -> None:
    from .alpaca import SYMBOLS, AlpacaError, live_prices

    trades = {a: held(a) for a in accounts}
    syms = sorted({SYMBOLS[t["asset"]] for ts in trades.values() for t in ts})
    if not syms:
        return
    os.environ.update(keys("A"))  # market data: any account's keys
    try:
        prices = live_prices(syms)
    except AlpacaError as e:
        log.write(f"- {now():%H:%M} live prices unavailable ({e})")
        return
    for a, ts in trades.items():
        for msg in touched(ts, prices):
            key = (a, msg.split(":")[0], "stop" in msg)
            if key not in seen:  # once per trade and level
                seen.add(key)
                log.write(f"- {now():%H:%M:%S} **{a}** {msg}")


def compare(log: Log, accounts, day: str) -> None:
    """What the hourly system really sent today, for the side-by-side check."""
    from .alpaca import AlpacaError, request

    log.write("", "## What the hourly system really sent today", "")
    for a in accounts:
        os.environ.update(keys(a))
        try:
            orders = request("GET", f"/v2/orders?status=all&after={day}T00:00:00Z&limit=200&direction=asc")
        except AlpacaError as e:
            log.write(f"- **{a}**: unavailable ({e})")
            continue
        main = [o for o in orders if o.get("type") in ("market", "limit") and not o.get("legs")]
        log.write(f"- **{a}**: " + ("no order" if not main else ""))
        log.write(*[f"  - `{o['submitted_at'][11:19]} {o['side'].upper()} {o.get('qty') or o.get('notional')} "
                    f"{o['symbol']} {o['type']} ({o['status']})`" for o in main])


def market(accounts) -> dict:
    from .alpaca import request

    os.environ.update(keys(accounts[0]))
    return request("GET", "/v2/clock")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--minutes", type=float, default=345, help="stop after this long (a GitHub job lasts 6 h)")
    ap.add_argument("--accounts", default="A,B,C")
    ap.add_argument("--decide-now", action="store_true", help="one decision at once (test)")
    args = ap.parse_args()
    accounts = [a for a in args.accounts.split(",") if keys(a)["ALPACA_API_KEY_ID"]]
    if not accounts:
        sys.exit("No Alpaca keys in the environment.")
    end = time.time() + args.minutes * 60
    day = now().strftime("%Y-%m-%d")
    log = Log(day)
    workspace()
    log.write("", f"Engine on at {now():%H:%M} UTC for {', '.join(accounts)} (shadow).")
    done, seen, closed_at = set(), set(), None
    if args.decide_now:
        decide(f"{now():%Y-%m-%d %H:%M} (test)", log, accounts)
    while time.time() < end:
        try:
            clock = market(accounts)
        except Exception as e:  # never die on one bad minute
            log.write(f"- {now():%H:%M} clock unavailable ({e})")
            time.sleep(60)
            continue
        if clock.get("is_open"):
            closed_at = None
            slot = due(now(), done)
            if slot:
                done.add(slot)
                try:
                    decide(slot, log, accounts)
                except Exception as e:
                    log.write(f"- {slot}: decision FAILED ({e})")
                save(log)
            try:
                watch(log, accounts, seen)
            except Exception as e:
                log.write(f"- {now():%H:%M} watch failed ({e})")
        else:
            closed_at = closed_at or time.time()
            opens = datetime.fromisoformat(clock["next_open"]).astimezone(timezone.utc)
            if (opens - now()).total_seconds() > 3 * 3600:  # closed for the day (or a holiday)
                if not done or time.time() - closed_at > STOP_AFTER_CLOSE_MIN * 60:
                    break
                slot = due(now(), done)  # the day's last bar is final 16 minutes after the close
                if slot:
                    done.add(slot)
                    decide(slot, log, accounts)
        time.sleep(max(5.0, 60 - now().second))
    log.write("", f"Engine off at {now():%H:%M} UTC.")
    try:
        compare(log, accounts, day)
    except Exception as e:
        log.write(f"Comparison unavailable ({e})")
    save(log)


if __name__ == "__main__":
    main()
