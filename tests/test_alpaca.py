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


def test_opening_auction_window_and_orders_at_the_open():
    """2026-10-26: Alpaca let the opening-auction ('opg') orders of A and B expire unfilled (AAPL, USO,
    SPY, DBC, EEM; only CLF filled) while every plain market order queued before the open filled at 9:30:
    orders sent before the open are plain market orders for the day, whole and fractional shares in one."""
    base = {"is_open": False, "next_open": "2026-10-01T09:30:00-04:00"}
    assert alpaca.opening_auction(base | {"timestamp": "2026-10-01T09:12:00.000000000-04:00"})
    assert not alpaca.opening_auction(base | {"timestamp": "2026-10-01T09:29:00.000000000-04:00"})  # too late
    assert not alpaca.opening_auction(base | {"timestamp": "2026-09-30T17:12:00.000000000-04:00"})  # evening
    orders = alpaca.at_the_open([
        {"symbol": "AAPL", "side": "buy", "qty": 10.4, "type": "market", "time_in_force": "day", "note": ""},
        {"symbol": "BTC/USD", "side": "buy", "qty": 0.1, "type": "market", "time_in_force": "gtc", "note": ""}])
    assert [(o["symbol"], o["qty"], o["time_in_force"]) for o in orders] == [
        ("AAPL", 10.4, "day"), ("BTC/USD", 0.1, "gtc")]


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
    monkeypatch.setattr(alpaca, "wanted", lambda live=None, seen=None: dict(plan))
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: {})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {})
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


def test_verify_counts_a_queued_exit_as_covered(monkeypatch):
    """An exit decided after the close is a market sell queued for the next open: those shares are on
    their way out, not unprotected (2026-10-07: NVDA trailing stop hit on the last bar)."""
    from algo import alpaca

    stop = {"symbol": "NVDA", "side": "sell", "type": "stop", "qty": "68"}
    exit_ = {"symbol": "NVDA", "side": "sell", "type": "market", "qty": "55.821786"}
    _fake_alpaca(monkeypatch, {"NVDA": 123.98}, [stop, exit_], {"NVDA": 68.16})
    assert alpaca.verify() == []
    _fake_alpaca(monkeypatch, {"NVDA": 123.98}, [exit_], {"NVDA": 68.16})
    assert alpaca.verify() == ["NVDA: 123.98 held, only 55.8218 covered by a stop"]  # the rest needs its stop


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
    monkeypatch.setattr(alpaca, "wanted", lambda live=None, seen=None: {"NVDA": 10.0, "AMD": 5.0})
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: {})
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


def test_a_trade_stopped_out_between_bars_is_not_bought_back(monkeypatch, tmp_path):
    """2026-10-08: NVDA's stop filled at Alpaca at 13:05 NY; the paper account sees it only when the
    bar closes, so each run bought the shares back and the stop check sold them again at once."""
    import json

    from algo import alpaca

    trades = [{"asset": "NVDA", "strategy": "donchian_trend", "qty": 67.6, "stop": 231.56, "target": 249.15},
              {"asset": "AMD", "strategy": "rsi2_reversion", "qty": 10.0, "stop": 598.89, "target": 658.16}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    monkeypatch.setattr(alpaca, "positions", lambda: {"AMD": 10.0})  # NVDA: stopped out at Alpaca
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {"NVDA": 230.1, "AMD": 618.0})
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None: {"is_open": True})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: False)
    out = alpaca._trade_and_protect(False, trades, {"NVDA": 230.1, "AMD": 618.0})
    assert not any(o["symbol"] == "NVDA" for o in out)  # no buy back, no market sell
    assert any(o["symbol"] == "AMD" and o.get("order_class") == "oco" for o in out)  # AMD still protected
    assert alpaca.wanted({"NVDA": 230.1}) == {"AMD": 10.0} and alpaca.wanted()["NVDA"] == 67.6


def test_stop_above_the_reference_price_before_the_open_is_put_just_under_it(monkeypatch, tmp_path):
    """2026-10-09 9:26 NY: AAPL's trailing stop 333.2 was above yesterday's close 331.7 (Alpaca's
    reference before the open) and refused: AAPL stayed without a stop. Now the stop goes in at 331.69."""
    import json

    from algo import alpaca

    trades = [{"asset": "AAPL", "strategy": "squeeze_breakout", "qty": 59.09, "stop": 333.2, "target": None}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    monkeypatch.setattr(alpaca, "positions", lambda: {"AAPL": 59.09})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {"AAPL": 340.43})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: False)
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None: {"is_open": False})
    sent = []

    def send(o):
        if o["stop_price"] > 331.7:
            raise alpaca.AlpacaError('POST /v2/orders -> 422: {"code":42210000,"market_price":"331.7",'
                                     '"message":"stop price must be less than current price","stop_price":"333.2"}')
        sent.append(o)
        return {"id": "ok"}

    monkeypatch.setattr(alpaca, "_send", send)
    alpaca._trade_and_protect(True, trades, {"AAPL": 340.43})
    assert [(o["qty"], o["stop_price"]) for o in sent] == [(59, 331.69), (0.09, 331.69)]
    assert alpaca._below_reference({"side": "sell", "stop_price": 1.0}, RuntimeError("403 forbidden")) is None


def test_verify_accepts_fractional_rest_without_stop_after_the_close(monkeypatch):
    from algo import alpaca

    stop = {"symbol": "AMD", "side": "sell", "type": "stop", "qty": "33"}
    _fake_alpaca(monkeypatch, {"AMD": 33.82}, [stop], {"AMD": 33.82})
    assert alpaca.verify() == []
    stop = {"symbol": "AMD", "side": "sell", "type": "stop", "qty": "32"}
    _fake_alpaca(monkeypatch, {"AMD": 33.82}, [stop], {"AMD": 33.82})
    assert alpaca.verify() == ["AMD: 33.82 held, only 32 covered by a stop"]


def test_request_retries_a_read_after_a_timeout(monkeypatch):
    import io
    import urllib.request
    from algo import alpaca

    calls = []

    def urlopen(req, timeout=30):
        calls.append(req.get_method())
        if len(calls) == 1:
            raise TimeoutError("timed out")
        return io.BytesIO(b'{"account_number": "X"}')

    monkeypatch.setenv("ALPACA_API_KEY_ID", "k")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "s")
    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(alpaca.time, "sleep", lambda s: None)
    assert alpaca.request("GET", "/v2/account")["account_number"] == "X" and len(calls) == 2
    calls.clear()

    def down(req, timeout=30):
        calls.append(req.get_method())
        raise TimeoutError("timed out")

    monkeypatch.setattr(urllib.request, "urlopen", down)
    try:  # an order is never resent: it may have reached Alpaca
        alpaca.request("POST", "/v2/orders", {"a": 1})
    except TimeoutError:
        pass
    assert calls == ["POST"]


def test_live_decisions_are_frozen(tmp_path):
    import pandas as pd
    from algo.paper import FrozenDecisions
    from algo.journal import Verdict

    class Learner:
        skip = False

        def judge(self, key):
            key["pred"] = (0.5, 0.0)
            return Verdict(self.skip, "skipped" if self.skip else "")

    start = pd.Timestamp("2026-10-01")
    key = lambda t: {"x": [1.0], "sleeve": ("QQQ", "s"), "strategy": "s", "time": pd.Timestamp(t), "pred": None}
    lr = Learner()
    f = FrozenDecisions(lr, start, tmp_path / "d.json")
    assert not f.judge(key("2026-10-05 18:00")).skip
    f.save()
    lr.skip = True  # the model changed overnight
    g = FrozenDecisions(lr, start, tmp_path / "d.json")
    assert not g.judge(key("2026-10-05 18:00")).skip  # the past decision stands
    assert g.judge(key("2026-10-06 14:00")).skip  # new candidates use the current model
    assert g.judge(key("2026-09-01 14:00")).skip  # before the start: the learner, never stored


def test_an_order_with_its_own_id_is_retried_once_safely(monkeypatch):
    """2026-10-10 03:56 UTC: Alpaca timed out while B's stops went in. An order carrying a
    client_order_id is retried: if the first try did reach Alpaca, the retry is refused as a duplicate
    and the order already placed is returned, never sent twice."""
    import io
    import urllib.error
    import urllib.request
    from algo import alpaca

    monkeypatch.setenv("ALPACA_API_KEY_ID", "k")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "s")
    monkeypatch.setattr(alpaca.time, "sleep", lambda s: None)
    calls = []

    def flaky(req, timeout=30):
        calls.append((req.get_method(), req.full_url))
        if len(calls) == 1:
            raise TimeoutError("timed out")
        return io.BytesIO(b'{"id": "o1"}')

    monkeypatch.setattr(urllib.request, "urlopen", flaky)
    assert alpaca._send({"symbol": "NVDA", "qty": 1, "side": "sell", "type": "stop", "stop_price": 1.0})["id"] == "o1"
    assert [m for m, _ in calls] == ["POST", "POST"]
    calls.clear()

    def reached(req, timeout=30):  # the first try got through, its answer was lost
        calls.append((req.get_method(), req.full_url))
        if len(calls) == 1:
            raise TimeoutError("timed out")
        if req.get_method() == "POST":
            raise urllib.error.HTTPError(req.full_url, 422, "dup", {}, io.BytesIO(
                b'{"code":40010001,"message":"client_order_id must be unique"}'))
        return io.BytesIO(b'{"id": "first"}')

    monkeypatch.setattr(urllib.request, "urlopen", reached)
    assert alpaca._send({"symbol": "NVDA", "qty": 1, "side": "sell", "type": "stop", "stop_price": 1.0})["id"] == "first"
    assert [m for m, _ in calls] == ["POST", "POST", "GET"] and "by_client_order_id" in calls[2][1]


def test_a_trade_whose_target_filled_between_bars_is_not_bought_back(monkeypatch, tmp_path):
    """2026-10-12: XOM's OCO target (rsi2, 130 shares) filled at 13:49 UTC; the paper account sees it only
    when the bar closes, so the 13:55 run bought the 130 shares back and the target sold them again."""
    import json

    from algo import alpaca

    trades = [{"asset": "XOM", "strategy": "rsi2_reversion", "qty": 130.0, "stop": 160.12, "target": 172.19},
              {"asset": "XOM", "strategy": "donchian_trend", "qty": 26.0, "stop": 162.57, "target": 173.82}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    monkeypatch.setattr(alpaca, "positions", lambda: {"XOM": 26.0})  # the rsi2 shares went at the target
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {"XOM": 172.20})
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None: {"is_open": True})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: False)
    assert alpaca.wanted({"XOM": 172.20}) == {"XOM": 26.0}
    out = alpaca._trade_and_protect(False, trades, {"XOM": 172.20})
    assert not any(o["side"] == "buy" for o in out)                    # no buy back
    assert [o.get("qty") for o in out if o.get("order_class") == "oco"] == [26]  # the trend trade keeps its OCO
    short = {"asset": "XOM", "qty": -5.0, "stop": 180.0, "target": 165.0}
    assert alpaca.through_stop(short, {"XOM": 164.9}) and not alpaca.through_stop(short, {"XOM": 170.0})


def test_a_stop_or_target_reached_earlier_in_the_bar_counts_although_the_price_came_back(monkeypatch, tmp_path):
    """2026-10-13: AMD gapped through its stop at the open (sold at 578.00, stop 577.57), the price came
    back to 588 and the 13:57 run bought it back; MSFT reached its target, fell back, bought back too."""
    import json

    from algo import alpaca

    trades = [{"asset": "AMD", "strategy": "rsi2_reversion", "qty": 7.69, "stop": 577.57, "target": 634.0},
              {"asset": "MSFT", "strategy": "donchian_trend", "qty": 34.0, "stop": 520.0, "target": 550.20},
              {"asset": "AAPL", "strategy": "donchian_trend", "qty": 10.0, "stop": 330.0, "target": 360.0}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    live = {"AMD": 588.66, "MSFT": 549.86, "AAPL": 345.0}         # the last prices alone look fine
    seen = {"AMD": (575.10, 590.0), "MSFT": (546.0, 550.40), "AAPL": (340.0, 346.0)}
    assert alpaca.wanted(live) == {"AMD": 7.69, "MSFT": 34.0, "AAPL": 10.0}
    assert alpaca.wanted(live, seen) == {"AAPL": 10.0}
    monkeypatch.setattr(alpaca, "positions", lambda: {"AAPL": 10.0})  # AMD and MSFT went at Alpaca
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: live)
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: seen)
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None: {"is_open": True})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: False)
    out = alpaca._trade_and_protect(False, trades, dict(live))
    assert not any(o["side"] == "buy" for o in out)
    short = {"asset": "AMD", "qty": -5.0, "stop": 600.0, "target": 560.0}
    assert alpaca.through_stop(short, {"AMD": 580.0}, {"AMD": (579.0, 601.0)})
    assert not alpaca.through_stop(short, {"AMD": 580.0}, {"AMD": (565.0, 590.0)})


def test_bar_range_starts_after_the_last_processed_bar(monkeypatch, tmp_path):
    from algo import alpaca

    (tmp_path / "equity.csv").write_text(",equity\n2026-10-13 13:00:00,97000\n")
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    calls = []

    def fake(path, params):
        calls.append(params)
        return {"bars": {"AMD": [{"t": "2026-10-13T13:20:00Z", "l": 570.0, "h": 600.0},  # pre-market: ignored
                                 {"t": "2026-10-13T14:01:00Z", "l": 578.0, "h": 589.0},
                                 {"t": "2026-10-13T14:02:00Z", "l": 585.0, "h": 590.5}]}}

    monkeypatch.setattr(alpaca, "get_data", fake)
    assert alpaca.bar_range(["AMD", "BTC/USD"]) == {"AMD": (578.0, 590.5)}
    assert calls[0]["start"] == "2026-10-13T14:00:00Z" and calls[0]["symbols"] == "AMD"
    (tmp_path / "equity.csv").write_text(",equity\n2026-10-13,97000\n")  # a daily account
    assert alpaca.bar_range(["AMD"]) == {}


def test_closed_market_leaves_matching_queued_orders_alone(monkeypatch, tmp_path):
    """2026-10-17: account D's 3 buys for Monday were cancelled and sent again by every weekend run."""
    import json

    from algo import alpaca

    trades = [{"asset": "FIS", "ticker": "FIS", "strategy": "insider_low_short", "qty": 125.932423,
               "stop": 32.83, "target": None, "mark": 36.01}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    monkeypatch.setitem(alpaca.SYMBOLS, "FIS", "FIS")
    monkeypatch.setattr(alpaca, "positions", lambda: {})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {"FIS": 36.0})
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: {})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: False)
    queued = [{"id": "1", "symbol": "FIS", "side": "buy", "qty": "125.932423", "type": "market",
               "time_in_force": "day", "order_class": "", "legs": None}]
    state = {"open": False, "orders": queued}

    def request(m, p, b=None, base=None):
        if p == "/v2/clock":
            return {"is_open": state["open"]}
        if p.startswith("/v2/orders?status=open"):
            return state["orders"]
        raise AssertionError(f"unexpected {m} {p}")

    monkeypatch.setattr(alpaca, "request", request)
    prices = {"FIS": 36.01}
    assert alpaca.already_queued(trades, prices)
    state["orders"] = queued + queued                        # a duplicate: clean up the normal way
    assert not alpaca.already_queued(trades, prices)
    state["orders"] = [dict(queued[0], qty="100")]            # the plan changed
    assert not alpaca.already_queued(trades, prices)
    state["orders"], state["open"] = queued, True            # market open: always the normal path
    assert not alpaca.already_queued(trades, prices)


def test_closed_market_match_includes_the_stops_of_held_positions(monkeypatch):
    from algo import alpaca

    trades = [{"asset": "NVDA", "strategy": "donchian_trend", "qty": 10.4, "stop": 190.12, "target": 240.0}]
    monkeypatch.setattr(alpaca, "positions", lambda: {"NVDA": 10.4})
    monkeypatch.setattr(alpaca, "wanted", lambda live=None, seen=None: {"NVDA": 10.4})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {"NVDA": 200.0})
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: {})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: False)
    oco = {"id": "1", "symbol": "NVDA", "side": "sell", "qty": "10", "type": "limit", "limit_price": "240",
           "time_in_force": "gtc", "order_class": "oco",
           "legs": [{"id": "2", "symbol": "NVDA", "side": "sell", "qty": "10", "type": "stop", "stop_price": "190.12"}]}
    frac = {"id": "3", "symbol": "NVDA", "side": "sell", "qty": "0.4", "type": "stop", "stop_price": "190.12",
            "time_in_force": "day", "order_class": "", "legs": None}
    orders = [oco, frac]
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None:
                        {"is_open": False} if p == "/v2/clock" else orders)
    assert alpaca.already_queued(trades, {"NVDA": 200.0})
    orders.remove(frac)                                       # the fractional day stop expired: re-send
    assert not alpaca.already_queued(trades, {"NVDA": 200.0})


def test_stop_range_starts_after_each_stocks_own_last_bar(monkeypatch, tmp_path):
    """2026-10-20: at 14:01 UTC the crypto bar of 13:00 was final, so equity.csv's last line was 13:00,
    but AAPL's 13:30-14:00 bar was not (stock data is 15 minutes late). The range started at 14:00,
    missed AAPL's stop at the 13:30 open, and the engine would have bought the shares back."""
    import json

    from algo import alpaca

    (tmp_path / "equity.csv").write_text("Date,equity\n2026-10-20 12:00:00,1\n2026-10-20 13:00:00,1\n")
    (tmp_path / "orders.json").write_text(json.dumps([
        {"asset": "AAPL", "qty": 62.8, "stop": 339.08, "target": 357.66, "bar": "2026-10-19 19:00:00"},
        {"asset": "MSFT", "qty": 15.4, "stop": 517.42, "target": 553.3, "bar": "2026-10-20 13:00:00"}]))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    asked = []

    def get_data(path, params):
        asked.append(dict(params))
        bar = lambda t, lo, hi: {"t": t, "l": lo, "h": hi}
        return {"bars": {"AAPL": [bar("2026-10-19T19:59:00Z", 330.0, 331.0),   # before the open: ignored
                                  bar("2026-10-20T13:30:00Z", 338.85, 341.2),  # the opening dip
                                  bar("2026-10-20T14:02:00Z", 341.5, 342.0)],
                         "MSFT": [bar("2026-10-20T13:30:00Z", 500.0, 530.0),   # its 13:00 bar was processed
                                  bar("2026-10-20T14:01:00Z", 528.0, 529.0)]}}

    monkeypatch.setattr(alpaca, "get_data", get_data)
    seen = alpaca.bar_range(["AAPL", "MSFT"])
    assert asked[0]["start"] == "2026-10-19T20:00:00Z"
    assert seen == {"AAPL": (338.85, 342.0), "MSFT": (528.0, 529.0)}
    assert alpaca.through_stop({"asset": "AAPL", "qty": 62.8, "stop": 339.08, "target": 357.66},
                               {"AAPL": 341.6}, seen)


def test_stop_range_without_bar_times_starts_after_the_last_equity_line(monkeypatch, tmp_path):
    import json

    from algo import alpaca

    (tmp_path / "equity.csv").write_text("Date,equity\n2026-10-20 13:00:00,1\n")
    (tmp_path / "orders.json").write_text(json.dumps([{"asset": "AAPL", "qty": 1.0, "stop": 1.0, "target": None}]))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    asked = []
    monkeypatch.setattr(alpaca, "get_data", lambda path, params: asked.append(dict(params)) or {"bars": {}})
    assert alpaca.bar_range(["AAPL"]) == {}
    assert asked[0]["start"] == "2026-10-20T14:00:00Z"


def test_opening_auction_orders_already_queued_are_not_sent_again(monkeypatch, tmp_path):
    """2026-10-22: account C's opening-auction sell of AMZN was cancelled and sent again by the 9:05,
    9:12 and 9:20 runs; the last copy went out at 9:26 and expired unfilled, so the position was sold
    at 9:57 instead of in the auction."""
    import json

    from algo import alpaca

    trades = [{"asset": "FIS", "ticker": "FIS", "strategy": "insider_low_short", "qty": 125.932423,
               "stop": 32.83, "target": None, "mark": 36.01}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    monkeypatch.setitem(alpaca.SYMBOLS, "FIS", "FIS")
    monkeypatch.setattr(alpaca, "positions", lambda: {})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {"FIS": 36.0})
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: {})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: True)
    auction = [{"id": "1", "symbol": "FIS", "side": "buy", "qty": "125.932423", "type": "market",
                "time_in_force": "day", "order_class": "", "legs": None}]
    state = {"orders": auction}

    def request(m, p, b=None, base=None):
        if p == "/v2/clock":
            return {"is_open": False}
        if p.startswith("/v2/orders?status=open"):
            return state["orders"]
        raise AssertionError(f"unexpected {m} {p}")

    monkeypatch.setattr(alpaca, "request", request)
    assert alpaca.already_queued(trades, {"FIS": 36.01})
    state["orders"] = [dict(auction[0], qty="100")]             # the plan changed
    assert not alpaca.already_queued(trades, {"FIS": 36.01})


def test_stop_put_under_the_reference_price_keeps_the_queued_orders(monkeypatch, tmp_path):
    """2026-10-28: before the open Alpaca's reference price for STC was 30.69 (it closed at 43.48), so its
    37.19 stop went in at 30.68 (just under the reference). The open orders never matched the plan's 37.19,
    and every run from 6:53 to 9:23 cancelled and re-sent everything, the queued FFIN buy included."""
    import json

    from algo import alpaca

    trades = [{"asset": "STC", "strategy": "insider_low_short", "qty": 54.253785, "stop": 37.19, "target": None},
              {"asset": "FFIN", "strategy": "insider_low_short", "qty": 181.685915, "stop": 28.12, "target": None,
               "pending": True}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    for s in ("STC", "FFIN"):
        monkeypatch.setitem(alpaca.SYMBOLS, s, s)
    monkeypatch.setattr(alpaca, "positions", lambda: {"STC": 54.253785})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {"STC": 43.48, "FFIN": 30.2})
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: {})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: True)
    refused = alpaca.AlpacaError('POST /v2/orders -> 422: {"code":42210000,"market_price":"30.69",'
                                 '"message":"stop price must be less than current price","stop_price":"37.19"}')
    lower = [alpaca._below_reference({"symbol": "STC", "side": "sell", "qty": q, "type": "stop", "stop_price": 37.19,
                                      "time_in_force": tif}, refused) for q, tif in ((54, "gtc"), (0.253785, "day"))]
    assert [_ for _ in lower if _["stop_price"] == 30.68] == lower
    buy = {"id": "1", "symbol": "FFIN", "side": "buy", "qty": "181.685915", "type": "market", "time_in_force": "day",
           "order_class": "", "legs": None, "client_order_id": "tf-0123"}
    open_ = [buy] + [{"id": str(i + 2), "symbol": "STC", "side": "sell", "qty": str(o["qty"]), "type": "stop",
                      "stop_price": "30.68", "time_in_force": o["time_in_force"], "order_class": "", "legs": None,
                      "client_order_id": o["client_order_id"]} for i, o in enumerate(lower)]
    state = {"orders": open_}
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None:
                        {"is_open": False} if p == "/v2/clock" else state["orders"])
    assert alpaca.already_queued(trades, {"STC": 43.48, "FFIN": 30.2})
    # a lower stop that is not a stand-in (an old level the trailing stop has since raised) still differs
    state["orders"] = [buy] + [dict(o, client_order_id=f"tf-{i}") for i, o in enumerate(open_[1:])]
    assert not alpaca.already_queued(trades, {"STC": 43.48, "FFIN": 30.2})


def test_stand_in_stops_are_tried_again_at_the_planned_level_without_touching_the_queue(monkeypatch, tmp_path):
    """A stop put under Alpaca's reference price stays only until Alpaca accepts the planned level
    (2026-10-27: BBT's reference came back by 18:50): while the market is closed and the queued orders
    match the plan, each run tries the planned stop again; queued market orders stay. Alpaca cannot
    replace an order held for the next session (2026-10-28: "cannot replace order in accepted status"),
    so the stand-in is cancelled and the planned stop sent, or a new stand-in if it is still refused."""
    import json

    from algo import alpaca

    (tmp_path / "config.json").write_text(json.dumps({"name": "A"}))
    (tmp_path / "orders.json").write_text("[]")
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    monkeypatch.setattr(alpaca, "check_account", lambda: "PA1")
    monkeypatch.setattr(alpaca, "last_prices", lambda: {})
    monkeypatch.setattr(alpaca, "already_queued", lambda trades, prices: True)
    monkeypatch.setattr(alpaca, "_wait", lambda check, seconds=20.0: check())
    sent = []

    def send(o):
        if o["symbol"] == "FFIN" and o["stop_price"] > 23.09:  # FFIN: still refused above the reference
            raise alpaca.AlpacaError('POST /v2/orders -> 422: {"code":42210000,"market_price":"23.09",'
                                     '"message":"stop price must be less than current price"}')
        sent.append(o)
        return {"id": f"n{len(sent)}"}

    monkeypatch.setattr(alpaca, "_send", send)
    open_ = [{"id": "s1", "symbol": "BBT", "side": "sell", "qty": "168", "type": "stop", "stop_price": "26.54",
              "time_in_force": "gtc", "client_order_id": "tf-ref288900-aaaa"},
             {"id": "s2", "symbol": "FFIN", "side": "sell", "qty": "181", "type": "stop", "stop_price": "23.08",
              "time_in_force": "gtc", "client_order_id": "tf-ref282800-bbbb"},
             {"id": "m1", "symbol": "XYZ", "side": "buy", "qty": "5", "type": "market", "time_in_force": "day",
              "client_order_id": "tf-cccc"},
             {"id": "s3", "symbol": "CLF", "side": "sell", "qty": "148", "type": "stop", "stop_price": "11.33",
              "time_in_force": "gtc", "client_order_id": "tf-dddd"}]
    calls = []

    def request(m, p, b=None, base=None):
        calls.append((m, p, b))
        if m == "GET" and p.startswith("/v2/orders?status=open"):
            return open_
        if m == "DELETE":
            return {}
        if m == "GET" and p.startswith("/v2/orders/s"):
            return {"status": "canceled"}
        raise AssertionError((m, p))

    monkeypatch.setattr(alpaca, "request", request)
    assert alpaca.sync(send=True) == []
    assert [p for m, p, b in calls if m == "DELETE"] == ["/v2/orders/s1", "/v2/orders/s2"]  # stand-ins only
    assert [(o["symbol"], o["qty"], o["stop_price"], o["time_in_force"]) for o in sent] == [
        ("BBT", 168.0, 28.89, "gtc"), ("FFIN", 181.0, 23.08, "gtc")]
    assert "client_order_id" not in sent[0] and sent[1]["client_order_id"].startswith("tf-ref282800-")


def test_opening_auction_orders_stop_five_minutes_before_the_open():
    from algo import alpaca

    clock = lambda mins: {"is_open": False, "timestamp": "2026-10-22T09:00:00.000000000-04:00",  # noqa: E731
                          "next_open": f"2026-10-22T09:{mins:02d}:00-04:00"}
    assert alpaca.opening_auction(clock(30)) and alpaca.opening_auction(clock(5))
    assert not alpaca.opening_auction(clock(4))      # 9:26: a plain market order, filled at the open


def _aapl_auction(monkeypatch, tmp_path):
    """Account A on 2026-10-23 before the open: 61.13 AAPL held, a second AAPL trade bought at the open."""
    import json

    from algo import alpaca

    trades = [{"asset": "AAPL", "strategy": "donchian_trend", "qty": 61.134829, "stop": 343.6, "target": 358.07},
              {"asset": "AAPL", "strategy": "donchian_trend", "qty": 77.921665, "stop": 343.6, "target": 358.07}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    monkeypatch.setattr(alpaca, "positions", lambda: {"AAPL": 61.134829})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {s: 348.0 for s in syms})
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: {})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: True)
    return trades


def test_auction_buy_of_a_held_stock_keeps_its_orders_queued(monkeypatch, tmp_path):
    """2026-10-23: Alpaca refused the stop of A's 0.13 fractional AAPL share next to the queued AAPL
    buy ("potential wash trade"), so the open orders never matched the plan and the 9:12 run cancelled
    and re-sent everything, the auction buy included."""
    from algo import alpaca

    trades = _aapl_auction(monkeypatch, tmp_path)
    open_ = [{"id": "1", "symbol": "AAPL", "side": "buy", "qty": "77.921665", "type": "market",
              "time_in_force": "day", "order_class": "", "legs": None},
             {"id": "3", "symbol": "AAPL", "side": "sell", "qty": "61", "type": "limit", "limit_price": "358.07",
              "time_in_force": "gtc", "order_class": "oco",
              "legs": [{"id": "4", "type": "stop", "stop_price": "343.6"}]}]
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None:
                        {"is_open": False} if p == "/v2/clock" else open_)
    assert alpaca.already_queued(trades, {"AAPL": 348.42})


def test_stop_next_to_a_pending_buy_waits_for_the_next_run(monkeypatch, tmp_path, capsys):
    from algo import alpaca, notify

    trades = _aapl_auction(monkeypatch, tmp_path)
    sent = []
    monkeypatch.setattr(alpaca, "_send", lambda o: sent.append(o) or {"id": f"id{len(sent)}"})
    monkeypatch.setattr(alpaca, "_wait", lambda check, seconds=20.0: check())
    monkeypatch.setattr(notify, "send", lambda *a, **k: True)

    def request(m, p, b=None, base=None):
        if p == "/v2/clock":
            return {"is_open": False}
        if p.startswith("/v2/orders/id"):
            o = sent[int(p.rsplit("id", 1)[1]) - 1]
            return {"status": "accepted", "side": o["side"], "qty": str(o["qty"]), "filled_qty": "0"}
        if p == "/v2/account":
            return {"equity": "96000"}
        raise AssertionError(p)

    monkeypatch.setattr(alpaca, "request", request)
    alpaca._trade_and_protect(True, trades, {"AAPL": 348.42})
    assert [(o["side"], o["qty"], o["time_in_force"], o.get("order_class", "")) for o in sent] == [
        ("buy", 77.921665, "day", ""), ("sell", 61, "gtc", "oco")]
    assert "0.134829 AAPL     stop 343.6" in capsys.readouterr().out


def test_daily_account_range_covers_the_session_after_its_last_bar(monkeypatch, tmp_path):
    """2026-10-23: account D's PRIM stop (63.76) filled at 9:45 (low 62.60); at 10:50 the price was back
    at 64 and, with no range for a daily account, the run bought PRIM back."""
    import json

    from algo import alpaca

    (tmp_path / "orders.json").write_text(json.dumps([
        {"asset": "PRIM", "qty": 32.34, "stop": 63.7567, "target": None, "bar": "2026-10-22"},
        {"asset": "PEP", "qty": 48.9, "stop": 130.47, "target": None}]))      # no bar: no range
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    calls = []

    def fake(path, params):
        calls.append(dict(params))
        return {"bars": {"PRIM": [{"t": "2026-10-23T12:00:00Z", "l": 60.0, "h": 61.0},   # pre-market
                                  {"t": "2026-10-23T13:45:00Z", "l": 62.595, "h": 65.1},
                                  {"t": "2026-10-23T14:50:00Z", "l": 63.9, "h": 64.4}]}}

    monkeypatch.setattr(alpaca, "get_data", fake)
    seen = alpaca.bar_range(["PEP", "PRIM"])
    assert calls[0]["start"] == "2026-10-23T00:00:00Z" and calls[0]["symbols"] == "PRIM"
    assert seen == {"PRIM": (62.595, 65.1)}
    assert alpaca.through_stop({"asset": "PRIM", "qty": 32.34, "stop": 63.7567}, {"PRIM": 64.3}, seen)


def test_holdings_without_a_stop_need_no_stop_order(monkeypatch, tmp_path):
    """From 26 Oct 2026: A keeps its idle cash in SPY and B holds monthly ETFs, both without stops."""
    import json

    from algo import alpaca

    trades = [{"asset": "SPY", "qty": 120.5, "stop": None, "target": None, "mark": 760.0},
              {"asset": "FIS", "qty": 10.0, "stop": 34.89, "target": None, "mark": 37.5}]
    assert alpaca.protect("SPY", 120.5, trades[:1], 760.0) == []
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    stop = {"symbol": "FIS", "side": "sell", "type": "stop", "qty": "10"}
    _fake_alpaca(monkeypatch, {"SPY": 120.5, "FIS": 10.0}, [stop], {"SPY": 120.5, "FIS": 10.0})
    assert alpaca.verify() == []
    _fake_alpaca(monkeypatch, {"SPY": 120.5, "FIS": 10.0}, [], {"SPY": 120.5, "FIS": 10.0})
    assert alpaca.verify() == ["FIS: 10 held, only 0 covered by a stop"]       # the stock still needs its stop


def test_queued_sales_of_stocks_the_plan_no_longer_holds_count_as_queued(monkeypatch, tmp_path):
    """2026-10-26: A's switch sold AAPL and USO, which are not in its new orders.json, so the check had no
    price for them, left their sales out of the plan, and the 9:12 and 9:20 runs cancelled and re-sent
    every opening-auction order."""
    import json

    from algo import alpaca

    trades = [{"asset": "SPY", "qty": 121.767363, "stop": None, "target": None, "mark": 759.97}]
    (tmp_path / "orders.json").write_text(json.dumps(trades))
    monkeypatch.setattr(alpaca, "PAPER_DIR", tmp_path)
    monkeypatch.setattr(alpaca, "positions", lambda: {"AAPL": 139.056494})
    monkeypatch.setattr(alpaca, "live_prices", lambda syms: {s: {"SPY": 760.0, "AAPL": 344.0}[s] for s in syms})
    monkeypatch.setattr(alpaca, "bar_range", lambda syms: {})
    monkeypatch.setattr(alpaca, "opening_auction", lambda clock: True)
    queued = [{"symbol": "AAPL", "side": "sell", "type": "market", "time_in_force": "day", "qty": "139.056494"},
              {"symbol": "SPY", "side": "buy", "type": "market", "time_in_force": "day", "qty": "121.767363"}]
    monkeypatch.setattr(alpaca, "request", lambda m, p, b=None, base=None:
                        {"is_open": False} if p == "/v2/clock" else queued)
    assert alpaca.already_queued(trades, alpaca.last_prices())
