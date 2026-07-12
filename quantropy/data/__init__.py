"""Data layer: instruments, snapshot-versioned storage, point-in-time integrity.

Design laws (MASTER_SPEC P3/P5): fetch-once-to-snapshot, then read offline; backtests
pin a snapshot id so a rerun months later returns the same result; fundamentals are
stored bitemporally (event date vs knowledge date) so backtests see only what was
knowable at the time.
"""

from quantropy.data.model import AssetClass, Instrument
from quantropy.data.pit import PointInTimeStore
from quantropy.data.store import SnapshotStore
from quantropy.data.universe import Universe

__all__ = ["AssetClass", "Instrument", "PointInTimeStore", "SnapshotStore", "Universe"]
