# Returns, covariance and Bayesian estimation

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [01-statistics](01-statistics.md); [02-numerics](02-numerics.md).

## Baseline estimators

Arithmetic mean estimates a single-period expectation under its sample assumptions. Geometric mean=(product(1+r_t))^(1/n)-1 measures compound growth, provided the gross-return product and definition are admissible. EWMA weights recent observations using a decay lambda in (0,1), normalizing finite-window weights and handling initialization explicitly. Annualization must match sampling frequency and dependence.

Sample covariance centers return columns and divides by n-1. EWMA covariance uses weighted deviations under a declared mean convention. Linear shrinkage Sigma_hat=(1-delta)S+delta F blends sample S with target F; delta∈[0,1] and F's structure are inputs or estimated rules. A diagonal target discards cross-covariances; an identity-scaled target equalizes variance. Ledoit-Wolf is a specific estimator of the intensity/target, not any manually chosen blend.

Factor covariance is B Sigma_f B'+Sigma_e under the residual assumptions. PCA decomposes covariance and retains selected eigenvectors; scale, component count and out-of-sample fitting matter. Random-matrix denoising and detoning are different transformations requiring explicit component-selection rules. A regime mixture needs state probabilities known or estimated from past information.

## Bayesian and view combination

For a Gaussian prior mu~N(pi,tau Sigma) and Gaussian views q=P mu+noise with covariance Omega, posterior mean is [(tau Sigma)^(-1)+P' Omega^(-1)P]^(-1)[(tau Sigma)^(-1)pi+P' Omega^(-1)q], using proper positive-definite assumptions. This is a declared Black-Litterman-style view update; posterior uncertainty in the mean is distinct from predictive return covariance. Equilibrium pi=delta Sigma w_market uses a specified risk aversion delta. Do not combine incompatible annual and monthly objects.

Example: a scalar prior mean .04 with variance .01 and view .08 with variance .01 gives posterior mean .06 and variance .005. Making the view less precise moves the posterior toward .04. Singular views or duplicate constraints require generalized treatment, not blind inversion.

Entropy pooling instead updates scenario probabilities by minimizing sum p_i log(p_i/p0_i) subject to chosen view constraints, probability nonnegativity and total one. Its inputs are a scenario distribution and views, not the same objects as a Gaussian mean update. Robust estimators, nonlinear shrinkage and latent regime fitting remain separate detailed algorithms.

## Validation

Use a training-only window; reconcile sample dates and corporate actions. Check symmetry, eigenvalues, scale and sensitivity. Bootstrap entire estimator pipelines for weight stability rather than treating estimated means as known constants. Estimation uncertainty can dominate solver precision.

## Evidence boundary

Supporting source map: [SHRINKAGE](../sources.md#shrinkage), [PYPORTFOLIOOPT](../sources.md#pyportfolioopt), [COCHRANE](../sources.md#cochrane). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
