# Provenance — where prior work feeds this project (internal note)

This is the *internal* record of what the current effort inherits from earlier
codebases. It exists so porting decisions stay auditable; nothing here is required
to understand `MASTER_SPEC.md` or the curriculum, which are self-contained.

## Sources

| Source | What it was | What we take |
|---|---|---|
| `legacy/matilda` (this repo, 2020–21) | Broad quant library: statements/ratios, CAPM/FF/Carhart, MPT/Black-Litterman, Black-Scholes, VaR, SEC/XBRL/FRED scrapers, Alpaca. Broad but uneven; import-time DB coupling; secrets were hardcoded (now scrubbed; **rotate the old Atlas/AlphaVantage/FRED credentials** — they remain in public git history). | Harvest formula-by-formula, only where used, each ported formula verified against a reference and tested first. Nothing imported wholesale. |
| `FinancialModelling/src/meridian` (sibling repo, 2026) | Clean systematic-futures framework: no-look-ahead event engine, venue Protocol (sim/live parity), trend/carry/xs-momentum/value sleeves, vol targeting, block bootstrap/deflated Sharpe/walk-forward, acceptance gates. | Design and code backbone for the backtest engine, venue seam, signal sleeves, and evaluation stack (spec milestones T1–M2). |
| `FinancialModelling/archive/v3_bearing_standard` | Fundamental valuation engine: identity-based DCF, **reverse DCF** with monotonicity guards, valuation archetypes (residual income, SOTP, serial acquirer), EDGAR/EDINET ingestion, point-in-time forecast backtesting. | Core of the valuation track (spec milestone M3). |
| `futures-quant` (sibling repo, spec-only) | No code; a rigorous research-governance spec: hypothesis registry, deflated Sharpe/PBO discipline, two-tier drawdown, continuous-contract (Panama) construction. | Methodology → the governance tooling and curriculum Module 8. |

## Porting rules

1. Nothing moves without a reference-value test (spec P2).
2. Port fixes defects rather than preserving them (e.g. the legacy TVM annuity-due
   mode and `r == g` division-by-zero were corrected on port — see `core/tvm.py`).
3. `legacy/` is read-only harvest material; it is never imported by `quantropy`.
