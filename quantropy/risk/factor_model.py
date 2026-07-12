"""The factor risk model: exposures → factor covariance → specific risk.

The third meaning of "factor" (Curriculum III.4/IX.2): risk factors DRIVE
covariance. A returns-based linear model — asset returns on factor returns —
yields betas B, factor covariance Ω, and idiosyncratic variances D, so any
portfolio's variance decomposes exactly:

    σ²(w) = wᵀ(B Ω Bᵀ)w  +  wᵀD w      (systematic + specific)

The decomposition's exactness (in-model) is tested, not asserted. Barra-style
fundamental models replace the time-series betas with characteristic exposures —
same algebra, licensed data (BOUNDARIES).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["FactorRiskModel"]


class FactorRiskModel:
    """Returns-based factor risk model, estimated by per-asset time-series OLS."""

    def __init__(self, asset_returns: pd.DataFrame, factor_returns: pd.DataFrame):
        common = asset_returns.index.intersection(factor_returns.index)
        r = asset_returns.loc[common].dropna(axis=1, how="any")
        f = factor_returns.loc[common]
        if len(common) < 3 * (f.shape[1] + 2):
            raise ValueError("not enough observations to estimate the model")
        x = np.column_stack([np.ones(len(f)), f.to_numpy()])
        coef, *_ = np.linalg.lstsq(x, r.to_numpy(), rcond=None)
        resid = r.to_numpy() - x @ coef

        self.assets = r.columns
        self.factors = f.columns
        self.betas = pd.DataFrame(coef[1:].T, index=r.columns, columns=f.columns)
        self.factor_cov = pd.DataFrame(
            np.cov(f.to_numpy().T, ddof=1), index=f.columns, columns=f.columns
        )
        self.specific_var = pd.Series(resid.var(axis=0, ddof=x.shape[1]), index=r.columns)
        self.r_squared = pd.Series(
            1.0 - resid.var(axis=0) / r.to_numpy().var(axis=0), index=r.columns
        )

    def portfolio_variance(self, weights: pd.Series) -> dict:
        """Exact in-model decomposition of portfolio variance (annualize outside)."""
        w = weights.reindex(self.assets).fillna(0.0).to_numpy()
        b = self.betas.to_numpy()
        omega = self.factor_cov.to_numpy()
        systematic = float(w @ b @ omega @ b.T @ w)
        specific = float((w**2 * self.specific_var.to_numpy()).sum())
        exposure = pd.Series(b.T @ w, index=self.factors)
        # per-factor contribution: x_k * (Ω x)_k over the factor exposures x
        contrib = exposure * (self.factor_cov @ exposure)
        return {
            "total": systematic + specific,
            "systematic": systematic,
            "specific": specific,
            "factor_exposures": exposure,
            "factor_contributions": contrib,
        }
