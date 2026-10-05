# Performance diagnostics and attribution conventions

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [01-statistics](01-statistics.md); [14-backtesting](14-backtesting.md).

## Inputs

Use comparable investor-net returns, external-flow-adjusted account valuations, benchmark, risk-free series and sampling frequency. Costs are either included in returns or attributed separately with exact reconciliation, never subtracted twice. Return units in numerators and denominators must match.

| Diagnostic | Declared baseline |
|---|---|
| CAGR | (ending/starting flow-free wealth)^(1/years)-1 |
| Sharpe | mean(period excess return)/standard deviation(period excess return); square-root annualization only with suitable dependence |
| Sortino | mean(return-target)/sqrt(mean(min(return-target,0)²)) over all observations |
| Information ratio | mean(active return)/std(active return) |
| Treynor | mean(excess return)/market beta, with beta sign/near-zero limitations |
| Jensen alpha | CAPM regression intercept for a declared horizon |
| Calmar | CAGR/absolute maximum drawdown with matched sample |
| Omega at threshold L | sum max(r-L,0)/sum max(L-r,0) for equally weighted sample |
| Profit factor | gross positive trade P&L/absolute gross negative trade P&L under complete net trade attribution |
| Hit/payoff | fraction profitable trades; average winner/absolute average loser |
| Ulcer index | sqrt(mean(percent drawdown²)) using the stated peak/reset convention |
| Concentration | sum squared capital weights; inverse gives a simple concentration count, not independent risk bets |

Skewness and kurtosis require a declared biased/unbiased estimator and excess versus raw kurtosis. Drawdown path DD_t=W_t/max_(s≤t)W_s-1; duration measures time below the prior peak. External contributions should not create false recovery. Zero denominators yield explicit undefined states; no losing trades makes profit factor unbounded/undefined rather than automatically trustworthy.

## Brinson single-period decomposition

For exhaustive sectors i, portfolio weights wp, benchmark weights wb, sector returns Rp,Rb and total benchmark RB, allocation=sum(wp-wb)(Rb-RB); selection=sum wb(Rp-Rb); interaction=sum(wp-wb)(Rp-Rb). Under fully invested compatible portfolios these sum to portfolio minus benchmark return. Example portfolio weights (.6,.4), benchmark (.5,.5), portfolio sector returns (.12,.04), benchmark (.10,.05) give active return .013. Allocation .005, selection .005 and interaction .003 reconcile to .013. Multi-period attribution needs an explicit linking method.

Money-weighted IRR solves dated net-investor cash flows with a sign convention and legal rate domain. Multiple sign changes can create multiple roots. Tracking difference compares compounded net portfolio/benchmark outcomes; tracking error measures dispersion of active periodic returns. Exposure and turnover require cash/notional/factor bases and one-way/two-way definitions.

## Evidence boundary

Supporting source map: [GIPS](../sources.md#gips), [CFA-RETURNS](../sources.md#cfa-returns). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
