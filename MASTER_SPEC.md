# Quantropy — Master Specification

> **An applied quant curriculum backed by a focused, genuinely-deep reference
> implementation.** The teaching is the product. The code is *deep and finished* where
> real data and real depth are reachable (systematic trading, fundamental equity
> valuation, and the rigor spine under them), and *illustrative* — wrapping best-in-class
> libraries — everywhere else. Built to be finished, correct, honest, and demonstrable —
> not to imitate a quant shop.

**Status:** v1.0 — refocused after an adversarial review. Supersedes the maximalist v0.3
(in git history). The change: **build narrow and deep where data allows; teach broad and
honest everywhere; integrate open source instead of reinventing it.**
**Owner:** Alain Daccache
**Goal:** a portfolio that gets its author hired as a quant — which means *finished,
deep, correct, and well-taught*, not sprawling and unfinished.

---

## 0. What this is — and what it is not

**It is:** (1) an **executable curriculum** teaching the quant body of knowledge applied;
(2) a **focused reference implementation** that is genuinely deep in two data-feasible
tracks; (3) a demonstration of **research rigor** (anti-overfit, point-in-time,
sim/live-parity) and a **real paper-traded track record**.

**It is not:** a quant shop, a product/platform business, a QuantLib/pysystemtrade
replacement, or a from-scratch rebuild of every asset class. We reached for that in v0.3
and an honest review killed it: it's undeliverable solo, it reinvents mature open source
with no edge, and half of it can't run on retail data. Ambition now lives in the
*curriculum's breadth*, not in reinvented software.

### The prime directive: integrate, don't reinvent
Where a mature, correct library exists, **use it** and add what it lacks (integration,
rigor, teaching). Reinventing a primitive is only justified when the *point is to teach
it from first principles* — and even then it's a lesson, not production code.

| Need | Use (don't rebuild) | We add |
|---|---|---|
| Derivatives pricing, curves, vol | **QuantLib** (via `QuantLib-Python`) | teaching, honest data caveats, integration |
| Vectorized backtests / analytics | **vectorbt**, ffn/empyrical | our no-look-ahead event engine + parity |
| Portfolio optimization baselines | **PyPortfolioOpt**, **Riskfolio-Lib** | robust-covariance defaults, our allocation layer |
| Systematic framework prior art | **pysystemtrade** patterns | curriculum + our own clean vertical |
| Econometrics (GARCH, coint.) | **statsmodels**, **arch** | applied lessons, signal integration |
| ML / NLP | **scikit-learn, torch, transformers** | anti-overfit gates, finance features |
| Filings data | **EDGAR** (free) | PIT ingestion, valuation engine |

---

## 1. The two scopes

### 1.1 BUILD scope — narrow, deep, data-feasible, finished
Only where **real data is available** and **real depth is reachable solo**:

- **Core spine** *(supports everything)* — numerics we actually need (optimization,
  Monte Carlo, interpolation, time-series/GARCH via `arch`), conventions (calendars,
  returns, TVM), data layer with **point-in-time** integrity and versioned snapshots.
- **Track A — Systematic trading** *(flagship; data-feasible on keyless equities/futures;
  meridian head start)* — full research→signal→portfolio→backtest→evaluation→**paper
  trade** loop, with a **real, honestly-evaluated track record**.
- **Track B — Fundamental equity valuation** *(free EDGAR data; v3 head start)* — DCF /
  reverse-DCF / archetypes / quality-distress scores, point-in-time clean.
- **The rigor stack** *(the differentiator)* — no-look-ahead engine, deflated/probabilistic
  Sharpe, PBO, walk-forward/purged CV, robust covariance, acceptance gates, trials ledger.
- **ML/NLP-alpha showcase** *(one, done right)* — an ML or filings-NLP signal whose
  purpose is to **pass the same anti-overfit gates** as a classical one (or an honest
  write-up of why it didn't).
- **Equity/portfolio risk** *(data-feasible slice of risk-quant)* — VaR/ES, a factor risk
  model on equities, drawdown/exposure.

### 1.2 TEACH scope — broad, honest, integrative
The **curriculum** (`docs/CURRICULUM.md`) covers the *whole field* (the §3 atlas). Each
lesson is honestly labeled:
- **Deep** — runs real data against our own implementation (the BUILD tracks).
- **Applied-via-integration** — teaches a topic by driving a mature library (e.g. pricing
  a swaption with QuantLib), with honest notes on the retail data gap.
- **Survey** — concept + small synthetic illustration + references, where neither our code
  nor free data supports a full treatment (deep derivatives, HFT microstructure).

Breadth is *cheap and valuable in a curriculum* and *ruinous as reinvented software* —
so it lives here, not in the BUILD scope.

---

## 2. Principles (non-negotiable)

- **P1 — Finished beats broad.** A smaller thing, done and demonstrable, always wins.
- **P2 — Correctness, tiered.** Money/sizing/risk code gets adversarial reference tests;
  the rest, proportionate. Every BUILD formula is tested.
- **P3 — No look-ahead, both classes.** Engine owns fill lag; a causal point-in-time
  **feature contract** governs in-sample leakage (as-reported data; trailing-only
  transforms).
- **P4 — Anti-overfit by default.** Deflated/probabilistic Sharpe, walk-forward/purged CV,
  a **cumulative trials ledger**, acceptance gates — on by default, taught explicitly.
- **P5 — Reproducible incl. data.** Deterministic given a seed; core network-free;
  backtests on versioned snapshots.
- **P6 — Sim/live code-path parity, modelled divergences.** One code path; the sim venue
  injects frictions (partial fills/rejects/latency). Interface parity, *not* assumed
  behavioral equality.
- **P7 — Integrate, don't reinvent** (§0).
- **P8 — Honest labels.** Every capability is `[deep]`, `[integration]`, or `[survey]`;
  every trading claim is `[paper]` or `[backtest]`. Never fake depth or a track record.
- **P9 — Secrets via env only.** Curriculum executes in CI so nothing rots (NFR: a broken
  lesson fails the build).
- **P10 — Start simple, refactor when it hurts.** No speculative architecture; earn each
  abstraction.

---

## 3. The field atlas (the complete map — this is CURRICULUM scope, not BUILD scope)

The full taxonomy is retained **as the curriculum's map and a knowledge reference**, not
as a build backlog. Two axes: capability × asset class. Each leaf is a *lesson*, tagged
`[deep]` / `[integration]` / `[survey]`.

**Capabilities:** C1 Foundations (math, numerics, stochastic calculus, ML core) · C2 Data
& PIT · C3 Instruments · C4 Pricing & valuation · C5 Risk · C6 Alpha & strategy · C7
Portfolio construction · C8 Backtesting · C9 Evaluation/robustness · C10 Execution &
microstructure · C11 Live/ops · C12 Research governance · C13 Platform/reporting.

**Asset classes:** Equity · Rates · Credit · FX · Commodity · Vol/Derivatives ·
Multi-asset/Macro · (Crypto — survey only).

**Where BUILD lands on the atlas** (everything else is `[integration]` or `[survey]` in
the curriculum):

| | Equity | Rates | Credit | FX | Vol/Deriv |
|---|---|---|---|---|---|
| C4 Pricing | **[deep]** DCF/reverse-DCF | [integration] QuantLib | [survey] | [integration] | [integration] QuantLib |
| C5 Risk | **[deep]** VaR/factor-model | [survey] | [survey] | [survey] | [integration] |
| C6 Alpha | **[deep]** premia+statarb+ML | [survey] | [survey] | [integration] | [survey] |
| C7/C8/C9 | **[deep]** (asset-agnostic spine) | | | | |
| C10 Execution | [integration]/[survey] | — | — | — | — |

The three MECE clarifications from v0.3 still hold and are taught explicitly: the **three
meanings of "factor"** (pricing/alpha/risk), the **five disjoint risk concerns**, and
**methods living once** in C1.

---

## 4. Architecture (deliberately modest)

Start as a **small, clean package** — not a 13-package cathedral. Grow structure only when
a module actually earns it (P10).

```
quantropy/
  core/        # numerics we need, conventions, stats, timeseries (arch/statsmodels)
  data/        # providers (keyless + EDGAR), PIT store, snapshots, quality
  research/    # signals, features, the signal lab, hypothesis registry + trials ledger
  portfolio/   # sizing, robust-covariance optimization (wraps PyPortfolioOpt), allocation
  backtest/    # event-driven engine (no-look-ahead) + costs + venue Protocol
  evaluation/  # deflated/probabilistic Sharpe, PBO, walk-forward, gates, tearsheets
  valuation/   # fundamentals: statements, DCF/reverse-DCF, archetypes, scores (Track B)
  live/        # IBKR paper/live venue, risk limits, reconciliation
legacy/        # archived matilda (harvest source)
```

Derivatives/rates/credit teaching drives **QuantLib** from curriculum notebooks — no
`quantropy` pricing package until (if ever) there's real data and a reason. Extras:
`[data] [live] [ml] [report] [dev]`. Core stays network-free & deterministic.

**Key contracts:** `Panel` · `Instrument` · `Signal` (pure, causal) · `Venue` (Protocol;
sim/live seam) · `BacktestConfig` (seeded, snapshot-pinned).

---

## 5. Reuse map

| Target | Port from | Action |
|---|---|---|
| `backtest`, `research` signals, `portfolio` sizing/allocation, `evaluation` stack | **meridian** | Port as Track A backbone — the best-engineered asset here. |
| `valuation` (reverse-DCF, archetypes), EDGAR ingest, PIT forecast backtesting | **v3_bearing_standard** | Port as Track B. |
| Selected formulas (Black-Scholes as a *teaching* lesson, VaR, ratios, Altman/Beneish, FF factors) | **matilda** | Harvest formula-by-formula *only where used*; verify + test. Most of matilda stays in `legacy/`. |
| Governance (registry, trials ledger), deflated Sharpe/PBO, continuous contracts | **futures-quant** spec | Port methodology → tooling + curriculum. |

**Discard / do-not-build:** the maximalist rates/credit/XVA/exotics/microstructure *code*
(teach via QuantLib/simulation instead), the product/platform/API business, matilda's
Flask app + import-time Mongo + **hardcoded secrets (rotate the exposed Atlas/AlphaVantage/
FRED creds now)** + 2020 pins.

---

## 6. Milestones (realistic, standalone-valuable, data-feasible)

Each milestone ends in something **finished and demonstrable**, and (from M2) ships its
curriculum course as definition-of-done. Rough solo effort in brackets — honesty about
cost is part of the plan.

- **M0 — Foundations, scaffolding & the book [2–3 wks].** Small package skeleton, modern
  deps, secrets hygiene, `legacy/` move; `core` (conventions, the numerics we need); the
  **Jupyter Book + CI-execution harness** with Course 0. *Exit:* clean install, core
  tested, book builds & executes in CI.
- **M1 — Data & PIT [2–4 wks].** Keyless equities/futures + EDGAR ingestion, versioned
  snapshots, survivorship-free universe, point-in-time store. *Exit:* reproducible offline
  `Panel`; PIT query tested; C2 course green.
- **⭐ T1 — Thin thread to first paper trade [2–3 wks].** One toy signal → sizing →
  event-driven backtest → `SimulatedVenue` → **IBKR paper** → one risk limit. Equity first,
  then a micro future. *Exit:* costed backtest + live paper orders through one code path;
  parity + risk-limit tests green.
- **M2 — Track A: systematic trading, deep [6–10 wks].** Full research→signal→portfolio→
  backtest→evaluation loop; a real multi-signal book; the anti-overfit stack; **begin a
  live paper track record**. *Exit:* a book with deflated Sharpe + walk-forward, paper-
  trading live; C6/C8/C9 courses green.
- **M3 — Track B: fundamental equity valuation, deep [4–6 wks].** DCF/reverse-DCF/
  archetypes/scores from EDGAR, PIT-clean. *Exit:* PIT-clean valuation of a real company;
  C4-equity course green.
- **M4 — ML/NLP-alpha showcase [3–5 wks].** One ML or filings-NLP signal through the *same*
  gates. *Exit:* the signal passes (or an honest post-mortem); C6-ML course green.
- **M5 — Equity/portfolio risk + optimization polish [3–4 wks].** VaR/ES, a factor risk
  model on equities, robust-covariance optimization (wrapping PyPortfolioOpt). *Exit:* full
  risk report on the Track-A book; C5/C7 courses green.
- **M6 — Curriculum breadth pass [ongoing].** Author the `[integration]` (QuantLib
  derivatives/rates) and `[survey]` (credit/XVA/microstructure) courses. *Exit:* the whole
  atlas has at least a survey lesson; book is complete-breadth, honest-depth.
- **M7 — Platform-lite & polish [2–3 wks].** Tearsheets, a thin local dashboard/report,
  strategy-decay monitoring, README/portfolio landing. *Exit:* the repo reads as finished.

**Graph:** M0 → M1 → **T1** → M2 → { M3, M4, M5 } → M6 (rolling) → M7. Realistic
end-to-end: a finished, deep, paper-traded, well-taught portfolio — not a stub farm.

---

## 7. Locked decisions

1. **Reframe:** applied curriculum + focused deep implementation; *not* a platform/shop.
2. **Integrate, don't reinvent** — wrap QuantLib/PyPortfolioOpt/vectorbt/statsmodels/arch.
3. **BUILD deep:** systematic (Track A) + fundamentals (Track B) + the rigor spine + an
   ML showcase + equity risk. **TEACH broad:** the whole field, honestly labeled.
4. **Data:** keyless equities/futures + free EDGAR; PIT via versioned Parquet snapshots.
5. **Broker:** IBKR paper/live; T1 equity-first then micro future.
6. **Curriculum:** executable Jupyter Book, CI-tested, per-milestone; `[deep]`/
   `[integration]`/`[survey]` tags.
7. **Home:** rebuild in place under `Quantropy`; old code → `legacy/`.

---

## 8. First concrete step

**M0**: stand up the small `quantropy` package + `core`, wire modern deps + secrets
hygiene, move old code to `legacy/`, and stand up the **Jupyter Book + CI-execution
harness** with Course 0 and one runnable "hello, PIT data" lesson. That gives a clean,
tested trunk *and* the teaching machine, before there's much to teach — so nothing rots
and every later milestone has a home for its lesson.

*Companion docs:* `docs/CURRICULUM.md` (the syllabus, deep/integration/survey) and
`docs/REFERENCES.md` (the verified canon behind every lesson).
