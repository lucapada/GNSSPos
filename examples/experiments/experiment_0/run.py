#!/usr/bin/env python3
"""
Experiment 0 – NMEA GGA baseline.

Parses NMEA GGA sentences from LocationAPI_230627_090521.ubx into a
.pos-compatible DataFrame and saves the result as:
  outputs/COM23_nmea.pos  (CSV)
  outputs/COM23_nmea.pkl  (pickle)

Usage:
    python run.py [--nmea PATH_TO_NMEA_FILE]
"""
import argparse
import logging
import sys
from datetime import date
from pathlib import Path

# Allow imports from the project root regardless of working directory.
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]          # GNSSPos/
sys.path.insert(0, str(_ROOT))

from gnsspos.processing.nmea_parser import parse_nmea_gga
from gnsspos.processing.coordinate import add_utm32_columns, add_web_mercator_columns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Default paths
_RAW_DATA = _ROOT / "examples" / "raw_data" / "GPS_Sassuolo_Forli" / "Volo_1"
_DEFAULT_NMEA = _RAW_DATA / "LocationAPI_230627_090521.ubx"
_OUTPUTS = _HERE / "outputs"

# Date encoded in filename: 230627 = 2023-06-27.
_ACQ_DATE = date(2023, 6, 27)


def run(nmea_path: Path = _DEFAULT_NMEA) -> None:
    _OUTPUTS.mkdir(parents=True, exist_ok=True)
    out_pos = _OUTPUTS / "COM23_nmea.pos"
    out_pkl = _OUTPUTS / "COM23_nmea.pkl"

    logger.info("Parsing NMEA GGA from: %s", nmea_path)
    df = parse_nmea_gga(nmea_path, acq_date=_ACQ_DATE)

    if df.empty:
        logger.error("No GGA sentences parsed. Aborting.")
        sys.exit(1)

    df = add_utm32_columns(df)
    df = add_web_mercator_columns(df)

    logger.info(
        "Parsed %d epochs: %s → %s",
        len(df), df.index[0], df.index[-1],
    )
    logger.info(
        "Lat range: [%.6f, %.6f]  Lon range: [%.6f, %.6f]",
        df["latitude_deg"].min(), df["latitude_deg"].max(),
        df["longitude_deg"].min(), df["longitude_deg"].max(),
    )

    # Save as CSV (.pos) and pickle
    df.to_csv(out_pos)
    df.to_pickle(out_pkl)
    logger.info("Saved → %s", out_pos)
    logger.info("Saved → %s", out_pkl)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experiment 0 – NMEA GGA baseline")
    parser.add_argument(
        "--nmea",
        type=Path,
        default=_DEFAULT_NMEA,
        help=f"Path to NMEA GGA text file (default: {_DEFAULT_NMEA})",
    )
    args = parser.parse_args()
    run(nmea_path=args.nmea)
