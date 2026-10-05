# Private markets, real assets and payoff waterfalls

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [08-valuation](08-valuation.md); [10-curves-credit](10-curves-credit.md).

## Private cash-flow measures

Track contributions, distributions, fees and NAV by date and currency. Paid-in capital is the agreed denominator scope; DPI=distributions/paid-in, RVPI=NAV/paid-in and TVPI=(distributions+NAV)/paid-in. Example paid-in 100, distributions 40 and NAV 90 give DPI .4, RVPI .9, TVPI 1.3. NAV is an estimate, not an immediately realizable sale price. IRR additionally depends on dates and can be manipulated by temporary funding/timing without the same change in total profit.

For Kaplan-Schoar-style PME under a specified total-return index I, scale each cash flow to terminal date T: PME=[sum distributions_t I_T/I_t+NAV_T]/[sum contributions_t I_T/I_t]. The benchmark, currency, fee scope and NAV date must match. Other PME/direct-alpha methods have different definitions; don't label every benchmark comparison PME without a variant.

## Waterfall baseline

A simple whole-fund waterfall: return contributed capital; pay a defined preferred return; apply a stated catch-up rule if any; split remaining profits by carry rate. Specify compounding/timing, fees, recycled capital, escrow/clawback and deal versus whole-fund treatment. Example contribution 100 and distribution 150 with no preferred return/catch-up and 20% carry: return capital 100, divide profit 50 into GP carry 10 and LP profit 40. Adding a preferred return changes the calculation; a universal “20% of gain” formula is incomplete.

Property uses rent/occupancy, NOI, maintenance/leasing capex and financing. Infrastructure adds construction, concession/tariff, demand and counterparty rules. Resources add production/depletion and closure liabilities. Commodity futures are a sequence of contracts and collateral cash flows, requiring roll, delivery and price-limit handling.

Digital claims require identification of enforceable rights, redemption, custody/key control, governance, settlement and counterparty risk. Token yield can come from fees, issuance/dilution, lending risk or contingent protocol payments. Stable price history is not proof of backing or unconditional redemption.

Stale appraisals and smoothed NAV distort measured volatility/correlation. Adjusting for smoothing needs an estimation model and should not invent liquid transaction prices. Collectibles, carbon credits, timber, intellectual property and litigation claims need their own economic-contract profiles. Illiquidity and access constraints must be treated as properties of the vehicle/claim, not inferred from a broad asset-class label.

## Evidence boundary

Supporting source map: [CAIA](../sources.md#caia), [CFA-III-PRIVATE](../sources.md#cfa-iii-private), [NAREIT-FFO](../sources.md#nareit-ffo). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
