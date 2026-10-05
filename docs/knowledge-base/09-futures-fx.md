# Systematic futures and FX

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Begin with interpretable strategies: time-series trend, cross-sectional momentum, curve carry, relative value and risk-managed ensembles. Time-series momentum uses an instrument's own history; cross-sectional momentum compares instruments. They need different economic explanations and tests. Published evidence is a starting hypothesis rather than assurance. [Time Series Momentum](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum).

Carry is the return component associated with holding an exposure under a specified unchanged-state convention; its calculation differs across commodities, rates, FX and equities. Futures curve slope is not a universal standalone forecast. Contract spacing, seasonality, financing, storage/convenience yield and macro risk change interpretation. [Carry paper](https://www.nber.org/papers/w19325.pdf).

Use real contract prices for tradable P&L, rolls and settlement. Continuous series may support particular signals but need documented construction and cannot directly stand in for an actual holding. Back adjustments can alter price levels; ratio/log rules fail around zero or negative prices. Maintain expiry, first notice, liquidity and roll decisions known at the time. Include collateral interest, commissions, spreads, roll turnover and margin liquidity.

Position sizing needs forecast calibration, volatility estimates, contract granularity and covariance. Micro contracts may help granularity but differ in liquidity and fees. Multi-strategy allocations must account for correlated signals on the same underlying exposure. FX spot requires financing/rollover conventions, currency cash books and dealer/venue distinctions.

COT is delayed positioning information: Tuesday observations are generally released Friday, with holiday changes. It must enter features at release availability, not observation date. [CFTC calendar](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm).

Acceptance: rolls create the correct old/new contract events; negative price fixtures work; no delivery risk slips through a calendar; turnover and collateral reconcile; actual achievable sizing is tested under account margin and stress.

## Coverage checklist

- Time-series trend and forecast calibration
- Cross-sectional futures momentum
- Commodity rates equity FX carry
- Curve spreads and relative value
- Seasonality and COT positioning
- Contract chains and continuous-series policies
- Roll execution and delivery prevention
- Volatility scaling and contract granularity
- Collateral interest and margin liquidity
- FX spot carry and currency accounting
- Multi-strategy ensembles and correlation

## Research sources

- [TREND](sources.md#trend)
- [CARRY](sources.md#carry)
- [COT](sources.md#cot)
- [CME-EXPIRY](sources.md#cme-expiry)
- [CME-CASH](sources.md#cme-cash)

[Knowledge base index](README.md)
