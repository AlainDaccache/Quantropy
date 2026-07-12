"""Fed GSW yield-curve provider — the free, canonical US Treasury curve.

Gürkaynak-Sack-Wright (2007, REFERENCES §12): the Fed Board publishes a daily
Svensson-fitted nominal curve back to 1961 — zero-coupon yields (SVENY01..30,
**continuously compounded, in percent**), par yields, forwards, and the fitted
NSS parameters (BETA0..3, TAU1, TAU2). This one free file makes the fixed-income
deep track executable: everything in `quantropy.pricing.curves` validates against
the Fed's own published numbers.

Fetch once → snapshot (the file is ~17MB; trim before committing fixtures).
"""

from __future__ import annotations

import io

import pandas as pd

__all__ = ["fetch_gsw", "parse_gsw", "GSW_URL"]

GSW_URL = "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"


def fetch_gsw(timeout: float = 120.0) -> pd.DataFrame:
    """Fetch and parse the full GSW dataset. Network — [data] extra."""
    import requests  # deferred

    resp = requests.get(GSW_URL, headers={"User-Agent": "Mozilla/5.0 (quantropy research)"},
                        timeout=timeout)
    resp.raise_for_status()
    return parse_gsw(resp.text)


def parse_gsw(text: str) -> pd.DataFrame:
    """Parse the GSW CSV: banner rows, then a Date-indexed numeric table.

    'NA' cells (fitting gaps, publication lag) become NaN; all-NA rows are
    dropped. Yields remain in PERCENT and continuous compounding — conversion is
    the pricing layer's explicit job, not a silent parser default.
    """
    lines = text.splitlines()
    header_row = next(i for i, line in enumerate(lines) if line.startswith("Date,"))
    frame = pd.read_csv(io.StringIO("\n".join(lines[header_row:])), na_values=["NA"])
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.set_index("Date").apply(pd.to_numeric, errors="coerce")
    return frame.dropna(how="all")
