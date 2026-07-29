"""PBO, MinBTL, and acceptance gates — the rest of the honesty stack.

- **PBO** (Bailey-Borwein-López de Prado-Zhu 2017): probability of backtest
  overfitting via Combinatorially Symmetric Cross-Validation — how often the
  best-in-sample strategy configuration underperforms the median out-of-sample.
- **MinBTL** (Bailey et al. 2014, Notices of the AMS): the minimum backtest length
  needed before a target Sharpe is distinguishable from best-of-N luck. Their
  famous illustration: ~45 trials already demand ~5 years of data.
- **Acceptance gates**: pre-committed pass/fail criteria a strategy clears before
  paper capital — decided before results exist, so the bar can't bend to them
  (MASTER_SPEC §6.2).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

from quantropy.evaluation.robustness import _EULER_GAMMA

__all__ = ["pbo", "min_backtest_length", "AcceptanceGates", "GateReport"]


def pbo(strategy_returns: pd.DataFrame, n_blocks: int = 10) -> float:
    """Probability of Backtest Overfitting via CSCV.

    ``strategy_returns`` — T×N returns of N strategy *configurations* (the trials).
    Splits time into ``n_blocks`` even blocks; for every half/half combination,
    picks the best in-sample config and asks where it ranks out-of-sample. PBO is
    the fraction of combinations where the IS winner lands in the OOS bottom half.
    ~0 = selection generalizes; ~0.5 = ranking is noise; >0.5 = actively inverted.
    """
    if n_blocks % 2 or n_blocks < 4:
        raise ValueError("n_blocks must be even and >= 4")
    if strategy_returns.shape[1] < 2:
        raise ValueError("PBO needs at least two strategy configurations")
    r = strategy_returns.dropna(how="any").to_numpy()
    t = len(r)
    if t < n_blocks * 10:
        raise ValueError("series too short for the chosen block count")
    blocks = np.array_split(np.arange(t), n_blocks)

    def sr(x: np.ndarray) -> np.ndarray:
        sd = x.std(axis=0, ddof=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(sd > 0, x.mean(axis=0) / sd, -np.inf)

    logits = []
    for half in combinations(range(n_blocks), n_blocks // 2):
        is_idx = np.concatenate([blocks[i] for i in half])
        oos_idx = np.concatenate([blocks[i] for i in range(n_blocks) if i not in half])
        best = int(np.argmax(sr(r[is_idx])))
        oos = sr(r[oos_idx])
        # relative rank of the IS winner among OOS results, in (0, 1)
        omega = (stats.rankdata(oos)[best]) / (len(oos) + 1.0)
        logits.append(np.log(omega / (1.0 - omega)))
    return float(np.mean(np.array(logits) <= 0.0))


def min_backtest_length(n_trials: int, target_annual_sr: float) -> float:
    """Minimum backtest length in YEARS before ``target_annual_sr`` beats
    best-of-``n_trials`` luck (MinBTL). Reference point from the paper's own
    illustration: n_trials=45, SR=1 → ≈ 5 years."""
    if n_trials < 2 or target_annual_sr <= 0:
        raise ValueError("n_trials >= 2 and target_annual_sr > 0 required")
    z1 = stats.norm.ppf(1.0 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1.0 - 1.0 / (n_trials * np.e))
    e_max = (1.0 - _EULER_GAMMA) * z1 + _EULER_GAMMA * z2
    return float((e_max / target_annual_sr) ** 2)


@dataclass(frozen=True, slots=True)
class GateReport:
    passed: bool
    reasons: list[str]  # every failed criterion, named — silence is not a verdict


@dataclass(frozen=True, slots=True)
class AcceptanceGates:
    """Pre-committed criteria. Instantiate BEFORE running the study; the instance
    (with its thresholds) belongs in the research log next to the hypothesis."""

    min_deflated_sharpe: float = 0.90  # P(true SR > luck hurdle)
    max_drawdown: float = 0.35
    min_bars: int = 750  # ~3 years daily
    max_pbo: float = 0.50
    min_oos_positive_folds: float = 0.5  # walk-forward: fraction of OOS folds > 0

    def evaluate(
        self,
        deflated_sharpe: float,
        max_dd: float,
        n_bars: int,
        pbo_value: float | None = None,
        oos_positive_frac: float | None = None,
    ) -> GateReport:
        reasons = []
        if not deflated_sharpe >= self.min_deflated_sharpe:  # NaN fails, correctly
            reasons.append(f"DSR {deflated_sharpe:.3f} < {self.min_deflated_sharpe}")
        if not max_dd <= self.max_drawdown:
            reasons.append(f"maxDD {max_dd:.1%} > {self.max_drawdown:.0%}")
        if n_bars < self.min_bars:
            reasons.append(f"only {n_bars} bars < {self.min_bars}")
        if pbo_value is not None and not pbo_value <= self.max_pbo:
            reasons.append(f"PBO {pbo_value:.2f} > {self.max_pbo}")
        if oos_positive_frac is not None and not (
            oos_positive_frac >= self.min_oos_positive_folds
        ):
            reasons.append(
                f"OOS positive folds {oos_positive_frac:.0%} < "
                f"{self.min_oos_positive_folds:.0%}"
            )
        return GateReport(passed=not reasons, reasons=reasons)
