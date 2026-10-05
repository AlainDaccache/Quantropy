# Allocation objectives and constraints

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [05-estimators](05-estimators.md).

## Shared input contract

Use aligned expected return mu, covariance Sigma, initial weights w0, benchmark b, risk-free return rf and a horizon. The feasible set states sum weights, cash, short bounds, gross leverage, sector/country exposures and funding. Long-only fully invested means w≥0 and 1'w=1; these are not suitable defaults for every derivative book. Objectives are below; changing constraints creates a different problem.

| Objective | Mathematical definition |
|---|---|
| Equal weight | w_i=1/n for eligible assets |
| Inverse volatility | w_i=(1/sigma_i)/sum(1/sigma_j), requiring positive sigma |
| Mean variance | Maximize mu'w-(gamma/2)w'Sigma w for gamma>0 |
| Global minimum variance | Minimize w'Sigma w; minimizing its square root is an alias |
| Target return/risk | Minimize variance with mu'w≥target; or maximize mu'w with variance≤budget |
| Maximum Sharpe | Maximize (mu'w-rf)/sqrt(w'Sigma w) for the declared funded-weight convention |
| Tracking error | Minimize (w-b)'Sigma(w-b); information ratio uses expected active return divided by active volatility |
| Diversification ratio | Maximize sum w_i sigma_i / sigma_p, ordinarily under long-only positive-volatility assumptions |
| Minimum correlation | Minimize w'Cw using correlation C; economically this rescales inputs and is not the same as variance |
| Semivariance | Minimize scenario average of min(r_p-target,0)² with target/horizon defined |
| Worst case | Minimize max_s loss_s(w) over explicitly chosen scenarios |
| Kelly | Maximize scenario expectation log(gross wealth(w)), requiring positive wealth in all supported outcomes |

For nonsingular Sigma with only full-investment constraint and unrestricted shorts, minimum-variance w=Sigma^(-1)1/[1'Sigma^(-1)1]. With independent volatilities .1 and .2 this gives (.8,.2). Additional constraints invalidate that closed form. Kelly may create intolerable drawdowns under estimated probabilities; fractional/capped allocations are policies, not an estimation cure.

Turnover penalty c'abs(w-w0), leverage limit sum abs(w_i)≤L and cardinality sum z_i≤k (binary z) make economic restrictions explicit. Tax-aware allocation needs lots, realized gains, cash taxes, account rules and sales constraints. Multi-period allocation chooses future holdings under wealth, costs and information transitions; a static objective repeated daily is not automatically the same problem.

Mean-skew-kurtosis, factor budgeting, liability-relative and goal-based objectives need loss and utility definitions. Distributionally robust allocation needs an ambiguity set and distance/radius; “robust” without these is underspecified. Report infeasibility, dual sensitivity where applicable and sensitivity to estimates. Never default to an unconstrained solution after a constrained solver fails.

## Evidence boundary

Supporting source map: [CVXPY-QP](../sources.md#cvxpy-qp), [PYPORTFOLIOOPT](../sources.md#pyportfolioopt), [RISKFOLIO](../sources.md#riskfolio). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
