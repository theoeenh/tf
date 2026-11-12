"""Shared test setup."""
import pytest


@pytest.fixture(autouse=True)
def no_membership_history(request, tmp_path, monkeypatch):
    """The finder tests use made-up tickers: they run without the real index-membership history
    (data/wide/members_history.csv), i.e. on a fixed list of stocks, unless a test builds its own table
    (tests/test_wide_pit.py, and the tests that ask for the `table` fixture)."""
    from algo import wide_pit

    if "table" in request.fixturenames:
        return
    monkeypatch.setattr(wide_pit, "PATH", tmp_path / "no_members_history.csv")
    wide_pit._cache.clear()
