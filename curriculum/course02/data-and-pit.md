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

# Course C2 — Data & Point-in-Time: Why Backtests Lie `[deep]`

**Learning objectives.** After this lesson you can: (1) explain the two dates every
observation carries and query "the world as of a date"; (2) demonstrate — with code —
how restatements and survivorship silently inflate backtests; (3) pin data to an
immutable snapshot so results reproduce forever.

## 1. Intuition

Most backtests don't fail because the math is wrong. They fail because the *data*
quietly contains the future:

- **Restatements** — the database shows Q4 earnings as they were *later corrected*,
  not as the market saw them on earnings day.
- **Survivorship** — today's index members exclude everyone who died along the way;
  backtesting on them means betting only on horses you already know finished.
- **Silent revisions** — the vendor backfills history, and last year's backtest is
  unrepeatable.

Quantropy's data layer makes each of these *structurally* hard to commit.

## 2. The bitemporal idea

Every observation carries two dates: the **event date** (the period the value
describes) and the **knowledge date** (when the market could first know it). A
point-in-time query returns only what was knowable:

```{code-cell} ipython3
from quantropy.data import PointInTimeStore

pit = PointInTimeStore()
# ACME's Q4-2023 EPS: first reported Feb 1 as $2.10... restated Mar 15 to $1.80
pit.record("ACME", "eps", event_date="2023-12-31", knowledge_date="2024-02-01", value=2.10)
pit.record("ACME", "eps", event_date="2023-12-31", knowledge_date="2024-03-15", value=1.80)

pit.as_of("2024-02-10")  # a backtest running on Feb 10 sees...
```

```{code-cell} ipython3
pit.as_of("2024-04-01")  # ...while an April backtest sees the restated truth
```

The naive approach — one row per period, updated in place — would feed the February
strategy the $1.80 that didn't exist yet. If EPS drives your signal, you just traded
on information from six weeks in the future, and your backtest will look *better*
than reality precisely when the company disappoints.

```{code-cell} ipython3
# The "current view" — every restatement applied — is exactly the WRONG
# frame to backtest on:
pit.latest()
```

## 3. Survivorship: the graveyard matters

```{code-cell} ipython3
import pandas as pd
from quantropy.data import Universe

u = Universe(pd.DataFrame({
    "symbol": ["AAA", "BBB", "CCC"],
    "start":  ["2010-01-01", "2010-01-01", "2010-01-01"],
    "end":    [None, "2018-03-01", "2020-09-15"],   # BBB and CCC didn't make it
}))

u.members("2016-01-04")   # who a 2016 backtest must include
```

```{code-cell} ipython3
u.members("2024-01-04")   # who survived — backtesting only these flatters every strategy
```

A strategy tested only on `["AAA"]` never held BBB through its 2018 delisting. The
loss you never simulated is return you never earned — classic estimates put the
survivorship inflation at 1–4% *per year* for equity strategies.

## 4. Snapshots: the same data, forever

```{code-cell} ipython3
import tempfile
from quantropy.data import SnapshotStore

store = SnapshotStore(tempfile.mkdtemp())
idx = pd.date_range("2024-01-01", periods=5, freq="B", name="Date")
prices = pd.DataFrame({"SPY": [470.0, 471.5, 469.8, 472.1, 473.0]}, index=idx)

store.write("2024-01-demo", {"prices": prices}, note="lesson demo")
store.read("2024-01-demo", "prices")
```

Snapshots are **immutable** — writing the same id twice raises. A `BacktestConfig`
pins a snapshot id, so a rerun after the vendor "improves" history still reads the
bytes the original run read. Real providers (e.g. the keyless Stooq fetcher in
`quantropy.data.providers`) follow the pattern: *fetch once → snapshot → work
offline*.

## 5. Pitfalls

- **PIT protects data, not features.** Even with a PIT store, standardizing a factor
  over its *full-sample* mean/vol leaks the future into every historical row. The
  feature contract (Course C8) is the other half of the defense.
- **Knowledge dates are hard.** Filing timestamps are a good proxy, but pre-release
  leaks, after-hours filings, and vendor lag all blur "when the market knew." Treat
  the knowledge date as *no earlier than* the truth.
- **Free data has gaps.** Stooq lacks delisted names — so a fully survivorship-free
  free-data universe is genuinely difficult. We say so rather than pretend
  (`[deep]`-track work uses what's verifiably free; the caveat travels with it).

## 6. Exercises

1. Add a Q1-2024 EPS report (event 2024-03-31, knowledge 2024-05-01, value 0.95) and
   show `as_of("2024-04-15")` still returns only Q4.
2. Record a *same-day* correction (equal knowledge dates) and verify the correction
   wins.
3. Why does `PointInTimeStore` refuse `knowledge_date < event_date`? Construct the
   rejected call.

## Further reading

`docs/REFERENCES.md` §1 — López de Prado (2018) on leakage and purging; the
survivorship discussions in Bailey & López de Prado; §3 — Chan (2008) on data
pitfalls in backtesting.
