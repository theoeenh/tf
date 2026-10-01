from datetime import datetime, timezone

from algo.live import due, keys, touched


def t(h, m):
    return datetime(2026, 10, 1, h, m, tzinfo=timezone.utc)


def test_due_slots():
    done = set()
    assert due(t(14, 0), done) is None
    assert due(t(14, 1), done) == "2026-10-01 14:01"
    done.add("2026-10-01 14:01")
    assert due(t(14, 10), done) is None
    assert due(t(14, 17), done) == "2026-10-01 14:17"
    done.add("2026-10-01 14:17")
    assert due(t(14, 59), done) is None
    # a late minute still catches the slot it missed
    assert due(t(15, 30), done) == "2026-10-01 15:17"


def test_touched_long_and_short():
    trades = [{"asset": "NVDA", "strategy": "s", "qty": 10, "stop": 100.0, "target": 110.0},
              {"asset": "TSLA", "strategy": "s", "qty": -5, "stop": 300.0, "target": 280.0}]
    assert touched(trades, {"NVDA": 105.0, "TSLA": 290.0}) == []
    msgs = touched(trades, {"NVDA": 99.5, "TSLA": 279.0})
    assert "stop" in msgs[0] and msgs[0].startswith("NVDA")
    assert "target" in msgs[1] and msgs[1].startswith("TSLA")


def test_each_account_its_own_keys(monkeypatch):
    monkeypatch.setenv("ALPACA_API_KEY_ID", "a")
    monkeypatch.setenv("ALPACA_B_API_KEY_ID", "b")
    assert keys("A")["ALPACA_API_KEY_ID"] == "a"
    assert keys("B")["ALPACA_API_KEY_ID"] == "b"
    monkeypatch.delenv("ALPACA_C_API_KEY_ID", raising=False)
    assert keys("C")["ALPACA_API_KEY_ID"] == ""
