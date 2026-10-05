# Rates, fixed income and credit

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

A bond is a schedule of promised cash flows with credit and option features. Provide clean/dirty price, accrued interest, yield, duration, convexity, spread measures and total return. Yield to maturity is not a guaranteed realized return; reinvestment, defaults, early calls and trading prices matter. [FINRA bonds](https://www.finra.org/investors/investing/investment-products/bonds).

Rates models need explicit day counts, business-day adjustment, settlement, compounding and calendars. Build discount and forward curves from instrument quotes using documented bootstrapping/interpolation. Add spot/forward yields, key-rate sensitivities, inflation-linked cash flows and scenario shifts/twists. Distinguish physical forecasting measures from risk-neutral pricing. Interest-rate futures and options need product-specific settlement and convexity considerations.

Credit modeling includes ratings history, issuer capital structure, default/hazard and recovery assumptions, structural/reduced-form approaches, spread duration and liquidity. Separate promised yield from expected loss-adjusted return. Callable/putable/convertible bonds and mortgage securities need optionality and path dependence; option-adjusted spread is model-dependent. Structured credit and OTC swaps are advanced analysis modules, not essential first live products.

Bond market data is often sparse and stale. Trade reports are evidence of transactions, not necessarily the price/size available now. Include odd-lot retail costs, minimum sizes, accrued interest and execution markups. [TRACE documentation](https://www.finra.org/finra-data/fixed-income/about-trade-activity). A bond ETF's exposures and price behavior are different from an individual bond held to maturity.

Acceptance: hand-worked coupon/discount fixtures; schedule edge cases; clean plus accrued equals dirty; duration agrees with revaluation; curve instruments reprice within justified tolerances; default/call scenarios reconcile cash. Implement country and tax conventions separately.

## Coverage checklist

- Bond cash-flow schedules and accrued interest
- Price yield duration convexity
- Discount and forward curve construction
- Key-rate DV01 and curve scenarios
- Inflation-linked debt and real yields
- Credit spreads default recovery
- Structural and reduced-form credit models
- Callable putable convertible bonds
- Mortgage prepayment and structured credit analysis
- Swaps swaptions and interest-rate models
- Retail liquidity markups and odd lots
- Bond fund look-through and tracking

## Research sources

- [FINRA-BONDS](sources.md#finra-bonds)
- [TRACE](sources.md#trace)
- [QUANTLIB](sources.md#quantlib)

[Knowledge base index](README.md)
