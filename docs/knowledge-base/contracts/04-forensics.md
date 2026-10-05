# Quality and distress screens

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [03-metrics](03-metrics.md).

## Purpose and boundaries

Screens prioritize investigation. They do not certify solvency, manipulation, fraud or future returns. Use matched original definitions, population, statement vintages and observation dates. Do not turn missing values into favorable points.

**Altman original public-manufacturing Z:** 1.2X1+1.4X2+3.3X3+0.6X4+X5, with X1=working capital/assets, X2=retained earnings/assets, X3=EBIT/assets, X4=market value equity/book total liabilities, X5=sales/assets. Ratios are decimals. Private-firm and non-manufacturing versions change coefficients and equity definitions; they require separate variant contracts. Original-paper full coefficient verification remains pending; this equation is a conventional draft, not a verified modern bankruptcy classifier. Example X=(.2,.3,.1,1,1.5) yields 3.09. Historical thresholds are not portable legal conclusions.

**Beneish eight-variable draft:** M=-4.84+.92DSRI+.528GMI+.404AQI+.892SGI+.115DEPI-.172SGAI+4.679TATA-.327LVGI. DSRI=(receivables/sales)_t/(receivables/sales)_(t-1); GMI=prior gross margin/current gross margin; SGI=current/prior sales; SGAI=(SG&A/sales)_t/(SG&A/sales)_(t-1); LVGI=((current liabilities+long-term debt)/assets)_t divided by prior. AQI compares [1-(current assets+net PP&E)/assets] across years. DEPI compares [depreciation/(depreciation+net PP&E)] prior/current. A common cash-flow TATA proxy is (income from continuing operations-CFO)/assets; original accrual construction and filing mapping require verification. Named proxy outputs must not be called exact original replication. With all seven indices 1 and TATA 0, M=-2.48. Cutoffs differ by study and loss preference; specify the chosen version and source. A probit score is not a contemporary calibrated fraud probability without calibration evidence.

**Piotroski nine tests:** positive ROA; positive CFO; improved ROA; CFO exceeding earnings under matched scaling; decreased leverage; improved current ratio; no common-equity issuance; improved gross margin; improved asset turnover. Each true test gives one point. The original study's scaling/timing and issuance definitions must be followed for exact replication; split-adjusted share growth alone is not a complete equity-issuance measure. A fixture with all tests true gives 9; one missing test produces an incomplete score with an explicit range, not a silently imputed 8 or 9.

## Required investigation

Review revenue recognition, capitalized costs, provisions, related parties, cash conversion, dilution, auditor and management disclosures. Structural negative working capital, asset-light models, buybacks and financial institutions can defeat generic ratio interpretations. Compare screens to notes and economic scenarios; report evidence and alternative explanations. Source-level restrictions on the original papers remain tracked, despite public summaries.

## Evidence boundary

Supporting source map: [ALTMAN](../sources.md#altman), [BENEISH](../sources.md#beneish), [PIOTROSKI](../sources.md#piotroski), [BENEISH-TUTORIAL](../sources.md#beneish-tutorial). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
