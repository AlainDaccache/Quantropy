# Options, volatility and derivative modeling

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Separate payoff understanding, theoretical pricing, market calibration, hedging and strategy P&L. A model price does not reveal an edge without executable prices and uncertainty. Support equity/index, futures and FX options with the right underlying, dividends, rates, settlement, multiplier and exercise conventions.

Start with payoff diagrams and European reference models; extend to trees, finite differences and Monte Carlo where appropriate. American exercise, discrete dividends and adjusted deliverables need explicit handling. Validate delta, gamma, vega, theta and rho units and bump conventions. Greeks are local sensitivities, not complete worst-case risk. QuantLib is a strong integration candidate, subject to convention and numerical review. [QuantLib](https://www.quantlib.org/).

Build implied volatility from qualified quotes with time-to-expiry, discount/forward curves and bid/ask uncertainty. Filter crossed, stale or implausible quotes rather than filling holes with fabricated observations. Represent strike/log-moneyness/delta and tenor consistently. Interpolate total variance carefully; test calendar and butterfly no-arbitrage constraints. SVI/SSVI, SABR, local volatility and stochastic volatility are advanced extensions with different assumptions. The SVI paper provides a research entry point, not an already validated implementation. [Gatheral and Jacquier](https://arxiv.org/abs/1204.0646).

Include realized volatility, realized/implied comparisons, volatility risk premium hypotheses, skew/term structure, event risk, dispersion and hedging P&L. Model assignment, expiry, pin risk, liquidation and multi-leg execution. Early assignment can occur; a protective spread leg may not automatically neutralize operational obligations. [OIC assignment](https://www.optionseducation.org/referencelibrary/faq/options-assignment).

Acceptance: parity and bounds for the applicable contract; analytic/numerical convergence; finite-difference Greeks; arbitrage diagnostics; dividend/assignment fixtures; actual chain histories and spread costs. Accurate historical options work likely needs a data vendor beyond broker history.

## Coverage checklist

- Payoff diagrams and strategy decomposition
- European equity futures FX pricing
- American exercise and dividends
- Trees finite differences Monte Carlo
- Greeks and finite-difference validation
- Implied volatility solver and quote filters
- Volatility smiles and term structures
- Arbitrage-aware surface calibration
- SVI SSVI SABR models
- Local and stochastic volatility
- Realized volatility and risk premia
- Dispersion event and skew analysis
- Dynamic hedging and P&L attribution
- Assignment expiry pin and deliverable risks
- Multi-leg liquidity margin and execution

## Research sources

- [QUANTLIB](sources.md#quantlib)
- [SVI](sources.md#svi)
- [OIC-EXERCISE](sources.md#oic-exercise)
- [OIC-ASSIGNMENT](sources.md#oic-assignment)
- [IBKR-HISTORY](sources.md#ibkr-history)

[Knowledge base index](README.md)
