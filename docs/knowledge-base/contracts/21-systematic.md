# Systematic futures, FX and strategy economics

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [13-factors](13-factors.md); [14-backtesting](14-backtesting.md).

## Contract and position accounting

A futures position has a contract month, multiplier, tick size, expiry, settlement, delivery obligations and margin schedule. Per-contract price P&L is multiplier*change in quoted price under its exchange contract rules. Notional is an exposure proxy, not cash paid; variation margin is a cash transfer. Continuous research prices require a stated roll/splice adjustment; they cannot be submitted as an instrument or interpreted as executable cash P&L.

Example one contract with multiplier 50 increases from 100 to 102: price P&L is 100 before fees/funding. A volatility target can size contracts as risk budget/(forecast price-volatility*multiplier), with horizon matching, integer rounding, liquidity and margin constraints. A small forecast volatility must not trigger unbounded leverage; floors/caps and funding stress are part of the policy.

## Signals and economic distinctions

Trend can use a past-return sign, moving-average difference or regression slope, computed from a declared causal series/window. Time-series trend is different from cross-sectional momentum. Carry estimates returns from holding an exposure assuming selected prices/curves remain unchanged; the economic definition differs across rates, FX, commodities and options. A commodity curve slope can reflect storage, seasonality and scarcity; it is not a universal guaranteed roll return.

FX return requires quote orientation, spot movement and funding/hedge cash flows. A carry portfolio selects funding/investment currencies with accessible instruments and models crash/funding risk. Relative-value spread trading requires contract hedge ratios, cointegration or economic relationships, entry/exit, risk and costs; historical correlation alone does not justify a mean-reversion trade.

Retail feasibility includes data coverage, contract minimum size, collateral, shortability, access, expiry monitoring and legal/account restrictions. Evaluate strategies as signals plus risk/cost/operational policies. Volatility targeting changes exposure after observations and can incur high turnover or procyclical deleveraging. No signal family is certified alpha by this description.

## Evidence boundary

Supporting source map: [TREND](../sources.md#trend), [CARRY](../sources.md#carry), [CME-CASH](../sources.md#cme-cash), [CME-EXPIRY](../sources.md#cme-expiry). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
