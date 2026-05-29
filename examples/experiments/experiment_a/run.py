#!/usr/bin/env python3
"""
Experiment A – Leica 1200 high-cost rover, RTK kinematic with Leica base.

Inputs
------
Rover OBS : raw_data/GPS_Sassuolo_Forli/1200_rover_rinex/45601780.23o
Base OBS  : raw_data/GPS_Sassuolo_Forli/1200_base_rinex/BASE1780.23o
NAV       : experiments/brdc1780.23n           (IGS broadcast, shared with B/C/D)
SP3       : experiments/IGS0OPSFIN_*_ORB.SP3   (IGS Final precise orbits)
CLK       : experiments/IGS0OPSFIN_*_CLK.CLK   (IGS Final precise clocks)
Config    : experiments/leica_kinematic.conf   (pos1-sateph=precise)

Output    : outputs/45601780.pos

All IGS products are downloaded automatically from NASA CDDIS if missing
(requires NASA_USER and NASA_PWD env vars).
"""
import logging
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_HERE.parent))   # so igs_products is importable

from gnsspos.processing.pos_reader import read_pos_file
from gnsspos.processing.coordinate import add_utm32_columns, add_web_mercator_columns
from igs_products import ensure_igs_products

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_EXPERIMENTS = _HERE.parent
_RAW_DATA    = _ROOT / "examples" / "raw_data" / "GPS_Sassuolo_Forli"
_RTKLIB      = _EXPERIMENTS / "rnx2rtkp"

_ROVER_OBS = _RAW_DATA / "1200_rover_rinex" / "45601780.23o"
_BASE_OBS  = _RAW_DATA / "1200_base_rinex"  / "BASE1780.23o"
_CONF      = _EXPERIMENTS / "leica_kinematic.conf"

_OUTPUTS = _HERE / "outputs"
_OUTPUT  = _OUTPUTS / "45601780.pos"
_PKL     = _OUTPUTS / "45601780.pkl"


def build_cmd(sp3: Path, clk: Path, nav: Path) -> list[str]:
    cmd = [str(_RTKLIB)]
    cmd += ["-k", str(_CONF)]
    cmd += ["-o", str(_OUTPUT)]
    cmd += [str(_ROVER_OBS), str(_BASE_OBS), str(nav), str(sp3), str(clk)]
    return cmd


def run() -> None:
    _OUTPUTS.mkdir(parents=True, exist_ok=True)

    products = ensure_igs_products(_EXPERIMENTS)
    sp3, clk, nav = products["sp3"], products["clk"], products["nav"]

    if _OUTPUT.exists():
        logger.info("Output already exists, skipping rnx2rtkp: %s", _OUTPUT)
    else:
        cmd = build_cmd(sp3, clk, nav)
        logger.info("Running: %s", " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(_HERE))
        if result.returncode != 0:
            logger.error("rnx2rtkp failed with code %d", result.returncode)
            sys.exit(result.returncode)

    df = read_pos_file(_OUTPUT)
    df = add_utm32_columns(df)
    df = add_web_mercator_columns(df)

    logger.info(
        "Loaded %d epochs: %s → %s",
        len(df), df.index[0], df.index[-1],
    )
    logger.info("Q distribution: %s", df["Q"].value_counts().to_dict())

    df.to_pickle(_PKL)
    logger.info("Saved pickle → %s", _PKL)


if __name__ == "__main__":
    run()
