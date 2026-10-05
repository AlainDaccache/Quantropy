# Instruments, markets and economic contracts

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

“All asset classes” must mean explicit contracts, cash flows and lifecycle support, not one generic price column. Distinguish the underlying economic exposure from the legal instrument used to obtain it. A gold ETF, gold futures contract, physical gold and mining company are different investments.

Use stable internal instrument IDs with time-valid symbol/identifier mappings, exchange, currency, tick size, lot size, multiplier, calendar and lifecycle. An issuer can have several securities and listings. Record fund share classes, distributing versus accumulating treatment, derivative underlying relationships, and baskets. Broker contract IDs belong in adapters, not as the universal identity.

Cash and deposits need interest, withdrawal and counterparty terms. Equities need share classes and corporate actions. Funds need fees, distributions, holdings and tracking behavior. Bonds need schedules, coupon/day-count conventions, accrued interest, settlement and embedded options. Futures need expiry, first-notice/delivery rules, multiplier and variation margin. Options need strike, style, expiry/last-trade/exercise timestamps, settlement and deliverables. FX needs base/quote orientation, account currencies, financing and rollover. Crypto needs venue, custody, network and token mechanics. Property and private assets need irregular cash flows and valuation uncertainty.

Analysis, historical simulation and live execution are separate readiness levels for each instrument family. Swaps, exotic options, structured notes and private investments may be worth analyzing while unsuitable or inaccessible for retail execution. An instrument must have exact exchange or issuer specifications before live support is enabled.

Acceptance: changing a ticker does not create or destroy holdings; splitting shares preserves economic value before costs; one futures tick produces the correct cash P&L; an option adjustment changes its deliverable correctly. Unsupported instrument features fail visibly.

## Coverage checklist

- Security master and identifier history
- Market calendars and time zones
- Cash and deposits
- Equities and depositary receipts
- ETFs mutual funds closed-end funds
- Government corporate municipal bonds
- Listed futures and commodity contracts
- Equity index FX futures options
- Spot FX and financing
- Crypto assets and custody
- Property and private assets
- Structured products and OTC analysis

## Research sources

- [LEAN](sources.md#lean)
- [CME-EXPIRY](sources.md#cme-expiry)
- [OIC-EXERCISE](sources.md#oic-exercise)
- [FINRA-BONDS](sources.md#finra-bonds)
- [ALTERNATIVES](sources.md#alternatives)

[Knowledge base index](README.md)
