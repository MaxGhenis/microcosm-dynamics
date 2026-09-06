"""Pin the gate-3 retrodiction-arm floor artifact v2.

v2 answers the referee round on v1. This suite pins the four things the
referees' blocking findings turn on, and pins them by RE-DERIVATION
rather than by literal, so that a silent change fails here and not in a
ceremony:

* the null-rule panel computations (A6 / B2) -- every panel rule's
  deviation is recomputed from the staged printings without calling the
  builder's own panel, and the tolerance is re-derived from the STATED
  FORMULA rather than compared to a stored number;
* the strict-below-null property for EVERY gated tolerance -- the
  property the whole redesign exists to establish, checked on all of
  them, plus the computed proof that no registered null rule passes a
  gated pair;
* the candidate reference fence (B1) -- both directions: the fenced
  path refuses every held-out year, and the deployed module is measured
  still failing the fence today;
* the draft fragment parses, splices into a scratch copy of gates.yaml,
  and carries exactly the artifact's numbers (A7 / A8).

v1 is untouched: its artifact, its builder and its 31 tests are
byte-identical on this branch and still pass.
``gates.yaml`` is untouched by v2 and by this suite; gate_3 stays at
``locked: false`` with no thresholds.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
EXTERNAL = ROOT / "data" / "external"
sys.path.insert(0, str(ROOT / "scripts"))

import build_gate3_retrodiction_floors_v2 as builder  # noqa: E402

ARTIFACT = RUNS / "gate3_retrodiction_floors_v2.json"
ENV_SIDECAR = RUNS / "gate3_retrodiction_floors_v2.env.json"
INPUT_SIDECAR = RUNS / "gate3_retrodiction_floors_v2.inputs.json"
BUILDER = ROOT / "scripts" / "build_gate3_retrodiction_floors_v2.py"

V1_ARTIFACT = RUNS / "gate3_retrodiction_floors_v1.json"
V1_BUILDER = ROOT / "scripts" / "build_gate3_retrodiction_floors.py"
V1_ARTIFACT_SHA256 = (
    "d78721185856650b1898a7e21d31203c4f0cf0f29e5c79e989f676aec1c78875"
)
V1_BUILDER_SHA256 = (
    "eedf2485c48daee3a8d52d214b52f98a17892e466a508400c7281856d1fae720"
)

CATEGORIES = (
    "age62",
    "age63",
    "age64",
    "age65",
    "age66",
    "disability_conversion",
    "age67_69",
    "age70plus",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def artifact() -> dict:
    return json.loads(ARTIFACT.read_text())


@pytest.fixture(scope="module")
def independent_series() -> tuple[dict, dict]:
    """Both printings, read WITHOUT the builder or the claiming reader.

    Every recomputation below starts here, so a check cannot pass by
    agreeing with the code under test about how to read a table.
    """

    def read(name: str) -> dict:
        document = json.loads((EXTERNAL / name).read_text())
        series: dict[str, dict[int, float]] = {}
        for sex in ("female", "male"):
            for year_key, row in document["data"][sex].items():
                year = int(year_key)
                for category in CATEGORIES:
                    value = row["categories"].get(category)
                    if value is None:
                        continue
                    series.setdefault(f"claim_share.{category}|{sex}", {})[
                        year
                    ] = float(value)
                series.setdefault(f"claim_average_age|{sex}", {})[year] = (
                    float(row["average_age"])
                )
        return series

    return (
        read("ssa_claim_ages_2014supplement.json"),
        read("ssa_claim_ages_2023supplement.json"),
    )


# --------------------------------------------------------------------------
# reproduction, and v1 left alone
# --------------------------------------------------------------------------
def test_rebuild_is_byte_identical():
    """The real reproduction check: rebuild and compare the bytes."""
    rebuilt = json.dumps(builder.build(), indent=2) + "\n"
    assert rebuilt == ARTIFACT.read_text()


def test_v1_is_read_only_and_unmoved():
    """v2 re-floors the package the referees reviewed, or nothing."""
    assert _sha256(V1_ARTIFACT) == V1_ARTIFACT_SHA256
    assert _sha256(V1_BUILDER) == V1_BUILDER_SHA256
    assert builder.V1_ARTIFACT_SHA256 == V1_ARTIFACT_SHA256
    assert builder.V1_BUILDER_SHA256 == V1_BUILDER_SHA256


def test_builder_refuses_a_moved_v1(monkeypatch):
    """The v1 pin is load-bearing, not decorative."""
    monkeypatch.setattr(builder, "V1_ARTIFACT_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="v1 artifact digest moved"):
        builder.build()


def test_artifact_carries_no_wall_clock_no_environment_no_git(artifact):
    """R11: v1's reproduction depended on git history. v2's does not."""
    import re

    text = json.dumps(artifact)
    assert "elapsed_seconds" not in artifact
    assert "environment" not in artifact
    assert "built_utc" not in text
    assert artifact["reproducibility"]["no_wall_clock"] is True

    def walk(node, path=""):
        """No git-derived VALUE anywhere -- prose may name the v1 key."""
        if isinstance(node, dict):
            for key, value in node.items():
                assert key not in ("reader_commit", "repo_commit"), path
                walk(value, f"{path}/{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")
        elif isinstance(node, str):
            # a bare 40-hex token is a git object name; 64-hex is a sha256
            for token in re.findall(r"\b[0-9a-f]{40}\b", node):
                raise AssertionError(f"git-shaped value at {path}: {token}")

    walk(artifact)
    # the commit lives in the sidecar, which is excluded from the compare
    assert json.loads(ENV_SIDECAR.read_text())["environment"]["repo_commit"]


def test_sidecars(artifact):
    assert _sha256(BUILDER) != ""
    environment = json.loads(ENV_SIDECAR.read_text())
    assert environment["status"] == "MEASUREMENT_ENVIRONMENT"
    for field in ("python", "numpy", "platform", "repo_commit"):
        assert environment["environment"][field]
    inputs = json.loads(INPUT_SIDECAR.read_text())
    assert inputs["status"] == "SOURCE_INPUT_DIGESTS"
    assert len(inputs["source_inputs"]) == len(builder.SOURCE_INPUTS)
    for entry in inputs["source_inputs"]:
        assert len(entry["sha256"]) == 64
        int(entry["sha256"], 16)
        assert entry["bytes"] > 0
        assert (ROOT / entry["path"]).exists()


def test_prelock_status_and_no_gate_movement(artifact):
    assert artifact["roll_up"]["locked"] is False
    assert artifact["roll_up"]["gates_yaml_untouched_by_this_draft"] is True
    assert "NOT A LOCK" in artifact["status"]
    assert "NOT A CANDIDATE SCORE" in artifact["status"]


def test_gates_yaml_still_has_no_gate_3_thresholds(artifact):
    """Unchanged from v1: gate_3 is untouched, and v2 did not write it."""
    text = (ROOT / "gates.yaml").read_text()
    start = text.index("  gate_3:\n")
    block = text[start : text.index("\n  gate_m4:", start)]
    assert "locked: false" in block
    assert "gate3_retrodiction_floors" not in text
    assert "gate_3a_retrodiction_claiming" not in text
    for forbidden in ("tolerance", "rho:", "null_rule_panel"):
        assert forbidden not in block
    assert (
        _sha256(ROOT / "gates.yaml")
        == artifact["revision_pins"]["gates_yaml_sha256"]
    )


# --------------------------------------------------------------------------
# A6 / B2: the null-rule panel, recomputed independently
# --------------------------------------------------------------------------
def test_panel_deviations_recompute_from_the_staged_printings(
    artifact, independent_series
):
    """Every panel rule at every gated pair, without the builder's panel.

    The rules are re-implemented here from their published FORMULA
    strings, not imported, so this checks the artifact against the
    contract text rather than against itself.
    """
    fit, resolution = independent_series
    T = builder.T_STAR

    def predict(name, years, values, target):
        last = values[-1]
        if name == "persistence":
            return last
        if name == "linear_trend":
            slope, intercept = np.polyfit(
                np.asarray(years, float), np.asarray(values, float), 1
            )
            return slope * target + intercept
        if name.startswith("drift"):
            lag = int(name[5:])
            slope = (last - values[-1 - lag]) / lag
            return last + (target - years[-1]) * slope
        if name.startswith("trend_last"):
            window = int(name[len("trend_last") :])
            slope, intercept = np.polyfit(
                np.asarray(years[-window:], float),
                np.asarray(values[-window:], float),
                1,
            )
            return slope * target + intercept
        if name.startswith("damped"):
            body = name[len("damped") :]
            if "_last" in body:
                phi_text, window_text = body.split("_last")
                window = int(window_text)
            else:
                phi_text, window = body, None
            phi = float(phi_text)
            use_y = years if window is None else years[-window:]
            use_v = values if window is None else values[-window:]
            slope, _ = np.polyfit(
                np.asarray(use_y, float), np.asarray(use_v, float), 1
            )
            horizon = target - years[-1]
            return last + slope * sum(phi**j for j in range(1, horizon + 1))
        if name == "mean_last3":
            return float(np.mean(values[-3:]))
        raise AssertionError(f"unregistered rule {name}")

    checked = 0
    for key, entry in artifact["F2_panel_deviations"].items():
        years = [
            y for y in sorted(fit[key]) if builder.FIT_FIRST_YEAR <= y <= T
        ]
        values = [fit[key][y] for y in years]
        for horizon, row in entry["by_horizon"].items():
            target = row["target_year"]
            assert target == T + int(horizon[1:])
            assert row["realized"] == pytest.approx(resolution[key][target])
            for name, published in row["rules"].items():
                expected = abs(
                    predict(name, years, values, target)
                    - resolution[key][target]
                )
                assert published["deviation"] == pytest.approx(
                    round(float(expected), 6), abs=1e-9
                ), f"{key}@{horizon} rule {name}"
                checked += 1
    assert checked == 18 * 6 * len(builder.NULL_RULE_PANEL)


def test_every_registered_rule_is_in_the_contract_fragment(artifact):
    """D7.3: the panel is contract, not a module dict."""
    fragment = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"]["text"]
    )
    registered = fragment["gates"]["gate_3"]["gate_3a_retrodiction_claiming"][
        "instrument"
    ]["null_rule_panel"]
    assert set(registered) == set(builder.NULL_RULE_PANEL)
    for name, (_fn, formula, _why) in builder.NULL_RULE_PANEL.items():
        assert registered[name] == formula


# --------------------------------------------------------------------------
# The property the whole redesign exists to establish
# --------------------------------------------------------------------------
def test_every_gated_tolerance_is_STRICTLY_below_the_null_panel(artifact):
    """A6 / B2, on all of them -- not a sample, not a spot check."""
    surface = artifact["gated_surface_recommended"]
    bounds = artifact["measurement_lower_bounds"]
    assert surface["n_gated"] > 0
    for pair, row in surface["gated"].items():
        key = pair.split("@")[0]
        lower = bounds[key]["lower_bound_used"]
        assert row["lower_bound"] == lower
        assert row["tolerance"] < row["F2_panel_min"], pair
        assert lower < row["tolerance"], pair
        assert row["F2_panel_min"] > 0.0, pair


def test_tolerances_are_re_derived_from_the_stated_formula(artifact):
    """D7.2: the FORMULA is authoritative, so re-derive from it."""
    surface = artifact["gated_surface_recommended"]
    rho = surface["rho"]
    panel = set(surface["panel"])
    for pair, row in surface["gated"].items():
        key, horizon = pair.split("@")
        rules = artifact["F2_panel_deviations"][key]["by_horizon"][horizon][
            "rules"
        ]
        minimum = min(
            value["deviation"]
            for name, value in rules.items()
            if name in panel
        )
        assert row["F2_panel_min"] == minimum, pair
        assert row["tolerance"] == round(rho * minimum, 3), pair
        assert row["achieved_by"] in panel
        assert rules[row["achieved_by"]]["deviation"] == minimum


def test_no_registered_null_rule_passes_any_gated_pair(artifact):
    """Computed, never asserted -- v1's equivalent claim was false."""
    surface = artifact["gated_surface_recommended"]
    exposure = artifact["null_rule_exposure"]
    assert set(exposure["in_panel_pass_counts"]) == set(surface["panel"])
    assert all(
        count == 0 for count in exposure["in_panel_pass_counts"].values()
    )
    # recomputed here rather than trusting the artifact's own count
    for pair, row in surface["gated"].items():
        key, horizon = pair.split("@")
        rules = artifact["F2_panel_deviations"][key]["by_horizon"][horizon][
            "rules"
        ]
        for name in surface["panel"]:
            if name in rules:
                assert (
                    rules[name]["deviation"] > row["tolerance"]
                ), f"{name} passes {pair}"


def test_residual_leave_one_out_exposure_is_published_and_nonzero(artifact):
    """The honest residual: the panel does NOT close an unregistered rule."""
    exposure = artifact["null_rule_exposure"]
    worst = exposure["worst_leave_one_out_rule"]
    counts = {
        name: row["n_passed_by_the_held_out_rule"]
        for name, row in exposure["leave_one_out"].items()
    }
    assert counts[worst] == max(counts.values())
    assert counts[worst] > 0, (
        "a zero residual would mean the leave-one-out diagnostic is not "
        "measuring anything; it must be published as a margin"
    )
    margins = {m["margin"] for m in artifact["not_certified"]}
    assert "residual_null_rule_exposure" in margins
    assert "the_panel_was_assembled_with_the_answer_in_hand" in margins


def test_demotions_carry_a_reason_and_the_counts_add_up(artifact):
    surface = artifact["gated_surface_recommended"]
    reasons = {
        builder.DEMOTION_EXACT,
        builder.DEMOTION_NO_ROOM,
        builder.DEMOTION_BELOW_FLOOR,
    }
    for pair, row in surface["reported_not_gated"].items():
        assert row["reason"] in reasons, pair
        assert row["detail"]
    assert (
        surface["n_gated"] + surface["n_reported_not_gated"]
        == surface["n_pairs_considered"]
    )
    assert surface["n_pairs_considered"] == 108
    assert surface["n_gated"] < 108, (
        "the honest count must be smaller than v1's 108; if it is not, "
        "the strict-below law is not binding anywhere"
    )


def test_v1_committed_tolerances_are_passed_by_information_null_rules(
    artifact, independent_series
):
    """The finding that forced v2, recomputed against v1's own numbers."""
    fit, resolution = independent_series
    v1 = json.loads(V1_ARTIFACT.read_text())["draft_thresholds"]["cells"]
    deviations = artifact["F2_panel_deviations"]
    passes = {name: 0 for name in builder.NULL_RULE_PANEL}
    for key, entry in deviations.items():
        for horizon, row in entry["by_horizon"].items():
            tolerance = v1[key]["instrument_b_skill_ratio"]["by_horizon"][
                horizon
            ]["tolerance"]
            for name, value in row["rules"].items():
                if value["deviation"] <= tolerance:
                    passes[name] += 1
    # referee A: persistence passes 5 of v1's 108 pairs.
    assert passes["persistence"] == 5
    # referee B: the classical drift rule passes 68 of v1's 108 pairs.
    assert passes["drift3"] == 68
    # and v1's own UNSELECTED rule passes 12.
    assert passes["linear_trend"] == 12


# --------------------------------------------------------------------------
# B1: the candidate reference fence, both directions
# --------------------------------------------------------------------------
def test_the_fenced_reference_holds_only_fit_window_rows(artifact):
    fence = artifact["candidate_reference_fence"]["fenced_reference"]
    assert fence["fit_window"] == [builder.FIT_FIRST_YEAR, builder.T_STAR]
    assert fence["admissible_years"] == list(
        range(builder.FIT_FIRST_YEAR, builder.T_STAR + 1)
    )
    assert 2013 in fence["held_out_years"]
    assert set(fence["held_out_years"]) == set(range(2013, 2023))
    for sex, rows in fence["rows"].items():
        assert sex in ("female", "male")
        years = {int(year) for year in rows}
        assert years == set(fence["admissible_years"])
        assert not years & set(fence["held_out_years"])
    assert fence["n_rows"] == 2 * len(fence["admissible_years"])
    assert fence["rows_sha256"] == builder._sha256_obj(fence["rows"])


def test_the_fenced_in_range_path_cannot_return_a_held_out_row(artifact):
    """The fence test the contract requires: no held-out row, ever.

    Every held-out year raises, including the ones the deployed
    module's nearest-year resolver would happily answer.
    """
    fence = artifact["candidate_reference_fence"]["fenced_reference"]
    for year in fence["held_out_years"]:
        for sex in ("female", "male"):
            with pytest.raises(builder.FenceViolation):
                builder.fenced_row(fence, sex, year)
    # and years outside the table entirely
    for year in (1997, 2023, 2030):
        with pytest.raises(builder.FenceViolation):
            builder.fenced_row(fence, "male", year)
    # while every admissible year is served, from the 2014 printing
    printing = json.loads(
        (EXTERNAL / "ssa_claim_ages_2014supplement.json").read_text()
    )["data"]
    for year in fence["admissible_years"]:
        for sex in ("female", "male"):
            row = builder.fenced_row(fence, sex, year)
            assert (
                row["average_age"] == printing[sex][str(year)]["average_age"]
            )


def test_no_gated_target_year_is_reachable_through_the_fence(artifact):
    """The property that matters: the answer key is not in the object."""
    fence = artifact["candidate_reference_fence"]["fenced_reference"]
    resolution = json.loads(
        (EXTERNAL / "ssa_claim_ages_2023supplement.json").read_text()
    )["data"]
    for horizon in builder.GATED_HORIZONS:
        target = builder.T_STAR + horizon
        assert target in fence["held_out_years"]
        with pytest.raises(builder.FenceViolation):
            builder.fenced_row(fence, "male", target)
        # the value exists in the resolution vintage, and is not here
        assert str(target) in resolution["male"]
    serialized = json.dumps(fence["rows"])
    for horizon in builder.GATED_HORIZONS:
        assert f'"{builder.T_STAR + horizon}"' not in serialized


def test_the_deployed_module_still_fails_the_fence(artifact):
    """Measured, and recorded as a failure -- not quietly asserted fixed.

    If claiming.py is ever fixed this test fails LOUDLY, which is the
    correct direction: the artifact's recorded measurement would then
    be stale and must be rebuilt.
    """
    check = artifact["candidate_reference_fence"][
        "deployed_module_fence_check"
    ]
    assert check["default_reference_is_the_resolution_source"] is True
    assert check["every_gated_target_year_is_in_range"] is True
    assert check["default_branch"]["byte_identical_to_the_answer_key"] is True
    assert check["default_branch"]["nearest_year_used"] is False
    assert artifact["roll_up"]["deployed_module_passes_the_fence"] is False

    from populace_dynamics import claiming

    assert claiming._DEFAULT_REFERENCE.name == check["default_reference_name"]
    assert (claiming.MIN_YEAR, claiming.MAX_YEAR) == (
        check["MIN_YEAR"],
        check["MAX_YEAR"],
    )
    live = claiming.claim_age_distribution("male", 2019)
    truth = json.loads(
        (EXTERNAL / "ssa_claim_ages_2023supplement.json").read_text()
    )["data"]["male"]["2019"]
    assert live.average_age == truth["average_age"]
    assert live.categories["age62"] == truth["categories"]["age62"]
    assert (
        builder._sha256_path(
            ROOT / "src" / "populace_dynamics" / "claiming.py"
        )
        == check["module_sha256"]
    )


def test_the_fence_is_carried_into_the_contract_fragment(artifact):
    fragment = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"]["text"]
    )["gates"]["gate_3"]["gate_3a_retrodiction_claiming"]
    fence = fragment["candidate_reference_fence"]
    assert fence["deployed_module_passes_this_fence_today"] is False
    assert (
        fence["fenced_reference_rows_sha256"]
        == artifact["candidate_reference_fence"]["fenced_reference"][
            "rows_sha256"
        ]
    )
    assert fence["required_module_change"]


# --------------------------------------------------------------------------
# A7 / A8: the fragment parses, splices, and says what the artifact says
# --------------------------------------------------------------------------
def test_the_draft_fragment_parses_standalone(artifact):
    fragment = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"]["text"]
    )
    gate = fragment["gates"]["gate_3"]
    assert gate["thresholds"]["locked"] is False
    tranche = gate["gate_3a_retrodiction_claiming"]
    assert tranche["locked"] is False
    assert tranche["status"] == "draft_pending_referee_round"
    assert tranche["gates_yaml_untouched_by_this_draft"] is True
    # the locked gates' top-level shape, not an arm-nested block
    for field in (
        "id",
        "kind",
        "covers",
        "holdout_basis",
        "not_certified",
        "protocol",
        "instrument",
        "scoring",
        "governance",
        "history",
    ):
        assert field in tranche, field
    # exactly two `locked` flags, as the locked gates carry -- never three
    assert json.dumps(tranche).count('"locked"') == 1


def test_the_draft_fragment_splices_into_gates_yaml_and_parses(artifact):
    """Referee A's own check, on a scratch copy. gates.yaml is not touched."""
    before = _sha256(ROOT / "gates.yaml")
    lines = (ROOT / "gates.yaml").read_text().split("\n")
    start = lines.index("  gate_3:")
    end = start + 1
    while end < len(lines) and (
        lines[end].startswith("    ") or not lines[end].strip()
    ):
        end += 1
    spliced = "\n".join(
        lines[:start]
        + artifact["draft_gates_yaml_fragment"]["text"]
        .rstrip("\n")
        .split("\n")
        + lines[end:]
    )
    document = yaml.safe_load(spliced)
    assert set(document["gates"]) >= {
        "gate_1",
        "gate_2",
        "gate_3",
        "gate_m4",
        "gate_w1",
        "gate_m6",
    }
    assert "gate_3a_retrodiction_claiming" in document["gates"]["gate_3"]
    assert _sha256(ROOT / "gates.yaml") == before


def test_the_fragment_carries_exactly_the_artifacts_numbers(artifact):
    """v1's fragment disagreed with its own rule on 28 of 108 pairs."""
    tranche = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"]["text"]
    )["gates"]["gate_3"]["gate_3a_retrodiction_claiming"]
    surface = artifact["gated_surface_recommended"]
    published = {
        f"{cell}@{horizon}": tolerance
        for cell, row in tranche["cells"].items()
        for horizon, tolerance in row.items()
    }
    assert published == {
        pair: row["tolerance"] for pair, row in surface["gated"].items()
    }
    assert tranche["scoring"]["n_gated_pairs"] == surface["n_gated"]
    demoted = {
        f"{cell}@{entry.split()[0]}"
        for cell, entries in tranche["reported_not_gated"].items()
        for entry in entries
    }
    assert demoted == set(surface["reported_not_gated"])
    assert tranche["protocol"]["fit_source_sha256"] == (
        artifact["revision_pins"]["claim_ages_2014_sha256"]
    )
    assert tranche["protocol"]["resolution_source_sha256"] == (
        artifact["revision_pins"]["claim_ages_2023_sha256"]
    )


def test_the_fragment_states_a_pass_rule_with_both_legs(artifact):
    """A7 / B3: v1 published 108 tolerances and no verdict function."""
    tranche = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"]["text"]
    )["gates"]["gate_3"]["gate_3a_retrodiction_claiming"]
    scoring = tranche["scoring"]
    assert "pass_rule" in scoring
    rule = scoring["pass_rule"]
    assert "LEG 1" in rule and "LEG 2" in rule
    assert "EVERY gated (cell, horizon) pair" in rule
    assert "at least 4 of the 5 blocks" in rule
    assert scoring["n_registered_origin_realizations"] == 1
    assert scoring["n_rolling_origin_blocks"] == len(builder.SEEDS)
    assert scoring["conjunction_leg_2"] == "4 of 5 blocks"
    governance = tranche["governance"]
    assert "publishes_regardless" in governance["registration"].lower() or (
        "PUBLISHES REGARDLESS" in governance["registration"]
    )
    assert "one-shot" in governance["registration"]
    assert "no_self_rescue" in governance["amendment_rules"]
    assert governance["amendment_rules"]["inherits"] == "gate_1"
    assert "amendments_only_via" in governance["amendment_rules"]


def test_A8_the_narrowed_description_and_the_missing_margin(artifact):
    defect = artifact["description_defect_A8"]
    assert defect["status"].startswith("PROPOSED TEXT. NOT APPLIED")
    assert defect["current_description_is_in_gates_yaml"] is True
    assert "lock defect" in defect["rule_text_verbatim"]
    narrowed = defect["cure_i_narrowed_description"]
    assert "6.B5.1" in narrowed
    assert "2014-2019" in narrowed
    assert "resolve against administrative publications" not in narrowed
    margins = {m["margin"] for m in artifact["not_certified"]}
    assert "tier2_live_resolution_arm_unscored" in margins
    margin = next(
        m
        for m in artifact["not_certified"]
        if m["margin"] == "tier2_live_resolution_arm_unscored"
    )
    assert "NEVER SUBSTITUTE FOR" in margin["detail"]
    assert "complement rather than substitute" in margin["detail"]
    # and the proposal is text only -- gate_3's description is unchanged
    tranche_parent = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"]["text"]
    )["gates"]["gate_3"]
    assert " ".join(tranche_parent["description"].split()) == " ".join(
        defect["current_description_verbatim"].split()
    )


# --------------------------------------------------------------------------
# Every other correction both referees made, pinned to its measurement
# --------------------------------------------------------------------------
def test_A1_the_award_relative_deviation_is_0_141_not_0_15(artifact):
    correction = artifact["referee_corrections"]["settlement"][
        "A1_award_relative_deviation"
    ]
    assert correction["measured_max_relative_percent"] == pytest.approx(
        0.140845, abs=1e-6
    )
    assert correction["v1_report_said"] == "0.15%"
    assert correction["presents_as"] == "0.141%"
    assert len(correction["all_settled_award_movers"]) == 4


def test_A1_the_revision_sentence_is_in_both_printings_and_absent_from_v1(
    artifact,
):
    block = artifact["referee_corrections"]["settlement"][
        "A1_the_notes_most_on_point_sentences"
    ]
    assert block["present_in_the_2014_printing"] is True
    assert block["present_in_the_2023_printing"] is True
    assert block["absent_from_the_v1_artifact"] is True
    assert "current and prior years" in block["revision_sentence_verbatim"]
    assert block["revision_sentence_verbatim"] not in json.dumps(
        json.loads(V1_ARTIFACT.read_text())
    )
    # v2 carries the publisher's broader statement AGAINST its own finding
    assert "AGAINST IT" in block["why_it_cuts_both_ways"]
    assert "true vintage" in block["why_it_cuts_both_ways"].lower()
    assert artifact["protocol"]["T_star_leakage_class"] == (
        "true_vintage_artifact"
    )


def test_B1_4_terminal_average_age_does_not_move(artifact, independent_series):
    """The half of the evidence v1 omitted, recomputed from the printings."""
    block = artifact["referee_corrections"]["settlement"][
        "B1_4_terminal_average_age_does_not_move"
    ]
    assert block["n_terminal_average_age_cellyears"] == 2
    assert block["n_differing"] == 0
    fit, resolution = independent_series
    for sex in ("female", "male"):
        key = f"claim_average_age|{sex}"
        assert fit[key][2013] == resolution[key][2013]


def test_B3A1_the_6A1_denominator_is_declared_both_ways(artifact):
    block = artifact["referee_corrections"]["settlement"][
        "B3A1_6A1_relative_gap_denominator"
    ]
    assert block["terminal_percent_as_published"] == pytest.approx(8.60)
    assert block["terminal_percent_on_the_reference"] == pytest.approx(7.92)
    assert block["ratio_terminal_over_settled_as_published"] > 6
    assert block["ratio_terminal_over_settled_on_the_reference"] > 6
    # the guard v1's suite carries sits 0.03 from failing on the other one
    assert block["ratio_terminal_over_settled_on_the_reference"] < 6.1


def test_A3_the_scored_window_is_the_quietest_in_the_panel(artifact):
    quiet = artifact["referee_corrections"]["quietest_window_ranking"]
    assert quiet["scored_window"] == "2014-2019"
    assert quiet["scored_window_rank"] == 1
    assert quiet["scored_window_is_the_quietest"] is True
    assert quiet["n_windows_compared"] == 19
    assert quiet["ratio_noisiest_to_scored"] > 2.0
    assert quiet["ranking"][0]["window"] == "2014-2019"
    margins = {m["margin"] for m in artifact["not_certified"]}
    assert "scored_window_is_the_quietest_in_the_panel" in margins


def test_A4_the_shock_window_is_2020_2022_and_scored_side_only(artifact):
    assert artifact["protocol"]["shock_years"] == [2020, 2021, 2022]
    shock = artifact["referee_corrections"]["shock_partition_asymmetry"]
    worst = shock["worst_year_inside_the_fit_window"]
    assert worst["year"] == 2009
    assert worst["sigma_vs_scored_window"] > 30
    assert worst["partitioned_as_shock"] is False
    assert worst["in_fit_window"] is True
    margins = {m["margin"] for m in artifact["not_certified"]}
    assert "shock_window_2020_2022" in margins
    assert "shock_partition_is_scored_side_only" in margins


def test_A3_1_instrument_A_sits_below_a_revision_the_table_made(artifact):
    block = artifact["referee_corrections"]["instrument_and_prose"][
        "A3_1_no_measurable_noise_is_refuted_by_the_artifacts_own_numbers"
    ]
    assert block["observed_settled_share_revision_max"] == 0.1
    assert block["n_such_cells"] == 18
    for tolerance in block["instrument_a_tolerances_ddof1"].values():
        assert tolerance < 0.1


def test_B4_2b_the_v1_rule_text_did_not_produce_the_v1_numbers(artifact):
    block = artifact["referee_corrections"]["instrument_and_prose"][
        "A4_2_B4_2b_the_stated_rule_does_not_produce_the_printed_numbers"
    ]
    assert block["sum_as_committed"] == pytest.approx(184.052)
    assert block["sum_under_the_rule_as_written"] == pytest.approx(165.878)
    assert block["n_pairs_that_change"] == 28
    assert block["every_change_is_downward"] is True
    assert "NEITHER" in block["which_reading_is_law_in_v2"]


def test_R5_the_T_star_2013_counterfactual_is_priced(artifact):
    block = artifact["referee_corrections"]["t_star_2013_counterfactual"]
    assert block["sum_of_tolerances_T_star_2012"] == pytest.approx(184.052)
    assert block["sum_of_tolerances_T_star_2013"] == pytest.approx(155.820)
    assert block["ratio"] == pytest.approx(1.1812, abs=1e-4)
    assert block["n_pairs_looser_under_T_star_2012"] == 84
    low, high = block["average_age_ratio_range"]
    assert low == pytest.approx(1.1429, abs=1e-3)
    assert high == pytest.approx(2.0)


def test_R9_the_ddof_convention_matches_the_rest_of_the_repository(artifact):
    block = artifact["referee_corrections"]["ddof_convention"]
    assert block["cells_the_convention_moves"] == ["claim_share.age67_69|male"]
    bounds = artifact["measurement_lower_bounds"]
    moved = bounds["claim_share.age67_69|male"]
    assert moved["instrument_a_mean_k_sd_v1_ddof0"] == 0.06
    assert moved["instrument_a_mean_k_sd_ddof1"] == 0.066
    for entry in bounds.values():
        assert entry["F1_block_summary_ddof1"]["ddof"] == 1
    # and the guard v1 lacked
    assert builder._summarize([1.0])["sd"] == 0.0


def test_D6_the_report_only_globs_matched_nothing(artifact):
    block = artifact["referee_corrections"]["instrument_and_prose"][
        "D6_report_only_globs_match_nothing"
    ]
    assert block["n_covered_earnings_glob_matches"] == 0
    assert len(block["actual_covered_earnings_cell_names"]) == 4
    assert block["disability_cells_the_glob_misses"] == [
        "di_worker_termination_rate"
    ]
    # the v2 fragment enumerates instead
    tranche = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"]["text"]
    )["gates"]["gate_3"]["gate_3a_retrodiction_claiming"]
    for entry in tranche["report_only"]:
        assert "*" not in entry


def test_R14_the_horizon_diagnostic_is_published_per_unit(artifact):
    block = artifact["horizon_monotonicity_by_unit"]["groups"]
    assert block["shares_percentage_points"]["n_cells"] == 16
    assert block["average_age_years"]["n_cells"] == 2
    assert block["shares_percentage_points"]["unit"].startswith(
        "percentage points"
    )
    assert block["average_age_years"]["unit"] == "years"
    # every published horizon series is single-unit: v1's mixed key is
    # named only in the correction prose, never as a v2 data key
    assert set(block) == {"shares_percentage_points", "average_age_years"}
    for group in block.values():
        assert set(group["pooled_F2_panel_min_by_horizon"]) == {
            f"h{h}" for h in builder.GATED_HORIZONS
        }

    def has_key(node, name):
        if isinstance(node, dict):
            return name in node or any(has_key(v, name) for v in node.values())
        if isinstance(node, list):
            return any(has_key(v, name) for v in node)
        return False

    assert not has_key(artifact, "pooled_mean_across_eligible_cells")


def test_A5_the_rolling_origins_are_nested_prefixes_not_replications(
    artifact,
):
    rolling = artifact["rolling_origin_provenance"]
    assert "NESTED PREFIXES" in rolling["why_no_dispersion_is_taken_from_it"]
    assert "PROVENANCE AND ROBUSTNESS ONLY" in rolling["status"]
    census = rolling["block_shape_census"]
    assert census, "block shapes must be published, not summarised as 5"
    # v1 reported n_seeds: 5 for every block set; the real shapes are not 5x1
    assert any(
        "1" in shape for shape in census
    ), "the single-observation blocks must be visible"
    for cell in rolling["cells"].values():
        for entry in cell.values():
            assert entry["blocks_are_equal_sized"] is False
            assert entry["n_single_observation_blocks"] >= 1
    # and nothing numeric reads them
    assert "rolling" not in json.dumps(artifact["gated_surface_recommended"])
    margins = {m["margin"] for m in artifact["not_certified"]}
    assert "no_replication" in margins


def test_A9_the_TR_anchor_is_relabelled_true_vintage(artifact):
    block = artifact["referee_corrections"]["instrument_and_prose"][
        "A9_the_TR_anchor_is_true_vintage_not_pseudo_vintage"
    ]
    assert "2014-07-28" in block["correction"]
    assert "TRUE-VINTAGE" in block["correction"]
    margins = {m["margin"] for m in artifact["not_certified"]}
    assert "the_TR_anchor_is_true_vintage" in margins


def test_the_roll_up_reports_the_honest_counts(artifact):
    roll = artifact["roll_up"]
    surface = artifact["gated_surface_recommended"]
    assert roll["n_gated_v1"] == 108
    assert roll["n_gated_v2"] == surface["n_gated"]
    assert roll["n_gated_v2"] < roll["n_gated_v1"]
    assert roll["sum_of_tolerances_v2"] == surface["sum_of_tolerances"]
    assert roll["sum_of_tolerances_v1"] == 184.052
    assert roll["tightening_factor"] > 3.0
    assert roll["registered_null_rules_passing_a_gated_pair"] == 0
    assert roll["worst_leave_one_out_exposure"] > 0
    assert roll["deployed_module_passes_the_fence"] is False


def test_the_sensitivity_grid_is_published_for_every_panel_and_rho(artifact):
    grid = artifact["gated_surface_sensitivity"]
    assert set(grid) == set(builder.PANEL_DEFINITIONS)
    for by_rho in grid.values():
        assert set(by_rho) == {str(r) for r in builder.RHO_SENSITIVITY}
        for surface in by_rho.values():
            assert surface["n_gated"] + surface["n_reported_not_gated"] == 108
    # the binding panel is the strictest: it gates fewest and sums least
    binding = grid[builder.BINDING_PANEL]["0.75"]
    v1_panel = grid["panel_v1_registered"]["0.75"]
    assert binding["n_gated"] < v1_panel["n_gated"]
    assert binding["sum_of_tolerances"] < v1_panel["sum_of_tolerances"]
    # v1's two-rule panel gates all 108 -- which is exactly the defect
    assert v1_panel["n_gated"] == 108
