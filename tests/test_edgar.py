"""Tests for the EDGAR provider — offline, against a trimmed *real* AAPL facts fixture
(fetched from data.sec.gov, periods 2021–2023) plus synthetic restatement cases.

External reference values are checkable against Apple's actual filings: Q1-FY2022
revenue $123.945B (10-Q filed 2022-01-28), FY2022 revenue $394.328B (10-K).
"""

import json
from pathlib import Path

import pytest

from quantropy.data import PointInTimeStore
from quantropy.data.providers import edgar

FIXTURE = Path(__file__).parent / "fixtures" / "aapl_facts_trimmed.json"
REVENUE = "RevenueFromContractWithCustomerExcludingAssessedTax"


@pytest.fixture(scope="module")
def aapl():
    return json.loads(FIXTURE.read_text())


class TestTickerToCik:
    def test_offline_lookup(self):
        table = {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}
        assert edgar.ticker_to_cik("aapl", tickers_table=table) == 320193

    def test_unknown_ticker_raises(self):
        with pytest.raises(KeyError):
            edgar.ticker_to_cik("ZZZZZZ", tickers_table={})


class TestHeaders:
    def test_missing_user_agent_raises(self, monkeypatch):
        monkeypatch.delenv("EDGAR_USER_AGENT", raising=False)
        with pytest.raises(RuntimeError, match="EDGAR_USER_AGENT"):
            edgar._headers()

    def test_user_agent_used(self, monkeypatch):
        monkeypatch.setenv("EDGAR_USER_AGENT", "Test test@example.com")
        assert edgar._headers()["User-Agent"] == "Test test@example.com"


class TestFactsToPitRecords:
    def test_quarterly_reference_value(self, aapl):
        """Q1-FY2022 (period ended 2021-12-25) revenue: $123.945B, filed 2022-01-28."""
        rec = edgar.facts_to_pit_records(aapl, [REVENUE], duration="quarterly")
        q1 = rec[rec["event_date"] == "2021-12-25"]
        assert len(q1) == 1
        assert q1["value"].item() == pytest.approx(123_945_000_000)
        assert str(q1["knowledge_date"].item().date()) == "2022-01-28"

    def test_annual_reference_value(self, aapl):
        """FY2022 (ended 2022-09-24) revenue: $394.328B."""
        rec = edgar.facts_to_pit_records(aapl, [REVENUE], duration="annual")
        fy22 = rec[rec["event_date"] == "2022-09-24"]
        assert fy22["value"].item() == pytest.approx(394_328_000_000)

    def test_quarterly_and_annual_do_not_mix(self, aapl):
        """The Dec-year-end ambiguity: no annual row may appear under 'quarterly'."""
        q = edgar.facts_to_pit_records(aapl, [REVENUE], duration="quarterly")
        a = edgar.facts_to_pit_records(aapl, [REVENUE], duration="annual")
        assert set(q["value"]).isdisjoint(set(a["value"]))
        assert (q["value"] < 130e9).all()  # no quarter in window tops FY revenue
        assert (a["value"] > 250e9).all()

    def test_instant_concept(self, aapl):
        rec = edgar.facts_to_pit_records(aapl, ["Assets"], duration="instant")
        assert len(rec) > 0
        # entity name comes from the document
        assert (rec["entity"] == "Apple Inc.").all()

    def test_missing_concept_raises(self, aapl):
        with pytest.raises(KeyError, match="NotAConcept"):
            edgar.facts_to_pit_records(aapl, ["NotAConcept"], duration="instant")

    def test_wrong_unit_raises(self, aapl):
        with pytest.raises(KeyError, match="EUR"):
            edgar.facts_to_pit_records(aapl, ["Assets"], duration="instant", unit="EUR")

    def test_invalid_duration_raises(self, aapl):
        with pytest.raises(ValueError, match="duration"):
            edgar.facts_to_pit_records(aapl, ["Assets"], duration="monthly")


def synthetic_facts(values_by_filing):
    """Minimal EDGAR-shaped document: one quarterly period, filed multiple times."""
    return {
        "cik": 1,
        "entityName": "SYNTH",
        "facts": {
            "us-gaap": {
                "NetIncomeLoss": {
                    "units": {
                        "USD": [
                            {
                                "start": "2023-10-01",
                                "end": "2023-12-31",
                                "val": val,
                                "filed": filed,
                                "form": form,
                            }
                            for filed, val, form in values_by_filing
                        ]
                    }
                }
            }
        },
    }


class TestRestatementFlow:
    def test_restatement_preserved_and_pit_correct(self):
        facts = synthetic_facts(
            [
                ("2024-02-01", 2.10e9, "10-Q"),  # original
                ("2024-03-15", 1.80e9, "10-K/A"),  # restated
            ]
        )
        rec = edgar.facts_to_pit_records(facts, ["NetIncomeLoss"], duration="quarterly")
        assert len(rec) == 2  # both filings survive — restatements are data, not noise

        pit = PointInTimeStore.from_frame(rec)
        feb = pit.as_of("2024-02-10")
        apr = pit.as_of("2024-04-01")
        assert feb["value"].item() == pytest.approx(2.10e9)  # as the market saw it
        assert apr["value"].item() == pytest.approx(1.80e9)  # as it truly was

    def test_identical_refilings_deduped(self):
        facts = synthetic_facts(
            [
                ("2024-02-01", 2.10e9, "10-Q"),
                ("2024-05-01", 2.10e9, "10-Q"),  # same value re-listed next quarter
            ]
        )
        rec = edgar.facts_to_pit_records(facts, ["NetIncomeLoss"], duration="quarterly")
        assert len(rec) == 1  # noise dropped, earliest knowledge_date kept
        assert str(rec["knowledge_date"].item().date()) == "2024-02-01"
