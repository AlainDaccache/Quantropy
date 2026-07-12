"""Hypothesis registry & cumulative trials ledger (Curriculum VI.7).

The discipline: register the hypothesis BEFORE testing it, log every trial, and
feed the *cumulative* trials count into deflated Sharpe — deflation must reflect
everything ever tried, not this study alone (Bailey-López de Prado; the
Arnott-Harvey-Markowitz protocol; docs/REFERENCES.md §1).

Storage is an append-only JSON-lines file: human-readable, diffable, and it lives
in the repo — the ledger is *part of the research record*, not an afterthought.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

__all__ = ["TrialsLedger"]


class TrialsLedger:
    """Append-only research ledger: hypotheses and every trial run against them."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    # -- write (append-only) ----------------------------------------------------

    def register_hypothesis(self, name: str, rationale: str) -> str:
        """Pre-register a hypothesis (economic rationale REQUIRED — no rationale,
        no test; that's the protocol). Returns the hypothesis id."""
        if not name or not rationale:
            raise ValueError("both name and rationale are required — pre-registration "
                             "without an economic rationale is data mining with extra steps")
        hyp_id = f"H{self._count('hypothesis') + 1:03d}"
        self._append(
            {
                "kind": "hypothesis",
                "id": hyp_id,
                "name": name,
                "rationale": rationale,
                "registered_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        return hyp_id

    def log_trial(
        self,
        hypothesis: str,
        sharpe_per_period: float,
        n_obs: int,
        params: dict | None = None,
        note: str = "",
    ) -> None:
        """Log one backtest/configuration. EVERY variation counts as a trial —
        a parameter tweak you looked at is a trial whether or not you liked it."""
        if not self._exists(hypothesis):
            raise KeyError(f"unknown hypothesis {hypothesis!r} — register before testing")
        self._append(
            {
                "kind": "trial",
                "hypothesis": hypothesis,
                "sharpe_per_period": float(sharpe_per_period),
                "n_obs": int(n_obs),
                "params": params or {},
                "note": note,
                "logged_utc": datetime.now(timezone.utc).isoformat(),
            }
        )

    # -- read (feeds deflated_sharpe) --------------------------------------------

    def n_trials(self) -> int:
        """Cumulative trials across ALL hypotheses — the deflation input."""
        return self._count("trial")

    def trial_sharpe_variance(self) -> float:
        """Variance of per-period Sharpe across all logged trials.

        The second input to expected_max_sharpe(). Returns 0.0 with fewer than two
        trials (nothing to deflate against yet).
        """
        srs = [rec["sharpe_per_period"] for rec in self._records() if rec["kind"] == "trial"]
        if len(srs) < 2:
            return 0.0
        return float(np.var(srs, ddof=1))

    def hypotheses(self) -> list[dict]:
        return [r for r in self._records() if r["kind"] == "hypothesis"]

    def trials(self, hypothesis: str | None = None) -> list[dict]:
        out = [r for r in self._records() if r["kind"] == "trial"]
        if hypothesis is not None:
            out = [r for r in out if r["hypothesis"] == hypothesis]
        return out

    # -- internals ----------------------------------------------------------------

    def _records(self) -> list[dict]:
        text = self.path.read_text().strip()
        return [json.loads(line) for line in text.splitlines()] if text else []

    def _append(self, record: dict) -> None:
        with self.path.open("a") as fh:
            fh.write(json.dumps(record) + "\n")

    def _count(self, kind: str) -> int:
        return sum(1 for r in self._records() if r["kind"] == kind)

    def _exists(self, hyp_id: str) -> bool:
        return any(r["kind"] == "hypothesis" and r["id"] == hyp_id for r in self._records())
