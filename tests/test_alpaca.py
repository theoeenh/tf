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
