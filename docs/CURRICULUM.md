# The Quantropy Curriculum

> The complete working knowledge of a quantitative researcher and portfolio manager,
> as an executable program. Nine parts, ~60 lessons, every concept in exactly one
> place, every lesson tagged by an operational depth contract, every claim cited,
> every code cell executed in CI. Completeness is audited against the CFA Body of
> Knowledge, the FRM curriculum, the graduate canon, and the production function of
> a quantitative fund (MASTER_SPEC §2) — not against anyone's taste.

---

## 1. The lesson contract

| Tag | A lesson earns it only if it… |
|---|---|
| **`[deep]`** | implements the concept from first principles in `quantropy`, runs on real snapshot-pinned data, **reproduces an externally checkable number**, and ends with failure modes + exercises. *Mechanism carve-out:* where the subject is the machinery itself (engine invariants, inference statistics), synthetic data with controlled ground truth satisfies verification — the "external number" is an analytic truth the reader can derive. Never applies to lessons about markets. |
| **`[integration]`** | teaches by driving a mature library (QuantLib, statsmodels/arch, PyPortfolioOpt, scikit-learn) on real data, stating what free data cannot support. |
| **`[survey]`** | concept + small illustration + routed references; labeled as such, never dressed up. |

Every lesson: learning outcomes first; pitfalls and solved exercises last; citations
into `docs/REFERENCES.md`. **One-home rule:** every concept is taught once and
referenced elsewhere (§3).

## 2. Honest status

| Shipped | Status |
|---|---|
| I.1 Orientation; I.4–I.5 (PIT & survivorship; EDGAR filings) | ✅ executing in CI |
| Everything else | 📋 syllabus; ships with its milestone (MASTER_SPEC §6) |

### 2.1 Coverage ledger — the one-page audit

Every field area (MASTER_SPEC §2) → depth, curriculum home, reference section.
What's *not* here is priced in `docs/BOUNDARIES.md`; the hardest objections are
pre-answered in `docs/SCRUTINY.md`.

| # | Field area | Depth | Curriculum | References |
|---|---|---|---|---|
| 1 | Returns, TVM, conventions | deep | I.1–.3 | §5, §8 |
| 2 | Data integrity (PIT, survivorship, snapshots) + toolchain | deep | I.4–.7 | §1, §11, §15 |
| 3 | Probability, stats, **stochastic calculus**, simulation, numerics | deep | II.1–.2, .5–.6 | §5 |
| 4 | Financial econometrics (+GMM, copulas) | deep/integration | II.3–.4 | §5, §11 |
| 5 | Economics & macro (+ international) | survey | III.1 | §14 |
| 6 | Efficiency & active-management economics | deep | III.2–.3 | §2, §7 |
| 7 | Asset pricing: theory + empirical toolkit + premia | deep | III.4–.6 | §2, §11 |
| 8 | Equity analysis & valuation (full FSA) | deep | IV.1–.5 | §6 |
| 9 | Fixed income (+swap curve, vanilla IR derivatives) | deep→integration | IV.6–.8, V.5 | §12 |
| 10 | Derivatives, vol & credit survey | deep→survey | V | §5, §13 |
| 11 | Prediction & inference (incl. LLM era, crowding) | deep | VI | §1, §11, §15 |
| 12 | Portfolio construction | deep | VII.1–.7 | §4 |
| 13 | Frictions & microstructure | survey/integration | VIII.1–.2 | §13 |
| 14 | Backtesting mechanics | deep | VIII.3 | §1, §3 |
| 15 | Risk management | deep→survey | IX.1–.4 | §4 |
| 16 | Live implementation | deep | VIII.4–.5 | §3 |
| 17 | Performance & attribution | deep | IX.5 | §4 |
| 18 | Governance & professional practice | deep/survey | VI.7, IX.6 | §1 |
| 19 | Operational risk & resilience | survey | IX.6 | §14 |
| 20 | ESG | survey | VII.8 | §14 |
| 21 | Currency & international | survey | III.1, VII.6–.7 | §14 |
| 22 | Alternatives & institutional ALM | survey | VII.8 | §14 |

## 3. One-home map (MECE anchors for historically homeless concepts)

| Concept | Home | Referenced by |
|---|---|---|
| Discounting/TVM (one idea: equities, bonds, projects) | I.2 | IV, V |
| Data-side leakage: PIT, survivorship, restatements | I.4 | VI, VIII |
| Transform-side leakage: the causal feature contract | VI.2 | VIII |
| Volatility models (EWMA/GARCH family), simulation, optimization, numerics | II | everything applies them |
| HAC/clustered standard errors (Newey-West, Petersen) | II.3 | III.5, VI |
| Efficiency, Grossman-Stiglitz, limits to arbitrage | III.2 | VI motivates |
| Behavioral finance — biases in **markets** | III.3 | — |
| Behavioral finance — biases in **researchers** | VI.6 | — |
| The three meanings of "factor" (pricing / alpha / risk) | III.4 | VI, VII, IX |
| The full inference discipline (multiple testing → trials ledger) | VI.6–.7 | VIII, IX use, never restate |
| Covariance estimation | VII.2 | IX consumes |
| Cost *economics* (impact, spreads) vs cost *mechanics* (engine modeling) | VIII.1 vs VIII.3 | — |
| Risk *measurement* vs live *enforcement* | IX.1–.3 vs VIII.5 | — |
| Cross-validation: generic (II.7) vs finance-specific purging/embargo (VI.6) | II.7 teaches the method; VI.6 owns why finance breaks it | — |
| Copulas/tail dependence (method) vs credit application | II.4 | V.6, IX |
| Stochastic calculus machinery vs its pricing outputs | II.5 | V applies |
| Crowding/decay/capacity (premia lifecycle) | III.6 | VI.1 applies |
| LLM data-contamination look-ahead: data side vs inference side | I.4 principle | VI.4 case |
| Quality/distress scores: *computed* in IV.5, *used as signals* in VI.3 | IV.5 | VI.3 |
| Track-record inference (luck vs skill) *applies* VI.6's statistics in IX.5 | VI.6 | IX.5 |

---

# The Program

## Part I — Measurement: prices, time, and data you can trust

**I.1 Orientation** `[deep]` ✅ — what quants do; the honesty labels; compounding and
the asymmetry of loss; run the library.
**I.2 Returns & discounting** `[deep]` — simple vs log returns and when each is
correct; multi-period linking; **total return vs price return** (dividends are not
optional); excess and real vs nominal returns; annualization and its abuses; TVM as
*the* pricing primitive; index construction (price-, cap-, equal-weighted) and why
index choice changes conclusions.
**I.3 Market conventions & instruments** `[deep/survey]` — calendars, day count,
settlement; equities/ETFs, futures (specs, margin, roll), FX quoting, bond
conventions (accrued interest, clean vs dirty); identifiers and the ticker-reuse
problem.
**I.4 Data integrity I: why backtests lie** `[deep]` ✅ — point-in-time/bitemporal
storage; restatements; survivorship and **delisting returns** (the delisting-bias
result); immutable snapshots and reproducibility.
**I.5 Data integrity II: filings** `[deep]` ✅ — SEC EDGAR: natively bitemporal;
concept drift; duration ambiguity.
**I.6 Data integrity III: prices & alternative data** `[deep/survey]` —
corporate-action adjustment done by hand (splits, dividends — how adjusted series
are actually constructed and where vendors disagree); outlier/error handling policy;
universe construction end-to-end; **alternative-data craft** `[survey]`: vendor due
diligence, entity/ticker mapping, panel and backfill bias — the alt-data analogue of
survivorship.
**I.7 The quant's toolchain** `[deep/integration]` — **SQL** and relational schemas
(joining PIT datasets is daily work); columnar data (Parquet/Arrow) and the modern
engines (**Polars, DuckDB**) vs pandas — when each; Linux/shell fluency; data
structures & algorithmic complexity as used in research code; distributed compute
(Dask/Spark) `[survey]`; git/testing/CI as research infrastructure (practiced
throughout this repo). Industrial reference points: **ArcticDB** (the production
version of this book's PIT/snapshot design), MLflow (the industrial trials ledger).
*Outcome: you can build a reproducible, PIT-clean, survivorship-free dataset with
professional tooling and demonstrate in code three distinct ways naive data inflates
results.*

## Part II — Uncertainty: the statistical toolkit

**II.1 The statistical facts of returns** `[deep]` — fat tails, skew, volatility
clustering, aggregational Gaussianity, autocorrelation of returns vs of |returns|;
why Gaussian assumptions fail and when they're tolerable.
**II.2 Estimation & testing** `[deep]` — MLE and method of moments; sampling error
in means vs variances (why expected returns are the hardest number in finance);
hypothesis tests; **the bootstrap (iid and block)**; Monte Carlo experiments as the
quant's laboratory.
**II.3 Regression & estimation frameworks** `[deep/integration]` — OLS and its
failure modes on financial data; heteroskedasticity and autocorrelation;
**Newey-West/HAC and clustered standard errors** (overlapping horizons, panel data);
**GMM** — the frame under which Fama-MacBeth, time-series, and SDF tests are all
special cases; logistic regression for defaults/events.
**II.4 Time series & dependence** `[integration: statsmodels/arch]` — stationarity
and unit roots (ADF); ARMA; **GARCH family** (GARCH/GJR/EGARCH) and realized
volatility; cointegration (Engle-Granger, Johansen); VAR; regime switching (Markov,
and modern statistical jump models); state space & the Kalman filter; **copulas and
tail dependence** — dependence beyond linear correlation (feeds credit and risk).
**II.5 Stochastic calculus & simulation** `[deep]` — the continuous-time machinery
made explicit: Brownian motion, **Itô's lemma**, SDEs; **martingales, change of
measure (Girsanov), risk-neutral pricing theory**, change of numeraire, Feynman-Kac
— the layer every derivatives interview tests; Poisson/jump processes; simulation:
GBM, mean reversion (OU), jumps, correlated paths (Cholesky), variance reduction;
simulation as pricing tool, robustness tool, and (survey) generative market
simulation/synthetic data.
**II.6 Optimization & numerics** `[deep]` — root finding (YTM, IRR, implied vol all
live here); interpolation (curves); convex/quadratic programming (portfolios live
here); penalties and regularization; trees and finite differences at teaching depth;
dynamic programming & HJB `[survey]` (the method under Merton's problem and
Almgren-Chriss).
**II.7 Machine learning foundations** `[deep/integration]` — bias-variance;
regularization (ridge/lasso); cross-validation **done right for dependent data**;
trees and ensembles; **deep learning explicitly** (a torch-based pass through MLPs
and sequence models; embeddings); **reinforcement learning** (MDPs, where RL fits
finance) `[survey]`; why financial ML fails differently (low signal-to-noise,
non-stationarity, adversarial adaptation).
*Outcome: you can estimate, test, simulate, and optimize — with standard errors you
can defend.*

## Part III — How markets set prices

**III.1 Macro & international context** `[survey + FRED data]` — business cycles;
inflation; monetary policy and the policy rate; the yield curve as a macro signal;
**exchange-rate economics** (parity conditions, regimes) and what currency exposure
does to portfolio returns (hedged vs unhedged — the management side lives in VII.6);
where macro data lives and its revision problem (PIT applies to macro too).
**III.2 Efficiency and its limits** `[deep]` — EMH forms and the joint-hypothesis
problem; **Grossman-Stiglitz** (why markets can't be perfectly efficient — edges are
compensation for information costs); limits to arbitrage (noise-trader risk, funding,
short constraints); anomaly vs risk premium vs data-mining artifact — the three
possible verdicts every "edge" faces; post-publication decay evidence.
**III.3 Behavioral markets** `[survey]` — prospect theory, overreaction/
underreaction, disposition, herding; what behavioral stories predict that risk
stories don't (and vice versa).
**III.4 Asset pricing theory** `[deep]` — utility and risk aversion; mean-variance
equilibrium → CAPM; the SML and its empirical flatness; APT and multifactor pricing;
the SDF view at survey depth; **the three meanings of "factor"** — pricing factors
(explain returns), alpha factors (predict returns), risk factors (drive
covariance) — kept distinct for the rest of the program.
**III.5 The empirical cross-section: the researcher's toolkit** `[deep]` — **this is
the complete process for establishing a risk factor or an alpha**: portfolio sorts
(univariate, double; NYSE breakpoints; equal vs value weighting and why results
flip); **Fama-MacBeth two-pass regressions** with Shanken and Newey-West
corrections; time-series alpha tests and the **GRS test**; factor construction
methodology (2×3 sorts, HML-style spreads); spanning and model-comparison tests;
**characteristics vs covariances** (Daniel-Titman); replication practice on the Ken
French library — premia reproduced to published numbers.
**III.6 The risk-premia catalog — and its lifecycle** `[deep]` — the complete map,
each with evidence, economic story (risk vs behavioral vs structural), and post-cost
reality: equity premium; size; value; **momentum (cross-sectional and time-series)**;
profitability/quality; investment; **low-beta/betting-against-beta**; **carry** (FX,
rates, commodities, equities); term premium; credit premium; liquidity premium;
**volatility risk premium**; skewness/lottery. Then the modern half: premia as
**decaying, crowdable, valuation-dependent objects** — post-publication decay,
**crowding metrics** (valuation spreads, co-movement, positioning), capacity, and
multi-manager/pod market structure (the 2025 quant unwind as case study).
*Outcome: you can take a candidate premium from hypothesis to sorts to Fama-MacBeth
to GRS, reproduce the published number, and argue all three verdicts.*

## Part IV — Valuing claims

**IV.1 Financial statement analysis, complete** `[deep]` — the three statements and
their articulation; revenue recognition; **accruals vs cash flow** (and the accruals
anomaly); capitalization vs expensing, leases, deferred taxes, off-balance-sheet
items; common-size analysis; the **full ratio system with DuPont decomposition**
(profitability, efficiency, liquidity, solvency, coverage); growth analysis;
earnings quality and red flags.
**IV.2 Forecasting fundamentals** `[deep]` — driver-based pro-forma statements;
working capital and capex schedules; **fade and base rates** (mean reversion of ROIC
and growth — the empirical discipline against hockey-sticks); scenario ranges, not
point estimates.
**IV.3 Cost of capital** `[deep]` — beta estimation and its instability; the equity
risk premium three ways (historical, implied, survey) and why they disagree; WACC;
cost of debt; when CAPM-Ke is indefensible and what practitioners do.
**IV.4 Equity valuation models** `[deep]` — DDM (Gordon, multi-stage); FCFF vs FCFE
(and when each); **residual income**; multiples done properly (what drives each
multiple, comps selection, enterprise vs equity consistency); **market-implied
expectations** (running any model backwards — what the price already believes);
sum-of-parts, real options, private/venture valuation `[survey]`. Cross-checks:
sensitivity tables, football fields, margin of safety.
**IV.5 Quality, distress & manipulation scores** `[deep]` — Altman Z and Ohlson O
(distress); Beneish M (manipulation); Piotroski F (quality); Sloan accruals — each
reproduced against real filings, then used as cross-sectional signals (bridge to VI).
**IV.6 Fixed income: the curve** `[deep]` — price/yield mechanics from I.3;
bootstrapping a sovereign curve from free Treasury/FRED data; **Nelson-Siegel(-
Svensson)** fitting; discount factors and forwards; level/slope/curvature (PCA).
**IV.7 Fixed income: risk & term structure** `[deep/survey]` — duration, convexity,
DV01, **key-rate durations**; term-structure theories (expectations hypothesis and
its failure; term premia); TIPS and breakevens; spreads (G/Z/OAS at survey); credit
fundamentals (ratings, default, recovery) and securitization `[survey]`.
**IV.8 The swap-curve layer** `[integration]` — post-LIBOR **multi-curve
construction** (SOFR compounding, OIS discounting, swap bootstrapping) via
QuantLib/rateslib; FRAs and futures-based hedging; the plumbing between our
sovereign curves and Part V's rate options.
*Outcome: you can value a company from its filings and a bond book off a curve you
built — one PV framework, two claim types — and defend every input against a
skeptical IC.*

## Part V — Contingent claims

**V.1 Forwards & futures** `[deep]` — cost-of-carry pricing; basis; contango/
backwardation and roll yield (bridge to carry, III.6); futures vs forwards.
**V.2 Options I: structure** `[deep]` — payoffs and strategy structures; put-call
parity; no-arbitrage bounds; early exercise.
**V.3 Options II: pricing** `[deep]` — binomial trees (with American exercise);
risk-neutral valuation as an idea; **Black-Scholes-Merton** — the formula, every
assumption, and each assumption's empirical failure; Greeks and the hedging
workflow.
**V.4 Volatility** `[deep/integration]` — implied vol; smile, skew, term structure;
**arbitrage-free surface construction (SVI/SSVI)** and risk-neutral density
extraction; the volatility risk premium (bridge to III.6); **flow-driven vol
dynamics** `[survey]`: 0DTE, dealer-gamma positioning, option-income supply; local/
stochastic vol (Heston, SABR) `[survey]`.
**V.5 Rate options & vanilla IR derivatives** `[integration]` — pricing under
forward measures (the II.5 machinery at work): **Black-76 for caps/floors/
swaptions**, Hull-White pricing, convexity adjustments — the teaching-depth layer
academia treats as core, below the excluded desk-grade calibration.
**V.6 Credit: a coherent survey** `[survey]` — the full arc in one place: **Merton
structural / distance-to-default → reduced-form hazard rates → CDS pricing → credit
VaR and default correlation (copulas from II.4)**; XVA and exotics as a map of what
desks do.
*Outcome: you can price and hedge a vanilla book, read a vol surface, and state
precisely where each model stops being trustworthy.*

## Part VI — Prediction: alpha research & the inference discipline *(the core)*

**VI.1 The economics of a signal** `[deep]` — where edges come from (III.2's
taxonomy: risk transfer, behavioral, structural/flow, information); who's on the
other side; expected decay and capacity *before* the first backtest.
**VI.2 Signal construction** `[deep]` — from raw data to a score: winsorization,
standardization, **sector/beta neutralization** — all under the **causal feature
contract** (trailing-window transforms only; the transform-side leakage home);
information coefficient and IC decay; quantile analysis; turnover; the **financial-ML
labeling stack** (triple-barrier labeling, **meta-labeling**, fractional
differentiation, bet sizing from predicted probabilities) — the data-construction
half of the López de Prado canon, paired with VI.6's validation half.
**VI.3 Classical signal families** `[deep]` — built and honestly evaluated: trend/
time-series momentum; cross-sectional momentum; value (price and fundamental);
carry; quality; mean reversion/pairs (cointegration from II.4); seasonality;
positioning. Each: construction → IC → costs → verdict.
**VI.4 ML, NLP & the LLM era** `[deep/integration]` — feature pipelines; tree
ensembles and regularized linear models as the workhorses; text alpha from
dictionary methods (historical context) to **embeddings and transformers** on
filings/news/calls; **LLMs in the investment process**: research-assistant
workflows, LLM-extracted alt-data, **automated/agentic alpha mining** (formulaic
alphas, genetic programming, LLM factor-generation agents) — taught *and critiqued*:
machine-scale factor generation is a multiple-testing bomb that makes VI.6 more
binding, not less; **LLM training-data contamination as a new look-ahead channel**
(the PIT discipline of I.4 applied to models); **genAI model risk** (herding,
foundation-model concentration — the FSB/IOSCO agenda, feeds IX.4); RL for
execution/sizing `[survey]`. Why ML alpha needs *stricter* inference, not looser.
**VI.5 Combining signals** `[deep]` — from scores to expected returns (the Grinold
rule); IC-weighting; ensembles; correlation among signals and marginal value.
**VI.6 The inference discipline** `[deep]` — the single home: data-mining bias;
**multiple testing** (FWER/FDR, Bonferroni, BHY); **deflated and haircut Sharpe**;
**PBO/CSCV**; minimum backtest length; walk-forward and **purged/embargoed CV**;
sample-splitting ethics (the holdout you only touch once); the researcher's own
biases — and the replication crisis as case study.
**VI.7 Research governance** `[deep]` — pre-registration; the **hypothesis registry
and cumulative trials ledger** (deflation must count *all* trials, not this study's);
findings logs; the research protocol end-to-end.
*Outcome: you can run the complete alpha process — hypothesis → construction →
evaluation → combination — and produce a verdict that survives adversarial scrutiny,
trials count disclosed.*

## Part VII — Portfolios

**VII.1 Theory** `[deep]` — diversification arithmetic; the efficient frontier;
two-fund separation; utility calibration; benchmark-relative investing and the
**Fundamental Law (IR ≈ IC·√breadth·TC)** with its assumptions.
**VII.2 The inputs problem** `[deep]` — expected returns (historical vs implied vs
shrunk — and why this input dominates); **covariance estimation** (sample → EWMA →
**Ledoit-Wolf shrinkage** → factor-based → RMT denoising `[survey]`); estimation
error compounding in optimizers.
**VII.3 Mean-variance and its failure** `[deep]` — MVO as QP; the
**error-maximization property demonstrated** (garbage in, leverage out); resampling
(Michaud) `[survey]`; robust optimization `[survey]`; why 1/N is hard to beat
(DeMiguel) — as evidence, not slogan.
**VII.4 Robust construction** `[deep/integration]` — **Black-Litterman** in full
(reverse optimization/equilibrium, views, uncertainty); **risk budgeting and risk
parity (ERC)**; **HRP**; min-variance and max-diversification; **CVaR optimization**
(Rockafellar-Uryasev); baselines cross-checked against PyPortfolioOpt.
**VII.5 Sizing & leverage** `[deep]` — volatility targeting; **Kelly and fractional
Kelly** (growth vs drawdown); drawdown control policies; leverage and its financing.
**VII.6 Real-world construction** `[deep]` — constraints (long-only, box, sector,
cardinality); turnover penalties and **transaction-cost-aware optimization**;
tracking error and active-share; factor-mimicking and characteristic portfolios;
long-short mechanics (shorting costs, margin); rebalancing policy (calendar vs
threshold); taxes `[survey]`.
**VII.7 Allocation across strategies & time** `[deep/survey]` — portfolio-of-
strategies (correlation-aware capital weighting, sleeve attribution, kill
decisions); multi-period view (Merton problem, glide paths) `[survey]`; SAA vs TAA;
**currency hedging policy** (to hedge or not, by asset class).
**VII.8 Alternatives & institutions** `[survey]` — the alternative-investment
landscape a PM must speak to: private equity/VC (J-curves, IRR vs PME pitfalls),
real estate & infrastructure, commodities as an allocation, hedge-fund strategy
taxonomy and their fee/liquidity structures; **private-markets measurement quant**:
return unsmoothing ("volatility laundering"), stale/discretionary NAVs, cash-flow-
based benchmarking; institutional context: mandates, vehicles, fees,
**asset-liability management** (pensions/insurers); **ESG & climate** — standards,
data problems, what the evidence does and doesn't show, with the quant frontier now
in **climate/transition risk** specifically.
*Outcome: signals + covariance → defensible weights under real constraints — and a
demonstration of exactly how the naive route destroys value.*

## Part VIII — Frictions & implementation

**VIII.1 Market microstructure** `[survey/integration]` — market structure
(auctions, makers/takers, fragmentation); the limit order book; **spread economics**
(inventory vs adverse selection); **price impact** (temporary vs permanent, the
square-root law); liquidity measurement (ADV, Amihud); capacity estimation.
**VIII.2 Execution** `[integration]` — order types; scheduling (TWAP/VWAP/POV);
**implementation shortfall** and **Almgren-Chriss** in simulation; TCA pre- and
post-trade; the build-vs-buy reality of execution algos.
**VIII.3 Backtesting mechanics** `[deep]` — vectorized vs event-driven engines and
when each lies; **the look-ahead catalog** (signal timing, fill timing, same-bar
fills); cost/borrow/financing modeling; corporate actions and delistings in the
engine; futures roll; **options-strategy backtest mechanics** (chains, expiry,
assignment, IV-conditioned entries) `[survey]`; invariant tests (shift tests,
buy-and-hold parity, cost monotonicity).
**VIII.4 From backtest to live** `[deep]` — one code path; the venue seam; paper
trading as a gate, not a demo; divergences modelled (partial fills, rejects,
latency).
**VIII.5 Live operations** `[deep]` — order management; **enforced risk limits and
drawdown circuit breakers**; reconciliation; monitoring and incident response;
**strategy decay** — live-vs-backtest drift and the kill decision.
*Outcome: you can name every way an engine flatters a strategy, test for each, and
run one live under enforced limits with an honest record.*

## Part IX — Risk, attribution & governance

**IX.1 Market risk measurement** `[deep]` — exposures and sensitivities; **VaR three
ways** (historical, parametric, Monte Carlo) and **Expected Shortfall**; **VaR
backtesting** (Kupiec, Christoffersen); EVT for tails `[survey]`.
**IX.2 Factor risk models** `[deep]` — build one: exposures → factor covariance →
specific risk; risk decomposition and marginal contributions; the risk-factor
meaning of "factor" made concrete; stress testing and **crisis correlations**.
**IX.3 Credit, counterparty & liquidity risk** `[survey]` — PD/LGD/EAD; migration;
CVA as a concept; funding and liquidity risk; where FRM goes deeper.
**IX.4 Model risk** `[deep/survey]` — validation practice (the SR 11-7 spirit):
benchmarking, sensitivity, monitoring; model inventories; every model in this
project as a worked example; **genAI model risk** `[survey]` — validating
non-deterministic models, hallucination, correlated-model herding, third-party
foundation-model concentration (the FSB/IOSCO 2025 agenda).
**IX.5 Performance measurement & attribution** `[deep]` — TWR vs MWR; risk-adjusted
metrics and their traps; **Brinson attribution**; **factor-based attribution** (on
our own live book); returns-based style analysis; luck vs skill (track-record
inference — connecting back to VI.6); GIPS `[survey]`.
**IX.6 Operational risk & professional practice** `[survey]` — **operational risk &
resilience** (process, key-person, vendor, cyber, model inventory — the FRM domain a
research shop still owns); ethics of reported results; conflicts; governance of a
research shop; what institutional allocators actually diligence; **communicating
research** — presenting quantitative work to non-technical decision-makers, the
skill every employer lists and few curricula train (practiced via the capstone
defenses).
*Outcome: you can produce a risk report, attribute a P&L to decisions, validate a
model, and audit a research process — including your own.*

## Role coverage map — which parts carry which quant seat

The program is one body of knowledge, but the four quant roles weight it
differently. Honest coverage assessment, including what a curriculum *cannot*
confer:

| Role | Core parts | Curriculum coverage | What only practice/time provides |
|---|---|---|---|
| **Quant researcher / modeler** | II, III, VI, VII, IX | ~95% — this program *is* that syllabus | research taste; publication-grade novelty |
| **Quant trader** | III.6, V, VI, VIII | ~75% | market feel (→ start the paper loop early); the interview gauntlet — mental math, probability under pressure, **game-theory/market-making games** (the SIG/Optiver/Jane Street hiring gates) — a separate practice track (references §15) |
| **Quant engineer** | I, VIII, + the repo itself as artifact | ~70% | C++/low-latency, at-scale distributed systems, kdb+/FIX — honestly outside a retail project's reach; needs a targeted artifact if that seat is the goal |
| **Portfolio manager** | VII, IX, III | ~80% | capital-at-risk temperament; a multi-year record (the paper track record is the legitimate substitute that starts now); stakeholder judgment |

Cross-cutting and non-negotiable for every seat: the owner works every `[deep]`
lesson personally and can re-derive it live (MASTER_SPEC §6.3) — a curriculum
possessed but not internalized is interview liability, not asset.

**The pipeline (getting the interview — actions, not lessons):** publish the book
and track record publicly (the board demo *is* the outreach artifact); enter the
visible competitions (IMC Prosperity, WorldQuant BRAIN alpha submissions, Kaggle
finance comps — each a line recruiters search for); be present where quants are
found (QuantNet, LinkedIn with the demo pinned); apply on-cycle for new-grad
programs (postings open ~August–October for following-year starts); and convert the
capstones into short public write-ups — a reproducible result note travels further
than a resume line.

## Capstones

**A.** A systematic multi-signal book: hypothesis registry → construction → VI.6
gates → VIII engine → live paper, with a public, honestly-evaluated track record.
**B.** A complete fundamental valuation from filings, defended input-by-input.
**C.** A bond portfolio risk-managed off a self-built curve (duration/key-rate/PCA).
**D.** An options book priced, hedged, and risk-reported via integration.
**E.** An ML/alt-data signal that survives VI.6 — or an honest post-mortem of why not.

---

## Mechanics

Executable Jupyter Book (MyST + jupytext); CI executes every cell, `allow_errors:
false` — a broken lesson fails the build. Data pinned to immutable snapshots.
**Verification ledger:** the book carries one table listing, per `[deep]` lesson,
the externally checkable number it reproduces and its source — the depth contract's
enforcement mechanism (MASTER_SPEC §6.2), not an honor system.
Bibliography: `docs/REFERENCES.md` — verified citations across 13 sections, including
the empirical-methodology toolkit (§11), fixed income (§12), and microstructure/
execution (§13).
