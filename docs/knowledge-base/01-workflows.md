# Workflows and the user experience

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Begin with questions a retail investor actually asks: Can I meet my spending goals? What do I own across accounts? Why did performance change? Is a company financially healthy? What assumptions make its current price reasonable? How does an option behave under a shock? Does a rule survive unseen data and realistic costs? What is the safest way to implement a desired portfolio?

Provide five connected workspaces. Plan shows balance sheet, liquidity, liabilities and goals. Analyze shows source-linked filings, valuation scenarios, charts and instrument economics. Research combines notebooks, reusable experiments and reports. Portfolio shows holdings, look-through exposures, risk, attribution and proposed rebalances. Operate shows broker connectivity, orders, executions, reconciliations and alerts. Learning should explain an unfamiliar metric at the point of use.

Every result needs an as-of time, units, account/currency scope, source, assumptions and uncertainty. Separate observed values, user estimates and computed outputs. Display missing information explicitly. A zero fee, zero position or zero implied volatility must mean zero, not missing. Retain saved scenarios and compare changes in assumptions rather than overwriting prior work.

A proposed trade should link back to the thesis or experiment, show portfolio impact, realistic cost and margin estimates, and disclose execution constraints. An investment journal records decisions and later reviews, including reasons to exit and evidence that would invalidate the thesis. Avoid encouraging constant trading merely because the interface has many charts.

Acceptance: a novice can follow a holding from its source transaction to cash, exposure, risk and performance; an advanced user can reproduce the same calculation through an API. UI and notebook results use the same domain services. Accessibility, keyboard use, readable units, export and offline research are product requirements, not cosmetic extras.

## Coverage checklist

- Household planning workspace
- Asset analysis workspace
- Research notebooks and reports
- Portfolio and attribution workspace
- Live operations console
- Investment journal
- Accessible explanatory interface
- API and export parity

## Research sources

- [PA](sources.md#pa)
- [OPENBB](sources.md#openbb)

[Knowledge base index](README.md)
