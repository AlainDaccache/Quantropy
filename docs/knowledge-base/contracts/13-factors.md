# Asset pricing, factor construction and attribution

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [01-statistics](01-statistics.md); [05-estimators](05-estimators.md).

## Theory and estimation

A stochastic discount factor m prices a payoff X as P=E[mX] under a specified economy and measure. For returns, E[mR]=1 implies E[R]-Rf=-Rf Cov(m,R) when Rf=1/E[m]. Risk premia therefore depend on payoffs in states where marginal value is high, not only variance. Consumption and intertemporal models impose economic structure on m; APT imposes factor-pricing restrictions under its assumptions. Statistical factor fit alone does not establish those restrictions.

For time-series regression, excess return r_i-rf=alpha_i+beta_i'f+epsilon_i. CAPM uses market excess return; FF3 adds size/value; FF5 additionally profitability/investment; momentum extensions use a separately constructed factor. Estimate intercept/exposures jointly, match currency/horizon and use appropriate inference. Rolling/state-space beta estimates must not use future data. Factor attribution beta_i*f_t is model-dependent; residuals and costs must remain visible.

## Sorting and construction

1. Define eligible point-in-time universe and formation date.
2. Compute characteristic from historically available data; document book-equity exclusions and lag rules.
3. Set breakpoints on a declared reference population, then independent or conditional sorts.
4. Compute equal/value weights, rebalance, corporate-action and delisting policies.
5. Form long-short differences with funding, shorts and transaction-cost assumptions.

A simple value factor is high-book/price portfolio return minus low-book/price return, but that statement does not replicate the French library. Its specific size/characteristic portfolios and SMB combinations must follow the source edition. Example long leg 8% and short leg 3% give gross long-short difference 5% under equal-notional conventions; a 2% stock-borrow/funding charge changes net economics.

Fama-MacBeth runs repeated cross-sectional regressions then averages slope estimates with dependence-aware inference. It differs from time-series factor exposure regression. Rank IC is rank correlation between available signal and later return in a defined cross-section; ties, missing values and horizon matter. Neutralization regresses/removes selected country/sector exposures using contemporaneously available classifications; it changes the question asked.

Quality, defensive/BAB, liquidity, q/mispricing, statistical PCA, characteristic risk models, IPCA and nonlinear pricing require named original construction/identification contracts. Post-publication decay, transaction costs, capacity and multiple testing must accompany anomaly claims. This contract supplies reusable theory/procedure; candidate models are not declared replicated by their inclusion.

## Evidence boundary

Supporting source map: [FRENCH-5-CONSTRUCTION](../sources.md#french-5-construction), [COCHRANE](../sources.md#cochrane), [OPEN-AP](../sources.md#open-ap). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
