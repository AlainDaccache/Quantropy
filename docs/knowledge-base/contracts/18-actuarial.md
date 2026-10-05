# Insurance mathematics, reserves and pension obligations

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [01-statistics](01-statistics.md); [10-curves-credit](10-curves-credit.md).

## Life-contingent baseline

Let T_x be remaining lifetime at age x, survival p_x(t)=P(T_x>t), and q_x,k probability of death during year k conditional on survival to its start. Under annual payments and constant effective discount v=1/(1+i), a unit life-annuity-immediate APV is sum_(k≥1) v^k p_x(k). A term death benefit B paid at the end of death year has APV=sum_(k=1..n) B v^k[p_x(k-1)-p_x(k)]. Specify cohort/period mortality, timing and selection effects.

Example one-year survival .99, benefit 1,000 on death and rate 5% gives death-benefit APV 9.523810. A two-year annuity pays 100 only if alive each year with survival .99 and .97: APV=100*.99/1.05+100*.97/1.05²=182.267574. Expenses, profit, capital and risk loadings distinguish a premium from expected benefit PV. A prospective net reserve at a future date is conditional PV of future benefits minus future premiums under its stated basis, not automatically the accounting/regulatory reserve.

## General-insurance baseline

Aggregate loss S=sum_(j=1..N) X_j. Under independent identically distributed severities independent of N, E[S]=E[N]E[X] and Var(S)=E[N]Var(X)+Var(N)E[X]². Poisson frequency lambda=2 and deterministic severity 100 give expected loss 200 and variance 20,000. Dependence/catastrophes require another model.

Chain ladder uses cumulative paid/incurred claim triangles and age-to-age factors estimated from comparable development data, then projects ultimate losses. It assumes stable development patterns and appropriate exposure/case-reserving treatment; sparse or changing portfolios can violate it. Bornhuetter-Ferguson combines expected ultimate loss with observed development. These reserve algorithms need detailed triangles and assumptions before implementation.

Proportional reinsurance shares claims by contract ratio; excess-of-loss recovery for one event can be min(max(loss-attachment,0),limit), subject to aggregation, reinstatement and counterparty terms. Example loss 150, attachment 100 and limit 30 gives recovery 30 and retained loss 120. Credibility blends experience with a prior/reference according to an explicit variance/exposure model; ruin models study capital exhaustion over time.

Pension liabilities combine benefit rules, salary/service, mortality, retirement behavior and discount basis. Compare asset/liability sensitivities and funding cash flows. Full actuarial pricing/reserving and legal bases require specialist review; basic equations cannot replace a certified actuarial assessment.

## Evidence boundary

Supporting source map: [SOA-SURVIVAL](../sources.md#soa-survival), [SOA-EDUCATION](../sources.md#soa-education). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
