#!/usr/bin/env python3
"""
Experiment B – uBlox EVK-M8T rovers, standalone positioning with precise ephemeris.

Each rover (COM23, COM24, COM25) is processed in standalone (single) mode
using the shared IGS precise SP3 + CLK + broadcast NAV files.

Inputs (per rover)
------------------
Rover OBS : raw_data/GPS_Sassuolo_Forli/Volo_1/COMxx_rover.obs
NAV       : experiments/brdc1780.23n           (IGS broadcast, shared with A/C/D)
SP3       : experiments/IGS0OPSFIN_*_ORB.SP3   (IGS Final precise orbits)
CLK       : experiments/IGS0OPSFIN_*_CLK.CLK   (IGS Final precise clocks)
Config    : experiments/ublox_single.conf

Outputs   : outputs/COM23_rover.pos, outputs/COM24_rover.pos, outputs/COM25_rover.pos

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
_RAW_DATA    = _ROOT / "examples" / "raw_data" / "GPS_Sassuolo_Forli" / "Volo_1"
_RTKLIB      = _EXPERIMENTS / "rnx2rtkp"
_CONF        = _EXPERIMENTS / "ublox_single.conf"

_ROVERS  = ["COM23", "COM24", "COM25"]
_OUTPUTS = _HERE / "outputs"


def build_cmd(rover: str, sp3: Path, clk: Path, nav: Path) -> list[str]:
    obs = _RAW_DATA / f"{rover}_rover.obs"
    out = _OUTPUTS / f"{rover}_rover.pos"
    cmd = [str(_RTKLIB)]
    cmd += ["-k", str(_CONF)]
    cmd += ["-o", str(out)]
    cmd += [str(obs), str(nav), str(sp3), str(clk)]
    return cmd


def run() -> None:
    _OUTPUTS.mkdir(parents=True, exist_ok=True)

    products = ensure_igs_products(_EXPERIMENTS)
    sp3, clk, nav = products["sp3"], products["clk"], products["nav"]

    results: dict[str, object] = {}
    for rover in _ROVERS:
        out = _OUTPUTS / f"{rover}_rover.pos"
        pkl = _OUTPUTS / f"{rover}_rover.pkl"

        if out.exists():
            logger.info("[%s] Output already exists, skipping rnx2rtkp.", rover)
        else:
            cmd = build_cmd(rover, sp3, clk, nav)
            logger.info("[%s] Running: %s", rover, " ".join(cmd))
            result = subprocess.run(cmd, cwd=str(_HERE))
            if result.returncode != 0:
                logger.error("[%s] rnx2rtkp failed with code %d", rover, result.returncode)
                continue

        df = read_pos_file(out)
        df = add_utm32_columns(df)
        df = add_web_mercator_columns(df)
        df.to_pickle(pkl)

        logger.info(
            "[%s] Loaded %d epochs: %s → %s | Q: %s",
            rover, len(df), df.index[0], df.index[-1],
            df["Q"].value_counts().to_dict(),
        )
        results[rover] = df

    return results


if __name__ == "__main__":
    run()
