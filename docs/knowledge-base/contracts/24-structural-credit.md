# Merton structural credit baseline

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [11-option-pricing](11-option-pricing.md); [10-curves-credit](10-curves-credit.md).

Assume firm asset value V follows a constant-volatility diffusion, no payouts, one zero-coupon debt claim with face K at T, and default only at T. Equity payoff is max(V_T-K,0), and debt payoff min(V_T,K). Thus E=V*N(d1)-K*exp(-rT)*N(d2), D=V-E, with d1=[ln(V/K)+(r+sigma_V²/2)T]/(sigma_V sqrt(T)), d2=d1-sigma_V sqrt(T). Risk-neutral default probability is N(-d2).

Physical default probability replaces r with an estimated physical asset drift; the two probabilities are not interchangeable. Observable equity volatility and value can be used with sigma_E*E=N(d1)*sigma_V*V to infer latent asset inputs under the model. Inference needs constraints and sensitivity checks.

At maturity V_T=120,K=100 gives equity 20/debt 100; V_T=80 gives equity 0/debt 80. Values reconcile to assets. Real firms have coupons, multiple maturities, payout, legal priority and earlier default; first-passage/covenant models are different contracts. This simple baseline is not a complete credit underwriting engine.

## Evidence boundary

Supporting source map: [MERTON-LECTURE](../sources.md#merton-lecture). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
