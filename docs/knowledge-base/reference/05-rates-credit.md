# Fixed income, curves and credit

A bond is a contract for dated payments with issuer, seniority, currency, collateral and optionality. Its promised payments are not necessarily its expected payments. A discount curve provides factors D(t); the value of deterministic cash flows is sum(CF_t D(t)). Curve construction requires instruments, quote types, calendars, settlement, interpolation and collateral conventions.

For an annual-coupon non-callable bond using a flat annual yield y, P=sum(CF_t/(1+y)^t). Yield to maturity solves this equation for promised flows at the observed full price. It is not an assured realized return: reinvestment, sale timing, default and costs can differ. Full (dirty) price equals quoted clean price plus accrued interest under the contractual accrual convention.

Macaulay duration=sum[t PV(CF_t)]/P. Modified duration=D_Mac/(1+y) in this annual convention. For a small parallel yield change, change in P/P approximately equals -D_mod change in y, with convexity correction +0.5 C(change in y)^2. Key-rate duration measures sensitivities to selected curve points under an explicitly specified shock and interpolation. Embedded options need revaluation; fixed-cash-flow duration is insufficient.

**Example.** A two-year bond with face 100 and annual coupon 5 has price 100 at yield 5%. Macaulay duration is 1.952381 years and modified duration 1.859410. A one-basis-point rise reduces price by approximately 0.018594 per 100 face. Actual repricing includes convexity; units distinguish percent yield from basis points.

Credit risk concerns non-payment, recovery, migration and exposure. A simplified one-period expected credit loss is PD times LGD times EAD: probability of default, loss given default and exposure at default. With PD 2%, LGD 40% and EAD 1,000, it is 8. This is an expectation under chosen assumptions, not a tail-capital measure or a full multi-period accounting impairment model.

Spreads bundle default compensation, liquidity, risk aversion and structural effects. A Z-spread adds a constant spread to a chosen curve; an option-adjusted spread depends on the model used to remove option value. Recovery assumptions, competing default models and discount measures cannot be mixed freely. Floating-rate notes, inflation-linked securities, securitizations, convertibles and distressed debt require distinct cash-flow engines.

Remaining advanced work includes multi-curve bootstrap, forward rates, swaps, repo, mortgage prepayments, structured-credit waterfalls, stochastic rates, reduced-form and structural credit models, CVA/DVA/FVA and collateral agreements. Those methods are inventoried, not derived by this introductory article.

## Evidence and depth

Source map: [FINRA-BONDS](../sources.md#finra-bonds), [CFA-II](../sources.md#cfa-ii). These are supporting references, not certification of every equation. This article is an introductory reference; specialized methods listed in the coverage register still require full specifications and independent review.

[Reference index](README.md)
