# GNSSPos

Post-processing tool for multi-receiver GNSS data. Combines observations from low-cost uBlox EVK-M8T receivers with IGS precise products and an optional high-accuracy reference station, then produces position time-series, accuracy metrics, and trajectory maps.

## Features

- Download SP3, CLK, NAV, and ionosphere files from NASA CDDIS (IGS portal)
- Run RTKLIB `rnx2rtkp` via subprocess (wine on Linux for `.exe` binaries)
- Parse NMEA GGA sentences as a baseline trajectory (Experiment 0)
- Time-series alignment with weighted linear interpolation for gap filling
- Accuracy metrics: RMS, mean 3D distance (μ_d), standard deviation (σ_d)
- Trajectory plots with OpenStreetMap basemap (contextily)
- Coordinate conversions: WGS84 → UTM Zone 32N (EPSG:32632) → Web Mercator (EPSG:3857)
- GUI (PyQt6) and CLI interfaces

## Project structure

```
GNSSPos/
├── main.py                         # Entry point (CLI / GUI)
├── gnsspos/
│   ├── gnsspos.py                  # Core orchestrator class
│   ├── rover.py                    # Rover dataclass
│   ├── processing/                 # Post-processing pipeline
│   │   ├── pos_reader.py           # RTKLIB .pos file parser
│   │   ├── nmea_parser.py          # NMEA GGA → DataFrame
│   │   ├── coordinate.py           # WGS84 / UTM32 / Web Mercator
│   │   ├── time_alignment.py       # Common-window alignment + gap fill
│   │   ├── metrics.py              # RMS, μ_d, σ_d
│   │   └── plotter.py              # Matplotlib / contextily figures
│   ├── service/
│   │   ├── rtk_post_runner.py      # rnx2rtkp subprocess wrapper
│   │   └── igs_data_downloader.py  # NASA CDDIS downloader
│   └── ui/
│       ├── gui.py                  # PyQt6 GUI
│       └── cli.py                  # CLI (stub)
├── examples/
│   └── experiments/
│       ├── experiment_0/run.py     # NMEA GGA baseline
│       ├── experiment_a/run.py     # High-cost rover (Leica 1200), kinematic
│       ├── experiment_b/run.py     # Low-cost rovers, standalone (no base)
│       ├── experiment_c/run.py     # Low-cost rovers, kinematic with base
│       ├── experiment_d/run.py     # Placeholder
│       └── plot.py                 # Master comparison plot
└── rtklib_2.4.2/                   # RTKLIB binaries (Windows .exe, run via wine)
```

## Requirements

Python ≥ 3.11. Install dependencies:

```bash
pip install -r requirements.txt
```

System dependency: `wine` (required to run the RTKLIB `.exe` binaries on Linux/macOS).

```bash
# Arch Linux
sudo pacman -S wine

# Ubuntu/Debian
sudo apt install wine
```

## Configuration

Copy `.env_template` to `.env` and fill in your NASA Earthdata credentials:

```
NASA_USER=your_earthdata_username
NASA_PWD=your_earthdata_password
RNX2RTKP_PATH=/absolute/path/to/rtklib_2.4.2/bin/rnx2rtkp.exe
```

Credentials for NASA CDDIS: register at <https://urs.earthdata.nasa.gov/>.

## Running experiments

All experiments live under `examples/experiments/`. Each `run.py` script:
- Checks whether output `.pos` files already exist and skips `rnx2rtkp` if so
- Logs the full `rnx2rtkp` command before executing it
- Saves results as both CSV (`.pos`) and pickle (`.pkl`)

> **Confirm the rnx2rtkp command before running.** Each script prints the
> exact command it will execute. Verify paths and options before proceeding.

### Experiment 0 – NMEA GGA baseline

Parses NMEA GGA sentences from a hand-held or smartphone receiver. No RTKLIB
call needed.

```bash
python examples/experiments/experiment_0/run.py
# or with a custom file:
python examples/experiments/experiment_0/run.py --nmea /path/to/file.txt
```

### Experiment A – High-cost rover (Leica 1200), kinematic

Processes the dual-frequency Leica 1200 rover against the Leica base station
in kinematic mode using precise SP3 + CLK products.

```bash
python examples/experiments/experiment_a/run.py
```

Approximate `rnx2rtkp` command (printed by the script before execution):

```
wine rtklib_2.4.2/bin/rnx2rtkp.exe \
  -k examples/experiments/leica_kinematic.conf \
  -o examples/experiments/experiment_a/outputs/45601780.pos \
  examples/raw_data/.../1200_rover_rinex/45601780.23o \
  examples/raw_data/.../1200_base_rinex/BASE1780.23o \
  examples/raw_data/.../1200_base_rinex/BASE1780.23n \
  examples/experiments/IGS0OPSFIN_20231780000_01D_15M_ORB.SP3 \
  examples/experiments/IGS0OPSFIN_20231780000_01D_05M_CLK.CLK
```

### Experiment B – Low-cost rovers, standalone

Each uBlox EVK-M8T receiver processed individually with precise SP3 + CLK
(no base station).

```bash
python examples/experiments/experiment_b/run.py
```

### Experiment C – Low-cost rovers, kinematic with base

Same receivers processed in kinematic RTK mode against the Leica 1200 base
station.

```bash
python examples/experiments/experiment_c/run.py
```

### Experiment D – Inverse-variance weighted combination

Fuses the three Experiment C rover solutions epoch-by-epoch with per-component
inverse-variance weighting. No temporal model.

```bash
python examples/experiments/experiment_d/run.py
```

### Experiment E – Kalman filter fusion

Constant-velocity Kalman filter that fuses the three Experiment C rover
solutions with a dynamic model. Adds temporal smoothing and a velocity
estimate. See `examples/experiments/experiment_e/README.md` for the full
algorithm description and tuning notes.

```bash
python examples/experiments/experiment_e/run.py
```

## Generating plots

After running the desired experiments:

```bash
python examples/experiments/plot.py
```

Figures are saved to `examples/experiments/figures/`:
- `trajectory_map.png` – 2D trajectory on OSM
- `time_series.png` – easting, northing, height vs time
- `metrics.png` – RMS, μ_d, σ_d vs baseline
- `all_experiments.png` – all series overlaid

## Switching the baseline

The reference trajectory used for accuracy metrics (RMS, μ_d, σ_d) and overlay
highlighting is controlled by `_REFERENCE_LABEL` in
`examples/experiments/plot.py`. All other active experiments are aligned to
the reference window and compared epoch-by-epoch against it.

**Current baseline:** Experiment 0 — NMEA GGA from the uBlox `LocationAPI` log
(`Exp 0 – NMEA COM23`). It is the longest series (~9954 epochs, Q=5) and
covers the full session 09:05:13 → 11:56:53.

**Switching to Experiment A (Leica 1200 kinematic)** as the reference for all
other experiments requires two edits in `examples/experiments/plot.py`, since
Exp A is currently *excluded* from the active set.

### Step 1 — Generate the Exp A outputs (if missing)

The Leica 1200 kinematic solution must already exist on disk:

```bash
python examples/experiments/experiment_a/run.py
```

This writes `examples/experiments/experiment_a/outputs/45601780.pos`, which is
the file referenced by the `"Exp A – Leica 1200"` entry in `_SOURCES`.

### Step 2 — Activate Exp A in `_ACTIVE_EXPERIMENTS`

The reference label **must** be present in `_ACTIVE_EXPERIMENTS`, otherwise
the experiment is filtered out before alignment and the metrics block is
silently skipped. Uncomment the corresponding line:

```python
_ACTIVE_EXPERIMENTS: set[str] = {
    "Exp 0 – NMEA COM23",
    "Exp A – Leica 1200",          # <-- uncomment this line
    # "Exp B – COM23 single",
    # "Exp B – COM24 single",
    # "Exp B – COM25 single",
    "Exp C – COM23 kinematic",
    "Exp C – COM24 kinematic",
    "Exp C – COM25 kinematic",
    "Exp D – Combined",
}
```

### Step 3 — Change `_REFERENCE_LABEL`

```python
# Before:
_REFERENCE_LABEL = "Exp 0 – NMEA COM23"
# After:
_REFERENCE_LABEL = "Exp A – Leica 1200"
```

### Step 4 — Re-run the master plot

```bash
python examples/experiments/plot.py
```

Figures in `examples/experiments/figures/` are regenerated with Exp A as the
new reference.

### Important caveat — temporal overlap

The Exp A solution only covers ~308 epochs in the ~11:58 window (Leica raw
data is much shorter than the uBlox session). When Exp A is the reference,
`align_series()` in `plot.py` restricts every other experiment to that short
window via:

```python
ref_start = series[_REFERENCE_LABEL].index.min()
ref_end   = series[_REFERENCE_LABEL].index.max()
```

Series that do not overlap the Exp A window are skipped with a warning:

```
Skipping '<label>' from alignment: no overlap with reference window <start> → <end>
```

Exp 0 (NMEA) starts at 09:05 and ends at 11:56:53, so it has **no overlap**
with the Exp A window and will be dropped from the metrics figure. Exp C and
Exp D, which run from ~10:15 to ~11:58, overlap the Exp A window and are
retained.

### Reverting

Re-comment the `"Exp A – Leica 1200"` line and restore
`_REFERENCE_LABEL = "Exp 0 – NMEA COM23"`. Any key present in `_SOURCES` can
be used as a reference, provided it is also listed in `_ACTIVE_EXPERIMENTS`.

## Architecture notes

### Coordinate pipeline

```
RTKLIB .pos  →  read_pos_file()   →  lat/lon/h  →  UTM32N (EPSG:32632)
NMEA GGA     →  parse_nmea_gga()  →             →  Web Mercator (EPSG:3857)
```

### File priority for IGS products

When input files are provided, `rnx2rtkp` config selects:
1. SP3 + CLK (precise final orbits and clocks) — highest quality
2. Final NAV — if SP3/CLK unavailable
3. Broadcast NAV (`brdc`) — fallback

When SP3 + CLK are used, do **not** pass a NAV file (redundant and can confuse
the solver).

### Future: nanobind integration

The current architecture calls `rnx2rtkp` via `subprocess`. A planned future
version will use [nanobind](https://github.com/wjakob/nanobind) to bind
RTKLIB C functions directly from Python, eliminating the subprocess overhead
and enabling tighter integration. `RTKPOSTRunner` in
`gnsspos/service/rtk_post_runner.py` is the abstraction layer that will be
updated for that transition.

## GUI

```bash
python main.py --gui
```

The GUI requires PyQt6. It provides a calendar-based date picker, rover and
base-station file selectors, one-click IGS data download, and a RUN button
that invokes the full processing pipeline.
