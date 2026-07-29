"""Time value of money.

Ordinary/due annuities with optional contribution growth, present/future value,
perpetuities. Reference: CFA Level I Quantitative Methods (see docs/REFERENCES.md §8);
formulas follow standard TVM identities.

Harvested from ``legacy/src/finance_calculator/time_value_of_money.py`` and fixed in
the port: correct annuity-due ("BGN") handling (the legacy version's was wrong per its
own FIXME), the ``rate == growth`` limit case (legacy divided by zero), and no
module-level side effects.
"""

from __future__ import annotations

from collections.abc import Sequence

__all__ = [
    "future_value",
    "present_value",
    "future_value_annuity",
    "present_value_annuity",
    "present_value_perpetuity",
]


def future_value(pv: float, rate: float | Sequence[float], periods: int | None = None) -> float:
    """Future value of a single cash flow: ``FV = PV * (1 + r)^n``.

    ``rate`` may be a sequence of per-period rates (e.g. a realized path), in which
    case ``periods`` must be omitted and compounding follows the sequence.
    """
    if isinstance(rate, Sequence):
        if periods is not None:
            raise ValueError("pass either a sequence of rates or (rate, periods), not both")
        fv = pv
        for r in rate:
            fv *= 1.0 + r
        return fv
    if periods is None:
        raise ValueError("periods is required when rate is a scalar")
    return pv * (1.0 + rate) ** periods


def present_value(fv: float, rate: float, periods: int) -> float:
    """Present value of a single future cash flow: ``PV = FV / (1 + r)^n``."""
    return fv / (1.0 + rate) ** periods


def _growing_annuity_factor(rate: float, growth: float, periods: int) -> float:
    """FV factor of a growing ordinary annuity of 1 per period.

    ``[(1+r)^n - (1+g)^n] / (r - g)``, with the ``r == g`` limit ``n * (1+r)^(n-1)``.
    """
    if abs(rate - growth) < 1e-12:
        return periods * (1.0 + rate) ** (periods - 1)
    return ((1.0 + rate) ** periods - (1.0 + growth) ** periods) / (rate - growth)


def future_value_annuity(
    contribution: float,
    rate: float,
    periods: int,
    growth: float = 0.0,
    pv: float = 0.0,
    due: bool = False,
) -> float:
    """Future value of a level or growing annuity, plus an optional initial balance.

    Ordinary annuity (``due=False``): contributions at period end.
    Annuity due (``due=True``): contributions at period start — each compounds one
    extra period, so the annuity part is multiplied by ``(1 + rate)``.

    ``FV = PV*(1+r)^n + C * [(1+r)^n - (1+g)^n]/(r-g) * (1+r if due else 1)``
    """
    fv_balance = future_value(pv, rate, periods) if pv else 0.0
    fv_annuity = contribution * _growing_annuity_factor(rate, growth, periods)
    if due:
        fv_annuity *= 1.0 + rate
    return fv_balance + fv_annuity


def present_value_annuity(
    payment: float,
    rate: float,
    periods: int,
    growth: float = 0.0,
    due: bool = False,
) -> float:
    """Present value of a level or growing annuity.

    Level: ``PV = C * (1 - (1+r)^-n) / r``. Growing: discounted growing-annuity
    identity; ``r == g`` limit ``n * C / (1+r)``. Due multiplies by ``(1 + rate)``.
    """
    if abs(rate - growth) < 1e-12:
        pv = periods * payment / (1.0 + rate)
    else:
        pv = payment / (rate - growth) * (1.0 - ((1.0 + growth) / (1.0 + rate)) ** periods)
    if due:
        pv *= 1.0 + rate
    return pv


def present_value_perpetuity(payment: float, rate: float, growth: float = 0.0) -> float:
    """PV of a (growing) perpetuity: ``C / (r - g)`` — the Gordon growth identity."""
    if rate <= growth:
        raise ValueError("rate must exceed growth for a finite perpetuity value")
    return payment / (rate - growth)
