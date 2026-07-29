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

# Module 3 (III.5) — The Cross-Section: Sorts, Fama-MacBeth, GRS `[deep]`

**Learning objectives.** After this lesson you can: (1) estimate a risk premium
and defend its standard error; (2) run the complete factor-research process —
sorts → cross-sectional regressions → joint-alpha test; (3) reproduce three of the
most famous results in empirical asset pricing from real data.

## 1. Intuition

Asset pricing's empirical question is brutally simple: *do average returns line up
with anything?* The toolkit for answering it hasn't changed in fifty years — sort
assets into portfolios, regress returns on characteristics period by period, and
test whether a factor model's residual alphas are jointly zero. This lesson runs
all three on **real Ken French library data** (committed fixture, monthly,
1963-07–2024-12 — the canonical post-Compustat sample).

```{code-cell} ipython3
import pandas as pd

ff3 = pd.read_csv("../../tests/fixtures/ff3_monthly.csv", index_col=0, parse_dates=True)
p25 = pd.read_csv("../../tests/fixtures/p25_monthly.csv", index_col=0, parse_dates=True)
p25_excess = p25.sub(ff3["RF"], axis=0)          # excess returns, always
ff3.tail(3).round(4)
```

## 2. The equity premium — and why the *standard error* is the story

```{code-cell} ipython3
import numpy as np

mkt = ff3["Mkt-RF"]
mean_monthly = mkt.mean() * 100
t_stat = mkt.mean() / (mkt.std() / np.sqrt(len(mkt)))
f"{mean_monthly:.3f}%/month  (~{((1+mkt.mean())**12-1)*100:.1f}%/yr),  t = {t_stat:.2f}"
```

Sixty-one years of data and the t-statistic is only ~4. That is the discipline's
foundational humility: **premia are estimated with enormous noise**, which is why
every claim downstream needs the machinery below (and Module VI's deflation).

## 3. Sorts: the value premium, read straight off the 25 portfolios

The French 5×5 size/book-to-market portfolios *are* a double sort. The classic
value spread — high B/M minus low B/M within small caps:

```{code-cell} ipython3
value_spread = p25_excess["SMALL HiBM"] - p25_excess["SMALL LoBM"]
f"small-cap value spread: {value_spread.mean()*100:.2f}%/month, t = {value_spread.mean()/(value_spread.std()/np.sqrt(len(value_spread))):.2f}"
```

(Our own `portfolio_sorts` builds these buckets from raw characteristics — and
**lags the characteristic internally**, so sorting on unknowable information is
impossible by construction. The self-fulfilling sort is the classic rookie
backtest.)

## 4. Fama-MacBeth: pricing the cross-section

The two-pass procedure: estimate betas in the time series, then regress returns on
betas **period by period** — the time series of slopes estimates the premia, with
Newey-West *and* Shanken corrections on the t-stats (pass-two regressors are
estimated, so naive standard errors overstate confidence):

```{code-cell} ipython3
from quantropy.research import two_pass_fama_macbeth

fm = two_pass_fama_macbeth(p25_excess, ff3[["Mkt-RF", "SMB", "HML"]])
summary = pd.DataFrame({
    "premium %/mo": fm.premia * 100,
    "t (Newey-West)": fm.t_stats,
    "t (Shanken)": fm.shanken_t_stats,
}).round(2)
summary
```

Note the market premium estimated from the cross-section sits *below* its
time-series mean (~0.59%/month from §2) — the **flat security market line** of
Black-Jensen-Scholes (1972), alive and well fifty years later.

## 5. GRS: the verdict on a factor model

Does FF3 price the 25 portfolios? The Gibbons-Ross-Shanken test asks whether all
25 time-series alphas are *jointly* zero:

```{code-cell} ipython3
from quantropy.research import grs_test

res = grs_test(p25_excess, ff3[["Mkt-RF", "SMB", "HML"]])
f"GRS = {res.statistic:.2f},  p = {res.p_value:.2e}  ->  rejected"
```

The famous answer: **rejected decisively** — the model that *defined* the factors
still can't fully price the portfolios sorted on them. Every "my factor model
works" claim you will ever hear should be met with this test.

## 6. Pitfalls

- **Sorting conventions drive results**: NYSE vs all-stock breakpoints and equal-
  vs value-weighting flip published anomalies (Hou-Xue-Zhang's replication
  lesson, REFERENCES §11). Our sorts support both; report which you used.
- **The 25 portfolios are a low hurdle** for cross-sectional R² (Lewellen-Nagel-
  Shanken): their strong factor structure flatters models. GRS on the *alphas* is
  the harder, honest question.
- **Premia are lifecycle objects** (III.6): a t-stat from 1963 says little about
  post-publication, post-crowding decades. Estimation is where the work *starts*.

## 7. Exercises

1. Run `grs_test` on the CAPM alone (drop SMB/HML). Does one factor do better or
   worse than three? Reconcile with the GRS statistic's construction.
2. Compute the value spread in the *large*-cap row (BIG HiBM − BIG LoBM). Compare
   with §3 and explain the size-value interaction.
3. Use `portfolio_sorts` on 20 synthetic assets with planted mean differences and
   verify the spread recovers what you planted (see `tests/test_crosssection.py`).

## Further reading

`docs/REFERENCES.md` §11 — Fama-MacBeth (1973), Shanken (1992), GRS (1989),
Newey-West (1987), Bali-Engle-Murray (2016); §2 — Fama-French (1993).
