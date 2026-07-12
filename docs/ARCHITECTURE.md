# Quantropy — Architecture & Domain Model

> The engineering companion to `MASTER_SPEC.md`. The spec says *what* and *why*;
> this document says *how the system is shaped*: the domain model (the entities and
> the language), the bounded contexts, the package architecture and its dependency
> law (CI-enforced, not aspirational), the contracts between parts, the invariants
> tests guarantee, and the extension points every future milestone plugs into.

**Status legend:** ✅ built · 🔜 next milestone · 📋 designed, later milestone.

---

## 1. Design stance

Four decisions shape everything below:

1. **One decision path, two worlds.** Research and live trading share the exact
   code path `Signal → Sizer → RiskLimits → Order → Venue`; only the `Venue`
   implementation differs. Everything else in the architecture exists to protect
   this property.
2. **Causality is structural, not behavioral.** No component *receives* future
   data: the engine slices history, transforms are trailing-only, allocation
   shifts by one bar. Prefix-invariance tests fail the build if any path peeks.
3. **Facts are immutable; state is append-only.** Snapshots never change; the PIT
   store and the trials ledger only append; corrections are new records. Anything
   that must "update" does so by adding, never rewriting.
4. **Small now, shaped for later.** Packages exist only when a milestone needs
   them (P10), but their *boundaries* are drawn for the full program — adding M3's
   valuation engine or M5's risk models must never require moving existing code.

---

## 2. The domain model — seven bounded contexts

Each context owns its entities and speaks its own language; contexts interact only
through the contracts in §4. (DDD-flavored: entities have identity, value objects
don't, aggregates enforce invariants.)

### 2.1 Market Data context ✅ — *"what was knowable, when"*

| Object | Kind | Essence |
|---|---|---|
| `Instrument` | value object | identity + the specs that change P&L math: symbol, asset class, currency, **multiplier**, tick size |
| `Bar` / price series | value | OHLCV at a date; the empirical substrate (raw `Close` *and* `AdjClose` — choosing is a decision, not a default) |
| `Snapshot` | aggregate | an **immutable**, id-addressed set of datasets; the reproducibility unit — a `snapshot_id` pins every downstream result |
| `PointInTimeRecord` | value | (entity, field, **event_date**, **knowledge_date**, value) — the bitemporal atom |
| `PointInTimeStore` | aggregate | append-only record set; `as_of(date)` reconstructs the world as knowable then; restatements append |
| `Universe` | aggregate | membership spans (symbol, start, end); `members(date)` is survivorship-free by construction |
| `Provider` | service | the only network-touching code; **fetch once → snapshot → offline forever** |

**Invariants (tested):** snapshots immutable (same id ⇒ same bytes, second write
raises); `knowledge_date ≥ event_date` (no clairvoyance); same-day corrections
supersede via stable ordering; providers refuse to snapshot garbage (granularity
guard, HTML-block detection).

### 2.2 Fundamentals & Valuation context 🔜 M3 — *"what a claim is worth"*

| Object | Kind | Essence |
|---|---|---|
| `Filing` | entity | a source document (EDGAR accession); facts flow from it into the PIT store |
| `StatementSet` | aggregate | articulated income/balance/cash-flow for one entity, one period, **as-reported** |
| `Ratio` / `DuPont` | value | derived diagnostics; pure functions of a StatementSet |
| `Forecast` | aggregate | driver-based pro-forma with fade/base-rate discipline |
| `ValuationModel` | service | DDM / FCFF / FCFE / residual-income / multiples — all `PV(claims)`; plus the inverse: **market-implied expectations** |
| `Score` | value | Altman Z, Beneish M, Piotroski F — computed here, *consumed* as signals in Research |

**Invariant:** every valuation is reproducible from a pinned snapshot + PIT
`as_of` — the model never touches restated history.

### 2.3 Research context ✅ core — *"is this signal real?"*

| Object | Kind | Essence |
|---|---|---|
| `Hypothesis` | entity | pre-registered (id, name, **mandatory economic rationale**, timestamp) |
| `Trial` | value | one configuration tested: per-period Sharpe, n_obs, params — **every variation looked at is a trial** |
| `TrialsLedger` | aggregate | append-only JSONL of both; `n_trials()` and `trial_sharpe_variance()` are DSR's inputs |
| `Signal` | contract | pure causal map: history-through-t → raw target in [-1, 1] (`MovingAverageCross`, `TimeSeriesMomentum`, …) |
| `Feature` (M2+) | value | any transform under the **causal feature contract**: trailing-window only |

**Invariants:** can't log a trial against an unregistered hypothesis; registration
without rationale is rejected; the ledger file is part of the research record
(committed, diffable).

### 2.4 Portfolio context ✅ core — *"from conviction to exposure"*

| Object | Kind | Essence |
|---|---|---|
| `Sizer` | contract | (raw, history) → weight; `VolatilityTarget` = target_vol / trailing_vol, hard leverage cap |
| `Sleeve` | concept | one (signal × instrument-set) return stream — the book's diversification atom |
| `combine_sleeves` | service | trailing inverse-vol weights across sleeves → vol-target the **combined** stream; fully causal (shift-by-one) |
| `CovarianceEstimator` 📋 M5 | service | sample → shrinkage → factor structure; feeds optimizers |
| `Optimizer` 📋 M5 | service | BL / risk-parity / HRP / CVaR — consumes robust covariance, never raw sample |

**Invariants:** sizing/allocation see only trailing data (prefix-invariance tested
on the combiner exactly as on the engine); no measurable risk ⇒ no position.

### 2.5 Execution context ✅ — *"one seam between research and reality"*

| Object | Kind | Essence |
|---|---|---|
| `Order` | value | signed units of an Instrument — *what*, never *how* |
| `Fill` | value | executed units, actual price (slippage included), explicit cost |
| `Venue` | **the contract** | `execute(Order, market_price) → Fill`; `SimulatedVenue` (adverse slippage + costs, never frictionless) and `IBKRVenue` (ib_async; `positions()` for reconciliation) |
| `RiskLimits` | aggregate | leverage clamp + **latching** drawdown kill switch; re-arm requires human `reset()` |
| `Engine` | service | the event loop: **settle → fill(yesterday's decision, today's price, via venue) → decide(history ≤ today)** ; equity & futures daily-settlement accounting |
| `BacktestConfig` / `BacktestResult` | value / aggregate | seeded, snapshot-pinned run description; equity curve + per-bar diagnostics + costs + kill flag |

**Invariants (the T1 test suite):** prefix invariance; impulse fills exactly at
t+1; hand-computed accounting (both asset styles); cost monotonicity; slippage
always adverse; kill switch latches.

### 2.6 Evaluation context ✅ core — *"honest numbers only"*

| Object | Kind | Essence |
|---|---|---|
| `summary` metrics | service | CAGR, vol, maxDD, **raw** Sharpe (labeled raw) |
| `probabilistic_sharpe` | service | PSR — credibility given length, skew, kurtosis |
| `expected_max_sharpe` + `deflated_sharpe` | service | the luck hurdle from (n_trials, trial-SR variance) — the ledger's numbers, cumulatively |
| `sharpe_confidence_interval` | service | seeded block bootstrap |
| `WalkForwardSplit` | value | train / embargo / test folds, disjoint, forward-only |
| `Attribution` 📋 M5 | service | Brinson & factor-based, on our own books |
| `TrackRecord` 📋 T1-live | aggregate | dated, protocol-bound paper results (spec §6.2): monthly, DSR-with-trials-count, no restatements |

**Invariant:** per-period convention — deflate in periods, annualize only for
display; a Sharpe without a trials count is labeled raw.

### 2.7 Curriculum context ✅ harness — *"claims that execute"*

| Object | Kind | Essence |
|---|---|---|
| `Lesson` | entity | MyST/jupytext page; tag `[deep]`/`[integration]`/`[survey]` is a **contract** (spec-defined), not a mood |
| Book build | service | CI executes every cell, `allow_errors: false` — the no-rot gate |
| `VerificationLedger` 📋 | aggregate | per-`[deep]`-lesson: the externally checkable number it reproduces + source |

### Planned contexts (boundaries reserved)

- **Pricing** 📋 M4/M6 — `Curve` (bootstrapped discount factors), `CurveFitter`
  (NSS), duration/key-rate risk; `OptionPricer` (trees, BSM, Greeks), vol surface
  via QuantLib integration. Depends on: core, data.
- **Risk** 📋 M5 — `RiskModel` (exposures → factor covariance → specific risk),
  VaR/ES + their backtests, stress scenarios. Depends on: core, data, portfolio.
- **Markets** 📋 M7 — macro context data (FRED), efficiency-evidence utilities.

---

## 3. Package architecture & the dependency law

```
quantropy/
  core/        ✅ conventions & numerics: returns, tvm            → (nothing internal)
  data/        ✅ model, pit, store, universe, providers/         → core
  research/    ✅ signals, registry (ledger)                      → core
  portfolio/   ✅ sizing, combine        [M5: covariance, optim]  → core
  evaluation/  ✅ metrics, robustness    [M5: attribution]        → core
  backtest/    ✅ venue, limits, engine                           → core, data, research, portfolio
  valuation/   🔜 M3 statements, models, scores                   → core, data
  pricing/     📋 M4/M6 curves, options                           → core, data
  risk/        📋 M5 var, factor model, stress                    → core, data, portfolio
  live/        ✅ ibkr                   [M8: runner, reconcile]  → core, data, backtest
curriculum/    ✅ the executable book (imports anything — it teaches everything)
examples/      ✅ entry points (imports anything)
legacy/        archived; imported by nothing, ever
```

**The law:** arrows point strictly down the table; `research` never imports
`backtest` or `live` (signals can't know about execution); `evaluation` judges
results without depending on how they were produced; `live` reuses the backtest's
venue contract and limits, never the reverse. **Enforced by
`tests/test_architecture.py`**, which parses every module's imports and fails the
build on a violation — the diagram above cannot silently rot.

Dependency *cheat-sheet for extension*: a new capability asks two questions —
*what data does it consume?* (→ below data) and *who consumes it?* (→ above it).
Valuation consumes data and is consumed by research (scores-as-signals) via plain
values, not imports — Research reads score *series*, not the valuation package.

---

## 4. Contracts (the six Protocols that hold the system together)

| Contract | Signature | Implementations |
|---|---|---|
| `Signal` | `target(history: Series) -> float` | MACross ✅, TSMOM ✅, factor signals 🔜 |
| `Sizer` | `scale(raw, history) -> float` | VolatilityTarget ✅, Kelly-fraction 📋 |
| `Venue` | `execute(Order, market_price) -> Fill` | SimulatedVenue ✅, IBKRVenue ✅ |
| Provider (informal) | `fetch_*(...) -> dict[str, DataFrame]` | yahoo ✅, stooq ✅, EDGAR ✅, FRED 📋 |
| Store | `write(id, datasets) / read(id, name)` | SnapshotStore ✅ (ArcticDB is the industrial analogue) |
| Ledger | `register / log_trial / n_trials / trial_sharpe_variance` | TrialsLedger ✅ (MLflow is the industrial analogue) |

Contracts are `typing.Protocol`s — structural, no inheritance required; a test
double is any object with the right method.

---

## 5. The two flows (and why they're one)

```
RESEARCH LOOP (offline, reproducible)
Provider ──fetch once──▶ Snapshot ──▶ prices
                                        │
     Hypothesis ──registered BEFORE──▶  │
                                        ▼
              ┌────────── decision path ──────────┐
              │ Signal → Sizer → RiskLimits → Order│
              └───────────────┬────────────────---┘
                              ▼
                Engine + SimulatedVenue  ──▶ BacktestResult
                              │
                              ▼
        metrics (raw) → Trial logged → DSR(ledger.n_trials, ledger.var)
                              │
                              ▼
                    walk-forward, bootstrap CI → verdict

LIVE LOOP (same decision path, different venue)
Snapshot(latest) ─▶ ┌ same Signal → Sizer → RiskLimits → Order ┐ ─▶ IBKRVenue
                    └──────────── byte-identical code ─────────┘      │
                                                                      ▼
                          reconciliation (venue.positions() vs intended)
                                                                      ▼
                          TrackRecord entry (protocol-bound, §6.2)
```

The boxed decision path is the same objects, the same code. That is the
architecture's central claim, and the reason `Venue` is the system's most
important contract.

---

## 6. State & persistence

| State | Form | Mutability |
|---|---|---|
| Market data | Parquet under `data/<snapshot_id>/` + manifest | immutable per id |
| PIT facts | records frame (persistable via snapshot) | append-only |
| Hypotheses & trials | `*.jsonl` (committed) | append-only |
| Backtest results | in-memory `BacktestResult` (reproducible from config+snapshot — results are *derived*, never stored authority) | ephemeral by design |
| Track record | dated files in-repo (M2+) | append-only, dated addenda for corrections |
| Curriculum outputs | rebuilt by CI every push | derived |

The rule of thumb: **inputs are immutable, records are append-only, derivations
are recomputed.** Nothing authoritative is ever edited in place.

---

## 7. Testing & error philosophy by layer

- **core / evaluation** — reference values (hand-derived or external) + property
  tests; money math gets adversarial cases (P2).
- **data** — semantics tests (PIT restatement scenario, immutability, traversal
  rejection) + loud provider failures: *refuse to snapshot garbage* beats
  best-effort parsing.
- **backtest / portfolio** — invariant tests: prefix invariance, hand-computed
  accounting, monotonicity, latching. New engine features must ship with the
  invariant that would catch their failure.
- **live** — code-complete flagged until exercised against a real gateway (P8);
  reconciliation is the runtime test.
- **architecture itself** — the import-law test (§3).
- Errors: raise early and specifically (`ValueError` with the *reason*), never
  return silently-degraded data; NaN in ⇒ exception, not NaN out.

---

## 8. Extension map (how each milestone lands without refactoring)

| Milestone | New code | Plugs into |
|---|---|---|
| T1-close | first paper order, MES leg | existing `IBKRVenue` (futures contract path ready) |
| M2 book | sleeve runs per instrument → `combine_sleeves` → book result; factor-research toolkit (sorts, Fama-MacBeth) in `research/` | existing engine per sleeve; ledger; DSR |
| M3 valuation | `valuation/` package (statements→models→scores) | reads data/PIT; emits score series research consumes as values |
| M4 fixed income | `pricing/curves` (bootstrap, NSS, duration) | reads Treasury/FRED provider (new, trivial) |
| M5 portfolio+risk | `portfolio/covariance`, `portfolio/optimizers`, `risk/` | optimizers consume covariance; risk consumes book results |
| M6 derivatives | `pricing/options` + QuantLib integration lessons | curriculum-heavy; core code is teaching-grade BSM/trees |
| M8 live ops | `live/runner` (scheduled decision loop), `live/reconcile`, track-record publisher | wraps the existing decision path; venue untouched |

Every row adds a package or module *below* an existing consumer or *above* an
existing input — no row moves existing code. That's the test of the boundaries
drawn in §2.
