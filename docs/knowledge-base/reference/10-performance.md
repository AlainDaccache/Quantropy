# Performance, execution and financial records

Holdings, cash, commitments, orders and fills are different records. An order expresses intent; a fill creates a trade; settlement transfers the contractual assets and cash. Corporate actions and derivative exercise can generate positions without a normal market order. Reconcile economic events to both broker records and an internal ledger.

For a single asset with price P_0, final price P_1 and cash distribution D paid at period end, holding-period return=(P_1-P_0+D)/P_0 before costs. Earlier distributions require a reinvestment or cash treatment convention. Total-return series, price series and account equity are therefore distinct objects.

Time-weighted return removes the effect of external cash flows by linking subperiod returns: TWR=product(1+r_j)-1. Money-weighted return solves a dated cash-flow IRR and reflects investor contribution timing. Modified Dietz approximates a flow-adjusted return with weighted flows; it is not universally identical to either exact TWR or IRR.

**Example.** Start with 100; earn 10%, then receive an external deposit of 100; earn 10% again. Ending value is 231. TWR=21%. The raw gain (231-100)/100=131% mistakenly treats the deposit as investment profit. The investor's IRR needs the deposit date and terminal withdrawal convention.

Attribution explains performance under a selected model: allocation/selection, security contributions, factor exposures or implementation costs. Contributions must reconcile to the selected return definition. Arithmetic attribution over one period and compounded multi-period returns require linking rules; residuals should be visible rather than silently allocated.

Execution quality compares fills with a specified decision, arrival, quoted or volume benchmark. Implementation shortfall includes price movement, fees and opportunity cost of unfilled intent under stated rules. A limit order offers price control but may remain unfilled; a market order offers execution priority without a guaranteed price. Queue position and market impact matter, particularly with bar data.

Trade-date and settlement-date views answer different questions. Counterparty exposure can exist before final settlement. Cash availability, collateral and buying power are not identical. Duplicate event processing, partial fills, cancels, reconnects and corrections require idempotent event identifiers and explicit state transitions.

Tax returns need local rules, year, account type, lot identity and currency basis. Do not infer legal tax liability from portfolio P&L. This foundational page explains reconciliation and returns; detailed execution venue rules, tax rules and compliant performance presentations remain dated specialist specifications.

## Evidence and depth

Source map: [CFA-RETURNS](../sources.md#cfa-returns), [GIPS](../sources.md#gips), [PFMI](../sources.md#pfmi), [IBKR-ORDER](../sources.md#ibkr-order). These are supporting references, not certification of every equation. This article is an introductory reference; specialized methods listed in the coverage register still require full specifications and independent review.

[Reference index](README.md)
