import pandas as pd

from algo import insider

XML = """<ownershipDocument><reportingOwner><reportingOwnerId><rptOwnerCik>0001</rptOwnerCik></reportingOwnerId></reportingOwner>
<aff10b5One>0</aff10b5One>
<nonDerivativeTable>
<nonDerivativeTransaction><transactionCoding><transactionCode>P</transactionCode></transactionCoding>
<transactionAmounts><transactionShares><value>1000</value></transactionShares>
<transactionPricePerShare><value>50.5</value></transactionPricePerShare></transactionAmounts></nonDerivativeTransaction>
<nonDerivativeTransaction><transactionCoding><transactionCode>F</transactionCode></transactionCoding>
<transactionAmounts><transactionShares><value>10</value></transactionShares></transactionAmounts></nonDerivativeTransaction>
</nonDerivativeTable></ownershipDocument>"""


def test_parse_keeps_open_market_trades_only():
    rows = insider.parse(XML)
    assert rows == [{"owner": "0001", "code": "P", "shares": 1000.0, "price": 50.5, "value": 50500.0, "plan": 0}]


def test_features_use_the_filing_time_not_the_trade_time():
    tx = pd.DataFrame([{"accession": "a", "accepted": "2026-03-02T21:00:00.000Z", "owner": "1", "code": "P",
                        "value": 1e6, "plan": 0}])
    idx = pd.DatetimeIndex(["2026-03-02 20:00", "2026-03-03 14:00", "2026-07-01 14:00"])
    f = insider.features(idx, tx)
    assert f["insider_buyers_90d"].tolist() == [0.0, 1.0, 0.0]  # before the filing / after / 90 days later
    assert f["insider_buy_90d"].iloc[1] > 13
