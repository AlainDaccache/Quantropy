# Market plumbing, financing and investor dependencies

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Model how obligations move after a trade. Distinguish order execution, allocation, clearing, settlement, custody, ownership record and cash availability. Central counterparties, depositories, settlement banks, brokers and custodians create dependencies beyond the strategy. Settlement finality and credit/liquidity risks belong in the market model. CPMI-IOSCO is a primary framework for understanding that infrastructure, not a requirement to build a clearing house. [Principles](https://www.bis.org/committees/cpmi/pfmi/overview).

Track trade/value dates, unsettled cash, receivables/payables, delivery-versus-payment assumptions, broker financing, interest accrual, collateral eligibility and margin transitions. Contract and jurisdiction rules are versioned; settlement calendars need both currencies/venues where appropriate. Moving funds between accounts has timing, FX and liquidity effects.

Securities lending and short selling require availability, locate/borrow assumptions, fees, recalls, buy-ins, dividend-in-lieu treatment and short-sale restrictions. Repurchase agreements and financing instruments can be useful analysis topics even when the retail implementation is via a broker product. The displayed margin requirement is a current constraint, not an assurance that requirements cannot change.

Microstructure analysis needs trade/quote distinction, spread, depth, auction behavior, fragmentation, tick/lot rules, market hours, halts and limit moves. An order-book reconstruction can estimate observable liquidity but not guarantee fills or reveal every hidden order. [CME methodology](https://www.cmegroup.com/education/articles-and-reports/understanding-the-cme-liquidity-tool-methodology). Execution benchmarks should distinguish arrival price, decision price, VWAP and opportunity cost.

Add investor-dependency scenarios: broker/custodian outage or failure, failed settlement, unavailable cash, market closure, emergency margin, borrow recall and incorrect corporate-action handling. Country-specific custody/protection arrangements need current official evidence before suggesting loss coverage. Maintain corporate-action elections, tender rights, rights issues, voting/proxy information and instrument eligibility as distinct workflows.

Acceptance: a purchase consumes funds according to the actual settlement/financing policy; unsettled cash is not double-counted; recalls/halts have explicit operational consequences; broker/custodian statements reconcile legal and economic records. These dependencies matter even to a buy-and-hold investor.

## Coverage checklist

- Trade clearing settlement custody distinctions
- Unsettled cash receivables and value dates
- Collateral financing interest and margin transitions
- Securities lending borrow recalls and buy-ins
- Repo and financing analysis
- Order book auctions halts and limit moves
- Arrival VWAP and opportunity-cost benchmarks
- Broker custody failure and protection research
- Corporate action elections rights and proxy workflows

## Research sources

- [PFMI](sources.md#pfmi)
- [CME-LIQUIDITY](sources.md#cme-liquidity)
- [IBKR-ORDER](sources.md#ibkr-order)
- [IBKR-FLEX](sources.md#ibkr-flex)

[Knowledge base index](README.md)
