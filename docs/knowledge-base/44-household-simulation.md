# Household, accumulation, retirement and FIRE simulation

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Use a shared economic simulation engine for broad-audience calculators and advanced planning. It should model household cash flows, account holdings, liabilities, taxes/fees, inflation, market scenarios and policy decisions. A compound-interest calculator is one simple view of that engine, not the whole model. Education scenarios should remain usable without a brokerage connection.

During accumulation, model income growth and interruptions, partner income, business income, pensions/employer benefits, mandatory/flexible spending, debt payments, education/property costs, taxes and account-specific contributions. Spending inflation need not equal wage growth or every category's inflation. Contributions occur at specified dates; borrowing and emergency cash have their own rates/liquidity. Include changes in household circumstances and uncertain income, not only smooth annual growth.

Retirement adds withdrawal sequencing, public/private pension timing, longevity, health/care costs, partner survival, taxes, account depletion rules, discretionary spending flexibility and legacy goals. Compare fixed-real, fixed-percentage, guardrail, funded-ratio and floor/upside policies. Cash buckets, bond ladders and annuities need their actual costs/risks; do not assume their labels eliminate sequence risk. [Retirement research](https://rpc.cfainstitute.org/research/foundation/2019/secure-retirement).

FIRE labels should be configurable scenario templates: conventional/full FIRE; lean/fat spending targets; coast scenarios with continued expense-covering work and reduced contributions; barista/partial-work scenarios; phased/semi-retirement. They are not standardized financial models. Show retirement age, required funding, contribution paths, downside/shortfall and spending tradeoffs rather than a universal multiple or a guaranteed withdrawal rate.

Sequence example: start with 100, withdraw 10 at the beginning of each of two periods, and earn +25% then -20%. Ending wealth is 82. Reverse the same returns and it is 77.5. With no withdrawals the same return product preserves equal ending wealth. Contributions also make return order relevant. The engine must make flow timing explicit.

Scenario engines should compare deterministic paths, historical rolling windows, block bootstrap and calibrated multivariate stochastic/regime paths. Preserve return/inflation/income dependence where justified; show model sensitivity, sampling error, horizon and failure definition. Outputs include shortfall amount/duration, spending paths, funding ratios and tail outcomes, not only one probability of success.

Acceptance: independently calculated contribution/withdrawal/debt/inflation cases; nominal/real and currency consistency; tax-year/account adapters; goal policies tested under identical paths; no negative cash silently finances spending. Calculators should expose assumptions and explain uncertainty in plain language.

## Coverage checklist

- Shared household policy and economic simulation engine
- Income growth interruptions partner business cash flows
- Spending inflation debt housing education and liquidity
- Account contribution benefits tax and fee timing
- Accumulation contribution and savings policy scenarios
- Longevity pension partner health and care scenarios
- Fixed real percentage guardrail floor-upside policies
- Lean fat coast barista phased FIRE scenario templates
- Sequence-of-returns and contribution-order fixtures
- Historical bootstrap stochastic regime scenario comparison
- Shortfall duration funding consumption and tail reports
- Beginner calculators with advanced assumption controls

## Research sources

- [RETIREMENT](sources.md#retirement)
- [CFP](sources.md#cfp)
- [CRA](sources.md#cra)
- [GIPS](sources.md#gips)

[Knowledge base index](README.md)
