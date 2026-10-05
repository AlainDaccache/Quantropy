# Build strategy, priorities and graduation gates

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Build breadth in architecture and depth in a few end-to-end workflows. Do not start by implementing every model. Prioritize the common foundation and prove it with independent examples, then add domains through capability profiles. Time/cost estimates require staffing, data budget and target workflows that are not settled yet.

Gate A: preserve existing repositories, inventory requirements/defects, define domain contracts and data licensing. Gate B: establish security master, as-of data, currency-aware economic ledger and a read-only portfolio dashboard. Gate C: deliver two research slices: source-linked company statements/valuation and daily futures trend/carry with actual contracts. Gate D: add portfolio risk and a realistic order simulator with independent fixtures. Gate E: IBKR read-only reconciliation, replay, paper and fault recovery. Gate F: a deliberately capped live profile with monitored accounting and explicit enablement. Gate G: historical option chains, surface/pricing validation and option lifecycle; expand rates, advanced ML and other assets only after prerequisites pass.

These are dependency gates rather than deadlines. Fundamental analysis need not wait for live trading; advanced pricing should not block the household overview. Existing personal futures restrictions can remain in one execution profile while the broader analysis platform expands.

Build Quantropy's integration, provenance, ledger semantics, policy enforcement and user workflows. Evaluate integrating QuantLib for pricing, LEAN for execution/simulation semantics, OpenBB for data/analysis, and IBKR for brokerage. Prefer verified mature capabilities to copying their functionality blindly. License, maintenance, deployment fit, data rights and deterministic fixtures decide adoption. No library solves point-in-time data procurement automatically.

Acceptance: a capability progresses through specified, sourced, implemented, independently validated, replay/paper proven and enabled stages; failed gates prevent progression. Select one initial engine after a small comparative spike, avoid maintaining competing simulators indefinitely, and deprecate duplicate code only after replacement coverage and migration evidence.

## Coverage checklist

- Foundation and ledger first
- Company analysis vertical slice
- Daily futures research vertical slice
- IBKR read-only to live graduation
- Options data pricing and lifecycle graduation
- Build buy integrate comparison
- Capability maturity and evidence gates
- Duplicate code retirement and migration

## Research sources

- [QUANTLIB](sources.md#quantlib)
- [LEAN](sources.md#lean)
- [OPENBB](sources.md#openbb)
- [IBKR-DATA](sources.md#ibkr-data)

[Knowledge base index](README.md)
