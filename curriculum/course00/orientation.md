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

# Module 0 — Orientation `[deep]`

**Learning objectives.** After this lesson you can: (1) explain what this curriculum
is and how its honesty labels work; (2) run Quantropy code yourself; (3) state the two
ideas that govern everything downstream — *compounding* and *why most backtests lie*.

## 1. Intuition

Quant finance is compounding plus statistics, wrapped in institutional discipline.
This first lesson proves the machinery works: the code below is not a screenshot —
it executes against the real `quantropy` library every time this book is built.
If it breaks, the build fails. That is this project's core promise: **nothing you
read here is stale.**

## 2. Applied — your first Quantropy code

The time value of money is the atom of all valuation. A dollar today is worth more
than a dollar tomorrow, because today's dollar can compound:

```{code-cell} ipython3
from quantropy.core import tvm

# $10,000 invested at 6% for 30 years
tvm.future_value(10_000, 0.06, 30)
```

Saving is a *growing annuity*: contribute yearly, grow the contribution with your
income, compound the balance.

```{code-cell} ipython3
# $8,000/yr, growing 6%/yr, earning 3%/yr, for 10 years
tvm.future_value_annuity(contribution=8_000, rate=0.03, periods=10, growth=0.06)
```

And the single most under-appreciated fact in finance — the asymmetry of loss:

```{code-cell} ipython3
from quantropy.core import returns

# +10% then -10% does NOT get you back to zero
returns.cumulative_return([0.10, -0.10])
```

## 3. Interpret

That last number is negative. Gains and losses do not cancel: a −50% drawdown needs
+100% to recover. Every risk-management idea in this curriculum — volatility
targeting, drawdown circuit breakers, position sizing — is downstream of this
asymmetry.

## 4. Pitfalls

The library's `annualize_volatility` uses the square-root-of-time rule — which
*assumes independent returns*. Real returns autocorrelate, so real risk is often
understated. This is the pattern you will see throughout: **every formula ships with
the assumption that breaks it.** The single largest way quantitative work goes wrong
is not bad math but silent assumptions — look-ahead in a backtest, survivorship in a
universe, multiple testing in a "discovery." The research-honesty module (Module 8) exists to
catch these, and every lesson ends the way this one does: with what breaks.

## 5. Exercises

1. You need \$1M in 25 years and can earn 5%. How much must you invest today?
   (*Answer with* `tvm.present_value` — expect ≈ \$295,303.)
2. Verify the −50%/+100% claim with `returns.cumulative_return`.
3. At 1% monthly volatility, what annual volatility does the square-root rule imply?
   Why might the truth be higher?

## Further reading

CFA Level I Quantitative Methods; `docs/REFERENCES.md` §8 (the CFA map) and §7
(the humility layer — Taleb, Mandelbrot).
