# Volatility models, calibration and arbitrage

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [11-option-pricing](11-option-pricing.md).

## Surface representation and constraints

Choose strike K, forward F, log-moneyness k=ln(K/F), maturity T and total variance w(k,T)=sigma_imp²T. A surface fits market option prices or derived implied volatility under recorded curve and exercise conventions. Weight residuals by a declared price/volatility/bid-ask criterion; do not fit stale or incompatible quotes as if they were simultaneous.

For fixed maturity, call price should be decreasing and convex in strike under compatible European claims. Numerical finite-strike convexity tests use unequal-grid slopes correctly. A calendar comparison needs consistent underlying/discount/dividend conventions; total-variance monotonicity statements depend on the chosen coordinates and model setup. Smoothness alone does not prove no arbitrage.

Raw SVI proposes w(k)=a+b[rho(k-m)+sqrt((k-m)²+s²)], with b≥0, s>0 and |rho|<1. Basic positivity conditions are not sufficient for absence of butterfly or calendar arbitrage. Example a=.02,b=.1,rho=0,m=0,s=.1 gives ATM total variance .03; at T=1, implied volatility sqrt(.03)=17.320508%. This is an equation example, not a fully constrained calibrated surface. SSVI and exact no-arbitrage admissibility require dedicated derivations.

## Dynamics and calibration

Heston specifies dS=(r-q)Sdt+sqrt(v)S dW1, dv=kappa(theta-v)dt+xi sqrt(v)dW2, with correlation rho between Brownian motions. Parameters govern mean reversion, long-run variance, variance volatility and dependence. Feller-type conditions concern variance boundary behavior; discretization schemes have their own positivity/bias properties. SABR specifies coupled forward/volatility dynamics with elasticity beta; formula approximations have asymptotic domains. Local volatility uses a deterministic sigma(S,t) consistent with a specified European-price surface under its assumptions. Jumps add discontinuous moves and alter hedging/completeness.

Procedure: clean quotes; freeze curve/forward versions; declare model/parameter domain; use multi-start or a justified convex method; report residuals against spreads, parameters and stability; test extrapolated wings/maturities; independently reprice out-of-fit quotes. Do not equate low calibration error with identifiable parameters or accurate exotic pricing. These dynamic descriptions are substantive model foundations; full characteristic-function integration, Dupire differentiation and SABR/SSVI implementation formulas still require specialist contracts.

## Evidence boundary

Supporting source map: [SVI](../sources.md#svi), [QUANTLIB](../sources.md#quantlib). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
