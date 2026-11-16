"""The SEC wants a contact in the User-Agent. The one in the code is the user's own: it may be sent from
the GitHub Actions workflows the user set up, or wherever SEC_CONTACT is set, never from another machine
(2026-11-16: the morning routine's research update sent it from the assistant's container)."""
import pandas as pd
import pytest

from algo import insider


@pytest.fixture
def sec(monkeypatch, tmp_path):
    monkeypatch.setattr(insider, "INSIDER_DIR", tmp_path)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("SEC_CONTACT", raising=False)
    monkeypatch.setattr(insider.time, "sleep", lambda s: None)
    asked = []

    class Answer:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"{}"

    def urlopen(req, timeout=None):
        asked.append(dict(req.header_items()))
        return Answer()

    monkeypatch.setattr(insider.urllib.request, "urlopen", urlopen)
    return asked


def test_outside_github_nothing_goes_to_the_sec(sec, tmp_path):
    pd.DataFrame({"accession": ["a"], "accepted": ["2026-11-13T21:00:00"], "code": ["P"]}).to_csv(
        tmp_path / "MSFT.csv", index=False)
    with pytest.raises(OSError, match="GitHub"):
        insider._get("https://data.sec.gov/submissions/CIK0000789019.json")
    assert sec == []
    assert list(insider.load("MSFT")["accession"]) == ["a"]           # the research book keeps its cache
    assert sec == []


def test_on_github_the_workflows_contact_is_sent(sec, monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    insider._get("https://data.sec.gov/x.json")
    assert sec[0]["User-agent"] == insider.UA["User-Agent"]


def test_a_contact_set_in_the_environment_is_used(sec, monkeypatch):
    monkeypatch.setenv("SEC_CONTACT", "research desk research@example.org")
    insider._get("https://data.sec.gov/x.json")
    assert sec[0]["User-agent"] == "tf-research research desk research@example.org"
