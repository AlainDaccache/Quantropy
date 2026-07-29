"""Performance attribution: Brinson and factor-based (Curriculum IX.5).

Brinson-Fachler: split active return vs a benchmark into allocation (overweighting
the right sectors) and selection (picking the right names within sectors), with
the interaction term reported explicitly — folding it into selection is a
convention, not a law, so it stays visible. Factor attribution regresses the
track record on factor returns: contributions = β·factor mean + α, summing (in
sample) to the mean return exactly — tested, not asserted.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["brinson", "factor_attribution"]


def brinson(
    portfolio_weights: pd.Series,
    benchmark_weights: pd.Series,
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> pd.DataFrame:
    """Single-period Brinson-Fachler by segment.

    Inputs indexed by segment (sector/asset class). Per segment:
      allocation  = (wp - wb) · (rb - Rb)
      selection   = wb · (rp - rb)
      interaction = (wp - wb) · (rp - rb)
    Total active = Σ(all three) = wpᵀrp - wbᵀrb (identity, tested).
    """
    idx = benchmark_weights.index
    wp = portfolio_weights.reindex(idx).fillna(0.0)
    wb = benchmark_weights
    rp = portfolio_returns.reindex(idx).fillna(0.0)
    rb = benchmark_returns.reindex(idx).fillna(0.0)
    if not np.isclose(wb.sum(), 1.0) or not np.isclose(wp.sum(), 1.0):
        raise ValueError("weights must each sum to 1")
    total_b = float(wb @ rb)
    out = pd.DataFrame(
        {
            "allocation": (wp - wb) * (rb - total_b),
            "selection": wb * (rp - rb),
            "interaction": (wp - wb) * (rp - rb),
        },
        index=idx,
    )
    out.attrs["active_return"] = float(wp @ rp - wb @ rb)
    return out


def factor_attribution(
    portfolio_returns: pd.Series, factor_returns: pd.DataFrame
) -> pd.Series:
    """Regress the track record on factors: mean return = α + Σ βk·mean(fk).

    Returns the per-factor contributions plus 'alpha' and 'total' (which equals
    the sample mean return exactly — the in-sample identity that makes the
    decomposition trustworthy).
    """
    common = portfolio_returns.dropna().index.intersection(factor_returns.dropna().index)
    if len(common) < factor_returns.shape[1] + 10:
        raise ValueError("not enough overlapping observations")
    y = portfolio_returns.loc[common].to_numpy()
    f = factor_returns.loc[common]
    x = np.column_stack([np.ones(len(f)), f.to_numpy()])
    coef, *_ = np.linalg.lstsq(x, y, rcond=None)
    alpha, betas = coef[0], coef[1:]
    contrib = pd.Series(betas * f.mean().to_numpy(), index=f.columns)
    contrib["alpha"] = alpha
    contrib["total"] = contrib.sum()
    return contrib
