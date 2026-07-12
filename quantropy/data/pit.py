"""Point-in-time (bitemporal) store.

Every observation carries two dates:

- ``event_date``     — the period the value describes (e.g. fiscal Q4 2023),
- ``knowledge_date`` — when the market could first know it (filing/publication date).

An ``as_of(date)`` query returns, per (entity, field, event_date), the **latest value
whose knowledge_date <= date**. Restatements simply append a new row with a later
knowledge_date — history is never overwritten, and a backtest run "as of" any day sees
exactly what was knowable that day (MASTER_SPEC P3: the feature contract's data half).

This is the difference between backtesting on *as-reported* vs *restated* fundamentals
— one of the classic silent look-aheads (see docs/REFERENCES.md §1).
"""

from __future__ import annotations

import pandas as pd

__all__ = ["PointInTimeStore"]

_COLUMNS = ["entity", "field", "event_date", "knowledge_date", "value"]


class PointInTimeStore:
    """Append-only bitemporal store over a pandas DataFrame.

    Construct empty, or from a records frame with columns
    ``entity, field, event_date, knowledge_date, value``.
    """

    def __init__(self, records: pd.DataFrame | None = None):
        if records is None:
            records = pd.DataFrame(columns=_COLUMNS)
        missing = set(_COLUMNS) - set(records.columns)
        if missing:
            raise ValueError(f"records missing columns: {sorted(missing)}")
        records = records[_COLUMNS].copy()
        records["event_date"] = pd.to_datetime(records["event_date"])
        records["knowledge_date"] = pd.to_datetime(records["knowledge_date"])
        if (records["knowledge_date"] < records["event_date"]).any():
            raise ValueError(
                "knowledge_date precedes event_date — a value cannot be known "
                "before the period it describes ends"
            )
        self._records = records

    # -- write (append-only) --------------------------------------------------

    def record(
        self,
        entity: str,
        field: str,
        event_date: str | pd.Timestamp,
        knowledge_date: str | pd.Timestamp,
        value: float,
    ) -> None:
        """Append one observation (an initial report or a restatement)."""
        row = PointInTimeStore(
            pd.DataFrame([[entity, field, event_date, knowledge_date, value]], columns=_COLUMNS)
        )._records
        # append-only, insertion order preserved: a same-day correction (equal
        # knowledge_date) supersedes what it corrects via the stable sort in as_of().
        # (Empty case handled separately — concat with empty frames is deprecated.)
        if self._records.empty:
            self._records = row
        else:
            self._records = pd.concat([self._records, row], ignore_index=True)

    # -- read -----------------------------------------------------------------

    def as_of(self, date: str | pd.Timestamp) -> pd.DataFrame:
        """The world as knowable on ``date``.

        Returns one row per (entity, field, event_date): the value with the latest
        knowledge_date <= date. Later restatements are invisible; not-yet-published
        periods are absent.
        """
        date = pd.Timestamp(date)
        known = self._records[self._records["knowledge_date"] <= date]
        if known.empty:
            return known.copy()
        latest = (
            known.sort_values("knowledge_date", kind="stable")
            .groupby(["entity", "field", "event_date"], as_index=False)
            .last()
        )
        return latest[_COLUMNS].reset_index(drop=True)

    def latest(self) -> pd.DataFrame:
        """Current view (all restatements applied) — the *wrong* frame to backtest on."""
        return self.as_of(self._records["knowledge_date"].max())

    # -- persistence ----------------------------------------------------------

    def to_frame(self) -> pd.DataFrame:
        """Full append-only history, for persistence via SnapshotStore."""
        return self._records.copy()

    @classmethod
    def from_frame(cls, frame: pd.DataFrame) -> "PointInTimeStore":
        return cls(frame)

    def __len__(self) -> int:
        return len(self._records)
