"""Snapshot-versioned Parquet store.

The reproducibility law (MASTER_SPEC P5): a backtest pins a ``snapshot_id``; reading
that snapshot months later — after a vendor has silently backfilled history — returns
byte-identical data. Snapshots are immutable once written.

Layout::

    <root>/
      <snapshot_id>/
        manifest.json          # datasets, row counts, created-at, note
        <dataset>.parquet
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

__all__ = ["SnapshotStore"]

_MANIFEST = "manifest.json"


class SnapshotStore:
    """Immutable, snapshot-versioned Parquet storage under a root directory."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # -- write ---------------------------------------------------------------

    def write(
        self,
        snapshot_id: str,
        datasets: dict[str, pd.DataFrame],
        note: str = "",
    ) -> str:
        """Write an immutable snapshot. Fails if ``snapshot_id`` already exists."""
        if not snapshot_id or any(sep in snapshot_id for sep in ("/", "\\", "..")):
            raise ValueError(f"invalid snapshot_id: {snapshot_id!r}")
        if not datasets:
            raise ValueError("datasets must be non-empty")
        path = self.root / snapshot_id
        if path.exists():
            raise FileExistsError(
                f"snapshot {snapshot_id!r} already exists — snapshots are immutable; "
                "write a new id instead"
            )
        path.mkdir(parents=True)
        manifest = {
            "snapshot_id": snapshot_id,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "note": note,
            "datasets": {},
        }
        for name, frame in datasets.items():
            frame.to_parquet(path / f"{name}.parquet")
            manifest["datasets"][name] = {"rows": int(len(frame))}
        (path / _MANIFEST).write_text(json.dumps(manifest, indent=2))
        return snapshot_id

    # -- read ----------------------------------------------------------------

    def read(self, snapshot_id: str, dataset: str) -> pd.DataFrame:
        """Read one dataset from a pinned snapshot."""
        file = self.root / snapshot_id / f"{dataset}.parquet"
        if not file.exists():
            raise FileNotFoundError(f"no dataset {dataset!r} in snapshot {snapshot_id!r}")
        return pd.read_parquet(file)

    def manifest(self, snapshot_id: str) -> dict:
        file = self.root / snapshot_id / _MANIFEST
        if not file.exists():
            raise FileNotFoundError(f"no snapshot {snapshot_id!r}")
        return json.loads(file.read_text())

    def snapshots(self) -> list[str]:
        """All snapshot ids, sorted."""
        return sorted(p.name for p in self.root.iterdir() if (p / _MANIFEST).exists())
