# Probabilistic and deflated Sharpe: baseline formula

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [15-validation](15-validation.md); [16-performance](16-performance.md).

Use non-annualized Sharpe s, sample length T>1, skewness g3 and raw kurtosis g4. Let A=1-g3*s+(g4-1)*s²/4. The asymptotic PSR against benchmark s0 is Phi[(s-s0)*sqrt(T-1)/sqrt(A)], requiring A>0 and the paper's moment/dependence assumptions. Phi is standard-normal CDF.

For N>1 independent trials under the stated normal approximation, null mean m and trial-Sharpe standard deviation v, define s0=m+v[(1-c)Phi_inverse(1-1/N)+c Phi_inverse(1-1/(N*e))], where c≈.577215665. DSR uses that selection benchmark in PSR. Effective independent trials are an estimation problem; raw experiment count is not automatically valid.

Example s=s0 gives .5. For normal moments g3=0,g4=3,s=.1,s0=0,T=101, PSR≈.840741. Dependence, unstable moments and omitted trials weaken interpretation. Minimum sample length for confidence p follows 1+A[Phi_inverse(p)/(s-s0)]² when s>s0; apply asymptotic and integer conventions. This diagnostic does not repair leakage or certify profitability.

## Evidence boundary

Supporting source map: [DSR-PAPER](../sources.md#dsr-paper). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
