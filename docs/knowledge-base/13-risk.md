# Risk, leverage and sizing

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Risk means failing the investor's goals or surviving neither a market shock nor an operational failure. Volatility is one useful measure, not the definition. Analyze drawdown depth/duration, tails, concentration, liquidity, leverage, financing, counterparty, currency, inflation and model uncertainty.

Provide historical and parametric VaR/expected shortfall with clearly stated confidence, horizon, data and valuation assumptions. Add full-revaluation historical and hypothetical scenarios: equity crash, rate jump, inflation shock, correlation convergence, volatility/skew change, FX shock, default, market closure and margin escalation. Combine shocks and cash demands; an apparently hedged portfolio can still run out of collateral.

Sizing must reflect estimation error and contract granularity. Kelly-style sizing depends strongly on uncertain distributions and idealized assumptions; it is not a default capital recommendation. Use conservative capped budgets, sensitivity and drawdown/liquidity simulations. Stops do not guarantee a maximum loss through gaps, limit moves or broker outages.

Separate pre-trade checks, continuous portfolio checks and emergency operations. Limits should address order quantity/value, concentration, gross/net exposure, margin headroom, stale data, daily loss and unauthorized instruments. A kill switch needs defined behavior: stop new orders, cancel eligible working orders and optionally reduce positions according to a reviewed policy. “Kill” must not blindly submit liquidation orders into an uncertain market.

Acceptance: known shock portfolios produce expected exposures/losses; scenario funding accounts for settlement timing; real positions plus working orders are included; failed/stale risk calculations block sensitive actions. Document exceptions and who can change limits. Risk reports never claim that a confidence interval bounds all possible losses.

## Coverage checklist

- Volatility drawdown and tail metrics
- VaR expected shortfall and assumptions
- Historical hypothetical combined stress
- Liquidity financing and collateral risk
- Concentration and correlated exposures
- Greeks and full-revaluation risk
- Conservative sizing and Kelly sensitivity
- Pre-trade limits and working-order exposure
- Margin headroom and cash forecasting
- Kill switch and emergency policies
- Risk exceptions and limits governance

## Research sources

- [LEAN-LIVE](sources.md#lean-live)
- [IBKR-WHATIF](sources.md#ibkr-whatif)

[Knowledge base index](README.md)
