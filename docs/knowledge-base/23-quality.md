# What “10/10” must mean in practice

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Replace a subjective overall score with a transparent evidence card for each supported workflow. Financial correctness: independently checked identities, pricing and cash conservation. Research integrity: availability, trial history and unseen validation. Data quality: provenance, coverage, missingness and licensing. Trading safety: order-state recovery, risk limits and actual reconciliation. Reliability: measured failure handling and restoration. Usability: understandable conclusions and uncertainty. Performance: adequate throughput/latency for the declared strategy. Security/privacy: verified controls and secrets isolation. Maintainability: clear modules, reproducibility and migration. Economic usefulness: realistic net benefit against a simple baseline and maintenance/data cost.

Not all dimensions are averageable. A beautiful UI cannot compensate for disappearing holdings; fast computation cannot compensate for future information; strong past returns cannot compensate for uncontrolled duplicate orders. Financial/operational blockers should be pass/fail gates with evidence, while convenience and coverage can be incremental.

Define acceptance fixtures before implementation where semantics are subtle. Cover positive/negative/zero prices, missing marks, flow timing, splits, delistings, negative yields, expiry, assignment, weekends/DST, restatements, failed submits and partial fills. Use independent hand-worked examples and library cross-checks rather than tests that duplicate the implementation. Property/invariant testing is useful for cash/position conservation and causality.

Track numerical tolerances by model and input precision. Convergence tests matter for numerical pricing; exact monetary fixtures matter for the ledger. Produce a release evidence bundle linking requirements, data manifests, model versions, tests, limitations and operational drills.

Acceptance: no advertised live-supported instrument has unverified lifecycle/ledger behavior; reports display limitations and stale evidence; the quality card can be audited without trusting the developer's opinion. Achieving excellence is an ongoing maintenance process, not a one-time claim of perfection.

## Coverage checklist

- Financial correctness evidence
- Research causality evidence
- Data coverage quality and rights
- Trading safety and recovery evidence
- Reliability and restore evidence
- Usability accessibility and explanations
- Workflow performance budgets
- Security and privacy verification
- Maintainability and reproducible releases
- Economic utility and baseline comparison
- Numerical tolerances and independent fixtures

## Research sources

- [LEAN-LIVE](sources.md#lean-live)
- [OWASP](sources.md#owasp)
- [OVERFIT](sources.md#overfit)

[Knowledge base index](README.md)
