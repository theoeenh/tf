from algo.social import hourly_counts, symbol


def test_counts_per_hour_and_symbols():
    msgs = [{"id": 3, "created_at": "2026-10-01T08:38:36Z", "entities": {"sentiment": {"basic": "Bullish"}}},
            {"id": 2, "created_at": "2026-10-01T08:05:00Z", "entities": {"sentiment": {"basic": "Bearish"}}},
            {"id": 1, "created_at": "2026-10-01T07:59:59Z", "entities": {"sentiment": None}}]
    c = hourly_counts(msgs)
    assert c.loc["2026-10-01 08:00"].tolist() == [2, 1, 1]
    assert c.loc["2026-10-01 07:00"].tolist() == [1, 0, 0]
    assert symbol("BTC") == "BTC.X" and symbol("GOLD") == "GLD" and symbol("NVDA") == "NVDA"
