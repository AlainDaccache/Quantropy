"""Backtesting: event-driven engine, the venue seam, costs, risk limits.

The central law (MASTER_SPEC P3/P6): the ENGINE owns the fill lag — a decision made
on bar t fills at bar t+1 through a Venue. `SimulatedVenue` (research) and the live
IBKR venue implement the same Protocol, so what is backtested is what trades.
"""

from quantropy.backtest.engine import BacktestConfig, BacktestResult, run_backtest
from quantropy.backtest.limits import RiskLimits
from quantropy.backtest.venue import Fill, Order, SimulatedVenue, Venue

__all__ = [
    "BacktestConfig",
    "BacktestResult",
    "run_backtest",
    "RiskLimits",
    "Order",
    "Fill",
    "Venue",
    "SimulatedVenue",
]
