"""Signals: pure, causal maps from price history to a raw target in [-1, 1].

The engine calls ``signal.target(history)`` where ``history`` is the close series
*up to and including* the decision bar t; the resulting order fills at t+1. A signal
must never index beyond its input — the prefix-invariance test in
``tests/test_engine.py`` fails the build if any path peeks.
"""

from __future__ import annotations

from typing import Protocol

import pandas as pd

__all__ = ["Signal", "MovingAverageCross"]


class Signal(Protocol):
    """Maps history (closes through the decision bar) to a raw weight in [-1, 1]."""

    def target(self, history: pd.Series) -> float: ...


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
