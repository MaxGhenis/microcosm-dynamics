"""Pin the gate-3 retrodiction-arm pre-lock floor artifact.

The artifact carries no wall clock and no environment block, so this
suite does not merely pin a digest: it re-runs the builder and requires
the result to be byte-identical to the committed bytes. It also pins the
load-bearing findings the referee round will argue over, so that a
silent change to any of them fails here rather than in a ceremony.

gates.yaml is untouched by the artifact and by this suite; gate_3 stays
at ``locked: false`` with no thresholds.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
sys.path.insert(0, str(ROOT / "scripts"))

import build_gate3_retrodiction_floors as builder  # noqa: E402

ARTIFACT = RUNS / "gate3_retrodiction_floors_v1.json"
ENV_SIDECAR = RUNS / "gate3_retrodiction_floors_v1.env.json"
INPUT_SIDECAR = RUNS / "gate3_retrodiction_floors_v1.inputs.json"
BUILDER = ROOT / "scripts" / "build_gate3_retrodiction_floors.py"

ARTIFACT_SHA256 = (
    "d78721185856650b1898a7e21d31203c4f0cf0f29e5c79e989f676aec1c78875"
)
BUILDER_SHA256 = (
    "eedf2485c48daee3a8d52d214b52f98a17892e466a508400c7281856d1fae720"
)


@pytest.fixture(scope="module")
def artifact() -> dict:
    return json.loads(ARTIFACT.read_text())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# reproduction
# --------------------------------------------------------------------------
def test_rebuild_is_byte_identical():
    """The real reproduction check: rebuild and compare the bytes."""
    rebuilt = json.dumps(builder.build(), indent=2) + "\n"
    assert rebuilt == ARTIFACT.read_text()


def test_artifact_carries_no_wall_clock_or_environment(artifact):
    """Byte-reproducibility depends on both staying out of the artifact."""
    assert "elapsed_seconds" not in artifact
    assert "environment" not in artifact
    assert "built_utc" not in json.dumps(artifact)
    assert "byte for byte" in artifact["reproducibility"]


def test_builder_and_sidecar_digests():
    assert _sha256(BUILDER) == BUILDER_SHA256
    assert _sha256(ARTIFACT) == ARTIFACT_SHA256
    environment = json.loads(ENV_SIDECAR.read_text())
    assert environment["status"] == "MEASUREMENT_ENVIRONMENT"
    for field in ("python", "numpy", "pandas", "platform"):
        assert environment["environment"][field]
    inputs = json.loads(INPUT_SIDECAR.read_text())
    assert inputs["status"] == "SOURCE_INPUT_DIGESTS"
    assert len(inputs["source_inputs"]) == len(builder.SOURCE_INPUTS)
    for entry in inputs["source_inputs"]:
        assert len(entry["sha256"]) == 64
        int(entry["sha256"], 16)
        assert entry["bytes"] > 0
        assert entry["official_url"]
        assert (ROOT / entry["path"]).exists()


# --------------------------------------------------------------------------
# pre-lock status: this artifact moves no gate
# --------------------------------------------------------------------------
def test_prelock_status_and_no_gate_movement(artifact):
    assert artifact["reported_anchor_not_gated"] is True
    assert "NOT RATIFIED" in artifact["status"]
    assert "pinning event, not a ratification" in artifact["status"]
    assert artifact["arm_scope"]["gate_3_locked"] is False
    assert "NOT RATIFIED" in artifact["draft_thresholds_note"]


def test_gates_yaml_still_has_no_gate_3_thresholds():
    text = (ROOT / "gates.yaml").read_text()
    start = text.index("  gate_3:\n")
    block = text[start : text.index("\n  gate_m4:", start)]
    assert "locked: false" in block
    assert "gate3_retrodiction_floors" not in text
    for forbidden in ("tolerance", "log_ratio_abs_max", "rho:", "k:"):
        assert forbidden not in block


def test_the_gate_3_description_is_quoted_verbatim(artifact):
    text = (ROOT / "gates.yaml").read_text()
    quoted = artifact["arm_scope"]["gate_3_text_verbatim"]
    collapsed = " ".join(text.split())
    assert " ".join(quoted.split()) in collapsed


# --------------------------------------------------------------------------
# the protocol windows, fixed by the settlement finding
# --------------------------------------------------------------------------
def test_protocol_windows(artifact):
    protocol = artifact["protocol"]
    assert protocol["vintage_boundary_year"] == 2014
    assert protocol["T_star"] == 2012
    assert protocol["fit_window"] == [1998, 2012]
    assert protocol["scored_window"] == [2014, 2021]
    assert sorted(protocol["excluded_years"]) == ["2013", "2022"]
    assert protocol["shock_window"] == [2020, 2021]
    assert protocol["clean_scored_years"] == [
        2014,
        2015,
        2016,
        2017,
        2018,
        2019,
    ]


def test_vintage_boundary_is_the_engine_constant():
    from populace_dynamics.engine import refit

    assert builder.VINTAGE_BOUNDARY_YEAR == refit.BOUNDARY_YEAR == 2014
    assert builder.T_STAR == 2012


def test_settlement_finding_is_pinned(artifact):
    """The finding the whole tolerance basis turns on."""
    regimes = artifact["settlement_analysis"]["by_regime"]
    settled = regimes["settled"]["abs_pp"]
    terminal = regimes["terminal"]["abs_pp"]
    assert settled["n_cell_years"] == 240
    assert settled["n_nonzero"] == 1
    assert settled["max"] == 0.1
    assert terminal["n_cell_years"] == 16
    assert terminal["n_nonzero"] == 16
    assert terminal["mean"] == 0.5375
    assert terminal["max"] == 1.1
    assert regimes["settled"]["abs_years"]["n_nonzero"] == 0


def test_settlement_finding_has_independent_confirmation(artifact):
    """6.B5.1 vs 6.A1: the same signature from a different table."""
    confirmation = artifact["settlement_analysis"]["independent_confirmation"]
    settled = confirmation["settled_years_max_relative_gap"]
    terminal = confirmation["terminal_year_relative_gap"]
    assert settled == pytest.approx(0.012954, abs=1e-6)
    assert terminal == pytest.approx(0.085997, abs=1e-6)
    assert terminal > 6 * settled


# --------------------------------------------------------------------------
# the floors
# --------------------------------------------------------------------------
def test_person_disjoint_is_declared_unavailable_in_principle(artifact):
    design = artifact["floor_design"]
    assert (
        "100 percent data (not a sample)"
        in design["person_disjoint_unavailable_in_principle"]
    )
    assert "IN PRINCIPLE" in design["person_disjoint_unavailable_in_principle"]
    assert design["seeds"] == [0, 1, 2, 3, 4]
    assert "not RNG draws" in design["seed_semantics"]


def test_vintage_revision_floor_is_degenerate_on_settled_rows(artifact):
    floors = artifact["floor_vintage_revision"]["cells"]
    share_cells = [k for k in floors if k.startswith("claim_share.")]
    assert len(share_cells) == 16
    assert sum(floors[k]["degenerate"] for k in share_cells) == 15
    cell = floors["claim_share.age62|female"]
    assert cell["regime"] == "settled_rows_only"
    assert cell["n_settled_years"] == 15
    assert cell["n_settled_nonzero"] == 0
    assert cell["mean"] == 0.0 and cell["sd"] == 0.0
    assert cell["terminal_row_deviation"] == 1.1
    # the unpartitioned number, recorded but never used
    assert cell["pooled_including_terminal_row"]["max_over_years"] == 1.1
    assert "never" not in cell["pooled_including_terminal_row"]["note"]
    assert "not used for any tolerance" in (
        cell["pooled_including_terminal_row"]["note"]
    )


def test_publication_rounding_floor_binds_the_share_cells(artifact):
    rounding = artifact["floor_publication_rounding"]
    cell = rounding["claim_share.age62|female"]
    assert cell["status"] == "established"
    assert cell["granularity"] == 0.1
    assert cell["floor"] == 0.05


def test_naive_baseline_horizon_structure_is_population_not_per_cell(
    artifact,
):
    """Growth with horizon holds POOLED, not cell by cell.

    Asserting per-cell monotonicity here would be false: six of the
    eighteen eligible cells have a flat or mean-reverting share, and
    their naive deviation shrinks with horizon. The artifact records
    that split and hands the referee the choice.
    """
    monotone = artifact["horizon_monotonicity"]
    pooled = list(monotone["pooled_mean_across_eligible_cells"].values())
    assert monotone["clean_horizons"] == [f"h{h}" for h in range(2, 8)]
    assert monotone["pooled_is_monotone_non_decreasing"] is True
    assert pooled == sorted(pooled)
    assert pooled[0] == pytest.approx(1.398571, abs=1e-6)
    assert pooled[-1] == pytest.approx(3.042222, abs=1e-6)
    assert monotone["n_eligible_cells"] == 18
    assert monotone["n_increasing_h2_to_h7"] == 12
    assert monotone["n_decreasing_h2_to_h7"] == 6
    assert "POPULATION property, not a per-cell law" in monotone["finding"]
    assert "this artifact takes neither" in monotone["referee_question"]


def test_every_eligible_cell_has_all_six_clean_horizons(artifact):
    cells = artifact["naive_baseline_pseudo_vintage"]["cells"]
    for key in artifact["draft_gate_eligible_cells"]:
        rule = cells[key]["rules"][cells[key]["baseline_rule"]]
        clean = rule["registered_origin"]["clean"]
        assert sorted(clean) == sorted(f"h{h}" for h in range(2, 8))
        assert [clean[f"h{h}"]["target_year"] for h in range(2, 8)] == list(
            range(2014, 2020)
        )


def test_non_decreasing_envelope_is_offered_but_not_taken(artifact):
    monotone = artifact["horizon_monotonicity"]
    envelope = monotone["non_decreasing_envelope_if_adopted"]
    assert len(envelope) == 18
    for row in envelope.values():
        values = list(row.values())
        assert values == sorted(values)
    # a mean-reverting cell: measured tolerance falls, the envelope holds
    measured = artifact["draft_thresholds"]["cells"][
        "claim_share.age64|female"
    ]["instrument_b_skill_ratio"]["by_horizon"]
    assert measured["h7"]["tolerance"] < measured["h2"]["tolerance"]
    assert envelope["claim_share.age64|female"]["h7"] == 0.45


def test_naive_baseline_registered_origin_targets(artifact):
    cells = artifact["naive_baseline_pseudo_vintage"]["cells"]
    rule = cells["claim_average_age|male"]["rules"]["persistence"]
    clean = rule["registered_origin"]["clean"]
    assert clean["h2"]["target_year"] == 2014
    assert clean["h7"]["target_year"] == 2019
    assert clean["h2"]["prediction"] == 64.2  # the T*=2012 value, carried
    assert clean["h7"]["realized"] == 64.9
    assert clean["h7"]["deviation"] == pytest.approx(0.7, abs=1e-9)
    assert "h1" not in clean  # target 2013 is the excluded provisional row
    assert set(rule["registered_origin"]["shock"]) == {"h8", "h9"}


# --------------------------------------------------------------------------
# the two instruments
# --------------------------------------------------------------------------
def test_instrument_a_degenerates_onto_the_rounding_floor(artifact):
    cells = artifact["draft_thresholds"]["cells"]
    collapsed = 0
    for key in artifact["draft_gate_eligible_cells"]:
        entry = cells[key]["instrument_a_mean_k_sd"]
        assert entry["horizon_invariant"] is True
        assert "collapses onto the publication-rounding floor" in (
            entry["why_not_recommended"]
        )
        if entry["tolerance"] == 0.05:
            collapsed += 1
    assert collapsed == 17
    assert artifact["draft_thresholds"]["k"] == 4


def test_instrument_b_is_per_horizon_and_records_its_tension(artifact):
    cells = artifact["draft_thresholds"]["cells"]
    entry = cells["claim_share.age66|male"]["instrument_b_skill_ratio"]
    assert entry["rho"] == 0.75
    assert entry["baseline_rule"] == "persistence"
    h7 = entry["by_horizon"]["h7"]
    assert h7["basis"] == "registered_origin_deviation"
    assert h7["registered_origin_target_year"] == 2019
    assert h7["basis_value"] == 4.8
    assert h7["tolerance"] == pytest.approx(3.6, abs=1e-9)
    assert h7["room_for_skill"] is True
    assert h7["sensitivity"] == {"0.5": 2.4, "0.75": 3.6, "0.9": 4.32}
    # h1 has no clean registered target (2013 is excluded)
    assert entry["by_horizon"]["h1"]["basis"] == (
        "rolling_block_mean_fallback"
    )
    assert "does not choose" in entry["unresolved_tension_for_the_referee"]


def test_neither_instrument_is_asserted(artifact):
    note = artifact["draft_thresholds"]["two_instruments_note"]
    assert "NEITHER is asserted" in note
    assert "referee round's decision" in note
    assert "No value here is mirrored into gates.yaml" in note


# --------------------------------------------------------------------------
# eligibility and the proposed surface
# --------------------------------------------------------------------------
def test_only_the_two_vintage_claiming_cells_are_eligible(artifact):
    eligible = artifact["draft_gate_eligible_cells"]
    assert len(eligible) == 18
    stability = artifact["cell_stability"]
    assert all(stability[key]["family"] == "claiming" for key in eligible)
    assert all(stability[key]["two_vintage"] for key in eligible)
    for _key, row in stability.items():
        if row["draft_gate_eligible"]:
            continue
        assert row["blocking_reasons"]
        if row["family"] in {"covered_earnings", "disability"}:
            assert (
                "no_second_publication_vintage_in_repository"
                in row["blocking_reasons"]
            )
    # level cells are excluded even inside the two-vintage family
    for sex in ("female", "male"):
        row = stability[f"claim_awards_thousands|{sex}"]
        assert row["draft_gate_eligible"] is False
        assert (
            "level_cell_not_gate_eligible_pre_w1_scale_invariance"
            in row["blocking_reasons"]
        )


def test_proposed_gated_surface_is_h2_to_h7(artifact):
    surface = artifact["recommended_gated_surface"]
    assert surface["status"].startswith("A PROPOSAL")
    assert surface["n_gated"] == 108  # 18 cells x 6 clean horizons
    horizons = {cell.split("@")[1] for cell in surface["gated"]}
    assert horizons == {"h2", "h3", "h4", "h5", "h6", "h7"}
    assert artifact["roll_up"]["n_proposed_gated_cell_horizons"] == 108


# --------------------------------------------------------------------------
# the deviation log gate_3's description requires
# --------------------------------------------------------------------------
def test_both_deviation_logs_are_published(artifact):
    revision = artifact["deviation_log_vintage_revision"]
    assert revision["n_deviations"] == 23
    assert revision["n_settled_deviations"] == 5
    assert revision["n_terminal_deviations"] == 18
    assert all(
        row["regime"] in {"settled", "terminal"} for row in revision["entries"]
    )
    leakage = artifact["deviation_log_specification_leakage"]
    ids = {entry["id"] for entry in leakage["entries"]}
    assert "outcome_knowledge_in_specification" in ids
    assert "cell_and_rule_selection_after_the_fact" in ids
    assert "claiming_projection_is_the_persistence_rule_today" in ids
    classes = set(
        artifact["definitions"]["deviation_log"]["deviation_classes"]
    )
    for entry in leakage["entries"]:
        assert entry["class"] in classes | {"candidate_side_disclosure"}
        assert entry["consequence"]


def test_the_carried_claiming_path_is_disclosed_as_baseline(artifact):
    entry = next(
        row
        for row in artifact["deviation_log_specification_leakage"]["entries"]
        if row["id"] == "claiming_projection_is_the_persistence_rule_today"
    )
    assert "would score EXACTLY the naive baseline" in entry["detail"]
    assert "grade a carried path as baseline, not as skill" in (
        entry["consequence"]
    )


# --------------------------------------------------------------------------
# external anchors
# --------------------------------------------------------------------------
def test_tr2014_anchor_concept_equivalence_is_demonstrated(artifact):
    anchor = artifact["external_anchor"]["tr2014_official_baseline"]
    evidence = anchor["concept_equivalence_evidence"]
    assert evidence["n_overlap_years"] == 44
    assert evidence["max_rel_gap"] <= evidence["max_rel_gap_allowed"]
    assert evidence["max_rel_gap"] == pytest.approx(0.001777, abs=1e-6)
    assert "4.A1 (OASI only)" in evidence["guard"]
    assert anchor["sources"]["realized"]["table"] == "4.A3"
    assert "Combined" in anchor["sources"]["realized"]["table_title"]
    assert anchor["status"] == "REPORTED EXTERNAL ANCHOR, NOT GATED"


def test_tr2014_concept_guard_is_load_bearing():
    """Mutate the caption binding to 4.A1 and require a loud failure."""
    original = builder.A3_CAPTION_MARKERS
    try:
        builder.A3_CAPTION_MARKERS = ("Table 4.A1",)
        with pytest.raises(ValueError, match="concept equivalence REFUTED"):
            builder.tr2014_projection_anchor()
    finally:
        builder.A3_CAPTION_MARKERS = original


def test_tr2014_official_baseline_deviations(artifact):
    anchor = artifact["external_anchor"]["tr2014_official_baseline"]
    deviations = anchor["official_baseline_deviations"]
    assert [row["year"] for row in deviations] == list(range(2015, 2025))
    assert all(row["signed_relative_error"] < 0 for row in deviations)
    assert deviations[0]["log_ratio_abs"] < deviations[-1]["log_ratio_abs"]
    assert anchor["summary"]["max_log_ratio_abs"] == pytest.approx(
        0.052529, abs=1e-6
    )


def test_level_anchor_crosscheck_is_computed_not_asserted(artifact):
    check = artifact["external_anchor"]["level_anchor_crosscheck"]
    assert check["status"] == "COMPUTED, not asserted"
    assert check["n_comparisons"] == 16
    assert check["all_exact"] is True
    assert check["max_abs_gap"] == 0.0


def test_draw_noise_is_context_not_a_floor(artifact):
    context = artifact["draw_noise_context"]
    assert context["status"].startswith("REPORT-ONLY CONTEXT")
    assert "creates no gate, floor, threshold, or verdict" in (
        context["why_not_a_floor"]
    )


# --------------------------------------------------------------------------
# the honest register of what is not computable
# --------------------------------------------------------------------------
def test_not_computable_register_names_the_gaps(artifact):
    items = {row["item"]: row for row in artifact["not_computable"]}
    assert any("beneficiary counts" in item for item in items)
    assert any("tier-2 arm" in item for item in items)
    assert any("LATENT TRAP" in item for item in items)
    for row in items.values():
        assert row["reason"] and row["unblocks_if"]


def test_the_claiming_reader_trap_is_recorded_and_avoided(artifact):
    from populace_dynamics import claiming

    trap = next(
        row
        for row in artifact["not_computable"]
        if "LATENT TRAP" in row["item"]
    )
    assert f"{claiming.MIN_YEAR}-{claiming.MAX_YEAR}" in trap["reason"]
    # the trap is real: the 2023-pinned constants accept a post-2013 year
    # against the 2014 vintage and then raise a bare KeyError
    reference = claiming.load_claim_age_reference(builder.CLAIM_2014)
    assert reference.supplement_year == 2014
    assert max(reference.years()) == 2013
    assert claiming.MAX_YEAR == 2022
    with pytest.raises(KeyError):
        reference.row("male", 2019)
    # and the builder avoids it by reading rows directly
    source = BUILDER.read_text()
    assert "reference.row(sex, year)" in source
    assert "claim_age_distribution(" not in source
