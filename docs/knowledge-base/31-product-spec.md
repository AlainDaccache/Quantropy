# Product specification: from knowledge to an app

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Build four connected layers. Knowledge: explanations, sources, definitions, qualitative frameworks and limitations. Quantitative library: validated calculations/pricing/statistics. Decision workflows: analysis notebooks, scenarios, screens, portfolio construction and research records. Operations: data pipelines, simulation, risk, broker state and reports. A concept can live in the knowledge layer, a checklist or a scenario without being ready for automated calculation or trading.

The central workflow is reproducible evidence. A user opens an instrument/company/portfolio, selects an as-of context and dataset snapshot, runs a versioned analysis, saves assumptions, compares alternatives and records a decision. Strategy research adds experiment/trial/holdout history. Portfolio proposals add constraints and estimated costs. Live deployment adds a separately approved capability profile and reconciled actual state.

Primary entities: KnowledgeConcept, SourceRecord, Instrument, Issuer, DatasetVersion, Observation, ModelDefinition, ModelRun, Scenario, Hypothesis, Experiment, Trial, StrategyArtifact, PortfolioPolicy, Account, LedgerEvent, PositionSnapshot, RiskReport, TradeIntent, BrokerOrder, Execution, ReconciliationBreak, Decision and Incident. Relations provide traceability: a model run consumes dataset versions; a strategy artifact derives from experiments; a trade intent derives from an approved artifact/policy; an execution creates ledger effects. Qualitative evidence attaches to concepts/theses with reviewer status.

Minimum end-to-end outcomes: reconstruct account holdings/cash and explain performance; reproduce a company analysis from filings; replicate and cost a daily futures rule; propose and simulate a risk-constrained rebalance; recover broker state after an uncertain order. An options slice later provides a quote-qualified chain, validated surface/pricing, scenario risk and lifecycle-aware simulation.

Full-stack acceptance: calculations in UI and API agree; jobs expose progress/failures; results and assumptions persist; no stale artifact is silently displayed as current; restricted profiles block orders; edits retain version history. Launching a dashboard with many tabs is insufficient. Each advertised workflow needs usable data, correct models and a complete evidence trail.

## Coverage checklist

- Knowledge concept and source graph
- Validated quantitative library
- Analysis scenario and qualitative workflows
- Research strategy and trial workflows
- Portfolio proposal and approval workflows
- Account ledger broker and incident workflows
- Versioned entities and lineage relations
- UI API calculation consistency
- Asynchronous jobs and failure visibility
- Persistent results assumptions and exports

## Research sources

- [CFA-PSM](sources.md#cfa-psm)
- [OPENBB](sources.md#openbb)
- [LEAN](sources.md#lean)
- [QUANTLIB](sources.md#quantlib)

[Knowledge base index](README.md)
