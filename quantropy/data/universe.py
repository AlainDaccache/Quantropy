"""Survivorship-aware universe: point-in-time membership.

A universe is a set of (symbol, start, end) membership spans. ``members(date)``
returns who was in the universe *on that date* — including names that later delisted
or were removed. Backtesting on today's members is survivorship bias, one of the
classic silent backtest inflators (docs/REFERENCES.md §1).

The mechanism is complete; *sourcing* true historical index membership is a data
problem handled per-provider (free sources are limited — documented honestly where
used).
"""

from __future__ import annotations

import pandas as pd

__all__ = ["Universe"]

_COLUMNS = ["symbol", "start", "end"]


class Universe:
    """Point-in-time membership table.

    ``spans`` — DataFrame with columns ``symbol, start, end``; ``end`` is NaT for
    current members. Overlapping spans for one symbol are allowed (re-inclusion).
    """

    def __init__(self, spans: pd.DataFrame):
        missing = set(_COLUMNS) - set(spans.columns)
        if missing:
            raise ValueError(f"spans missing columns: {sorted(missing)}")
        spans = spans[_COLUMNS].copy()
        spans["start"] = pd.to_datetime(spans["start"])
        spans["end"] = pd.to_datetime(spans["end"])
        ended = spans["end"].notna()
        if (spans.loc[ended, "end"] < spans.loc[ended, "start"]).any():
            raise ValueError("membership span ends before it starts")
        self._spans = spans

    def members(self, date: str | pd.Timestamp) -> list[str]:
        """Symbols in the universe on ``date`` (survivorship-free by construction)."""
        date = pd.Timestamp(date)
        live = (self._spans["start"] <= date) & (
            self._spans["end"].isna() | (self._spans["end"] >= date)
        )
        return sorted(self._spans.loc[live, "symbol"].unique())

    def all_symbols(self) -> list[str]:
        """Every symbol ever a member — the set a survivorship-free backtest must load."""
        return sorted(self._spans["symbol"].unique())

    def to_frame(self) -> pd.DataFrame:
        return self._spans.copy()

    @classmethod
    def from_frame(cls, frame: pd.DataFrame) -> "Universe":
        return cls(frame)

    def __len__(self) -> int:
        return len(self._spans)
