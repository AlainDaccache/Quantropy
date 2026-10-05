# Research design, statistics and machine learning

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Start with a falsifiable question and an economic mechanism before selecting a technique. Declare universe, sample, input availability, benchmark, costs, evaluation metric and stopping rules. Save every trial and discarded idea, because the selected winner is drawn from the whole search.

Use chronological out-of-sample and walk-forward evaluation appropriate to the horizon. Overlapping labels and serial dependence can contaminate naive splits. Purging/embargo must be tailored to feature and label information intervals, not applied as magical constants. Keep a final holdout untouched by model selection; use it sparingly with a documented promotion decision. Backtest-overfitting analysis provides tools, not a guarantee. [Bailey et al.](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf).

Support uncertainty estimates, dependence-aware bootstrap, robustness across subperiods/universes, regime analysis and parameter stability. Evaluate economic significance after all costs. Compare simple baselines before complex ML. Stationarity, cointegration, volatility models, Bayesian inference, causal/event studies and alternative-data NLP belong in reviewed model modules with applicability assumptions.

Fit imputation, scaling, feature selection and calibration only within training partitions. Pipeline tooling helps; it does not automatically enforce release-time causality. [scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html). Monitor feature/label drift, calibration and degradation in production. NLP/LLM outputs require provenance, verification and reproducibility; they should not autonomously turn untrusted retrieved text into orders.

Acceptance: append-future-data and prefix replay preserve earlier features/decisions; reproducible runs pin code/config/data/seeds; selection counts include failures; no chosen model sees its evaluation labels; uncertainty and negative results appear in the report. Prediction accuracy alone is insufficient if economic payoffs, turnover or downside are poor.

## Coverage checklist

- Hypothesis registry and experiment manifests
- Time-aware train validation test splits
- Purging embargo and overlapping labels
- Walk-forward and holdout governance
- Multiple-testing and selection bias
- Dependence-aware bootstrap uncertainty
- Stationarity cointegration econometrics
- Volatility forecasting and Bayesian models
- Feature pipelines and ML calibration
- NLP alternative data and LLM verification
- Regime robustness and drift monitoring
- Benchmark economic significance and costs

## Research sources

- [OVERFIT](sources.md#overfit)
- [SKLEARN](sources.md#sklearn)
- [MULTIPLE-TESTS](sources.md#multiple-tests)

[Knowledge base index](README.md)
