# Curves, bonds, credit and collateral

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [02-numerics](02-numerics.md).

## Cash-flow and curve procedure

Generate contractual dates from issue/maturity, payment frequency, calendar, business-day adjustment, day count and ex-coupon terms. Preserve both contractual and adjusted dates. Price=sum CF_i D(t_i). For single-curve deterministic deposits, D(T)=1/(1+r delta) under simple interest. For a par swap with accruals delta_i and par rate K in a simplified single-curve setting, K sum delta_i D(t_i)=1-D(T). Bootstrap the next factor from already known factors; multi-curve collateralized pricing changes projection and discount inputs.

Example D(1)=1/1.05 and a two-year annual par swap K=.05 imply D(2)=[1-.05D(1)]/1.05=.907029478. Reprice every input instrument and verify tolerances. Interpolation in discount factors, zero rates or forwards produces different curves; forbid silent extrapolation. Negative yields can be admissible but discount factors must respect the chosen economic/model setting.

Dollar duration is -dP/dy; DV01 is approximately -dP/dy*0.0001, conventionally quoted as a positive loss magnitude for a yield increase. Convexity=P''/P. Key-rate shocks perturb selected curve inputs under explicit interpolation and rebootstrap rules. Full repricing is required when optionality/default behavior changes.

## Default and funding

Under a chosen default-intensity model lambda(t), survival Q(t)=exp(-integral lambda du). Expected promised flows multiply survival; recovery adds a separate default-payment integral under a specified recovery-of-par, market-value or treasury convention. Risk-neutral intensity inferred from traded prices differs from physical default probability. The rough spread≈hazard*(1-recovery) relation omits term structure, liquidity and detailed cash timing.

For constant hazard .02 and recovery .4, one-year survival is exp(-.02)=.980198673 and the rough spread is .012, not a complete bond price. Structural credit relates default to firm assets/debt and model dynamics; reduced-form credit uses event intensity. CVA integrates discounted exposure against counterparty default/loss under joint assumptions; wrong-way risk invalidates naive independence.

Repo and securities lending involve collateral, haircuts, mark-to-market, maturity and legal closeout. A haircut creates funding needs; it is not the same as expected credit loss. Floating, inflation-linked, callable, mortgage and securitized contracts require distinct payoff projections and waterfalls. This contract specifies the simple bootstrap/default baseline; specialist legal and multi-curve extensions remain separate contracts.

## Evidence boundary

Supporting source map: [FINRA-BONDS](../sources.md#finra-bonds), [QUANTLIB](../sources.md#quantlib), [BASEL](../sources.md#basel). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
