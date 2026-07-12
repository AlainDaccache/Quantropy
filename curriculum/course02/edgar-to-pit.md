---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Course C2 — Filings to Point-in-Time: SEC EDGAR `[deep]`

**Learning objectives.** After this lesson you can: (1) pull structured fundamentals
from SEC EDGAR's free XBRL API; (2) explain why EDGAR is *natively bitemporal* and
load it into a `PointInTimeStore`; (3) recognize two real-world XBRL warts — concept
drift and the quarterly/annual ambiguity — before they poison a backtest.

## 1. Intuition

EDGAR is the rare free data source that is *honest about time*: every XBRL fact
carries both the period it describes (`end`) and the date it was filed (`filed`) —
exactly the **event date** and **knowledge date** of the previous lesson. Restatements
aren't a data-cleaning nightmare; they're just the same period filed again later.

## 2. Applied — real Apple filings

This lesson runs on a committed, *trimmed but real* extract of Apple's company facts
(fetched once from `data.sec.gov`, periods 2021–2023) so it executes offline in CI.
The one-line live path is shown at the end.

```{code-cell} ipython3
import json
from quantropy.data.providers.edgar import facts_to_pit_records

facts = json.load(open("../../tests/fixtures/aapl_facts_trimmed.json"))
facts["entityName"], list(facts["facts"]["us-gaap"].keys())
```

**Wart #1 — concept drift.** Apple's `Revenues` tag is empty in this era: after the
ASC 606 accounting standard, revenue lives under
`RevenueFromContractWithCustomerExcludingAssessedTax`. Concept names vary by company
and by era — hardcoding one tag across a universe silently drops companies.

```{code-cell} ipython3
REV = "RevenueFromContractWithCustomerExcludingAssessedTax"
quarterly = facts_to_pit_records(facts, [REV], duration="quarterly")
quarterly[["event_date", "knowledge_date", "value"]].head()
```

That first row is real: fiscal Q2-2021 revenue of $89.58B, knowable from 2021-04-29 —
the 10-Q filing date. Now the annual view:

```{code-cell} ipython3
annual = facts_to_pit_records(facts, [REV], duration="annual")
annual[["event_date", "knowledge_date", "value"]]
```

**Wart #2 — the duration ambiguity.** A fact ending 2022-09-24 could be Q4 (three
months) or the full fiscal year (twelve). Both share the same `end`. That's why
`facts_to_pit_records` *requires* a `duration` — collapsing them into one key would
average quarters into years somewhere deep in a factor, and nothing would error.

## 3. Into the point-in-time store

```{code-cell} ipython3
from quantropy.data import PointInTimeStore

pit = PointInTimeStore.from_frame(quarterly)

# A backtest running on 2022-02-01 sees exactly the quarters then knowable:
pit.as_of("2022-02-01")[["event_date", "knowledge_date", "value"]]
```

Three quarters — the latest being the $123.945B holiday quarter filed four days
earlier. Nothing from the future. This frame is safe to feed a valuation model or a
fundamental factor *as of that date* (Course C4 does exactly that).

## 4. The live path

With the `[data]` extra installed and `EDGAR_USER_AGENT` set in your `.env`
(SEC's fair-access policy requires a contact):

```python
from quantropy.data.providers import edgar, use_system_trust

use_system_trust()                      # only if your machine's certifi can't verify sec.gov
cik = edgar.ticker_to_cik("AAPL")       # 320193
facts = edgar.fetch_company_facts(cik)  # then snapshot it — fetch once, work offline
```

## 5. Pitfalls

- **Knowledge date ≈ filing date** — earnings are *press-released* days before the
  10-Q hits EDGAR. Treating `filed` as the knowledge date is conservative (late), which
  is the safe direction for a backtest.
- **Dedup ≠ restatement.** The same value re-listed in next quarter's comparatives is
  noise (we keep the earliest); a *changed* value for the same period is a restatement
  (we keep both). Conflating them either destroys the PIT record or double-counts.
- **One company ≠ the universe.** Concept coverage varies wildly across filers;
  production pipelines map many tags per economic concept and log coverage.

## 6. Exercises

1. Load `NetIncomeLoss` quarterly and find Apple's most profitable quarter in the
   fixture window.
2. `Assets` is an *instant* concept. What happens if you request it with
   `duration="quarterly"`, and why is that the correct behavior?
3. Using the synthetic-restatement pattern from the tests
   (`tests/test_edgar.py::TestRestatementFlow`), show `as_of` flipping from the
   original to the restated value.

## Further reading

`docs/REFERENCES.md` §1 (leakage), §6 (financial-statement analysis). SEC's
`data.sec.gov` API docs for the `companyconcept` and `frames` endpoints.
