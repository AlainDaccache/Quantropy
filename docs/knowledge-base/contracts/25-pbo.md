# Combinatorially symmetric cross-validation and PBO

Status: substantive baseline draft; independent review pending. Prerequisite: [selection and validation](15-validation.md).

Arrange synchronous performance observations as T rows by N candidate strategies. Choose an even number S of contiguous, equal-size row blocks; declare treatment when T is not divisible by S. Fix the performance statistic and deterministic tie policy.

For every combination of S/2 blocks, use those blocks as in-sample selection and the complement as out-of-sample evaluation. Select the best in-sample candidate. Rank all candidates out of sample in ascending performance order, using average ranks for ties. If the selected candidate's out-of-sample rank is r, calculate omega=r/(N+1) and logit=ln(omega/(1-omega)). Baseline PBO is the proportion of logits below zero; report zero logits separately and document threshold conventions.

Example: N=3 and the in-sample winner ranks first out of sample. Omega=.25 and logit=-1.098612, indicating below-median out-of-sample rank. At rank 2 the logit is zero. S=4 creates six selections, including complementary selections.

This assesses selection across the submitted candidate family. Missing trials, leakage, unstable statistics and dependence affect interpretation. CSCV is different from chronological walk-forward or combinatorial **purged** cross-validation.

Evidence: [author paper, Algorithm 2.3](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf), inspected during this pass. [Contract index](README.md).
