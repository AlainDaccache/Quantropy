# Risk premia, anomalies, alpha and retail feasibility

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

A risk premium is compensation associated with bearing an exposure or adverse-state risk. An anomaly is a return pattern that a stated model struggles to explain. Alpha is residual performance relative to a declared benchmark/model after relevant costs; it is not a permanent property of an indicator. A return source can have competing explanations, and a popular “alternative premium” label does not settle the academic debate.

Build a strategy research library, not a promise that these opportunities are available profitably today. Core families include market/duration/credit exposures and styles such as value, momentum, carry, defensive, trend and volatility. The latter six appear in AQR's overview; actual access and implementation differ materially. [AQR research](https://www.aqr.com/Insights/Research/White-Papers/Understanding-Alternative-Risk-Premia). Academic low-beta portfolios can require leverage and shorts; a long-only low-vol fund is not the same construction. [Betting Against Beta](https://www.nber.org/papers/w16601).

Candidate alpha families include accounting/earnings information, event-driven research, relative value/statistical arbitrage, liquidity provision, macro forecasting and alternative data. These are research classifications, not verified edge claims. Some demand costly point-in-time data or very fast execution; others need legal/catalyst expertise, borrow or patient risk capital. Many supposed arbitrages retain basis, funding, timing and tail risk.

For each family store mechanism, evidence, original construction, investable expression, data, costs, turnover, capacity, financing, adverse states, crowding, retail limitations and current replication status. Long convexity/insurance may be useful protection even if its unconditional expected excess return is negative; avoid rejecting a hedge solely for low standalone Sharpe. Selling volatility should not be confused with free yield. [Variance-premium research](https://www.federalreserve.gov/econres/feds/expected-stock-returns-and-variance-risk-premia.htm).

The [strategy-family catalogue](strategy-families.csv) is a candidate research queue. A row becomes sourced only after exact paper/construction review, replicated after independent reproduction, feasible after cost/access tests, and live eligible only after the full operational gates. Include simple passive products as alternatives to self-built implementations.

## Coverage checklist

- Risk-premium anomaly alpha classification
- Market duration credit and liquidity exposures
- Value momentum carry defensive trend families
- Variance skew correlation and tail exposures
- Accounting earnings and event hypotheses
- Relative value and statistical arbitrage hypotheses
- Macro alternative-data and liquidity hypotheses
- Access turnover costs and capacity screening
- Crowding adverse states and diversification
- Replication and net retail feasibility evidence
- Hedges insurance and passive implementation alternatives

## Research sources

- [ARP](sources.md#arp)
- [BAB](sources.md#bab)
- [VRP](sources.md#vrp)
- [FF5](sources.md#ff5)
- [TREND](sources.md#trend)
- [CARRY](sources.md#carry)
- [OVERFIT](sources.md#overfit)

[Knowledge base index](README.md)
