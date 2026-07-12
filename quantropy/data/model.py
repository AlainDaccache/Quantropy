"""Instrument model: identity plus the contract specs that change P&L math.

Kept deliberately small (P10) — fields are added when a capability actually consumes
them (the futures multiplier matters to the backtester's P&L; an ISIN does not, yet).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = ["AssetClass", "Instrument"]


class AssetClass(str, Enum):
    EQUITY = "equity"
    ETF = "etf"
    FUTURE = "future"
    FX = "fx"


@dataclass(frozen=True, slots=True)
class Instrument:
    """An instrument's identity and the specs the engine needs to get P&L right.

    ``multiplier`` — contract multiplier (1 for cash equities; e.g. 5 for MES).
    ``tick_size`` — minimum price increment; used for realistic fill rounding.
    """

    symbol: str
    asset_class: AssetClass
    currency: str = "USD"
    multiplier: float = 1.0
    tick_size: float = 0.01

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol must be non-empty")
        if self.multiplier <= 0:
            raise ValueError("multiplier must be positive")
        if self.tick_size <= 0:
            raise ValueError("tick_size must be positive")
