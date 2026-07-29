"""Yahoo Finance chart-API provider — keyless daily bars.

Uses the public chart endpoint (JSON, no API key). Prices come back both raw and
**adjusted** (splits + dividends); we keep both — `Close` (raw) and `AdjClose` —
because which one a backtest should use is a *decision* (total-return vs price
series; Curriculum I.6), not a default to hide.

Best-effort convenience provider: undocumented endpoint, can change. Fetch once →
snapshot → work offline (MASTER_SPEC P5), so a future endpoint change can never
touch an existing result.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["fetch_daily"]

_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
_HEADERS = {"User-Agent": "Mozilla/5.0 (quantropy research; fetch-once-to-snapshot)"}


def fetch_daily(symbols: list[str], timeout: float = 30.0) -> dict[str, pd.DataFrame]:
    """Full daily history per symbol. Network — requires the [data] extra.

    Returns ``{symbol: DataFrame[Open, High, Low, Close, AdjClose, Volume]}``
    indexed by date. Raises on empty/malformed responses rather than snapshotting
    garbage.
    """
    import time

    import requests  # deferred: core stays importable without the [data] extra

    out: dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        resp = requests.get(
            _URL.format(symbol=symbol),
            # period1/period2 epoch form, NOT range=max: with range=max yahoo
            # silently downgrades 1d to monthly bars (verified 2026-07) — the
            # granularity guard below makes that class of bug loud forever.
            params={
                "period1": "0",
                "period2": str(int(time.time())),
                "interval": "1d",
                "events": "div,split",
            },
            headers=_HEADERS,
            timeout=timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
        try:
            result = payload["chart"]["result"][0]
            ts = result["timestamp"]
            quote = result["indicators"]["quote"][0]
            adj = result["indicators"]["adjclose"][0]["adjclose"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"yahoo returned no usable data for {symbol!r}") from exc
        frame = pd.DataFrame(
            {
                "Open": quote["open"],
                "High": quote["high"],
                "Low": quote["low"],
                "Close": quote["close"],
                "AdjClose": adj,
                "Volume": quote["volume"],
            },
            index=pd.to_datetime(ts, unit="s").normalize(),
        )
        frame.index.name = "Date"
        frame = frame.dropna(subset=["Close"]).sort_index()
        if frame.empty:
            raise ValueError(f"yahoo returned an empty series for {symbol!r}")
        if len(frame) > 10:
            median_gap = frame.index.to_series().diff().median()
            if median_gap > pd.Timedelta(days=5):
                raise ValueError(
                    f"yahoo returned non-daily bars for {symbol!r} "
                    f"(median gap {median_gap}) — refusing to snapshot garbage"
                )
        out[symbol] = frame
    return out
