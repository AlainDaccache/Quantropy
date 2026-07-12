"""Ken French Data Library provider — the canonical free factor data. Keyless.

The library (mba.tuck.dartmouth.edu/pages/faculty/ken.french/) serves zipped CSVs
whose format is famous and famously awkward: banner text, a monthly block with
YYYYMM row labels, then annual blocks. We parse the **first monthly block** only,
convert percent → decimal, and mark the -99.99/-999 missing codes as NaN.

Its documentation implicitly defines the field's sorting conventions (NYSE
breakpoints, 2×3 sorts — REFERENCES §11); reproducing its published numbers is the
validation standard for our cross-sectional toolkit. Fetch once → snapshot.
"""

from __future__ import annotations

import io
import re
import zipfile

import pandas as pd

__all__ = ["fetch_dataset", "FF3_FACTORS", "PORTFOLIOS_5X5"]

_BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/{name}_CSV.zip"

FF3_FACTORS = "F-F_Research_Data_Factors"
PORTFOLIOS_5X5 = "25_Portfolios_5x5"

_MISSING = (-99.99, -999.0)


def fetch_dataset(name: str, timeout: float = 60.0) -> pd.DataFrame:
    """Fetch a French-library dataset and return its first monthly block.

    Returns a DataFrame indexed by month-end Timestamp, values as **decimal**
    returns (the library publishes percents). Network — [data] extra.
    """
    import requests  # deferred

    resp = requests.get(
        _BASE.format(name=name),
        headers={"User-Agent": "Mozilla/5.0 (quantropy research)"},
        timeout=timeout,
    )
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        csv_name = zf.namelist()[0]
        text = zf.read(csv_name).decode("utf-8", errors="replace")
    return parse_french_csv(text)


def parse_french_csv(text: str) -> pd.DataFrame:
    """Parse the first monthly (YYYYMM-indexed) block of a French-library CSV."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^\s*\d{6}\s*,", line):
            start = i
            break
    if start is None:
        raise ValueError("no monthly (YYYYMM) block found — not a French-library CSV?")
    header = lines[start - 1]
    block = [header]
    for line in lines[start:]:
        if re.match(r"^\s*\d{6}\s*,", line):
            block.append(line)
        else:
            break  # first non-monthly row ends the block (annual section follows)
    frame = pd.read_csv(io.StringIO("\n".join(block)), index_col=0, skipinitialspace=True)
    frame.index = pd.to_datetime(frame.index.astype(str), format="%Y%m") + pd.offsets.MonthEnd(0)
    frame.index.name = "Date"
    frame.columns = [c.strip() for c in frame.columns]
    frame = frame.apply(pd.to_numeric, errors="coerce")
    for code in _MISSING:
        frame = frame.mask(frame == code)
    return frame / 100.0  # percent -> decimal
