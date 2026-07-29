"""Risk limits: enforced in the engine (sim) and before any live order — same object.

T1 ships the two limits that matter first: a hard leverage cap and a latching
drawdown kill switch. Enforcement is *structural*: the engine applies limits to
every target before it becomes an order, so a strategy cannot bypass them
(MASTER_SPEC §6.1: enforced limits, not advisory ones).
"""

from __future__ import annotations

__all__ = ["RiskLimits"]


class RiskLimits:
    """Pre-trade risk limits with a latching drawdown kill switch.

    ``max_leverage`` — hard cap on |weight| (gross position notional / equity).
    ``max_drawdown`` — fraction of peak equity (e.g. 0.20); once breached, the
    switch LATCHES: the book goes flat and stays flat until a human calls
    ``reset()``. Latching is deliberate — an automatic re-entry after a breach is
    how drawdowns compound (Curriculum VIII.5).
    """

    def __init__(self, max_leverage: float = 2.0, max_drawdown: float = 0.20):
        if max_leverage <= 0 or not 0 < max_drawdown < 1:
            raise ValueError("max_leverage > 0 and 0 < max_drawdown < 1 required")
        self.max_leverage = max_leverage
        self.max_drawdown = max_drawdown
        self._peak_equity: float | None = None
        self._killed = False

    @property
    def killed(self) -> bool:
        return self._killed

    def reset(self) -> None:
        """Human intervention: acknowledge the breach and re-arm."""
        self._killed = False
        self._peak_equity = None

    def apply(self, weight: float, equity: float) -> float:
        """Clamp a target weight given current equity. Call once per decision bar."""
        if self._peak_equity is None or equity > self._peak_equity:
            self._peak_equity = equity
        drawdown = 1.0 - equity / self._peak_equity
        if drawdown > self.max_drawdown:
            self._killed = True
        if self._killed:
            return 0.0
        return max(-self.max_leverage, min(self.max_leverage, weight))
