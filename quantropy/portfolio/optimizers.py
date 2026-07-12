"""Portfolio optimizers: min-variance, tangency, ERC risk parity, HRP.

Curriculum VII.3–.4 (REFERENCES §4). Presented with the health warning built in:
`min_variance` and `tangency` are the error-maximizing classics — feed them
`ledoit_wolf`, never raw sample covariance; `risk_parity` and `hrp` are the robust
alternatives that need no expected returns at all. All weights are long-only-free
(unconstrained) unless stated; constraint handling is a stated M5 extension.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

__all__ = ["min_variance", "tangency", "risk_parity", "hrp", "risk_contributions"]


def _to_matrix(cov: pd.DataFrame) -> tuple[np.ndarray, pd.Index]:
    return cov.to_numpy(), cov.index


def min_variance(cov: pd.DataFrame) -> pd.Series:
    """Global minimum-variance weights: w ∝ Σ⁻¹1 (closed form, sums to 1)."""
    sigma, names = _to_matrix(cov)
    ones = np.ones(len(names))
    w = np.linalg.solve(sigma, ones)
    return pd.Series(w / w.sum(), index=names)


def tangency(cov: pd.DataFrame, expected_returns: pd.Series) -> pd.Series:
    """Maximum-Sharpe (tangency) weights: w ∝ Σ⁻¹μ — the error maximizer itself.

    Included because the curriculum demonstrates *why* it fails with estimated μ,
    not because you should feed it estimates casually (Curriculum VII.3).
    """
    sigma, names = _to_matrix(cov)
    mu = expected_returns.reindex(names).to_numpy()
    w = np.linalg.solve(sigma, mu)
    if w.sum() == 0:
        raise ValueError("degenerate tangency portfolio (weights sum to zero)")
    return pd.Series(w / w.sum(), index=names)


def risk_contributions(weights: pd.Series, cov: pd.DataFrame) -> pd.Series:
    """Each asset's share of portfolio variance: w_i (Σw)_i / (wᵀΣw)."""
    sigma, names = _to_matrix(cov)
    w = weights.reindex(names).to_numpy()
    total = float(w @ sigma @ w)
    if total <= 0:
        raise ValueError("non-positive portfolio variance")
    rc = w * (sigma @ w) / total
    return pd.Series(rc, index=names)


def risk_parity(cov: pd.DataFrame, tol: float = 1e-10, max_iter: int = 10_000) -> pd.Series:
    """Equal-risk-contribution weights (long-only), by cyclical coordinate descent.

    Converges for any positive-definite Σ; each asset ends contributing exactly
    1/N of portfolio variance (tested to tolerance, not asserted).
    """
    sigma, names = _to_matrix(cov)
    n = len(names)
    w = np.full(n, 1.0 / n)
    target = 1.0 / n
    for _ in range(max_iter):
        w_prev = w.copy()
        for i in range(n):
            others = w @ sigma[i] - w[i] * sigma[i, i]
            # solve w_i * (sigma_ii * w_i + others) = target * wᵀΣw for w_i > 0
            port_var = w @ sigma @ w
            a, b, c = sigma[i, i], others, -target * port_var
            w[i] = (-b + np.sqrt(b * b - 4 * a * c)) / (2 * a)
        w /= w.sum()
        if np.abs(w - w_prev).max() < tol:
            break
    return pd.Series(w, index=names)


def hrp(cov: pd.DataFrame) -> pd.Series:
    """Hierarchical Risk Parity (López de Prado 2016, REFERENCES §4).

    Correlation distance → single-linkage clustering → quasi-diagonalization →
    recursive bisection with inverse-variance splits. No matrix inversion at any
    step — robust where MVO is fragile.
    """
    sigma, names = _to_matrix(cov)
    std = np.sqrt(np.diag(sigma))
    corr = sigma / np.outer(std, std)
    dist = np.sqrt(np.clip((1.0 - corr) / 2.0, 0.0, 1.0))
    order = leaves_list(linkage(squareform(dist, checks=False), method="single"))

    weights = np.ones(len(names))

    def bisect(items: np.ndarray) -> None:
        if len(items) <= 1:
            return
        left, right = np.array_split(items, 2)

        def cluster_var(idx: np.ndarray) -> float:
            sub = sigma[np.ix_(idx, idx)]
            ivp = 1.0 / np.diag(sub)
            ivp /= ivp.sum()
            return float(ivp @ sub @ ivp)

        v_left, v_right = cluster_var(left), cluster_var(right)
        alpha = 1.0 - v_left / (v_left + v_right)
        weights[left] *= alpha
        weights[right] *= 1.0 - alpha
        bisect(left)
        bisect(right)

    bisect(np.asarray(order))
    return pd.Series(weights / weights.sum(), index=names[order]).reindex(names)
