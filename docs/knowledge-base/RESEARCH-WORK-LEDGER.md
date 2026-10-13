# Research work ledger

## Current evidence, without an overall completion claim

The reference layer contains fifteen foundational articles. Twenty-five substantive family contracts now define reusable formulas/procedures and examples. All 306 legacy method IDs have a canonical family owner in the method catalog. The 120 broad research units have a learner reference owner and, where applicable, a family link. These are ownership and draft-coverage facts; they do not imply each method or unit is complete or independently verified.

## Mathematical and model-specific work still required

- Forensics: exact original Altman variants, Beneish original input construction versus named proxies, and Piotroski original scaling/issuance population. This pass does not erase earlier source-access limitations.
- Estimation: the centered ML scaled-identity Ledoit-Wolf variant now has a source-inspected exact procedure and checked offline implementation (KC-26); constant-correlation and nonlinear shrinkage, robust covariance, random-matrix thresholds, detoning, regime inference, entropy-pooling constraints and Bayesian predictive uncertainty remain open. Independent domain review and empirical estimator assessment remain open for the implemented variant too.
- Allocation: dedicated HERC/NCO algorithms; robust ambiguity sets; factor risk decomposition; CDaR path formulations; skew/kurtosis, distributionally robust, dynamic goal/utility, tax-lot and integer variants.
- Derivatives: constrained SVI/SSVI, SABR approximations, Dupire differentiation, stable Heston characteristic integration/calibration, jumps, Hull-White, PDE/tree boundaries, early exercise, and complex settlement.
- Credit/fixed income: multicurve conventions, recovery variants, mortgage prepayment, securitized waterfalls, credit derivatives, CVA/wrong-way risk and full structural calibration.
- Empirical finance: exact q/QMJ/BAB/liquidity/mispricing/IPCA constructions, causal designs, Fama-MacBeth inference, latent state models and complete published-factor replications.
- Validation: CSCV/PBO tie and dependence sensitivity, correlated-trial estimation for DSR, track-record assumptions, sequential bootstrap and label concurrency, nested purged searches and null-model design.
- Planning/actuarial: dated pension/product rules, joint-life and disability state models, claims triangles, credibility, catastrophe dependence, reinsurance aggregation and reserve bases.
- Private/sector models: full deal waterfalls, PME variants, issuer examples, dilution/milestone dependency, serial-acquisition capital deployment and sector accounting reconciliation.

## Business knowledge beyond formulas

Full economics/monetary theory, public welfare appraisal, financial history, behavioral interventions, corporate governance, sustainable/climate finance, Islamic finance, development/microfinance, commercial guarantees, niche real assets and cross-border family planning need additional substantive references. Their existing coverage containers remain research entry points, not finished specialist teaching material.

## Source and review work

Some original papers are inaccessible or only partially inspected; public summaries cannot be promoted to full original-paper review. Claim evidence needs exact section/edition links for each material equation. Independent mathematical and domain reviews remain outstanding; author review and automated example checks are separate. Jurisdiction rules require country, account/entity type, effective date and update monitoring. No universal tax/regulatory rulebook is claimed.

## Progress discipline

Keep working through prerequisite dependencies, attaching new exact variants to existing IDs or creating scoped new IDs. Replace duplicated discovery definitions with links after reconciliation. Mark a method complete only when the knowledge contract is fulfilled; do not set every row complete because a family draft exists. Source count, article count and automated arithmetic are evidence about specific activities, not a global quality rating.

[Family contracts](contracts/README.md) · [Catalog](method-catalog.csv) · [Index](README.md)

## Research direction update — 2026-10-13

The [reset brief](RESEARCH-RESET-BRIEF.md) establishes broad multi-role intent and separates research breadth from profile-specific feasibility. Use the [question register](research-questions.csv) to discover missing decisions and the [handoff prompt](CONTINUE-IN-FRESH-SESSION.md) to continue. These new artifacts do not certify additional methods or close the backlog above.

## Exact estimator and offline vertical workflow — 2026-10-13

Added [KC-26](contracts/26-ledoit-wolf.md) for QMV-114-LW-I under the existing QM-114 family, and [KC-27](contracts/27-portfolio-comparison.md) for a reproducible funded-return policy comparison. There are now 27 registered contracts; the original 306 family mappings are retained. One exact child variant is recorded in [method-variants.csv](method-variants.csv). No method is marked globally complete.

Source work: original scaled-identity paper Sections 3.1-3.3 and the key equation page inspected; scanned *Honey* target pages visually checked; pinned scikit-learn 1.7.2 functions inspected; author-linked diversification paper abstract/introduction and evaluation section inspected. Detailed depths and missing proofs/replications are recorded in [sources](sources.md) and claims EVD-017 through EVD-021. Author-run source-function agreement is not independent scholarly review.

Development: isolated `quantropy_research` library and CLI, without importing legacy service modules. It compares equal weight, explicitly capped inverse volatility, sample GMV and LW identity GMV with shared timestamps, concentration cap and costs. Explicit user/mandate/account/deployment scenario fields prevent inferred personal constraints. Availability determines the training window; drifted holdings and self-financing costs determine wealth. Unsupported funding profiles and failed solvers raise errors.

Validation maintenance: extended variant ownership/prerequisite, claim-source and question-ID checks; added eight standard-library hand calculations. Existing manifest hashes were Windows-checkout byte hashes rather than Git blob hashes. Research artifacts now use LF through `.gitattributes`, and the reviewed manifest is refreshed against those portable bytes. This is a verification correction, not additional conceptual completion credit.

Evidence: 18 implementation tests; 85 fixtures against the extracted pinned reference routine; analytical examples plus existing repository verifiers. The [demonstration](portfolio-comparison-verification.json) records four policies over thirteen common evaluation intervals, entirely synthetic; [reference comparison](portfolio-reference-verification.json) records the pinned source hash and exact check scope. No market data, empirical superiority, independent domain approval, full-stack application integration or live readiness is certified. No broker service was started or transaction/spending performed.

Next dependency work: specify point-in-time versioned real datasets and rights; choose a predeclared empirical comparison protocol with dependence-aware uncertainty and all trials retained; derive constant-correlation and nonlinear alternatives; expand allocation policies without hiding new funding/mandate requirements. Continue return-source cards across markets and horizons, specialist contracts and the broad backlog above in parallel research sequence; the first implementation's funded long-only boundary is not the product's ultimate scope. User-specific deployment choices remain scenarios until known.
