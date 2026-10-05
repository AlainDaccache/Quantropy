# Time, money, cash flows and units

Money at different dates cannot be added meaningfully until a valuation date and discounting convention are chosen. A cash flow is an amount, currency, payment date and legal condition. A discount factor D(t) is the present value of one unit paid at date t under a specified curve and credit assumption.

For an effective rate r per period, PV = CF_t/(1+r)^t and FV = PV(1+r)^t. For multiple dated flows, PV = sum(CF_t D(t)). A continuous rate z gives D(t)=exp(-zt). An annual nominal rate j compounded m times has effective annual rate (1+j/m)^m-1. Never interchange these rates silently. Year fractions require a day-count convention; actual/365 and 30/360 can give different interest amounts.

An ordinary annuity pays A at each period end: PV=A[1-(1+r)^(-n)]/r. At r=0 use PV=nA. An annuity due pays at each period start and has PV multiplied by (1+r). A growing perpetuity has PV=CF_1/(r-g), only when r>g and perpetual growth and discount assumptions are coherent. These equations assume equal periods; irregular payments need date-specific factors.

**Example.** 100 invested for two years at 5% becomes 110.25. Three annual end-of-year payments of 100 discounted at 5% have PV=272.324803. A three-period loan of 1,000 at 5% requires payments of 367.208565. Each payment first covers interest on the opening balance; the remainder reduces principal. Rounding and a final balancing payment matter in a real loan schedule.

Nominal returns include inflation. Exact real return is (1+r_nominal)/(1+inflation)-1. At 5% return and 2% inflation, it is 2.941176%, not exactly 3%. Discount nominal cash flows with a nominal rate and real cash flows with a compatible real rate. Match currency as well as inflation basis.

NPV adds discounted incremental project flows, including the initial cost. IRR is a rate making NPV zero; multiple sign changes can create multiple or no economically useful IRRs. Comparing mutually exclusive projects by IRR alone can reverse the NPV decision. An annualized return is not a payment guarantee.

**Boundaries.** Negative rates are possible; discrete accumulation requires 1+r>0 for general real exponents. Forecast discount rates need currency, maturity, risk and valuation-purpose definitions. Tax, default and embedded options are additional economic inputs, not adjustments that can always be hidden inside one rate.

## Evidence and depth

Source map: [CFA-I](../sources.md#cfa-i), [DAMODARAN](../sources.md#damodaran). These are supporting references, not certification of every equation. This article is an introductory reference; specialized methods listed in the coverage register still require full specifications and independent review.

[Reference index](README.md)
