# Changelog

All notable changes to GNSSPos follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [2.4.0] – 2026-05-16

### Fixed

- `gnsspos/service/igs_data_downloader.py` — `downloadBroadcastEphemeris`
  corrected URL patterns for multi-GNSS combined NAV files.  Directory is
  `daily/YYYY/DDD/YYp/` (not `YYb/`) and analysis-centre codes are `IGS`/`DLR`
  (not `DLF`).  New priority order:
  1. `daily/YYYY/DDD/YYp/BRDC00IGS_R_YYYYDDD0000_01D_MN.rnx.gz` — IGS combined
     multi-GNSS RINEX 3 (best; ~12 MB uncompressed for DOY 178/2023)
  2. `daily/YYYY/DDD/YYp/BRDM00DLR_S_YYYYDDD0000_01D_MN.rnx.gz` — DLR merged
     multi-GNSS RINEX 3
  3. `daily/YYYY/DDD/YYn/brdcDDD0.YYn.gz` — GPS-only RINEX 2 fallback
  4. `daily/YYYY/brdc/brdcDDD0.YYn.gz` — GPS-only alternate path
  The old attempt at `YYb/BRDM00DLF_S_*` always 404-ed because that directory
  does not exist on CDDIS for any tested date.
- `examples/experiments/igs_products.py` — `_NAV_CANDIDATES` updated to match
  real CDDIS filenames: `BRDC00IGS_R_20231780000_01D_MN.rnx` →
  `BRDM00DLR_S_20231780000_01D_MN.rnx` → `brdc1780.23n`.
- `.gitignore` — added `examples/experiments/BRDC*.rnx` and
  `examples/experiments/BRDM*.rnx` to exclude downloaded multi-GNSS NAV files.
- All experiments re-run with `BRDC00IGS_R_20231780000_01D_MN.rnx` (multi-GNSS
  RINEX 3 including GPS + GLONASS + Galileo + BeiDou) replacing the old GPS-only
  `brdc1780.23n`.

---

## [2.3.0] – 2026-05-15

### Changed

- `gnsspos/service/igs_data_downloader.py` — `downloadBroadcastEphemeris` now
  tries products in priority order (best → fallback):
  1. RINEX 3 multi-GNSS BRDM (`daily/YYYY/DDD/YYb/BRDM00DLF_S_*_MN.rnx.gz`) — post-2020
  2. RINEX 2 multi-GNSS mixed (`daily/YYYY/DDD/YYp/brdmDDD0.YYp.gz`)
  3. RINEX 2 GPS-only (`daily/YYYY/DDD/YYn/brdcDDD0.YYn.gz`)
  4. RINEX 2 GPS-only alternate path (`daily/YYYY/brdc/brdcDDD0.YYn.gz`)
  For DOY 178/2023, CDDIS does not host BRDM or brdm; falls back to `brdc1780.23n`.
- `gnsspos/service/igs_data_downloader.py` — Fixed `DDD` formatting to
  `{DDD:03d}` (zero-padded 3 digits) in all URL f-strings — was broken for DOY < 100.
- `gnsspos/service/igs_data_downloader.py` — Fixed day-of-GPS-week in old-format
  SP3/CLK URLs: `D_iso` (0=Mon) replaced with `D_us` (0=Sun), matching GPS convention.
- `examples/experiments/igs_products.py` — NAV detection uses `_NAV_CANDIDATES`
  priority list (BRDM → brdm → brdc); returns whichever is found/downloaded.

---

## [2.2.0] – 2026-05-15

### Added

- `examples/experiments/igs_products.py` — shared IGS product manager for the
  GPS_Sassuolo_Forlì campaign. All experiment `run.py` scripts call
  `ensure_igs_products()` at startup; missing files (SP3, CLK, NAV, INX) are
  downloaded automatically from NASA CDDIS before rnx2rtkp runs.
- `examples/experiments/brdc1780.23n` — IGS combined broadcast NAV (DOY 178,
  2023) downloaded from NASA CDDIS. Shared across all experiments (A/B/C) as
  the single authoritative Klobuchar ionosphere source.

### Changed

- `examples/experiments/experiment_a/run.py` — now uses shared IGS SP3 + CLK +
  broadcast NAV (`brdc1780.23n`) instead of the base station's `BASE1780.23n`.
- `examples/experiments/experiment_b/run.py`,
  `examples/experiments/experiment_c/run.py` — switched from per-rover `.nav`
  files to the shared `brdc1780.23n`.
- `examples/experiments/experiment_0/run.py` — NMEA source changed from
  `COM23_NMEA.txt` to `LocationAPI_230627_090521.ubx` (9954 GGA epochs,
  09:05:13 → 11:56:53 UTC).
- `examples/experiments/leica_kinematic.conf` — `pos1-sateph` changed from
  `brdc` to `precise`; `pos1-tidecorr` fixed from `0` to `off` (SWTOPT option).
- `gnsspos/processing/nmea_parser.py` — parser now handles receivers that emit
  binary-prefixed lines (uses `re.search` instead of `re.match`) and tolerates
  empty num_satellites, HDOP, and geoid-separation fields.
- `gnsspos/processing/time_alignment.py` — `fill_gaps` accepts optional
  `target_index` so all series in `align_series` land on an identical datetime
  grid. Sub-second timestamps (NMEA) are rounded to the target frequency;
  duplicate timestamps from rounding are collapsed. `align_series` floors
  t_start/t_end to the target freq and passes a shared `DatetimeIndex` to every
  `fill_gaps` call — eliminates one-epoch misalignment when mixing NMEA
  (sub-second) and RTKLIB (integer-second) data.

### Fixed

- `Dockerfile` — removed `COPY main.py .` (entry point deleted in v2.2.0 refactor).
- `gnsspos/` — removed virtualenv artifacts (`bin/`, `lib/`, `share/`,
  `CACHEDIR.TAG`, `pyvenv.cfg`, `.gitignore`) that were mistakenly committed
  inside the Python package directory.
- v1 entry points removed: `gnsspos/ui/`, `gnsspos/gnsspos.py`, `gnsspos/rover.py`,
  `main.py`. Active pipeline uses `gnsspos/processing/` and
  `gnsspos/service/` directly from the experiment scripts.
- `.gitignore` — added `*.atx` (antenna calibration files not needed at project
  root) and `examples/experiments/brdc*.23n` (downloaded broadcast NAV files).

---

## [2.1.0] – 2026-05-15

### Added

- `examples/experiments/experiment_d/run.py` — implemented Experiment D:
  inverse-variance weighted combination of the three Experiment C rover solutions
  (COM23, COM24, COM25). Per-epoch algorithm:
  - Diagonal weight matrices `W_i = diag(w_in, w_ie, w_iu)` with
    `w_{ij} = (1/σ_{ji}²) / Σ_k(1/σ_{jk}²)`
  - Combined position `x̂ = Σ_i W_i x_i` in UTM32N (northing, easting, height)
  - Combined covariance `Ĉ = Σ_i W_i C_i W_i^T`; off-diagonal elements scaled
    ×0.9 until `det(Ĉ) > 0` (positive-definiteness regularisation)
  - TODO stub for eigenvalue-based regularisation (Higham 1988) in module docstring
  - Outputs `combined.pos` (RTKLIB LLH/UTC format) and `combined.pkl`
  - Generates four figures: trajectory map, time series, overlay, metrics vs Exp 0
  - Observed σ reduction ≈ 43% across all components (3 independent L1 receivers)

- `examples/experiments/plot.py` — `_ACTIVE_EXPERIMENTS` set: control which
  experiments appear in all plots by commenting/uncommenting keys in code.
  Exp D added to `_SOURCES`.

### Changed

- `examples/experiments/experiment_a/run.py`,
  `examples/experiments/experiment_b/run.py`,
  `examples/experiments/experiment_c/run.py` — switched from
  `wine rtklib_2.4.2/bin/rnx2rtkp.exe` to native Linux binary
  `examples/experiments/rnx2rtkp` (RTKLIB EX 2.5.0). The RTKLIB 2.4.2 Windows
  executable cannot read RINEX 3.04 observation files (returns "no obs data");
  the native EX 2.5.0 binary handles them correctly.

### Fixed

- `examples/experiments/ublox_kinematic.conf` — `pos1-tidecorr` changed from
  `0` to `off`; RTKLIB config parser expects `on`/`off` for this switch option
  (`SWTOPT` in `options.c:64`), not a bare integer.

---

## [2.0.0] – 2026-05-15

Complete architectural overhaul. Introduced a dedicated post-processing pipeline,
fixed the RTKLIB subprocess integration, and restructured all experiment scripts.

### Added

- `gnsspos/processing/` package with six new modules:
  - `pos_reader.py` — parses RTKLIB `.pos` files (LLH/UTC) into DataFrames
  - `nmea_parser.py` — parses NMEA GGA sentences (Experiment 0 baseline)
  - `coordinate.py` — WGS84 → UTM Zone 32N (EPSG:32632) → Web Mercator (EPSG:3857)
  - `time_alignment.py` — aligns series to common time window; fills gaps with
    linear interpolation (position) and variance propagation (covariance: W₁²C₁ + W₂²C₂)
  - `metrics.py` — cumulative RMS per axis, mean 3D distance (μ_d), σ_d vs reference
  - `plotter.py` — trajectory map (OSM via contextily), time-series panels, metrics
    panels, all-experiments overlay
- `examples/experiments/experiment_0/run.py` — new Experiment 0: parse NMEA GGA
  from a LocationAPI / hand-held receiver file; no RTKLIB call required
- `CHANGELOG.md` (this file)
- `README.md` comprehensive guide covering installation, experiments, baseline
  switching, and architecture roadmap

### Changed

- `gnsspos/service/rtk_post_runner.py`:
  - `out-solformat` corrected from `xyz` → `llh`
  - `out-timesys` corrected from `gpst` → `utc`
  - `wine` prefix now detected from `.exe` file extension (not OS type)
  - Removed `os.chdir()` calls; subprocess uses `cwd=` parameter instead
  - Added `run_rnx2rtkp()` method (returns stdout/stderr; raises on non-zero exit)
  - `runRtkPost()` kept as backward-compatible alias
- `examples/experiments/experiment_a/run.py` — rewritten: absolute paths from
  `__file__`, skip-if-exists logic, pickle output
- `examples/experiments/experiment_b/run.py` — rewritten: per-rover loop, SP3+CLK,
  skip-if-exists, pickle output
- `examples/experiments/experiment_c/run.py` — rewritten: per-rover loop, Leica base,
  SP3+CLK, skip-if-exists, pickle output
- `examples/experiments/experiment_d/run.py` — converted to documented placeholder
  (`NotImplementedError` with algorithm sketch in docstring)
- `examples/experiments/plot.py` — full rewrite: loads all experiments, aligns to
  common 1-second window, computes metrics vs Experiment 0 baseline, generates
  four figures under `figures/`

### Fixed

- `examples/experiments/plot.py` now loads Experiment 0 from its pickle (pandas
  CSV format) rather than attempting to parse it as a RTKLIB `.pos` file
- Metrics reference switched from Experiment A (Leica 1200) to Experiment 0 (NMEA)
  as the correct current baseline; Experiment A data for Volo_1 covers only ~30 s
  with no overlap with the other experiments

---

## [1.5.0] – 2025-12-07

### Added

- GUI: distance and threshold configuration popups
- `processBase` and `processRover` in `RTKPOSTRunner` using `.conf` files
- IGS downloader: precise orbit (SP3), clock (CLK), ionosphere (IONEX),
  and troposphere (TRO) products from NASA CDDIS
- Preliminary experiment scripts (`experiment_b/run.py`, `experiment_c/run.py`)

### Changed

- Working directory validated before processing (must be empty or new)
- Rover names auto-generated (`Rover 1`, `Rover 2`, …)

---

## [1.0.0] – 2025-11-01 (estimated)

Initial public release.

### Added

- `algoritmo.py`: prototype combining multiple `.pos` files with inverse-variance
  weighted averaging and linear gap interpolation
- `Rover` class with `obs_file` / `pos_file` attributes
- Basic PyQt6 GUI skeleton
- `IGSDataDownloader` for NASA CDDIS authentication and file retrieval
- `RTKPOSTRunner` subprocess wrapper for `rnx2rtkp`
