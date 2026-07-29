"""Return algebra and conventions.

Simple vs log returns, compounding, and annualization. Conventions follow standard
practice (e.g. 252 trading days); see docs/REFERENCES.md §5 (Tsay) and §8 (CFA
Quantitative Methods).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "PERIODS_PER_YEAR",
    "to_log",
    "to_simple",
    "cumulative_return",
    "annualize_return",
    "annualize_volatility",
    "cagr",
]

#: Conventional period counts per year, by sampling frequency.
PERIODS_PER_YEAR = {"daily": 252, "weekly": 52, "monthly": 12, "quarterly": 4, "annual": 1}


def to_log(simple: pd.Series | np.ndarray | float):
    """Log return from simple return: ``ln(1 + r)``."""
    return np.log1p(simple)


def to_simple(log_ret: pd.Series | np.ndarray | float):
    """Simple return from log return: ``exp(r) - 1``."""
    return np.expm1(log_ret)


def cumulative_return(simple: pd.Series | np.ndarray) -> float:
    """Total compounded return of a series of simple returns: ``prod(1+r) - 1``."""
    return float(np.prod(1.0 + np.asarray(simple)) - 1.0)


def annualize_return(mean_periodic: float, periods_per_year: int, geometric: bool = True) -> float:
    """Annualize a mean periodic simple return.

    Geometric (default): ``(1 + r)^p - 1``. Arithmetic: ``r * p``.
    """
    if geometric:
        return (1.0 + mean_periodic) ** periods_per_year - 1.0
    return mean_periodic * periods_per_year


def annualize_volatility(periodic_vol: float, periods_per_year: int) -> float:
    """Annualize periodic volatility by the square-root-of-time rule: ``σ * sqrt(p)``.

    Assumes i.i.d. returns — an assumption, not a law; autocorrelation breaks it
    (taught explicitly in the curriculum's pitfalls sections).
    """
    return periodic_vol * float(np.sqrt(periods_per_year))


def cagr(total_growth: float, years: float) -> float:
    """Compound annual growth rate from total growth factor: ``G^(1/y) - 1``.

    ``total_growth`` is the end/start value ratio (e.g. 2.0 for a doubling).
    """
    if total_growth <= 0:
        raise ValueError("total_growth must be positive")
    if years <= 0:
        raise ValueError("years must be positive")
    return total_growth ** (1.0 / years) - 1.0
