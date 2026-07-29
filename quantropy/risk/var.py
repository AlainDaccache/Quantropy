"""VaR and Expected Shortfall — measured AND backtested (Curriculum IX.1).

A VaR number without its backtest is decoration: Kupiec's proportion-of-failures
test asks whether the breach *frequency* matches the confidence level;
Christoffersen's independence test asks whether breaches *cluster* (a model can
pass Kupiec while failing every crisis at once). References: Jorion; REFERENCES §4.

Sign convention: VaR and ES are reported as POSITIVE loss magnitudes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

__all__ = ["value_at_risk", "expected_shortfall", "kupiec_test", "christoffersen_test"]


def value_at_risk(returns: pd.Series, level: float = 0.99, method: str = "historical") -> float:
    """VaR at ``level`` (e.g. 0.99): the loss exceeded with prob 1-level.

    ``historical`` — empirical quantile (no distributional assumption);
    ``parametric`` — normal approximation μ + σ·z (fails exactly when tails
    matter; taught as the contrast, not the default).
    """
    r = returns.dropna()
    if len(r) < 50:
        raise ValueError("need >= 50 observations for a meaningful VaR")
    if method == "historical":
        return float(-np.quantile(r, 1.0 - level))
    if method == "parametric":
        return float(-(r.mean() + r.std(ddof=1) * stats.norm.ppf(1.0 - level)))
    raise ValueError("method must be 'historical' or 'parametric'")


def expected_shortfall(returns: pd.Series, level: float = 0.99) -> float:
    """ES/CVaR: the mean loss GIVEN a VaR breach — coherent where VaR is not."""
    r = returns.dropna()
    var = value_at_risk(r, level, "historical")
    tail = r[r <= -var]
    if tail.empty:
        return var
    return float(-tail.mean())


def kupiec_test(returns: pd.Series, var_forecasts: pd.Series, level: float = 0.99) -> dict:
    """Kupiec (1995) proportion-of-failures likelihood-ratio test.

    H0: the breach probability equals 1-level. Returns breaches, expected count,
    LR statistic and p-value (χ², 1 dof). Low p ⇒ the VaR model is miscalibrated.
    """
    common = returns.dropna().index.intersection(var_forecasts.dropna().index)
    r, v = returns.loc[common], var_forecasts.loc[common]
    breaches = (r < -v).to_numpy()
    n, x = len(breaches), int(breaches.sum())
    p = 1.0 - level
    if n == 0:
        raise ValueError("no overlapping observations")
    p_hat = x / n
    if x in (0, n):  # degenerate likelihood; handle explicitly
        lr = -2.0 * (n * np.log(1 - p) if x == 0 else n * np.log(p))
    else:
        lr = -2.0 * (
            (n - x) * np.log((1 - p) / (1 - p_hat)) + x * np.log(p / p_hat)
        )
    return {
        "breaches": x,
        "expected": n * p,
        "lr_stat": float(lr),
        "p_value": float(stats.chi2.sf(lr, df=1)),
    }


def christoffersen_test(returns: pd.Series, var_forecasts: pd.Series, level: float = 0.99) -> dict:
    """Christoffersen (1998) independence test: do breaches cluster?

    H0: breach today is independent of breach yesterday (first-order Markov).
    A model whose breaches all arrive in one crisis fails here while passing
    Kupiec — which is why both are run.
    """
    common = returns.dropna().index.intersection(var_forecasts.dropna().index)
    b = (returns.loc[common] < -var_forecasts.loc[common]).to_numpy().astype(int)
    if len(b) < 3:
        raise ValueError("series too short")
    pairs = np.stack([b[:-1], b[1:]], axis=1)
    n00 = int(((pairs[:, 0] == 0) & (pairs[:, 1] == 0)).sum())
    n01 = int(((pairs[:, 0] == 0) & (pairs[:, 1] == 1)).sum())
    n10 = int(((pairs[:, 0] == 1) & (pairs[:, 1] == 0)).sum())
    n11 = int(((pairs[:, 0] == 1) & (pairs[:, 1] == 1)).sum())

    def _safe_log(x: float) -> float:
        return np.log(x) if x > 0 else 0.0

    pi = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)
    pi0 = n01 / max(n00 + n01, 1)
    pi1 = n11 / max(n10 + n11, 1)
    log_l0 = (n00 + n10) * _safe_log(1 - pi) + (n01 + n11) * _safe_log(pi)
    log_l1 = (
        n00 * _safe_log(1 - pi0) + n01 * _safe_log(pi0)
        + n10 * _safe_log(1 - pi1) + n11 * _safe_log(pi1)
    )
    lr = -2.0 * (log_l0 - log_l1)
    return {"lr_stat": float(lr), "p_value": float(stats.chi2.sf(lr, df=1)),
            "transition_11": n11}
