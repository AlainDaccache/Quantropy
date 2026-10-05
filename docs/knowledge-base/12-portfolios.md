# Portfolio construction and allocation

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Portfolio construction turns uncertain beliefs and constraints into holdings. The objective must include the investor's horizon, liquidity, taxes, tolerable losses and implementation costs. Optimizing a historical Sharpe ratio is not a complete financial plan.

Provide transparent baselines: cash, equal weights and diversified policy allocations. Compare mean–variance, minimum variance, risk budgets, volatility targets, hierarchical approaches and liability-aware allocation where justified. Expected returns and covariance are estimates, not facts. Shrinkage and robust/scenario approaches can reduce sensitivity, but require independent numerical specifications. [Ledoit–Wolf author page](https://ledoit.net/honey_abstract.htm). Black–Litterman is an advanced candidate; full mathematical source validation is pending.

Constraints include account permissions, long/short limits, leverage, concentration, sector/country/currency exposures, lot sizes, turnover, cash reserves, margin and tax budgets. Integer holdings matter for small accounts. Position sizing must distinguish economic notional, asset value and derivative margin. Include cash and FX explicitly, rather than allocating every dollar to signals.

Research optimizer fragility by perturbing estimates and showing how weights change. Display marginal/component risk, diversification and scenario loss, with a meaningful baseline. Combine strategies by shared underlying exposure and dependence, not just separate backtest returns. Rebalancing uses current actual holdings and costs; a stored previous target is not the current portfolio.

Acceptance: budgets/constraints hold after rounding and estimated fees; infeasible problems return explanations; missing inputs cannot silently remove holdings; weights reproduce independently; results remain understandable under parameter perturbations. Allocation suggestions become proposed trades, then pass account-specific risk and execution checks.

## Coverage checklist

- Policy and strategic asset allocation
- Equal-weight cash and index baselines
- Mean variance and minimum variance
- Covariance shrinkage and robust estimates
- Risk parity and risk budgeting
- Hierarchical and Black Litterman research
- Goal and liability-aware allocation
- Constrained and integer optimization
- Tax and turnover-aware rebalance
- Strategy ensemble allocation
- Cash FX and margin allocation
- Optimizer stability and sensitivity

## Research sources

- [SHRINKAGE](sources.md#shrinkage)
- [VANGUARD](sources.md#vanguard)

[Knowledge base index](README.md)
