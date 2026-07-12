"""Combining sleeves into a book: inverse-vol weights, then vol-target the whole.

The flagship-book aggregation (MASTER_SPEC M2): each sleeve contributes risk, not
notional — weight sleeves by trailing inverse volatility (a robust, estimation-
light allocation; Curriculum VII.4), then scale the *combined* stream to the book's
target volatility with a hard leverage cap. All estimates are trailing-only — the
causal contract applies to allocation exactly as it does to signals.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from quantropy.core.returns import PERIODS_PER_YEAR, annualize_volatility

__all__ = ["combine_sleeves"]


def combine_sleeves(
    sleeve_returns: pd.DataFrame,
    target_vol: float = 0.10,
    lookback: int = 63,
    max_leverage: float = 3.0,
    periods_per_year: int = PERIODS_PER_YEAR["daily"],
) -> pd.DataFrame:
    """Risk-weight sleeves and vol-target the combined book. Fully causal.

    ``sleeve_returns`` — one column per sleeve, simple per-period returns.
    Returns a frame with per-sleeve weights, the book leverage, and ``book``
    (the combined, vol-targeted return stream). Bars with insufficient history
    carry zero exposure — no position before risk can be measured.
    """
    if sleeve_returns.shape[1] < 1:
        raise ValueError("need at least one sleeve")
    if target_vol <= 0 or lookback < 2 or max_leverage <= 0:
        raise ValueError("target_vol, max_leverage > 0 and lookback >= 2 required")

    # trailing per-sleeve vol -> inverse-vol weights, normalized (shifted: weights
    # decided on t-1 information apply to bar t — no same-bar estimation)
    trailing_vol = sleeve_returns.rolling(lookback, min_periods=lookback).std(ddof=1)
    inv = (1.0 / trailing_vol).replace([np.inf, -np.inf], np.nan)
    weights = inv.div(inv.sum(axis=1), axis=0).shift(1)

    sleeve_mix = (weights * sleeve_returns).sum(axis=1, min_count=1).fillna(0.0)

    # vol-target the combined stream (again trailing, again shifted)
    mix_vol = sleeve_mix.rolling(lookback, min_periods=lookback).std(ddof=1)
    ann_mix_vol = mix_vol * np.sqrt(periods_per_year)
    leverage = (target_vol / ann_mix_vol).clip(upper=max_leverage).shift(1).fillna(0.0)

    book = leverage * sleeve_mix
    out = weights.add_suffix("_w")
    out["leverage"] = leverage
    out["book"] = book
    return out


def realized_book_vol(book: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized realized vol of the combined book (diagnostic)."""
    r = book.dropna()
    return annualize_volatility(float(r.std(ddof=1)), periods_per_year)
