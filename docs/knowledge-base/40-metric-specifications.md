# Metrics and ratios need exact contracts

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Every metric must have an economic definition, formula version, statement mapping, period, units, currency, availability policy, adjustments and invalid-input behavior. A company can report an identically named non-GAAP metric using a different definition. Preserve reported and normalized metrics separately.

Examples of proposed core conventions follow. These are transparent definitions to review and fixture, not a claim that all sector/accounting variants have been verified.

| Metric | Proposed basic definition | Essential qualification |
|---|---|---|
| Gross margin | Gross profit / revenue | Service/financial firms may report incompatible cost categories |
| EBIT margin | EBIT / revenue | Define operating/nonoperating treatment |
| Net margin | Net income attributable to chosen owners / revenue | Consolidated versus parent scope |
| ROA | Chosen income / average assets | Income and average-period definition required |
| ROE | Common-owner income / average common equity | Negative equity can make interpretation meaningless |
| ROIC | NOPAT / average invested capital | Tax, goodwill, excess cash, leases and acquisitions matter |
| Current ratio | Current assets / current liabilities | Business model and classification matter |
| Cash conversion cycle | DSO + DIO - DPO | Align days, sales/COGS and average balances |
| Interest coverage | Chosen earnings measure / interest expense | EBIT versus EBITDA versus cash variants |
| Net debt | Defined debt minus eligible cash | Include leases? Exclude restricted cash? |
| Enterprise value | Equity market value + defined senior/noncommon claims - eligible nonoperating cash | Dilution, minority interests, pensions and leases require a bridge |
| FCFF | NOPAT + noncash charges - reinvestment in operations | Acquisitions and recurring investment cannot disappear |
| FCFE | Equity cash flow after operating investment and net borrowing | Financing assumptions and owner scope |
| FCF conversion | Defined FCF / chosen earnings denominator | Negative denominators and period alignment |
| Accrual measure | Chosen earnings-minus-cash measure / defined asset scale | Multiple published constructions exist |

The method inventory specifies named profitability, liquidity, solvency, efficiency, valuation, forensic and sector metrics. Add bank loan/deposit and credit-quality measures; insurer underwriting/reserve measures; REIT property/FFO measures; SaaS revenue-retention/unit economics; commodity production/reserve measures. Definitions differ even within a sector.

Implementation gate: build independently reviewed filing-derived examples, show reported-to-normalized bridges, prohibit silent division by zero, record missing/unsuitable outcomes, and test fiscal-period/availability alignment. Exact Altman/Beneish formula variants still need full-text review. A large metric registry without those contracts would repeat the original project's weakness.

## Coverage checklist

- Metric definition formula version and applicability
- Statement mapping period currency and availability
- Reported normalized non-GAAP bridges
- Profitability liquidity leverage efficiency ratios
- Cash conversion and enterprise equity bridges
- Forensic scores and accrual variants
- Bank insurance REIT SaaS commodity metric profiles
- Invalid denominator and independent filing fixtures

## Research sources

- [SEC-STATEMENTS](sources.md#sec-statements)
- [SEC-XBRL](sources.md#sec-xbrl)
- [PIOTROSKI](sources.md#piotroski)
- [ALTMAN](sources.md#altman)
- [BENEISH](sources.md#beneish)
- [IFRS](sources.md#ifrs)

[Knowledge base index](README.md)
