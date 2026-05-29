"""
Visualisation for GNSSPos experiments.

Plots produced:

1. ``plot_trajectory_map``   – 2-D trajectory overlaid on an OSM basemap.
2. ``plot_time_series``      – Three-panel time series: easting, northing, height.
3. ``plot_metrics``          – Five-panel accuracy metrics: RMS x/y/z, μ_d, σ_d.
4. ``plot_all_experiments``  – All experiments overlaid for quick comparison.
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import contextily as ctx

    _CTX_AVAILABLE = True
except ImportError:
    _CTX_AVAILABLE = False

logger = logging.getLogger(__name__)

_COLORS: list[str] = plt.rcParams["axes.prop_cycle"].by_key()["color"]


def _color(i: int) -> str:
    return _COLORS[i % len(_COLORS)]


def _save(fig: plt.Figure, path: str | Path | None) -> None:
    if path is not None:
        fig.savefig(path, dpi=150, bbox_inches="tight")
        logger.info("Saved figure → %s", path)


def _format_xaxis(ax: plt.Axes) -> None:
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")


def plot_trajectory_map(
    series: dict[str, pd.DataFrame],
    title: str = "Trajectory Map",
    save_path: str | Path | None = None,
) -> plt.Figure:
    """
    Plot 2-D trajectory on an OpenStreetMap basemap.

    Parameters
    ----------
    series:
        ``{label: df}`` where each *df* has columns ``x_wm`` and ``y_wm``
        (Web Mercator, EPSG:3857).
    title:
        Figure title.
    save_path:
        If given, the figure is saved to this path (PNG/PDF/SVG).

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    for i, (label, df) in enumerate(series.items()):
        c = _color(i)
        ax.plot(df["x_wm"], df["y_wm"], lw=1.5, label=label, color=c, alpha=0.85)
        ax.scatter(
            df["x_wm"].iloc[0], df["y_wm"].iloc[0],
            marker="o", s=60, color=c, zorder=5,
        )

    if _CTX_AVAILABLE:
        try:
            ctx.add_basemap(
                ax,
                source=ctx.providers.OpenStreetMap.Mapnik,
                crs="EPSG:3857",
            )
        except Exception as exc:
            logger.warning("Could not add OSM basemap: %s", exc)

    ax.set_xlabel("Easting – Web Mercator (m)")
    ax.set_ylabel("Northing – Web Mercator (m)")
    ax.set_title(title)
    ax.legend(fontsize=8)
    ax.grid(True, linestyle=":", alpha=0.5)
    fig.tight_layout()
    _save(fig, save_path)
    return fig


def plot_time_series(
    series: dict[str, pd.DataFrame],
    title: str = "Time Series",
    save_path: str | Path | None = None,
) -> plt.Figure:
    """
    Three-panel time-series plot: easting, northing, height.

    Parameters
    ----------
    series:
        ``{label: df}`` where each *df* has columns ``easting_m``,
        ``northing_m``, ``height_m`` and a UTC datetime index.
    title:
        Figure title (placed on the top panel).
    save_path:
        Optional output path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    cols = ["easting_m", "northing_m", "height_m"]
    ylabels = ["Easting (m)", "Northing (m)", "Height (m)"]

    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

    for i, (label, df) in enumerate(series.items()):
        c = _color(i)
        for ax, col in zip(axes, cols):
            ax.plot(df.index, df[col], lw=1.0, label=label, color=c, alpha=0.9)

    for ax, ylabel in zip(axes, ylabels):
        ax.set_ylabel(ylabel, fontsize=9)
        ax.legend(fontsize=7, loc="upper right")
        ax.grid(True, linestyle=":", alpha=0.5)

    _format_xaxis(axes[-1])
    axes[-1].set_xlabel("UTC")
    axes[0].set_title(title)
    fig.tight_layout()
    _save(fig, save_path)
    return fig


def plot_metrics(
    metrics: dict[str, dict[str, pd.Series]],
    title: str = "Accuracy Metrics",
    save_path: str | Path | None = None,
) -> plt.Figure:
    """
    Five-panel metrics plot: RMS-easting, RMS-northing, RMS-height, μ_d, σ_d.

    Parameters
    ----------
    metrics:
        ``{exp_label: metric_dict}`` where each *metric_dict* has keys
        ``rms_easting_m``, ``rms_northing_m``, ``rms_height_m``,
        ``mu_d``, ``sigma_d`` (as returned by
        :func:`~gnsspos.processing.metrics.compute_all_metrics`).
    title:
        Figure title.
    save_path:
        Optional output path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    keys = ["rms_easting_m", "rms_northing_m", "rms_height_m", "mu_d", "sigma_d"]
    ylabels = [
        "RMS Easting (m)",
        "RMS Northing (m)",
        "RMS Height (m)",
        "μ_d (m)",
        "σ_d (m)",
    ]

    fig, axes = plt.subplots(len(keys), 1, figsize=(14, 12), sharex=True)

    for i, (exp_label, m) in enumerate(metrics.items()):
        c = _color(i)
        for ax, key in zip(axes, keys):
            if key in m:
                s = m[key]
                ax.plot(s.index, s.values, lw=1.0, label=exp_label, color=c)

    for ax, ylabel in zip(axes, ylabels):
        ax.set_ylabel(ylabel, fontsize=9)
        ax.legend(fontsize=7, loc="upper right")
        ax.grid(True, linestyle=":", alpha=0.5)

    _format_xaxis(axes[-1])
    axes[-1].set_xlabel("UTC")
    axes[0].set_title(title)
    fig.tight_layout()
    _save(fig, save_path)
    return fig


def plot_all_experiments(
    series: dict[str, pd.DataFrame],
    reference_label: str,
    title: str = "All Experiments – Comparison",
    save_path: str | Path | None = None,
) -> plt.Figure:
    """
    Overlay all experiments on a single three-panel figure.

    The reference trajectory is drawn as a thick black dashed line; all
    other experiments use thin coloured lines.

    Parameters
    ----------
    series:
        ``{label: df}`` where each *df* has ``easting_m``, ``northing_m``,
        ``height_m`` and a UTC datetime index.
    reference_label:
        Key in *series* that identifies the reference trajectory.
    title:
        Figure title.
    save_path:
        Optional output path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    cols = ["easting_m", "northing_m", "height_m"]
    ylabels = ["Easting (m)", "Northing (m)", "Height (m)"]

    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

    color_idx = 0
    for label, df in series.items():
        if label == reference_label:
            style: dict = dict(lw=2.0, linestyle="--", color="black", zorder=5)
        else:
            style = dict(lw=0.9, color=_color(color_idx), alpha=0.85)
            color_idx += 1
        for ax, col in zip(axes, cols):
            ax.plot(df.index, df[col], label=label, **style)

    for ax, ylabel in zip(axes, ylabels):
        ax.set_ylabel(ylabel, fontsize=9)
        ax.legend(fontsize=7, loc="upper right")
        ax.grid(True, linestyle=":", alpha=0.5)

    _format_xaxis(axes[-1])
    axes[-1].set_xlabel("UTC")
    axes[0].set_title(title)
    fig.tight_layout()
    _save(fig, save_path)
    return fig
