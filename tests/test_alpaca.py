import pytest

from algo import alpaca


def test_plan_nets_strategies_and_respects_alpaca_limits():
    want = {"NVDA": 10.4, "BTC/USD": -0.2, "TSLA": -3.7, "GLD": 5.0}
    have = {"NVDA": 4.0, "GLD": 5.0, "SLV": 12.0}
    prices = {"NVDA": 200.0, "BTC/USD": 80000.0, "TSLA": 350.0, "GLD": 380.0, "SLV": 55.0}
    orders = {o["symbol"]: o for o in alpaca.plan(want, have, prices)}
    assert orders["NVDA"]["side"] == "buy" and orders["NVDA"]["qty"] == pytest.approx(6.4)
    assert "BTC/USD" not in orders  # crypto short -> flat, and we hold none
    assert orders["TSLA"]["side"] == "sell" and orders["TSLA"]["qty"] == 3  # whole shares for shorts
    assert "GLD" not in orders  # already matches
    assert orders["SLV"]["side"] == "sell" and orders["SLV"]["qty"] == 12  # no longer wanted
    assert orders["SLV"]["time_in_force"] == "day"


def test_crypto_short_is_flattened_with_a_note():
    orders = alpaca.plan({"ETH/USD": -1.0}, {"ETH/USD": 2.0}, {"ETH/USD": 2600.0})
    (o,) = orders
    assert o["side"] == "sell" and o["qty"] == 2.0 and "crypto shorts" in o["note"]
    assert o["time_in_force"] == "gtc"


def test_missing_keys_give_a_clear_error(monkeypatch):
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)
    with pytest.raises(alpaca.AlpacaError, match="ALPACA_API_KEY_ID"):
        alpaca.request("GET", "/v2/account")


def test_only_the_paper_endpoint_is_used():
    assert alpaca.BASE_URL == "https://paper-api.alpaca.markets"


def test_stock_trade_gets_oco_for_whole_shares_and_stop_for_the_rest():
    trades = [{"asset": "NVDA", "strategy": "donchian_trend", "qty": 10.4, "stop": 190.123, "target": 240.0}]
    orders = alpaca.protect("NVDA", 10.4, trades, price=200.0)
    oco, frac = orders
    assert oco["order_class"] == "oco" and oco["qty"] == 10 and oco["side"] == "sell"
    assert oco["stop_loss"]["stop_price"] == 190.12 and oco["take_profit"]["limit_price"] == 240.0
    assert frac["type"] == "stop" and frac["qty"] == pytest.approx(0.4) and frac["time_in_force"] == "day"


def test_short_stock_and_trailing_stop_without_target():
    trades = [{"asset": "TSLA", "strategy": "squeeze_breakout", "qty": -3.0, "stop": 380.0, "target": None}]
    (o,) = alpaca.protect("TSLA", -3.0, trades, price=350.0)
    assert o["side"] == "buy" and o["type"] == "stop" and o["qty"] == 3 and o["time_in_force"] == "gtc"


def test_crypto_gets_stop_limit_and_protection_never_exceeds_holding():
    trades = [{"asset": "BTC", "strategy": "a", "qty": 0.5, "stop": 80000.0, "target": 90000.0},
              {"asset": "BTC", "strategy": "b", "qty": 0.5, "stop": 79000.0, "target": None}]
    orders = alpaca.protect("BTC/USD", 0.7, trades, price=84000.0)  # e.g. fees made the fill a bit smaller
    assert [o["type"] for o in orders] == ["stop_limit", "stop_limit"]
    assert sum(o["qty"] for o in orders) == pytest.approx(0.7)
    assert orders[0]["limit_price"] < orders[0]["stop_price"]


def test_price_already_through_stop_closes_at_market():
    trades = [{"asset": "GOLD", "strategy": "a", "qty": 5.0, "stop": 380.0, "target": 400.0}]
    (o,) = alpaca.protect("GLD", 5.0, trades, price=379.0)
    assert o["type"] == "market" and o["side"] == "sell" and o["qty"] == 5.0


def test_opposite_side_trades_are_not_protected():
    trades = [{"asset": "NVDA", "strategy": "a", "qty": -2.0, "stop": 210.0, "target": None}]
    assert alpaca.protect("NVDA", 4.0, trades, price=200.0) == []


def test_first_hour_with_one_bar_per_asset_is_not_enough_to_trade():
    import pandas as pd

    from algo.paper import bars_since

    t = pd.Timestamp("2026-09-30 14:00")
    one = {a: pd.DataFrame({"Close": [1.0, 1.0]}, index=[t - pd.Timedelta(hours=1), t]) for a in ("BTC", "NVDA")}
    assert bars_since(one, t) == 1  # 2 assets, but a single bar time
    two = {"BTC": pd.DataFrame({"Close": [1.0, 1.0]}, index=[t, t + pd.Timedelta(hours=1)])}
    assert bars_since(two, t) == 2


def test_notifications_only_for_real_trades_and_off_without_topic(monkeypatch):
    from algo import notify

    monkeypatch.delenv("NTFY_TOPIC", raising=False)
    assert notify.send("t", "b") is False  # nothing is sent without a topic
    msgs = notify.trade_messages([
        {"symbol": "ETH/USD", "side": "buy", "qty": 0.42, "type": "market", "note": ""},
        {"symbol": "NVDA", "side": "sell", "qty": 10, "type": "stop", "stop_price": 200, "note": "x"},
    ], equity=100000)
    assert len(msgs) == 1 and msgs[0][0] == "BUY 0.42 ETH/USD" and "$100,000" in msgs[0][1]


def test_opening_auction_window_and_order_split():
    base = {"is_open": False, "next_open": "2026-10-01T09:30:00-04:00"}
    assert alpaca.opening_auction(base | {"timestamp": "2026-10-01T09:12:00.000000000-04:00"})
    assert not alpaca.opening_auction(base | {"timestamp": "2026-10-01T09:29:00.000000000-04:00"})  # too late
    assert not alpaca.opening_auction(base | {"timestamp": "2026-09-30T17:12:00.000000000-04:00"})  # evening
    orders = alpaca.at_the_open([
        {"symbol": "AAPL", "side": "buy", "qty": 10.4, "type": "market", "time_in_force": "day", "note": ""},
        {"symbol": "BTC/USD", "side": "buy", "qty": 0.1, "type": "market", "time_in_force": "gtc", "note": ""}])
    assert [(o["symbol"], o["qty"], o["time_in_force"]) for o in orders] == [
        ("AAPL", 10, "opg"), ("AAPL", 0.4, "day"), ("BTC/USD", 0.1, "gtc")]


def test_clock_without_fractional_seconds():
    assert alpaca.opening_auction({"is_open": False, "next_open": "2026-10-01T09:30:00-04:00",
                                   "timestamp": "2026-10-01T09:10:00-04:00"})
