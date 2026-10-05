# Risk budgets, hierarchical allocation and tail objectives

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [06-allocation](06-allocation.md).

## Volatility risk budgets

For sigma_p=sqrt(w'Sigma w)>0, marginal risk m_i=(Sigma w)_i/sigma_p and component risk RC_i=w_i m_i. Euler homogeneity implies sum RC_i=sigma_p. Risk budgeting seeks RC_i=b_i sigma_p with budgets b_i≥0 and sum b=1, under stated long-only and covariance assumptions. Equal budgets create equal-risk contribution; inverse volatility is exact only in special dependence structures.

For two independent assets with volatilities .1 and .2, equal-risk weights (2/3,1/3) give equal variance terms and volatility .0942809. Equal-risk weights differ from minimum-variance (.8,.2). Zero-volatility assets need a cash/floor policy; negative contributions from shorting or hedging require a separate budget interpretation.

## Baseline HRP procedure

1. Compute an admissible correlation matrix; form distance d_ij=sqrt((1-rho_ij)/2).
2. Select and record a hierarchical linkage rule and deterministic tie-breaking. Obtain leaf order from the tree.
3. Start weights at one on the ordered leaves; recursively bisect ordered clusters.
4. For each child cluster C, form internal inverse-variance weights a_i=(1/Sigma_ii)/sum_j(1/Sigma_jj). Compute cluster variance V_C=a' Sigma_C a.
5. Allocate parent mass to left child as V_right/(V_left+V_right), and right as the complement. Continue to leaves.

For two independent leaves with variances .01 and .04 this baseline yields (.8,.2). It does not imply equal asset risk contributions. Tree leaf order and recursive midpoint splits are part of this algorithm. HERC changes clustering and risk allocation; NCO optimizes within and between clusters. Their exact procedures remain separate variant contracts, not aliases for HRP. Constraints added after HRP require revalidation.

## Scenario expected shortfall

With loss L_s(w), probabilities p_s summing one and alpha∈(0,1), minimize z+[1/(1-alpha)]sum p_s u_s, subject to u_s≥L_s(w)-z and u_s≥0, plus allocation constraints. For linear scenario losses this is a linear-program formulation of ES. z is a quantile-associated threshold, not necessarily unique. CDaR uses path-dependent drawdowns and needs path/time definitions; it cannot substitute terminal loss rows without changing the objective.

Entropic risk rho=(1/theta)log(sum p_s exp(theta L_s)) uses theta>0; large theta increases focus on adverse outcomes. Use log-sum-exp numerics. Confidence levels, scenarios and parameters are preferences/assumptions; optimizer outputs are conditional solutions, not objective truths.

## Evidence boundary

Supporting source map: [HRP](../sources.md#hrp), [HRP-CODE](../sources.md#hrp-code), [RISKFOLIO](../sources.md#riskfolio), [ES-DEFINITION](../sources.md#es-definition). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
