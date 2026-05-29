"""Read RTKLIB .pos files (LLH/UTC format) into DataFrames."""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

POS_COLUMNS = [
    "latitude_deg", "longitude_deg", "height_m",
    "Q", "ns",
    "sdn_m", "sde_m", "sdu_m",
    "sdne_m", "sdeu_m", "sdun_m",
    "age_s", "ratio",
    "vn_ms", "ve_ms", "vu_ms",
    "sdvn", "sdve", "sdvu", "sdvne", "sdveu", "sdvun",
]

_INT_COLS = {"Q", "ns"}


def read_pos_file(path: str | Path) -> pd.DataFrame:
    """
    Parse a RTKLIB .pos file (LLH, UTC time-system) into a DataFrame.

    Lines beginning with '%' are skipped.  The date and time tokens in each
    data row are merged into a UTC ``datetime`` index named ``utc``.

    Parameters
    ----------
    path:
        Absolute or relative path to the .pos file.

    Returns
    -------
    pd.DataFrame
        Indexed by ``utc`` (UTC datetime64[ns]).  Columns match POS_COLUMNS.
        Rows with fewer than 7 tokens are silently dropped.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"pos file not found: {path}")

    rows: list[list[str]] = []
    with path.open("r") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("%"):
                continue
            tokens = line.split()
            # minimum: date + time + lat + lon + height + Q + ns = 7
            if len(tokens) < 7:
                continue
            rows.append(tokens)

    if not rows:
        logger.warning("No data rows found in %s", path)
        return pd.DataFrame(columns=["utc"] + POS_COLUMNS).set_index("utc")

    n_fixed = len(POS_COLUMNS)
    records: list[list] = []
    for tokens in rows:
        # tokens[0] = YYYY/MM/DD, tokens[1] = HH:MM:SS.sss, tokens[2:] = fields
        utc_str = tokens[0] + " " + tokens[1]
        data = tokens[2:]
        data = data[:n_fixed]
        while len(data) < n_fixed:
            data.append("0")
        records.append([utc_str] + data)

    df = pd.DataFrame(records, columns=["utc"] + POS_COLUMNS)
    df["utc"] = pd.to_datetime(df["utc"], format="%Y/%m/%d %H:%M:%S.%f")

    for col in POS_COLUMNS:
        if col in _INT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df.set_index("utc", inplace=True)
    df.index.name = "utc"
    logger.info("Loaded %d epochs from %s", len(df), path.name)
    return df
