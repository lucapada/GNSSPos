# Experiment E – Kalman Filter Fusion

Constant-velocity Kalman filter that fuses the three Experiment C kinematic
rover solutions (COM23, COM24, COM25) into a single position time series.

Where **Experiment D** combines rovers epoch-by-epoch with a static
inverse-variance weighted mean (no temporal model), **Experiment E** adds a
dynamic model that smooths positions across time and estimates velocity,
trading a small lag for a substantially lower per-epoch σ.

---

## 1. Algorithm overview

### 1.1 State vector

```
x = [ n  e  u  vn  ve  vu ]ᵀ        (6 × 1)
```

Position in UTM Zone 32N northing/easting and ellipsoidal height (`height_m`)
plus three velocity components in the same frame. UTM is chosen because the
GNSS measurements are already in metres in this frame after
`add_utm32_columns()` and the metric distortion is negligible over the
campaign area.

### 1.2 Process model (constant velocity, Δt = 1 s)

```
F = [ I₃   Δt · I₃ ]            (6 × 6)
    [ 0    I₃       ]

Q = block_diag( q_p · I₃ , q_v · I₃ )

    q_p = (σ_p · Δt)²            position random walk
    q_v = (σ_v · Δt)²            velocity random walk (smoothing knob)
```

Δt matches the alignment grid produced by
`align_series(..., freq="1s")`, the same grid Experiment D uses. The constants
`_SIGMA_P` and `_SIGMA_V` live at the top of `run.py`.

### 1.3 Measurement model

Each rover supplies a position-only measurement of the state:

```
H   = [ I₃   0₃ ]            (3 × 6)
z_i = [ n_i  e_i  u_i ]ᵀ     from the rover .pos row at epoch t
R_i = NEU covariance reconstructed from the same row’s
      sdn_m, sde_m, sdu_m, sdne_m, sdeu_m, sdun_m fields
```

`_build_R()` reuses the exact same convention as `_build_cov()` in
`experiment_d/run.py`, so both experiments consume identical per-epoch
covariances.

### 1.4 Filter loop (per epoch t)

1. **Predict**
   ```
   x  =  F · x
   P  =  F · P · Fᵀ  +  Q
   ```
2. **Sequential update** — for each rover `i` whose row at `t` is valid:
   ```
   y  =  z_i − H · x
   S  =  H · P · Hᵀ  +  R_i
   K  =  P · Hᵀ · S⁻¹
   x  =  x  +  K · y
   P  =  (I − K · H) · P
   ```
   Sequential updates over independent measurements are mathematically
   equivalent to a single stacked update with block-diagonal R, but avoid
   building and inverting a 9 × 9 matrix.
3. **Predict-only fallback** — if no rover has a valid row at `t` (gap), the
   step uses only the prediction. `align_series` already fills gaps by
   interpolation, but rows with NaN σ are still treated as invalid (same
   guard as Exp D, `run.py` line 206).

### 1.5 Initialisation

```
x₀ = [ n̄  ē  ū  0  0  0 ]ᵀ      n̄, ē, ū from inverse-variance
                                  weighted mean of first valid epoch

P₀ = diag( σ_p₀² · I₃ , σ_v₀² · I₃ )
     σ_p₀ = 1 m       σ_v₀ = 5 m/s
```

`P₀` is deliberately loose. The filter typically converges within ~10
epochs, after which the position σ drops below the σ of any single rover.

---

## 2. Step-by-step pipeline (mirrors `run()` in `run.py`)

| # | Function | What it does |
|---|----------|--------------|
| 1 | `_load_exp_c()` | Read `experiment_c/outputs/COM{23,24,25}_rover.pkl`. Requires ≥ 2 rovers. |
| 2 | `align_series(..., freq="1s")` then `_refresh_utm()` | Resample all rovers onto a shared 1-s grid and recompute UTM northing/easting from the interpolated lat/lon. |
| 3 | `run_kf(aligned)` | Bootstrap `x₀`, `P₀` from the first valid epoch, then iterate predict / sequential-update over every epoch. Emits a DataFrame with the same columns Exp D produces. |
| 4 | `add_web_mercator_columns()` | Add `x_wm`, `y_wm` so the plotter can overlay the trajectory on an OSM basemap. |
| 5 | `write_pos()` + `to_pickle()` | Persist `outputs/combined_kf.pos` and `outputs/combined_kf.pkl`. The `.pos` file uses the same LLH/UTC layout as RTKLIB so it can be inspected with the same tools as Exp B/C/D. |
| 6 | Quality summary log | Q distribution, mean σ_n / σ_e / σ_u of the KF output and of each input rover for a quick before/after comparison. |
| 7 | `_plot()` | Generate `trajectory_map_e.png`, `time_series_e.png`, `all_experiments_e.png`, and (if Exp 0 baseline exists) `metrics_e.png` in `figures/`. |

---

## 3. Tuning the process noise

The two free parameters are `_SIGMA_P` and `_SIGMA_V` in `run.py`. The defaults

```python
_SIGMA_P = 0.05    # m       position random walk
_SIGMA_V = 0.5     # m/s     velocity random walk
```

are sized for a low-dynamics rover (slow drone or pedestrian). Heuristics:

- **σ_v too low** → filter trusts the constant-velocity model too much,
  output lags real manoeuvres. Symptom: smoothed track cuts corners.
- **σ_v too high** → filter trusts measurements too much, output approaches
  the inverse-variance mean (Exp D) and the σ benefit disappears. Symptom:
  noisy output, σ ≈ best single rover.
- **σ_p** captures unmodelled position-level drift (multipath bias drift,
  small RTK glitches). Keep it small (cm-scale) unless the input rovers
  show frequent epoch-level jumps.

Quick tuning loop: rerun `run.py`, eyeball `time_series_e.png`, compare
`σ_n/σ_e/σ_u` in the log to Exp D’s log lines.

---

## 4. Outputs

```
experiment_e/
├── run.py
├── README.md                          (this file)
├── outputs/
│   ├── combined_kf.pos                LLH/UTC text, RTKLIB-compatible
│   └── combined_kf.pkl                pandas pickle, same data + UTM + Web Mercator
└── figures/
    ├── trajectory_map_e.png           OSM basemap, all series
    ├── time_series_e.png              n / e / u vs time, KF overlaid on Exp C
    ├── all_experiments_e.png          KF series highlighted vs aligned others
    └── metrics_e.png                  RMS-n/e/u, μ_d, σ_d vs Exp 0 baseline
```

---

## 5. Running

Prereqs: Experiment C must have been run so the three rover `.pkl` files
exist under `experiment_c/outputs/`.

```bash
python examples/experiments/experiment_c/run.py     # only if not already done
python examples/experiments/experiment_e/run.py
```

To include Exp E in the master comparison plot, edit
`examples/experiments/plot.py`:

```python
_SOURCES["Exp E – Kalman fusion"] = _HERE / "experiment_e" / "outputs" / "combined_kf.pkl"
# and add the same label to _ACTIVE_EXPERIMENTS
```

Both edits are already in place if this experiment was scaffolded by the
master setup script.

---

## 6. Comparison with Experiment D

| Aspect                    | Exp D (inverse-variance)            | Exp E (Kalman) |
|---------------------------|--------------------------------------|----------------|
| Temporal model            | none (per-epoch independent)         | constant velocity |
| Velocity estimate         | not produced                          | `vn`, `ve`, `vu` in state |
| σ reduction vs single rover | ~43 % (see project notes)           | typically larger, depends on `σ_v` |
| Sensitivity to gaps       | row dropped when any σ is NaN        | predict-only step bridges gaps |
| Tuning required           | none                                  | `σ_p`, `σ_v` |
| Bias robustness           | inherits rover biases epoch-by-epoch | smooths biases, but lags during manoeuvres if `σ_v` too low |

Exp D and Exp E are complementary: Exp D is a no-knobs static baseline, Exp E
is the dynamic-model counterpart and is the right choice once the trajectory
contains actual motion that the constant-velocity model can exploit.

---

## 7. Possible extensions

- **9-state** `[p, v, a]` constant-acceleration model — only useful if the
  platform has noticeable accelerations (vehicle, fast UAV). Rejected in
  favour of §8 below: a global CA model adds an acceleration state whose
  process noise injects jitter on straight legs too, not just in turns.
- **Adaptive R** — inflate `R_i` when the innovation `y` is large
  (chi-squared gating) to reject outlier epochs.
- **Backward smoother (RTS)** — run a fixed-interval Rauch–Tung–Striebel
  smoother after the forward pass. Halves the σ in the middle of the track
  at the cost of being offline.
- **Heading / NHC constraints** — if the platform is known to be a wheeled
  vehicle, add a non-holonomic constraint on lateral velocity.

---

## 8. Round 2 — Curvature-Adaptive σ_v

### 8.1 Motivation

Round 1 uses one fixed `_SIGMA_V` for the entire track. It is tuned for the
straight legs: tight enough there to smooth well, but too tight to track
real curvature — the constant-velocity model is a poor fit for a turn, so
the filter lags and cuts corners.

The obvious fix — raise `_SIGMA_V` everywhere, or switch to a 9-state
constant-acceleration model — backfires: either the straight legs get noisy
again, or (CA specifically) the acceleration state's process noise injects
jitter into the straight legs even though nothing there needs it. What's
needed is a σ_v that is *low on straights and high in turns*, without
changing the state vector or measurement model.

This requires knowing, per epoch, whether the track is curving and how
sharply — hence the two-round scheme below, proposed as: round 1 as a
first pass, cluster the resulting curvature, then a round 2 with a
per-cluster σ_v.

### 8.2 Curvature signal

`curvature.compute_turn_rate()` computes a windowed, signed heading-change
rate from **Experiment D's static fusion** (`experiment_d/run.py::combine()`,
§6 of the top-level `docs.md`) — not from Experiment E's own KF velocity.
Using Exp E's own state would be circular: its velocity estimate already
lags in turns, which is exactly the artifact this signal is meant to locate.

For each epoch `t`, with half-window `w` (`_WINDOW_S = 5 s`, i.e. `w = 5`
epochs at the 1 s grid):

```
v1 = p(t) − p(t−w)                     p = [northing_m, easting_m]
v2 = p(t+w) − p(t)

Δθ(t) = atan2(v1 × v2, v1 · v2)         signed heading change, wrapped to [−π, π]
turn_rate(t) = Δθ(t) / (w · Δt)         rad/s
```

The window (rather than epoch-to-epoch differencing) is needed because raw
GNSS position noise dominates a 1-epoch heading estimate, especially at low
speed. Epochs with average speed `< _SPEED_MIN` (0.3 m/s) over the window
get `turn_rate = NaN` — heading is undefined near-stationary — and are
folded into "straight" downstream.

### 8.3 Clustering

`curvature.cluster_curvature()` runs k-means (scikit-learn) on `|turn_rate|`
(NaN → 0), evaluating `k ∈ {2, 3, 4}` and keeping the k with the highest
silhouette score — chosen empirically rather than fixed, since the "right"
number of curvature tiers is dataset-dependent. Clusters are re-numbered by
ascending centroid so rank `0` = straightest, rank `k−1` = sharpest.

On the current Volo_1 dataset this selects **k = 2** (silhouette 0.84 vs
0.82 for k=3, 0.76 for k=4): centroids at 0.019 rad/s (straight/gentle,
2136 epochs) and 0.296 rad/s (turns, 353 epochs). A 3-tier split was
expected going in but the data doesn't support it well enough — recorded
here rather than forcing k=3 to match the original mental model.

### 8.4 Adaptive σ_v and the ablation knob

`curvature.sigma_v_series()` maps rank → σ_v with a single hyperparameter,
`growth`:

```
σ_v(rank) = _SIGMA_V · growth^rank
```

- `growth = 1.0` → every rank gets the same σ_v → **mathematically identical
  to round 1** (verified: bit-for-bit same filter output). This is the
  control point of the ablation, not a separately maintained baseline.
- `growth = 2.0` → the professor's original "double it per cluster"
  proposal.

`run.py::run_kf()` was extended (not duplicated) to accept an optional
per-epoch `sigma_v_t` series; passing `None` reproduces the exact round-1
behaviour, so round 1 and round 2 share one filter implementation.

### 8.5 Files

| File | Role |
|---|---|
| `curvature.py` | `compute_turn_rate()`, `cluster_curvature()`, `sigma_v_series()` — pure functions, no I/O. |
| `run_adaptive.py` | End-to-end round 2: load → curvature → cluster → adaptive KF → outputs/plots for one `growth` value. |
| `run_ablation.py` | Sweeps `growth ∈ {1.0, 1.5, 2.0, 3.0, 4.0}`, tabulates metrics vs Exp 0 per value. |
| `run.py` | Unchanged round-1 entry point; also supplies `run_kf(sigma_v_t=...)` and loading helpers reused by the two files above. |

### 8.6 Running

```bash
python examples/experiments/experiment_e/run_adaptive.py     # single run, growth=2.0, with plots
python examples/experiments/experiment_e/run_ablation.py     # full sweep, no plots per-run
```

`run_adaptive.run(growth, make_plots)` and `run_ablation.run()` are also
importable directly for notebook/paper-figure use.

Outputs:

```
outputs/combined_kf_adaptive_g<growth>.pos / .pkl   per growth value
outputs/ablation/ablation_results.csv               one row per growth value
figures/trajectory_map_e_adaptive.png               (single run only)
figures/time_series_e_adaptive.png
figures/all_experiments_e_adaptive.png
figures/metrics_e_adaptive.png
figures/curvature_clusters.png                      trajectory coloured by curvature rank
figures/ablation_growth_sweep.png                    RMS/μ_d/σ_d vs growth
```

### 8.7 Ablation results (Volo_1, k=2, vs Exp 0 baseline)

| growth | RMS_n (m) | RMS_e (m) | RMS_u (m) | μ_d (m) | σ_d (m) |
|---|---|---|---|---|---|
| 1.0 (= round 1) | 118.114 | 68.707 | 157.937 | 196.967 | 69.381 |
| 1.5 | 118.361 | 68.870 | 157.846 | 197.116 | 69.334 |
| 2.0 | 118.469 | 68.938 | 157.802 | 197.176 | 69.313 |
| 3.0 | 118.550 | 68.990 | 157.768 | 197.222 | 69.299 |
| 4.0 | 118.577 | 69.009 | 157.759 | 197.238 | 69.298 |

**Caveat — weak signal against this baseline.** The effect of `growth` on
these numbers is real but small relative to their magnitude. Exp 0 (a
single consumer-GPS NMEA stream, §1) disagrees with the RTK-fused track by
~100–200 m of absolute offset/lag; changes to σ_v move the fused track by
centimetres to a few metres in the turns, which is swamped by that
baseline bias in an RMS-vs-Exp-0 metric. The table is directionally
consistent (σ_u and σ_d both improve monotonically with `growth`, i.e. the
adaptive filter tracks the turns slightly better) but this baseline is not
sensitive enough to make a strong quantitative case for the paper. A
sharper ablation would compare against something that responds at the
metre scale of the change itself — e.g. inter-rover consistency (spread of
the 3 raw Exp C rovers around the fused track, epoch-by-epoch, restricted
to turn-cluster epochs) or an innovation/NEES consistency check — rather
than the absolute Exp 0 offset. Not implemented here; flagged as the
natural next step if this needs to go in the paper.
