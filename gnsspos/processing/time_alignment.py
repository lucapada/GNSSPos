"""Time alignment and gap-filling for GNSS position series."""
from __future__ import annotations

import logging
from typing import Sequence

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

_POS_COLS = ["latitude_deg", "longitude_deg", "height_m"]
_COV_COLS = ["sdn_m", "sde_m", "sdu_m", "sdne_m", "sdeu_m", "sdun_m"]
_ZERO_COLS = [
    "age_s", "ratio",
    "vn_ms", "ve_ms", "vu_ms",
    "sdvn", "sdve", "sdvu", "sdvne", "sdveu", "sdvun",
]


def common_time_range(dfs: Sequence[pd.DataFrame]) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Return the intersection time window across all DataFrames.

    Parameters
    ----------
    dfs:
        Sequence of DataFrames with a UTC datetime index.

    Returns
    -------
    (t_start, t_end):
        t_start = max of all index minima.
        t_end   = min of all index maxima.

    Raises
    ------
    ValueError
        If the intersection window is empty (t_start >= t_end).
    """
    t_start = max(df.index.min() for df in dfs)
    t_end = min(df.index.max() for df in dfs)
    if t_start >= t_end:
        raise ValueError(
            f"No common time window: t_start={t_start}, t_end={t_end}."
        )
    return t_start, t_end


def _interp_epoch(df: pd.DataFrame, t: pd.Timestamp) -> pd.Series | None:
    """
    Linearly interpolate a single missing epoch *t* from its neighbours.

    Position columns: standard linear interpolation.
    Covariance columns: variance propagation W1^2*C1 + W2^2*C2.
    Q, ns: minimum of the two bounding epochs.
    Everything else: 0.0.

    Returns ``None`` if *t* has no valid bounding epochs.
    """
    idx = df.index
    before = idx[idx < t]
    after = idx[idx > t]
    if before.empty or after.empty:
        return None

    t1, t2 = before[-1], after[0]
    r1_raw, r2_raw = df.loc[t1], df.loc[t2]
    # If duplicate timestamps exist, loc returns a DataFrame; take the first row.
    r1 = r1_raw.iloc[0] if isinstance(r1_raw, pd.DataFrame) else r1_raw
    r2 = r2_raw.iloc[0] if isinstance(r2_raw, pd.DataFrame) else r2_raw

    total_dt = (t2 - t1).total_seconds()
    w2 = (t - t1).total_seconds() / total_dt
    w1 = 1.0 - w2

    row: dict = {}
    for col in _POS_COLS:
        row[col] = w1 * float(r1[col]) + w2 * float(r2[col])
    for col in _COV_COLS:
        row[col] = w1**2 * float(r1[col]) + w2**2 * float(r2[col])
    row["Q"] = min(int(r1["Q"]), int(r2["Q"]))
    row["ns"] = min(int(r1["ns"]), int(r2["ns"]))
    for col in _ZERO_COLS:
        row[col] = 0.0

    return pd.Series(row, name=t)


def fill_gaps(
    df: pd.DataFrame,
    freq: str = "1s",
    target_index: pd.DatetimeIndex | None = None,
) -> pd.DataFrame:
    """
    Resample a pos DataFrame to a regular *freq* grid and fill gaps.

    Existing epochs are kept as-is.  Missing epochs within the time span
    of *df* are filled by weighted linear interpolation (see
    :func:`_interp_epoch`).

    Parameters
    ----------
    df:
        DataFrame with a UTC datetime index.
    freq:
        Pandas offset string for the target frequency (default ``"1s"``).
    target_index:
        If provided, use this exact DatetimeIndex instead of computing one
        from df.index.min()/max().  Used by :func:`align_series` to ensure
        all series land on an identical grid.

    Returns
    -------
    pd.DataFrame
        DataFrame on a complete regular datetime grid.
    """
    # Round sub-second timestamps to the target frequency (e.g. NMEA at .17 s).
    df = df.copy()
    df.index = df.index.round(freq)

    # Collapse any duplicate timestamps that arise after rounding.
    if df.index.duplicated().any():
        df = df[~df.index.duplicated(keep="first")]

    full_index = target_index if target_index is not None else pd.date_range(df.index.min(), df.index.max(), freq=freq)
    missing = full_index.difference(df.index)

    if missing.empty:
        return df.reindex(full_index)

    new_rows: dict[pd.Timestamp, pd.Series] = {}
    for t in missing:
        row = _interp_epoch(df, t)
        if row is not None:
            new_rows[t] = row
        else:
            logger.debug("Cannot interpolate epoch %s (no surrounding valid data)", t)

    if new_rows:
        extra = pd.DataFrame(new_rows).T
        extra.index.name = "utc"
        df = pd.concat([df, extra]).sort_index()

    return df.reindex(full_index)


def align_series(dfs: Sequence[pd.DataFrame], freq: str = "1s") -> list[pd.DataFrame]:
    """
    Align multiple pos DataFrames to their common time window with gap-filling.

    Steps:

    1. Compute the intersection time window via :func:`common_time_range`.
    2. Clip each DataFrame to that window.
    3. Fill gaps in each clipped DataFrame using :func:`fill_gaps`.

    Parameters
    ----------
    dfs:
        Sequence of pos DataFrames (UTC datetime index).
    freq:
        Target sampling frequency (default ``"1s"``).

    Returns
    -------
    list[pd.DataFrame]
        List of DataFrames on the same regular datetime index.
    """
    t_start, t_end = common_time_range(dfs)
    # Floor/ceil to freq so the shared grid has integer-second boundaries.
    t_start = t_start.floor(freq)
    t_end   = t_end.floor(freq)
    logger.info("Common time window: %s → %s", t_start, t_end)

    # One shared index guarantees all outputs are bit-for-bit identical in time.
    shared_index = pd.date_range(t_start, t_end, freq=freq)

    aligned: list[pd.DataFrame] = []
    for df in dfs:
        clipped = df[(df.index >= t_start) & (df.index <= t_end)].copy()
        filled = fill_gaps(clipped, freq=freq, target_index=shared_index)
        aligned.append(filled)

    return aligned
