# Probability, statistics and econometric foundations

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: Foundational arithmetic and the reference reading path.

## Objects and equations

A probability distribution assigns nonnegative mass totaling one. For a discrete variable X, E[X]=sum p_i x_i and Var(X)=E[(X-E[X])²]. Cov(X,Y)=E[(X-E[X])(Y-E[Y])]; correlation divides by both standard deviations and is undefined when either is zero. Conditional expectation describes a distribution after specified information, not an observed future fact.

For n equally weighted observations, sample mean is sum x_i/n and the conventional unbiased sample variance uses sum(x_i-mean)²/(n-1) when n>1 under an iid sampling interpretation. Covariance uses paired dates and the same centering. Missing observations require a declared policy: pairwise deletion can produce a non-positive-semidefinite matrix. Log return ln(P_t/P_(t-1)) adds across time; simple return P_t/P_(t-1)-1 combines multiplicatively. Negative asset prices invalidate that log transformation.

## Estimation procedure

Define population, sample selection, horizon, dependence and estimator before fitting. OLS minimizes squared residuals for y=X beta+epsilon; with full-column-rank X, beta_hat=(X'X)^(-1)X'y. QR/SVD is normally numerically preferable to explicitly forming the inverse. A coefficient is conditional on included regressors; omitted confounders can defeat a causal interpretation. Heteroskedasticity-robust or HAC covariance addresses specified inference issues, not omitted variables or data leakage. Clustered panel errors require a sampling-unit justification.

Stationarity means a selected distributional property does not change with time. A unit-root price series can produce misleading level regressions; cointegration models a stationary combination of nonstationary variables under a specific hypothesis. Differencing and detrending answer different questions. ADF, KPSS and Johansen procedures need distinct lag, trend, null and sample assumptions. These tests are not fully specified here.

## Worked and boundary cases

Observations 1,2,3 have mean 2 and sample variance 1. If y=2+3x at x=0,1,2, OLS with intercept returns 2 and 3 and zero residual sum of squares. This exact fit cannot supply a meaningful residual-noise estimate for inference about an uncertain world. Two identical columns in X destroy unique coefficient identification even when fitted predictions remain identifiable.

An iid mean standard error is s/sqrt(n); serial correlation requires another variance estimator. A confidence interval describes a sampling procedure; a Bayesian credible interval is conditional on a prior and likelihood. Report sample size, estimator, units and assumptions. Bootstrapping must preserve relevant dependence and refit the whole selection process when assessing selection uncertainty.

## Evidence boundary

Supporting source map: [NUMERICAL-FOUNDATIONS](../sources.md#numerical-foundations), [STATSMODELS](../sources.md#statsmodels). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
