"""The ratio system with the DuPont decomposition (Curriculum IV.1).

Pure functions of a StatementSet; missing inputs produce NaN, never a silent
default. The DuPont identity — ROE = net margin × asset turnover × leverage —
is enforced by test, not asserted in prose.
"""

from __future__ import annotations

from dataclasses import dataclass

from quantropy.valuation.statements import StatementSet

__all__ = ["RatioReport", "ratios"]


def _div(a: float, b: float) -> float:
    try:
        return a / b if b not in (0.0,) else float("nan")
    except TypeError:
        return float("nan")


@dataclass(frozen=True, slots=True)
class RatioReport:
    # profitability
    gross_margin: float
    operating_margin: float
    net_margin: float
    roa: float
    roe: float
    # DuPont components (three-way)
    asset_turnover: float
    leverage: float  # assets / equity
    # liquidity & solvency
    current_ratio: float
    debt_to_equity: float
    # cash quality
    accruals_ratio: float  # (NI - CFO) / assets — Sloan's red flag direction: high = bad

    @property
    def dupont_roe(self) -> float:
        """ROE rebuilt from the decomposition — must equal roe (identity test)."""
        return self.net_margin * self.asset_turnover * self.leverage


def ratios(s: StatementSet) -> RatioReport:
    return RatioReport(
        gross_margin=_div(s.gross_profit, s.revenue),
        operating_margin=_div(s.operating_income, s.revenue),
        net_margin=_div(s.net_income, s.revenue),
        roa=_div(s.net_income, s.total_assets),
        roe=_div(s.net_income, s.equity),
        asset_turnover=_div(s.revenue, s.total_assets),
        leverage=_div(s.total_assets, s.equity),
        current_ratio=_div(s.current_assets, s.current_liabilities),
        debt_to_equity=_div(s.total_liabilities, s.equity),
        accruals_ratio=_div(s.net_income - s.cash_from_operations, s.total_assets),
    )
