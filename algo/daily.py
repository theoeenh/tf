"""The daily routine, in order:

    python -m algo.daily

1. Refresh prices and news (only the missing days are downloaded).
2. Trade the new bars in the paper account (paper/status.md, trades.csv, orders.json).
3. Write the daily brief with events ahead, news and signals (paper/brief.md).
4. Race every version of the system side by side and rank the strategies
   (paper/leaderboard.md, see algo/leaderboard.py).
5. The shared learner's report: what it learned, what changed (paper/learner/).

Step 6 is done by the AI analyst: read paper/brief.md and write
paper/ai_views/<date>.json (see algo/analyst.py). The next run uses those
views in the learner and scores them once their horizon has passed.
"""
from __future__ import annotations

import logging

from . import brief, leaderboard, learner_report, paper


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(f"Paper account: {paper.update()}")
    print(f"Brief: {brief.write_brief('auto')}")
    print(f"Leaderboard: {leaderboard.write()}")
    print(f"Learner report: {learner_report.write()}")


if __name__ == "__main__":
    main()
