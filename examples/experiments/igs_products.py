#!/usr/bin/env python3
"""
Shared IGS product manager for the GPS_Sassuolo_Forlì campaign (2023-06-27).

All experiments use the same set of IGS precise products:
  - SP3  (Final precise orbits, 15 min)  — IGS0OPSFIN_*_ORB.SP3
  - CLK  (Final precise clocks, 5 min)   — IGS0OPSFIN_*_CLK.CLK
  - NAV  (Broadcast ephemeris, RINEX 3)  — BRDC00IGS > BRDM00DLR > brdc  (priority order)
  - INX  (Final ionosphere GIM, 2 h)     — IGS0OPSFIN_*_GIM.INX  [optional]

Priority:
  SP3/CLK: IGS Final only (no fallback — raises if unavailable).
  NAV: BRDC00IGS_R (RINEX 3 IGS combined multi-GNSS, best, in daily/YYp/)
       → BRDM00DLR_S (RINEX 3 DLR merged multi-GNSS, in daily/YYp/)
       → brdc*.n (RINEX 2 GPS-only, last resort, in daily/YYn/).
Credentials: NASA_USER and NASA_PWD env vars (from .env via docker-compose or set manually).

Usage (inside an experiment run.py)::

    from igs_products import ensure_igs_products
    products = ensure_igs_products(_EXPERIMENTS)
    # products['sp3'], products['clk'], products['nav'] are Path objects
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
sys.path.insert(0, str(_ROOT))

from gnsspos.service.igs_data_downloader import IGSDataDownloader

logger = logging.getLogger(__name__)

# Campaign: 2023-06-27 = DOY 178, GPS week 2268
_CAMPAIGN_YEAR  = 2023
_CAMPAIGN_MONTH = 6
_CAMPAIGN_DAY   = 27

# Known filenames for this campaign (downloaded once, reused by all experiments)
_SP3_NAME = "IGS0OPSFIN_20231780000_01D_15M_ORB.SP3"
_CLK_NAME = "IGS0OPSFIN_20231780000_01D_05M_CLK.CLK"
# NAV candidates in priority order (multi-GNSS RINEX 3 first, GPS-only RINEX 2 fallback)
# Combined files live in daily/YYYY/DDD/YYp/; individual GPS-only in YYn/.
_NAV_CANDIDATES = [
    "BRDC00IGS_R_20231780000_01D_MN.rnx",   # RINEX 3 IGS combined multi-GNSS (best)
    "BRDM00DLR_S_20231780000_01D_MN.rnx",   # RINEX 3 DLR merged multi-GNSS
    "brdc1780.23n",                           # RINEX 2 GPS-only (fallback)
]
_INX_NAME = "IGS0OPSFIN_20231780000_01D_02H_GIM.INX"


def ensure_igs_products(save_dir: Path) -> dict[str, Path]:
    """
    Check whether the shared IGS products for the campaign are present in
    *save_dir*.  Any missing file is downloaded from NASA CDDIS.

    Parameters
    ----------
    save_dir:
        Directory where the products are stored (usually examples/experiments/).

    Returns
    -------
    dict with keys 'sp3', 'clk', 'nav', 'inx' → absolute Path objects.

    Raises
    ------
    RuntimeError
        If a required file cannot be downloaded (credentials missing or server
        unavailable).
    """
    save_dir = Path(save_dir)
    sp3 = save_dir / _SP3_NAME
    clk = save_dir / _CLK_NAME
    nav = next((save_dir / n for n in _NAV_CANDIDATES if (save_dir / n).exists()), None)
    inx = save_dir / _INX_NAME

    missing_igs = [f for f in (sp3, clk) if not f.exists()]
    nav_missing = nav is None
    if not missing_igs and not nav_missing:
        logger.info("All IGS products already present in %s", save_dir)
        return {"sp3": sp3, "clk": clk, "nav": nav, "inx": inx if inx.exists() else None}

    nasa_user = os.environ.get("NASA_USER")
    nasa_pwd  = os.environ.get("NASA_PWD")
    if not nasa_user or not nasa_pwd:
        raise RuntimeError(
            "NASA_USER and NASA_PWD env vars required to download IGS products. "
            "Set them in .env or export before running."
        )

    dl = IGSDataDownloader(nasaUsr=nasa_user, nasaPwd=nasa_pwd)
    dl.setDate(_CAMPAIGN_YEAR, _CAMPAIGN_MONTH, _CAMPAIGN_DAY)

    if not sp3.exists():
        logger.info("Downloading SP3 (precise orbits)…")
        dl.downloadPreciseFinalOrbit(str(save_dir))
        logger.info("SP3 saved → %s", sp3)

    if not clk.exists():
        logger.info("Downloading CLK (precise clocks)…")
        dl.downloadPreciseFinalClock(str(save_dir))
        logger.info("CLK saved → %s", clk)

    if nav is None:
        logger.info("Downloading broadcast NAV (trying BRDM → brdm → brdc)…")
        dl.downloadBroadcastEphemeris(str(save_dir))
        nav = next((save_dir / n for n in _NAV_CANDIDATES if (save_dir / n).exists()), None)
        if nav is None:
            raise RuntimeError(f"Broadcast NAV download succeeded but none of {_NAV_CANDIDATES} found in {save_dir}.")
        logger.info("NAV saved → %s", nav)

    if not inx.exists():
        try:
            logger.info("Downloading IONEX (ionosphere GIM)…")
            dl.downloadIonosphere(str(save_dir))
            logger.info("INX saved → %s", inx)
        except Exception as exc:
            logger.warning("IONEX download failed (non-fatal): %s", exc)

    return {"sp3": sp3, "clk": clk, "nav": nav, "inx": inx if inx.exists() else None}
