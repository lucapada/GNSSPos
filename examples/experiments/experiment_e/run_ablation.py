#!/usr/bin/env python3
"""
Experiment E — Ablation: sweep the curvature-adaptive growth factor.

`run_adaptive.py` maps curvature rank -> σ_v via a single knob:
`sigma_v(rank) = base_sigma_v * growth ** rank`. This script reruns the
adaptive KF for a range of `growth` values and tabulates the accuracy
metrics vs the Exp 0 baseline, so the paper can show the smoothing/
responsiveness tradeoff quantitatively instead of picking one value by eye.

growth = 1.0 is the control: every curvature rank gets the same σ_v, so
this row is mathematically identical to round 1 (`run.py`)'s fixed-σ_v
output — included as the zero-adaptation reference point, not as a
separate implementation to keep in sync.

Outputs
-------
outputs/ablation/ablation_results.csv   one row per growth value
figures/ablation_growth_sweep.png       RMS_n/e/u, μ_d, σ_d vs growth
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import run_adaptive

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

_OUTPUTS = _HERE / "outputs" / "ablation"
_FIGURES = _HERE / "figures"

# 1.0 = control (no adaptation, == round 1). 2.0 = professor's original
# "double it per cluster" proposal. The rest bracket it for the sweep.
_GROWTH_VALUES = [1.0, 1.5, 2.0, 3.0, 4.0]


def run() -> pd.DataFrame:
    _OUTPUTS.mkdir(parents=True, exist_ok=True)

    baseline_df = run_adaptive._round1._load_baseline()
    if baseline_df is None:
        logger.error("Exp 0 baseline not found; cannot compute ablation metrics.")
        sys.exit(1)

    rows: list[dict] = []
    for growth in _GROWTH_VALUES:
        logger.info("=== growth=%.3g ===", growth)
        kf_df = run_adaptive.run(growth=growth, make_plots=False)
        m = run_adaptive.summary_metrics(kf_df, baseline_df)
        rows.append({"growth": growth, **m})

    table = pd.DataFrame(rows).set_index("growth")
    table.to_csv(_OUTPUTS / "ablation_results.csv")
    logger.info("Ablation table:\n%s", table.to_string())
    logger.info("Saved -> %s", _OUTPUTS / "ablation_results.csv")

    _plot(table)
    return table


def _plot(table: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    _FIGURES.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    for col in ["rms_northing_m", "rms_easting_m", "rms_height_m"]:
        ax.plot(table.index, table[col], marker="o", label=col)
    ax.set_xlabel("growth")
    ax.set_ylabel("Final cumulative RMS (m)")
    ax.set_title("RMS vs growth")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(table.index, table["mu_d"], marker="o", label="μ_d")
    ax.plot(table.index, table["sigma_d"], marker="o", label="σ_d")
    ax.set_xlabel("growth")
    ax.set_ylabel("3-D distance (m)")
    ax.set_title("μ_d / σ_d vs growth")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.suptitle("Experiment E – Curvature-Adaptive σ_v Ablation")
    fig.tight_layout()
    fig.savefig(_FIGURES / "ablation_growth_sweep.png", dpi=150)
    plt.close(fig)
    logger.info("Saved -> %s", _FIGURES / "ablation_growth_sweep.png")


if __name__ == "__main__":
    run()
