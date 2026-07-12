"""The venue seam: one Protocol, simulated and live implementations.

An Order says *what* to trade; a Venue decides *how it fills*. The engine never
computes its own fills — that separation is what makes the backtest and the live
path share one code path (MASTER_SPEC P6). The simulated venue models frictions
explicitly (slippage, commission) rather than assuming free fills.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from quantropy.data.model import Instrument

__all__ = ["Order", "Fill", "Venue", "SimulatedVenue"]


@dataclass(frozen=True, slots=True)
class Order:
    """A signed order for `units` of `instrument` (units, not notional)."""

    instrument: Instrument
    units: float  # positive = buy, negative = sell

    @property
    def is_noop(self) -> bool:
        return self.units == 0.0


@dataclass(frozen=True, slots=True)
class Fill:
    """An execution: price actually paid/received, plus explicit costs."""

    units: float
    price: float  # per-unit fill price, slippage included
    cost: float  # commissions + fees, in cash


class Venue(Protocol):
    """The single seam between research and production.

    ``execute`` turns an order into a fill given the current market price. The
    simulated implementation fills at the bar's price with modelled frictions; the
    live implementation routes to a broker. Same signature, same caller (the
    engine / live runner).
    """

    def execute(self, order: Order, market_price: float) -> Fill: ...


class SimulatedVenue:
    """Research venue: fills at the bar price with explicit, modelled frictions.

    ``slippage_bps`` — adverse price movement per side, in basis points (buys fill
    above, sells below — never in your favor).
    ``cost_bps`` — proportional costs (spread share, fees) on traded notional.
    ``commission`` — flat cash per executed order.
    """

    def __init__(self, slippage_bps: float = 1.0, cost_bps: float = 1.0, commission: float = 0.0):
        if min(slippage_bps, cost_bps, commission) < 0:
            raise ValueError("frictions cannot be negative")
        self.slippage_bps = slippage_bps
        self.cost_bps = cost_bps
        self.commission = commission

    def execute(self, order: Order, market_price: float) -> Fill:
        if order.is_noop:
            return Fill(units=0.0, price=market_price, cost=0.0)
        side = 1.0 if order.units > 0 else -1.0
        fill_price = market_price * (1.0 + side * self.slippage_bps / 1e4)
        notional = abs(order.units) * fill_price * order.instrument.multiplier
        cost = notional * self.cost_bps / 1e4 + self.commission
        return Fill(units=order.units, price=fill_price, cost=cost)
