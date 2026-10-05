# Household finance, retirement and insurance

A household plan coordinates earnings, spending, debt, reserves, protection, investment, taxes and transfer goals over time. Net worth equals assets minus liabilities at a date; affordability concerns future cash flows. Emergency liquidity and insurance protect against risks that a long-horizon expected return cannot pay on demand.

For end-of-period contribution C and withdrawal W, a simple balance recurrence is B_t=B_(t-1)(1+r_t)+C_t-W_t. Beginning-of-period cash flows instead participate in the period return. Spending can grow with an inflation path, earnings with an income path, and taxes with dated jurisdiction rules. Use explicit timing rather than calling every path a generic compound-growth calculator.

**Example.** Start at 100 and withdraw 10 at each year end. Returns +20%, then -20% leave 78. Reversing them leaves 74. Without withdrawals both paths leave 96. This is sequence-of-returns risk: the same compounded market return can produce different wealth when cash flows interact with the path.

Accumulation models need employment variability, salary growth, contributions, debt amortization, dependants and exceptional expenses. Retirement models need longevity, pensions, inflation-linked and nominal income, medical/care expenses, spending flexibility and bequests. Deterministic scenarios reveal sensitivities; stochastic simulation needs joint return/inflation assumptions, regime behavior and transparent uncertainty.

FIRE variants express goals and labor/spending choices rather than separate laws of finance. A rough target spending divided by withdrawal rate is a starting heuristic, not proof of perpetual funding. Coast-style plans reduce future contributions; part-time income changes withdrawals. Define failure as inability to fund essential needs or another explicit criterion, not merely terminal wealth below zero.

Insurance pools uncertain losses in exchange for premiums. Expected discounted benefit is the sum of payment amounts times payment probabilities times discount factors under a selected model. **Example.** A hypothetical benefit 1,000 payable in one year with probability 1% has expected present value 9.523810 at 5%, before expenses, profit, capital and risk adjustments. That is not a market premium quote.

Life-contingent annuities weight each future payment by survival probability; mortality tables, selection and cohort improvement assumptions matter. General insurance requires frequency/severity and reserving development models; reinsurance changes the loss allocation. Estate, succession, disability, long-term care and behavioral constraints also belong in household planning. Product suitability and local legal/tax details require separate dated references.

## Evidence and depth

Source map: [CFP](../sources.md#cfp), [RETIREMENT](../sources.md#retirement), [SOA-EDUCATION](../sources.md#soa-education). These are supporting references, not certification of every equation. This article is an introductory reference; specialized methods listed in the coverage register still require full specifications and independent review.

[Reference index](README.md)
