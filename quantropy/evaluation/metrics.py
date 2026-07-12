"""Performance metrics on an equity curve.

T1 ships the basics; the anti-overfit statistics (deflated Sharpe, PBO — the
statistics that make these numbers *believable*) arrive with M2 and are the
project's center of gravity. Until then, every Sharpe printed here is a raw,
undeflated number and is labeled as such.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from quantropy.core.returns import PERIODS_PER_YEAR, annualize_volatility, cagr

__all__ = ["max_drawdown", "sharpe", "summary"]


def max_drawdown(equity: pd.Series) -> float:
    """Largest peak-to-trough decline, as a positive fraction."""
    peak = equity.cummax()
    return float((1.0 - equity / peak).max())


def sharpe(
    equity: pd.Series,
    periods_per_year: int = PERIODS_PER_YEAR["daily"],
    rf_annual: float = 0.0,
) -> float:
    """Annualized Sharpe of the equity curve's returns (RAW — not deflated).

    ``rf_annual`` — annual risk-free rate to excess against (default 0; pass the
    cash rate for an honest excess-return Sharpe).
    """
    rets = equity.pct_change().dropna()
    if len(rets) < 2 or rets.std(ddof=1) == 0:
        return float("nan")
    rf_periodic = (1.0 + rf_annual) ** (1.0 / periods_per_year) - 1.0
    excess = rets - rf_periodic
    return float(excess.mean() / excess.std(ddof=1) * np.sqrt(periods_per_year))


def summary(equity: pd.Series, periods_per_year: int = PERIODS_PER_YEAR["daily"]) -> dict:
    """Headline stats. Sharpe here is RAW; deflation (trials-aware) lands in M2."""
    years = len(equity) / periods_per_year
    growth = float(equity.iloc[-1] / equity.iloc[0])
    rets = equity.pct_change().dropna()
    return {
        "cagr": cagr(growth, years) if growth > 0 and years > 0 else float("nan"),
        "ann_vol": annualize_volatility(float(rets.std(ddof=1)), periods_per_year),
        "sharpe_raw": sharpe(equity, periods_per_year),
        "max_drawdown": max_drawdown(equity),
        "bars": int(len(equity)),
    }
