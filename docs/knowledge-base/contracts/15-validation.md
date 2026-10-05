# Bootstrap, selection bias and ML research controls

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [14-backtesting](14-backtesting.md).

## Dependence and resampling

An iid bootstrap samples observations with replacement; it destroys time dependence. A moving-block bootstrap samples contiguous blocks of a chosen length and concatenates them. A stationary bootstrap chooses random block lengths, commonly geometric with declared mean length, and a boundary policy. For cross-asset returns, sample the same dates jointly to retain contemporaneous dependence. Refit estimation and selection inside resamples when assessing the complete research process.

Monte Carlo null testing defines a null-generating model and compares an observed statistic with its simulated distribution. Randomized-signal placebos must preserve the structure relevant to the null. Shuffling all returns can falsely make persistent or seasonal patterns look significant. A bootstrap of an already overfitted strategy does not account for unlogged search.

## Multiple tests and overfit

For m hypotheses with valid individual p-values, Bonferroni tests at alpha/m to control family-wise error by the union bound. Holm orders p-values and applies sequential thresholds alpha/(m-j+1). Benjamini-Hochberg targets false-discovery rate under specified dependence conditions: find largest j with p_(j)≤j*q/m and reject through j. The desired error criterion and candidate family must be declared.

Example m=10 and alpha=.05 give Bonferroni cutoff .005; an isolated p=.01 does not pass that criterion. PSR/DSR and minimum-track-record formulas require higher-moment, benchmark and effective-trial conventions. CSCV/PBO compares in-sample selection with out-of-sample ranks under a specific partition algorithm. These diagnostics remain specialist derivations here; no invented numeric score should substitute for a missing formula.

## Feature and label pipeline

Triple-barrier labels define upper/lower price barriers plus a timeout and a first-touch rule; ambiguity in coarse prices must be resolved explicitly. Meta-labeling estimates a decision to accept/reject a separately specified primary signal; use out-of-fold primary predictions to prevent reuse leakage. Sample uniqueness depends on overlapping event spans and concurrency; sequential bootstrap seeks informative samples under its algorithm, not arbitrary iid draws.

Fractional differencing weights follow w0=1, wk=-w_(k-1)(d-k+1)/k for an explicitly truncated or expanding filter. At d=1 this becomes first difference; at d=0 identity. Fixed-width threshold and fitting window affect information loss and stationarity. Permutation importance breaks feature dependence and can mislead with correlated predictors; conditional/grouped importance and orthogonal transformations answer different questions. Hyperparameter search must nest inside the training/evaluation protocol.

## Evidence boundary

Supporting source map: [OVERFIT](../sources.md#overfit), [MULTIPLE-TESTS](../sources.md#multiple-tests), [SKLEARN](../sources.md#sklearn). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
