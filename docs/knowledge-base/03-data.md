# Data, provenance and point-in-time truth

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

The most important data distinction is when something happened versus when it became knowable. Store event/effective time, publication/availability time and ingestion time; retain revisions. A statement ending in December may not be usable in December. Restated historical fundamentals can contaminate a backtest. Macro observations may later change. SEC API aggregates still need context and filing selection to support historical decisions. FRED real-time periods help recover vintages; a vintage date alone may not prove intraday availability. [SEC APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [FRED](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html).

Separate immutable raw captures, normalized domain tables and derived features. Record provider, endpoint/query, extraction time, content hash, license, transformation version, schema and quality checks. Snapshot each experiment's exact input manifest. Do not silently repair data: mark, explain and version corrections. Avoid copying confidential account exports into a public repository.

Data families: trades/quotes/bars and depth; instrument metadata/calendars; corporate actions and distributions; filings/fundamentals/estimates; option chains and historical surfaces; actual futures chains; rates/curves/credit; FX; macro releases/vintages; fund holdings; ownership/short interest/borrow; news/events; benchmark/factor returns; alternative data; household and broker records.

Budget and rights belong in the specification. Free data can support learning but may lack delisted securities, historical option chains, survivorship-free universes or redistribution rights. Broker connectivity is not a comprehensive historical database. Reference FX is different from an executable quote. [IBKR data](https://www.interactivebrokers.com/docs/general/market-data-subscriptions/introduction), [Bank of Canada](https://www.bankofcanada.ca/valet-api-how-to/).

Acceptance: an as-of query never returns a later release; appending future data cannot alter an earlier decision; missingness coverage is measured; units and quote currencies are validated; stale quotes block sensitive trading actions. Data access, provider costs and coverage remain procurement decisions, not assumed resources.

## Coverage checklist

- Immutable raw ingestion
- Bitemporal availability and revisions
- Price trades quotes order book
- Corporate actions and delistings
- Historical universes and membership
- Filings and fundamental vintages
- Historical option chains
- Individual futures contract histories
- Curves credit spreads and FX
- Macro vintages and releases
- Ownership borrow short interest
- News and alternative data
- Data licenses and cost budget
- Data quality monitoring
- Dataset manifests and reproducibility

## Research sources

- [SEC-XBRL](sources.md#sec-xbrl)
- [FRED](sources.md#fred)
- [IBKR-DATA](sources.md#ibkr-data)
- [IBKR-HISTORY](sources.md#ibkr-history)
- [BOC](sources.md#boc)
- [FRENCH](sources.md#french)

[Knowledge base index](README.md)
