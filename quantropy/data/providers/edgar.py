"""SEC EDGAR provider — filings facts with true point-in-time dates. Free, keyless.

EDGAR's XBRL "company facts" API reports every fact with both the period it
describes (``end``) and the date it was filed (``filed``) — i.e. **event date and
knowledge date**, natively bitemporal. Restatements show up as the same period
re-reported in a later filing, which drops straight into
:class:`quantropy.data.pit.PointInTimeStore` with no reconstruction.

Endpoints (all JSON):

- ``https://www.sec.gov/files/company_tickers.json``          — ticker → CIK
- ``https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`` — all facts

SEC fair-access policy requires a descriptive ``User-Agent`` with a contact —
set ``EDGAR_USER_AGENT`` in your ``.env`` (see ``.env.example``); requests are
also rate-limited (max 10/s) on their side. Fetch once → snapshot → work offline.

One real subtlety, handled explicitly: *duration* facts (e.g. Revenues) with the
same ``end`` can describe different windows — Q4 (3 months) and the full year (12
months) both end on Dec 31. Collapsing them into one (entity, field, event_date)
key would silently mix quarterly and annual values, so :func:`facts_to_pit_records`
requires a ``duration`` choice for duration concepts.
"""

from __future__ import annotations

import os

import pandas as pd

__all__ = ["ticker_to_cik", "fetch_company_facts", "facts_to_pit_records"]

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:0>10}.json"


def _headers() -> dict[str, str]:
    agent = os.environ.get("EDGAR_USER_AGENT")
    if not agent:
        raise RuntimeError(
            "EDGAR_USER_AGENT is not set. SEC fair-access policy requires a "
            "descriptive User-Agent with contact info, e.g. "
            "'YourName your@email.com' — put it in .env (see .env.example)."
        )
    return {"User-Agent": agent, "Accept-Encoding": "gzip, deflate"}


def ticker_to_cik(ticker: str, tickers_table: dict | None = None) -> int:
    """Resolve a ticker to its SEC CIK. Pass ``tickers_table`` to stay offline."""
    if tickers_table is None:
        import requests  # deferred: [data] extra

        resp = requests.get(_TICKERS_URL, headers=_headers(), timeout=30)
        resp.raise_for_status()
        tickers_table = resp.json()
    want = ticker.upper()
    for row in tickers_table.values():
        if row["ticker"].upper() == want:
            return int(row["cik_str"])
    raise KeyError(f"ticker {ticker!r} not found in EDGAR company_tickers")


def fetch_company_facts(cik: int) -> dict:
    """Fetch the full XBRL company-facts document for a CIK. Network."""
    import requests  # deferred: [data] extra

    resp = requests.get(_FACTS_URL.format(cik=cik), headers=_headers(), timeout=60)
    resp.raise_for_status()
    return resp.json()


def _months_between(start: pd.Timestamp, end: pd.Timestamp) -> float:
    return (end - start).days / 30.44


def facts_to_pit_records(
    facts: dict,
    concepts: list[str],
    duration: str,
    taxonomy: str = "us-gaap",
    unit: str = "USD",
) -> pd.DataFrame:
    """Flatten EDGAR company facts into PointInTimeStore records.

    ``duration`` — ``"instant"`` (balance-sheet concepts: Assets, equity),
    ``"quarterly"`` (~3-month windows) or ``"annual"`` (~12-month windows) for
    flow concepts (Revenues, NetIncomeLoss). Explicit because a Dec-31 ``end``
    is ambiguous between Q4 and FY — mixing them poisons the store.

    Returns columns ``entity, field, event_date, knowledge_date, value`` — feed
    directly to :meth:`PointInTimeStore.from_frame`. The same period filed
    multiple times (10-Q then 10-K, or an amendment) yields multiple rows with
    increasing ``knowledge_date`` — restatements, preserved by design.
    """
    if duration not in ("instant", "quarterly", "annual"):
        raise ValueError(f"duration must be instant|quarterly|annual, got {duration!r}")
    entity = facts.get("entityName") or str(facts.get("cik", "UNKNOWN"))
    rows: list[list] = []
    taxo = facts.get("facts", {}).get(taxonomy, {})
    for concept in concepts:
        if concept not in taxo:
            raise KeyError(f"concept {concept!r} not present under {taxonomy!r}")
        units = taxo[concept].get("units", {})
        if unit not in units:
            raise KeyError(f"unit {unit!r} not available for {concept!r} (has {list(units)})")
        for fact in units[unit]:
            end = pd.Timestamp(fact["end"])
            start = fact.get("start")
            if duration == "instant":
                if start is not None:
                    continue  # duration fact under an instant request — skip
            else:
                if start is None:
                    continue  # instant fact under a duration request — skip
                months = _months_between(pd.Timestamp(start), end)
                if duration == "quarterly" and not (2.0 <= months <= 4.0):
                    continue
                if duration == "annual" and not (10.0 <= months <= 14.0):
                    continue
            filed = pd.Timestamp(fact["filed"])
            rows.append([entity, concept, end, filed, float(fact["val"])])
    frame = pd.DataFrame(
        rows, columns=["entity", "field", "event_date", "knowledge_date", "value"]
    )
    # EDGAR occasionally re-lists identical values across filings; keep the earliest
    # filing of each identical (field, period, value) and any later *changed* value —
    # dedup noise, preserve true restatements.
    frame = (
        frame.sort_values("knowledge_date", kind="stable")
        .drop_duplicates(subset=["entity", "field", "event_date", "value"], keep="first")
        .reset_index(drop=True)
    )
    return frame
