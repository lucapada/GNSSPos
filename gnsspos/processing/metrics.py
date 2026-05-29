"""
GNSS accuracy metrics relative to a reference trajectory.

All metrics are computed in UTM Zone 32N:
  x = easting_m,  y = northing_m,  z = height_m.

Both *experiment* and *reference* DataFrames must share the same time index
before calling these functions — use
:func:`~gnsspos.processing.time_alignment.align_series` first.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _check_alignment(exp: pd.DataFrame, ref: pd.DataFrame) -> None:
    if not exp.index.equals(ref.index):
        raise ValueError(
            "Experiment and reference time indices do not match. "
            "Call time_alignment.align_series() first."
        )


def _residuals(exp: pd.DataFrame, ref: pd.DataFrame, col: str) -> np.ndarray:
    return (exp[col] - ref[col]).to_numpy(dtype=float)


def compute_rms(exp: pd.DataFrame, ref: pd.DataFrame, col: str) -> pd.Series:
    """
    Cumulative RMS of position residuals for *col* at each epoch.

    RMS(col, t_i) = sqrt( (1/i) * sum_{k=1}^{i} (exp_k - ref_k)^2 )

    Parameters
    ----------
    exp:
        Experiment DataFrame (must share the index of *ref*).
    ref:
        Reference DataFrame.
    col:
        Column name, e.g. ``"easting_m"``.

    Returns
    -------
    pd.Series
        Cumulative RMS indexed by UTC datetime.
    """
    _check_alignment(exp, ref)
    res = _residuals(exp, ref, col)
    n = np.arange(1, len(res) + 1)
    rms = np.sqrt(np.cumsum(res**2) / n)
    return pd.Series(rms, index=exp.index, name=f"rms_{col}")


def compute_3d_distances(exp: pd.DataFrame, ref: pd.DataFrame) -> np.ndarray:
    """
    Per-epoch 3-D Euclidean distance between *exp* and *ref*.

    d_i = sqrt(dx_i^2 + dy_i^2 + dz_i^2)
    where dx = easting_m residual, dy = northing_m residual, dz = height_m residual.
    """
    _check_alignment(exp, ref)
    dx = _residuals(exp, ref, "easting_m")
    dy = _residuals(exp, ref, "northing_m")
    dz = _residuals(exp, ref, "height_m")
    return np.sqrt(dx**2 + dy**2 + dz**2)


def compute_mean_3d_distance(exp: pd.DataFrame, ref: pd.DataFrame) -> pd.Series:
    """
    Cumulative mean 3-D distance μ_d at each epoch.

    μ_d(t_i) = (1/i) * sum_{k=1}^{i} d_k

    Returns
    -------
    pd.Series
        Cumulative mean 3-D distance, indexed by UTC datetime.
    """
    d = compute_3d_distances(exp, ref)
    n = np.arange(1, len(d) + 1)
    mu = np.cumsum(d) / n
    return pd.Series(mu, index=exp.index, name="mu_d")


def compute_sigma_d(exp: pd.DataFrame, ref: pd.DataFrame) -> pd.Series:
    """
    Cumulative standard deviation of 3-D distances σ_d at each epoch.

    Uses the running mean μ_d(t_i) at each step:

    σ_d(t_i) = sqrt( (1/i) * sum_{k=1}^{i} (d_k - μ_d(t_k))^2 )

    Returns
    -------
    pd.Series
        Cumulative σ_d, indexed by UTC datetime.
    """
    d = compute_3d_distances(exp, ref)
    n = np.arange(1, len(d) + 1)
    mu = np.cumsum(d) / n
    # squared deviation from running mean at each epoch
    sq_dev = (d - mu) ** 2
    sigma = np.sqrt(np.cumsum(sq_dev) / n)
    return pd.Series(sigma, index=exp.index, name="sigma_d")


def compute_all_metrics(
    exp: pd.DataFrame,
    ref: pd.DataFrame,
) -> dict[str, pd.Series]:
    """
    Compute the full set of accuracy metrics for one experiment vs reference.

    Parameters
    ----------
    exp:
        Experiment DataFrame with ``easting_m``, ``northing_m``, ``height_m``.
    ref:
        Reference DataFrame on the same time index.

    Returns
    -------
    dict
        Keys: ``rms_easting_m``, ``rms_northing_m``, ``rms_height_m``,
        ``mu_d``, ``sigma_d``.  Values are :class:`pd.Series` indexed by
        UTC datetime.
    """
    return {
        "rms_easting_m": compute_rms(exp, ref, "easting_m"),
        "rms_northing_m": compute_rms(exp, ref, "northing_m"),
        "rms_height_m": compute_rms(exp, ref, "height_m"),
        "mu_d": compute_mean_3d_distance(exp, ref),
        "sigma_d": compute_sigma_d(exp, ref),
    }
