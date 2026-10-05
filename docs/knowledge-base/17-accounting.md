# Accounting, performance, taxes and reporting

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

The economic ledger is the authoritative record of holdings, cash and obligations. Strategy targets are intentions, not holdings. Record trades, fees, deposits/withdrawals, dividends, interest, FX conversions, corporate actions, settlement and tax adjustments as versioned auditable events. Retain currency-level cash and both instrument and reporting-currency P&L. Futures variation margin must not be double-counted as both settled cash and unchanged unrealized P&L.

Reconcile internal positions/cash with broker executions and independent statements; explain breaks rather than forcing equality through unexplained adjustments. Handle cancellations/corrections, settlement receivables/payables and manual transactions. Imports need duplicate detection and reversible correction paths. [IBKR statements](https://www.interactivebrokers.com/docs/web-api/api-reference/get-statement).

Performance reporting should separately show gross/net returns, costs, income, FX, benchmark and attribution. Time-weighted return isolates investment performance from external flows; money-weighted return reflects the investor's cash-flow experience. Neither should be selected merely because it looks better. IRR may have multiple or nonexistent roots. State valuation and flow-timing conventions. GIPS is a useful calculation reference without implying compliance. [GIPS handbook](https://www.gipsstandards.org/standards/gips-standards-for-asset-owners/gips-standards-handbook-for-asset-owners/).

Tax is country/year/account-specific. For a Canadian profile, assess ACB and foreign-currency conversion, superficial-loss rules across relevant accounts/relationships, distributions/return of capital, withholding and registered-account distinctions. Investment versus business income classification and derivatives can require expert review. Do not freeze an assumed capital-gains rate into strategy code. [CRA guide](https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/t4037/capital-gains.html).

Acceptance: deposits change cash/wealth without becoming alpha; a complete round trip reconciles costs/P&L; FX attribution sums; tax adjustments retain source and review; statement discrepancies remain visible. Reports export evidence and assumptions for an accountant.

## Coverage checklist

- Economic event ledger and currency cash books
- Realized unrealized income and fee accounting
- Futures variation margin and settlement
- Corporate action and transaction corrections
- Broker statement import and reconciliation
- TWR MWR benchmark and attribution
- Tax lots ACB and foreign FX basis
- Superficial losses and cross-account review
- Registered taxable and withholding treatment
- Versioned jurisdiction and tax-year rules
- Accountant exports and audit trail

## Research sources

- [IBKR-FLEX](sources.md#ibkr-flex)
- [GIPS](sources.md#gips)
- [CRA](sources.md#cra)
- [CME-CASH](sources.md#cme-cash)

[Knowledge base index](README.md)
