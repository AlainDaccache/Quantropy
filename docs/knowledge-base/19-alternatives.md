# Funds, property, crypto and less standard assets

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Retail assets outside individual listed securities need their own economics. ETF/mutual-fund analysis should cover fees, tracking difference, index methodology, turnover, distributions, securities lending, replication, domicile and look-through holdings. Leveraged/inverse products need daily-reset path analysis, not a fixed multiple assumption over arbitrary holding periods. Closed-end funds add discount/premium and leverage. REITs differ from direct property.

Property modeling includes purchase/sale costs, rent, vacancy, maintenance/capex, insurance/tax, debt, refinancing and sale assumptions. Show levered and unlevered cash flows, DSCR, cap rate, IRR and liquidity. Appraisals and smooth historical valuations understate uncertainty and cannot be treated like executable daily prices.

Private equity, private credit, crowdfunding and venture need commitment/capital-call/distribution schedules, fees, waterfalls, lockups, dilution, recovery and scenario valuation. IRR comparisons can be misleading across cash-flow timing; add multiples and public-market-equivalent approaches only after method review. Structured products require payoff decomposition, issuer credit, barriers, callability and realistic secondary-market liquidity.

Crypto analysis needs custody/keys, venue solvency, token supply/unlocks, staking economics, smart-contract and oracle risk, stablecoin backing, protocol dependencies, funding/liquidations and chain fees. A high yield may be compensation for substantial loss risk or dilution. On-chain availability and exchange outages complicate backtesting. Derivative leverage and liquidation mechanics are venue-specific.

Acceptance: each product has explicit accessible valuation/exit assumptions and reliable source terms; no synthetic liquidity is introduced to improve backtests. Many capabilities should begin as scenario analysis/imports rather than automated execution. FINRA provides an introductory map of [alternative and emerging products](https://www.finra.org/investors/investing/investment-products/alternative-and-emerging-products); specialized quantitative and legal specifications remain research tasks.

## Coverage checklist

- Fund fees methodology and tracking
- Fund holdings look-through
- Leveraged inverse daily-reset products
- Closed-end fund discounts and leverage
- Property operating and financing models
- Private capital calls fees and waterfalls
- Private credit and recovery analysis
- Structured note payoff and issuer risk
- Crypto custody supply and token economics
- Staking DeFi smart-contract and oracle risks
- Crypto funding liquidation and venue models
- Illiquid valuation and exit scenarios

## Research sources

- [ALTERNATIVES](sources.md#alternatives)

[Knowledge base index](README.md)
