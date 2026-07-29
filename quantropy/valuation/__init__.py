"""Valuation: statements → ratios → DCF / market-implied expectations → scores.

The fundamentals arm (ARCHITECTURE §2.2, Curriculum Part IV). Everything here is a
pure function of as-reported inputs; the PIT store (Part I) guarantees a backtest
only ever sees what was knowable. Reference-tested against real filing figures.
"""

from quantropy.valuation.dcf import dcf_value, implied_growth
from quantropy.valuation.ratios import RatioReport, ratios
from quantropy.valuation.scores import altman_z, beneish_m, piotroski_f
from quantropy.valuation.statements import StatementSet

__all__ = [
    "StatementSet",
    "ratios",
    "RatioReport",
    "dcf_value",
    "implied_growth",
    "altman_z",
    "piotroski_f",
    "beneish_m",
]
