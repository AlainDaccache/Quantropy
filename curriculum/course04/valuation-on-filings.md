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

# Module 4 (IV) — Valuation on Real Filings: Apple, PIT-Clean `[deep]`

**Learning objectives.** After this lesson you can: (1) build as-reported
statements from raw filings through the point-in-time store; (2) read a DuPont
decomposition and explain a 197% ROE without flinching; (3) run a DCF *backwards*
— extracting what the market price already believes; (4) score quality and
distress from primary-source formulas.

## 1. Intuition

Valuation is the discipline of pricing a claim on future cash flows using only
what is knowable today. Every number below comes from **Apple's actual SEC
filings** (the committed EDGAR fixture) through the PIT store — so the analysis is
exactly what an analyst could have produced in December 2022, restatements and
hindsight excluded by construction.

## 2. From filings to statements

```{code-cell} ipython3
import json
import pandas as pd

from quantropy.data import PointInTimeStore
from quantropy.data.providers import edgar
from quantropy.valuation import StatementSet

facts = json.load(open("../../tests/fixtures/aapl_facts_trimmed.json"))

FLOWS = ["RevenueFromContractWithCustomerExcludingAssessedTax", "NetIncomeLoss",
         "GrossProfit", "OperatingIncomeLoss",
         "NetCashProvidedByUsedInOperatingActivities",
         "PaymentsToAcquirePropertyPlantAndEquipment"]
STOCKS = ["Assets", "StockholdersEquity", "AssetsCurrent", "LiabilitiesCurrent",
          "Liabilities", "LongTermDebtNoncurrent",
          "RetainedEarningsAccumulatedDeficit"]

records = pd.concat(
    [edgar.facts_to_pit_records(facts, FLOWS, duration="annual"),
     edgar.facts_to_pit_records(facts, STOCKS, duration="instant"),
     edgar.facts_to_pit_records(facts, ["CommonStockSharesOutstanding"],
                                duration="instant", unit="shares")],
    ignore_index=True,
)
pit = PointInTimeStore.from_frame(records)

view = pit.as_of("2022-12-01")            # the world as of December 2022
fy22 = StatementSet.from_pit_view(view, "Apple Inc.", "2022-09-24")
fy21 = StatementSet.from_pit_view(view, "Apple Inc.", "2021-09-25")
f"FY22: revenue ${fy22.revenue/1e9:.1f}B, net income ${fy22.net_income/1e9:.1f}B, CFO ${fy22.cash_from_operations/1e9:.1f}B"
```

Real 10-K figures, to the dollar — and reproducible: rerun this lesson in five
years and the `as_of("2022-12-01")` view cannot change.

## 3. The DuPont decomposition — explaining a 197% ROE

```{code-cell} ipython3
from quantropy.valuation import ratios

r = ratios(fy22)
pd.Series({
    "net margin": r.net_margin,
    "asset turnover": r.asset_turnover,
    "leverage (assets/equity)": r.leverage,
    "ROE  = margin × turnover × leverage": r.dupont_roe,
    "ROA": r.roa,
}).round(3)
```

ROE near **2.0** — not a typo. The decomposition shows why: a very good but not
otherworldly margin (~25%) and turnover (~1.1) multiplied by **leverage near 7×**
— Apple's buybacks have shrunk book equity to a sliver, so ROE mostly measures
capital-structure choice, not operating brilliance. This is why DuPont exists:
one number lies, three numbers explain. (ROA, capital-structure-neutral, is a
more honest ~28%.)

## 4. Reverse DCF: what did the price believe?

Free cash flow, the real thing: CFO minus capex.

```{code-cell} ipython3
from quantropy.valuation import implied_growth

fcf = fy22.cash_from_operations - fy22.capex
market_cap = 129.93 * 15.943e9   # Dec 30, 2022 close × shares outstanding (10-K)
g = implied_growth(market_cap, fcf, discount_rate=0.09,
                   horizon=10, terminal_growth=0.025)
f"FCF ${fcf/1e9:.1f}B; market cap ${market_cap/1e12:.2f}T -> implied stage-1 growth ~ {g:.1%}/yr"
```

Instead of arguing about *our* growth forecast, the reverse DCF states the
market's: at a 9% discount rate, the December-2022 price required roughly this
FCF growth for a decade. The analyst's question becomes falsifiable — *is that
plausible for a company this size?* — which is the entire point of
expectations investing (REFERENCES §6, Rappaport-Mauboussin).

## 5. Quality and distress, scored

```{code-cell} ipython3
from quantropy.valuation import altman_z, piotroski_f

fscore = piotroski_f(fy22, fy21)
z = altman_z(fy22, market_cap=market_cap)
f"Piotroski F = {fscore.score}/{fscore.max_computable} computable checks; Altman Z = {z:.2f} (safe > 2.99)"
```

Two-period quality checks on real statements, and a distress score deep in the
safe zone — as expected for 2022 Apple; the *interesting* uses are cross-sectional
(these scores become signals in Part VI).

## 6. Pitfalls

- **A DCF is an argument, not an answer.** The implied-growth form is honest
  because it exposes the assumption instead of burying it; sensitivity to the
  discount rate is enormous (try 8% and 10% in §4).
- **Book equity can be economically meaningless** (buybacks, intangibles) — hence
  ROE's DuPont autopsy and residual-income models that adjust for it.
- **Concept drift is permanent**: this lesson's revenue arrives under the
  post-ASC-606 tag; the `CONCEPT_MAP` fallbacks are load-bearing, not cosmetic.
- **One company teaches mechanics, not investing.** Cross-sectional application
  with PIT discipline (Parts III and VI) is where these tools earn returns.

## 7. Exercises

1. Recompute §4 with discount rates of 8% and 10%. How much does implied growth
   move? What does that say about "the market thinks…" claims?
2. Compute FY21's DuPont and explain what changed into FY22.
3. `as_of("2022-01-15")` instead — FY22 doesn't exist yet. Verify the store
   refuses to show it to you and FY21 is the newest period available.

## Further reading

`docs/REFERENCES.md` §6 — Damodaran; Penman (residual income); Rappaport &
Mauboussin (expectations); Altman (1968); Piotroski (2000); Beneish (1999).
