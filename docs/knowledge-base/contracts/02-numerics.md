# Linear algebra, optimization and numerical controls

Status: substantive draft; author review only. Examples are fictional. This is a family contract: named advanced variants are not fully specified unless their procedure appears explicitly below. Implementation is unassessed.

Prerequisites: [01-statistics](01-statistics.md).

## Contracts

A covariance matrix must be symmetric and positive semidefinite: x' Sigma x≥0 for every vector x. Positive definite matrices have strictly positive quadratic form for nonzero x and are invertible. Eigenvalues diagnose admissibility but tolerances depend on scale. Cholesky requires positive definiteness; singular positive-semidefinite cases need another factorization. Clipping negative eigenvalues changes the estimate and must be logged.

Root finding solves f(x)=0. For a continuous f with opposite signs at a and b, bisection repeatedly halves the bracket while preserving a root. Brent-style methods combine bracketed safeguards and interpolation. A sign-change bracket is sufficient, not necessary: an even-multiplicity root need not change sign. A discontinuity can change sign without a root. Newton iteration x_next=x-f(x)/f'(x) can diverge or cross invalid domains.

Constrained minimization defines an objective, feasible set and tolerance. Convex objectives on convex sets have global-optimum guarantees under appropriate existence conditions; nonconvex methods can return local solutions. KKT conditions use stationarity, feasibility, dual feasibility and complementarity; qualification assumptions matter. Solver success does not establish economically appropriate inputs.

## Procedure and examples

1. Validate dimensions, units, finite values and economic input domains.
2. Scale variables; choose algorithm based on smoothness, convexity and constraints.
3. Record tolerances, initialization, convergence and residuals.
4. Recompute constraints/objective independently and compare a benchmark or limiting case.
5. Return explicit failure instead of silently reusing a stale or infeasible result.

For f(x)=x²-2 on [1,2], bisection converges to sqrt(2). For f(x)=1/x on [-1,1], opposite signs do not justify bisection because f is discontinuous at zero. A bond price decreasing with yield supports a unique bracketed yield root only under positive fixed cash flows and an admissible rate domain.

Finite differences for f'(x) use [f(x+h)-f(x-h)]/(2h). For x² at x=3, this gives 6 in exact arithmetic. Tiny h magnifies cancellation; large h increases approximation error. Check multiple step sizes. Monte Carlo error decreases roughly as 1/sqrt(N) for iid finite-variance samples; discretization and calibration error do not disappear by increasing N alone.

## Evidence boundary

Supporting source map: [SCIPY-ROOTS](../sources.md#scipy-roots), [CVXPY-QP](../sources.md#cvxpy-qp). Review depths are recorded there. These references support the inspected concepts, not every extension in this draft. Independent domain review and full claim-level source reconciliation remain release gates.

[Contract index](README.md)
