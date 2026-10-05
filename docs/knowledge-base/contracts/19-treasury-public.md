# Corporate treasury, financing and public debt scenarios

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [10-curves-credit](10-curves-credit.md); [08-valuation](08-valuation.md).

## Cash and financing mechanics

Use a dated currency-specific cash ladder: opening unrestricted cash+collections+available draws-payment obligations=closing cash. Separate restricted cash and committed/conditional facilities. Stress timing, customer default, margin calls and facility withdrawal. Liquidity headroom is available cash/funding less stressed obligations under named availability assumptions.

Working-capital finance models receivables/payables/inventory and contractual payment periods. Factoring and guarantees require recourse and legal-risk allocation; collateral borrowing does not necessarily remove the asset/default exposure. Debt covenants use contract-defined metrics, cure periods and cross-default terms. Project-finance waterfalls pay prioritized operating expense, reserves, senior debt, junior claims and distributions with lock-up tests.

Example cash 20+collections 30-operating payments 35-debt service 10=5. A collection delay of 12 gives -7 before facility draws. An available facility of 10 can cover it only if contractual conditions and currency access remain valid. DSCR=CFADS/debt service uses the actual covenant cash-flow definition; EBIT/interest is not a substitute.

## Institutions and public debt

Bank liquidity coverage ratio compares eligible high-quality liquid assets with stressed 30-day net cash outflows under specific rules. Asset eligibility, haircuts, flow caps and implementation dates matter; this page does not state a universal legal threshold. NSFR considers stable funding on a different horizon and basis. Legal settlement finality, DvP/PvP, central clearing, custody and collateral closeout are contract/system properties.

For public debt use the [nominal debt/GDP identity](../reference/03-economics.md). Add foreign-currency valuation, primary-budget scenarios, maturity/refinancing, contingent liabilities and stock-flow adjustments. A government that issues domestic currency differs economically from a municipality or household; inflation, political and institutional constraints still matter. Public project appraisal compares incremental social benefits/costs under explicit discount and distributional assumptions, not just private investor cash flows.

Forward FX hedges reduce exchange uncertainty for a stated amount/date but can create mark-to-market collateral. Rates/commodity hedges similarly need exposure and basis-risk scenarios. Sustainability, development finance, Islamic contract structures and cross-border commercial rules need dedicated legal/economic profiles; generic funding equations do not specify them.

## Evidence boundary

Supporting source map: [PFMI](../sources.md#pfmi), [IMF-DEBT](../sources.md#imf-debt), [BASEL-LCR](../sources.md#basel-lcr), [OECD-MSME](../sources.md#oecd-msme). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
