# Option pricing and numerical solvers

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [10-curves-credit](10-curves-credit.md); [01-statistics](01-statistics.md).

## Baseline pricing models

Use the [BSM equation and measure conventions](../reference/06-derivatives.md) for continuous-dividend equities. Black's forward model prices C=D[F N(d1)-K N(d2)], d1=[ln(F/K)+.5sigma²T]/(sigma sqrt(T)), d2=d1-sigma sqrt(T), requiring positive F,K. Bachelier prices C=D[(F-K)N(d)+sigma_N sqrt(T)phi(d)], d=(F-K)/(sigma_N sqrt(T)); normal volatility has price units per sqrt(year), unlike dimensionless lognormal volatility. A zero-volatility or zero-time limit is discounted intrinsic value under compatible forward timing.

A CRR binomial step sets u=exp(sigma sqrt(dt)), d=1/u, p=[exp((r-q)dt)-d]/(u-d). Require p∈[0,1]. Start with terminal payoff and recurse discounted expectation; American exercise takes max(continuation, immediate intrinsic) at eligible nodes. Discrete dividends and negative prices need a different construction. Example a one-step tree S=100,u=1.1,d=.9,r=0,K=100 has p=.5 and call value 5; it is a declared simple tree fixture rather than CRR-calibrated diffusion.

Monte Carlo simulates under the selected pricing measure and discounts expected payoff. For constant BSM dynamics, S_T=S0 exp[(r-q-.5sigma²)T+sigma sqrt(T)Z]. Antithetic draws and control variates reduce estimator variance under stated construction. American exercise requires optimal stopping, such as a separately validated regression-based algorithm; simply averaging intrinsic values is wrong. PDE finite differences require grid, boundary/terminal conditions, time scheme and convergence analysis.

## Implied volatility and sensitivities

For valid European quotes, bracket sigma and solve model_price(sigma)-observed_price=0 with residual and tolerance. Reject prices outside admissible bounds; quotes on bounds can imply zero or unbounded limiting volatility. Low vega makes implied vol unstable. Equity call bounds under nonnegative rates/compatible dividend inputs include discounted intrinsic lower bound and prepaid-forward upper bound; put bounds use the analogous discounted strike. Exercise-style differences require separate bounds.

Greeks are partial derivatives holding stated inputs fixed. Central differences use paired repricing and multiple step-size checks. Record per-unit versus percentage-point vega, daily versus yearly theta, multiplier and currency. Put-call parity, monotonicity, limiting cases, tree/PDE refinement and an independent benchmark are mandatory validation cases. Hedging error, spread, borrow and discrete exercise remain economic/operational risks outside the idealized solver.

## Evidence boundary

Supporting source map: [QUANTLIB](../sources.md#quantlib), [OIC-EXERCISE](../sources.md#oic-exercise), [SCIPY-ROOTS](../sources.md#scipy-roots). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
