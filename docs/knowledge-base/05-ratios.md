# Ratios, quality and forensic screening

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

A ratio needs a precise definition, measurement period and denominator policy. Support margins, ROIC/ROE/ROA, liquidity, leverage, debt service, coverage, turnover, cash conversion, dilution, payout and valuation multiples. Average versus ending balance, gross versus net debt, operating versus total earnings and treatment of leases can change the answer materially. Return unavailable or not meaningful for unsuitable denominators rather than a fake extreme rank.

Altman is a family of distress models, not one universally applicable bankruptcy probability. Public manufacturing, private-firm and other adaptations cannot share coefficients indiscriminately. Beneish screens accounting patterns associated with manipulation; it is neither proof of fraud nor a generic quality score. Their exact variant, coefficients, cutoff, applicability and handling of missing inputs must be versioned from the full original specification before implementation. Full-text formula verification remains open here. [Altman](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1540-6261.1968.tb00843.x), [Beneish](https://rpc.cfainstitute.org/research/financial-analysts-journal/1999/the-detection-of-earnings-manipulation).

Piotroski's original nine signals cover positive ROA/CFO, improved ROA, cash flow exceeding accrual earnings, lower leverage, better liquidity, no common-equity issuance, better gross margin and better asset turnover. The sum ranges from zero to nine; the original research focused on high book-to-market firms. Preserve the original scaling conventions and issuance definition rather than substituting net share-count changes. [Original paper](https://www.chicagobooth.edu/~/media/FE874EE65F624AAEBD0166B1974FD74D).

Add accruals, earnings persistence, cash backing, balance-sheet resilience and sector peer comparisons as independently specified measures. Display each component and its evidence; a composite score should never hide missing inputs. Historical screening must use a point-in-time universe and available filings.

Acceptance: independent hand-worked company examples match; misleading sector applications are blocked or labeled; results show variants and missing-input policies. A screen informs investigation. Trading it requires a separate strategy and validation record.

## Coverage checklist

- Profitability return and margin ratios
- Liquidity leverage coverage ratios
- Working capital turnover efficiency
- Dilution payout and cash quality
- Valuation multiples and peer ranks
- Altman variant-aware distress screens
- Beneish variant-aware manipulation screens
- Piotroski nine-component score
- Accrual and earnings-quality measures
- Sector applicability and missing-input policies

## Research sources

- [ALTMAN](sources.md#altman)
- [BENEISH](sources.md#beneish)
- [PIOTROSKI](sources.md#piotroski)

[Knowledge base index](README.md)
