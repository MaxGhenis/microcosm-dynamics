"""Build the report-only entrant-schedule evidence artifact (v1).

REPORT-ONLY.  **This is not a gate run and not a gate candidate.**  It writes
no ``gates.yaml`` block, registers no candidate, and scores nothing.  It exists
to convert "no immigration: no entrant cohorts" from an absence into a
labelled, audited capability, and to exercise the scheduled-entries seam at
scale before any entrant-native law is estimated.

What it produces, in ``runs/entrant_schedule_v1.json``:

* the **control** -- Trustees Table V.A2 gross positive inflow, parsed from a
  hash-pinned snapshot of the 2026 report;
* the **donor** -- the certified frame's recent-arrival nativity pool, with
  the measured counts that identify it;
* the **schedule** -- entrant cohorts by activation year, age band, sex and
  nativity, sized to the control, with alignment residuals;
* the **exclusions** -- what the entrants are kept out of, and how many rows
  each exclusion covers;
* the **disclosures** -- every claim this artifact does NOT support.

Run from the repository root.  It needs pandas + pytables + huggingface_hub to
resolve the pinned certified frame, and no PSID and no populace-fit::

    PYTHONPATH=src \\
      ~/PolicyEngine/policyengine.py/.venv/bin/python \\
      scripts/build_entrant_schedule_v1.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from populace_dynamics.data import nativity_frame as nfm  # noqa: E402
from populace_dynamics.data import trustees_immigration as tim  # noqa: E402
from populace_dynamics.engine import entrant_domains as edm  # noqa: E402
from populace_dynamics.engine import entrant_schedule as esm  # noqa: E402
from populace_dynamics.engine.loop import (  # noqa: E402
    SyntheticPersonIdAllocator,
)

ARTIFACT_PATH = ROOT / "runs" / "entrant_schedule_v1.json"
ARTIFACT_SCHEMA_VERSION = "entrant_schedule.v1"

#: The activation window.  Starts at the first year V.A2's projection period
#: covers under the intermediate assumptions.
ACTIVATION_YEARS = tuple(range(2026, 2036))
SCENARIO = "intermediate"

#: The donor vintage and band.  ONE ASEC vintage, because PEINUSYR's top code
#: means different arrival windows on different vintages (nativity_frame).
DONOR_VINTAGE = 2024
DONOR_CODES = (28,)

#: Synthetic IDs start well above the certified frame's person_id range; the
#: allocator raises on any overlap with the reserved real namespace.
SYNTHETIC_ID_START = 90_000_000


def _resolve_certified_h5() -> str:
    from huggingface_hub import hf_hub_download

    pin = nfm.CERTIFIED_PIN
    return hf_hub_download(
        repo_id=pin["hf_repo_id"],
        filename=pin["hf_filename"],
        repo_type=pin["hf_repo_type"],
        revision=pin["revision"],
    )


def _file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _cohort_cells(frame, bands=nfm.DONOR_AGE_BANDS) -> dict[str, Any]:
    """Weighted entrant counts by age band x sex x nativity for one year."""
    age = frame["entry_age"].to_numpy(dtype=np.float64)
    weight = frame["weight"].to_numpy(dtype=np.float64)
    female = frame["sex"].astype(str).to_numpy() == "female"
    foreign = frame["foreign_born"].to_numpy(dtype=bool)
    cells: dict[str, Any] = {}
    for lo, hi in bands:
        label = f"{lo}+" if hi >= 200 else f"{lo}-{hi}"
        in_band = (age >= lo) & (age <= hi)
        for is_f, sex_label in ((True, "female"), (False, "male")):
            mask = in_band & (female == is_f)
            cells[f"{label}|{sex_label}"] = {
                "n_rows": int(mask.sum()),
                "weighted_persons": float(weight[mask].sum()),
                "n_foreign_born_rows": int((mask & foreign).sum()),
                "weighted_foreign_born": float(weight[mask & foreign].sum()),
            }
    return cells


def run(verbose: bool = False) -> dict[str, Any]:
    # ---- control: Trustees Table V.A2 -------------------------------------
    control = tim.load_control(SCENARIO)
    inflow = control.positive_inflow(ACTIVATION_YEARS)
    control_rows = {
        int(record.year): record.as_dict()
        for record in control.rows
        if record.year in set(ACTIVATION_YEARS)
    }
    if verbose:
        print(f"control: {len(control.rows)} rows, {SCENARIO}")

    # ---- donor: the certified frame's recent arrivals ----------------------
    h5_path = _resolve_certified_h5()
    observed_sha = _file_sha256(h5_path)
    if observed_sha != nfm.CERTIFIED_PIN["artifact_sha256"]:
        raise ValueError(
            f"certified frame sha256 mismatch: got {observed_sha}, pinned "
            f"{nfm.CERTIFIED_PIN['artifact_sha256']}"
        )
    persons, populated = nfm.load_nativity_persons(h5_path)
    diagnostics = nfm.nativity_diagnostics(persons)
    mismatch = nfm.vintage_domain_mismatch(persons)
    donor_pool = nfm.recent_arrival_donor(
        persons, vintage=DONOR_VINTAGE, codes=DONOR_CODES
    )
    composition = nfm.donor_composition(donor_pool)
    donor = nfm.NativityDonor(
        pool=donor_pool,
        composition=composition,
        vintage=DONOR_VINTAGE,
        codes=DONOR_CODES,
    )
    if verbose:
        print(f"donor: {len(donor_pool)} rows")

    # ---- schedule ----------------------------------------------------------
    allocator = SyntheticPersonIdAllocator(SYNTHETIC_ID_START)
    schedule = esm.build_entrant_schedule(
        donor_pool,
        inflow,
        allocator=allocator,
        control_provenance=control.provenance(),
        donor_provenance=donor.provenance(),
    )
    counters = esm.entrant_provenance_counters(schedule.frames)

    # ---- exclusions --------------------------------------------------------
    import pandas as pd

    pooled = pd.concat(schedule.frames.values(), ignore_index=True)
    report = edm.exclusion_report(pooled)

    per_year = {
        str(year): {
            "alignment": schedule.alignment[year],
            "cells_by_age_band_sex": _cohort_cells(frame),
        }
        for year, frame in sorted(schedule.frames.items())
    }

    residuals = [
        record["relative_residual"] for record in schedule.alignment.values()
    ]
    artifact: dict[str, Any] = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_role": "report_only_capability_evidence",
        "gated": False,
        "gate_id": None,
        "candidate_id": None,
        "status": "reported",
        "build": {
            "network_access": (
                "none at build time; the Trustees control reads a committed "
                "hash-verified snapshot and the donor reads the pinned "
                "certified frame resolved from the local Hugging Face cache"
            ),
            "certified_frame_sha256": observed_sha,
            "certified_pin": dict(nfm.CERTIFIED_PIN),
            "populated_column_fractions": populated,
            "synthetic_id_start": SYNTHETIC_ID_START,
            "next_synthetic_id": allocator.next_id,
        },
        "control": {
            "provenance": control.provenance(),
            "gross_positive_inflow_thousands": {
                str(year): value for year, value in inflow.items()
            },
            "rows": {str(k): v for k, v in control_rows.items()},
        },
        "donor": {
            "provenance": donor.provenance(),
            "frame_diagnostics": diagnostics,
            "vintage_domain_mismatch": mismatch,
            "composition_by_age_band_sex": composition,
        },
        "schedule": {
            "provenance": schedule.provenance,
            "activation_years": list(ACTIVATION_YEARS),
            "total_rows": schedule.total_rows(),
            "total_weighted_persons": schedule.total_weight(),
            "entrant_provenance_counters": counters,
            "by_activation_year": per_year,
            "alignment_summary": {
                "max_abs_relative_residual": (
                    float(np.max(np.abs(residuals))) if residuals else 0.0
                ),
                "basis": (
                    "the donor is reweighted, not resampled, so the residual "
                    "against the control is floating-point arithmetic and not "
                    "sampling noise"
                ),
            },
        },
        "exclusions": report.as_dict(),
        "disclosures": {
            "universe_bridge_status": "ssa_area_proxy_unbridged",
            "donor_basis_status": "stock_proxy_not_arrival_observation",
            "net_alignment_status": "entry_only_no_emigration_law",
            "entry_only_minus_net_gap_thousands": {
                str(record.year): record.entry_only_minus_net_gap
                for record in control.rows
                if record.year in set(ACTIVATION_YEARS)
            },
            "not_supported_by_this_artifact": [
                "entrant benefit levels (AIME, PIA, claiming) - suppressed",
                "insured status and prior US covered earnings - censored, "
                "not zero",
                "legal status and undocumented share",
                "population stocks, dependency ratios and net migration - "
                "an entry-only schedule cannot close a net path",
                "any post-entry transition of an entrant",
                "annual arrival resolution - the donor band is 2022-2024",
            ],
            "gates_yaml_untouched": True,
        },
    }
    return _json_safe(artifact)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--out", type=Path, default=ARTIFACT_PATH, help="artifact path"
    )
    args = parser.parse_args()
    artifact = run(verbose=args.verbose)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
