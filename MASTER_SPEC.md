# Quantropy — Specification

> **An applied quantitative-finance curriculum backed by a reference implementation
> that is deep where it matters and honest everywhere.** The teaching is the product.
> The code is built from first principles where real data and real depth are
> reachable — systematic trading, fundamental valuation, and the research-honesty
> stack beneath them — and integrates mature libraries everywhere else.

**Version:** 1.1 · **Owner:** Alain Daccache
**Companions:** `docs/CURRICULUM.md` (the program) · `docs/REFERENCES.md` (verified
canon) · `docs/PROVENANCE.md` (internal: lineage of ported code)

---

## 1. Mission

Demonstrate — publicly, verifiably — the working knowledge of a quant researcher:

1. **A curriculum that executes.** Every lesson's code runs against this library in
   CI on every build. Claims cannot rot, and depth is a contract
   (`docs/CURRICULUM.md` §1), not an adjective.
2. **A reference implementation with real depth.** Not a framework collection — a
   small library where the load-bearing parts (data integrity, backtesting,
   evaluation statistics, valuation) are built from first principles, tested against
   externally checkable numbers.
3. **A live, honestly-evaluated track record.** A systematic book paper-traded
   through the *same code path* as its backtest, with the overfitting corrections
   applied and the trials count disclosed.

## 2. Scope — two levels, tagged in code

**BUILD (deep, from first principles)** — chosen because free, verifiable data
supports genuine depth:
- **Data integrity layer**: point-in-time (bitemporal) storage, immutable versioned
  snapshots, survivorship-aware universes, SEC EDGAR filings ingestion.
- **Systematic trading track**: signals → sizing → event-driven no-look-ahead
  backtest → evaluation → IBKR paper trading, one code path.
- **Research-honesty stack**: deflated/probabilistic Sharpe, PBO, walk-forward &
  purged CV, robust covariance, acceptance gates, a cumulative trials ledger.
- **Fundamental valuation track**: statements → ratios → DCF / reverse-DCF /
  archetypes → distress/fraud/quality scores, PIT-clean from real filings.
- **Risk on the above**: VaR/ES with backtesting, an equity factor risk model.
- **One ML/alt-data showcase** judged by the same gates as everything else.

**INTEGRATE / SURVEY (broad, honest)** — taught in the curriculum, not rebuilt:
derivatives pricing beyond vanilla teaching implementations (QuantLib), portfolio
optimizers as baselines (PyPortfolioOpt), econometrics engines (statsmodels/arch),
execution & microstructure (models + simulation; no retail L2 data), rates/credit/
XVA (survey; retail data cannot support more). Every capability is tagged
`[deep]` / `[integration]` / `[survey]` — the boundary lives in the artifacts, not
in marketing.

**Out entirely:** HFT infrastructure, hosted multi-user product, compliance/tax
operations, crypto (calendar layer stays general enough to admit it later).

## 3. Principles (enforced, not aspirational)

- **P1 Finished beats broad.** Smaller and demonstrable beats sprawling and stubbed.
- **P2 Tiered correctness.** Money/sizing/risk/pricing code gets adversarial
  reference-value tests (externally checkable numbers, brute-force cross-checks);
  the rest gets proportionate coverage. Warnings fail the suite.
- **P3 No look-ahead, both kinds.** The engine owns fill timing (execution
  leakage); a causal feature contract governs transforms (in-sample leakage);
  fundamentals are as-reported via the PIT store, never restated history.
- **P4 Anti-overfit by default.** Multiple-testing corrections, walk-forward/purged
  CV, and the trials ledger are the standard path, and the curriculum teaches why.
- **P5 Reproducible, including data.** Seeded determinism; a network-free core;
  backtests pin immutable data snapshots.
- **P6 One code path to live, divergences modelled.** Backtest and paper/live share
  the signal→portfolio→venue path; the simulated venue can inject partial fills,
  rejects, and latency rather than assuming parity.
- **P7 Integrate, don't reinvent.** Where a mature library is correct, drive it and
  add rigor + teaching; rebuild only where building *is* the lesson or the edge.
- **P8 Honest labels.** `[deep]`/`[integration]`/`[survey]` on capabilities;
  `[backtest]`/`[paper]` on any performance claim.
- **P9 Secrets via environment only.** Enforced by hooks and tests.
- **P10 Earn each abstraction.** Structure grows when it hurts, not speculatively.

## 4. Architecture

```
quantropy/
  core/        # conventions & numerics: returns, TVM, stats, (grows per P10)
  data/        # PIT store, snapshot store, universe, providers (stooq, EDGAR)
  research/    # signals, feature contract, signal lab, hypothesis/trials ledger
  portfolio/   # sizing (vol targeting), covariance, optimization wrappers
  backtest/    # event-driven engine, costs, venue Protocol + SimulatedVenue
  evaluation/  # deflated Sharpe, PBO, walk-forward, gates, tearsheets
  valuation/   # statements, DCF/reverse-DCF, archetypes, scores
  live/        # IBKRVenue (paper/live), risk limits, reconciliation
curriculum/    # the executable book (CI-built, execution-gated)
legacy/        # archived prior work; never imported (docs/PROVENANCE.md)
```

Core dependencies: numpy/pandas/scipy/pyarrow only — offline and deterministic.
Extras: `[data]` (requests, truststore) · `[live]` (ib_async) · `[ml]` · `[report]` ·
`[book]` (jupyter-book<2, jupytext) · `[dev]` (pytest, ruff).

Contracts that matter: `PointInTimeStore.as_of()` (only what was knowable),
`SnapshotStore` (immutable by id), `Signal` (pure, causal), `Venue` (the single
sim/live seam), `BacktestConfig` (seeded, snapshot-pinned).

## 5. Milestones

Each milestone ends demonstrable and ships its curriculum module as
definition-of-done.

| # | Deliverable | Status |
|---|---|---|
| M0 | Package, CI, executable book harness; `core` conventions with reference tests | ✅ shipped |
| M1 | Data layer: PIT + snapshots + universe + stooq/EDGAR providers; curriculum Module 2 | ✅ shipped |
| T1 | **Thin thread**: one toy signal → sizing → event-driven backtest → simulated venue → IBKR paper order → one enforced risk limit (equity, then micro future) | ◀ next |
| M2 | Systematic track deep: signal families, evaluation stack, trials ledger; begin the public paper track record; Modules 8–9 | |
| M3 | Valuation track deep: statements→DCF/reverse-DCF/scores from EDGAR; Module 3 | |
| M4 | ML/alt-data showcase through the same gates | |
| M5 | Risk: VaR/ES + backtesting, equity factor risk model; portfolio construction on robust covariance; Modules 6–7 | |
| M6 | Curriculum breadth: Modules 1, 4, 5, 10 (integration/survey) | |
| M7 | Live hardening + reporting polish; Module 11; capstones | |

## 6. Standing decisions

Broker: IBKR (equities + futures, paper first). Data: keyless (stooq) + EDGAR;
snapshots as versioned Parquet (DuckDB later only if querying hurts). Book engine:
jupyter-book 1.x pinned. Old credentials that ever touched this repo's history:
**rotate at the provider** — scrubbing files does not scrub history.
