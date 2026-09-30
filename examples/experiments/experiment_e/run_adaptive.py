#!/usr/bin/env python3
"""
Experiment E — Round 2: curvature-adaptive process noise.

Round 1 (`run.py`) runs the constant-velocity KF with a single fixed σ_v for
the whole track. It smooths straight legs well but lags/cuts corners in
turns, because a constant-velocity model is a poor fit for real curvature —
raising σ_v everywhere to fix the turns would just make the straight legs
noisy again (see README.md "Round 2" for the full writeup).

This script implements the two-round scheme proposed for the paper:

    1. Locate curvature.
       `curvature.compute_turn_rate()` computes a windowed heading-change
       rate from Experiment D's *static* fused position (no temporal model,
       so it is not biased by Exp E's own lag — using Exp E's KF velocity
       here would be circular, since that lag is exactly what we're trying
       to fix).
    2. Cluster it.
       `curvature.cluster_curvature()` runs k-means on |turn rate| (k chosen
       by silhouette score) and ranks the clusters 0 (straight) .. k-1
       (sharpest turn).
    3. Re-run the KF with a per-epoch σ_v.
       `curvature.sigma_v_series()` maps rank -> σ_v via a single knob,
       `growth`: σ_v(rank) = base_σ_v · growth^rank. growth = 1.0 reproduces
       the round-1 baseline exactly (sanity check). growth = 2.0 is the
       professor's original "double it per cluster" proposal. `run_ablation.py`
       sweeps `growth` and reports the effect on the accuracy metrics.

Outputs
-------
outputs/combined_kf_adaptive_g<growth>.pos / .pkl   same layout as round 1,
    plus `curvature_cluster` (int rank) and `sigma_v_used` (m/s) columns.
figures/ (only when `make_plots=True`)
    trajectory_map_e_adaptive.png, time_series_e_adaptive.png,
    all_experiments_e_adaptive.png, metrics_e_adaptive.png,
    curvature_clusters.png (trajectory coloured by curvature rank)

See README.md for the full derivation and the ablation results table.
"""
from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
_EXPERIMENTS = _HERE.parent
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_HERE))

from gnsspos.processing.coordinate import add_web_mercator_columns
from gnsspos.processing.time_alignment import align_series
from gnsspos.processing.metrics import compute_all_metrics
from gnsspos.processing import plotter

from curvature import compute_turn_rate, cluster_curvature, sigma_v_series

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _import_module(path: Path, name: str):
    """Load a sibling experiment's run.py under a unique module name.

    Both experiment_d/run.py and experiment_e/run.py are literally called
    `run.py` — a plain `import run` would collide in sys.modules, so both
    are loaded explicitly by file path instead.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_round1 = _import_module(_HERE / "run.py", "exp_e_round1")
_expd = _import_module(_EXPERIMENTS / "experiment_d" / "run.py", "exp_d_combine")

_OUTPUTS = _HERE / "outputs"
_FIGURES = _HERE / "figures"

# ---------------------------------------------------------------------------
# Tuning constants — see curvature.py and README.md §"Round 2" for rationale
# ---------------------------------------------------------------------------
_WINDOW_S = 5.0        # curvature estimation half-window, seconds
_SPEED_MIN = 0.3       # m/s, below which heading is undefined -> straight
_K_CANDIDATES = (2, 3, 4)


def _locate_curvature(aligned: dict[str, pd.DataFrame]) -> tuple[pd.Series, dict]:
    """Turn-rate + k-means clustering, reindexed onto the KF's full time grid."""
    raw_fused = _expd.combine(aligned)  # static, no temporal model -> no lag bias
    turn_rate = compute_turn_rate(raw_fused, window_s=_WINDOW_S, dt=_round1._DT, speed_min=_SPEED_MIN)
    labels, info = cluster_curvature(turn_rate, k_candidates=_K_CANDIDATES)

    rover_labels = list(aligned.keys())
    common_idx = aligned[rover_labels[0]].index
    # combine() drops epochs where any rover's sigma is NaN, so `labels` can
    # be a strict subset of the KF's full grid. Small gaps are bridged by
    # holding the nearest known rank; anything still missing (leading/
    # trailing gaps) defaults to rank 0 (straight).
    labels_full = labels.reindex(common_idx).ffill().bfill().fillna(0).astype(int)
    labels_full.name = "curvature_cluster"
    return labels_full, info


def _plot(
    aligned_c: dict[str, pd.DataFrame],
    kf_df: pd.DataFrame,
    baseline_df: pd.DataFrame | None,
) -> None:
    _FIGURES.mkdir(parents=True, exist_ok=True)

    series: dict[str, pd.DataFrame] = {}
    if baseline_df is not None:
        series["Exp 0 – NMEA (baseline)"] = baseline_df
    for rover, df in aligned_c.items():
        series[f"Exp C – {rover}"] = df
    series["Exp E round 2 – Adaptive KF"] = kf_df

    ref_label = "Exp 0 – NMEA (baseline)" if baseline_df is not None else None

    plotter.plot_trajectory_map(
        series,
        title="Experiment E Round 2 – Trajectory Comparison",
        save_path=_FIGURES / "trajectory_map_e_adaptive.png",
    )
    plotter.plot_time_series(
        series,
        title="Experiment E Round 2 – Time Series (Exp C rovers + Adaptive KF)",
        save_path=_FIGURES / "time_series_e_adaptive.png",
    )
    plotter.plot_all_experiments(
        series,
        reference_label=ref_label or list(series.keys())[0],
        title="Experiment E Round 2 – All Series Aligned",
        save_path=_FIGURES / "all_experiments_e_adaptive.png",
    )

    # Curvature cluster map: trajectory coloured by rank, independent of
    # the plotter module (no existing helper takes a per-point colour).
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 8))
    sc = ax.scatter(
        kf_df["easting_m"], kf_df["northing_m"],
        c=kf_df["curvature_cluster"], cmap="viridis", s=4,
    )
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    ax.set_title("Experiment E Round 2 – Curvature Clusters (0 = straight)")
    ax.set_aspect("equal")
    fig.colorbar(sc, ax=ax, label="Curvature rank")
    fig.tight_layout()
    fig.savefig(_FIGURES / "curvature_clusters.png", dpi=150)
    plt.close(fig)

    if ref_label and ref_label in series:
        try:
            ref_start = series[ref_label].index.min()
            ref_end = series[ref_label].index.max()
            alignable = {
                lbl: df for lbl, df in series.items()
                if df.index.min() <= ref_end and df.index.max() >= ref_start
            }
            if len(alignable) < 2:
                logger.warning("Not enough overlapping series for metrics.")
                return

            a_labels = list(alignable.keys())
            aligned_all = align_series(list(alignable.values()), freq="1s")
            aligned_all = _round1._refresh_utm(aligned_all)
            aligned_all = [add_web_mercator_columns(df) for df in aligned_all]
            aligned_dict = dict(zip(a_labels, aligned_all))

            ref_df = aligned_dict[ref_label]
            metrics: dict[str, dict] = {}
            for label, df in aligned_dict.items():
                if label == ref_label:
                    continue
                try:
                    metrics[label] = compute_all_metrics(df, ref_df)
                except Exception as exc:
                    logger.warning("Metrics failed for '%s': %s", label, exc)

            if metrics:
                plotter.plot_metrics(
                    metrics,
                    title=f"Experiment E Round 2 – Metrics vs {ref_label}",
                    save_path=_FIGURES / "metrics_e_adaptive.png",
                )
        except Exception as exc:
            logger.warning("Metrics computation failed: %s", exc)


def summary_metrics(kf_df: pd.DataFrame, baseline_df: pd.DataFrame) -> dict[str, float]:
    """Final cumulative RMS_n/e/u, μ_d, σ_d of `kf_df` vs `baseline_df` (Exp 0).

    Shared by `run_adaptive.py`'s own logging and by `run_ablation.py`'s
    per-growth comparison table — both need the same "one number per run"
    reduction of `compute_all_metrics`' cumulative series (last value = the
    metric computed over the full overlapping window).

    `align_series` can leave NaN rows at the window edge (no interpolation
    neighbour just inside the clip boundary) or across gaps wider than the
    grid step (pre-existing behaviour of `time_alignment.fill_gaps`, not
    specific to this script). `compute_rms`/`compute_sigma_d` cumsum their
    residuals, so a single NaN row poisons every value after it — dropping
    the NaN rows before computing metrics keeps the summary over the epochs
    that actually have data on both sides.
    """
    aligned = align_series([kf_df, baseline_df], freq="1s")
    aligned = _round1._refresh_utm(aligned)
    exp_aligned, ref_aligned = aligned
    valid = ~(
        exp_aligned[["northing_m", "easting_m", "height_m"]].isna().any(axis=1)
        | ref_aligned[["northing_m", "easting_m", "height_m"]].isna().any(axis=1)
    )
    exp_aligned, ref_aligned = exp_aligned[valid], ref_aligned[valid]
    metrics = compute_all_metrics(exp_aligned, ref_aligned)
    return {name: float(series.iloc[-1]) for name, series in metrics.items()}


def run(growth: float = 2.0, make_plots: bool = True) -> pd.DataFrame:
    _OUTPUTS.mkdir(parents=True, exist_ok=True)

    exp_c = _round1._load_exp_c()
    if len(exp_c) < 2:
        logger.error(
            "Need >= 2 rover series; found %d. Run experiment_c/run.py first.", len(exp_c),
        )
        sys.exit(1)
    rover_labels = list(exp_c.keys())
    aligned_dfs = align_series(list(exp_c.values()), freq=f"{int(_round1._DT)}s")
    aligned_dfs = _round1._refresh_utm(aligned_dfs)
    aligned = dict(zip(rover_labels, aligned_dfs))

    logger.info("Locating curvature (window=%.1fs, speed_min=%.1f m/s)...", _WINDOW_S, _SPEED_MIN)
    labels_full, info = _locate_curvature(aligned)
    logger.info(
        "k-means: k=%d  centroids(rad/s)=%s  silhouette=%s",
        info["k"], [f"{c:.4f}" for c in info["centroids_rad_s"]], info["silhouette"],
    )
    logger.info("Cluster occupancy (epochs): %s", labels_full.value_counts().sort_index().to_dict())

    sigma_v_t = sigma_v_series(labels_full, base_sigma_v=_round1._SIGMA_V, growth=growth)
    logger.info(
        "Running adaptive KF (growth=%.3g, base σ_v=%.3f m/s, per-rank σ_v=%s)...",
        growth, _round1._SIGMA_V,
        [f"{_round1._SIGMA_V * growth ** r:.3f}" for r in range(info["k"])],
    )
    kf_df = _round1.run_kf(aligned, sigma_v_t=sigma_v_t)
    kf_df = add_web_mercator_columns(kf_df)
    kf_df["curvature_cluster"] = labels_full.to_numpy()
    kf_df["sigma_v_used"] = sigma_v_t.to_numpy()
    logger.info("Adaptive KF output: %d epochs", len(kf_df))

    growth_tag = f"{growth:g}".replace(".", "p")
    _round1.write_pos(kf_df, _OUTPUTS / f"combined_kf_adaptive_g{growth_tag}.pos")
    kf_df.to_pickle(_OUTPUTS / f"combined_kf_adaptive_g{growth_tag}.pkl")

    logger.info("Q distribution: %s", kf_df["Q"].value_counts().to_dict())
    logger.info(
        "Adaptive KF mean σ:  σ_n=%.4f m  σ_e=%.4f m  σ_u=%.4f m",
        kf_df["sdn_m"].mean(), kf_df["sde_m"].mean(), kf_df["sdu_m"].mean(),
    )

    baseline_df = _round1._load_baseline()
    if baseline_df is not None:
        m = summary_metrics(kf_df, baseline_df)
        logger.info(
            "Final metrics vs Exp 0:  RMS_n=%.4f m  RMS_e=%.4f m  RMS_u=%.4f m  μ_d=%.4f m  σ_d=%.4f m",
            m["rms_northing_m"], m["rms_easting_m"], m["rms_height_m"], m["mu_d"], m["sigma_d"],
        )

    if make_plots:
        logger.info("Generating plots -> %s", _FIGURES)
        _plot(aligned, kf_df, baseline_df)
        import matplotlib.pyplot as plt
        plt.show()

    return kf_df


if __name__ == "__main__":
    run()
