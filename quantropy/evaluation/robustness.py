"""The honesty statistics: PSR, deflated Sharpe, bootstrap CIs, walk-forward.

This is the project's center of gravity (MASTER_SPEC §2): the statistics that make
a Sharpe ratio *believable*. References (docs/REFERENCES.md §1): Bailey & López de
Prado (2012) "The Sharpe Ratio Efficient Frontier" (PSR) and (2014) "The Deflated
Sharpe Ratio" (DSR); block bootstrap per Politis-Romano-style fixed blocks.

Convention that matters: PSR/DSR operate on **per-period** (NOT annualized) Sharpe
ratios and per-period return moments. Annualize for humans, deflate in periods.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

__all__ = [
    "probabilistic_sharpe",
    "expected_max_sharpe",
    "deflated_sharpe",
    "sharpe_confidence_interval",
    "WalkForwardSplit",
    "walk_forward_splits",
]

_EULER_GAMMA = 0.5772156649015329


def _sr_per_period(returns: pd.Series) -> float:
    r = returns.dropna()
    sd = r.std(ddof=1)
    if len(r) < 2 or sd == 0:
        return float("nan")
    return float(r.mean() / sd)


def probabilistic_sharpe(
    returns: pd.Series,
    benchmark_sr: float = 0.0,
) -> float:
    """PSR: probability the true (per-period) Sharpe exceeds ``benchmark_sr``.

    Bailey & López de Prado (2012): accounts for sample length, skewness, and
    kurtosis — a short, lucky, negatively-skewed track record gets the credibility
    it deserves (little).
    """
    r = returns.dropna()
    n = len(r)
    if n < 3:
        return float("nan")
    sr = _sr_per_period(r)
    skew = float(stats.skew(r, bias=False))
    kurt = float(stats.kurtosis(r, fisher=False, bias=False))  # Pearson (normal=3)
    denom = np.sqrt(1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr**2)
    if not np.isfinite(denom) or denom <= 0:
        return float("nan")
    z = (sr - benchmark_sr) * np.sqrt(n - 1) / denom
    return float(stats.norm.cdf(z))


def expected_max_sharpe(n_trials: int, var_trial_sr: float) -> float:
    """E[max SR] under N independent trials of zero-true-Sharpe strategies.

    Bailey & López de Prado (2014): the Sharpe you'd expect the *best* of N tries
    to show by pure luck. This is the hurdle a discovered strategy must clear.
    ``var_trial_sr`` — variance of the per-period Sharpe across the trials.
    """
    if n_trials < 1 or var_trial_sr < 0:
        raise ValueError("n_trials >= 1 and var_trial_sr >= 0 required")
    if n_trials == 1 or var_trial_sr == 0:
        return 0.0  # no selection happened -> nothing to deflate
    z1 = stats.norm.ppf(1.0 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1.0 - 1.0 / (n_trials * np.e))
    return float(np.sqrt(var_trial_sr) * ((1.0 - _EULER_GAMMA) * z1 + _EULER_GAMMA * z2))


def deflated_sharpe(
    returns: pd.Series,
    n_trials: int,
    var_trial_sr: float,
) -> float:
    """DSR: PSR evaluated against the luck hurdle implied by the trials count.

    ``n_trials`` — how many strategy configurations were tried, cumulatively (the
    trials ledger's number — not this study's alone). Reporting a Sharpe without
    this number is the pseudo-mathematics the references warn about.
    """
    hurdle = expected_max_sharpe(n_trials, var_trial_sr)
    return probabilistic_sharpe(returns, benchmark_sr=hurdle)


def sharpe_confidence_interval(
    returns: pd.Series,
    level: float = 0.90,
    block: int = 21,
    n_boot: int = 2000,
    seed: int = 0,
    periods_per_year: int = 252,
) -> tuple[float, float]:
    """Block-bootstrap CI for the *annualized* Sharpe (blocks preserve serial
    dependence a naive iid bootstrap would destroy). Seeded — reproducible."""
    r = returns.dropna().to_numpy()
    n = len(r)
    if n < 2 * block:
        raise ValueError("series too short for the chosen block length")
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block))
    starts_max = n - block
    sharpes = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, starts_max + 1, size=n_blocks)
        sample = np.concatenate([r[s : s + block] for s in starts])[:n]
        sd = sample.std(ddof=1)
        sharpes[b] = np.nan if sd == 0 else sample.mean() / sd * np.sqrt(periods_per_year)
    lo, hi = np.nanpercentile(sharpes, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return float(lo), float(hi)


@dataclass(frozen=True, slots=True)
class WalkForwardSplit:
    """One fold: train on [train_start, train_end], embargo, test on [test_start, test_end]."""

    train: pd.Index
    test: pd.Index


def walk_forward_splits(
    index: pd.Index,
    train_size: int,
    test_size: int,
    embargo: int = 5,
) -> list[WalkForwardSplit]:
    """Rolling, embargoed walk-forward folds over a time index.

    The embargo drops ``embargo`` bars between train and test so serial dependence
    (and signal lookbacks) can't leak the train edge into the test set — the
    single-series version of purging (López de Prado 2018, ch. 7).
    Test sets are disjoint and consecutive; every decision uses only prior data.
    """
    if train_size < 2 or test_size < 1 or embargo < 0:
        raise ValueError("train_size >= 2, test_size >= 1, embargo >= 0")
    splits: list[WalkForwardSplit] = []
    start = 0
    while True:
        train_end = start + train_size
        test_start = train_end + embargo
        test_end = test_start + test_size
        if test_end > len(index):
            break
        splits.append(
            WalkForwardSplit(
                train=index[start:train_end],
                test=index[test_start:test_end],
            )
        )
        start += test_size  # roll forward by one test window
    return splits
