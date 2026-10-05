# Portfolio methods: estimators, objectives and allocation rules

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Portfolio construction is a pipeline, not a list of competing buzzwords. Specify return/covariance estimates or scenarios; objective and risk measure; constraints; algorithm/solver; rounding/trading implementation; and evaluation. Compare methods under the same available information and net cost conventions.

Classic MPT/mean–variance supports efficient-frontier and utility/target-return choices. Global minimum variance avoids required expected-return estimates but still depends on covariance and constraints. Minimum volatility is the same ordering as minimum variance under the same setup; do not advertise them as independent discoveries. Maximum Sharpe, tracking-error/information-ratio and liability-relative formulations optimize different objectives.

Equal weights and inverse volatility are allocation baselines. Equal-risk-contribution and generalized risk budgeting allocate risk rather than equal capital. Maximum diversification and correlation-based allocation target other portfolio properties. HRP uses hierarchical structure in allocation; HERC and NCO are related but distinct methods. Their distance, linkage, cluster and allocation choices must be declared. None is universally optimal. [Original HRP reference](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2708678).

CVaR/expected-shortfall, downside and drawdown objectives need their own definitions, scenarios and solver fit. Compounded versus uncompounded drawdowns cannot be exchanged silently. Robust/distributionally robust approaches require explicit uncertainty sets. Bayesian/Black–Litterman views, covariance shrinkage, denoising and factor covariance change estimates rather than inherently replacing the objective.

Integrate constraints on concentration, long/short exposure, factors, currency, turnover, costs, taxes, cash, margin and integer lots. Cardinality and nonconvex extensions add complexity. Dynamic/multiperiod allocation, goal-based funding and liability matching require decisions across time rather than static weights.

PyPortfolioOpt and Riskfolio are candidate references/integrations with substantial method coverage. Inspect licensing, solver requirements, exact numerical specifications and release behavior before adoption. [PyPortfolioOpt](https://pyportfolioopt.readthedocs.io/en/latest/OtherOptimizers.html), [Riskfolio](https://riskfolio-lib.readthedocs.io/en/latest/).

Acceptance: hand cases, independent solution comparisons, feasibility after rounding, covariance conditioning, estimation sensitivity, clustered-asset tests and walk-forward net comparison to simple baselines. Original method sources and exact versions must be verified individually; this map does not certify the complete derivations.

## Coverage checklist

- Estimator objective constraint solver separation
- Classic MPT efficient frontier min variance max Sharpe
- Equal weight inverse volatility risk-budget baselines
- ERC maximum diversification correlation methods
- HRP HERC NCO distinct hierarchical methods
- CVaR downside drawdown robust objectives
- Black Litterman Bayesian shrinkage denoising inputs
- Tax turnover leverage and integer constraints
- Dynamic goal liability-relative allocation
- Independent optimizer and economic robustness evidence

## Research sources

- [HRP](sources.md#hrp)
- [PRADO-PUBLICATIONS](sources.md#prado-publications)
- [PYPORTFOLIOOPT](sources.md#pyportfolioopt)
- [RISKFOLIO](sources.md#riskfolio)
- [SHRINKAGE](sources.md#shrinkage)

[Knowledge base index](README.md)
