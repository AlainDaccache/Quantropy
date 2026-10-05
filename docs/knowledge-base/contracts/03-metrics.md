# Financial metrics: exact baseline conventions

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [01-statistics](01-statistics.md).

## Inputs and common policy

Flows cover a stated interval; balances are dated stocks. Average balances mean (opening+closing)/2 in this baseline, with a time-weighted alternative needed for material intra-period transactions. Amounts share currency, consolidation and accounting scope. Undefined ratios return an explicit reason, not zero. Negative denominators are retained only when economically interpretable.

| Family | Baseline definitions |
|---|---|
| Margins | Gross profit/revenue; EBIT/revenue; explicitly normalized EBITDA/revenue; owner net income/revenue |
| Returns | ROA=chosen net income/average assets; ROE=common earnings/average common equity; ROIC=normalized NOPAT/average operating invested capital; ROCE=EBIT/average defined capital employed |
| Liquidity | Current=current assets/current liabilities; quick=(cash+eligible short-term investments+net trade receivables)/current liabilities; cash=(cash+eligible liquid investments)/current liabilities |
| Leverage | Debt/equity and debt/assets use defined debt; net debt=debt-eligible cash; net-debt/EBITDA uses matched lease/debt/earnings scope |
| Coverage | EBIT/interest; cash-interest coverage=defined cash available for interest/cash interest; DSCR=contractual cash available for debt service/(interest+required principal) |
| Turnover | Revenue/average assets; revenue/average net fixed assets; COGS/average inventory; credit sales/average receivables |
| Days | DSO=days*average receivables/credit sales; DIO=days*average inventory/COGS; DPO=days*average payables/purchases; CCC=DSO+DIO-DPO |
| Cash quality | CFO/net income; defined FCF/earnings; (net income-CFO)/average assets as a named cash-flow accrual screen |
| Growth | Current/prior-1 for positive comparable bases; report absolute changes separately when bases are zero or negative |
| Reinvestment | Gross capex/revenue; (capex-D&A+change operating NWC)/NOPAT, with acquisitions separately disclosed |
| Payout | Common dividends/common income; defined equity FCF/common cash distributions; net repurchases plus dividends divided by beginning equity market value |
| Dilution | Split-adjusted ending common shares/beginning shares-1; separate basic outstanding and diluted weighted-average shares |
| Multiples | Price/compatible EPS; common market cap/common book equity; equity value/sales; defined EV/sales, EBIT or EBITDA |
| Yields | Common earnings/common market cap; equity FCF/common market cap. Firm FCF requires an enterprise denominator |

The balance-sheet accrual screen [(change current assets-change cash)-(change current liabilities-change short-term debt)-D&A]/average assets is a specific approximation; acquisitions, currency and reclassifications can distort it. PEG=(P/E)/(EPS growth in percentage points) is a heuristic with a declared forecast horizon, not an intrinsic-value equation. Sustainable growth approximately equals ROE*retention under a stable equity model, not with arbitrary financing and payout changes.

## Worked case and controls

Sales 365, average receivables 30, COGS 200, average inventory 40, purchases 220 and average payables 22 imply DSO 30, DIO 73, DPO 36.5 and CCC 66.5 days using a 365-day period. Purchases may be approximated by COGS+change inventory only under a consistent manufacturing/trade accounting boundary. If credit sales are unavailable, total sales is an explicitly labeled approximation.

DuPont's three-factor identity is net margin*(sales/average assets)*(average assets/average equity)=net income/average equity when all scopes and periods match. The identity cancels algebraically; it does not show causation. Store original statement facts, adjustments and final ratios separately. Industry and covenant variants must use named profiles instead of silently replacing this baseline.

## Evidence boundary

Supporting source map: [SEC-STATEMENTS](../sources.md#sec-statements), [IFRS-CONCEPT](../sources.md#ifrs-concept). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
