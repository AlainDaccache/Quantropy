"""KC-26: centered, ML-denominator Ledoit-Wolf scaled-identity shrinkage."""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class CovarianceEstimate:
    covariance: np.ndarray
    shrinkage: float
    observations: int
    target_variance: float


def _observations(values):
    x = np.asarray(values, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 1:
        raise ValueError("Require at least two observations and one column")
    if not np.isfinite(x).all():
        raise ValueError("Missing or nonfinite observations are unsupported")
    return x


def sample_covariance(values):
    """Unbiased sample convention: demean columns, divide by n-1."""
    x = _observations(values)
    scale = float(np.max(np.abs(x)))
    if scale == 0:
        return np.zeros((x.shape[1], x.shape[1]))
    centered = x / scale
    centered -= centered.mean(axis=0)
    normalized = centered.T @ centered / (len(x) - 1)
    with np.errstate(over="ignore", invalid="ignore", under="ignore"):
        covariance = (normalized * scale) * scale
    if not np.isfinite(covariance).all():
        raise ValueError("Covariance is outside floating-point range")
    if np.trace(normalized) > 0 and not np.any(covariance):
        raise ValueError("Covariance underflows floating-point range")
    return covariance


def ledoit_wolf_identity(values):
    """Estimate covariance with target trace(S)/p I; S uses denominator n.

    This is not the constant-correlation or nonlinear Ledoit-Wolf variant.
    Intensity is calculated in normalized units to avoid fourth-power overflow.
    Zero scatter returns zero covariance and intensity zero, not an inverse.
    """
    x = _observations(values)
    n, p = x.shape
    scale = float(np.max(np.abs(x)))
    if scale == 0:
        return CovarianceEstimate(np.zeros((p, p)), 0.0, n, 0.0)
    centered = x / scale
    centered -= centered.mean(axis=0)
    s = centered.T @ centered / n
    mu = float(np.trace(s) / p)
    distance = float(np.sum((s - mu * np.eye(p)) ** 2) / p)
    # Direct outer-product deviations avoid cancellation in the fourth moment.
    noise = sum(float(np.sum((np.outer(row, row) - s) ** 2))
                for row in centered) / (p * n * n)
    intensity = 0.0 if distance == 0 else min(noise / distance, 1.0)
    normalized = (1 - intensity) * s + intensity * mu * np.eye(p)
    with np.errstate(over="ignore", invalid="ignore", under="ignore"):
        covariance = (normalized * scale) * scale
        target = (mu * scale) * scale
    if not np.isfinite(covariance).all() or not np.isfinite(target):
        raise ValueError("Covariance is outside floating-point range")
    if mu > 0 and target == 0:
        raise ValueError("Covariance underflows floating-point range")
    return CovarianceEstimate(covariance, intensity, n, float(target))
