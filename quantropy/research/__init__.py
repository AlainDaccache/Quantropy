"""Research: signals under the causal feature contract (MASTER_SPEC P3).

A Signal is a pure function of *history up to the decision date* — the engine
guarantees it never sees a bar past t, and fills happen at t+1 (no look-ahead,
enforced by tests, not intentions).
"""

from quantropy.research.signals import MovingAverageCross, Signal

__all__ = ["Signal", "MovingAverageCross"]
