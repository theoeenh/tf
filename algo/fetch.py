"""Download the market data every paper account needs, once.

    python -m algo.fetch

Reads the config of every account (paper/, paper/B/, ...) and refreshes the
price and news caches for the union of their assets. The hourly job runs this
once, then each account starts from the same cache instead of all of them
downloading (and hitting Alpaca's rate limit) at the same time.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from . import data, news

ROOT_PAPER = Path(__file__).resolve().parent.parent / "paper"


def account_configs() -> list[dict]:
    dirs = [ROOT_PAPER] + sorted(d for d in ROOT_PAPER.iterdir() if d.is_dir())
    cfgs = [json.loads((d / "config.json").read_text()) for d in dirs if (d / "config.json").exists()]
    return [c for c in cfgs if "universe" in c]  # D / E / F trade from other plans: no bars of their own


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    cfgs = account_configs()
    assets = sorted({a for c in cfgs for a in c["universe"]})
    for c in {(c.get("source", "auto"), c["interval"]) for c in cfgs}:
        source, interval = c
        for a in assets:
            data.load(a, source, interval=interval)
    hourly = any(c["interval"] != "1d" for c in cfgs)
    news.load_all(assets, strict=True, alpaca_news=hourly)
    print(f"Data ready for {len(assets)} assets, {len(cfgs)} accounts.")


if __name__ == "__main__":
    main()
