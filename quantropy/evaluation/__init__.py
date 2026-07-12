"""Evaluation: performance metrics and the honesty statistics (PSR/DSR/bootstrap)."""

from quantropy.evaluation.metrics import summary
from quantropy.evaluation.overfitting import (
    AcceptanceGates,
    GateReport,
    min_backtest_length,
    pbo,
)
from quantropy.evaluation.robustness import (
    deflated_sharpe,
    expected_max_sharpe,
    probabilistic_sharpe,
    sharpe_confidence_interval,
    walk_forward_splits,
)

__all__ = [
    "summary",
    "probabilistic_sharpe",
    "expected_max_sharpe",
    "deflated_sharpe",
    "sharpe_confidence_interval",
    "walk_forward_splits",
    "pbo",
    "min_backtest_length",
    "AcceptanceGates",
    "GateReport",
]
