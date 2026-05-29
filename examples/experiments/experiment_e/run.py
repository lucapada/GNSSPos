#!/usr/bin/env python3
"""
Experiment E – Kalman filter fusion of Experiment C rover solutions.

Combines the three kinematic RTK solutions (COM23, COM24, COM25) from
Experiment C into a single position time series using a constant-velocity
Kalman filter with sequential per-rover measurement updates.

State (6-dim)
-------------
    x = [n, e, u, vn, ve, vu]^T          # NEU position + velocity

Process model (constant velocity, Δt = 1 s)
-------------------------------------------
    F = [[I_3,  Δt · I_3],
         [0,    I_3      ]]

    Q = block_diag(q_p · I_3, q_v · I_3)
        q_p  = (σ_p · Δt)^2     position random walk
        q_v  = (σ_v · Δt)^2     velocity random walk (drives smoothing)

Measurement model (per rover i)
-------------------------------
    z_i = H · x + ν_i           H = [I_3,  0_3]
    R_i = NEU covariance from rover .pos row (Exp D _build_cov reused)

Filter loop (per epoch t)
-------------------------
    1. Predict:    x = F·x ;  P = F·P·F^T + Q
    2. For each rover i with a valid row at t:
           y  = z_i − H·x
           S  = H·P·H^T + R_i
           K  = P·H^T·S^{-1}
           x  = x + K·y
           P  = (I − K·H)·P
    3. If no rover has a valid row → predict-only step (skip update).

Initialisation
--------------
    x_0 = [n̄, ē, ū, 0, 0, 0]   from first epoch inverse-variance position mean
    P_0 = diag(σ_p0^2 · I_3, σ_v0^2 · I_3)  with σ_p0 = 1 m, σ_v0 = 5 m/s
          (deliberately loose; filter converges within ~10 epochs)

Outputs
-------
outputs/combined_kf.pos   RTKLIB-compatible LLH/UTC .pos file
outputs/combined_kf.pkl   pandas pickle (same data + UTM32 + WebMercator columns)
figures/                  trajectory_map_e.png, time_series_e.png,
                          all_experiments_e.png, metrics_e.png

See README.md in this folder for the full algorithm rationale and tuning notes.
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

# ---------------------------------------------------------------------------
# Tuning constants — see README.md §"Tuning the process noise" for guidance
# ---------------------------------------------------------------------------
_DT       = 1.0        # epoch spacing (matches align_series freq="1s")
_SIGMA_P  = 0.05       # m       — position random walk per epoch
_SIGMA_V  = 0.5        # m/s     — velocity random walk per epoch (smoothing knob)
_P0_POS   = 1.0        # m       — initial position uncertainty
_P0_VEL   = 5.0        # m/s     — initial velocity uncertainty

_H = np.hstack([np.eye(3), np.zeros((3, 3))])           # (3, 6)
_F = np.block([[np.eye(3), _DT * np.eye(3)],            # (6, 6)
               [np.zeros((3, 3)), np.eye(3)]])
_Q = np.diag([
    (_SIGMA_P * _DT) ** 2, (_SIGMA_P * _DT) ** 2, (_SIGMA_P * _DT) ** 2,
    (_SIGMA_V * _DT) ** 2, (_SIGMA_V * _DT) ** 2, (_SIGMA_V * _DT) ** 2,
])
_I6 = np.eye(6)


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
# Filter primitives
# ---------------------------------------------------------------------------

def _build_R(r: pd.Series) -> np.ndarray:
    """3×3 NEU measurement covariance from a pos row (same as Exp D)."""
    return np.array([
        [r["sdn_m"] ** 2, r["sdne_m"],      r["sdun_m"]     ],
        [r["sdne_m"],     r["sde_m"] ** 2,  r["sdeu_m"]     ],
        [r["sdun_m"],     r["sdeu_m"],       r["sdu_m"] ** 2 ],
    ])


def _row_valid(r: pd.Series) -> bool:
    return not r[["sdn_m", "sde_m", "sdu_m", "northing_m", "easting_m", "height_m"]].isna().any()


def _initial_state(rows: list[pd.Series]) -> tuple[np.ndarray, np.ndarray]:
    """Inverse-variance weighted mean of first valid epoch → x_0, P_0."""
    positions = np.array([[r["northing_m"], r["easting_m"], r["height_m"]] for r in rows])
    sigmas    = np.array([[r["sdn_m"],      r["sde_m"],     r["sdu_m"]]    for r in rows])
    sigmas    = np.where(sigmas > 0, sigmas, 1e6)
    w         = (1.0 / sigmas ** 2)
    w        /= w.sum(axis=0)
    p0        = (w * positions).sum(axis=0)

    x0 = np.concatenate([p0, np.zeros(3)])
    P0 = np.diag([_P0_POS ** 2] * 3 + [_P0_VEL ** 2] * 3)
    return x0, P0


# ---------------------------------------------------------------------------
# Kalman filter loop
# ---------------------------------------------------------------------------

def run_kf(aligned: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Constant-velocity KF on aligned rover DataFrames, sequential updates."""
    rover_labels = list(aligned.keys())
    common_idx   = aligned[rover_labels[0]].index

    # Bootstrap from first epoch with ≥ 1 valid rover row
    x = P = None
    for t in common_idx:
        rows = [aligned[r].loc[t] for r in rover_labels]
        valid = [r for r in rows if _row_valid(r)]
        if valid:
            x, P = _initial_state(valid)
            t_start = t
            break
    if x is None:
        raise RuntimeError("No valid epoch found to initialise the filter.")
    logger.info("Filter initialised at %s with %d valid rover(s)", t_start, len(valid))

    records: list[dict] = []
    n_predict_only = 0
    for t in common_idx:
        # Predict
        x = _F @ x
        P = _F @ P @ _F.T + _Q

        # Sequential update over each rover with a valid row
        updates = 0
        for rover in rover_labels:
            r = aligned[rover].loc[t]
            if not _row_valid(r):
                continue
            z = np.array([r["northing_m"], r["easting_m"], r["height_m"]])
            R = _build_R(r)
            y = z - _H @ x
            S = _H @ P @ _H.T + R
            K = P @ _H.T @ np.linalg.inv(S)
            x = x + K @ y
            P = (_I6 - K @ _H) @ P
            updates += 1
        if updates == 0:
            n_predict_only += 1

        n_c, e_c, u_c = x[0], x[1], x[2]
        lon_c, lat_c   = _UTM_TO_WGS84.transform(e_c, n_c)

        # Worst-case Q/ns across rovers contributing this epoch (for downstream colouring)
        contributing = [aligned[r].loc[t] for r in rover_labels if _row_valid(aligned[r].loc[t])]
        q_min  = int(min((r["Q"]  for r in contributing), default=0))
        ns_min = int(min((r["ns"] for r in contributing), default=0))

        records.append({
            "time":          t,
            "latitude_deg":  lat_c,
            "longitude_deg": lon_c,
            "height_m":      u_c,
            "northing_m":    n_c,
            "easting_m":     e_c,
            "Q":             q_min,
            "ns":            ns_min,
            "sdn_m":         float(np.sqrt(max(P[0, 0], 0.0))),
            "sde_m":         float(np.sqrt(max(P[1, 1], 0.0))),
            "sdu_m":         float(np.sqrt(max(P[2, 2], 0.0))),
            "sdne_m":        float(P[0, 1]),
            "sdeu_m":        float(P[1, 2]),
            "sdun_m":        float(P[2, 0]),
            "age_s":         0.0,
            "ratio":         0.0,
        })

    if n_predict_only:
        logger.info("Predict-only steps (no rover update): %d", n_predict_only)

    df = pd.DataFrame(records).set_index("time")
    df.index.name = "utc"
    return df


# ---------------------------------------------------------------------------
# .pos writer
# ---------------------------------------------------------------------------

_POS_HEADER = (
    "% program   : GNSSPos experiment_e (Kalman filter fusion)\n"
    "% (lat/lon/height=WGS84/ellipsoidal,Q=1:fix,2:float,3:sbas,4:dgps,5:single,6:ppp,"
    "ns=# of satellites)\n"
    "%  UTC                   latitude(deg) longitude(deg)  height(m)   Q  ns"
    "   sdn(m)   sde(m)   sdu(m)  sdne(m)  sdeu(m)  sdun(m) age(s)  ratio"
    "    vn(m/s)    ve(m/s)    vu(m/s)      sdvn     sdve     sdvu"
    "    sdvne    sdveu    sdvun\n"
)


def write_pos(df: pd.DataFrame, path: Path) -> None:
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
    kf_df: pd.DataFrame,
    baseline_df: pd.DataFrame | None,
) -> None:
    _FIGURES.mkdir(parents=True, exist_ok=True)

    series: dict[str, pd.DataFrame] = {}
    if baseline_df is not None:
        series["Exp 0 – NMEA (baseline)"] = baseline_df
    for rover, df in aligned_c.items():
        series[f"Exp C – {rover}"] = df
    series["Exp E – Kalman fusion"] = kf_df

    ref_label = "Exp 0 – NMEA (baseline)" if baseline_df is not None else None

    plotter.plot_trajectory_map(
        series,
        title="Experiment E – Trajectory Comparison",
        save_path=_FIGURES / "trajectory_map_e.png",
    )
    plotter.plot_time_series(
        series,
        title="Experiment E – Time Series (Exp C rovers + KF Fusion)",
        save_path=_FIGURES / "time_series_e.png",
    )
    plotter.plot_all_experiments(
        series,
        reference_label=ref_label or list(series.keys())[0],
        title="Experiment E – All Series Aligned",
        save_path=_FIGURES / "all_experiments_e.png",
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
                    title=f"Experiment E – Metrics vs {ref_label}",
                    save_path=_FIGURES / "metrics_e.png",
                )
        except Exception as exc:
            logger.warning("Metrics computation failed: %s", exc)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> pd.DataFrame:
    _OUTPUTS.mkdir(parents=True, exist_ok=True)

    # 1. Load Experiment C rover series
    exp_c = _load_exp_c()
    if len(exp_c) < 2:
        logger.error(
            "Need ≥ 2 rover series; found %d. Run experiment_c/run.py first.", len(exp_c),
        )
        sys.exit(1)

    # 2. Align to common 1 s time grid (same grid as Exp D)
    logger.info("Aligning %d rover series to %.0f s grid...", len(exp_c), _DT)
    rover_labels = list(exp_c.keys())
    aligned_dfs  = align_series(list(exp_c.values()), freq=f"{int(_DT)}s")
    aligned_dfs  = _refresh_utm(aligned_dfs)
    aligned      = dict(zip(rover_labels, aligned_dfs))

    # 3. Run Kalman filter
    logger.info("Running KF (σ_p=%.3f m, σ_v=%.3f m/s)...", _SIGMA_P, _SIGMA_V)
    kf_df = run_kf(aligned)
    kf_df = add_web_mercator_columns(kf_df)
    logger.info("KF output: %d epochs", len(kf_df))

    # 4. Write outputs
    write_pos(kf_df, _OUTPUTS / "combined_kf.pos")
    kf_df.to_pickle(_OUTPUTS / "combined_kf.pkl")

    # 5. Quality summary
    logger.info("Q distribution: %s", kf_df["Q"].value_counts().to_dict())
    logger.info(
        "KF mean σ:  σ_n=%.4f m  σ_e=%.4f m  σ_u=%.4f m",
        kf_df["sdn_m"].mean(), kf_df["sde_m"].mean(), kf_df["sdu_m"].mean(),
    )
    for rover in rover_labels:
        df_r = aligned[rover]
        logger.info(
            "[%s]   σ_n=%.4f m  σ_e=%.4f m  σ_u=%.4f m",
            rover, df_r["sdn_m"].mean(), df_r["sde_m"].mean(), df_r["sdu_m"].mean(),
        )

    # 6. Plots
    baseline_df = _load_baseline()
    logger.info("Generating plots → %s", _FIGURES)
    _plot(aligned, kf_df, baseline_df)

    import matplotlib.pyplot as plt
    plt.show()

    return kf_df


if __name__ == "__main__":
    run()
