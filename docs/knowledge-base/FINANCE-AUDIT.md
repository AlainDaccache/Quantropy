# Independent finance knowledge audit

## Finding

The previous edition contains 46 scoping chapters and 306 candidate method entries. That is useful discovery material, but is not a self-contained encyclopedia or a verified method library. Chapter presence, method count, textbook title and source count do not establish completeness, correctness or implementation readiness. This revision adds an explanatory foundation and a broader independently organized research denominator.

## Scope and exclusions

Finance covers the allocation of resources across time and uncertain states, the contracts and institutions that support that allocation, and decisions made by households, businesses and public bodies. Investing is one major application. The fifteen reference domains now include mathematics, reporting, economics/public finance, corporate finance, debt, derivatives, portfolios, risk, empirical research, market operations, households, institutions, treasury/payments, alternatives and governance.

The [coverage register](finance-coverage.csv) lists 120 research units with one owner each. Units are bounded containers, not a claim that 120 exhaust all financial ideas. Specialized topics such as Islamic finance, health finance, energy markets, climate risk, litigation finance, microfinance and new instruments must be routed to their economic-function owner and decomposed when researched. Product and infrastructure requirements live separately. Local law, tax, accounting and regulation require dated jurisdiction extensions; no global rulebook is promised.

## Cross-check and evidence

Existing CFA/FRM/CAIA/CFP/CMT maps provide educational lenses, not a universal syllabus. This audit adds IFRS reporting concepts, BIS banking structure, IMF financial-system/public-debt material, OECD small-business literacy and actuarial education scope. Review depths are explicit in [sources](sources.md): some public pages were opened, some sources were only identified through official search excerpts. Full books, full standards and all curricula were not read in this audit. No source-count metric is a substitute for claim-level validation.

## Material corrections and new boundaries

- A generic FCFF expression can double-count depreciation when “reinvestment” already means net investment. The [canonical valuation explanation](reference/04-valuation.md) explicitly uses gross capex and states the acquisition boundary.
- Minimum variance and minimum volatility are the same optimum under the same constraints; separate labels should be aliases, not separate conceptual coverage credit.
- VaR/ES quantile conventions, return cash-flow timing and nominal/real rate compatibility require explicit definitions. The reference adds examples for each.
- Bank equity capital, payment liquidity and insurer reserves are distinct concepts; portfolio volatility is not an adequate universal risk measure.
- Detailed sector models, advanced optimizers, forensic-score variants, volatility calibration and backtest diagnostics remain unfinished. A new introductory article does not close those gaps.

## MECE, KISS, DRY and SOLID as editorial rules

**MECE:** assign one economic-function owner to each unit; expose overlapping curricula, assets and users as tags/views. Absolute non-overlap between financial ideas is unrealistic because the same claim links accounting, valuation and risk. Exclusivity concerns ownership, not denial of connections. Split an ambiguous unit before declaring its detailed specification complete.

**KISS:** a short foundational path precedes advanced method contracts. Use consistent units, symbols and worked examples. Do not simplify away economically necessary assumptions.

**DRY:** keep each detailed definition/equation in one canonical contract; generated registers and product pages link to it. Existing method tables are discovery material and remain a migration backlog; they are not silently treated as reconciled canonical definitions.

**SOLID:** these are software principles adapted to knowledge maintenance. Single responsibility means a bounded article or method; extension uses new contracts and jurisdiction profiles; substitution requires equivalent economic conventions; separate learner, model and execution interfaces; depend on economic definitions and provenance rather than broker/vendor labels. This is an editorial analogy, not a claim that prose satisfies a software type system.

## Completion contract

A detailed method is publishable as self-contained only after: purpose and scope; definitions and prerequisites; equation/procedure with every symbol and unit; assumptions and domain restrictions; input provenance; worked example; limiting/negative cases; failure modes and uncertainty; primary evidence attached to material claims; independent mathematical/domain review; and implementation links clearly separate from conceptual validity. Models also need calibration, identification and validation specifications. Conceptual topics require explanatory examples and evidence rather than an artificial calculator.

Lifecycle: identified → introductory explanation → full draft → independently reviewed → verified example → implementation validated. These are separate milestones, not interchangeable badges. This edition reaches **introductory explanation** for foundational articles, with selected arithmetic examples checked. No article has independent expert review. The older candidate inventory keeps its existing unresolved status.

## Next research work, in dependency order

1. Decompose the 120 units and map each existing method to a canonical concept ID; resolve aliases and incompatible conventions rather than merging by name.
2. Finish probability/statistics, econometrics and numerical foundations, then method contracts for statements, valuation, curves, option pricing and portfolio objectives.
3. Derive specialist sector, actuarial, treasury, public-finance and private-market contracts with source-specific examples.
4. Attach evidence at claim/formula level and arrange independent reviews. Track inaccessible sources as gaps; never imply an unread book was covered.
5. Define reproducible data and model validation cases, then connect them to application capabilities. Dates, licenses, execution and legal profiles remain separate release gates.

## Validation meaning

[Verification report](reference-verification.json) records arithmetic identities and selected illustrative cases. Repository checks validate IDs, owners, internal links and hashes. They do not establish empirical alpha, full scholarly coverage, legal correctness, or live trading safety. No overall percentage-complete is reported because the ultimate denominator is open-ended.

[Reference index](reference/README.md) · [Knowledge base index](README.md)

## Detailed-method follow-through

The next pass adds [25 family contracts](contracts/README.md), all-method ownership in [the catalog](method-catalog.csv), a checked prerequisite graph and additional worked cases. The [work ledger](RESEARCH-WORK-LEDGER.md) supersedes broad “pending” labels with specific remaining derivations. Family drafts do not close independent review or dedicated advanced-method completeness.
