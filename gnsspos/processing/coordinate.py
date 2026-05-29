"""Coordinate transformations: WGS84 LLH ↔ UTM Zone 32N ↔ Web Mercator."""
from __future__ import annotations

import numpy as np
import pandas as pd
from pyproj import Transformer

_llh_to_utm32 = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)
_utm32_to_wm = Transformer.from_crs("EPSG:32632", "EPSG:3857", always_xy=True)
_llh_to_wm = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)


def llh_to_utm32(
    lat_deg: np.ndarray | float,
    lon_deg: np.ndarray | float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert WGS84 geodetic coordinates to UTM Zone 32N (EPSG:32632).

    Parameters
    ----------
    lat_deg:
        Geodetic latitude(s) in decimal degrees.
    lon_deg:
        Geodetic longitude(s) in decimal degrees.

    Returns
    -------
    (easting_m, northing_m):
        Arrays of easting and northing coordinates in metres.
    """
    return _llh_to_utm32.transform(lon_deg, lat_deg)


def utm32_to_web_mercator(
    easting: np.ndarray | float,
    northing: np.ndarray | float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert UTM Zone 32N coordinates to Web Mercator (EPSG:3857).

    Returns
    -------
    (x_wm, y_wm):
        Web Mercator coordinates in metres.
    """
    return _utm32_to_wm.transform(easting, northing)


def llh_to_web_mercator(
    lat_deg: np.ndarray | float,
    lon_deg: np.ndarray | float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert WGS84 geodetic coordinates directly to Web Mercator (EPSG:3857).

    Returns
    -------
    (x_wm, y_wm):
        Web Mercator coordinates in metres.
    """
    return _llh_to_wm.transform(lon_deg, lat_deg)


def add_utm32_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ``easting_m`` and ``northing_m`` (UTM Zone 32N) columns to a pos DataFrame.

    Reads ``latitude_deg`` and ``longitude_deg`` from *df* and returns a new
    DataFrame with two additional columns.

    Parameters
    ----------
    df:
        DataFrame with at least ``latitude_deg`` and ``longitude_deg`` columns.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with added ``easting_m`` and ``northing_m`` columns.
    """
    e, n = llh_to_utm32(df["latitude_deg"].values, df["longitude_deg"].values)
    df = df.copy()
    df["easting_m"] = e
    df["northing_m"] = n
    return df


def add_web_mercator_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ``x_wm`` and ``y_wm`` (Web Mercator, EPSG:3857) columns to a pos DataFrame.

    Parameters
    ----------
    df:
        DataFrame with at least ``latitude_deg`` and ``longitude_deg`` columns.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with added ``x_wm`` and ``y_wm`` columns.
    """
    x, y = llh_to_web_mercator(df["latitude_deg"].values, df["longitude_deg"].values)
    df = df.copy()
    df["x_wm"] = x
    df["y_wm"] = y
    return df
