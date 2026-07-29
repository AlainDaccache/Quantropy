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

# Module 4 (IV.6–.7) — The Yield Curve, From the Fed's Own Numbers `[deep]`

**Learning objectives.** After this lesson you can: (1) build a discount curve
and price bonds off it; (2) bootstrap zeros from par yields and prove the
round-trip; (3) validate an NSS implementation against the Fed's published
parameters; (4) measure rate risk (duration, DV01, key-rates) and name the three
factors that drive the whole curve.

## 1. Intuition

Fixed income is Part I's discounting idea industrialized: one curve of discount
factors prices every default-free cash flow. The remarkable free lunch here is
data: the Fed publishes its fitted Treasury curve **daily back to 1961** —
zero yields, forwards, and the Svensson parameters themselves (Gürkaynak-Sack-
Wright; REFERENCES §12). This lesson runs on a committed month-end extract,
1990–2025.

```{code-cell} ipython3
import pandas as pd

gsw = pd.read_csv("../../tests/fixtures/gsw_monthly.csv", index_col=0, parse_dates=True)
row = gsw.loc["2024-12-31"]
row[["SVENY01", "SVENY05", "SVENY10", "SVENY30"]].round(3)  # zeros, cc %, end-2024
```

## 2. A curve you can price with

GSW publishes continuously-compounded percents; our `DiscountCurve` converts to
annually-compounded decimals in one visible place — conventions are decisions,
never defaults:

```{code-cell} ipython3
from quantropy.pricing import DiscountCurve, bond_price

curve = DiscountCurve.from_gsw_row(row)
p = bond_price(coupon=0.04, maturity=10, curve=curve)
f"a 4% 10y Treasury priced off the end-2024 curve: {p*100:.2f} per 100"
```

```{code-cell} ipython3
f"5y5y forward rate: {curve.forward(5, 10):.2%}  (the market's implied future 5y rate)"
```

## 3. Bootstrapping — and the round-trip proof

Par yields are what you observe; zeros are what you discount with. The bootstrap
recursion recovers one from the other — and the honest test is the exact
round-trip (zeros → par yields → bootstrap → identical zeros; see
`tests/test_curves.py::TestBootstrap`):

```{code-cell} ipython3
from quantropy.pricing import bootstrap_par_curve

pars = {n: 0.02 + 0.002 * n for n in range(1, 11)}          # upward-sloping par curve
boot = bootstrap_par_curve(pars)
pd.DataFrame({"par": pars.values(), "zero": boot.zero_rates.round(5)},
             index=range(1, 11)).tail(3)
```

Zeros sit *above* par yields on an upward slope — coupon drag, the first
interview question of every rates seat.

## 4. Validating against the Fed itself

The GSW file carries its own answer key: the NSS parameters that generated the
published yields. Our implementation must reproduce them:

```{code-cell} ipython3
from quantropy.pricing import nss_yield

ours = nss_yield(10, row["BETA0"], row["BETA1"], row["BETA2"],
                 row["BETA3"], row["TAU1"], row["TAU2"])
f"our NSS 10y: {ours:.4f}%  vs Fed's published: {row['SVENY10']:.4f}%"
```

Agreement to a basis point, across decades of dates (CI-tested). This is the
`[deep]` contract at its purest — the externally checkable number is the Fed's.

## 5. Rate risk: duration, DV01, key rates

```{code-cell} ipython3
from quantropy.pricing import dv01, key_rate_durations, modified_duration

d = modified_duration(0.04, 10, ytm=0.04)
kr = key_rate_durations(0.04, 10, curve)
print(f"modified duration ~ {d:.2f}y | parallel DV01 {dv01(0.04,10,curve)*10000:.2f} bp of face")
kr.round(6)
```

The key-rate profile shows *where* on the curve the risk lives (a 10y bond is
mostly 10y risk), and the profile sums back to the parallel DV01 — additivity
tested, not assumed.

## 6. Level, slope, curvature — the whole curve in three numbers

```{code-cell} ipython3
from quantropy.pricing import pca_level_slope_curvature

yields = gsw[[f"SVENY{t:02d}" for t in (1, 2, 3, 5, 7, 10, 20, 30)]].dropna()
loadings, explained = pca_level_slope_curvature(yields)
f"variance explained by 3 PCs over 35 years: {explained.sum():.1%}  (level alone: {explained[0]:.1%})"
```

Litterman-Scheinkman (1991), reproduced on data through 2025: three factors —
parallel level, slope, curvature — carry ~everything. This is why key-rate
hedging works and why "the 10y went up" is usually a sufficient sentence.

## 7. Pitfalls

- **Compounding conventions kill silently.** cc-percent vs annual-decimal caused
  more real losses than any model error; our conversion lives in exactly one
  named place.
- **No silent extrapolation** — the curve refuses maturities beyond its pillars;
  the 40y point you "need" is a modeling decision, not an interpolation.
- **The GSW curve is fitted, not traded**: great for research and risk, but the
  cheapest-to-deliver and repo specialness of *actual* bonds live elsewhere
  (BOUNDARIES: swap-desk depth).

## 8. Exercises

1. Price the same 4% 10y off the 2020-06-30 curve (near-zero era) and compare —
   how much of the change is level vs slope, using §6's loadings?
2. Build the 2s10s slope series from the fixture and find the inversions; what
   followed each?
3. Prove the bootstrap round-trip yourself for a 5-pillar curve of your choosing.

## Further reading

`docs/REFERENCES.md` §12 — Gürkaynak-Sack-Wright (2007), Nelson-Siegel (1987),
Svensson (1994), Litterman-Scheinkman (1991), Tuckman & Serrat.
