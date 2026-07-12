"""The sovereign curve: discounting, bootstrapping, NSS, duration, PCA.

Curriculum IV.6–.7 (REFERENCES §12). Conventions are explicit everywhere:
- `DiscountCurve` holds **annually-compounded zero rates in decimals**; the GSW
  file publishes **continuously-compounded percents** — `DiscountCurve.from_gsw_row`
  performs that conversion in one visible place.
- Bond cash flows are annual-coupon, unit face (teaching grade; day-count and
  semi-annual conventions are Part I.3 refinements, stated not hidden).

Validation strategy: hand-computed bond math, exact bootstrap round-trips, and the
Fed's own internal consistency (NSS parameters reproducing published SVENY yields).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = [
    "nss_yield",
    "DiscountCurve",
    "bootstrap_par_curve",
    "bond_price",
    "macaulay_duration",
    "modified_duration",
    "dv01",
    "key_rate_durations",
    "pca_level_slope_curvature",
]


def nss_yield(t, beta0, beta1, beta2, beta3=0.0, tau1=1.0, tau2=1.0):
    """Nelson-Siegel-Svensson zero yield at maturity ``t`` (years).

    Same units in, same units out (the Fed publishes percent). β0 is the long-end
    level; the β1/β2 terms shape the short end (slope, hump); β3/τ2 add the second
    hump. As t→∞ the yield → β0; as t→0 it → β0+β1.
    """
    t = np.asarray(t, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        x1 = t / tau1
        lam1 = np.where(t > 0, (1 - np.exp(-x1)) / x1, 1.0)
        term2 = lam1 - np.exp(-x1)
        x2 = t / tau2
        lam2 = np.where(t > 0, (1 - np.exp(-x2)) / x2, 1.0)
        term3 = lam2 - np.exp(-x2)
    out = beta0 + beta1 * lam1 + beta2 * term2 + beta3 * term3
    return float(out) if out.ndim == 0 else out


@dataclass(frozen=True)
class DiscountCurve:
    """Zero curve: maturities (years) → annually-compounded zero rates (decimal).

    Linear interpolation on zero rates between pillars; flat extrapolation is
    refused (silent extrapolation is how curve bugs hide).
    """

    maturities: np.ndarray
    zero_rates: np.ndarray

    def __post_init__(self):
        m = np.asarray(self.maturities, dtype=float)
        z = np.asarray(self.zero_rates, dtype=float)
        if len(m) != len(z) or len(m) < 2:
            raise ValueError("need >= 2 (maturity, rate) pillars of equal length")
        if not np.all(np.diff(m) > 0):
            raise ValueError("maturities must be strictly increasing")
        object.__setattr__(self, "maturities", m)
        object.__setattr__(self, "zero_rates", z)

    @classmethod
    def from_gsw_row(cls, row: pd.Series, max_maturity: int = 30) -> "DiscountCurve":
        """Build from one GSW row's SVENY01..NN columns.

        GSW zeros are continuously compounded percents; converted here to
        annually-compounded decimals: z_annual = exp(z_cc) - 1.
        """
        mats, rates = [], []
        for t in range(1, max_maturity + 1):
            col = f"SVENY{t:02d}"
            if col in row.index and pd.notna(row[col]):
                mats.append(float(t))
                rates.append(float(np.exp(row[col] / 100.0) - 1.0))
        return cls(np.array(mats), np.array(rates))

    def zero(self, t: float) -> float:
        if t < self.maturities[0] - 1e-9 or t > self.maturities[-1] + 1e-9:
            raise ValueError(
                f"maturity {t} outside pillar range "
                f"[{self.maturities[0]}, {self.maturities[-1]}] — no silent extrapolation"
            )
        return float(np.interp(t, self.maturities, self.zero_rates))

    def discount(self, t: float) -> float:
        return 1.0 / (1.0 + self.zero(t)) ** t

    def forward(self, t1: float, t2: float) -> float:
        """Annually-compounded forward rate between t1 and t2 (t2 > t1)."""
        if t2 <= t1:
            raise ValueError("t2 must exceed t1")
        d1, d2 = self.discount(t1), self.discount(t2)
        return (d1 / d2) ** (1.0 / (t2 - t1)) - 1.0


def bootstrap_par_curve(par_yields: dict[int, float]) -> DiscountCurve:
    """Bootstrap zero rates from annual-coupon par yields {maturity: decimal}.

    A par bond prices at 1.0 by definition: 1 = c·Σ df(i) + df(n). Solve df
    year by year — the classic recursion. Requires consecutive integer maturities
    starting at 1 (interpolating missing pillars is a stated extension, not a
    silent default).
    """
    mats = sorted(par_yields)
    if mats != list(range(1, len(mats) + 1)):
        raise ValueError("need consecutive integer maturities starting at 1")
    dfs: list[float] = []
    for n in mats:
        c = par_yields[n]
        df_n = (1.0 - c * sum(dfs)) / (1.0 + c)
        if df_n <= 0:
            raise ValueError(f"non-positive discount factor at {n}y — inputs inconsistent")
        dfs.append(df_n)
    zeros = np.array([df ** (-1.0 / n) - 1.0 for n, df in zip(mats, dfs)])
    return DiscountCurve(np.array(mats, dtype=float), zeros)


def _cashflows(coupon: float, maturity: int) -> list[tuple[float, float]]:
    return [(float(t), coupon) for t in range(1, maturity)] + [(float(maturity), 1.0 + coupon)]


def bond_price(coupon: float, maturity: int, curve: DiscountCurve) -> float:
    """Price of a unit-face annual-coupon bond off the zero curve."""
    return float(sum(cf * curve.discount(t) for t, cf in _cashflows(coupon, maturity)))


def macaulay_duration(coupon: float, maturity: int, ytm: float) -> float:
    """PV-weighted average time to cash flows, flat yield ``ytm`` (annual comp)."""
    pv_total, weighted = 0.0, 0.0
    for t, cf in _cashflows(coupon, maturity):
        pv = cf / (1.0 + ytm) ** t
        pv_total += pv
        weighted += t * pv
    return weighted / pv_total


def modified_duration(coupon: float, maturity: int, ytm: float) -> float:
    """Price sensitivity: -(1/P)·dP/dy = Macaulay / (1 + y)."""
    return macaulay_duration(coupon, maturity, ytm) / (1.0 + ytm)


def dv01(coupon: float, maturity: int, curve: DiscountCurve, bump_bp: float = 1.0) -> float:
    """Dollar value of a basis point, by symmetric parallel bump of the zero curve
    (per unit face). Positive for a long bond position."""
    up = DiscountCurve(curve.maturities, curve.zero_rates + bump_bp / 1e4)
    down = DiscountCurve(curve.maturities, curve.zero_rates - bump_bp / 1e4)
    return (bond_price(coupon, maturity, down) - bond_price(coupon, maturity, up)) / 2.0


def key_rate_durations(
    coupon: float,
    maturity: int,
    curve: DiscountCurve,
    key_rates: tuple[float, ...] = (2.0, 5.0, 10.0, 30.0),
    bump_bp: float = 1.0,
) -> pd.Series:
    """Per-pillar rate sensitivities: bump ONE key maturity (triangular weights to
    its neighbors), reprice. Sums approximately to the parallel DV01 — tested."""
    price0 = bond_price(coupon, maturity, curve)
    krds = {}
    keys = sorted(key_rates)
    for i, k in enumerate(keys):
        left = keys[i - 1] if i > 0 else None
        right = keys[i + 1] if i < len(keys) - 1 else None

        def weight(m: float, k=k, left=left, right=right) -> float:
            # triangular bump: 1 at the key, ramping to 0 at neighboring keys,
            # flat beyond the first/last key (so the weights sum to 1 everywhere)
            if m == k:
                return 1.0
            if m < k:
                if left is None:
                    return 1.0
                return max(0.0, (m - left) / (k - left))
            if right is None:
                return 1.0
            return max(0.0, (right - m) / (right - k))

        w = np.array([weight(m) for m in curve.maturities])
        bumped = DiscountCurve(curve.maturities, curve.zero_rates + w * bump_bp / 1e4)
        krds[f"{k:g}y"] = price0 - bond_price(coupon, maturity, bumped)
    return pd.Series(krds)


def pca_level_slope_curvature(yields: pd.DataFrame, n_components: int = 3):
    """PCA on yield CHANGES (Litterman-Scheinkman 1991): returns (loadings frame,
    explained-variance ratios). Expect level/slope/curvature explaining ~95%+."""
    changes = yields.diff().dropna()
    if len(changes) < 10:
        raise ValueError("need more observations than that")
    x = changes - changes.mean()
    cov = np.cov(x.to_numpy().T)
    eigval, eigvec = np.linalg.eigh(cov)
    order = np.argsort(eigval)[::-1]
    eigval, eigvec = eigval[order], eigvec[:, order]
    explained = eigval[:n_components] / eigval.sum()
    loadings = pd.DataFrame(
        eigvec[:, :n_components],
        index=yields.columns,
        columns=[f"PC{i + 1}" for i in range(n_components)],
    )
    # sign convention: PC1 positive (level up), PC2 increasing with maturity (slope)
    if loadings["PC1"].mean() < 0:
        loadings["PC1"] *= -1
    if loadings["PC2"].iloc[-1] < loadings["PC2"].iloc[0]:
        loadings["PC2"] *= -1
    return loadings, explained
