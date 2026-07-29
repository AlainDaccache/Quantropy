"""Interactive Brokers venue — the live end of the venue seam.

Design (MASTER_SPEC P6): implements the same ``execute(Order, market_price) -> Fill``
contract as ``SimulatedVenue``, so the decision path (signal → sizing → limits →
Order) is byte-identical between backtest and live; only the venue differs. Orders
are plain market orders at T1 — order-type sophistication belongs to M8, plumbing
proof belongs to T1.

Status: **[paper]** — written against ib_async's documented API; exercised against a
live IB Gateway the first time the owner runs ``examples/thin_thread.py --live``
with TWS/Gateway up (API port 7497 for paper). Until that run happens this module is
flagged code-complete-but-unverified — stated per the honesty rule (P8).
"""

from __future__ import annotations

import math
import os

from quantropy.backtest.venue import Fill, Order
from quantropy.data.model import AssetClass

__all__ = ["IBKRVenue"]


class IBKRVenue:
    """Live/paper venue over ib_async. One venue instance = one gateway session."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        client_id: int | None = None,
        timeout: float = 30.0,
    ):
        from ib_async import IB  # [live] extra; deferred so core imports stay clean

        self.host = host or os.environ.get("IBKR_HOST", "127.0.0.1")
        self.port = int(port or os.environ.get("IBKR_PORT", "7497"))  # 7497 = paper
        self.client_id = int(client_id or os.environ.get("IBKR_CLIENT_ID", "1"))
        self.timeout = timeout
        self.ib = IB()
        self.ib.connect(self.host, self.port, clientId=self.client_id, timeout=timeout)

    # -- venue contract --------------------------------------------------------

    def execute(self, order: Order, market_price: float) -> Fill:
        """Place a market order and wait for the fill. Same contract as the sim.

        ``market_price`` is the caller's reference price (used only for sanity
        logging; the real fill price comes from the broker).
        """
        from ib_async import MarketOrder

        if order.is_noop:
            return Fill(units=0.0, price=market_price, cost=0.0)

        contract = self._contract(order)
        self.ib.qualifyContracts(contract)
        side = "BUY" if order.units > 0 else "SELL"
        qty = abs(_round_units(order))
        if qty == 0:
            return Fill(units=0.0, price=market_price, cost=0.0)

        trade = self.ib.placeOrder(contract, MarketOrder(side, qty))
        self.ib.sleep(0)  # let the event loop breathe
        while not trade.isDone():
            self.ib.waitOnUpdate(timeout=self.timeout)

        if trade.orderStatus.status != "Filled":
            raise RuntimeError(
                f"order not filled: status={trade.orderStatus.status!r} "
                f"({side} {qty} {order.instrument.symbol})"
            )
        fill_price = float(trade.orderStatus.avgFillPrice)
        commission = sum(
            f.commissionReport.commission for f in trade.fills if f.commissionReport
        )
        signed_units = qty if order.units > 0 else -qty
        return Fill(units=float(signed_units), price=fill_price, cost=float(commission))

    def positions(self) -> dict[str, float]:
        """Current broker positions by symbol — the reconciliation source of truth."""
        return {p.contract.symbol: float(p.position) for p in self.ib.positions()}

    def disconnect(self) -> None:
        self.ib.disconnect()

    # -- helpers ----------------------------------------------------------------

    def _contract(self, order: Order):
        from ib_async import Future, Stock

        inst = order.instrument
        if inst.asset_class in (AssetClass.EQUITY, AssetClass.ETF):
            return Stock(inst.symbol, "SMART", inst.currency)
        if inst.asset_class is AssetClass.FUTURE:
            # front-month resolution via qualifyContracts on a continuous symbol
            # is deliberately NOT attempted at T1 — pass an explicit expiry symbol
            # (e.g. 'MESU6') when the futures leg of T1 runs.
            return Future(inst.symbol, exchange="CME", currency=inst.currency)
        raise ValueError(f"unsupported asset class for IBKR venue: {inst.asset_class}")


def _round_units(order: Order) -> int:
    """Whole units only (shares/contracts) — fractional support is out of T1 scope."""
    return int(math.floor(abs(order.units)))
