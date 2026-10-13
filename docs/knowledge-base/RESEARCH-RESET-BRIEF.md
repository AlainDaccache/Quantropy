# Quantropy: research reset and decision questions

Date: 2026-10-13. This is a product/research synthesis and discovery brief, not a personalized allocation or a verified alpha catalog. It supersedes the assumption that Quantropy's users or conceptual capabilities must be restricted to retail investing.

## Product intent

Quantropy should be a financial research, modeling, portfolio decision and trading platform used by its owner, traders, researchers and portfolio managers. A reusable library and programmatic interfaces support a full-stack application, notebooks and automated workflows. Education, household planning and calculators can coexist with professional analysis. User roles change permissions and workflows, not the underlying financial definitions.

Keep the solution space broad. Investigate instruments, markets, return horizons, discretionary/systematic methods and specialist financial domains. Judge implementability separately for each user, mandate, capital base, market access and deployment. A method can be valuable for explanation or research before it is feasible to trade. The first release is an implementation priority, not the ultimate domain boundary.

## Constraints without premature narrowing

| Type | Treatment |
|---|---|
| Economic and evidence requirements | Enforce accounting reconciliation, causal information use, correct units, honest uncertainty and no invented empirical results |
| User/mandate profiles | Parameterize objectives, horizon, capital, liabilities, loss capacity, currency, taxes and account permissions; unknowns remain scenarios |
| Implementation conditions | Assess data rights, tradability, costs, collateral, liquidity, infrastructure and operating support for the specific implementation |
| Design hypotheses | Compare architecture, algorithms, strategy families, brokers and UI choices; do not canonize guesses prematurely |
| Research scope | Expand when evidence reveals missing concepts; inaccessible execution does not automatically exclude knowledge |

Do not infer the owner's tax residence, capital, employment rules or client-management permissions from the laptop location or timezone. Do not require the user to answer 96 questions before research can proceed. Research open questions autonomously; defer irreversible deployment decisions that genuinely depend on a profile.

## What was missing from the questions

“All resources,” “all premiums,” and “maximize returns” describe breadth but not a decision standard. The missing questions concern objectives and loss capacity; mechanisms and who pays; evidence and falsification; actual investor costs; overlap and bad-state dependence; allocation uncertainty; operational failure; and strategy retirement. They also concern who uses the platform and how different deployments change obligations.

The [96-question register](research-questions.csv) covers twelve decision domains with expected artifacts and decision types. It is an expandable discovery framework, not an exhaustive syllabus or a gate preventing progress. Ask “what would change our decision?” alongside “what method exists?”

## Can expected returns be maximized?

Within a specified feasible set and an assumed return distribution, yes: solve the stated objective. We cannot know a universally optimal future portfolio because expected returns, dependence and tail behavior must be estimated. Maximizing expected one-period return alone may concentrate in the exposure with the largest estimate; without position/funding limits, leverage can make the problem unbounded. That is a defect in the objective specification, not a reason to constrain the research universe.

Compare net expected return, expected utility, long-run compound growth, benchmark-relative performance and probability/severity of goal shortfall. They are different objectives. Leverage, volatility drag, margin calls and withdrawals can make an apparently superior mean return inferior for a particular objective. Tax and cost efficiency can improve retained outcomes without creating predictive alpha.

## Return sources and edge: organize by economic mechanism

| Family | What to investigate | What not to assume |
|---|---|---|
| Market exposure | Equity/business risk; duration/term; credit/default; property/infrastructure and other asset exposures | Every asset class has an independent positive premium at every valuation |
| Cross-sectional styles | Value, momentum, profitability, quality, investment, defensive/low-risk, size and liquidity variants | Every characteristic is distinct, causal or reliably profitable after costs |
| Cross-asset strategies | Time-series trend, carry, relative value and defensive construction across equities, rates, FX and commodities | Trend is identical to equity momentum, or carry is risk-free income |
| Contingent-risk compensation | Volatility/variance, skew, jump/crash insurance, liquidity provision and catastrophe exposures | A high win rate or option premium demonstrates superior economic value |
| Events and constraints | M&A, restructurings, issuance/buybacks, earnings information, index flows, forced selling and specialized rules | Every event creates tradable alpha or an arbitrage without funding risk |
| Informational/model advantage | Better measurement, sector understanding, forecasts, causal insight, data processing and execution | Public-data availability or model complexity establishes an advantage |
| Implementation advantage | Costs, tax efficiency, patient capital, execution, niche capacity and disciplined behavior | All efficiency gains should be labeled alpha |
| Specialized niches | Funding/basis trades, convertibles, private/illiquid claims, energy/storage, digital claims and other domains | Apparent spreads remain executable after borrow, counterparty, settlement and capital costs |

This classification is original organizing analysis. Families overlap; one strategy can load on several. A return-source card should state mechanism, payer, evidence, exposure, tail/funding risk, instrument access, cost/capacity, independent replication, falsification and current research status. Day/swing/position describe horizons; they do not identify an edge.

Research supports examining diverse styles and cross-asset implementations, rather than treating equity factors as the entire universe. AQR's public alternative-premia framework names value, momentum, carry, defensive, trend and volatility; it is a manager-authored framework and not proof that any chosen implementation will work. [Public framework](https://www.aqr.com/insights/research/white-papers/understanding-alternative-risk-premia).

Historical trend research and cross-asset carry research supply useful hypotheses. The trend overview was opened; the carry abstract was available through search, while its NBER page returned 403 during this pass. Exact strategy replication and forward evidence remain required. [Trend study overview](https://www.aqr.com/insights/research/journal-article/a-century-of-evidence-on-trend-following-investing), [carry paper](https://www.nber.org/papers/w19325).

The Taiwan day-trader study reports negative aggregate performance in its 1992–2006 sample. This challenges casual assumptions about intraday edge; it does not establish that every trader or every market has the same outcome. Read the methods and scope before generalizing. [Original author-hosted paper](https://faculty.haas.berkeley.edu/odean/papers/Day%20Traders/Day%20Trading%20and%20Learning%20110217.pdf).

## Resource strategy

Use curricula to identify concepts; original papers for claims and methods; books for coherent exposition; author code and data for replication; standards and venue/broker documentation for conventions and lifecycle; and prospective records for implementation evidence. These are different evidence sources. Start from the existing [source register](sources.md) and [book map](book-research-map.csv); do not claim an unread book has been covered.

Add competing research rather than asserting that the factor literature is either uniformly valid or uniformly false. Jensen, Kelly and Pedersen report substantial replication evidence in their study; the public abstract was inspected via search here, not the full paper. Chen and Zimmermann's author project supplies replicated signals and code, which still need independent data/timing/cost checks before use. [Replication study](https://www.nber.org/papers/w28432), [Open Source Asset Pricing](https://www.openassetpricing.com/).

## Allocation research

Allocate first to economic exposures and strategy return streams, then translate allocations into instruments and orders. Compare equal weight and simple bounded policies with shrinkage mean-variance, risk budgeting, HRP/HERC/NCO, Bayesian views, robust/tail-risk objectives and multi-period liability/tax-aware approaches. Match comparison data, cost model, information set and risk budget. Do not treat an optimizer's best in-sample allocation as evidence of superiority.

Separate signal estimates from risk/funding policies and the feasible trade set. Test shared factor exposure, crisis co-loss, margin needs, concentration, turnover, estimation sensitivity and capacity. Tactical timing is another hypothesis needing evidence, not an assumed free enhancement. No fixed weights can be recommended from the currently unspecified user/mandate profiles.

## What the system should be

A financial decision platform with shared domain contracts and multiple user interfaces:

1. Knowledge and evidence: canonical concepts, method contracts, source claims, dependencies, uncertainty and research gaps.
2. Economic data: instrument master, raw/versioned/point-in-time facts, corporate actions, curves, entitlements and provenance.
3. Analysis/modeling: statements, valuation, pricing, econometrics, risk, scenarios and lifecycle/household models.
4. Research workbench: datasets, hypotheses, features, experiments, causal replay, validation, replication and reports.
5. Portfolio policy: strategic/tactical exposures, forecasts, allocation alternatives, constraints, tax/cost/funding and stress.
6. Operations: intents, orders, fills, settlement, ledger, reconciliation, monitoring, incidents and retirement decisions.
7. App/API surfaces: role-specific dashboards, screeners, calculators, notebooks, collaborative artifacts and reports with permissions/audit.

This is a proposed domain decomposition, not a committed technology stack. Share economic primitives across historical, paper and live environments while explicitly modeling environment-specific information, fills and failures. Prefer reversible implementation choices until workload evidence calls for more complexity. Begin with a reproducible complete vertical workflow; preserve the ability to add markets, models, brokers and deployment profiles.

## Continue from evidence, not from a blank slate

Existing scope: 15 introductory reference articles, 25 family-contract drafts, 306 mapped methods and 120 broad finance units. Ownership and arithmetic checks do not mean every method is fully derived or independently reviewed. The [work ledger](RESEARCH-WORK-LEDGER.md) remains authoritative for unfinished research. Proceed with the [fresh-session handoff](CONTINUE-IN-FRESH-SESSION.md).
