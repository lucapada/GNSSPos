#!/usr/bin/env python3
"""
Experiment D – Inverse-variance weighted combination of Experiment C rover solutions.

Combines the three kinematic RTK solutions (COM23, COM24, COM25) from Experiment C
into a single position time series using per-component inverse-variance weighting.

Algorithm (per epoch, N = 3 receivers)
---------------------------------------
Position weights (diagonal W_i matrices):

    w_{ij} = (1/σ_{ji}²) / Σ_k (1/σ_{jk}²)
    j ∈ {n, e, u}  →  {northing, easting, height}

Combined position:

    x̂ = Σ_i W_i x_i        (component-wise weighted mean)

Combined covariance:

    Ĉ = Σ_i W_i C_i W_i^T,   W_i = diag(w_in, w_ie, w_iu)

    C_i = [[sdn²  sdne  sdun],
           [sdne  sde²  sdeu],
           [sdun  sdeu  sdu²]]

Positive-definiteness: while det(Ĉ) ≤ 0, scale all off-diagonal elements by 0.9.

# TODO: alternative regularisation – project onto nearest PSD matrix by clamping
# negative eigenvalues to zero (Higham 1988, numerically more stable):
#     vals, vecs = np.linalg.eigh(C_hat)
#     vals = np.maximum(vals, 0)
#     C_hat = vecs @ np.diag(vals) @ vecs.T
# Enable this block if supervisors request eigenvalue-based regularisation.

Outputs
-------
outputs/combined.pos   RTKLIB-compatible LLH/UTC .pos file
outputs/combined.pkl   pandas pickle (same data + UTM32 + WebMercator columns)
figures/               trajectory_map_d.png, time_series_d.png,
                       all_experiments_d.png, metrics_d.png
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_ROOT))

from gnsspos.processing.coordinate import add_utm32_columns, add_web_mercator_columns
from gnsspos.processing.time_alignment import align_series
from gnsspos.processing.metrics import compute_all_metrics
from gnsspos.processing import plotter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

_EXPERIMENTS = _HERE.parent
_EXP_C_OUT   = _EXPERIMENTS / "experiment_c" / "outputs"
_EXP_0_OUT   = _EXPERIMENTS / "experiment_0" / "outputs"
_OUTPUTS     = _HERE / "outputs"
_FIGURES     = _HERE / "figures"

_ROVERS = ["COM23", "COM24", "COM25"]

_WGS84_TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)
_UTM_TO_WGS84 = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

# Pre-built index for all off-diagonal elements of a 3×3 matrix
_OFF_DIAG = np.where(~np.eye(3, dtype=bool))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_exp_c() -> dict[str, pd.DataFrame]:
    series: dict[str, pd.DataFrame] = {}
    for rover in _ROVERS:
        pkl = _EXP_C_OUT / f"{rover}_rover.pkl"
        if not pkl.exists():
            logger.warning("Missing exp_c pkl: %s", pkl)
            continue
        df = pd.read_pickle(pkl)
        series[rover] = df
        logger.info(
            "Loaded %s: %d epochs  %s → %s",
            rover, len(df), df.index[0], df.index[-1],
        )
    return series


def _load_baseline() -> pd.DataFrame | None:
    pkl = _EXP_0_OUT / "COM23_nmea.pkl"
    if not pkl.exists():
        logger.warning("Baseline (exp_0) not found: %s", pkl)
        return None
    df = pd.read_pickle(pkl)
    logger.info("Loaded baseline: %d epochs  %s → %s", len(df), df.index[0], df.index[-1])
    return df


# ---------------------------------------------------------------------------
# UTM refresh (alignment interpolates lat/lon but not UTM columns)
# ---------------------------------------------------------------------------

def _refresh_utm(dfs: list[pd.DataFrame]) -> list[pd.DataFrame]:
    result = []
    for df in dfs:
        df = df.copy()
        easting, northing = _WGS84_TO_UTM.transform(
            df["longitude_deg"].values, df["latitude_deg"].values,
        )
        df["easting_m"]  = easting
        df["northing_m"] = northing
        result.append(df)
    return result


# ---------------------------------------------------------------------------
# Combination
# ---------------------------------------------------------------------------

def _build_cov(r: pd.Series) -> np.ndarray:
    """3×3 N-E-U covariance matrix from a pos row."""
    return np.array([
        [r["sdn_m"] ** 2, r["sdne_m"],      r["sdun_m"]     ],
        [r["sdne_m"],     r["sde_m"] ** 2,  r["sdeu_m"]     ],
        [r["sdun_m"],     r["sdeu_m"],       r["sdu_m"] ** 2 ],
    ])


def _combine_epoch(rows: list[pd.Series]) -> dict:
    """Inverse-variance weighted combination of N receiver rows."""
    positions = np.array([
        [r["northing_m"], r["easting_m"], r["height_m"]] for r in rows
    ])  # (N, 3): columns = [north, east, up]

    sigmas = np.array([
        [r["sdn_m"], r["sde_m"], r["sdu_m"]] for r in rows
    ])  # (N, 3): σ_n, σ_e, σ_u

    # Guard against degenerate zero/negative sigma
    sigmas = np.where(sigmas > 0, sigmas, 1e6)

    inv_var     = 1.0 / sigmas ** 2          # (N, 3)
    sum_inv_var = inv_var.sum(axis=0)         # (3,)
    W_scalars   = inv_var / sum_inv_var       # (N, 3): w_{ij}

    # Combined position (per-component weighted mean)
    combined                      = (W_scalars * positions).sum(axis=0)  # (3,)
    northing_c, easting_c, height_c = combined

    # Combined covariance  Ĉ = Σ_i W_i C_i W_i^T
    C_hat = np.zeros((3, 3))
    for i, r in enumerate(rows):
        W_i    = np.diag(W_scalars[i])
        C_hat += W_i @ _build_cov(r) @ W_i.T

    # Regularise: scale off-diagonals by 0.9 until det(Ĉ) > 0
    # TODO: see module docstring for eigenvalue-based alternative
    for _ in range(2000):
        if np.linalg.det(C_hat) > 0:
            break
        C_hat[_OFF_DIAG] *= 0.9

    lon_c, lat_c = _UTM_TO_WGS84.transform(easting_c, northing_c)

    return {
        "latitude_deg":  lat_c,
        "longitude_deg": lon_c,
        "height_m":      height_c,
        "northing_m":    northing_c,
        "easting_m":     easting_c,
        "Q":             int(min(r["Q"]  for r in rows)),
        "ns":            int(min(r["ns"] for r in rows)),
        "sdn_m":         float(np.sqrt(max(C_hat[0, 0], 0.0))),
        "sde_m":         float(np.sqrt(max(C_hat[1, 1], 0.0))),
        "sdu_m":         float(np.sqrt(max(C_hat[2, 2], 0.0))),
        "sdne_m":        float(C_hat[0, 1]),
        "sdeu_m":        float(C_hat[1, 2]),
        "sdun_m":        float(C_hat[2, 0]),
        "age_s":         0.0,
        "ratio":         0.0,
    }


def combine(aligned: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Epoch-wise weighted combination of aligned rover DataFrames."""
    rover_list = list(aligned.keys())
    common_idx = aligned[rover_list[0]].index
    records: list[dict] = []

    for t in common_idx:
        rows = []
        skip = False
        for rover in rover_list:
            r = aligned[rover].loc[t]
            if r[["sdn_m", "sde_m", "sdu_m"]].isna().any():
                skip = True
                break
            rows.append(r)
        if skip:
            continue
        rec = _combine_epoch(rows)
        rec["time"] = t
        records.append(rec)

    df = pd.DataFrame(records).set_index("time")
    df.index.name = "utc"
    return df


# ---------------------------------------------------------------------------
# .pos writer
# ---------------------------------------------------------------------------

_POS_HEADER = (
    "% program   : GNSSPos experiment_d (inverse-variance weighted combination)\n"
    "% (lat/lon/height=WGS84/ellipsoidal,Q=1:fix,2:float,3:sbas,4:dgps,5:single,6:ppp,"
    "ns=# of satellites)\n"
    "%  UTC                   latitude(deg) longitude(deg)  height(m)   Q  ns"
    "   sdn(m)   sde(m)   sdu(m)  sdne(m)  sdeu(m)  sdun(m) age(s)  ratio"
    "    vn(m/s)    ve(m/s)    vu(m/s)      sdvn     sdve     sdvu"
    "    sdvne    sdveu    sdvun\n"
)


def write_pos(df: pd.DataFrame, path: Path) -> None:
    """Write a RTKLIB-compatible LLH/UTC .pos file."""
    lines = [_POS_HEADER]
    for t, row in df.iterrows():
        ts   = pd.Timestamp(t).strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
        line = (
            f"{ts}  {row['latitude_deg']:14.9f}  {row['longitude_deg']:14.9f}  "
            f"{row['height_m']:10.4f}  {int(row['Q']):2d}  {int(row['ns']):3d}  "
            f"{row['sdn_m']:8.4f}  {row['sde_m']:8.4f}  {row['sdu_m']:8.4f}  "
            f"{row['sdne_m']:8.4f}  {row['sdeu_m']:8.4f}  {row['sdun_m']:8.4f}  "
            f"{row['age_s']:6.2f}  {row['ratio']:6.1f}"
            "    0.00000    0.00000    0.00000   0.00000  0.00000  0.00000"
            "   0.00000   0.00000   0.00000\n"
        )
        lines.append(line)
    path.write_text("".join(lines), encoding="utf-8")
    logger.info("Written %d epochs → %s", len(df), path)


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def _plot(
    aligned_c: dict[str, pd.DataFrame],
    combined_df: pd.DataFrame,
    baseline_df: pd.DataFrame | None,
) -> None:
    _FIGURES.mkdir(parents=True, exist_ok=True)

    series: dict[str, pd.DataFrame] = {}
    if baseline_df is not None:
        series["Exp 0 – NMEA (baseline)"] = baseline_df
    for rover, df in aligned_c.items():
        series[f"Exp C – {rover}"] = df
    series["Exp D – Combined"] = combined_df

    ref_label = "Exp 0 – NMEA (baseline)" if baseline_df is not None else None

    plotter.plot_trajectory_map(
        series,
        title="Experiment D – Trajectory Comparison",
        save_path=_FIGURES / "trajectory_map_d.png",
    )
    plotter.plot_time_series(
        series,
        title="Experiment D – Time Series (Exp C rovers + Combined)",
        save_path=_FIGURES / "time_series_d.png",
    )
    plotter.plot_all_experiments(
        series,
        reference_label=ref_label or list(series.keys())[0],
        title="Experiment D – All Series Aligned",
        save_path=_FIGURES / "all_experiments_d.png",
    )

    if ref_label and ref_label in series:
        try:
            ref_start = series[ref_label].index.min()
            ref_end   = series[ref_label].index.max()
            alignable = {
                lbl: df for lbl, df in series.items()
                if df.index.min() <= ref_end and df.index.max() >= ref_start
            }
            if len(alignable) < 2:
                logger.warning("Not enough overlapping series for metrics.")
                return

            a_labels    = list(alignable.keys())
            aligned_all = align_series(list(alignable.values()), freq="1s")
            aligned_all = _refresh_utm(aligned_all)
            aligned_all = [add_web_mercator_columns(df) for df in aligned_all]
            aligned_dict = dict(zip(a_labels, aligned_all))

            ref_df  = aligned_dict[ref_label]
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
                    title=f"Experiment D – Metrics vs {ref_label}",
                    save_path=_FIGURES / "metrics_d.png",
                )
        except Exception as exc:
            logger.warning("Metrics computation failed: %s", exc)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> pd.DataFrame:
    _OUTPUTS.mkdir(parents=True, exist_ok=True)

    # 1. Load experiment C series
    exp_c = _load_exp_c()
    if len(exp_c) < 2:
        logger.error(
            "Need ≥ 2 rover series; found %d. Run experiment_c/run.py first.", len(exp_c),
        )
        sys.exit(1)

    # 2. Align to common 1 s time grid
    logger.info("Aligning %d rover series to 1 s grid...", len(exp_c))
    rover_labels = list(exp_c.keys())
    aligned_dfs  = align_series(list(exp_c.values()), freq="1s")
    aligned_dfs  = _refresh_utm(aligned_dfs)
    aligned      = dict(zip(rover_labels, aligned_dfs))

    # 3. Inverse-variance weighted combination
    logger.info("Computing weighted combination...")
    combined_df = combine(aligned)
    combined_df = add_web_mercator_columns(combined_df)
    logger.info("Combined: %d epochs", len(combined_df))

    # 4. Write outputs
    write_pos(combined_df, _OUTPUTS / "combined.pos")
    combined_df.to_pickle(_OUTPUTS / "combined.pkl")

    # 5. Quality summary
    logger.info("Q distribution: %s", combined_df["Q"].value_counts().to_dict())
    logger.info(
        "Combined  σ_n=%.4f m  σ_e=%.4f m  σ_u=%.4f m  (epoch mean)",
        combined_df["sdn_m"].mean(), combined_df["sde_m"].mean(), combined_df["sdu_m"].mean(),
    )
    for rover in rover_labels:
        df_r = aligned[rover]
        logger.info(
            "[%s]    σ_n=%.4f m  σ_e=%.4f m  σ_u=%.4f m",
            rover, df_r["sdn_m"].mean(), df_r["sde_m"].mean(), df_r["sdu_m"].mean(),
        )

    # 6. Plots
    baseline_df = _load_baseline()
    logger.info("Generating plots → %s", _FIGURES)
    _plot(aligned, combined_df, baseline_df)

    import matplotlib.pyplot as plt
    plt.show()

    return combined_df


if __name__ == "__main__":
    run()
