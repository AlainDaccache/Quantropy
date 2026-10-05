# Mathematical foundations and numerical model risk

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

The library needs a validated mathematical foundation, not just named financial models. Specify compounding, present value, cash-flow dates, probability, conditional expectation, estimation, optimization and units before advanced models depend on them. Keep arithmetic identities, statistical approximations and economic assumptions visibly distinct.

Advanced models need a clear probability measure and purpose: real-world dynamics for forecasting/scenarios versus risk-neutral dynamics for pricing under stated assumptions. Study stochastic processes, diffusion/jump dynamics, simulation discretization, trees, finite differences and numerical integration through separately reviewed mathematical sources. A model can fit observed prices and still produce unstable or inappropriate forecasts.

Calibration must state objective, weighting, quote uncertainty, constraints, regularization, parameter bounds and identifiability. Test convergence, sensitivity and alternative parameter sets. Illiquid quotes do not justify precise parameters. Numerical solvers need failure status, tolerance/termination policy and boundary cases; do not return the last iterate as a verified answer.

Validate analytic identities, limiting cases, finite-difference sensitivities and independent implementations. Monte Carlo output needs sampling error and convergence analysis; optimization needs feasibility and perturbation tests. Curves/surfaces require no-arbitrage diagnostics appropriate to the product, plus interpolation/extrapolation policies. Library integrations require convention review as well as numerical agreement.

Model governance stores model/source/version, applicability, assumptions, calibration inputs, reviewer, tests, known weaknesses and revalidation triggers. Review uncertainty across plausible models as well as within one model. Distinguish input, parameter, structural and operational risk. No single precise output should conceal unsupported assumptions.

Acceptance: failures are explicit; scaling/time/unit mistakes are caught independently; calibration is reproducible; estimated results disclose precision and uncertainty; every enabled calculation has a reviewed exact specification. This chapter defines required foundations. It does not claim the stochastic mathematics or every pricing algorithm has already been derived here.

## Coverage checklist

- Time value compounding and dated cash-flow primitives
- Probability estimation and conditional expectation
- Physical versus risk-neutral purpose
- Stochastic diffusion jump and scenario specifications
- Numerical trees PDE integration simulation
- Calibration objectives identifiability and constraints
- Solver convergence tolerance and explicit failures
- Independent limiting-case and sensitivity checks
- Model uncertainty governance and revalidation

## Research sources

- [QUANTLIB](sources.md#quantlib)
- [SVI](sources.md#svi)
- [SKLEARN](sources.md#sklearn)
- [FRM](sources.md#frm)

[Knowledge base index](README.md)
