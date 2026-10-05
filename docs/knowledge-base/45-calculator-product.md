# Calculators and simulations for a broader audience

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

The latest scope includes useful calculators beyond the owner's advanced trading workbench. Treat this as a product requirement: a novice should be able to explore a financial question with understandable assumptions and outcomes, while an advanced user can inspect or reproduce the exact model. The same financial services should power both experiences.

Initial calculator workflows: contribution/compound growth; savings and income-growth planning; inflation/purchasing power; debt amortization; emergency liquidity; retirement/FIRE scenarios; withdrawal-policy comparison; allocation/risk comparison; company valuation sensitivity; bond/option payoff and sensitivity education. Do not expose every advanced solver as an unexplained dropdown. Provide appropriate defaults only after verification, allow customization, and show why an input matters.

Separate scenario presets from user facts. FIRE spending/work labels are presets users define, not official targets. A user can compare retirement dates, spending, contribution rates and return/inflation assumptions using identical scenario paths. Reports should show money in today's and future currency with timing conventions, percentiles/shortfalls and deterministic examples. Do not imply that one probability output is an objective guarantee.

Privacy is part of the design for a broader audience. Anonymous educational calculators may run without account creation or permanent storage. Saved scenarios and broker-linked households require identity, explicit data controls, retention and separate authorization. Sharing a scenario must disclose which assumptions/details become visible and require an intentional user action. Public deployment and commercial advice are distinct decisions from building the calculation capability.

Implementation should separate the household policy simulator from the market execution simulator. They can share instrument models, accounting primitives and scenario services, but household income/spending policies and exchange order matching answer different questions. Avoid a single overly generic engine that hides those distinctions.

Acceptance: deterministic and stochastic calculators use the same reviewed primitives; hand examples match; flow and inflation timing is visible; advanced assumptions are inspectable; missing rules remain explicit; no broker credential is needed for education; saved/private/shared scenarios follow intentional permissions. Broader audience support expands the product scope without requiring every institutional modeling feature at launch.

## Coverage checklist

- Beginner calculator and advanced model parity
- Savings income inflation debt and liquidity calculators
- FIRE retirement withdrawal policy comparisons
- Valuation bond option and portfolio education
- Explicit presets assumptions and outcome uncertainty
- Anonymous private saved and shared scenario boundaries
- Household versus exchange simulation responsibilities
- Public deployment and advice scope decisions

## Research sources

- [RETIREMENT](sources.md#retirement)
- [CFP](sources.md#cfp)
- [OWASP](sources.md#owasp)
- [GIPS](sources.md#gips)

[Knowledge base index](README.md)
