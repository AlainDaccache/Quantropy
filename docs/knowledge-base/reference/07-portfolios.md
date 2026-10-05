# Portfolio construction and optimization

A portfolio is a set of claims, funding arrangements and constraints. For compatible single-period simple returns, expected portfolio return is w' mu and variance is w' Sigma w, where weights w use the selected capital base, mu expected asset returns, and Sigma their covariance matrix. Covariance estimates must be symmetric and positive semidefinite for the standard variance interpretation. Leveraged and derivative positions need exposure and funding definitions beyond cash weights.

**Example.** Two assets have volatilities 10% and 20%, correlation zero and weights 50% each. Portfolio variance is 0.0125 and volatility 11.180340%. Unconstrained fully invested minimum-variance weights are 80% and 20%, giving volatility 8.944272%. Diversification depends on joint behavior, not simply the number of tickers.

Minimum variance solves min w' Sigma w subject to constraints. Minimizing volatility has the same optimum when the constraints are the same because square root is monotone. Mean-variance utility optimizes expected return minus a chosen variance penalty; the efficient frontier expresses different risk/return trade-offs. Maximum Sharpe maximizes excess expected return per volatility under a specified risk-free/funding convention. These are related objectives, not interchangeable promises.

Risk budgeting allocates contributions to portfolio risk. For volatility sigma_p, asset contribution is w_i(Sigma w)_i/sigma_p; contributions sum to sigma_p where differentiable. Equal risk contribution is not generally equal capital or inverse volatility; the latter ignores correlations. Negative contributions are possible, especially with hedges, and complicate target constraints.

Hierarchical risk parity uses clustering and allocation rules; it is not a universal superior solution. Cluster metric, linkage, ordering and allocation variants need explicit definitions. Black-Litterman combines a prior with uncertain views; outcomes depend on prior construction and confidence. Robust optimization constrains uncertainty sets. CVaR optimization targets average loss in a chosen tail. Tracking-error minimization targets deviations from a benchmark. Liability-driven allocation targets obligations rather than an asset-only Sharpe ratio.

Expected returns are noisy and extreme weights often reveal unstable estimates. Shrinkage, bounds, turnover penalties, transaction costs and scenario sensitivity can improve robustness but also encode preferences. Rebalancing depends on tax lots, cash, liquidity and feasible orders. An unconstrained mathematical optimum can be operationally unusable.

Implementation must document objective, estimates, feasible set, solver, tolerances and failure behavior. Compare methods using the same information set and costs. No portfolio method guarantees future optimality. Full HRP/HERC/NCO, Bayesian, entropy, distributionally robust, Kelly and multi-period methods remain method-level specification work; this page establishes their surrounding concepts, not their complete algorithms.

## Evidence and depth

Source map: [CFA-III-PM](../sources.md#cfa-iii-pm), [SHRINKAGE](../sources.md#shrinkage), [HRP](../sources.md#hrp), [PYPORTFOLIOOPT](../sources.md#pyportfolioopt), [RISKFOLIO](../sources.md#riskfolio). These are supporting references, not certification of every equation. This article is an introductory reference; specialized methods listed in the coverage register still require full specifications and independent review.

[Reference index](README.md)
