# The Quantropy Curriculum

> An applied program in quantitative finance, taught *through working code*. Twelve
> modules in learner order — each concept has exactly one home, every lesson executes
> in CI against the `quantropy` library, and depth is a contract, not an adjective.

---

## 1. What "depth" means here (the lesson contract)

Every lesson carries one tag, with **operational** requirements — a lesson that
doesn't meet them doesn't get the tag:

| Tag | A lesson earns it only if it… |
|---|---|
| **`[deep]`** | implements the concept **from first principles in `quantropy`**, runs on **real (snapshot-pinned) data**, **reproduces an externally checkable number** (a filing figure, a published result, a textbook value), and ends with failure modes + exercises. |
| **`[integration]`** | drives a **mature external library** (e.g. QuantLib) on real or realistic data, teaches the concept through it, and states honestly what retail data cannot support. |
| **`[survey]`** | explains the concept with a small illustration and routes to the literature. Explicitly labeled a survey — never dressed up as more. |

Every lesson opens with **learning outcomes** ("after this you can …") and closes with
**pitfalls** (where the method breaks) and **exercises with solutions**. Every claim
cites `docs/REFERENCES.md`. All code cells execute in CI on every build — a broken
example fails the build, so nothing in the book can rot.

**One-home rule:** each concept is taught in exactly one module and *referenced*
everywhere else. The map in §3 states the home of the historically homeless concepts
(validation, leakage, GARCH, behavioral finance).

---

## 2. Honest status — claim never outruns artifact

The curriculum ships module-by-module as the underlying capability lands (it is each
milestone's definition-of-done). Today:

| Module | Status |
|---|---|
| M0 Orientation | ✅ published, executing in CI |
| M2 Data & Point-in-Time (2 lessons: PIT/survivorship/snapshots; EDGAR filings) | ✅ published, executing in CI |
| M1, M3–M11 | 📋 designed below, not yet written — they arrive with their capability |

Everything below the line in §4 is a **syllabus**, not a promise of existing content.

---

## 3. The one-home map (MECE anchors)

Concepts that plausibly belong in several places, assigned one home:

| Concept | Home | Everyone else |
|---|---|---|
| Leakage, look-ahead, PIT discipline (data side) | **M2** | referenced by M8, M9 |
| Causal feature contract (transform side) | **M8** | referenced by M9 |
| Multiple testing, deflated/haircut Sharpe, PBO, purged CV, trials ledger, research protocol | **M8** (single home for the entire overfitting discipline) | M9 references; never re-taught |
| Volatility models (EWMA, GARCH) | **M1** (methods live once) | applied in M6, M7 |
| Optimization, Monte Carlo, PDE/lattice methods | **M1** | applied in M5, M6 |
| Behavioral finance — biases in **markets** (why premia/anomalies persist) | **M4** | — |
| Behavioral finance — biases in **researchers** (why backtests lie to their authors) | **M8** | — |
| Backtest **mechanics** (engines, fills, costs, corporate actions) | **M9** | uses M8's statistics, doesn't restate them |
| Covariance estimation | **M6** | M7 consumes |
| Live risk limits & circuit breakers (enforcement) | **M11** | M7 measures, M11 enforces |

---

## 4. The program — twelve modules in learner order

Ordering is pedagogical (each module uses only what came before), not architectural.

**M0 — Orientation** `[deep]` ✅
What quants do; the honesty labels; compounding and the asymmetry of loss; run your
first Quantropy code. *Outcome: you can execute and modify every example in this book.*

**M1 — Quantitative foundations**
Probability and distributions for returns; statistics & inference (and the bootstrap);
time-series basics through volatility models (EWMA, GARCH); stochastic processes (GBM,
mean reversion, jumps) and simulation; optimization; numerical methods (roots,
interpolation, trees/PDE at survey depth). *Outcome: you can simulate, estimate, and
test the building blocks every later module assumes.* Mostly `[deep]`.

**M2 — Markets, instruments & data** ✅ (2 of ~4 lessons)
Instruments and conventions (calendars, day count, contract specs); the data problem:
survivorship, restatements, point-in-time storage, immutable snapshots; filings
ingestion (SEC EDGAR — natively bitemporal). *Outcome: you can build a
reproducible, PIT-clean dataset and demonstrate — in code — two ways naive data
inflates a backtest.* `[deep]`.

**M3 — Fundamental analysis & equity valuation**
Financial statements to ratios; cost of capital; DCF (FCFF/FCFE), residual income,
multiples; **reverse DCF** (reading expectations out of price); distress/fraud/quality
scores (Altman, Beneish, Piotroski); PIT-clean fundamental data from M2. *Outcome: you
can value a real company from its real filings and defend every input.* `[deep]` —
values reproduce against actual filing figures.

**M4 — Asset pricing & the cross-section**
CAPM and its empirical failure; the factor program (size, value, momentum, quality,
low-vol, carry); **the three meanings of "factor"** (pricing vs alpha vs risk — kept
distinct from here on); why premia persist (risk vs behavioral vs limits-to-arbitrage);
the factor zoo and the replication crisis. *Outcome: you can construct a factor from
raw data, run the standard asset-pricing tests, and argue both sides of "is this
real?".* `[deep]` on equity factors.

**M5 — Derivatives & volatility** `[integration]` (QuantLib) + `[survey]`
Payoffs and no-arbitrage; Black-Scholes assumptions *and their failure modes*; Greeks;
implied vol and the surface; rates/credit instruments at survey depth; where XVA and
exotics live in practice and why we don't pretend to trade them. *Outcome: you can
price and risk a vanilla option book with QuantLib and explain every number.*

**M6 — Portfolio construction**
The covariance problem first (sample error → shrinkage → factor structure); why naive
mean-variance is an error maximizer; robust construction (Black-Litterman, risk
parity, HRP); position sizing (volatility targeting, fractional Kelly); costs and
turnover as first-class constraints. *Outcome: you can take signals + covariance to
defensible weights and show why the naive route fails out-of-sample.* `[deep]`.

**M7 — Risk measurement & management**
Sensitivities and scenario P&L; VaR/ES done properly (and backtested); factor risk
models for portfolios; stress testing and crisis correlations; drawdown dynamics.
*Outcome: you can produce and interpret a full risk report on a real portfolio.*
`[deep]` on equity/futures books.

**M8 — Strategy research & the overfitting problem** ← *the program's core*
The economics of an edge; signal construction and the causal feature contract;
**the single home of research honesty**: multiple testing, deflated & haircut Sharpe,
PBO, walk-forward and purged CV, the trials ledger, pre-registration, and the
researcher's own biases; the classic signal families (trend, cross-sectional momentum,
value, carry, mean reversion) built and *honestly* evaluated. *Outcome: you can take a
hypothesis to a verdict that survives adversarial scrutiny — and show your trials
count.* `[deep]` — this module is the project's reason to exist.

**M9 — Backtesting mechanics**
Event-driven simulation; where look-ahead hides in an *engine* (fill timing, signal
lags); cost, financing, and corporate-action modeling; sim-vs-live divergences
(partial fills, rejects) and how to stress them. Uses M8's statistics; owns none of
them. *Outcome: you can explain — and test for — every way an engine flatters a
strategy.* `[deep]`.

**M10 — Execution & microstructure** `[survey]`/`[integration]`
Order books and price formation; market impact and why costs scale with size; optimal
execution (Almgren-Chriss) in simulation; TCA. Honest scope: no retail L2 data — taught
via models and simulation, labeled as such. *Outcome: you can reason about what your
trading costs and capacity actually are.*

**M11 — Live trading & operations**
Paper/live trading through the same code path as the backtest; order management and
broker-resident stops; live risk limits and drawdown circuit breakers; reconciliation;
**strategy decay** — monitoring live vs backtest and deciding when to kill. *Outcome:
you can run a strategy live-paper with enforced limits and an honest track record.*
`[deep]`.

**Capstones** (close the program; one per depth track)
A. a systematic multi-signal book: research → gates → backtest → paper-live with a
public, honestly-evaluated track record; B. a full fundamental valuation defended
end-to-end from filings; C. an options book priced and risk-managed via integration;
D. an ML/alt-data signal that either survives M8's gates or gets an honest post-mortem.

---

## 5. Mechanics

Executable **Jupyter Book** (MyST + jupytext; clean diffs, downloadable notebooks).
CI builds with `execute: force`, `allow_errors: false` — the no-rot gate. Lessons pin
data snapshots (M2 machinery) so outputs are deterministic. Reference lookups:
`docs/REFERENCES.md`, organized to match these modules.
