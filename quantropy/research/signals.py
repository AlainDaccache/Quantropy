"""Signals: pure, causal maps from price history to a raw target in [-1, 1].

The engine calls ``signal.target(history)`` where ``history`` is the close series
*up to and including* the decision bar t; the resulting order fills at t+1. A signal
must never index beyond its input — the prefix-invariance test in
``tests/test_engine.py`` fails the build if any path peeks.
"""

from __future__ import annotations

from typing import Protocol

import pandas as pd

__all__ = ["Signal", "MovingAverageCross", "TimeSeriesMomentum"]


class Signal(Protocol):
    """Maps history (closes through the decision bar) to a raw weight in [-1, 1]."""

    def target(self, history: pd.Series) -> float: ...


class TimeSeriesMomentum:
    """Time-series momentum: long when the trailing return is positive.

    The Moskowitz-Ooi-Pedersen (2012) effect at its simplest (REFERENCES §2):
    sign of the ``lookback``-bar return, optionally skipping the most recent
    ``skip`` bars (the equity convention — short-term reversal contaminates the
    signal; futures TSMOM conventionally uses skip=0). ``long_only`` controls
    whether a negative trend means flat (ETF-friendly) or short.
    """

    def __init__(self, lookback: int = 252, skip: int = 0, long_only: bool = True):
        if lookback < 2 or skip < 0 or skip >= lookback:
            raise ValueError("require lookback >= 2 and 0 <= skip < lookback")
        self.lookback = lookback
        self.skip = skip
        self.long_only = long_only

    def target(self, history: pd.Series) -> float:
        if len(history) < self.lookback + 1:
            return 0.0
        end = -self.skip if self.skip else None
        window = history.iloc[-(self.lookback + 1) : end]
        if len(window) < 2:
            return 0.0
        trend = float(window.iloc[-1] / window.iloc[0] - 1.0)
        if trend > 0:
            return 1.0
        return 0.0 if self.long_only else -1.0


class MovingAverageCross:
    """Long/flat moving-average cross — the canonical *toy* signal.

    +1 when the fast MA is above the slow MA, else 0. Chosen for T1 because the
    point is proving the plumbing (engine, venue, live seam), not alpha
    (MASTER_SPEC §6, T1).
    """

    def __init__(self, fast: int = 20, slow: int = 100):
        if not 0 < fast < slow:
            raise ValueError("require 0 < fast < slow")
        self.fast = fast
        self.slow = slow

    def target(self, history: pd.Series) -> float:
        if len(history) < self.slow:
            return 0.0  # not enough history — no position, never an exception
        fast_ma = history.iloc[-self.fast :].mean()
        slow_ma = history.iloc[-self.slow :].mean()
        return 1.0 if fast_ma > slow_ma else 0.0
