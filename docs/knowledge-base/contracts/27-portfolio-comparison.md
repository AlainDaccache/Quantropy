# Profile-bound portfolio comparison and funded replay

ID: KC-27. Date: 2026-10-13. Status: self-contained offline prototype contract with author-run numerical checks; empirical and independent domain review pending. Prerequisites: [LW identity estimator](26-ledoit-wolf.md), [allocation objectives](06-allocation.md), [causal replay](14-backtesting.md), [performance](16-performance.md).

## Decision and evidence standard

Compare predeclared allocation policies under common observations, timing, costs and feasible sets. This is a vertical research workflow from data/profile to estimates, feasible target weights, reconciled wealth and an auditable report. It answers how policy outcomes differ under a declared scenario. It does not determine the owner's mandate or establish future optimality.

DeMiguel, Garlappi and Uppal's 2009 study found no consistent dominance of 1/N across its tested models, datasets and performance measures. Its Sections 3-4 use rolling estimation and report turnover and cost effects. This supports a demanding simple benchmark, not a universal conclusion that optimization is useless. The covariance paper addresses estimation loss; the diversification paper addresses portfolio outcomes. Their questions and experiments differ. This prototype replicates neither study. See [DGU-2009](../sources.md#dgu-2009).

## Profiles and data boundary

| Layer | Explicit fields and effect |
|---|---|
| User | `user_role`: owner, trader, researcher or portfolio_manager; role recorded for workflow context, not proof of authority to manage accounts |
| Mandate | `mandate_id`, `currency`, `period_label`, `allocation_basis`, `max_weight`; this implementation compares fully invested long-only funded wealth with a common concentration cap |
| Account | `account_profile_id`, `permitted_labels`, `cost_bps`; scenario access and symmetric proportional trading cost, not actual broker permissions or legal eligibility |
| Deployment | `deployment=offline`; the implemented capability fails for other environments |

All fields are required. Unknown personal details remain named scenarios. Labels may denote funded assets or funded strategy sleeves across asset classes and horizons. A raw futures price return, option quote return or long-short excess-return factor is not automatically a fully funded sleeve return. Broader short, leveraged, derivative, liability and tax profiles need their own funding and accounting contracts before this runner can accept them. The implementation boundary does not limit the research catalog.

Dataset fields: `labels`, `currency`, `period_label`, `allocation_basis=funded_total_return`, `provenance`, and `records`. Each record has timezone-aware ISO `start`, `end`, `available_at`, plus aligned decimal total `returns`. Require contiguous nonoverlapping intervals, start<end, available_at>=end and finite returns >=-1. Stream identity/order stays fixed. Zero/negative variance is an error for inverse volatility; a zero covariance is an error for GMV. Missingness, changing universes, external flows, revisions and frequency conversion are upstream or future contracts. Every value here has one declared availability timestamp; this is not a bitemporal vendor/revision store.

At decision time t (the start of evaluation interval t), use the most recent M prior records whose end and availability times are <=t; M is a predeclared integer >=2. Delayed observations are excluded until available. Record the actual training indices, including any gaps from delays. All policies begin on the first interval with sufficient eligible history and evaluate the same subsequent intervals. No current or future return enters fitting. Execution at the interval boundary is an explicit stylized assumption: instantaneous access to a just-published value at that boundary requires a separate latency/fill model in any real implementation.

## Policy procedure

Canonical objective definitions remain in KC-06. Implemented policies:

| ID | Estimator and construction |
|---|---|
| `equal_weight` | Equal weights, no estimated moments; feasible only if p*cap>=1 |
| `inverse_volatility` | n-1 sample variances; normalize reciprocal positive standard deviations; if needed apply Euclidean projection to the capped simplex |
| `sample_gmv` | n-1 sample covariance; minimize w'Sw on the capped simplex |
| `lw_identity_gmv` | KC-26 covariance; minimize the same objective and feasible set |

The inverse-volatility cap procedure is an explicit policy variant. Projection can change its risk characteristics and does not turn it into equal-risk-contribution allocation. Sample GMV and LW GMV differ in their covariance shape; a common scalar denominator adjustment alone would not change GMV weights. No policy estimates expected return or optimizes realized future return.

For GMV, divide covariance by its largest eigenvalue L>0. Reject materially indefinite matrices. Starting from equal weights, update w_next = projection(w - gradient/2), gradient = 2(S/L)w. Projection is clip(v-theta,0,cap), with theta found by 80 bisection iterations so weights sum to one. The normalized objective has gradient Lipschitz constant 2. Minimize gradient'v over the feasible set by filling the smallest-gradient entries up to cap. The convex objective gap certificate is G = gradient'w - min_v gradient'v. By convexity it bounds normalized suboptimality. Stop at G<=1e-10; after 20,000 updates fail explicitly. Check weight sum, bounds and finiteness before returning. Ill-conditioning can make convergence slow; numerical tolerance does not remove estimation uncertainty. Singular PSD covariance is admissible if nonzero, with potentially nonunique optima.

## Self-financing costs, drift and wealth

Weights are fractions of funded capital after transaction costs. At each decision let W be pretrade wealth, h be pretrade risky holdings divided by W, w be desired weights summing to one, c=cost_bps/10000 and q be the fraction of wealth remaining after trading costs. Initially W=1 and h=0: funding begins from cash. Solve

`q + c * sum_i |q*w_i - h_i| = 1`, with 0<q<=1.

Actual asset trades in units of W are q*w-h. Thus traded notional T=sum|q*w-h| counts buys plus sells, not half turnover, and costs are W*c*T=W*(1-q). With nonnegative fully invested weights and 0<=c<1, the left side is continuous and strictly increasing in q: its slope is at least 1-c. Bisection gives a unique root. Report the funding trade and do not ignore the cost of initial investment. Cash is not charged as a separately traded risky asset.

Apply the next interval's aligned return vector r: g=w'r, W_next=W*q*(1+g), net_return=q*(1+g)-1. Drifted next holdings are h_next_i=w_i*(1+r_i)/(1+g). Those holdings, rather than yesterday's target, determine the next rebalance. A concentration cap applies at decision times; market drift can exceed it between decisions. Zero portfolio gross wealth fails explicitly as exhaustion. Rebalancing occurs every evaluation interval; holding through several intervals would be a different policy.

Example: with c=.01 and initial cash, q=1/1.01; a 50/50 portfolio with returns .10 and 0 ends at wealth 1.05/1.01. Its pretrade weights next period are 11/21 and 10/21. Separately, h=(.6,.4), target=(.5,.5), c=.01 gives q=.998, T=.2 and cost=.002. After a 5% portfolio gross return, net growth is .998*1.05-1=.0479. Charges are part of the wealth equation, not an unfinanced subtraction from a full-dollar target.

## Report, use and validation limits

Each policy records every decision, training indices, target weights, estimator/solver diagnostics, traded notional, costs, gross/net return and wealth. Summaries include terminal wealth, compound net return, period arithmetic mean, n-1 period volatility and maximum drawdown including initial wealth. No annualization, Sharpe ratio, significance, utility or goal success is invented without their own timing/objective inputs. Summed turnover fractions use different pretrade wealth denominators; they are not a total currency expenditure.

Run from repository root with Python 3.10+ and NumPy. The generated report records the validated Python and NumPy versions; those fields identify the actual runtime.

```text
python -m quantropy_research examples/portfolio-comparison.json --output comparison.json
python -m unittest discover -s tests -p test_research_portfolio.py -v
python tools/verify_portfolio_research.py
```

The isolated package imports no legacy application/database/broker modules. The commands run from the source tree; legacy package installation and its old dependency pins are unvalidated for this prototype. It supplies a CLI and reusable Python functions; no full-stack UI or production integration is claimed. The [committed demonstration](../portfolio-comparison-verification.json) is entirely synthetic and includes input and code hashes. Its ranking is an arithmetic outcome of fictional data, not a policy recommendation or empirical return estimate.

Checks include a hand-computed partial-shrinkage case; positive-definiteness, trace, scale, translation and permutation relationships; analytical capped and boundary GMV cases; a three-stream objective grid; zero-variance and infeasible-profile rejection; prefix/future-perturbation causality; delayed availability; common evaluation intervals; initial funding, drift and cost reconciliation; and explicit exhaustion/convergence failure. These are meaningful implementation checks, not independent expert review. Source-function comparison is recorded separately.

Remaining work: survivorship and revision-aware datasets with rights and independent reconciliation; published strategy replication; dependence-aware confidence intervals and selection accounting; risk-budget/HRP/HERC/NCO/Bayesian/robust/tail/dynamic alternatives; explicit mandates for liability/tax/short/derivative economics; market impact, capacity, funding and execution lifecycle; prospective observation and domain review. Keep all research trials and negative outcomes. A synthetic test cannot graduate an investment policy to live use.

[Contract index](README.md) · [Work ledger](../RESEARCH-WORK-LEDGER.md)
