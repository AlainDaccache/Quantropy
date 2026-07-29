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

# Module 5 (V.2–.3) — Options: Trees, Black-Scholes, Greeks `[deep]`

**Learning objectives.** After this lesson you can: (1) price a European option
two independent ways and show they agree; (2) verify every Greek against
bump-and-reprice; (3) state exactly when early exercise matters; (4) invert a
price into the market's implied volatility — and know which quotes to refuse.

## 1. Intuition

An option's price is the cost of *manufacturing* it: hold delta units of stock,
adjust continuously, and the payoff replicates — no forecast of direction ever
enters. Everything below validates against published numbers: Hull's classic
example (S=42, K=40, T=0.5, r=10%, σ=20%) is the externally checkable reference.

```{code-cell} ipython3
from quantropy.pricing import binomial_price, bs_price

HULL = dict(s=42.0, k=40.0, t=0.5, r=0.10, sigma=0.20)
c, p = bs_price(**HULL, kind="call"), bs_price(**HULL, kind="put")
f"call {c:.3f} (Hull: 4.76), put {p:.3f} (Hull: 0.81)"
```

## 2. Two roads, one price

The CRR binomial tree knows nothing of the BSM formula — only no-arbitrage on a
lattice. It must converge to the same number:

```{code-cell} ipython3
import pandas as pd

pd.Series({n: binomial_price(**HULL, kind="call", steps=n) for n in (10, 50, 250, 1000)},
          name="tree price").round(4).to_frame().assign(bsm=round(c, 4))
```

Two independent derivations agreeing to a third decimal is what "the model is
implemented correctly" *means* — the same cross-validation logic as the
bootstrap round-trip in the curve lesson.

## 3. Greeks — and the test that keeps them honest

```{code-cell} ipython3
from quantropy.pricing import bs_greeks

g = bs_greeks(**HULL, kind="call")
pd.Series(g).round(4)
```

Every analytic Greek in this library is CI-tested against bump-and-reprice
(`tests/test_options.py`): if the closed form and the finite difference ever
disagree, the build fails. Two structural facts worth memorizing — **gamma and
vega are identical for calls and puts** (same second derivative, same vol
exposure), and `delta_call − delta_put = e^{−qT}` (parity, differentiated).

## 4. Early exercise: when American ≠ European

```{code-cell} ipython3
eu_put = binomial_price(**HULL, kind="put", style="european", steps=500)
am_put = binomial_price(**HULL, kind="put", style="american", steps=500)
eu_call = binomial_price(**HULL, kind="call", style="european", steps=500)
am_call = binomial_price(**HULL, kind="call", style="american", steps=500)
f"put premium for early exercise: {am_put-eu_put:.4f} | call premium: {am_call-eu_call:.6f}"
```

The put carries a real early-exercise premium (deep ITM, take the cash and earn
r). The call's premium is **zero without dividends** — Merton's theorem, verified
numerically rather than recited.

## 5. Implied volatility — reading the market's parameter

```{code-cell} ipython3
from quantropy.pricing import implied_vol

market_price = 4.759
iv = implied_vol(market_price, 42.0, 40.0, 0.5, 0.10, "call")
f"implied vol from the quoted price: {iv:.4%}"
```

Inverting price→vol is how the market actually quotes options; the *smile* —
different strikes implying different vols — is the empirical proof that BSM's
constant-σ assumption fails, and the doorway to Part V.4 (surface via QuantLib,
SVI). Note the guardrail: a price below the no-arbitrage floor **raises** rather
than returning nonsense — refusing bad quotes is part of the model.

## 6. Pitfalls

- **BSM's assumptions are the syllabus of its failures**: constant vol (smile),
  continuous hedging (gap risk), no jumps (crash premia), lognormal returns
  (fat tails — Part II.1). The formula's value is being *wrong in measurable
  ways*.
- **Theta conventions bite**: ours is per-year; desks quote per-day. Vega per
  vol-point vs per-unit likewise. Check units before comparing to a broker
  screen.
- **Trees before Monte Carlo**: for American exercise, backward induction is the
  honest baseline; Longstaff-Schwartz (BOUNDARIES) is for path-dependence, not a
  substitute.

## 7. Exercises

1. Reproduce the §2 convergence table for the *American* put. Does it converge
   from above or below, and why?
2. Verify put-call parity numerically with q = 3% and prove which side of the
   identity dividend yield enters.
3. Plot delta over S ∈ [20, 60] for the Hull call at T = 0.5 and T = 0.05 —
   explain the sharpening around K in trading terms (pin risk).

## Further reading

`docs/REFERENCES.md` §5 — Black-Scholes (1973), Merton (1973), Cox-Ross-
Rubinstein (1979), Hull; Gatheral for where the smile leads.
