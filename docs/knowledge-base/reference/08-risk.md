# Risk, uncertainty and model validation

Risk is exposure to outcomes that can undermine an objective. Market, credit, liquidity, funding, operational, legal, counterparty and model risks interact. A profitable expected payoff can still be unacceptable because losses arrive before available capital, or because the payoff cannot be realized when needed.

Define loss L over a horizon and confidence alpha. VaR is an alpha quantile of L. Expected shortfall is the average of quantiles above alpha, ES_alpha=(1/(1-alpha)) integral from alpha to 1 of VaR_u du. In a continuous distribution this equals the tail conditional mean; with atoms, handle probability at the quantile explicitly. VaR is a threshold, not the worst possible loss. Horizon scaling by square root of time needs restrictive dependence/distribution assumptions.

**Example.** Equally likely losses 0,1,2,3,4 have 80% VaR 3 using the left quantile convention, and ES 4 using the integrated-quantile definition. The naive average of all values at or above 3 would be 3.5 and does not match that definition. Quantile conventions matter even in small examples.

Drawdown is decline from an earlier running peak, measured consistently after handling external flows. Maximum drawdown is path-dependent; two return series can have identical mean and variance but different drawdowns. Stress testing asks what happens under specified shocks; reverse stress testing asks what could cause failure. Neither yields a reliable event probability without a defensible probability model.

Liquidity risk includes spread, market impact, depth and time to liquidate. Funding liquidity concerns cash needed for withdrawals, collateral and margin. Gross/net exposures, concentration and correlated collateral calls can reveal risks hidden by aggregate volatility. Tail dependence can differ from ordinary correlation.

Model risk arises from wrong assumptions, estimation, implementation, misuse and drift. Verification asks whether the code matches its specification. Validation asks whether the specification is fit for its purpose. A passing unit test establishes neither data truth nor market validity. Use independent benchmark cases, limiting cases, dimensional analysis, stress behavior, reconciliation and sensitivity, not only outputs from the same library.

Probabilities, confidence intervals and scenario ranges represent different uncertainty statements. A Bayesian credible interval is conditional on a prior and likelihood; a frequentist confidence procedure concerns repeated sampling. Monte Carlo standard error measures simulation noise, not uncertainty about whether the model is true. Record epistemic gaps separately from estimated stochastic variability.

## Evidence and depth

Source map: [ES-DEFINITION](../sources.md#es-definition), [FRM](../sources.md#frm), [CFA-III-PM](../sources.md#cfa-iii-pm), [NUMERICAL-FOUNDATIONS](../sources.md#numerical-foundations). These are supporting references, not certification of every equation. This article is an introductory reference; specialized methods listed in the coverage register still require full specifications and independent review.

[Reference index](README.md)
