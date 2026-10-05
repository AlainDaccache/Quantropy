# Quantropy knowledge base

**A research-backed specification for a broad retail investment platform.** Edition 1, 2026-10-05. The project goal is trustworthy analysis, research, portfolios and operations across instrument families. This is a comprehensive domain map and a foundation for implementation; no feature list here certifies live readiness or investment profitability.

Start with [the critique and vision](00-vision.md), [the build strategy](22-roadmap.md), [quality gates](23-quality.md) and [known gaps](26-open-questions.md). Then read the relevant modeling chapters. The scope was designed independently of the existing code.

The governing distinction is **analysis coverage / simulation fidelity / live readiness**. A model can be useful offline while its data, lifecycle or execution support remains unsuitable for live use. Personal account and employment restrictions remain execution-policy inputs until verified.

## Domain map

- [What Quantropy should become](00-vision.md)
- [Workflows and the user experience](01-workflows.md)
- [Instruments, markets and economic contracts](02-instruments.md)
- [Data, provenance and point-in-time truth](03-data.md)
- [Financial statement analysis](04-statements.md)
- [Ratios, quality and forensic screening](05-ratios.md)
- [Valuation and business modeling](06-valuation.md)
- [Learning from investors without pretending to clone them](07-investor-styles.md)
- [Factor research and empirical asset pricing](08-factors.md)
- [Systematic futures and FX](09-futures-fx.md)
- [Options, volatility and derivative modeling](10-options.md)
- [Rates, fixed income and credit](11-rates-credit.md)
- [Portfolio construction and allocation](12-portfolios.md)
- [Risk, leverage and sizing](13-risk.md)
- [Research design, statistics and machine learning](14-research.md)
- [Backtesting and realistic simulation](15-simulation.md)
- [Interactive Brokers and execution engineering](16-execution.md)
- [Accounting, performance, taxes and reporting](17-accounting.md)
- [Household wealth and goals](18-household.md)
- [Funds, property, crypto and less standard assets](19-alternatives.md)
- [Operations, security and governance](20-operations.md)
- [Architecture and domain contracts](21-architecture.md)
- [Build strategy, priorities and graduation gates](22-roadmap.md)
- [What “10/10” must mean in practice](23-quality.md)
- [Independent worked validation cases](24-validation-cases.md)
- [Learning path and vocabulary](25-learning.md)
- [Open research, decisions and explicit gaps](26-open-questions.md)
- [Economics, macro scenarios and market structure](27-economics.md)
- [Corporate finance, governance and qualitative research](28-corporate-finance.md)
- [Ethics, behavior and decision discipline](29-ethics-behavior.md)
- [Risk premia, anomalies, alpha and retail feasibility](30-premia-alpha.md)
- [Product specification: from knowledge to an app](31-product-spec.md)
- [Proposed full-stack architecture and engineering sequence](32-full-stack-design.md)
- [CFA coverage map and how to achieve completeness](33-cfa-coverage.md)
- [What the owner is trying to build](34-product-reassessment.md)
- [Independent coverage audit and research boundaries](35-independent-coverage.md)
- [Market plumbing, financing and investor dependencies](36-market-plumbing.md)
- [Fund, manager and product due diligence](37-manager-diligence.md)
- [Mathematical foundations and numerical model risk](38-numerical-model-risk.md)
- [How research becomes a complete usable library](39-research-completion.md)
- [Metrics and ratios need exact contracts](40-metric-specifications.md)
- [Sector and business-model valuation profiles](41-sector-valuation.md)
- [Portfolio methods: estimators, objectives and allocation rules](42-optimization-methods.md)
- [Backtesting methodology at method level](43-backtest-methods.md)
- [Household, accumulation, retirement and FIRE simulation](44-household-simulation.md)
- [Calculators and simulations for a broader audience](45-calculator-product.md)

## Registries and reusable specifications

- [Capability register](capability-register.csv): every checklist item is traceable to its domain specification. All initial statuses are specified; implementation evidence is unassessed.
- [Primary source register](sources.md): research depth and limits, including papers not yet read in full.
- [Risk-premium and alpha candidate catalogue](strategy-families.csv): mechanisms, retail expressions, obstacles and evidence gaps.
- [Independent coverage audit](coverage-audit.csv): domain owners, depth gaps and required completion evidence.
- [Detailed method inventory](method-inventory.csv): named metrics, estimators, allocation methods, valuation profiles, validation procedures and simulation policies.
- [Book research map](book-research-map.csv): selected author/publisher sources and explicit chapter-review requirements; not a claim to have reviewed all investment books.
- [Model specification template](templates/model-card.md).
- [Data contract template](templates/data-contract.md).
- [Experiment and strategy template](templates/experiment-card.md).
- [Live capability profile template](templates/live-profile.md).
- [Architecture decision template](templates/decision.md).
- [Maintenance and coverage protocol](maintenance.md).

The initial laptop code audit is separate. Keep its confirmed defects and scope limitations distinct from this independent design. This edition creates documentation; it neither replaces the current runtime nor repairs the audited defects.
