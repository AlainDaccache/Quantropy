"""The event-driven engine: owns the fill lag, applies limits, never peeks.

Per-bar sequence (the no-look-ahead contract, tested in tests/test_engine.py):

1. **Settle** — mark the existing position to today's price (futures: daily cash
   settlement; equities: mark-to-market).
2. **Fill** — execute the order decided on the *previous* bar, at today's price,
   through the Venue (slippage/costs are the venue's job).
3. **Decide** — hand the signal only history *through today*, size it, clamp it
   with RiskLimits, and queue the order for tomorrow.

A decision can therefore never touch the price it fills at, and the signal can
never see a bar after its decision date. Accounting supports both asset styles:
equities consume cash; futures settle P&L daily into cash (margin is not modelled
at T1 — flagged, arrives with the flagship book in M2).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from quantropy.backtest.limits import RiskLimits
from quantropy.backtest.venue import Order, SimulatedVenue, Venue
from quantropy.data.model import AssetClass, Instrument
from quantropy.portfolio.sizing import Sizer
from quantropy.research.signals import Signal

__all__ = ["BacktestConfig", "BacktestResult", "run_backtest"]


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    """Declarative, reproducible run description (MASTER_SPEC P5).

    ``margin_rate_annual`` — interest charged on negative cash (equity leverage is
    never free; IBKR margin runs ~benchmark+1.5% retail). Futures embed financing
    in the basis, so it applies to the equity accounting path only.
    ``periods_per_year`` — accrual convention for the daily charge.
    """

    initial_cash: float = 100_000.0
    snapshot_id: str = ""  # the pinned data snapshot this run used (provenance)
    margin_rate_annual: float = 0.06
    periods_per_year: int = 252


@dataclass
class BacktestResult:
    """Equity curve plus per-bar diagnostics; metrics live in evaluation."""

    frame: pd.DataFrame  # columns: equity, position_units, target_weight, cost
    config: BacktestConfig
    killed: bool = False  # did the drawdown switch latch during the run?
    total_costs: float = field(init=False)

    def __post_init__(self) -> None:
        self.total_costs = float(self.frame["cost"].sum())

    @property
    def equity(self) -> pd.Series:
        return self.frame["equity"]


def run_backtest(
    prices: pd.Series,
    signal: Signal,
    sizer: Sizer,
    instrument: Instrument,
    limits: RiskLimits | None = None,
    venue: Venue | None = None,
    config: BacktestConfig | None = None,
) -> BacktestResult:
    """Run the event-driven loop over a close-price series.

    ``prices`` — close series indexed by date (from a pinned snapshot).
    All decisions are made on bar t and fill on bar t+1 via ``venue``.
    """
    if prices.isna().any():
        raise ValueError("prices contain NaNs — clean data upstream (Curriculum I.6)")
    if len(prices) < 2:
        raise ValueError("need at least two bars")
    limits = limits if limits is not None else RiskLimits()
    venue = venue if venue is not None else SimulatedVenue()
    config = config if config is not None else BacktestConfig()

    cash = config.initial_cash
    units = 0.0
    last_price: float | None = None
    pending_units: float | None = None  # order queued on the previous bar

    rows = []
    for t, (date, price) in enumerate(prices.items()):
        price = float(price)

        # 1) settle the existing position to today's price; charge financing
        if last_price is not None:
            if instrument.asset_class is AssetClass.FUTURE and units != 0.0:
                cash += units * (price - last_price) * instrument.multiplier
            elif cash < 0.0:
                # leveraged equity position: margin interest accrues daily —
                # free leverage is how backtests flatter themselves (spec P2/P6)
                cash -= abs(cash) * config.margin_rate_annual / config.periods_per_year

        # 2) fill the order decided on the previous bar, at today's price
        cost = 0.0
        if pending_units is not None:
            delta = pending_units - units
            fill = venue.execute(Order(instrument, delta), price)
            if instrument.asset_class is AssetClass.FUTURE:
                cash -= fill.cost  # futures: no cash outlay for notional, costs only
            else:
                cash -= fill.units * fill.price * instrument.multiplier + fill.cost
            units += fill.units
            cost = fill.cost
            pending_units = None

        # mark equity
        if instrument.asset_class is AssetClass.FUTURE:
            equity = cash  # daily-settled: cash IS equity
        else:
            equity = cash + units * price * instrument.multiplier

        # 3) decide from history THROUGH today only; fills tomorrow
        history = prices.iloc[: t + 1]
        raw = signal.target(history)
        weight = limits.apply(sizer.scale(raw, history), equity)
        if t < len(prices) - 1:  # nothing to queue on the final bar
            target_notional = weight * equity
            pending_units = target_notional / (price * instrument.multiplier)

        rows.append((date, equity, units, weight, cost))
        last_price = price  # today's close becomes the settlement reference

    frame = pd.DataFrame(
        rows, columns=["date", "equity", "position_units", "target_weight", "cost"]
    ).set_index("date")
    return BacktestResult(frame=frame, config=config, killed=limits.killed)
