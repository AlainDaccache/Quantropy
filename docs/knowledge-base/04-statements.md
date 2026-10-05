# Financial statement analysis

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Understand the business before producing ratios. Balance sheets show resources and obligations at a date; income statements show accounting performance over a period; cash-flow statements explain cash changes; equity statements connect ownership movements. Their relationships and footnotes matter as much as headline values. Start with the SEC's [statement guide](https://www.sec.gov/about/reports-publications/beginners-guide-financial-statements).

Quantropy should ingest filings while preserving issuer facts, taxonomy, unit, fiscal period, reporting date, accession and context. Map normalized concepts without deleting original labels. Distinguish consolidated and segment values, annual and interim periods, reported and adjusted figures, and fiscal calendars. Handle restatements, discontinued operations, stock compensation, leases, pensions, deferred taxes, acquisitions and currency translation. GAAP and IFRS differences must be explicit rather than blended into an apparently comparable table.

Provide common-size statements, multi-year trends and bridges: revenue growth into price/volume/mix where disclosed; earnings into operating cash flow; capex and working capital into free cash flow; debt into interest burden; shares into dilution. Reconcile opening/closing cash and the accounting equation before trusting downstream analysis. Read MD&A and footnotes for obligations, concentration, accounting estimates and risks. [SEC MD&A guidance](https://www.sec.gov/about/divisions-offices/division-corporation-finance/financial-reporting-manual/frm-topic-9).

Analysis must adapt to business type. Banks, insurers, REITs, commodity producers and early-stage businesses need different measures. Negative equity or unusual working capital can make conventional ratios misleading. Present original evidence alongside adjustments with a reviewer-editable explanation.

Acceptance: a displayed value can be traced to a filing and context; annual/quarterly conversions avoid double-counting; a restatement changes a later view without rewriting what a historical investor knew; cash and balance-sheet reconciliation errors stop automatic scoring. Global coverage requires separately verified filing/accounting adapters.

## Coverage checklist

- Filing ingestion and XBRL contexts
- Normalized statements with original evidence
- Common-size and trend analysis
- Cash earnings reconciliation
- Working capital and cash conversion
- Segment and geographic analysis
- Accounting adjustments and restatements
- GAAP IFRS comparison
- Industry-specific statement analysis
- Footnotes MD&A and obligations

## Research sources

- [SEC-XBRL](sources.md#sec-xbrl)
- [SEC-STATEMENTS](sources.md#sec-statements)
- [SEC-MDA](sources.md#sec-mda)

[Knowledge base index](README.md)
