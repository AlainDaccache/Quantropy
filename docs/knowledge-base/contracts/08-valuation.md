# Cash-flow valuation, residual income and transactions

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [03-metrics](03-metrics.md); [02-numerics](02-numerics.md).

## Cash-flow contracts

FCFF uses the [canonical gross-investment bridge](../reference/04-valuation.md). FCFE=common net income+D&A-capex-change operating NWC+net debt issuance under a conventional non-financial accounting boundary, adjusting preferred claims and non-operating items as required. Discount FCFF using a compatible capital-cost policy and FCFE using cost of equity. Dividend discount uses actual expected distributions, justified against sustainable distribution capacity.

Terminal value at forecast date T is CF_(T+1)/(k-g), with k>g, consistent currencies and reinvestment. In a simplified steady-state firm, growth reinvestment can be NOPAT*g/ROIC; assuming perpetual growth with zero investment generally violates the model economics. Terminal value is discounted once from T. A debt/equity bridge separately reconciles cash, minority claims, pensions, options and non-operating assets.

Residual-income equity value is B0+sum[(NI_t-k_e B_(t-1))/(1+k_e)^t]+continuing excess-income value under clean-surplus accounting and compatible terminal treatment. Example book equity 100, expected earnings 12 next year, cost of equity 10%, and thereafter no excess returns give value 100+2/1.1=101.818182. Dirty-surplus items and share transactions require adjustments.

APV=unlevered operating value+PV(financing benefits)-PV(financing costs), with debt-policy-specific tax-shield discounting. Reverse DCF solves a chosen driver such as growth for an observed price, holding other assumptions fixed; multiple driver combinations can explain the same price. NAV estimates realizable asset values less liabilities; liquidation adds timing, seniority and transaction costs.

## M&A and serial acquirers

Combined incremental value equals stand-alone values plus after-tax synergy less integration and transaction costs. Allocation of that benefit between buyer and seller depends on price and financing. Serial-acquirer forecasts need organic growth, acquired revenue, purchase consideration, earnouts, debt, dilution, integration costs and return on all deployed capital. Forecasting acquisition-driven growth without cash acquisition expenditure inflates FCF. Goodwill amortization policy does not replace the economic acquisition cost.

Example: buyer standalone 500, target standalone 100, PV synergy 20, integration PV 5 and purchase price 115 create buyer incremental value 100+20-5-115=0 before other financing effects. EPS accretion alone does not show value creation. For a sum of parts, each segment value uses the correct claim basis, then shared costs, debt and cross-holdings are reconciled once.

Scenario/real-option methods need risk measures, decision timing and exercise rules. Probability-weighted milestone value is not automatically risk-neutral option valuation. Distress scenarios must allocate outcomes by priority rather than letting common equity become an unqualified negative liquidation claim.

## Evidence boundary

Supporting source map: [DAMODARAN-CASH](../sources.md#damodaran-cash), [DAMODARAN-SECTORS](../sources.md#damodaran-sectors), [BANK-VALUATION](../sources.md#bank-valuation). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
