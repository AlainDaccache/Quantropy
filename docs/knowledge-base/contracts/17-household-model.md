# Household lifecycle and retirement simulation

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [01-statistics](01-statistics.md); [10-curves-credit](10-curves-credit.md).

## State and transitions

Maintain dated balances by account, lots/debt, salary, pensions, essential/discretionary spending, family survival, inflation and tax jurisdiction. For end-period cash flows, B_t=B_(t-1)(1+r_t)+contributions_t-withdrawals_t-fees_t-tax_t under a defined ordering. For beginning-period contributions use (B_(t-1)+C_t)(1+r_t)-W_t instead. Taxes on taxable gains, pension receipts and withdrawals need dated local modules.

Income projection I_t=I0 product(1+g_I,s) and real-linked spending E_t=E0 product(1+inflation_s) define different processes. Correlate employment loss, income and investment shocks where justified. A refinance compares discounted remaining/new loan flows, transaction costs, reset risk and liquidity, not only monthly payment. Coast target today is future required capital/(1+assumed return)^years under a deterministic scenario; the assumption is not guaranteed.

## Policies

Fixed-real spending inflates an initial amount; fixed-percentage spending uses a fraction of current assets and accepts variable consumption. Guardrails state the exact triggers and increase/decrease rules. Funded-ratio policies compare asset value to a defined liability PV and select spending/risk rules. Floor/upside policies fund essential needs with an explicitly modeled instrument set. Buckets are accounting/behavioral organization unless their trading rules produce a different allocation path.

Success means meeting defined essential/discretionary obligations over the chosen lifetime, optionally preserving legacy. Report probability and severity of shortfalls, real consumption distributions, time to ruin and remaining capital; no one terminal-success percentage captures all objectives. Mortality, partner joint survival and exceptional health/care costs require separate joint scenarios. Historical windows, joint block bootstrap and regime models have distinct assumptions and cannot be pooled as if they were equivalent evidence.

## Worked and adversarial cases

Start 100, contribute 10 at year end, return 5%: end value 115. Begin-period contribution instead ends 115.5. At fixed real spending 10 with 2% inflation, second-year spending is 10.2. Zero return with 10 end-year withdrawals exhausts 100 in ten years, absent other flows/costs. A simulator must detect a mid-period essential shortfall rather than allowing negative balances to earn investment returns.

FIRE, Lean/Fat, Coast and partial-work scenarios set spending, work and contribution policies. They do not require separate investment mathematics. Pension timing, annuities, account withdrawal order, estate and cross-border cases need contract/rule profiles and suitability considerations.

## Evidence boundary

Supporting source map: [RETIREMENT](../sources.md#retirement), [CFP](../sources.md#cfp), [SOA-SURVIVAL](../sources.md#soa-survival). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
