# The Quantropy Quant Curriculum — *A CFA Program for Quants*

> A complete, applied curriculum that teaches the entire quant body of knowledge — *deep*
> where our own code and real data reach (systematic trading, fundamental valuation, the
> rigor spine), *by integration* where a mature library is the right tool (QuantLib for
> derivatives), *survey-level* where retail data can't support more (deep rates/credit,
> HFT). Not a textbook rewrite — an *applied bridge*: concept → code → run → interpret →
> where it breaks → the honest caveat. Every lesson executes in CI, so nothing rots. Each
> lesson is tagged `[deep]` / `[integration]` / `[survey]` so depth is never faked.

**Format:** an executable **Jupyter Book** (MyST Markdown, jupytext-paired for clean
diffs), built to a searchable website + PDF, with BibTeX citations wired to
`docs/REFERENCES.md` and "launch in Colab/Binder" buttons.
**Status:** syllabus (this file). Lessons are authored per-milestone as each capability
lands (definition-of-done, MASTER_SPEC §5 / NFR9).

---

## 1. Design principles

1. **Applied-first, theory-referenced.** We don't re-derive Hull or Shreve — they did it
   better. We *reference* the derivation (REFERENCES.md) and spend our pages on the part
   nobody else provides: making it real in code, running it, interpreting the number,
   and showing where it breaks.
2. **Honest depth, not fake breadth.** Breadth is the *curriculum's* job, but depth is
   tiered by what real (retail) data and our own code support. Every lesson is labeled:
   - **`[deep]`** — runs real data against *our* implementation (systematic trading,
     fundamental valuation, the rigor spine). Full working depth.
   - **`[integration]`** — teaches a topic by driving a mature library (e.g. price a
     swaption with **QuantLib**), with an honest note on the retail data gap. We
     *integrate, don't reinvent* (MASTER_SPEC §0).
   - **`[survey]`** — concept + small synthetic illustration + references, where neither
     our code nor free data supports a full treatment (deep rates/credit/XVA, HFT
     microstructure). Honest about being a survey.
   No fake toy examples dressed up as production depth — a sharp reader sees through them.
3. **Honest by construction.** Every lesson ends with pitfalls and the anti-overfit /
   point-in-time caveat. We teach *why most backtests lie* as rigorously as the methods.
4. **Executable & reproducible.** Code runs on a pinned data snapshot; CI executes every
   cell; a broken example fails the build. Outputs are deterministic (seeded).
5. **Teaching is the acceptance test.** If a `[deep]` capability is hard to teach cleanly,
   the API is wrong. Writing the lesson validates the software.

### Diátaxis positioning
This curriculum is the **tutorials + explanation** quadrants. It is *distinct* from:
- **How-to guides** → `examples/` (task recipes),
- **Reference** → auto-generated API docs (Sphinx autodoc; never hand-written),
- so the program reads as a program, not a blog.

---

## 2. Tooling & mechanics

- **Jupyter Book** builds the site/PDF and executes content (`jupyter-book build --execute`).
- **MyST Markdown + jupytext pairing** — lessons are `.md` (reviewable diffs) that execute
  as notebooks; readers can download the `.ipynb` or launch Colab/Binder.
- **CI gate** — a GitHub Action runs the full book with execution on every push; failure
  blocks merge. This is the no-rot guarantee (NFR9).
- **Pinned data snapshot** — lessons read a versioned snapshot (MASTER_SPEC NFR2), so
  outputs never drift.
- **Citations** — `{cite}` directives resolve against `references.bib` (generated from
  `docs/REFERENCES.md`), so every claim links to a verified source.

### The lesson template (every lesson follows it)
```
1. Learning objectives   — LOS-style: "after this you can…"
2. Intuition             — the concept in plain words
3. The math              — compact; {cite} REFERENCES, don't re-derive
4. Applied               — build & run with Quantropy on pinned real data
5. Interpret             — what the number means, with plots
6. Pitfalls              — where it breaks; anti-overfit / PIT caveat
7. Exercises             — 2–3 problems, with worked solutions
8. Further reading       — REFERENCES.md links
```

### Assessment (the "program" part)
- **LOS** (learning outcome statements) open each lesson.
- **Exercises** with solutions close each lesson.
- **Capstones** close each Level — integrative, end-to-end projects (below).
- Optional **self-check quizzes** per course.

---

## 3. Structure — three CFA-style levels

The curriculum mirrors the platform's capability taxonomy (C1–C13). Courses are grouped
into three levels of increasing integration, echoing the CFA I/II/III progression.

- **Level I — Foundations & Tools** (the building blocks; maps to M0–M1)
- **Level II — Discipline Depth** (deep single-discipline mastery across asset classes;
  maps to M2–M8)
- **Level III — Integration & Practice** (synthesis, live, governance, capstones; M8–M9)

---

## Level I — Foundations & Tools

**Course 0 — Orientation.** What a quant does; the quant archetypes (buy-side
systematic, sell-side derivatives, risk, ML, execution); how to use this book and the
library; the reproducibility / point-in-time discipline.

**Course C1 — Quant Foundations** *(math, stats, numerical methods, ML core)*
- Probability & random variables for finance
- Stochastic processes: random walks, Brownian motion, Itô's lemma (simulate & visualize)
- SDEs & key processes: GBM, Ornstein-Uhlenbeck (mean reversion), Merton jump-diffusion
- Monte Carlo: sampling, variance reduction, quasi-MC, convergence diagnostics
- Numerical methods: root-finding, interpolation, **finite-difference PDE**, binomial/
  trinomial trees
- Optimization: convex, quadratic, constrained; using the solvers
- **Automatic/adjoint differentiation (AAD)** for fast, exact Greeks
- Linear algebra & PCA for finance
- Statistics & inference; hypothesis testing; the bootstrap
- Time series: stationarity, autocorrelation, AR/MA/ARIMA
- Volatility modeling: EWMA and **GARCH**
- State-space models & the **Kalman filter**
- Return algebra & conventions (simple vs log, annualization); time value of money
- ML core: the pipeline, train/validate/test, **leakage & cross-validation done right**

**Course C2 — Data & Infrastructure**
- The data landscape: market, reference, fundamental/filings, macro, alternative
- Cleaning: adjustments, corporate actions, gap handling
- **Survivorship bias & point-in-time data — why backtests lie**
- Continuous-contract construction (the Panama roll)
- Storage, versioned snapshots, reproducibility
- Building a data pipeline with Quantropy end-to-end

**Course C3 — Instruments & Market Conventions**
- Equities & ETFs; futures (specs, multipliers, roll); options
- Bonds & swaps; FX; credit (CDS)
- Quoting, settlement, day-count, calendars — the plumbing that trips everyone

**Capstone I —** *Build a reproducible, point-in-time data pipeline and instrument a
survivorship-free universe; demonstrate a look-ahead bug and then fix it.*

---

## Level II — Discipline Depth

**Course C4 — Pricing & Valuation** *(Equity = `[deep]`, our engine; Rates/FX/Options =
`[integration]` via QuantLib; Credit/exotics/XVA = `[survey]` — retail data can't support
full depth, and we don't reinvent QuantLib)*
- **Equity `[deep]`:** financial statements & ratios; DCF (FCFF/FCFE); DDM; **residual income**;
  multiples/comps; **reverse-DCF & expectations investing**; archetypes (sum-of-parts,
  serial acquirer); cost of capital (WACC/CAPM); distress (**Altman Z**), fraud
  (**Beneish M**), quality (**Piotroski F**)
- **Fixed income:** bond math; **yield-curve bootstrapping**; multi-curve / **OIS**
  discounting; duration/convexity/DV01; spreads & OAS
- **Rates derivatives:** short-rate models (Vasicek/CIR/**Hull-White**); HJM; **LMM/BGM**;
  swaps, caps/floors, swaptions
- **Credit:** structural (**Merton**) & reduced-form/**hazard-rate**; **CDS** pricing;
  credit curves; portfolio credit & copulas
- **FX:** covered-interest parity & forwards; **Garman-Kohlhagen**; FX volatility
- **Options & volatility:** Black-Scholes (assumptions & failure modes); **Greeks**;
  **implied vol, smile & skew**; local vol; **SABR**; **Heston**; jump models; **vol-surface
  calibration**
- **Exotics:** barriers/Asians/lookbacks/autocallables; American/Bermudan via
  **Longstaff-Schwartz**; PDE finite-difference pricing
- **XVA:** counterparty exposure; **CVA/DVA/FVA/MVA**; collateral
- **Calibration & model risk:** fitting models to market; model validation

**Course C5 — Risk** *(by concern — the risk-quant depth track)*
- Sensitivities/Greeks & scenario P&L
- **VaR** (historical, parametric, Monte Carlo) and **ES/CVaR**; coherent measures
- **VaR backtesting** (Kupiec, Christoffersen)
- Covariance estimation: sample pitfalls → **Ledoit-Wolf shrinkage** → RMT denoising
- **Factor risk models (Barra-style):** build one; risk decomposition & attribution
- **Credit risk:** PD/LGD/EAD; portfolio credit; default correlation; concentration
- **Counterparty / XVA risk**
- Tail risk & **EVT**; stress testing & scenario design
- Model risk & validation; regulatory literacy (Basel/FRTB) *[awareness]*

**Course C6 — Alpha & Strategy Research** *(buy-side + ML depth tracks)*
- The research process, and the overfitting enemy
- Factor construction; **the three meanings of "factor"** (pricing vs alpha vs risk)
- **Risk premia:** trend/TSMOM; cross-sectional momentum; carry; value; quality;
  low-vol/defensive; seasonality; positioning (COT)
- **Statistical arbitrage:** pairs (cointegration); **PCA stat-arb**; baskets
- **Event-driven:** earnings; **merger/risk arbitrage**; index rebalancing
- **Volatility strategies:** vol-risk-premium; dispersion; term structure *[research]*
- **Macro:** cross-asset; nowcasting; regime
- **ML alpha:** features; models; leakage; deep learning for sequences (LSTM/transformers)
- **NLP alpha:** filings, news, earnings-call sentiment
- **Reinforcement learning** for execution/sizing
- Signal combination & the **signal lab** (multiple-testing-deflated screening)

**Course C7 — Portfolio Construction & Allocation**
- MPT & the efficient frontier; **why naive MVO fails** (error maximization)
- Robust construction: shrinkage, **Black-Litterman**, **entropy pooling**
- Risk-based: **risk parity**, **HRP**, min-variance, max-diversification
- Position sizing: **volatility targeting**, **Kelly & fractional Kelly**
- Constraints, turnover, **transaction-cost-aware** & tax-aware allocation
- **Dynamic/multi-period:** stochastic control (Merton problem); LDI/ALM
- **Cross-strategy allocation** (portfolio-of-strategies)
- **Performance attribution:** Brinson, factor-based, risk; the Fundamental Law (IR=IC·√B)

**Course C8 — Backtesting & Simulation**
- Vectorized vs event-driven engines; **no-look-ahead** & fill lag
- Cost, financing, corporate-action modeling
- Walk-forward, **purged/embargoed CV**, CPCV
- Building and reconciling both engines in Quantropy

**Course C9 — Evaluation & Robustness** *(the honesty layer)*
- Performance metrics; **the Sharpe ratio and its traps**
- Multiple testing: **deflated & probabilistic Sharpe**, **PBO**, MinBTL, haircut Sharpe
- Bootstrap CIs; diversification & **crisis-correlation** diagnostics; acceptance gates
- **Strategy-decay** monitoring (live vs backtest)

**Course C10 — Execution & Microstructure** *(`[survey]`/`[integration]` — no retail L2
order-book data; taught via simulation and models, honestly labeled)*
- Market microstructure: order books, price formation, adverse selection
- **Optimal execution:** Almgren-Chriss; implementation shortfall; VWAP/TWAP/POV
- **Market-impact models** (linear/square-root/propagator); **TCA**; capacity
- **Market making:** Avellaneda-Stoikov; inventory management *[research]*

**Capstone II (choose per track) —**
- *Sell-side:* price & risk-manage an options book — calibrate a vol surface, compute
  Greeks via AAD, aggregate book VaR.
- *Rates:* build a curve, price a swap & swaption, compute key-rate risk.
- *Risk:* build a factor risk model and a full multi-asset risk report with VaR backtest.
- *Buy-side/ML:* take an ML/NLP signal from raw data through the anti-overfit gates.

---

## Level III — Integration & Practice

**Course C11 — Live Trading & Operations** *(retail-limited, [live])*
- Paper trading via IBKR through the *same code path* as the backtest
- OMS, order types, broker-resident protective stops
- Real-time risk limits, the **two-tier drawdown circuit breaker**, reconciliation

**Course C12 — Research Governance & Meta** *(cross-cutting)*
- Hypothesis pre-registration; the **research protocol** (Arnott-Harvey-Markowitz)
- The cumulative **trials ledger** and why per-study deflation isn't enough
- Reproducibility & experiment tracking

**Course C13 — Platform, Reporting & Product**
- Config, secrets, scheduling, monitoring
- Tearsheets, dashboards, the local API
- HPC where it pays (vectorization, numba/GPU)

**Course B — Behavioral & Foundational** *(the humility layer, woven throughout)*
- Fooled by randomness; fat tails; biases; **why edges decay** (McLean-Pontiff)

**Level III Capstones (integrative, end-to-end):**
- **Capstone A — Systematic multi-asset book:** research → both backtests → evaluation →
  paper-trade → risk limits. The whole spine in one project.
- **Capstone B — Fundamental equity:** value a company (PIT-clean) and build a factor
  portfolio around the thesis.
- **Capstone C — Derivatives desk:** price, calibrate, and risk-manage an options/rates
  book with XVA.
- **Capstone D — ML alpha, honestly:** an ML/NLP strategy that survives deflated-Sharpe
  and walk-forward — or an honest write-up of why it didn't.

---

## 4. Course → milestone → references map

| Course | Ships in milestone | Primary references (`docs/REFERENCES.md`) |
|---|---|---|
| C1 Foundations | M0 | §5 (Shreve, Glasserman, Hamilton, Tsay), §4 (Kelly) |
| C2 Data / C3 Instruments | M1 | §1 (PIT/leakage), §3 (continuous contracts) |
| C4 Pricing — equity | M3 | §6 (Damodaran, Penman, scores) |
| C4 Pricing — derivatives/rates/credit/XVA | M4 | §5 (+ supplemental: Brigo-Mercurio, Gregory) |
| C5 Risk | M5 | §4 (Ledoit-Wolf, Jorion, ADEH, Rockafellar-Uryasev) |
| C6 Alpha — systematic | M2 | §2 (factors/premia), §3 (Carver, Chan, Clenow) |
| C6 Alpha — ML/NLP/RL | M6 | §1 (López de Prado), + supplemental ML |
| C7 Portfolio | M7 | §4 (Markowitz→HRP, Roncalli, Grinold-Kahn) |
| C8 Backtest / C9 Evaluation | M2, M8 | §1 (deflated Sharpe, PBO, protocol) |
| C10 Execution | M8 | §3 (Johnson, Harris), + supplemental (Almgren-Chriss) |
| C11/C12/C13 + capstones | M8–M9 | §1, §7 (behavioral) |

*Note:* the derivatives, XVA, execution, and ML rows depend on the **supplemental
references pass** (rates/credit/microstructure/ML canon) flagged in the spec — those
sources should land before those courses are authored.

---

## 5. How it grows (the anti-scope-explosion plan)

- **One course per milestone**, authored as that capability lands — never ahead (would be
  vaporware), never behind (would rot).
- **The book + CI harness is stood up in M0** (empty shell + one Course-0 lesson), so the
  machine exists before there's much to teach.
- **Depth tracks first:** C4/C5/C6-ML courses (the differentiators) get the richest
  treatment; agnostic plumbing courses stay lean.
- **The lesson is the integration test.** Authoring is not overhead — it's how we prove
  each capability is correct and usable.
