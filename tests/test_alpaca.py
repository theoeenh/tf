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


def test_notification_title_with_dash(monkeypatch):
    """Account names contain '–', which an HTTP header cannot carry: sent as JSON."""
    import json
    from unittest import mock

    from algo import notify

    monkeypatch.setenv("NTFY_TOPIC", "topic")
    with mock.patch("urllib.request.urlopen") as u:
        assert notify.send("[B – ML brake 10%] BUY 68 AAPL", "body", "green_circle")
        sent = json.loads(u.call_args[0][0].data)
    assert sent["topic"] == "topic" and sent["title"].startswith("[B – ML")


def test_plan_closes_a_position_no_longer_wanted():
    from algo.alpaca import plan

    # the price comes from live data when orders.json no longer lists the asset
    o = plan({}, {"AAPL": 68.06}, {"AAPL": 328.0})
    assert o and o[0]["side"] == "sell" and abs(o[0]["qty"] - 68.06) < 1e-9


def test_closing_crypto_sells_exactly_what_is_held():
    from algo.alpaca import plan

    o = plan({}, {"SOL/USD": 140.302451782}, {"SOL/USD": 120.0})
    assert o[0]["side"] == "sell" and o[0]["qty"] == 140.302451782
    o = plan({"SOL/USD": 10.0000000004}, {}, {"SOL/USD": 120.0})
    assert o[0]["qty"] <= 10.0000000004


def _fake_alpaca(monkeypatch, positions, open_orders, plan, cash=1e6):
    import json

    from algo import alpaca, notify

    monkeypatch.setattr(alpaca, "positions", lambda: dict(positions))
    monkeypatch.setattr(alpaca, "wanted", lambda: dict(plan))
    monkeypatch.setattr(alpaca, "last_prices", lambda: {s: 100.0 for s in plan})
    sent, alerts = [], []
    monkeypatch.setattr(alpaca, "_send", lambda o: sent.append(o) or {"id": "x"})
    monkeypatch.setattr(notify, "send", lambda *a, **k: alerts.append(a) or True)

    def request(method, path, body=None, base=None):
        if path.startswith("/v2/orders?status=open"):
            return open_orders
        if path == "/v2/account":
            return {"non_marginable_buying_power": str(cash), "equity": "100000"}
        raise AssertionError(path)

    monkeypatch.setattr(alpaca, "request", request)
    return sent, alerts


def test_verify_flags_a_position_without_stop(monkeypatch):
    from algo import alpaca

    oco = {"symbol": "NVDA", "side": "sell", "type": "limit", "qty": "10", "order_class": "oco",
           "legs": [{"symbol": "NVDA", "side": "sell", "type": "stop", "qty": "10"}]}
    _, alerts = _fake_alpaca(monkeypatch, {"NVDA": 10.0, "AMD": 5.0}, [oco], {"NVDA": 10.0, "AMD": 5.0})
    problems = alpaca.verify(alert=True)
    assert problems == ["AMD: 5 held, only 0 covered by a stop"] and alerts


def test_verify_all_good(monkeypatch):
    from algo import alpaca

    stop = {"symbol": "AMD", "side": "sell", "type": "stop", "qty": "5"}
    _fake_alpaca(monkeypatch, {"AMD": 5.0}, [stop], {"AMD": 5.0})
    assert alpaca.verify() == []


def test_failed_run_puts_the_stops_back(monkeypatch):
    from algo import alpaca

    sent, alerts = _fake_alpaca(monkeypatch, {"NVDA": 10.0}, [], {"NVDA": 10.0})
    trades = [{"asset": "NVDA", "strategy": "s", "qty": 10.0, "stop": 95.0, "target": 120.0}]
    alpaca.emergency_protect(trades, RuntimeError("boom"))
    assert sent and sent[0]["symbol"] == "NVDA" and alerts and "NVDA" in alerts[0][1]


def test_tiny_top_up_is_skipped_but_real_changes_are_not():
    from algo.alpaca import plan

    assert plan({"NVDA": 111.876}, {"NVDA": 111.819}, {"NVDA": 234.0}) == []  # 0.05%: keep
    assert plan({"NVDA": 130.0}, {"NVDA": 111.8}, {"NVDA": 234.0})[0]["side"] == "buy"  # real add
    assert plan({}, {"NVDA": 111.8}, {"NVDA": 234.0})[0]["side"] == "sell"  # close


def test_crypto_buy_is_cut_to_the_cash_left(monkeypatch):
    from algo import alpaca

    monkeypatch.setattr(alpaca, "get_data", lambda path, q: {"quotes": {"SOL/USD": {"bp": 100.0, "ap": 100.1}}})
    sent = []
    monkeypatch.setattr(alpaca, "_send", lambda o: sent.append(o) or {"id": "x"})
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None: {"status": "filled", "filled_qty": "1"})
    monkeypatch.setattr(alpaca, "PAPER_DIR", __import__("pathlib").Path(__import__("tempfile").mkdtemp()))
    oid, how = alpaca.crypto_limit_first({"symbol": "SOL/USD", "side": "buy", "qty": 500.0, "note": ""}, wait=0,
                                         cash=10_000.0)
    assert sent[0]["qty"] * 100.0 <= 0.97 * 10_000 + 1e-6 and "crypto needs cash" in how
    sent.clear()
    oid, how = alpaca.crypto_limit_first({"symbol": "SOL/USD", "side": "buy", "qty": 5.0, "note": ""}, wait=0, cash=2.0)
    assert oid is None and not sent and "skipped" in how


def test_verify_accepts_crypto_smaller_than_plan_when_cash_is_short(monkeypatch):
    from algo import alpaca

    stop = {"symbol": "SOLUSD", "side": "sell", "type": "stop_limit", "qty": "100"}
    _fake_alpaca(monkeypatch, {"SOL/USD": 100.0}, [stop], {"SOL/USD": 500.0}, cash=1_000.0)
    assert alpaca.verify() == []
    _fake_alpaca(monkeypatch, {"SOL/USD": 100.0}, [stop], {"SOL/USD": 500.0}, cash=1e6)
    assert alpaca.verify()  # with the cash there, a gap is a real problem


def test_one_refused_order_does_not_stop_the_others(monkeypatch):
    from algo import alpaca

    monkeypatch.setattr(alpaca, "positions", lambda: {})
    monkeypatch.setattr(alpaca, "wanted", lambda: {"NVDA": 10.0, "AMD": 5.0})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {s: 100.0 for s in syms})
    sent = []

    def send(o):
        if o["symbol"] == "AMD" and o["type"] == "market":
            raise alpaca.AlpacaError("403 refused")
        sent.append(o)
        return {"id": o["symbol"]}

    monkeypatch.setattr(alpaca, "_send", send)
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None:
                        {"is_open": True} if p == "/v2/clock" else {"status": "filled", "equity": "1"})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: False)
    import pytest

    with pytest.raises(alpaca.AlpacaError, match="AMD"):
        alpaca._trade_and_protect(True, [], {"NVDA": 100.0, "AMD": 100.0})
    assert any(o["symbol"] == "NVDA" for o in sent)
