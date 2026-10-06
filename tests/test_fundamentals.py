import json

import numpy as np
import pandas as pd

from algo import fundamentals as F


def _fact(start, end, val, filed, form="10-Q"):
    return {"start": start, "end": end, "val": val, "filed": filed, "form": form}


def test_quarters_from_year_to_date_and_first_filed_wins():
    facts = {"NetIncomeLoss": {"units": {"USD": [
        _fact("2020-01-01", "2020-03-31", 10, "2020-05-01"),
        _fact("2020-01-01", "2020-06-30", 25, "2020-08-01"),         # 6 months: Q2 = 15
        _fact("2020-01-01", "2020-09-30", 45, "2020-11-01"),         # 9 months: Q3 = 20
        _fact("2020-01-01", "2020-12-31", 70, "2021-02-20", "10-K"),  # year: Q4 = 25
        _fact("2020-01-01", "2020-03-31", 99, "2021-05-01"),         # restated later: ignored
    ]}}}
    q = F.quarters(F._facts(facts, ["NetIncomeLoss"]))
    assert list(q["val"]) == [10, 15, 20, 25]
    assert q["filed"].iloc[-1] == pd.Timestamp("2021-02-20")


def test_features_only_after_the_filing_day():
    rows = []
    for k, (end, filed) in enumerate([("2020-03-31", "2020-05-01"), ("2020-06-30", "2020-08-03"),
                                      ("2020-09-30", "2020-11-02"), ("2020-12-31", "2021-02-19")]):
        rows += [("S", "ni_q", end, filed, 10.0 * (k + 1)), ("S", "cfo_q", end, filed, 10.0)]
    rows += [("S", "assets", "2020-12-31", "2021-02-19", 1000.0), ("S", "shares", "2021-01-31", "2021-02-19", 10.0),
             ("S", "equity", "2020-12-31", "2021-02-19", 500.0)]
    df = pd.DataFrame(rows, columns=["ticker", "item", "end", "filed", "val"])
    df["end"], df["filed"] = pd.to_datetime(df["end"]), pd.to_datetime(df["filed"])
    F_load = F.load
    try:
        F.load = lambda: df
        dates = pd.DatetimeIndex(["2021-02-12", "2021-02-19", "2021-02-26"])
        close = pd.DataFrame({"S": [10.0, 10.0, 10.0]}, dates)
        f = F.features(dates, close)
    finally:
        F.load = F_load
    # TTM net income 100 known only after the 10-K of 2021-02-19 (from the next session)
    assert np.isnan(f["f_roa"]["S"].iloc[0]) and np.isnan(f["f_roa"]["S"].iloc[1])
    assert f["f_roa"]["S"].iloc[2] == 100 / 1000
    assert f["f_ey"]["S"].iloc[2] == 100 / (10 * 10)
    assert f["f_accr"]["S"].iloc[2] == (100 - 40) / 1000
    assert f["f_bm"]["S"].iloc[2] == 500 / 100


def test_parse_company_reads_gaap_and_shares():
    d = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [_fact("2020-01-01", "2020-03-31", 5, "2020-05-01")]}},
                               "Assets": {"units": {"USD": [{"end": "2020-03-31", "val": 9, "filed": "2020-05-01", "form": "10-Q"}]}}},
                   "dei": {"EntityCommonStockSharesOutstanding": {"units": {"shares": [
                       {"end": "2020-04-25", "val": 3, "filed": "2020-05-01", "form": "10-Q"}]}}}}}
    out = F.parse_company(json.dumps(d).encode())
    assert set(out["item"]) == {"rev_q", "assets", "shares"}
