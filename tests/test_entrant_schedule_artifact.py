"""Reproduction and framing pins for ``runs/entrant_schedule_v1.json``.

REPORT-ONLY EVIDENCE.  The artifact is not a gate run, not a gate candidate,
and writes no ``gates.yaml`` block.  Several tests below exist specifically to
keep it that way: if a later change quietly promotes this artifact into a
gated surface, they fail.

Most tests read only the committed artifact and always run.  The reproduction
pin rebuilds it from the pinned certified frame and is skipped unless
``huggingface_hub`` + ``tables`` are importable AND the h5 is already in the
local Hugging Face cache (no network in CI).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "runs" / "entrant_schedule_v1.json"
SCRIPTS = ROOT / "scripts"
GATES = ROOT / "gates.yaml"

ARTIFACT_SHA256 = (
    "94b670dca35037cb550b874f2403e70d3a8563ffbf5d882942451ca4cc989607"
)
ACTIVATION_YEARS = tuple(range(2026, 2036))


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text())


def _import_builder():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import build_entrant_schedule_v1 as builder

    return builder


# --------------------------------------------------------------------------
# Schema and the report-only framing
# --------------------------------------------------------------------------
def test_schema_and_role():
    art = _artifact()
    assert art["schema_version"] == "entrant_schedule.v1"
    assert art["artifact_role"] == "report_only_capability_evidence"
    assert art["status"] == "reported"


def test_the_artifact_is_not_gated_and_names_no_gate_or_candidate():
    art = _artifact()
    assert art["gated"] is False
    assert art["gate_id"] is None
    assert art["candidate_id"] is None
    assert art["schedule"]["provenance"]["gated"] is False
    assert art["schedule"]["provenance"]["report_only"] is True
    assert art["exclusions"]["gated"] is False


def test_gates_yaml_is_untouched_by_this_lane():
    """No ``gate_imm`` (or any entrant gate) was introduced."""
    text = GATES.read_text()
    assert "gate_imm" not in text
    assert "entrant_schedule" not in text
    assert _artifact()["disclosures"]["gates_yaml_untouched"] is True


def test_the_build_touched_no_network():
    assert _artifact()["build"]["network_access"].startswith("none")


# --------------------------------------------------------------------------
# Control
# --------------------------------------------------------------------------
def test_control_is_the_2026_trustees_va2_intermediate_scenario():
    provenance = _artifact()["control"]["provenance"]
    assert provenance["publication"] == "2026 OASDI Trustees Report"
    assert provenance["table_id"] == "V.A2"
    assert provenance["scenario"] == "intermediate"
    assert provenance["units"] == "thousands_of_persons"
    assert provenance["snapshot_sha256"] == (
        "5dfd05e5c5d4bbe413dd97f2256db24d5595e561623455edca3761bbfece89da"
    )


def test_control_inflow_is_gross_not_net():
    art = _artifact()
    inflow = art["control"]["gross_positive_inflow_thousands"]
    row = art["control"]["rows"]["2026"]
    assert inflow["2026"] == 1340.0
    assert row["lpr_inflow"] + row["other_inflow"] == 1340.0
    assert row["total_net_change"] == 130.0
    # The seam is sized to 1340, not 130.
    assert inflow["2026"] != row["total_net_change"]


def test_the_entry_only_minus_net_gap_is_published():
    gap = _artifact()["disclosures"]["entry_only_minus_net_gap_thousands"]
    assert set(gap) == {str(year) for year in ACTIVATION_YEARS}
    assert gap["2026"] == 1340.0 - 130.0


# --------------------------------------------------------------------------
# Donor
# --------------------------------------------------------------------------
def test_donor_is_the_certified_frame_not_acs():
    donor = _artifact()["donor"]["provenance"]
    assert donor["donor_source"] == "certified populace deployment frame"
    assert donor["certified_pin"]["dataset"] == "populace_us_2024"
    assert donor["asec_vintage"] == 2024
    assert donor["peinusyr_codes"] == [28]
    assert donor["arrival_windows"]["28"] == [2022, 2024]


def test_the_donor_universe_matches_the_control_universe():
    """Only the foreign-born, because only they are in V.A2's two stocks."""
    donor = _artifact()["donor"]["provenance"]
    assert donor["universe"] == "foreign_born_prcitshp_4_or_5"
    assert donor["n_donor_rows"] == 1155
    assert donor["n_foreign_born_rows"] == donor["n_donor_rows"]
    assert "internal migration, not" in donor["universe_reason"]


def test_donor_publishes_the_frame_measurements():
    diagnostics = _artifact()["donor"]["frame_diagnostics"]
    assert diagnostics["n_rows"] == 166302
    assert diagnostics["entry_year_universe_identity"]["holds"] is True
    assert diagnostics["foreign_born"]["n_rows"] == 23732
    assert diagnostics["foreign_born"]["share"] == pytest.approx(
        0.179627, abs=1e-6
    )
    assert diagnostics["calibration_status"].startswith("UNCALIBRATED")


def test_donor_publishes_the_vintage_domain_mismatch():
    mismatch = _artifact()["donor"]["vintage_domain_mismatch"]
    assert mismatch["rows_with_undefined_band"] == 795
    assert mismatch["undefined_pairs"] == {"source_year=2023,peinusyr=28": 795}


def test_donor_composition_shares_sum_to_one():
    composition = _artifact()["donor"]["composition_by_age_band_sex"]
    assert sum(cell["share"] for cell in composition.values()) == (
        pytest.approx(1.0)
    )


def test_the_thinnest_donor_cell_is_published_for_a_future_floor():
    """The support a floors ceremony would have to price or demote.

    Publishing the raw n per cell is what makes the demotion decision
    reviewable instead of a surprise mid-ceremony.
    """
    composition = _artifact()["donor"]["composition_by_age_band_sex"]
    counts = {key: cell["n_rows"] for key, cell in composition.items()}
    assert min(counts.values()) == 12
    assert counts["65+|male"] == 12


# --------------------------------------------------------------------------
# Schedule
# --------------------------------------------------------------------------
def test_schedule_covers_the_activation_window():
    schedule = _artifact()["schedule"]
    assert schedule["activation_years"] == list(ACTIVATION_YEARS)
    assert set(schedule["by_activation_year"]) == {
        str(year) for year in ACTIVATION_YEARS
    }


def test_schedule_totals_and_counters_agree():
    schedule = _artifact()["schedule"]
    counters = schedule["entrant_provenance_counters"]
    assert schedule["total_rows"] == 11550
    assert counters["immigrant_cohorts"] == 11550
    assert counters["n_rows_by_entry_kind"] == {"immigrant_cohort": 11550}
    assert "not ID arithmetic" in counters["counter_basis"]


def test_each_year_aligns_to_its_control_within_floating_point():
    schedule = _artifact()["schedule"]
    for year, record in schedule["by_activation_year"].items():
        alignment = record["alignment"]
        assert alignment["target_weighted_persons"] == (
            alignment["control_inflow_thousands"] * 1000.0
        )
        assert abs(alignment["relative_residual"]) < 1e-12, year
    assert schedule["alignment_summary"]["max_abs_relative_residual"] < 1e-12


def test_cell_weights_sum_to_the_year_total():
    schedule = _artifact()["schedule"]
    for year, record in schedule["by_activation_year"].items():
        cells = record["cells_by_age_band_sex"]
        total = sum(cell["weighted_persons"] for cell in cells.values())
        assert total == pytest.approx(
            record["alignment"]["scheduled_weighted_persons"], rel=1e-9
        ), year


# --------------------------------------------------------------------------
# Exclusions
# --------------------------------------------------------------------------
def test_all_four_domains_are_excluded_for_every_entrant():
    exclusions = _artifact()["exclusions"]
    assert exclusions["n_entrants"] == 11550
    assert set(exclusions["excluded_domains"]) == {
        "fertility_risk",
        "claiming_eligibility",
        "disability_panel",
        "earnings_domain",
    }
    for domain, record in exclusions["excluded_domains"].items():
        assert record["n_excluded"] == 11550, domain


def test_the_claiming_counterfactual_is_quantified():
    """How many rows the unconditional draw would have caught."""
    record = _artifact()["exclusions"]["excluded_domains"][
        "claiming_eligibility"
    ]
    assert record["n_would_have_drawn_a_claim_age"] == 1350
    assert "apply_claiming would draw a claim age" in record["counterfactual"]


def test_disclosures_refuse_the_claims_this_artifact_cannot_support():
    disclosures = _artifact()["disclosures"]
    assert disclosures["universe_bridge_status"] == "ssa_area_proxy_unbridged"
    assert disclosures["donor_basis_status"] == (
        "stock_proxy_not_arrival_observation"
    )
    assert disclosures["net_alignment_status"] == (
        "entry_only_no_emigration_law"
    )
    joined = " ".join(disclosures["not_supported_by_this_artifact"])
    for phrase in (
        "AIME",
        "insured status",
        "legal status",
        "dependency ratios",
        "annual arrival resolution",
    ):
        assert phrase in joined


# --------------------------------------------------------------------------
# Reproduction
# --------------------------------------------------------------------------
def test_committed_artifact_matches_its_pinned_digest():
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert digest == ARTIFACT_SHA256


def test_artifact_reproduces_from_the_certified_frame():
    pytest.importorskip("huggingface_hub")
    pytest.importorskip("tables")
    from huggingface_hub import hf_hub_download

    from populace_dynamics.data import nativity_frame as nfm

    pin = nfm.CERTIFIED_PIN
    try:
        hf_hub_download(
            repo_id=pin["hf_repo_id"],
            filename=pin["hf_filename"],
            repo_type=pin["hf_repo_type"],
            revision=pin["revision"],
            local_files_only=True,
        )
    except Exception:  # noqa: BLE001
        pytest.skip("certified populace h5 not in local HF cache")

    rebuilt = _import_builder().run()
    committed = _artifact()
    assert rebuilt == committed
    serialized = json.dumps(rebuilt, indent=2, sort_keys=True) + "\n"
    assert (
        hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        == ARTIFACT_SHA256
    )
