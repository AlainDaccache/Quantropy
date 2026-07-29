"""DCF with fading growth — and its inverse, market-implied expectations.

Two-stage free-cash-flow model (Curriculum IV.4): growth fades linearly from
``growth`` to ``terminal_growth`` over ``horizon`` years (the fade discipline —
hockey-sticks are how DCFs lie), then a Gordon terminal value. The inverse,
``implied_growth``, asks the more honest question: *what does the price already
believe?* (Rappaport-Mauboussin, REFERENCES §6). Solved by bisection with a
monotonicity guarantee.
"""

from __future__ import annotations

from scipy.optimize import brentq

__all__ = ["dcf_value", "implied_growth"]


def dcf_value(
    fcf0: float,
    growth: float,
    discount_rate: float,
    horizon: int = 10,
    terminal_growth: float = 0.02,
) -> float:
    """PV of FCF fading from ``growth`` to ``terminal_growth`` + Gordon terminal.

    ``fcf0`` — last observed annual free cash flow. Requires
    ``discount_rate > terminal_growth`` (a firm can't outgrow its discount rate
    forever — the Gordon condition).
    """
    if discount_rate <= terminal_growth:
        raise ValueError("discount_rate must exceed terminal_growth (Gordon condition)")
    if horizon < 1:
        raise ValueError("horizon >= 1")
    pv = 0.0
    fcf = fcf0
    for year in range(1, horizon + 1):
        # linear fade of the growth rate over the explicit horizon
        w = (year - 1) / max(horizon - 1, 1)
        g = growth * (1 - w) + terminal_growth * w
        fcf *= 1.0 + g
        pv += fcf / (1.0 + discount_rate) ** year
    terminal = fcf * (1.0 + terminal_growth) / (discount_rate - terminal_growth)
    pv += terminal / (1.0 + discount_rate) ** horizon
    return pv


def implied_growth(
    market_value: float,
    fcf0: float,
    discount_rate: float,
    horizon: int = 10,
    terminal_growth: float = 0.02,
    bounds: tuple[float, float] = (-0.5, 1.0),
) -> float:
    """Reverse DCF: the stage-one growth rate that justifies ``market_value``.

    dcf_value is strictly increasing in ``growth`` (for fcf0 > 0), so the root is
    unique when it exists; raises with the price outside the achievable range
    rather than returning a boundary silently.
    """
    if fcf0 <= 0:
        raise ValueError("implied growth needs positive current FCF (fcf0 > 0)")
    lo, hi = bounds

    def gap(g: float) -> float:
        return dcf_value(fcf0, g, discount_rate, horizon, terminal_growth) - market_value

    if gap(lo) > 0:
        raise ValueError("market value below the no-growth floor — check inputs")
    if gap(hi) < 0:
        raise ValueError(f"market value implies growth above {hi:.0%} — outside bounds")
    return float(brentq(gap, lo, hi, xtol=1e-8))
