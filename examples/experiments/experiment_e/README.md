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
  platform has noticeable accelerations (vehicle, fast UAV).
- **Adaptive R** — inflate `R_i` when the innovation `y` is large
  (chi-squared gating) to reject outlier epochs.
- **Backward smoother (RTS)** — run a fixed-interval Rauch–Tung–Striebel
  smoother after the forward pass. Halves the σ in the middle of the track
  at the cost of being offline.
- **Heading / NHC constraints** — if the platform is known to be a wheeled
  vehicle, add a non-holonomic constraint on lateral velocity.
