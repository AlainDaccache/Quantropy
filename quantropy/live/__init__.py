"""Live trading: the IBKR venue behind the same seam the backtest uses.

Requires the ``[live]`` extra (``ib_async``) and a running TWS/IB Gateway with the
API enabled (paper: port 7497). Connection settings come from the environment
(.env — see .env.example), never from code.
"""

from quantropy.live.ibkr import IBKRVenue

__all__ = ["IBKRVenue"]
