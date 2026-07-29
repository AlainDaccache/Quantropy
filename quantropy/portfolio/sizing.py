"""Position sizing: volatility targeting (Curriculum VII.5; REFERENCES §3, Carver).

Scale a raw signal so the *position's* expected volatility matches a target:
``weight = raw * min(max_leverage, target_vol / realized_vol)``. Realized vol is
estimated on trailing data only (causal — the feature contract applies to sizing
too).
"""

from __future__ import annotations

from typing import Protocol

import numpy as np
import pandas as pd

from quantropy.core.returns import PERIODS_PER_YEAR, annualize_volatility

__all__ = ["Sizer", "VolatilityTarget"]


class Sizer(Protocol):
    """Maps a raw signal and history to a target weight (fraction of equity)."""

    def scale(self, raw: float, history: pd.Series) -> float: ...


class VolatilityTarget:
    """Vol-targeted sizing with a hard leverage cap.

    ``target_vol`` — annualized volatility the *fully-signaled* position should run
    (e.g. 0.10 = 10%). ``lookback`` — trailing bars for the vol estimate.
    ``max_leverage`` — cap on |weight| regardless of how quiet markets look
    (quiet markets are where vol targeting over-levers; the cap is the safety).
    """

    def __init__(
        self,
        target_vol: float = 0.10,
        lookback: int = 63,
        max_leverage: float = 2.0,
        periods_per_year: int = PERIODS_PER_YEAR["daily"],
    ):
        if target_vol <= 0 or lookback < 2 or max_leverage <= 0:
            raise ValueError("target_vol, max_leverage must be > 0 and lookback >= 2")
        self.target_vol = target_vol
        self.lookback = lookback
        self.max_leverage = max_leverage
        self.periods_per_year = periods_per_year

    def realized_vol(self, history: pd.Series) -> float:
        """Annualized trailing volatility; NaN-safe, causal."""
        rets = history.pct_change().dropna().iloc[-self.lookback :]
        if len(rets) < self.lookback // 2:
            return float("nan")  # too little history to size responsibly
        return annualize_volatility(float(rets.std(ddof=1)), self.periods_per_year)

    def scale(self, raw: float, history: pd.Series) -> float:
        """Map a raw signal in [-1, 1] to a vol-targeted, leverage-capped weight."""
        vol = self.realized_vol(history)
        if not np.isfinite(vol) or vol <= 0:
            return 0.0  # can't measure risk -> take none
        leverage = min(self.max_leverage, self.target_vol / vol)
        return float(raw) * leverage
