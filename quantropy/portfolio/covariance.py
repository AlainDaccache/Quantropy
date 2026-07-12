"""Covariance estimation: sample, EWMA, Ledoit-Wolf shrinkage.

The load-bearing input to everything in Part VII (Curriculum VII.2; REFERENCES §4):
naive sample covariance is noisy exactly where optimizers listen hardest. The
Ledoit-Wolf estimator shrinks toward a structured target with an analytically
optimal intensity — implemented here from the papers, validated by Monte Carlo
against a known ground-truth covariance (shrinkage must reduce estimation error
in the N ~ T regime, and stay invertible when N > T).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["sample_covariance", "ewma_covariance", "ledoit_wolf"]


def sample_covariance(returns: pd.DataFrame) -> pd.DataFrame:
    """Plain sample covariance (ddof=1) — the honest baseline, noise included."""
    return returns.dropna(how="any").cov()


def ewma_covariance(returns: pd.DataFrame, halflife: float = 60.0) -> pd.DataFrame:
    """Exponentially-weighted covariance (RiskMetrics-style), causal by nature."""
    r = returns.dropna(how="any")
    lam = 0.5 ** (1.0 / halflife)
    x = r.to_numpy() - r.to_numpy().mean(axis=0)
    w = lam ** np.arange(len(x) - 1, -1, -1)
    w /= w.sum()
    cov = (x * w[:, None]).T @ x
    return pd.DataFrame(cov, index=r.columns, columns=r.columns)


def ledoit_wolf(returns: pd.DataFrame, target: str = "constant_correlation") -> pd.DataFrame:
    """Ledoit-Wolf linear shrinkage with analytically optimal intensity.

    ``target='identity'`` — the 2004a well-conditioned estimator (shrinks toward
    the scaled identity μI). ``target='constant_correlation'`` — the "Honey, I
    Shrunk the Sample Covariance Matrix" target: sample variances kept, all
    correlations shrunk toward their mean. Intensity is clipped to [0, 1] and the
    result is symmetric, PSD, and invertible even when N > T.
    """
    r = returns.dropna(how="any")
    x = r.to_numpy() - r.to_numpy().mean(axis=0)
    t, n = x.shape
    if t < 3:
        raise ValueError("need at least 3 observations")
    s = x.T @ x / t  # MLE sample covariance

    if target == "identity":
        mu = np.trace(s) / n
        f = mu * np.eye(n)
    elif target == "constant_correlation":
        std = np.sqrt(np.diag(s))
        corr = s / np.outer(std, std)
        rbar = (corr.sum() - n) / (n * (n - 1))
        f = rbar * np.outer(std, std)
        np.fill_diagonal(f, np.diag(s))
    else:
        raise ValueError("target must be 'identity' or 'constant_correlation'")

    # pi-hat: sum of asymptotic variances of sample-covariance entries
    y = x[:, :, None] * x[:, None, :]  # t × n × n outer products
    pi_mat = ((y - s) ** 2).mean(axis=0)
    pi_hat = pi_mat.sum()
    # gamma-hat: misspecification of the target
    gamma_hat = ((f - s) ** 2).sum()
    # rho-hat: covariance between estimation errors of s and f. For the identity
    # target the off-diagonal terms vanish; the diagonal contribution is common.
    rho_hat = np.trace(pi_mat) if target == "identity" else np.diag(pi_mat).sum()

    kappa = (pi_hat - rho_hat) / gamma_hat if gamma_hat > 0 else 0.0
    intensity = float(np.clip(kappa / t, 0.0, 1.0))

    shrunk = intensity * f + (1.0 - intensity) * s
    shrunk = (shrunk + shrunk.T) / 2.0  # enforce exact symmetry
    out = pd.DataFrame(shrunk, index=r.columns, columns=r.columns)
    out.attrs["shrinkage_intensity"] = intensity
    return out
