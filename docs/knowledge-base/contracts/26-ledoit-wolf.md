# Ledoit-Wolf covariance: scaled-identity variant

ID: KC-26; exact variant QMV-114-LW-I of QM-114. Owner: this contract, linked by the [estimator family](05-estimators.md). Date: 2026-10-13. Status: source-inspected procedure, numerical examples and offline implementation checked; author review only. Independent mathematical/domain review and empirical validation pending.

Prerequisites: [statistics](01-statistics.md), [numerics](02-numerics.md), [estimator conventions](05-estimators.md). This estimates a physical-measure return covariance, not expected return, alpha or a risk-neutral price. Researchers and portfolio managers can apply it to aligned asset or strategy observations; deployment feasibility is a separate profile decision.

## Inputs and convention

Let R have n rows of observations and p columns of aligned streams, n >= 2 and p >= 1. Entries are finite, same-period decimal returns in the same currency and return convention. For example, 1% is 0.01. Missing observations are rejected: no pairwise deletion, forward filling or implicit interpolation. A complete-case sampling decision must be documented upstream. Estimation uses only information available before the decision. Center each column using its training-window mean: x_t = R_t - mean(R). Units of covariance are squared period returns; fourth-moment quantities below have fourth-power return units.

Here S = sum_t x_t x_t' / n. This ML denominator deliberately differs from the n-1 sample convention in KC-05. Scaling an n-1 covariance into the formula without changing every term defines a different estimator. The implementation always estimates the mean; known-zero-mean and finite-sample unbiased corrections are different variants.

## Procedure and interpretation

Define the normalized squared Frobenius norm ||A||_p^2 = sum_ij A_ij^2 / p. Calculate:

1. m = trace(S) / p and F = m I_p.
2. d2 = ||S - F||_p^2.
3. b_bar2 = sum_t ||x_t x_t' - S||_p^2 / n^2.
4. b2 = min(b_bar2, d2). If d2 > 0, delta = b2/d2; otherwise define delta = 0.
5. Sigma_hat = (1-delta) S + delta F.

The paper's Section 3.3, Lemmas 3.2-3.5 and equation (14), provide this target and intensity for its zero-mean observations. Centering and the degenerate convention are checked against the pinned scikit-learn implementation. The ratio is dimensionless. d2 measures departure from isotropic scatter; b_bar2 estimates sampling noise using dispersion of observation outer products around their mean. The cap produces a convex blend. It trades bias toward equal variances and zero covariances against sampling error. It does not shrink expected returns or invent independent assets.

For PSD S, the eigenvalues are (1-delta) lambda_i(S) + delta m, and the trace is preserved. Positive delta and m give positive definiteness; zero scatter gives a zero matrix. An inverse is therefore not universally guaranteed for arbitrary degenerate input. One column has F=S and returns its ML variance, with delta=0. At exactly isotropic S, intensity has no economic effect because both endpoints coincide.

## Assumptions and evidence limits

The original asymptotic analysis uses independent identically distributed observations with zero mean, bounded p/n, an averaged eighth-moment bound and restrictions on dependence among products in the population eigenbasis (Section 3.1, Assumptions 1-3). Distribution-free does not mean assumption-free. Centered financial returns with serial dependence, regime shifts, jumps or heavy tails may violate those conditions. The implementation is a defined estimator under those inputs; the paper's guarantee must not be automatically carried over. Block-resampling, regime sensitivity and economic risk/funding tests remain necessary.

Its optimality concerns a quadratic covariance loss in a stated asymptotic linear-shrinkage class. It is not a universal portfolio-performance theorem. The constant-correlation target of *Honey, I Shrunk the Sample Covariance Matrix* (published page 113) preserves separate variances and equalizes pairwise correlations. It needs a different intensity calculation. Nonlinear shrinkage, OAS, EWMA and robust estimators also remain separate methods. Neither that paper's active-manager study nor the diversification study establishes this prototype's future performance.

## Worked and edge cases

Use four fictional observations (1,0), (-1,0), (0,2), (0,-2) in arbitrary observation units, chosen for arithmetic transparency rather than plausible funded returns. Means are zero. S=diag(1/2,2), m=5/4. d2=9/16. The four squared normalized outer-product deviations are 17/8, 17/8, 17/8, 17/8, so b_bar2=17/32. Delta=17/18 and Sigma_hat=diag(29/24,31/24). Trace remains 5/2. Multiplying every observation by 0.01 multiplies covariance by 0.0001 and leaves intensity unchanged. The unbiased sample covariance is diag(2/3,8/3), illustrating the denominator distinction.

Constant columns produce zero scatter, not infinite precision or a risk-free tradable opportunity. Singular high-dimensional samples can become full rank under positive shrinkage, while perfectly deterministic outer products can leave delta=0. Translation, common scaling and column permutation must preserve the corresponding covariance relationship. Scaling each column separately changes the target: shrinking a correlation matrix and rescaling is not this estimator.

Numerical procedure: divide observations by their maximum absolute magnitude, center, accumulate outer-product deviations, then rescale covariance. This avoids fourth-power overflow and cancellation in a subtractive fourth-moment formula. It costs O(n p^2) time and O(p^2+n p) memory. Reject nonfinite data, insufficient history, overflow and nonzero covariance underflow; never silently replace invalid input with an identity matrix.

## Evidence and validation

| Claim | Exact inspected evidence | Remaining limit |
|---|---|---|
| Target, norm and intensity | [LW-IDENTITY-2004](../sources.md#lw-identity-2004), Sections 3.1-3.3; equation (14), printed page 380 visually checked | Proof appendices not reviewed in full |
| Centering, ML convention and degenerate intensity | [SKLEARN-LW-172](../sources.md#sklearn-lw-172), `_ledoit_wolf` and `ledoit_wolf_shrinkage`, pinned 1.7.2 source | Function comparison is not a full installed-library integration test |
| Constant-correlation variant differs | [SHRINKAGE](../sources.md#shrinkage), published pages 112-113 visually checked | Its intensity appendices and empirical results not replicated |

Implementation: repository module `quantropy_research/covariance.py`; tests `tests/test_research_portfolio.py`. The [reference-function report](../portfolio-reference-verification.json) records source hash and numerical comparison scope. This cross-check and hand arithmetic are author-run evidence, not independent human review. Revalidate if denominator, centering, target, input timing, numerical scaling or source version changes. Production risk-model integration is unassessed.

[Contract index](README.md) · [Workflow using this estimator](27-portfolio-comparison.md)
