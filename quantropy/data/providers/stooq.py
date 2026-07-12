"""Stooq daily-bar provider — keyless, free, long history.

Stooq serves daily OHLCV as plain CSV with no API key
(``https://stooq.com/q/d/l/?s=aapl.us&i=d``). Good enough for reproducible research
on liquid US equities/ETFs; its limits (adjusted-close methodology, occasional gaps,
no delisted names) are exactly the kind of data caveat the curriculum teaches
honestly. US symbols take a ``.us`` suffix.

Usage — fetch once, snapshot, then work offline::

    frames = fetch_daily(["SPY", "AAPL"])
    store.write("2026-07-12-us-etf", frames, note="stooq daily")
"""

from __future__ import annotations

import io

import pandas as pd

__all__ = ["fetch_daily", "stooq_symbol"]

_BASE = "https://stooq.com/q/d/l/"


def stooq_symbol(symbol: str) -> str:
    """Map a plain US ticker to stooq's convention (``AAPL`` -> ``aapl.us``)."""
    s = symbol.lower()
    return s if "." in s else f"{s}.us"


def fetch_daily(symbols: list[str], timeout: float = 30.0) -> dict[str, pd.DataFrame]:
    """Fetch full daily OHLCV history per symbol. Network — requires the [data] extra.

    Returns ``{symbol: DataFrame[Open, High, Low, Close, Volume]}`` indexed by date.
    Raises on symbols that return no data (a silent empty frame would poison a
    snapshot).
    """
    import requests  # deferred: core stays importable without the [data] extra

    out: dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        resp = requests.get(
            _BASE, params={"s": stooq_symbol(symbol), "i": "d"}, timeout=timeout
        )
        resp.raise_for_status()
        frame = pd.read_csv(io.StringIO(resp.text))
        if "Close" not in frame.columns or frame.empty:
            raise ValueError(f"stooq returned no data for {symbol!r}")
        frame["Date"] = pd.to_datetime(frame["Date"])
        out[symbol] = frame.set_index("Date").sort_index()
    return out
