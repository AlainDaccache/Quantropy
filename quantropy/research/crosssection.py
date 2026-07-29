"""The cross-sectional researcher's toolkit: sorts, Fama-MacBeth, GRS.

The complete empirical process for establishing (or demolishing) a factor
(Curriculum III.5; REFERENCES §11): portfolio sorts with the field's conventions,
Fama-MacBeth two-pass regressions with Newey-West and Shanken corrections, and the
GRS joint-alpha test. Validated two ways: synthetic ground truth (the estimator
recovers a known premium) and real Ken French data (reproducing published numbers).

Causality note: `portfolio_sorts` lags the characteristic internally by one period
— you sort on what was knowable *before* the return you earn. Passing an unlagged
characteristic is the classic self-fulfilling backtest, and the API makes it
impossible rather than discouraged.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

__all__ = ["portfolio_sorts", "fama_macbeth", "two_pass_fama_macbeth", "grs_test"]


# ---------------------------------------------------------------------------
# Portfolio sorts
# ---------------------------------------------------------------------------


def portfolio_sorts(
    returns: pd.DataFrame,
    characteristic: pd.DataFrame,
    n_quantiles: int = 5,
    weights: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Univariate quantile sorts: rank on the (internally lagged) characteristic,
    earn next period's return per bucket, plus the high-minus-low ``spread``.

    ``returns``/``characteristic`` — T×N frames, same columns. ``weights`` —
    optional T×N (e.g. market cap) for value-weighted buckets; equal-weight if
    omitted. Assets missing a characteristic that period are excluded, not zeroed.
    """
    if not returns.columns.equals(characteristic.columns):
        raise ValueError("returns and characteristic must share the same columns")
    if n_quantiles < 2:
        raise ValueError("n_quantiles >= 2 required")
    char = characteristic.shift(1)  # sort on what was knowable BEFORE the return
    w = weights.shift(1) if weights is not None else None

    labels = [f"Q{i + 1}" for i in range(n_quantiles)]
    rows = []
    for t in returns.index:
        c = char.loc[t].dropna()
        r = returns.loc[t]
        if len(c) < n_quantiles:  # can't form buckets this period
            rows.append([np.nan] * (n_quantiles + 1))
            continue
        buckets = pd.qcut(c.rank(method="first"), n_quantiles, labels=labels)
        means = []
        for q in labels:
            names = c.index[buckets == q]
            rets = r[names].dropna()
            if rets.empty:
                means.append(np.nan)
            elif w is None:
                means.append(float(rets.mean()))
            else:
                wt = w.loc[t, rets.index].fillna(0.0)
                means.append(float((rets * wt).sum() / wt.sum()) if wt.sum() > 0 else np.nan)
        means.append(means[-1] - means[0])  # spread = top - bottom
        rows.append(means)
    return pd.DataFrame(rows, index=returns.index, columns=labels + ["spread"])


# ---------------------------------------------------------------------------
# Fama-MacBeth
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FMResult:
    """Fama-MacBeth output: mean premia, Newey-West t-stats, per-period lambdas."""

    premia: pd.Series
    t_stats: pd.Series
    lambdas: pd.DataFrame  # T × (const + regressors)
    shanken_t_stats: pd.Series | None = None


def _newey_west_t(series: pd.Series, lags: int) -> float:
    """t-stat of the mean with Newey-West (HAC) standard errors."""
    x = series.dropna().to_numpy()
    n = len(x)
    if n < 2:
        return float("nan")
    e = x - x.mean()
    gamma0 = float(e @ e) / n
    s = gamma0
    for lag in range(1, min(lags, n - 1) + 1):
        cov = float(e[lag:] @ e[:-lag]) / n
        s += 2.0 * (1.0 - lag / (lags + 1)) * cov
    se = np.sqrt(s / n)
    return float(x.mean() / se) if se > 0 else float("nan")


def fama_macbeth(
    returns: pd.DataFrame,
    regressors: dict[str, pd.DataFrame],
    nw_lags: int = 6,
) -> FMResult:
    """Period-by-period cross-sectional regressions; premia = time-mean of slopes.

    ``regressors`` — {name: T×N frame}, already causal (lag before passing —
    unlike sorts, FM regressors are often betas estimated out-of-window, so the
    lag policy belongs to the caller and is their stated responsibility).
    """
    names = list(regressors)
    cols = ["const"] + names
    lambdas = []
    for t in returns.index:
        y = returns.loc[t]
        X = pd.DataFrame({name: regressors[name].loc[t] for name in names})
        data = pd.concat([y.rename("y"), X], axis=1).dropna()
        if len(data) < len(cols) + 2:  # not enough names for a cross-section
            lambdas.append([np.nan] * len(cols))
            continue
        A = np.column_stack([np.ones(len(data))] + [data[n].to_numpy() for n in names])
        coef, *_ = np.linalg.lstsq(A, data["y"].to_numpy(), rcond=None)
        lambdas.append(list(coef))
    lam = pd.DataFrame(lambdas, index=returns.index, columns=cols)
    premia = lam.mean()
    t_stats = pd.Series({c: _newey_west_t(lam[c], nw_lags) for c in cols})
    return FMResult(premia=premia, t_stats=t_stats, lambdas=lam)


def two_pass_fama_macbeth(
    asset_returns: pd.DataFrame,
    factor_returns: pd.DataFrame,
    nw_lags: int = 6,
) -> FMResult:
    """The classic two-pass: full-sample time-series betas, then FM on the betas —
    with the **Shanken (1992) errors-in-variables correction**.

    Pass-two regressors are *estimated* betas, so naive FM standard errors are
    overstated confidence; Shanken's multiplier ``(1 + λ' Σ_f⁻¹ λ)`` deflates the
    t-stats accordingly (REFERENCES §11).
    """
    common = asset_returns.index.intersection(factor_returns.index)
    R, F = asset_returns.loc[common], factor_returns.loc[common]

    # pass 1: betas per asset
    X = np.column_stack([np.ones(len(F)), F.to_numpy()])
    betas = {}
    for asset in R.columns:
        y = R[asset].to_numpy()
        mask = ~np.isnan(y)
        if mask.sum() < F.shape[1] + 10:
            continue
        coef, *_ = np.linalg.lstsq(X[mask], y[mask], rcond=None)
        betas[asset] = coef[1:]  # drop intercept
    beta = pd.DataFrame(betas, index=list(F.columns)).T  # N × K

    # pass 2: FM of returns on (constant) betas each period
    regressors = {f: pd.DataFrame(
        np.tile(beta[f].to_numpy(), (len(R), 1)), index=R.index, columns=beta.index
    ) for f in F.columns}
    fm = fama_macbeth(R[beta.index], regressors, nw_lags=nw_lags)

    # Shanken correction
    lam = fm.premia[list(F.columns)].to_numpy()
    sigma_f = np.cov(F.to_numpy().T, ddof=1)
    sigma_f = np.atleast_2d(sigma_f)
    c = float(lam @ np.linalg.inv(sigma_f) @ lam)
    shanken = fm.t_stats / np.sqrt(1.0 + c)
    shanken["const"] = fm.t_stats["const"]  # correction applies to factor premia
    return FMResult(
        premia=fm.premia, t_stats=fm.t_stats, lambdas=fm.lambdas, shanken_t_stats=shanken
    )


# ---------------------------------------------------------------------------
# GRS
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GRSResult:
    statistic: float
    p_value: float
    alphas: pd.Series
    alpha_t_stats: pd.Series


def grs_test(asset_excess_returns: pd.DataFrame, factor_returns: pd.DataFrame) -> GRSResult:
    """Gibbons-Ross-Shanken (1989): are all time-series alphas jointly zero?

    The exact finite-sample F-test of whether the factor portfolios span the
    mean-variance frontier of the test assets. GRS ~ F(N, T-N-K) under the null.
    Requires T > N + K. Inputs: T×N excess returns, T×K factor returns.
    """
    common = asset_excess_returns.index.intersection(factor_returns.index)
    R = asset_excess_returns.loc[common].dropna(axis=0, how="any")
    F = factor_returns.loc[R.index]
    T, N = R.shape
    K = F.shape[1]
    if T <= N + K:
        raise ValueError(f"GRS needs T > N + K (got T={T}, N={N}, K={K})")

    X = np.column_stack([np.ones(T), F.to_numpy()])
    coef, *_ = np.linalg.lstsq(X, R.to_numpy(), rcond=None)
    alphas = coef[0]
    resid = R.to_numpy() - X @ coef

    sigma = resid.T @ resid / T  # MLE residual covariance
    f_bar = F.mean().to_numpy()
    omega = np.cov(F.to_numpy().T, ddof=0)
    omega = np.atleast_2d(omega)

    quad_alpha = float(alphas @ np.linalg.solve(sigma, alphas))
    quad_f = float(f_bar @ np.linalg.solve(omega, f_bar))
    grs = (T - N - K) / N * quad_alpha / (1.0 + quad_f)
    p = float(stats.f.sf(grs, N, T - N - K))

    alpha_se = np.sqrt(np.diag(sigma) / T * (1.0 + quad_f))
    return GRSResult(
        statistic=float(grs),
        p_value=p,
        alphas=pd.Series(alphas, index=R.columns),
        alpha_t_stats=pd.Series(alphas / alpha_se, index=R.columns),
    )
