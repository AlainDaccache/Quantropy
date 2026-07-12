"""StatementSet: the as-reported line items one period of analysis needs.

A deliberately small, explicit container (P10): the fields the ratio system and
the scores actually consume — not a full XBRL mirror. Values are as-reported
(PIT discipline); `from_pit_view` builds one from a PointInTimeStore.as_of() frame,
handling **concept drift** (the same economic item lives under different XBRL tags
across filers and eras — Curriculum I.5's wart, handled with fallback lists).
"""

from __future__ import annotations

from dataclasses import dataclass, fields

import pandas as pd

__all__ = ["StatementSet", "CONCEPT_MAP"]

#: economic item -> XBRL concept fallbacks, in priority order
CONCEPT_MAP: dict[str, list[str]] = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ],
    "net_income": ["NetIncomeLoss"],
    "total_assets": ["Assets"],
    "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "current_assets": ["AssetsCurrent"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "total_liabilities": ["Liabilities"],
    "cash_from_operations": ["NetCashProvidedByUsedInOperatingActivities"],
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "retained_earnings": ["RetainedEarningsAccumulatedDeficit"],
    "ebit": ["OperatingIncomeLoss"],  # teaching proxy; document the approximation
    "receivables": ["AccountsReceivableNetCurrent"],
    "shares_outstanding": ["CommonStockSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"],
}


@dataclass(frozen=True, slots=True)
class StatementSet:
    """As-reported line items for one entity, one fiscal period. NaN = not filed."""

    entity: str
    period_end: pd.Timestamp
    revenue: float = float("nan")
    net_income: float = float("nan")
    total_assets: float = float("nan")
    equity: float = float("nan")
    current_assets: float = float("nan")
    current_liabilities: float = float("nan")
    total_liabilities: float = float("nan")
    cash_from_operations: float = float("nan")
    long_term_debt: float = float("nan")
    gross_profit: float = float("nan")
    operating_income: float = float("nan")
    retained_earnings: float = float("nan")
    ebit: float = float("nan")
    receivables: float = float("nan")
    shares_outstanding: float = float("nan")

    @classmethod
    def from_pit_view(
        cls, view: pd.DataFrame, entity: str, period_end: str | pd.Timestamp
    ) -> "StatementSet":
        """Build from a PointInTimeStore.as_of() frame — i.e. only what was knowable.

        ``view`` columns: entity, field, event_date, knowledge_date, value. Concept
        drift handled via CONCEPT_MAP fallbacks; absent items stay NaN (ratios and
        scores degrade explicitly, never silently).
        """
        period_end = pd.Timestamp(period_end)
        rows = view[(view["entity"] == entity) & (view["event_date"] == period_end)]
        by_field = dict(zip(rows["field"], rows["value"]))
        values: dict[str, float] = {}
        for item, concepts in CONCEPT_MAP.items():
            for concept in concepts:
                if concept in by_field:
                    values[item] = float(by_field[concept])
                    break
        valid = {f.name for f in fields(cls)}
        return cls(entity=entity, period_end=period_end,
                   **{k: v for k, v in values.items() if k in valid})
