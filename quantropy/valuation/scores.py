"""Distress, quality, and manipulation scores (Curriculum IV.5; REFERENCES §6).

Primary-source formulas: Altman (1968) Z, Piotroski (2000) F, Beneish (1999) M.
Computed here as fundamentals; *used* as cross-sectional signals in Part VI (the
one-home rule: computed once, consumed elsewhere). Missing inputs -> NaN, and the
F-score reports how many of its nine tests were computable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from quantropy.valuation.statements import StatementSet

__all__ = ["altman_z", "piotroski_f", "beneish_m"]


def altman_z(s: StatementSet, market_cap: float) -> float:
    """Altman (1968) Z-score, original public-manufacturer coefficients.

    Z = 1.2·WC/TA + 1.4·RE/TA + 3.3·EBIT/TA + 0.6·MVE/TL + 1.0·Sales/TA.
    Distress < 1.81 < grey < 2.99 < safe. NaN if any input is missing.
    """
    ta = s.total_assets
    x1 = (s.current_assets - s.current_liabilities) / ta
    x2 = s.retained_earnings / ta
    x3 = s.ebit / ta
    x4 = market_cap / s.total_liabilities
    x5 = s.revenue / ta
    return 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5


@dataclass(frozen=True, slots=True)
class FScore:
    score: int
    max_computable: int  # of 9 — honesty about missing inputs

    def __int__(self) -> int:
        return self.score


def piotroski_f(current: StatementSet, prior: StatementSet) -> FScore:
    """Piotroski (2000) F-score: nine binary quality signals across two periods.

    Profitability: ROA>0, CFO>0, ΔROA>0, accruals (CFO>NI).
    Leverage/liquidity: Δleverage<0 (LTD/TA), Δcurrent-ratio>0, no dilution
    (Δshares<=0). Efficiency: Δgross-margin>0, Δasset-turnover>0.
    """
    checks: list[bool | None] = []

    def _ratio(a: float, b: float) -> float:
        return a / b if b and not math.isnan(a) and not math.isnan(b) else float("nan")

    roa_now = _ratio(current.net_income, current.total_assets)
    roa_prev = _ratio(prior.net_income, prior.total_assets)
    pairs = [
        roa_now > 0 if not math.isnan(roa_now) else None,
        current.cash_from_operations > 0 if not math.isnan(current.cash_from_operations) else None,
        roa_now > roa_prev if not (math.isnan(roa_now) or math.isnan(roa_prev)) else None,
        (current.cash_from_operations > current.net_income)
        if not (math.isnan(current.cash_from_operations) or math.isnan(current.net_income))
        else None,
        (_ratio(current.long_term_debt, current.total_assets)
         < _ratio(prior.long_term_debt, prior.total_assets))
        if not math.isnan(_ratio(current.long_term_debt, current.total_assets))
        and not math.isnan(_ratio(prior.long_term_debt, prior.total_assets))
        else None,
        (_ratio(current.current_assets, current.current_liabilities)
         > _ratio(prior.current_assets, prior.current_liabilities))
        if not math.isnan(_ratio(current.current_assets, current.current_liabilities))
        and not math.isnan(_ratio(prior.current_assets, prior.current_liabilities))
        else None,
        (current.shares_outstanding <= prior.shares_outstanding)
        if not (math.isnan(current.shares_outstanding) or math.isnan(prior.shares_outstanding))
        else None,
        (_ratio(current.gross_profit, current.revenue)
         > _ratio(prior.gross_profit, prior.revenue))
        if not math.isnan(_ratio(current.gross_profit, current.revenue))
        and not math.isnan(_ratio(prior.gross_profit, prior.revenue))
        else None,
        (_ratio(current.revenue, current.total_assets)
         > _ratio(prior.revenue, prior.total_assets))
        if not math.isnan(_ratio(current.revenue, current.total_assets))
        and not math.isnan(_ratio(prior.revenue, prior.total_assets))
        else None,
    ]
    checks.extend(pairs)
    computable = [c for c in checks if c is not None]
    return FScore(score=sum(bool(c) for c in computable), max_computable=len(computable))


def beneish_m(
    dsri: float, gmi: float, aqi: float, sgi: float,
    depi: float, sgai: float, tata: float, lvgi: float,
) -> float:
    """Beneish (1999) M-score from its eight pre-computed indices.

    M = -4.84 + 0.92·DSRI + 0.528·GMI + 0.404·AQI + 0.892·SGI + 0.115·DEPI
        - 0.172·SGAI + 4.679·TATA - 0.327·LVGI.
    M > -1.78 flags likely manipulation. Index construction needs line items
    beyond StatementSet's core set, so inputs are explicit here (Curriculum IV.5
    covers building them; a manipulation-free firm scores ~ -2.4 to -2.6).
    """
    return (
        -4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi
        + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi
    )
