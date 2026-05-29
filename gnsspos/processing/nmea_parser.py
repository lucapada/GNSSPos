"""Parse NMEA GGA sentences into a .pos-compatible DataFrame."""
from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from gnsspos.processing.pos_reader import POS_COLUMNS

logger = logging.getLogger(__name__)

# GGA quality flag → RTKLIB Q code
_GGA_QUALITY_MAP: dict[int, int] = {
    1: 5,   # GPS SPS       → single
    2: 4,   # DGPS          → dgps
    4: 1,   # RTK fixed     → fix
    5: 2,   # RTK float     → float
}

# Matches $GPGGA, $GNGGA, $GLGGA, $GAGGA, etc.
# Some receivers (e.g. LocationAPI) omit num_satellites, HDOP, or geoid separation.
_GGA_RE = re.compile(
    r"\$(GP|GN|GL|GA)GGA,"    # talker + GGA
    r"(\d{6}(?:\.\d+)?),"     # HHMMSS[.ss]
    r"(\d+\.\d+),([NS]),"     # lat, hemisphere
    r"(\d+\.\d+),([EW]),"     # lon, hemisphere
    r"(\d+),"                 # fix quality
    r"(\d*),"                 # num satellites (may be empty)
    r"([\d.]*),"              # HDOP (may be empty)
    r"(-?[\d.]+),M,"          # altitude MSL (m)
    r"(-?[\d.]*),M"           # geoid separation (may be empty)
)


def _infer_date_from_path(path: Path) -> date | None:
    """
    Try to extract a YYMMDD pattern from the file stem or any parent directory
    name and return a :class:`datetime.date` object.

    For example, the path ``.../230627/COM23_NMEA.txt`` or a file stem such
    as ``LocationAPI_230627_090521.ubx`` will both yield 2023-06-27.
    """
    # Search stem first, then each parent directory component in order.
    candidates = [path.stem] + [p.name for p in path.parents]
    for candidate in candidates:
        m = re.search(r"(\d{2})(\d{2})(\d{2})", candidate)
        if m:
            yy, mm, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
            year = 2000 + yy
            try:
                return date(year, mm, dd)
            except ValueError:
                continue
    return None


def parse_nmea_gga(path: str | Path, acq_date: date | None = None) -> pd.DataFrame:
    """
    Parse NMEA GGA sentences from a text file into a .pos-compatible DataFrame.

    Parameters
    ----------
    path:
        Path to the NMEA text file.  Mixed sentence types are accepted;
        only ``$G*GGA`` lines are processed.
    acq_date:
        Acquisition date (UTC).  If ``None``, it is inferred from the
        filename by searching for a ``YYMMDD`` pattern.

    Returns
    -------
    pd.DataFrame
        Same format as :func:`~gnsspos.processing.pos_reader.read_pos_file`,
        indexed by UTC datetime.  Fields unavailable in GGA (e.g., velocity,
        covariance off-diagonal) are set to ``0.0``.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ValueError
        If the acquisition date cannot be determined.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"NMEA file not found: {path}")

    if acq_date is None:
        acq_date = _infer_date_from_path(path)
    if acq_date is None:
        raise ValueError(
            f"Cannot infer acquisition date from filename '{path.name}'. "
            "Pass acq_date explicitly."
        )

    records: list[dict] = []
    prev_time: datetime | None = None
    day_offset = 0

    with path.open("r", errors="replace") as fh:
        for raw in fh:
            # Use search (not match): some receivers prepend binary data before '$'
            m = _GGA_RE.search(raw)
            if not m:
                continue

            time_str = m.group(2)
            lat_raw, lat_hemi = m.group(3), m.group(4)
            lon_raw, lon_hemi = m.group(5), m.group(6)
            quality = int(m.group(7))
            ns_count = int(m.group(8)) if m.group(8) else 0
            hdop = float(m.group(9)) if m.group(9) else 0.0
            alt_msl = float(m.group(10))
            geoid_sep = float(m.group(11)) if m.group(11) else 0.0

            # Parse HHMMSS[.ss] → hours, minutes, seconds+microseconds
            hh = int(time_str[0:2])
            mm_t = int(time_str[2:4])
            ss_frac = float(time_str[4:])
            ss = int(ss_frac)
            us = round((ss_frac - ss) * 1_000_000)

            epoch = datetime(
                acq_date.year, acq_date.month, acq_date.day,
                hh, mm_t, ss, us,
            ) + timedelta(days=day_offset)

            # Midnight rollover: if epoch jumped back more than 1 hour
            if prev_time is not None and epoch < prev_time - timedelta(hours=1):
                day_offset += 1
                epoch += timedelta(days=1)
            prev_time = epoch

            # DDMM.mmmmm → decimal degrees (latitude)
            lat_d = int(lat_raw[:2])
            lat_m = float(lat_raw[2:])
            lat = lat_d + lat_m / 60.0
            if lat_hemi == "S":
                lat = -lat

            # DDDMM.mmmmm → decimal degrees (longitude)
            lon_d = int(lon_raw[:3])
            lon_m = float(lon_raw[3:])
            lon = lon_d + lon_m / 60.0
            if lon_hemi == "W":
                lon = -lon

            height = alt_msl + geoid_sep
            Q = _GGA_QUALITY_MAP.get(quality, 0)

            # Uncertainty estimate from HDOP
            sdn = sde = hdop * 2.0
            sdu = hdop * 3.0

            records.append({
                "utc": epoch,
                "latitude_deg": lat,
                "longitude_deg": lon,
                "height_m": height,
                "Q": Q,
                "ns": ns_count,
                "sdn_m": sdn,
                "sde_m": sde,
                "sdu_m": sdu,
                "sdne_m": 0.0,
                "sdeu_m": 0.0,
                "sdun_m": 0.0,
                "age_s": 0.0,
                "ratio": 0.0,
                "vn_ms": 0.0,
                "ve_ms": 0.0,
                "vu_ms": 0.0,
                "sdvn": 0.0,
                "sdve": 0.0,
                "sdvu": 0.0,
                "sdvne": 0.0,
                "sdveu": 0.0,
                "sdvun": 0.0,
            })

    if not records:
        logger.warning("No GGA sentences found in %s", path)
        return pd.DataFrame(columns=["utc"] + POS_COLUMNS).set_index("utc")

    df = pd.DataFrame(records)
    df["Q"] = df["Q"].astype(int)
    df["ns"] = df["ns"].astype(int)
    df.set_index("utc", inplace=True)
    df.index.name = "utc"
    logger.info("Parsed %d GGA epochs from %s", len(df), path.name)
    return df
