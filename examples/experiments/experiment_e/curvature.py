"""
Curvature estimation and clustering for Experiment E round 2 (adaptive σ_v).

Motivation
----------
The constant-velocity KF in `run.py` uses a single fixed σ_v for the whole
track. σ_v low enough to smooth the straight legs well is too tight to
follow tight turns (the CV model is a poor fit for real curvature, so the
filter lags/cuts corners there). Rather than switching to a richer motion
model (constant-acceleration adds an acceleration state whose process noise
injects jitter even on straight legs — see README.md "Round 2"), this module
locates *where* the track curves and *how sharply*, so `run_adaptive.py` can
raise σ_v only in those epochs and keep it tight elsewhere.

Two functions:
    compute_turn_rate()   raw signal: windowed heading-change rate (rad/s)
    cluster_curvature()   k-means over |turn rate| -> discrete curvature rank

The turn rate is computed from Experiment D's static (no temporal model)
fused position — never from Experiment E's own KF state, which is exactly
the biased signal this module exists to correct (using it as the clustering
input would be circular).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def compute_turn_rate(
    df: pd.DataFrame,
    window_s: float = 5.0,
    dt: float = 1.0,
    speed_min: float = 0.3,
) -> pd.Series:
    """Windowed signed heading-change rate (rad/s) from northing/easting.

    Uses a central-difference window [-window_s, +window_s] around each
    epoch instead of epoch-to-epoch differencing: single-epoch GNSS noise
    otherwise dominates the heading estimate, especially near-stationary.

        v1 = p(t) - p(t - w)
        v2 = p(t + w) - p(t)
        Δθ = atan2(v1 × v2, v1 · v2)         (signed, wrapped to [-π, π])
        turn_rate(t) = Δθ / (w · dt)

    Epochs where the average speed over the window is below `speed_min`
    get NaN — heading is undefined near-stationary, and forcing a value
    there would inject clustering noise. Callers should treat NaN as
    "straight" (rank 0); `cluster_curvature` does this via `fillna(0.0)`.

    Parameters
    ----------
    df:
        Must have `northing_m`, `easting_m` columns on a uniform-spacing
        time index (e.g. the `align_series(..., freq="1s")` grid).
    window_s:
        Half-window, in seconds, converted to an epoch count via `dt`.
    dt:
        Epoch spacing in seconds (must match the grid `df` is sampled on).
    speed_min:
        m/s. Below this, the window is considered near-stationary.
    """
    w = max(1, round(window_s / dt))
    n = df["northing_m"].to_numpy(dtype=float)
    e = df["easting_m"].to_numpy(dtype=float)
    m = len(df)

    turn_rate = np.full(m, np.nan)
    for i in range(w, m - w):
        v1n, v1e = n[i] - n[i - w], e[i] - e[i - w]
        v2n, v2e = n[i + w] - n[i], e[i + w] - e[i]
        speed = (np.hypot(v1n, v1e) + np.hypot(v2n, v2e)) / (2 * w * dt)
        if speed < speed_min:
            continue
        cross = v1n * v2e - v1e * v2n
        dot = v1n * v2n + v1e * v2e
        dtheta = np.arctan2(cross, dot)
        turn_rate[i] = dtheta / (w * dt)

    return pd.Series(turn_rate, index=df.index, name="turn_rate_rad_s")


def cluster_curvature(
    turn_rate: pd.Series,
    k_candidates: tuple[int, ...] = (2, 3, 4),
    random_state: int = 0,
) -> tuple[pd.Series, dict]:
    """K-means on |turn rate|, k chosen by max silhouette score over `k_candidates`.

    Returns
    -------
    labels:
        Integer cluster rank per epoch, re-numbered by ascending centroid
        so rank 0 = straightest, rank k-1 = sharpest. NaN turn rate
        (near-stationary, see `compute_turn_rate`) is treated as 0 rad/s
        and therefore falls into rank 0.
    info:
        {"k": chosen k,
         "centroids_rad_s": rank-sorted centroid |turn rate|,
         "silhouette": {k: score, ...} for every candidate}
    """
    feature = turn_rate.abs().fillna(0.0).to_numpy().reshape(-1, 1)

    best_k, best_score, best_model = None, -1.0, None
    scores: dict[int, float] = {}
    for k in k_candidates:
        model = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(feature)
        score = float(silhouette_score(feature, model.labels_))
        scores[k] = score
        if score > best_score:
            best_k, best_score, best_model = k, score, model

    centroids = best_model.cluster_centers_.ravel()
    order = np.argsort(centroids)
    rank_of = {int(old): new for new, old in enumerate(order)}
    ranks = np.array([rank_of[int(c)] for c in best_model.labels_])

    labels = pd.Series(ranks, index=turn_rate.index, name="curvature_cluster")
    info = {
        "k": best_k,
        "centroids_rad_s": centroids[order].tolist(),
        "silhouette": scores,
    }
    return labels, info


def sigma_v_series(labels: pd.Series, base_sigma_v: float, growth: float) -> pd.Series:
    """σ_v(t) = base_sigma_v · growth^rank(t) — one knob (`growth`) for the whole ablation.

    growth = 1.0 reproduces the constant-σ_v baseline exactly (every rank
    gets the same multiplier). growth = 2.0 is the professor's original
    "double it" proposal: each curvature rank gets twice the σ_v of the
    rank below it.
    """
    k = int(labels.max()) + 1
    multipliers = growth ** np.arange(k)
    mult = labels.map(dict(enumerate(multipliers)))
    return base_sigma_v * mult
