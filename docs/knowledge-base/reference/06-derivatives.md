# Derivatives, optionality and volatility

A derivative's payments depend on an underlying observation or event. A forward commits to exchange at a future date; a future has exchange-defined settlement and margin; a swap exchanges payment streams; an option gives a contractual right with an exercise rule. Document multiplier, deliverable, observation calendar, settlement method and lifecycle before computing value.

At expiry, a call payoff per underlying unit is max(S-K,0); a put is max(K-S,0). Profit includes premium, financing and costs. In a frictionless constant-rate, continuously dividend-yielding equity setting, the forward delivery price is F_0=S_0 exp((r-q)T). A newly agreed forward has zero value under the same assumptions; delivery price is not the contract's present value.

For European options with the same expiry and strike under the same simple assumptions, put-call parity is C-P=S_0 exp(-qT)-K exp(-rT). **Example.** With S=100, K=100, T=1, r=5%, q=0 and put price 6, the parity-consistent call is 10.877058. This relation can expose inconsistent inputs; exercise style, borrow constraints and transaction costs determine whether an apparent deviation is actionable.

In the Black-Scholes-Merton idealization, C=S exp(-qT)N(d1)-K exp(-rT)N(d2), d1=[ln(S/K)+(r-q+sigma^2/2)T]/(sigma sqrt(T)), d2=d1-sigma sqrt(T). N is the standard-normal cumulative distribution and sigma is annualized log-return volatility. This assumes a continuous diffusion with constant volatility/rates and idealized replication. T=0 and sigma=0 need limit cases; American exercise generally requires another solver.

Implied volatility is the model input reproducing a price, not observed future volatility. A surface organizes it by strike/moneyness and maturity. Smile/skew describes strike variation; term structure describes maturity variation. Static-arbitrage checks operate on compatible option prices, not merely a smooth-looking chart. Local volatility, stochastic volatility, jumps and SVI are distinct model families with calibration and validity constraints requiring separate specifications.

Delta measures first price sensitivity to the underlying; gamma measures its curvature; vega volatility sensitivity; theta time sensitivity; rho rate sensitivity. Specify whether vega/rho refer to a unit or a percentage-point change and theta to a day or year. Greeks describe local behavior; jumps, liquidity and discrete hedging create residual risk. Short options can produce large contingent losses and margin needs despite a small initial premium.

Pricing under a risk-neutral measure supports replication valuation under model assumptions; forecasting real-world returns uses a physical measure. Do not substitute one for the other. Exercise, assignment and settlement are operational events that can change holdings and funding, not just terminal payoff formulas.

## Evidence and depth

Source map: [CFA-II](../sources.md#cfa-ii), [OIC-EXERCISE](../sources.md#oic-exercise), [OIC-ASSIGNMENT](../sources.md#oic-assignment), [SVI](../sources.md#svi). These are supporting references, not certification of every equation. This article is an introductory reference; specialized methods listed in the coverage register still require full specifications and independent review.

[Reference index](README.md)
