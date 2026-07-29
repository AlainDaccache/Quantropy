---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Module 7 (VII.2–.4) — The Inputs Problem: Why Optimizers Fail and What Fixes Them `[deep]`

**Learning objectives.** After this lesson you can: (1) demonstrate — on real data,
out-of-sample — that shrinkage beats the sample covariance where it matters;
(2) show why the tangency portfolio is an error maximizer; (3) build risk-parity
and HRP allocations and read a risk-contribution report.

## 1. Intuition

Markowitz gave portfolio construction its objective; estimation error decides
whether the answer means anything. An optimizer *maximizes* along whatever noise
the inputs contain — overweighting every overstated return and understated risk.
The fixes are not better intentions but better inputs (shrinkage) and objectives
that need fewer inputs (risk parity, HRP). We demonstrate on the real French 25
portfolios (committed fixture, monthly 1963–2024).

```{code-cell} ipython3
import numpy as np
import pandas as pd

ff3 = pd.read_csv("../../tests/fixtures/ff3_monthly.csv", index_col=0, parse_dates=True)
p25 = pd.read_csv("../../tests/fixtures/p25_monthly.csv", index_col=0, parse_dates=True)
rets = p25.sub(ff3["RF"], axis=0).dropna()
rets.shape
```

## 2. The experiment: sample vs shrinkage, judged out-of-sample

25 assets estimated on 60 months is exactly the N~T regime where the sample
covariance is noise wearing a suit. Protocol: each year, estimate Σ on the past 60
months, hold the **minimum-variance** portfolio for the next 12, repeat — and
judge by *realized OOS volatility* (the thing min-var claims to minimize):

```{code-cell} ipython3
from quantropy.portfolio import ledoit_wolf, min_variance, sample_covariance

oos = {"sample": [], "ledoit_wolf": []}
dates = rets.index
for start in range(60, len(dates) - 12, 12):
    est, hold = rets.iloc[start - 60 : start], rets.iloc[start : start + 12]
    for name, estimator in [("sample", sample_covariance), ("ledoit_wolf", ledoit_wolf)]:
        w = min_variance(estimator(est))
        oos[name].extend((hold @ w).tolist())

result = pd.Series({k: np.std(v, ddof=1) * np.sqrt(12) for k, v in oos.items()})
result.round(4)  # annualized OOS volatility — lower is the entire point
```

Same objective, same data, same rebalancing — the only difference is the
covariance estimator. Shrinkage wins where it counts: **out of sample**. (The
sample-based weights also swing harder between rebalances — estimation noise
becomes turnover, which becomes costs.)

## 3. The error maximizer, exhibited

Give tangency (max-Sharpe) weights an *estimated* mean vector and watch:

```{code-cell} ipython3
from quantropy.portfolio import tangency

est = rets.iloc[-120:]                       # ten years to "estimate" means
w_tan = tangency(ledoit_wolf(est), est.mean())
w_min = min_variance(ledoit_wolf(est))
pd.Series({
    "tangency max |weight|": w_tan.abs().max(),
    "tangency gross leverage": w_tan.abs().sum(),
    "min-var max |weight|": w_min.abs().max(),
}).round(2)
```

Triple-digit percentage positions from a decade of monthly means — not a bug, the
*definition*: `Σ⁻¹μ` amplifies exactly the components of μ it should distrust.
This is why expected returns are the most dangerous input in finance (DeMiguel's
1/N result, REFERENCES §4, is this lesson run at journal scale).

## 4. Objectives that need fewer inputs

```{code-cell} ipython3
from quantropy.portfolio import hrp, risk_contributions, risk_parity

cov = ledoit_wolf(est)
w_erc = risk_parity(cov)
w_hrp = hrp(cov)
pd.DataFrame({
    "ERC risk contribution (should be flat)": risk_contributions(w_erc, cov).describe()[["min", "max"]],
    "HRP weight range": w_hrp.describe()[["min", "max"]],
}).round(4)
```

Risk parity equalizes what you actually care about — *risk* — with no expected
returns anywhere; HRP gets robustness a second way, replacing matrix inversion
with clustering (it never inverts Σ at all). Both are tested against ground truth
in `tests/test_m5_portfolio_risk.py`.

## 5. Pitfalls

- **Shrinkage is not magic** — it trades variance for bias optimally *within a
  target family*; a grotesquely wrong target still hurts. Factor-structure
  targets (Barra-style) are the industrial next step.
- **Min-var concentrates in low-vol assets** — that's its job; without weight
  caps it will happily become a utilities fund.
- **Constraints are information**: a long-only bound often improves OOS
  performance precisely because it truncates estimation error (Jagannathan-Ma's
  "wrong constraints help" result — worth reading before adding fancier math).
- Monthly data, 25 assets is the *demo* regime; daily data across hundreds of
  names moves the numbers, not the moral.

## 6. Exercises

1. Rerun §2 with `target="identity"`. Which target wins here, and why might
   constant-correlation suit equity portfolios?
2. Add equal-weight (1/N) to the §2 horse race. Where does it land, and what does
   that say about the marginal value of optimization?
3. Compute §3's tangency weights using only the last 36 months of means. How much
   worse do the extremes get?

## Further reading

`docs/REFERENCES.md` §4 — Ledoit-Wolf (2003, 2004, 2017), Michaud (1989),
DeMiguel-Garlappi-Uppal (2009), López de Prado HRP (2016), Roncalli (2013).
