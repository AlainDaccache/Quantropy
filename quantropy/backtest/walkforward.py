"""The walk-forward harness: run the engine per embargoed fold, judge only OOS.

Bridges evaluation's fold splitter to the actual engine: each fold trains (or just
warms up) on the train window and records performance on the test window only.
Signals with no fitting step still benefit — OOS-fold consistency is a robustness
check that a single full-sample equity curve cannot provide (Curriculum VIII.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from quantropy.backtest.engine import BacktestConfig, run_backtest
from quantropy.backtest.limits import RiskLimits
from quantropy.backtest.venue import Venue
from quantropy.data.model import Instrument
from quantropy.evaluation.robustness import walk_forward_splits
from quantropy.portfolio.sizing import Sizer
from quantropy.research.signals import Signal

__all__ = ["FoldResult", "WalkForwardReport", "run_walk_forward"]


@dataclass(frozen=True, slots=True)
class FoldResult:
    fold: int
    oos_return: float  # total simple return over the test window
    oos_sharpe_raw: float
    test_start: pd.Timestamp
    test_end: pd.Timestamp


@dataclass(frozen=True, slots=True)
class WalkForwardReport:
    folds: list[FoldResult]

    @property
    def oos_positive_frac(self) -> float:
        if not self.folds:
            return float("nan")
        return float(np.mean([f.oos_return > 0 for f in self.folds]))

    @property
    def mean_oos_sharpe(self) -> float:
        vals = [f.oos_sharpe_raw for f in self.folds if np.isfinite(f.oos_sharpe_raw)]
        return float(np.mean(vals)) if vals else float("nan")


def run_walk_forward(
    prices: pd.Series,
    signal_factory: Callable[[pd.Series], Signal],
    sizer: Sizer,
    instrument: Instrument,
    train_size: int,
    test_size: int,
    embargo: int = 5,
    venue: Venue | None = None,
    limits_factory: Callable[[], RiskLimits] | None = None,
    config: BacktestConfig | None = None,
) -> WalkForwardReport:
    """Per fold: build the signal from TRAIN data only, run the engine over
    train∪embargo∪test (warm-up included), and score the TEST window alone.

    ``signal_factory`` — receives the train slice, returns the signal (a fixed,
    unfitted signal is `lambda train: my_signal`). ``limits_factory`` — fresh
    limits per fold (the kill switch must not latch across folds).
    """
    splits = walk_forward_splits(prices.index, train_size, test_size, embargo)
    if not splits:
        raise ValueError("no folds — series too short for train/test sizes")
    folds: list[FoldResult] = []
    for k, split in enumerate(splits):
        train = prices.loc[split.train[0] : split.train[-1]]
        window = prices.loc[split.train[0] : split.test[-1]]  # train + embargo + test
        signal = signal_factory(train)
        limits = limits_factory() if limits_factory else RiskLimits()
        result = run_backtest(
            window, signal, sizer, instrument, limits=limits, venue=venue, config=config
        )
        oos_equity = result.equity.loc[split.test[0] : split.test[-1]]
        if len(oos_equity) < 2:
            continue
        rets = oos_equity.pct_change().dropna()
        sd = rets.std(ddof=1)
        folds.append(
            FoldResult(
                fold=k,
                oos_return=float(oos_equity.iloc[-1] / oos_equity.iloc[0] - 1.0),
                oos_sharpe_raw=float(rets.mean() / sd * np.sqrt(252)) if sd > 0 else float("nan"),
                test_start=split.test[0],
                test_end=split.test[-1],
            )
        )
    return WalkForwardReport(folds=folds)
