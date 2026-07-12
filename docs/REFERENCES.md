# Quantropy — Intellectual Foundations & References

> The canon Quantropy is built on. Every module should cite its source here
> (NFR8: "documented as a body of knowledge"). Organized by platform layer so that
> when you build, say, `analytics/covariance`, the relevant literature is one lookup
> away. All citations below were verified against primary publisher / journal records
> during research; edition and attribution caveats are noted inline.

**Layer legend:** L0 core · L1 data · L2 analytics · L3 portfolio construction ·
L4 strategy/signals · L4.5 allocation · L5 backtesting · L6 evaluation/robustness ·
L7 execution · XC cross-cutting (governance / philosophy).

**How to read the map:** §1 is the discipline that keeps us honest (governs L4–L6);
§2–§6 are the domain canon; §7 is philosophy; §8 is the CFA completeness check; §9 is
prior-art code to learn from; §10 is the curated "start here" shortlist.

---

## 1. Research governance, backtesting rigor & anti-overfit `[L4/L5/L6/XC]`

The literature that makes the difference between a real edge and a data-mined mirage.
This is the spine of the platform's credibility.

- **López de Prado, M. (2018).** *Advances in Financial Machine Learning.* Wiley. —
  The practitioner playbook: triple-barrier labeling, meta-labeling, fractional
  differentiation, **purged/embargoed CV** and **CPCV**, sample weighting, leakage-free
  feature importance. `[L5/L6/L4]`
- **López de Prado, M. (2020).** *Machine Learning for Asset Managers.* Cambridge UP
  (Elements in Quantitative Finance). — Covariance **denoising/detoning**
  (Marčenko–Pastur), clustering, compact multiple-testing treatment. `[L2/L6]`
- **Bailey, D. H. & López de Prado, M. (2014).** "The Deflated Sharpe Ratio." *J.
  Portfolio Management* 40(5), 94–107. — **DSR**: deflates observed Sharpe for number
  of trials, sample length, skew, kurtosis. Requires a trials count → trials ledger.
  `[L6/L4]`
- **Bailey, Borwein, López de Prado & Zhu (2017).** "The Probability of Backtest
  Overfitting." *J. Computational Finance* 20(4), 39–69. — **PBO** via combinatorially
  symmetric CV. `[L6]`
- **Bailey, Borwein, López de Prado & Zhu (2014).** "Pseudo-Mathematics and Financial
  Charlatanism." *Notices of the AMS* 61(5), 458–471. — **Minimum backtest length**;
  with enough trials a high in-sample Sharpe is guaranteed on random data. Not
  reporting trial count makes a backtest meaningless. `[L6/L4]`
- **Harvey, C. R., Liu, Y. & Zhu, H. (2016).** "…and the Cross-Section of Expected
  Returns." *Review of Financial Studies* 29(1), 5–68. — The **factor-zoo** indictment;
  a new factor needs t ≳ 3.0 after multiple-testing correction. `[L6/L2]`
- **Harvey, C. R. & Liu, Y. (2015).** "Backtesting." *J. Portfolio Management* 42(1),
  13–28. — The **haircut Sharpe** (Bonferroni/Holm/BHY) reflecting how many strategies
  were tried. `[L6]`
- **Arnott, R., Harvey, C. R. & Markowitz, H. (2019).** "A Backtesting Protocol in the
  Era of Machine Learning." *J. Financial Data Science* 1(1), 64–74. — A seven-point
  research-protocol checklist. **This is essentially our L4 governance blueprint.** `[L4]`
- **Harvey, C. R. (2017).** "Presidential Address: The Scientific Outlook in Financial
  Economics." *J. Finance* 72(4), 1399–1440. — Reproducibility-crisis manifesto;
  p-hacking, Bayesianized evidence standards. `[XC/L4]`
- **Hou, K., Xue, C. & Zhang, L. (2020).** "Replicating Anomalies." *RFS* 33(5),
  2019–2133. — ~64% of 447 anomalies vanish under NYSE breakpoints + value-weighting.
  `[L6]`
- **Feng, G., Giglio, S. & Xiu, D. (2020).** "Taming the Factor Zoo: A Test of New
  Factors." *J. Finance* 75(3), 1327–1370. — Double-selection LASSO test for whether a
  *new* factor adds anything beyond hundreds of existing ones. `[L6/L4]`
- **Chen, A. Y. & Zimmermann, T. (2022).** "Open Source Cross-Sectional Asset Pricing."
  *Critical Finance Review* 11(2), 207–264. — The counterpoint: ~98% of clearly-
  significant predictors replicate. Plus a reproducible dataset (openassetpricing.com).
  `[L4/L6]`
- **Dixon, Halperin & Bilokon (2020).** *Machine Learning in Finance: From Theory to
  Practice.* Springer. — Academic bridge from supervised/RL to financial econometrics.
  `[L5/L6]`
- **Jansen, S. (2020).** *Machine Learning for Algorithmic Trading*, 2nd ed. Packt. —
  End-to-end applied workflow (Zipline/backtrader/Alphalens/pyfolio). `[L4/L5]`

*Lead to verify:* Gu, Kelly & Xiu, "Empirical Asset Pricing via Machine Learning" (RFS
2020) — the ML cross-section benchmark.

---

## 2. Factors, risk premia & academic asset pricing `[L2/L4]`

The theory of *what* is compensated and *why* — feeds factor construction (L2) and the
signal taxonomy (L4).

**Foundations (CAPM/APT):**
- **Sharpe (1964)** "Capital Asset Prices." *J. Finance* 19(3), 425–442 — CAPM / SML.
- **Lintner (1965)** *Rev. Econ. & Statistics* 47(1) · **Mossin (1966)** *Econometrica*
  34(4) — complete the Sharpe–Lintner–Mossin CAPM.
- **Ross (1976)** "The Arbitrage Theory of Capital Asset Pricing." *JET* 13(3),
  341–360 — **APT**; the charter for multi-factor models.
- **Fama & MacBeth (1973)** *JPE* 81(3), 607–636 — the two-pass cross-sectional
  regression for estimating factor premia. `[L2 method]`
- **Cochrane (2011)** "Presidential Address: Discount Rates." *J. Finance* 66(4),
  1047–1108 — reframes asset pricing around time-varying expected returns. `[L2]`

**The empirical factor program:**
- **Fama & French (1992)** *J. Finance* 47(2), 427–465 — beta is flat once size & value
  control; the empirical precursor.
- **Fama & French (1993)** "Common Risk Factors…" *JFE* 33(1), 3–56 — the **3-factor**
  model + 2×3 sort construction. `[L2 construction]`
- **Fama & French (2015)** "A Five-Factor Asset Pricing Model." *JFE* 116(1), 1–22 —
  adds profitability (RMW) and investment (CMA).
- **Jegadeesh & Titman (1993)** *J. Finance* 48(1), 65–91 — cross-sectional **momentum**.
- **Carhart (1997)** *J. Finance* 52(1), 57–82 — the **4-factor** (adds UMD); standard
  attribution benchmark. `[L2/L6 attribution]`
- **Hou, Xue & Zhang (2015)** "Digesting Anomalies." *RFS* 28(3), 650–705 — the
  **q-factor** model (investment + profitability).
- **Novy-Marx (2013)** "The Other Side of Value: The Gross Profitability Premium."
  *JFE* 108(1), 1–28 — profitability/**quality** as a factor.
- **Ang, Hodrick, Xing & Zhang (2006)** "The Cross-Section of Volatility and Expected
  Returns." *J. Finance* 61(1), 259–299 — the **low-vol / idiosyncratic-vol** anchor.

**AQR school (practitioner-academic):**
- **Asness, Moskowitz & Pedersen (2013)** "Value and Momentum Everywhere." *J. Finance*
  68(3), 929–985 — value + momentum across 8 markets; negatively correlated. `[L4]`
- **Moskowitz, Ooi & Pedersen (2012)** "Time Series Momentum." *JFE* 104(2), 228–250 —
  academic basis for **trend-following / managed futures**. `[L4 trend]`
- **Frazzini & Pedersen (2014)** "Betting Against Beta." *JFE* 111(1), 1–25 — the
  **BAB** / defensive factor. `[L4 defensive]`
- **Asness, Frazzini & Pedersen (2019)** "Quality Minus Junk." *Rev. Accounting
  Studies* 24(1), 34–112 — the modern **quality** factor definition. `[L4]`
- **Koijen, Moskowitz, Pedersen & Vrugt (2018)** "Carry." *JFE* 127(2), 197–225 —
  generalizes **carry** to every asset class. `[L4 carry]`
- **Frazzini, Kabiller & Pedersen (2018)** "Buffett's Alpha." *FAJ* 74(4), 35–55 —
  Berkshire = leverage + BAB + QMJ; the flagship *tradeable*-factor demonstration.
- **Frazzini, Israel & Moskowitz (2012, WP)** "Trading Costs of Asset Pricing
  Anomalies." SSRN 2294498 — real trading costs are small at scale (the pro-tradeable
  side of the post-cost debate). *Working paper — cite as SSRN.*

**Alpha decay / post-publication (the "does it survive?" camp):**
- **McLean & Pontiff (2016)** "Does Academic Research Destroy Stock Return
  Predictability?" *J. Finance* 71(1), 5–32 — predictors decay ~26% OOS, ~58%
  post-publication.

**Practitioner syntheses (books):**
- **Ilmanen (2011)** *Expected Returns.* Wiley — cross-asset risk-premia survey.
- **Ilmanen (2022)** *Investing Amid Low Expected Returns.* Wiley.
- **Ang (2014)** *Asset Management: A Systematic Approach to Factor Investing.* Oxford UP
  — "assets are bundles of factor risks."

---

## 3. Systematic & algorithmic trading — practitioner canon `[L1/L3/L4/L5/L7]`

How strategies are actually built, sized, rolled, and executed.

- **Carver, R. (2015)** *Systematic Trading.* Harriman House — foundational for
  **volatility targeting** + **forecast diversification** + modular design
  (instrument → forecast → position). `[L3/L4]`
- **Carver, R. (2019)** *Leveraged Trading.* Harriman House — leverage/cost/risk for
  smaller accounts. `[L3/L4]`
- **Carver, R. (2023)** *Advanced Futures Trading Strategies.* Harriman House — 30
  backtested futures strategies with rigorous risk-scaling across 100+ instruments.
  `[L4/L3/L1]`
- **Chan, E. (2008/2021)** *Quantitative Trading*, 2nd ed. Wiley — the retail-quant
  "starter business" book; backtest hygiene. `[L4/L5]`
- **Chan, E. (2013)** *Algorithmic Trading: Winning Strategies and Their Rationale.*
  Wiley — cointegration/pairs, mean-reversion vs momentum, with tests. `[L4/L1]`
- **Chan, E. (2017)** *Machine Trading.* Wiley — ML + Kelly sizing across asset classes.
  `[L4/L3]`
- **Clenow, A. (2013/2023)** *Following the Trend*, 2nd ed. Wiley — how diversified CTA
  trend-following actually works; vol-based sizing. `[L4/L3/L1]`
- **Clenow, A. (2015)** *Stocks on the Move.* Equilateral — a replicable equity
  cross-sectional momentum system. `[L4/L3]`
- **Clenow, A. (2019)** *Trading Evolved.* Self-pub — practical Python backtesting on
  Zipline. `[L5/L4]`
- **Kaufman, P. (2019)** *Trading Systems and Methods*, 6th ed. Wiley — the encyclopedic
  reference. `[L4, broad L3/L5]`
- **Davey, K. (2014)** *Building Winning Algorithmic Trading Systems.* Wiley —
  disciplined dev process; walk-forward + **Monte Carlo** validation of drawdown/sizing.
  `[L5/L3]`
- **Johnson, B. (2010)** *Algorithmic Trading & DMA.* 4Myeloma Press — the **execution**
  reference (VWAP/TWAP/POV/IS algos, microstructure, TCA). `[L7/L5]`
- **Narang, R. (2013/2024)** *Inside the Black Box*, 2nd/3rd ed. Wiley — the best
  conceptual map of a quant fund's alpha/risk/execution stack. `[whole-stack]`
- **Harris, L. (2003)** *Trading and Exchanges: Market Microstructure for
  Practitioners.* Oxford UP — underpins realistic cost/slippage models. `[L5/L7]`
- **Gatev, Goetzmann & Rouwenhorst (2006)** "Pairs Trading." *RFS* 19(3), 797–827 —
  canonical empirical validation of distance-based **pairs trading**. `[L4]`

---

## 4. Portfolio construction, covariance & risk `[L2/L3/L6]`

The optimizers — and, crucially, the robust *inputs* they need.

**MVO and its fragility:**
- **Markowitz (1952)** "Portfolio Selection." *J. Finance* 7(1), 77–91 — MPT / efficient
  frontier (needs a covariance matrix → §L2). `[L3]`
- **Michaud (1989)** "The Markowitz Optimization Enigma." *FAJ* 45(1), 31–42 — the
  canonical "**MVO is an error-maximizer**" critique; motivates resampling. `[L3]`
- **DeMiguel, Garlappi & Uppal (2009)** "Optimal Versus Naive Diversification." *RFS*
  22(5), 1915–1953 — **1/N** is the benchmark every optimizer must beat OOS. `[L3]`

**Covariance estimation (the load-bearing L2 input):**
- **Ledoit & Wolf (2004)** "Honey, I Shrunk the Sample Covariance Matrix." *JPM* 30(4),
  110–119 — the well-known **linear shrinkage** estimator. `[L2]`
- **Ledoit & Wolf (2003)** *J. Empirical Finance* 10(5), 603–621 — shrinkage toward a
  single-index (factor) target. `[L2]`
- **Ledoit & Wolf (2017)** "Nonlinear Shrinkage… Markowitz Meets Goldilocks." *RFS*
  30(12), 4349–4388 — eigenvalue-wise **nonlinear shrinkage**, asymptotically optimal.
  `[L2]`

**Bayesian / view-blending & robust construction:**
- **Black & Litterman (1992)** "Global Portfolio Optimization." *FAJ* 48(5), 28–43 —
  equilibrium anchor + Bayesian views; tames MVO instability. `[L3]`
- **Meucci (2005)** *Risk and Asset Allocation.* Springer — estimation-risk-aware
  allocation. `[L3/L2]`
- **Meucci (2008)** "Fully Flexible Views." *Risk* 21(10) — **Entropy Pooling**;
  generalizes BL to arbitrary priors/views and stress tests. `[L3/L6]`
- **López de Prado (2016)** "Building Diversified Portfolios that Outperform Out of
  Sample." *JPM* 42(4), 59–69 — **Hierarchical Risk Parity (HRP)**; no matrix
  inversion. `[L3]`

**Risk parity & active-management theory:**
- **Roncalli (2013)** *Introduction to Risk Parity and Budgeting.* CRC — the definitive
  risk-parity text. `[L3]`
- **Qian (2005/2006)** "Risk Parity Portfolios" (PanAgora WP) + "On the Financial
  Interpretation of Risk Contribution" *JOIM* 4(4) — coins **risk parity**; risk
  contribution = expected-loss contribution. `[L3]`
- **Grinold & Kahn (2000)** *Active Portfolio Management*, 2nd ed. McGraw-Hill — the
  **Fundamental Law** (IR ≈ IC·√Breadth), IR, transfer coefficient. `[L3]`

**Growth-optimal / Kelly sizing:**
- **Kelly (1956)** "A New Interpretation of Information Rate." *Bell System Tech. J.*
  35(4), 917–926 — maximize expected log wealth → long-run growth. `[L3]`
- **Thorp (2006)** "The Kelly Criterion in Blackjack, Sports Betting, and the Stock
  Market." *Handbook of Asset & Liability Management* Vol. 1 — Kelly in markets;
  fractional-Kelly rationale. `[L3]`
- **MacLean, Thorp & Ziemba (eds., 2011)** *The Kelly Capital Growth Investment
  Criterion.* World Scientific — definitive collected volume. `[L3]`

**Risk measurement (L2/L6):**
- **Artzner, Delbaen, Eber & Heath (1999)** "Coherent Measures of Risk." *Math. Finance*
  9(3), 203–228 — the coherence axioms; **VaR is not subadditive**. `[L2/L6]`
- **Rockafellar & Uryasev (2000)** "Optimization of Conditional Value-at-Risk." *J. Risk*
  2(3), 21–41 — **CVaR/ES** minimization as a convex/LP problem. `[L6→L3]`
- **Jorion (2006)** *Value at Risk*, 3rd ed. McGraw-Hill — standard VaR reference. `[L2/L6]`
- **McNeil, Frey & Embrechts (2015)** *Quantitative Risk Management*, rev. ed. Princeton
  UP — EVT, copulas, coherent measures. `[L2/L6]`

---

## 5. Derivatives, stochastic modelling & econometrics `[L2/L0]`

**Derivatives pricing:**
- **Black & Scholes (1973)** *JPE* 81(3), 637–654 · **Merton (1973)** *Bell J. Econ.*
  4(1), 141–183 — continuous-time option pricing. `[L2]`
- **Merton (1976)** "…Discontinuous." *JFE* 3(1–2), 125–144 — **jump-diffusion**. `[L2]`
- **Cox, Ross & Rubinstein (1979)** *JFE* 7(3), 229–263 — the **binomial tree**;
  American options. `[L2/L0]`
- **Heston (1993)** *RFS* 6(2), 327–343 — **stochastic volatility**; smile/skew via
  characteristic functions. `[L2]`
- **Hull** *Options, Futures, and Other Derivatives*, 11th ed. (2021). Pearson — standard
  reference across derivatives & Greeks. `[L2]`
- **Gatheral (2006)** *The Volatility Surface.* Wiley — local/stochastic vol,
  calibration. `[L2]`
- **Glasserman (2003)** *Monte Carlo Methods in Financial Engineering.* Springer — the
  **MC engine** spec: variance reduction, quasi-MC, Greeks by simulation. `[L2/L0]`

**Stochastic calculus (texts):**
- **Shreve (2004)** *Stochastic Calculus for Finance* **I** (binomial) & **II**
  (continuous-time). Springer — canonical. `[L2]`
- **Øksendal (2003)** *Stochastic Differential Equations*, 6th ed. Springer · **Björk
  (2019)** *Arbitrage Theory in Continuous Time*, 4th ed. Oxford UP · **Joshi (2008)**
  *The Concepts and Practice of Mathematical Finance*, 2nd ed. Cambridge UP. `[L2/L0]`

**Time series & econometrics:**
- **Engle (1982)** *Econometrica* 50(4) — **ARCH** (Nobel 2003) · **Bollerslev (1986)**
  *J. Econometrics* 31(3) — **GARCH**. `[L2 vol]`
- **Engle & Granger (1987)** *Econometrica* 55(2), 251–276 — **cointegration** + ECM
  (basis for stat-arb spreads) · **Johansen (1988, 1991)** — multivariate cointegration
  tests. `[L2]`
- **Hamilton (1989)** *Econometrica* 57(2), 357–384 — **Markov regime-switching** ·
  **Hamilton (1994)** *Time Series Analysis.* Princeton UP — the graduate reference.
  `[L2]`
- **Tsay (2010)** *Analysis of Financial Time Series*, 3rd ed. Wiley — applied financial
  econometrics. `[L2]`
- **Campbell, Lo & MacKinlay (1997)** *The Econometrics of Financial Markets.* Princeton
  UP · **Cochrane (2005)** *Asset Pricing*, rev. ed. Princeton UP — SDF framework. `[L2]`
- **Harvey, A. C. (1989)** *Forecasting, Structural Time Series Models and the Kalman
  Filter.* Cambridge UP — state-space / **Kalman** reference. `[L2/L0]`
- **Elliott, van der Hoek & Malcolm (2005)** "Pairs Trading." *Quantitative Finance*
  5(3), 271–276 — OU spread + Kalman; ties stochastic modelling to stat-arb. `[L2/L4]`

*Also:* Wilmott (2006) *Paul Wilmott on Quantitative Finance* (PDE/numerics); Rebonato
(2004) *Volatility and Correlation* (smile modelling).

---

## 6. Fundamental valuation & financial-statement analysis `[L2/L4]`

**Valuation & FSA:**
- **Damodaran** *Investment Valuation*, 3rd ed. (2012). Wiley — the canonical DCF /
  relative-valuation reference. Plus **datasets** (NYU Stern, updated annually): industry
  betas, ERP, margins, cost of capital. `[L2/L4]`
- **Damodaran** *The Dark Side of Valuation*, 3rd ed. (2018). **Pearson/FT Press** (not
  Wiley) — valuing young/distressed/cyclical/financial firms; feeds archetypes. `[L2/L4]`
- **Damodaran** *Narrative and Numbers* (2017). Columbia UP — the story→driver→DCF
  bridge underpinning archetype framing. `[L2/XC]`
- **Koller, Goedhart & Wessels (McKinsey)** *Valuation: Measuring and Managing the Value
  of Companies*, **8th ed. (2025)**. Wiley — value drivers (ROIC, growth, WACC). `[L2/L4]`
- **Penman** *Financial Statement Analysis and Security Valuation*, 5th ed. (2013).
  McGraw-Hill — **residual-income** / accounting-based valuation. `[L2/L4]`
- **Graham & Dodd** *Security Analysis*, 6th ed. (2008; orig. 1934). McGraw-Hill ·
  **Graham** *The Intelligent Investor* (rev. 2003; orig. 1949) — margin of safety. `[L4/XC]`
- **Rappaport & Mauboussin** *Expectations Investing* (rev. 2021; orig. 2001). Columbia
  Business School Publishing — founding text of **reverse DCF**. `[L2/L4]`
- **CFA Institute Investment Series:** *Equity Asset Valuation*, 4th ed. (2020) —
  DDM/FCFF/FCFE/RIM/multiples · *International Financial Statement Analysis*, 4th ed.
  (2020). Wiley. `[L2/L4]`
- **Greenblatt** *The Little Book That Still Beats the Market* (2010; orig. 2005). Wiley
  — the **Magic Formula** (ROIC + earnings yield). `[L4]`

**Distress / fraud / quality scores (primary sources):**
- **Altman (1968)** *J. Finance* 23(4), 589–609 — **Z-score** (distress). `[L2→L4]`
- **Beneish (1999)** *FAJ* 55(5), 24–36 — **M-score** (earnings manipulation). `[L2→L4]`
- **Piotroski (2000)** *J. Accounting Research* 38(Suppl.), 1–41 — **F-score** (quality).
  `[L2→L4]`
- **Ohlson (1980)** *J. Accounting Research* 18(1), 109–131 — **O-score** (distress). `[L2]`
- **Sloan (1996)** *The Accounting Review* 71(3), 289–315 — the **accruals anomaly**. `[L2/L4]`
- *Practitioner red-flag companions (verify before citing):* Schilit, *Financial
  Shenanigans* (McGraw-Hill); Fridson & Alvarez, *Financial Statement Analysis: A
  Practitioner's Guide* (Wiley).

---

## 7. Behavioral, foundational & skeptical `[XC]`

The humility layer — why most backtests lie and most edges decay.
- **Taleb** *Fooled by Randomness* (2001); *The Black Swan* (2007); *Dynamic Hedging*
  (1997, the technical one); *Antifragile* (2012). — luck vs skill, fat tails, convexity.
- **Mandelbrot & Hudson (2004)** *The (Mis)Behavior of Markets.* Basic Books — fractal
  risk; critique of Gaussian finance. *(Subtitle differs by edition — see note.)*
- **Kahneman (2011)** *Thinking, Fast and Slow.* FSG — heuristics & biases.
- **Shiller (2000/2015)** *Irrational Exuberance.* Princeton UP — bubbles vs strict EMH.
- **Malkiel (1973/2023)** *A Random Walk Down Wall Street.* Norton — the EMH/indexing
  baseline every active signal must beat.

---

## 8. CFA Body of Knowledge — completeness check

The CFA curriculum's 10 topic areas, used as an independent "no gaps" audit of our
taxonomy. (Names/weights per current CFA Institute Level I.)

| CFA topic area | Level I weight | Curriculum home (`docs/CURRICULUM.md`) |
|---|---|---|
| Ethical & Professional Standards | 15–20% | Part IX.6, VI.7 (governance) |
| Quantitative Methods | 6–9% | Part II |
| Economics | 6–9% | Part III.1 |
| Financial Statement Analysis | 11–14% | **Part IV.1–.2** |
| Corporate Issuers | 6–9% | Part IV.2–.3 |
| Equity Investments | 11–14% | **Parts III.5–.6, IV.4–.5** |
| Fixed Income | 11–14% | **Part IV.6–.7** |
| Derivatives | 5–8% | **Part V** |
| Alternative Investments | 7–10% | V.1 futures; VII.7 institutions `[survey]`; crypto out |
| Portfolio Management | 8–12% | **Parts VII, IX.5** |

*Note:* since 2025, CFA Level III offers three specialized pathways (Portfolio
Management, Private Markets, Private Wealth). Every CFA topic area maps to a
curriculum Part — the one deliberate partial is Alternative Investments (crypto and
private markets at survey depth), an honest free-data boundary, not a gap.

---

## 9. Open-source prior art — code to learn from `[borrow, don't inherit]`

- **pysystemtrade** (Carver; now `pst-group`) — the closest prior art done properly:
  forecast → vol-scaled position → portfolio, first-class cost/financing, futures
  roll/back-adjustment. **Study for L1/L3/L5.**
- **vectorbt** (polakowo) — vectorized NumPy/Numba backtesting over thousands of param
  combos. **Model for our fast vectorized research engine (L5).**
- **zipline-reloaded** (stefan-jansen) — event-driven pipeline + point-in-time bundles
  that prevent lookahead. **Model for the event-driven engine (L5).** (Original
  Quantopian zipline is unmaintained.)
- **QuantConnect / LEAN** — production multi-asset data/brokerage/execution abstractions
  with a genuine backtest→live parity path. **Reference for L5↔L7 continuity.**
- **PyPortfolioOpt** (robertmartin8) — clean MVO, Black-Litterman, shrinkage, HRP.
  **Reference implementations for L3.**
- **bt / ffn** (pmorissette) — composable select→weigh→rebalance `Algo` blocks. **Model
  for L4.5 allocation/rebalancing.**
- **backtrader** (mementum) — ergonomic Strategy/Indicator/Analyzer API (borrow design,
  not the dependency — largely unmaintained).
- *Also worth a look:* NautilusTrader (high-perf event-driven live/backtest);
  Riskfolio-Lib (advanced optimization); quantstats / pyfolio / empyrical (tearsheets &
  performance analytics); Alphalens (factor analytics).

---

## 10. "Start here" shortlist

If you read only a handful before building each layer:
- **Discipline (read first):** López de Prado, *Advances in Financial ML* (2018) +
  Bailey & López de Prado, "Deflated Sharpe" (2014) + Arnott-Harvey-Markowitz protocol
  (2019).
- **Systematic trading:** Carver, *Systematic Trading* (2015) + Clenow, *Following the
  Trend* (2013).
- **Factors/premia:** Ang, *Asset Management* (2014) + Ilmanen, *Expected Returns* (2011).
- **Portfolio/risk:** Ledoit-Wolf (2004) + López de Prado HRP (2016) + Roncalli (2013).
- **Derivatives/stochastic:** Hull (11th ed.) + Shreve II + Glasserman (2003).
- **Fundamentals:** Damodaran, *Investment Valuation* (3rd ed.) + Penman (5th ed.) +
  Rappaport & Mauboussin, *Expectations Investing* (reverse DCF).

---

## 11. Empirical asset-pricing methodology — the researcher's toolkit `[Curriculum III.5]`

The papers behind sorts, cross-sectional regressions, and alpha tests — the *methods*
of Part III.5, distinct from the factors themselves (§2).

**The core machinery:**
- **Fama & MacBeth (1973)** *JPE* 81(3), 607–636 — the two-pass cross-sectional
  regression; still the workhorse for pricing characteristics.
- **Shanken (1992)** *RFS* 5(1), 1–33 — errors-in-variables correction: FM standard
  errors are understated because pass-two regressors are estimated betas. *(Pages
  1–33; the circulating "1–55" is a miscitation.)*
- **Gibbons, Ross & Shanken (1989)** *Econometrica* 57(5), 1121–1152 — the **GRS
  test**: exact finite-sample joint test that all alphas are zero.
- **Black, Jensen & Scholes (1972)** in *Studies in the Theory of Capital Markets*
  (Praeger), 79–121 — the original beta-sorted time-series tests; the flat SML.
- **Newey & West (1987)** *Econometrica* 55(3), 703–708 — HAC standard errors.
- **Petersen (2009)** *RFS* 22(1), 435–480 — clustered vs FM standard errors in
  panels; the referee's reference.
- **Hansen (1982)** *Econometrica* 50(4), 1029–1054 — GMM: the frame under which FM,
  time-series, and SDF tests are all special cases.

**Design & interpretation:**
- **Daniel & Titman (1997)** *JF* 52(1), 1–33 — characteristics vs covariances via
  double sorts.
- **Kan & Zhang (1999)** *JF* 54(1), 203–235 — useless factors appear spuriously
  priced in two-pass regressions.
- **Lewellen, Nagel & Shanken (2010)** *JFE* 96(2), 175–194 — why high R² on 25
  size/B-M portfolios is a low hurdle; expanded test assets, GLS R².
- **Barillas & Shanken (2017)** *RFS* 30(4) "Which Alpha?" and **(2018)** *JF* 73(2),
  715–754 — modern factor-model comparison (test assets drop out; Bayesian model
  probabilities).
- **Novy-Marx & Velikov (2016)** *RFS* 29(1), 104–147 — anomalies net of transaction
  costs; whether a sort survives implementation.

**The how-to text:** **Bali, Engle & Murray (2016)** *Empirical Asset Pricing: The
Cross Section of Stock Returns.* Wiley — step-by-step sorts, breakpoints, FM
mechanics, winsorization, CRSP/Compustat handling.

**Modern cross-section:** **Gu, Kelly & Xiu (2020)** *RFS* 33(5), 2223–2273 (ML
benchmark & OOS-R² protocol) · **Kelly, Pruitt & Su (2019)** *JFE* 134(3) (IPCA) ·
**Kozak, Nagel & Santosh (2020)** *JFE* 135(2) (shrinking the SDF) · **Jensen, Kelly
& Pedersen (2023)** *JF* 78(5), 2465–2518 (Bayesian replication counterpoint + the
JKP global factor data).

**Data conventions:** **Shumway (1997)** *JF* 52(1), 327–340 and **Shumway & Warther
(1999)** *JF* 54(6) — delisting-bias corrections (−30% NYSE/AMEX, −55% Nasdaq) ·
**Ken French Data Library** (factors, sorted portfolios, breakpoints — the field's
sorting conventions) · **Chen & Zimmermann (2022)** open-source predictor library
(§1 #14).

## 12. Fixed income — curves, duration, term structure `[Curriculum IV.6–.7]`

**Texts:** **Tuckman & Serrat (2022)** *Fixed Income Securities*, 4th ed. Wiley — the
practitioner curve/duration/hedging toolkit (primary teaching text) · **CFA Institute
(2022)** *Fixed Income Analysis*, 5th ed. Wiley · **Fabozzi (2021)** *Handbook of
Fixed Income Securities*, 9th ed. McGraw-Hill (reference volume).

**Curve construction:** **Nelson & Siegel (1987)** *J. Business* 60(4), 473–489 —
the parsimonious functional form · **Svensson (1994)** NBER w4871 (working paper
only) — the six-parameter extension behind most central-bank curves · **Hagan & West
(2006)** *Applied Mathematical Finance* 13(2), 89–129 — production bootstrapping &
monotone-convex interpolation.

**Factor structure:** **Litterman & Scheinkman (1991)** *J. Fixed Income* 1(1),
54–61 — level/slope/curvature via PCA · **Diebold & Li (2006)** *J. Econometrics*
130(2), 337–364 — dynamic Nelson-Siegel forecasting · **Diebold & Rudebusch (2013)**
*Yield Curve Modeling and Forecasting.* Princeton UP.

**Term-structure models (lineage):** **Vasicek (1977)** *JFE* 5(2), 177–188 ·
**Cox, Ingersoll & Ross (1985)** *Econometrica* 53(2), 385–407 · **Ho & Lee (1986)**
*JF* 41(5) — first curve-calibrated model · **Hull & White (1990)** *RFS* 3(4),
573–592 · **Heath, Jarrow & Morton (1992)** *Econometrica* 60(1), 77–105 *(not
77–106)* · **Duffie & Kan (1996)** *Math. Finance* 6(4) — the affine class ·
Black-Derman-Toy (1990) *FAJ* 46(1) *(page range secondary-sourced)*.

**Expectations hypothesis & term premia:** **Fama & Bliss (1987)** *AER* 77(4),
680–692 *(not 680–699)* · **Campbell & Shiller (1991)** *REStud* 58(3), 495–514 —
the canonical EH-failure pair · **Cochrane & Piazzesi (2005)** *AER* 95(1), 138–160
— the tent-shaped return-forecasting factor · **Adrian, Crump & Moench (2013)** *JFE*
110(1), 110–138 — the ACM term premium (NY Fed publishes daily) · Kim & Wright
(2005) FEDS WP 2005-33 (working paper; series on FRED).

**Free data (what makes the deep track executable):** **Gürkaynak, Sack & Wright
(2007)** *J. Monetary Economics* 54(8), 2291–2304 — the Fed's fitted Treasury curve,
daily since 1961, free (+ the 2010 TIPS companion) · **Liu & Wu (2021)** *JFE*
142(3) — modern reconstruction, free monthly zeros · **BIS Papers No. 25** — which
method each central bank uses.

## 13. Microstructure, transaction costs & execution `[Curriculum VIII.1–.2]`

**Theory of spreads & impact:** **Kyle (1985)** *Econometrica* 53(6), 1315–1335 —
lambda, depth, strategic informed trading · **Glosten & Milgrom (1985)** *JFE* 14(1),
71–100 — adverse-selection spreads · **Roll (1984)** *JF* 39(4), 1127–1139 — the
implicit spread estimator from prices alone.

**Empirical liquidity & the impact law:** **Amihud (2002)** *J. Financial Markets*
5(1), 31–56 — the ILLIQ measure · **Tóth et al. (2011)** *Physical Review X* 1(2),
021006 — the square-root metaorder impact law (latent liquidity) · **Gatheral
(2010)** *Quantitative Finance* 10(7), 749–759 — no-dynamic-arbitrage constraints on
impact/decay · **Almgren, Thum, Hauptmann & Li (2005)** *Risk* 18(7) — fitted impact
on ~700k real orders · **Frazzini, Israel & Moskowitz (2018)** SSRN 3229719 *(working
paper)* — $1.7T of live institutional executions; realized costs far below academic
estimates.

**Optimal execution & market making:** **Bertsimas & Lo (1998)** *J. Financial
Markets* 1(1), 1–50 — the first DP execution model · **Almgren & Chriss** "Optimal
Execution of Portfolio Transactions," *J. Risk* 3(2), Winter 2000/01, 5–39 *(year
cited both ways; this is the same issue)* — the mean-variance execution frontier ·
**Obizhaeva & Wang (2013)** *J. Financial Markets* 16(1), 1–32 — execution with LOB
resilience · **Perold (1988)** *JPM* 14(3), 4–9 — implementation shortfall ·
**Avellaneda & Stoikov (2008)** *Quantitative Finance* 8(3), 217–224 — inventory-based
market making.

**Texts:** **Harris (2003)** *Trading and Exchanges.* Oxford UP — the institutional
foundation · **Hasbrouck (2007)** *Empirical Market Microstructure.* Oxford UP —
the econometrics · **O'Hara (1995)** *Market Microstructure Theory.* Blackwell ·
**Foucault, Pagano & Röell (2013)** *Market Liquidity.* Oxford UP — the modern
graduate text · **Cartea, Jaimungal & Penalva (2015)** *Algorithmic and
High-Frequency Trading.* Cambridge UP — stochastic control for trading ·
**Bouchaud, Bonart, Donier & Gould (2018)** *Trades, Quotes and Prices.* Cambridge UP
— the modern empirical LOB reference.

---

*Verification: all §1–§6, §8, §11–§13 citations confirmed against primary
publisher/journal records (Wiley, Springer, Cambridge/Oxford UP, Princeton UP,
McGraw-Hill, Pearson, JFE/JF/RFS/Econometrica/AER, SSRN/NBER, CFA Institute, Fed/BIS).
Working papers and page-range discrepancies flagged inline. Items marked "verify
before citing" were surfaced as leads and not independently confirmed.*
