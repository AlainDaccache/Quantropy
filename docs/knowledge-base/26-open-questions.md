# Open research, decisions and explicit gaps

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

This first edition covers the principal domains and their connections. It is not an encyclopedia of every jurisdiction, security and model, and it does not mark existing Quantropy modules as validated. The capability register is a specification inventory; all rows begin as specified, with implementation evidence unassessed.

Decisions needed before sizing a build: intended first live instruments and horizons; owner trading restrictions; brokerage account types/permissions; data/license budget; local versus dedicated hosting; approximate capital and liquidity constraints; supported countries/account tax profiles; discretionary versus automated workflows; acceptable maintenance effort. These do not block the knowledge map but they change implementation priorities.

Research gates: verify full Altman/Beneish variants and fixtures; audit the original statistical definitions for advanced inference; derive and independently validate surface no-arbitrage constraints and rate/credit models; obtain actual historical option/futures and point-in-time global fundamental data samples; review Canadian and other jurisdiction tax/account rules for the relevant year; validate corporate-action/option adjustment sources; decide library licenses and fit; establish historical borrow/liquidity assumptions. Many advanced capabilities currently have a domain outline rather than a complete executable specification.

Operational gates: choose the IBKR API/version; prove account/contract permissions; define uncertain-submission recovery; test real statement reconciliation; establish disaster recovery and independent alerts. Paper trading alone cannot validate queue priority, market impact or stressed margin.

The initial laptop audit found important concrete defects and useful existing components, but did not manually inspect every finance-related file. The manifest includes archives, duplicates and some irrelevant candidates. Separate initial findings from later repository-by-repository reviews; no sweeping deletion follows from a static scan.

Maintain this page after each investigation. A gap must have an owner, decision/evidence needed and effect on readiness. “No stone left unturned” is best operationalized as explicit coverage, traceable unknowns and systematic expansion, not pretending there are no unknowns.

## Coverage checklist

- Owner constraints and priority decisions
- Historical data procurement sample tests
- Advanced model full-text specification review
- Jurisdiction and account rules verification
- IBKR API permission and recovery proof
- Full repository-by-repository code audit
- Unresolved gap ownership and readiness impact

## Research sources

- [ALTMAN](sources.md#altman)
- [BENEISH](sources.md#beneish)
- [SVI](sources.md#svi)
- [IBKR-HISTORY](sources.md#ibkr-history)
- [CRA](sources.md#cra)

[Knowledge base index](README.md)
