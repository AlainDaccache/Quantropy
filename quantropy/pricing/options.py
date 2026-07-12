"""Options: Black-Scholes-Merton, Greeks, CRR binomial trees, implied vol.

Teaching-grade from first principles (Curriculum V.2–.3; REFERENCES §5) —
the closed forms are exactly what makes this `[deep]`-verifiable: prices check
against published textbook values (Hull), Greeks check against bump-and-reprice,
trees check against BSM in the limit, and implied vol round-trips the price.

Conventions, stated: ``T`` in years; ``r`` and dividend yield ``q`` continuously
compounded; theta per YEAR (divide by 365 for per-day); vega/rho per unit of
vol/rate (divide by 100 for per-point).
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

__all__ = ["bs_price", "bs_greeks", "implied_vol", "binomial_price"]


def _d1_d2(s, k, t, r, sigma, q):
    d1 = (np.log(s / k) + (r - q + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
    return d1, d1 - sigma * np.sqrt(t)


def _validate(s, k, t, sigma):
    if min(s, k) <= 0:
        raise ValueError("spot and strike must be positive")
    if t <= 0:
        raise ValueError("T must be positive (price expiry payoffs directly)")
    if sigma <= 0:
        raise ValueError("sigma must be positive")


def bs_price(s: float, k: float, t: float, r: float, sigma: float,
             kind: str = "call", q: float = 0.0) -> float:
    """Black-Scholes-Merton European price with continuous dividend yield ``q``."""
    _validate(s, k, t, sigma)
    d1, d2 = _d1_d2(s, k, t, r, sigma, q)
    if kind == "call":
        return float(s * np.exp(-q * t) * norm.cdf(d1) - k * np.exp(-r * t) * norm.cdf(d2))
    if kind == "put":
        return float(k * np.exp(-r * t) * norm.cdf(-d2) - s * np.exp(-q * t) * norm.cdf(-d1))
    raise ValueError("kind must be 'call' or 'put'")


def bs_greeks(s: float, k: float, t: float, r: float, sigma: float,
              kind: str = "call", q: float = 0.0) -> dict:
    """Analytic Greeks (cross-checked against bump-and-reprice in tests)."""
    _validate(s, k, t, sigma)
    d1, d2 = _d1_d2(s, k, t, r, sigma, q)
    disc_q, disc_r = np.exp(-q * t), np.exp(-r * t)
    pdf = norm.pdf(d1)
    gamma = disc_q * pdf / (s * sigma * np.sqrt(t))
    vega = s * disc_q * pdf * np.sqrt(t)
    if kind == "call":
        delta = disc_q * norm.cdf(d1)
        theta = (-s * disc_q * pdf * sigma / (2 * np.sqrt(t))
                 - r * k * disc_r * norm.cdf(d2) + q * s * disc_q * norm.cdf(d1))
        rho = k * t * disc_r * norm.cdf(d2)
    elif kind == "put":
        delta = -disc_q * norm.cdf(-d1)
        theta = (-s * disc_q * pdf * sigma / (2 * np.sqrt(t))
                 + r * k * disc_r * norm.cdf(-d2) - q * s * disc_q * norm.cdf(-d1))
        rho = -k * t * disc_r * norm.cdf(-d2)
    else:
        raise ValueError("kind must be 'call' or 'put'")
    return {"delta": float(delta), "gamma": float(gamma), "vega": float(vega),
            "theta": float(theta), "rho": float(rho)}


def implied_vol(price: float, s: float, k: float, t: float, r: float,
                kind: str = "call", q: float = 0.0,
                bounds: tuple[float, float] = (1e-4, 5.0)) -> float:
    """Invert BSM for volatility (Brent). Prices outside the no-arbitrage range
    raise with the violated bound named — a price below intrinsic is data error,
    not 'zero vol'."""
    lo, hi = bounds
    p_lo, p_hi = (bs_price(s, k, t, r, v, kind, q) for v in (lo, hi))
    if not p_lo <= price <= p_hi:
        raise ValueError(
            f"price {price:.4f} outside achievable range [{p_lo:.4f}, {p_hi:.4f}] "
            f"for vol in [{lo}, {hi}] — check for arbitrage/data error"
        )
    return float(brentq(lambda v: bs_price(s, k, t, r, v, kind, q) - price, lo, hi,
                        xtol=1e-10))


def binomial_price(s: float, k: float, t: float, r: float, sigma: float,
                   kind: str = "call", style: str = "european",
                   steps: int = 500, q: float = 0.0) -> float:
    """Cox-Ross-Rubinstein tree; handles American early exercise by backward
    induction with the exercise check at every node. Converges to BSM for
    European options as steps grow (tested)."""
    _validate(s, k, t, sigma)
    if style not in ("european", "american"):
        raise ValueError("style must be 'european' or 'american'")
    if steps < 1:
        raise ValueError("steps >= 1")
    dt = t / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    disc = np.exp(-r * dt)
    p = (np.exp((r - q) * dt) - d) / (u - d)
    if not 0.0 < p < 1.0:
        raise ValueError("risk-neutral probability outside (0,1) — reduce dt or check inputs")

    j = np.arange(steps + 1)
    prices = s * u ** (steps - j) * d**j
    sign = 1.0 if kind == "call" else -1.0
    values = np.maximum(sign * (prices - k), 0.0)
    for step in range(steps - 1, -1, -1):
        values = disc * (p * values[:-1] + (1 - p) * values[1:])
        if style == "american":
            prices = s * u ** (step - np.arange(step + 1)) * d ** np.arange(step + 1)
            values = np.maximum(values, sign * (prices - k))
    return float(values[0])
