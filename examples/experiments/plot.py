#!/usr/bin/env python3
"""
GNSSPos – Master comparison plot script.

Loads all available experiment outputs, aligns them to a common time window,
computes accuracy metrics vs the NMEA baseline (Experiment 0), and generates
the following figures:

  1. Trajectory map (all experiments, OSM basemap)
  2. Time-series comparison (easting, northing, height)
  3. Accuracy metrics vs baseline (RMS-x/y/z, μ_d, σ_d)
  4. All-experiments overlay

Output figures are saved to ``figures/`` alongside this script.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent   # examples/experiments/
_ROOT = _HERE.parents[1]                  # GNSSPos/
sys.path.insert(0, str(_ROOT))

import pandas as pd

from gnsspos.processing.pos_reader import read_pos_file
from gnsspos.processing.nmea_parser import parse_nmea_gga
from gnsspos.processing.coordinate import add_utm32_columns, add_web_mercator_columns
from gnsspos.processing.time_alignment import align_series
from gnsspos.processing.metrics import compute_all_metrics
from gnsspos.processing import plotter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

_FIGURES = _HERE / "figures"
_RAW     = _ROOT / "examples" / "raw_data" / "GPS_Sassuolo_Forli"

# ---------------------------------------------------------------------------
# Source definitions:  label → path
# Each entry is either a .pos file (RTKLIB) or a NMEA file (experiment 0).
# ---------------------------------------------------------------------------
_SOURCES: dict[str, Path] = {
    # Experiment 0 is saved as a pickle (pandas CSV format, not RTKLIB .pos)
    "Exp 0 – NMEA COM23":      _HERE / "experiment_0" / "outputs" / "COM23_nmea.pkl",
    "Exp A – Leica 1200":      _HERE / "experiment_a" / "outputs" / "45601780.pos",
    "Exp B – COM23 single":    _HERE / "experiment_b" / "outputs" / "COM23_rover.pos",
    "Exp B – COM24 single":    _HERE / "experiment_b" / "outputs" / "COM24_rover.pos",
    "Exp B – COM25 single":    _HERE / "experiment_b" / "outputs" / "COM25_rover.pos",
    "Exp C – COM23 kinematic": _HERE / "experiment_c" / "outputs" / "COM23_rover.pos",
    "Exp C – COM24 kinematic": _HERE / "experiment_c" / "outputs" / "COM24_rover.pos",
    "Exp C – COM25 kinematic": _HERE / "experiment_c" / "outputs" / "COM25_rover.pos",
    "Exp D – Combined":        _HERE / "experiment_d" / "outputs" / "combined.pkl",
    "Exp E – Kalman fusion":   _HERE / "experiment_e" / "outputs" / "combined_kf.pkl",
}

# ---------------------------------------------------------------------------
# Experiment selection.
# Comment out any key to exclude it from all plots and metrics.
# _SOURCES entries not listed here are silently ignored.
# ---------------------------------------------------------------------------
_ACTIVE_EXPERIMENTS: set[str] = {
    "Exp 0 – NMEA COM23",
    # "Exp A – Leica 1200",      # short coverage (~30 s), no temporal overlap
    # "Exp B – COM23 single",
    # "Exp B – COM24 single",
    # "Exp B – COM25 single",
    "Exp C – COM23 kinematic",
    "Exp C – COM24 kinematic",
    "Exp C – COM25 kinematic",
    "Exp D – Combined",
    "Exp E – Kalman fusion",
}

# Reference label used for metrics comparison and overlay highlighting.
# Must be a key present in _ACTIVE_EXPERIMENTS.
# Switch to "Exp A – Leica 1200" once Experiment A data is validated.
_REFERENCE_LABEL = "Exp 0 – NMEA COM23"


def _load_all() -> dict[str, pd.DataFrame]:
    """Load experiment outputs for all keys listed in _ACTIVE_EXPERIMENTS."""
    loaded: dict[str, pd.DataFrame] = {}
    for label, path in _SOURCES.items():
        if label not in _ACTIVE_EXPERIMENTS:
            continue
        if not path.exists():
            logger.warning("Skipping (not found): %s  [%s]", label, path)
            continue
        try:
            if path.suffix == ".pkl":
                df = pd.read_pickle(path)
            else:
                df = read_pos_file(path)
            if df.empty:
                logger.warning("Empty file, skipping: %s", label)
                continue
            # Add coordinate columns if not already present (pkl files may have them)
            if "easting_m" not in df.columns:
                df = add_utm32_columns(df)
            if "x_wm" not in df.columns:
                df = add_web_mercator_columns(df)
            loaded[label] = df
            logger.info(
                "Loaded %-30s  %5d epochs  %s → %s",
                label, len(df), df.index[0], df.index[-1],
            )
        except Exception as exc:
            logger.error("Failed to load '%s': %s", label, exc)
    return loaded


def main() -> None:
    _FIGURES.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # 1. Load data
    # -----------------------------------------------------------------------
    series = _load_all()
    if not series:
        logger.error("No experiment outputs found. Run the experiment scripts first.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 2. Trajectory map (raw, not aligned)
    # -----------------------------------------------------------------------
    logger.info("Generating trajectory map...")
    plotter.plot_trajectory_map(
        series,
        title="GNSS Trajectory Comparison – Sassuolo / Forlì",
        save_path=_FIGURES / "trajectory_map.png",
    )

    # -----------------------------------------------------------------------
    # 3. Time-series plot (raw, not aligned)
    # -----------------------------------------------------------------------
    logger.info("Generating raw time-series plot...")
    plotter.plot_time_series(
        series,
        title="Time Series – All Experiments",
        save_path=_FIGURES / "time_series.png",
    )

    # -----------------------------------------------------------------------
    # 4. Align series to common window (1-second grid)
    # Only align series that overlap with the reference to avoid empty windows.
    # -----------------------------------------------------------------------
    if len(series) >= 2 and _REFERENCE_LABEL in series:
        ref_start = series[_REFERENCE_LABEL].index.min()
        ref_end   = series[_REFERENCE_LABEL].index.max()

        alignable = {
            lbl: df for lbl, df in series.items()
            if df.index.min() <= ref_end and df.index.max() >= ref_start
        }
        skipped = set(series) - set(alignable)
        for lbl in skipped:
            logger.warning(
                "Skipping '%s' from alignment: no overlap with reference window %s → %s",
                lbl, ref_start, ref_end,
            )

        if len(alignable) >= 2:
            logger.info("Aligning %d series to common time window...", len(alignable))
            try:
                labels = list(alignable.keys())
                dfs    = list(alignable.values())
                aligned_dfs = align_series(dfs, freq="1s")
                aligned = dict(zip(labels, aligned_dfs))
            except ValueError as exc:
                logger.warning("Time alignment failed (%s). Skipping metrics.", exc)
                aligned = {}
        else:
            logger.warning("Only 1 series overlaps the reference. Skipping alignment.")
            aligned = {}
    else:
        aligned = {}

    # -----------------------------------------------------------------------
    # 5. Metrics vs reference
    # -----------------------------------------------------------------------
    if aligned and _REFERENCE_LABEL in aligned:
        logger.info("Computing metrics vs reference '%s'...", _REFERENCE_LABEL)
        ref_df = aligned[_REFERENCE_LABEL]
        metrics: dict[str, dict] = {}
        for label, df in aligned.items():
            if label == _REFERENCE_LABEL:
                continue
            try:
                metrics[label] = compute_all_metrics(df, ref_df)
            except Exception as exc:
                logger.warning("Metrics failed for '%s': %s", label, exc)

        if metrics:
            plotter.plot_metrics(
                metrics,
                title=f"Accuracy Metrics vs {_REFERENCE_LABEL}",
                save_path=_FIGURES / "metrics.png",
            )
    else:
        if not aligned:
            logger.info("Skipping metrics (alignment not available).")
        else:
            logger.warning(
                "Reference '%s' not in aligned series. Skipping metrics.",
                _REFERENCE_LABEL,
            )

    # -----------------------------------------------------------------------
    # 6. All-experiments overlay (aligned)
    # -----------------------------------------------------------------------
    if aligned:
        plotter.plot_all_experiments(
            aligned,
            reference_label=_REFERENCE_LABEL,
            title="All Experiments – Aligned Comparison",
            save_path=_FIGURES / "all_experiments.png",
        )

    logger.info("All figures saved to %s", _FIGURES)

    import matplotlib.pyplot as plt
    plt.show()


if __name__ == "__main__":
    main()
