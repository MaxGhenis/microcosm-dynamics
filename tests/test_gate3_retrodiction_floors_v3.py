"""Pin the gate-3 retrodiction-arm floor artifact v3.

v3 answers the seven findings an INDEPENDENT VERIFIER returned against
v2. This suite pins each of them, and pins them by RE-DERIVATION rather
than by literal wherever a literal could drift:

* finding 1 -- the widened 55-rule panel is recomputed here from the
  staged printings, from the FORMULA STRINGS the artifact publishes,
  without calling the builder's panel; every gated tolerance is shown
  strictly below the widened panel minimum; no registered rule passes a
  gated pair; and the out-of-panel probe residual is re-measured;
* finding 2 -- leg 2's blocks are one global stride-5 partition, the
  same five sets at every cell and horizon, with the admissible origin
  list per horizon recomputed and no block free under the fence;
* finding 3 -- every count the report may state is resolved from its own
  dotted artifact path, and the stale v1-shaped counts appear nowhere
  but in the forbidden list;
* finding 4 -- gated + eligible_not_gated + report_only is exactly the
  35-cell registry, with all 17 non-eligible cells named and reasoned;
* finding 5 -- the power cap is recomputed from its stated derivation
  and its effect measured here and on v2's committed surface;
* finding 6 -- the tie rule is exercised on all three of the verifier's
  exact ties and on every gated tolerance;
* finding 7 -- both A8 cures are present as complete alternative
  fragment texts; cure A narrows ``gate_3.description`` and declares the
  ``gate_3b_live_resolution`` sibling where cure B does neither; the two
  tranches are equal object-for-object once the cure label and the one
  ``satisfied_how`` field are set aside; and v3 chooses neither.

v1 and v2 are untouched: their artifacts, their builders and their 31-
and 41-test suites are byte-identical on this branch and still pass.
``gates.yaml`` is untouched by v3 and by this suite; gate_3 stays at
``locked: false`` with no thresholds.
"""

from __future__ import annotations

import hashlib
import json
import sys
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

import numpy as np
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
EXTERNAL = ROOT / "data" / "external"
sys.path.insert(0, str(ROOT / "scripts"))

import build_gate3_retrodiction_floors_v3 as builder  # noqa: E402

ARTIFACT = RUNS / "gate3_retrodiction_floors_v3.json"
ENV_SIDECAR = RUNS / "gate3_retrodiction_floors_v3.env.json"
INPUT_SIDECAR = RUNS / "gate3_retrodiction_floors_v3.inputs.json"
BUILDER = ROOT / "scripts" / "build_gate3_retrodiction_floors_v3.py"

V1_ARTIFACT = RUNS / "gate3_retrodiction_floors_v1.json"
V1_BUILDER = ROOT / "scripts" / "build_gate3_retrodiction_floors.py"
V2_ARTIFACT = RUNS / "gate3_retrodiction_floors_v2.json"
V2_BUILDER = ROOT / "scripts" / "build_gate3_retrodiction_floors_v2.py"
V1_ARTIFACT_SHA256 = (
    "d78721185856650b1898a7e21d31203c4f0cf0f29e5c79e989f676aec1c78875"
)
V1_BUILDER_SHA256 = (
    "eedf2485c48daee3a8d52d214b52f98a17892e466a508400c7281856d1fae720"
)
V2_ARTIFACT_SHA256 = (
    "385cb7c5e780f5bd174740542c37da191d7d6ee2fa96babafd1cc7a13614461d"
)
V2_BUILDER_SHA256 = (
    "726ad3a13cbdfc013f9338613df26466af26d5643fec2059769d4d453ad42189"
)

T_STAR = 2012
FIT_FIRST = 1998
HORIZONS = (2, 3, 4, 5, 6, 7)
RHO = 0.75
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
    """Both printings, read WITHOUT the builder or the claiming reader."""

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
# An INDEPENDENT implementation of all 55 registered rules, written from
# the formula strings the artifact publishes -- not imported from the
# builder. Everything below that recomputes a deviation uses these.
# --------------------------------------------------------------------------
def _persistence(years, values, target):
    return float(values[-1])


def _linear(years, values, target):
    slope, intercept = np.polyfit(
        np.asarray(years, float), np.asarray(values, float), 1
    )
    return float(slope * target + intercept)


def _drift(lag):
    def rule(years, values, target):
        if len(values) < lag + 1:
            return None
        slope = (values[-1] - values[-1 - lag]) / lag
        return float(values[-1] + (target - years[-1]) * slope)

    return rule


def _trend_last(window):
    def rule(years, values, target):
        if len(values) < window:
            return None
        slope, intercept = np.polyfit(
            np.asarray(years[-window:], float),
            np.asarray(values[-window:], float),
            1,
        )
        return float(slope * target + intercept)

    return rule


def _damped(phi, window=None):
    def rule(years, values, target):
        use_y = years if window is None else years[-window:]
        use_v = values if window is None else values[-window:]
        if len(use_v) < 2:
            return None
        slope, _ = np.polyfit(
            np.asarray(use_y, float), np.asarray(use_v, float), 1
        )
        horizon = target - years[-1]
        return float(
            values[-1] + slope * sum(phi**j for j in range(1, horizon + 1))
        )

    return rule


def _mean_last(window):
    def rule(years, values, target):
        if len(values) < window:
            return None
        return float(np.mean(values[-window:]))

    return rule


def _median_last(window):
    def rule(years, values, target):
        if len(values) < window:
            return None
        return float(np.median(values[-window:]))

    return rule


def _poly(degree, window=None):
    def rule(years, values, target):
        use_y = years if window is None else years[-window:]
        use_v = values if window is None else values[-window:]
        if len(use_v) < degree + 1:
            return None
        coefficients = np.polyfit(
            np.asarray(use_y, float), np.asarray(use_v, float), degree
        )
        return float(np.polyval(coefficients, target))

    return rule


def _holt(alpha, beta):
    def rule(years, values, target):
        level, trend = float(values[0]), float(values[1] - values[0])
        for value in values[1:]:
            previous = level
            level = alpha * value + (1 - alpha) * (level + trend)
            trend = beta * (level - previous) + (1 - beta) * trend
        return float(level + (target - years[-1]) * trend)

    return rule


def _theta(years, values, target):
    slope, intercept = np.polyfit(
        np.asarray(years, float), np.asarray(values, float), 1
    )
    linear = slope * target + intercept
    level = float(values[0])
    for value in values[1:]:
        level = 0.3 * value + 0.7 * level
    return float(0.5 * level + 0.5 * linear)


def _blend(first, second, weight):
    def rule(years, values, target):
        a = first(years, values, target)
        b = second(years, values, target)
        if a is None or b is None:
            return None
        return float(weight * a + (1 - weight) * b)

    return rule


INDEPENDENT_PANEL = {
    "persistence": _persistence,
    "linear_trend": _linear,
    "drift1": _drift(1),
    "drift2": _drift(2),
    "drift3": _drift(3),
    "drift4": _drift(4),
    "drift5": _drift(5),
    "drift6": _drift(6),
    "drift7": _drift(7),
    "drift10": _drift(10),
    "drift14": _drift(14),
    "trend_last3": _trend_last(3),
    "trend_last4": _trend_last(4),
    "trend_last5": _trend_last(5),
    "trend_last6": _trend_last(6),
    "trend_last7": _trend_last(7),
    "trend_last8": _trend_last(8),
    "trend_last9": _trend_last(9),
    "trend_last10": _trend_last(10),
    "trend_last12": _trend_last(12),
    "damped0.6": _damped(0.6),
    "damped0.75": _damped(0.75),
    "damped0.8": _damped(0.8),
    "damped0.85": _damped(0.85),
    "damped0.9": _damped(0.9),
    "damped0.95": _damped(0.95),
    "damped0.99": _damped(0.99),
    "damped0.5_last5": _damped(0.5, 5),
    "damped0.7_last5": _damped(0.7, 5),
    "damped0.8_last5": _damped(0.8, 5),
    "damped0.7_last10": _damped(0.7, 10),
    "damped0.9_last8": _damped(0.9, 8),
    "mean_last2": _mean_last(2),
    "mean_last3": _mean_last(3),
    "mean_last5": _mean_last(5),
    "mean_last7": _mean_last(7),
    "median_last2": _median_last(2),
    "median_last3": _median_last(3),
    "median_last5": _median_last(5),
    "median_last7": _median_last(7),
    "quad_full": _poly(2),
    "quad_last8": _poly(2, 8),
    "cubic_full": _poly(3),
    "cubic_last8": _poly(3, 8),
    "holt(.3,.1)": _holt(0.3, 0.1),
    "holt(.5,.2)": _holt(0.5, 0.2),
    "holt(.8,.3)": _holt(0.8, 0.3),
    "theta": _theta,
    "blend_pers_lin_50": _blend(_persistence, _linear, 0.5),
    "blend_pers_lin_25": _blend(_persistence, _linear, 0.25),
    "blend_pers_lin_75": _blend(_persistence, _linear, 0.75),
    "blend_pers_drift3_50": _blend(_persistence, _drift(3), 0.5),
    "blend_drift3_trend8_50": _blend(_drift(3), _trend_last(8), 0.5),
    "blend_drift3_drift5_50": _blend(_drift(3), _drift(5), 0.5),
    "blend_d0.8_d0.9_50": _blend(_damped(0.8), _damped(0.9), 0.5),
}


def _independent_deviations(fit, resolution, cells):
    """All 55 rules, all cells, all horizons, from the printings alone."""
    out: dict[str, dict[str, dict[str, float]]] = {}
    for key in cells:
        years = [y for y in sorted(fit[key]) if FIT_FIRST <= y <= T_STAR]
        values = [fit[key][y] for y in years]
        per_horizon = {}
        for horizon in HORIZONS:
            target = T_STAR + horizon
            if target not in resolution[key]:
                continue
            scored = {}
            for name, function in INDEPENDENT_PANEL.items():
                prediction = function(years, values, target)
                if prediction is None:
                    continue
                scored[name] = round(
                    abs(float(prediction) - resolution[key][target]), 6
                )
            per_horizon[f"h{horizon}"] = scored
        out[key] = per_horizon
    return out


def _tolerance(panel_min: float, rho: float = RHO) -> float:
    """The stated tie rule, implemented independently of the builder."""
    return float(
        (Decimal(str(rho)) * Decimal(repr(panel_min))).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_EVEN
        )
    )


def _dig(obj, dotted: str):
    for part in dotted.split("."):
        obj = obj[part]
    return obj


# --------------------------------------------------------------------------
# reproduction, and the predecessors left alone
# --------------------------------------------------------------------------
def test_rebuild_is_byte_identical():
    rebuilt = json.dumps(builder.build(), indent=2) + "\n"
    assert rebuilt == ARTIFACT.read_text()


def test_v1_and_v2_are_read_only_and_unmoved():
    assert _sha256(V1_ARTIFACT) == V1_ARTIFACT_SHA256
    assert _sha256(V1_BUILDER) == V1_BUILDER_SHA256
    assert _sha256(V2_ARTIFACT) == V2_ARTIFACT_SHA256
    assert _sha256(V2_BUILDER) == V2_BUILDER_SHA256


def test_builder_refuses_a_moved_predecessor(monkeypatch):
    monkeypatch.setattr(builder, "V2_ARTIFACT_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="v2 artifact digest moved"):
        builder.build()


def test_artifact_carries_no_wall_clock_no_git(artifact):
    blob = json.dumps(artifact)
    for banned in (
        "repo_commit",
        "reader_commit",
        "timestamp",
        "generated_at",
    ):
        assert banned not in blob, banned
    assert "environment" not in artifact


def test_sidecars(artifact):
    inputs = json.loads(INPUT_SIDECAR.read_text())
    paths = {row["path"] for row in inputs["source_inputs"]}
    assert {
        "runs/gate3_retrodiction_floors_v1.json",
        "runs/gate3_retrodiction_floors_v2.json",
        "gates.yaml",
    } <= paths
    for row in inputs["source_inputs"]:
        assert _sha256(ROOT / row["path"]) == row["sha256"], row["path"]
    environment = json.loads(ENV_SIDECAR.read_text())
    assert "repo_commit" in environment["environment"]


def test_prelock_status_and_no_gate_movement(artifact):
    assert artifact["roll_up"]["locked"] is False
    assert artifact["roll_up"]["gates_yaml_untouched_by_this_draft"] is True
    assert "NOT A LOCK" in artifact["status"]
    assert (
        artifact["roll_up"]["a8_cure_chosen"]
        == "NEITHER -- the ratifying round decides"
    )


def test_gates_yaml_still_has_no_gate_3_thresholds(artifact):
    document = yaml.safe_load((ROOT / "gates.yaml").read_text())
    gate = document["gates"]["gate_3"]
    assert set(gate) == {"name", "description", "thresholds"}
    assert gate["thresholds"] == {"locked": False}
    assert (
        _sha256(ROOT / "gates.yaml")
        == artifact["revision_pins"]["gates_yaml_sha256"]
    )


# --------------------------------------------------------------------------
# FINDING 1 -- the widened panel, recomputed from the printings
# --------------------------------------------------------------------------
def test_the_panel_holds_55_rules_with_their_provenance(artifact):
    panel = artifact["null_rule_panel"]
    assert panel["panel_version"] == 3
    assert panel["n_rules"] == 55
    assert len(panel["rules"]) == 55
    assert set(panel["rules"]) == set(INDEPENDENT_PANEL)
    # 11 carried from v2 (2 of them v1's), 41 the verifier's script
    # defines, 3 more its prose names
    counts = panel["provenance_counts"]
    assert sum(counts.values()) == 55
    assert sorted(counts.values()) == [2, 3, 9, 41]
    assert "quad_last8" in panel["rules"]
    assert "23 of v2's" in panel["rules"]["quad_last8"]["source"]


def test_panel_deviations_recompute_from_the_staged_printings(
    artifact, independent_series
):
    """All 55 rules x 18 cells x 6 horizons, from the formula strings."""
    fit, resolution = independent_series
    cells = sorted(artifact["F2_panel_deviations"])
    mine = _independent_deviations(fit, resolution, cells)
    checked = 0
    for key, entry in artifact["F2_panel_deviations"].items():
        for horizon, row in entry["by_horizon"].items():
            assert row["realized"] == round(
                resolution[key][row["target_year"]], 6
            )
            for name, scored in row["rules"].items():
                assert name in mine[key][horizon], (key, horizon, name)
                assert scored["deviation"] == mine[key][horizon][name], (
                    key,
                    horizon,
                    name,
                )
                checked += 1
    assert checked == 18 * 6 * 55


def test_every_gated_tolerance_is_strictly_below_the_widened_panel(
    artifact, independent_series
):
    """The property the whole v3 redesign exists to establish."""
    fit, resolution = independent_series
    cells = sorted(artifact["F2_panel_deviations"])
    mine = _independent_deviations(fit, resolution, cells)
    surface = artifact["gated_surface_recommended"]
    assert surface["n_gated"] > 0
    for pair, row in surface["gated"].items():
        key, horizon = pair.split("@")
        panel_min = min(mine[key][horizon].values())
        assert row["F2_panel_min"] == panel_min, pair
        assert row["lower_bound"] < row["tolerance"] < panel_min, pair
        assert row["tolerance"] <= row["power_cap"], pair


def test_tolerances_are_re_derived_from_the_stated_formula(artifact):
    surface = artifact["gated_surface_recommended"]
    for pair, row in surface["gated"].items():
        assert row["tolerance"] == _tolerance(row["F2_panel_min"]), pair


def test_no_registered_null_rule_passes_any_gated_pair(
    artifact, independent_series
):
    fit, resolution = independent_series
    cells = sorted(artifact["F2_panel_deviations"])
    mine = _independent_deviations(fit, resolution, cells)
    surface = artifact["gated_surface_recommended"]
    for name in INDEPENDENT_PANEL:
        passes = [
            pair
            for pair, row in surface["gated"].items()
            if mine[pair.split("@")[0]][pair.split("@")[1]].get(name, 1e9)
            <= row["tolerance"]
        ]
        assert passes == [], (name, passes)
    assert artifact["null_rule_exposure"]["in_panel_pass_counts"] == {
        name: 0 for name in INDEPENDENT_PANEL
    }


def test_the_out_of_panel_residual_is_measured_not_leave_one_out(artifact):
    exposure = artifact["null_rule_exposure"]
    probe = exposure["out_of_panel_probe_set"]
    assert probe["n_probes"] == 35
    assert set(probe["results"]) == set(probe["formulas"])
    assert not set(probe["results"]) & set(
        artifact["null_rule_panel"]["rules"]
    )
    worst = probe["worst_probe"]
    assert probe["worst_probe_n_passed"] == max(
        row["n_passed_of_the_gated_surface"]
        for row in probe["results"].values()
    )
    assert (
        probe["results"][worst]["n_passed_of_the_gated_surface"]
        == probe["worst_probe_n_passed"]
    )
    # the residual is NOT zero and is NOT the leave-one-out number
    assert probe["worst_probe_n_passed"] > 0
    assert "THE PANEL'S EXPOSURE TO ITS OWN MEMBERS" in (
        exposure["what_leave_one_out_measures"]
    )
    margin = next(
        row
        for row in artifact["not_certified"]
        if row["margin"] == "residual_null_rule_exposure"
    )
    assert str(probe["worst_probe_n_passed"]) in margin["detail"]
    assert worst in margin["detail"]


def test_the_probe_results_recompute_against_the_gated_surface(artifact):
    """Each probe's pass list is re-derived from the stored deviations."""
    surface = artifact["gated_surface_recommended"]
    probes = artifact["null_rule_exposure"]["out_of_panel_probe_set"]
    for name, row in probes["results"].items():
        recomputed = sorted(
            pair
            for pair, gated in surface["gated"].items()
            if name
            in artifact["probe_deviations"][pair.split("@")[0]]["by_horizon"][
                pair.split("@")[1]
            ]["rules"]
            and artifact["probe_deviations"][pair.split("@")[0]]["by_horizon"][
                pair.split("@")[1]
            ]["rules"][name]["deviation"]
            <= gated["tolerance"]
        )
        assert row["pairs"] == recomputed, name
        assert row["n_passed_of_the_gated_surface"] == len(recomputed)


def test_the_admission_procedure_direction_claim_is_true(artifact):
    """Admitting rules may only tighten and only shrink. Measured."""
    counterfactual = artifact["null_rule_exposure"][
        "counterfactual_if_every_probe_were_admitted"
    ]
    assert counterfactual["gated_set_is_a_subset_of_the_v3_gated_set"] is True
    assert counterfactual["no_tolerance_loosened"] is True
    assert (
        counterfactual["n_gated"]
        <= artifact["gated_surface_recommended"]["n_gated"]
    )
    procedure = artifact["null_rule_panel"]["admission_procedure"]
    for phrase in (
        "INFORMATION-NULL",
        "DETERMINISTIC",
        "panel_version",
        "can only SHRINK",
        "NO SELF-RESCUE",
    ):
        assert phrase in procedure, phrase


def test_the_gated_count_fell_and_is_reported_as_such(artifact):
    roll = artifact["roll_up"]
    assert roll["n_gated_v1"] == 108
    assert roll["n_gated_v2"] == 88
    assert roll["n_gated_v3"] < roll["n_gated_v2"]
    assert roll["n_panel_rules_v3"] == 55
    assert roll["sum_of_tolerances_v3"] < roll["sum_of_tolerances_v2"]
    margin = next(
        row
        for row in artifact["not_certified"]
        if row["margin"] == "the_gateable_surface_is_small_and_got_smaller"
    )
    assert str(roll["n_gated_v3"]) in margin["detail"]


# --------------------------------------------------------------------------
# FINDING 6 -- the tie rule
# --------------------------------------------------------------------------
def test_the_three_verifier_ties_resolve_under_the_stated_convention(
    artifact,
):
    fixture = artifact["tie_rule_fixture"]["ties"]
    assert len(fixture) == 3
    expected = {
        "claim_share.age63|male@h5": 0.202,
        "claim_share.age63|male@h7": 0.128,
        "claim_share.disability_conversion|male@h3": 0.068,
    }
    for row in fixture:
        assert row["matches"] is True, row["pair_in_v2"]
        assert (
            row["v3_tolerance_under_ROUND_HALF_EVEN"]
            == expected[row["pair_in_v2"]]
        )
        # recomputed here, independently of the builder
        assert (
            _tolerance(row["exact_deviation"]) == expected[row["pair_in_v2"]]
        )
    # and the one that moves against v2 is the one the verifier named
    moved = [
        row
        for row in fixture
        if row["v2_committed"] is not None
        and row["v2_committed"] != row["v3_tolerance_under_ROUND_HALF_EVEN"]
    ]
    assert [row["pair_in_v2"] for row in moved] == [
        "claim_share.age63|male@h5"
    ]


def test_the_tie_rule_is_stated_in_the_contract(artifact):
    for text in (
        artifact["protocol"]["tie_rule"],
        artifact["draft_gates_yaml_fragment"]["text_cure_A"],
        artifact["draft_gates_yaml_fragment"]["text_cure_B"],
    ):
        assert "ROUND_HALF_EVEN" in text
        assert "6 decimal places" in text or "6-dp" in text


def test_the_tie_rule_uses_exact_decimal_not_binary_float():
    """0.2025 is exactly representable in Decimal, not in binary."""
    assert builder.tolerance_from(0.27, 0.75) == 0.202
    assert builder.tolerance_from(0.17, 0.75) == 0.128
    assert builder.tolerance_from(0.09, 0.75) == 0.068
    # half-to-even, not half-up, on two exact ties at rho = 0.5:
    # 0.0125 -> 0.012 (2 is even) and 0.0135 -> 0.014 (4 is even)
    assert builder.tolerance_from(0.025, 0.5) == 0.012
    assert builder.tolerance_from(0.027, 0.5) == 0.014


# --------------------------------------------------------------------------
# FINDING 5 -- the power cap
# --------------------------------------------------------------------------
def test_the_power_cap_is_recomputed_from_its_stated_derivation(artifact):
    """cap = (1 - 1/1.5) * (realized - origin(unit)), origins 0 and 62."""
    factor = 1.0 - 1.0 / 1.5
    assert artifact["power_cap"]["factor"] == factor
    assert artifact["power_cap"]["metric_origins"] == {
        "abs_pp": 0.0,
        "abs_years": 62.0,
    }
    surface = artifact["gated_surface_recommended"]
    for pair, row in surface["gated"].items():
        key = pair.split("@")[0]
        unit = artifact["F2_panel_deviations"][key]["metric"]
        origin = 0.0 if unit == "abs_pp" else 62.0
        expected = float(
            (
                Decimal(str(factor))
                * Decimal(repr(round(row["realized"] - origin, 6)))
            ).quantize(Decimal("0.000001"))
        )
        assert row["power_cap"] == expected, pair
        assert row["tolerance"] <= row["power_cap"], pair


def test_the_power_cap_demotes_what_it_says_it_demotes(artifact):
    cap = artifact["power_cap"]
    surface = artifact["gated_surface_recommended"]
    assert cap["n_demoted_on_the_v3_surface"] == len(
        cap["demoted_on_the_v3_surface"]
    )
    assert (
        surface["demotion_census"]["tolerance_exceeds_the_power_cap"]
        == cap["n_demoted_on_the_v3_surface"]
    )
    # it is not a token: it bites on v2's committed surface and harder
    # on the v1 two-rule panel
    assert cap["v2_surface_size_without_the_cap"] == 88
    assert cap["demoted_if_applied_to_the_v2_surface"] == [
        "claim_share.age70plus|male@h7"
    ]
    assert cap["n_demoted_if_applied_to_the_v1_panel_surface"] > 0
    assert cap["v1_panel_surface_size_without_the_cap"] == 108


def test_the_power_cap_is_in_both_fragment_texts(artifact):
    for cure in ("A", "B"):
        text = artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
        assert "power_cap" in text
        assert "ln(1.5)" in text
        tranche = yaml.safe_load("gates:\n" + text)["gates"]["gate_3"][
            "gate_3a_retrodiction_claiming"
        ]
        assert tranche["instrument"]["power_cap_metric_origins"] == {
            "abs_pp": 0,
            "abs_years": 62,
        }


# --------------------------------------------------------------------------
# FINDING 2 -- leg 2's blocks
# --------------------------------------------------------------------------
def test_leg_2_blocks_are_one_global_partition(artifact):
    rolling = artifact["rolling_origin_provenance"]
    origins = list(range(2004, 2013))
    expected = {str(seed): origins[seed::5] for seed in range(5)}
    assert rolling["blocks"] == expected
    assert rolling["block_sizes"] == [2, 2, 2, 2, 1]
    assert rolling["block_shape"] == "(2, 2, 2, 2, 1)"
    assert rolling["n_single_observation_blocks"] == 1
    # the blocks do not depend on the cell or the horizon: every
    # (cell, horizon) reports its origins inside the SAME five sets
    for key, per_horizon in rolling["cells"].items():
        for horizon, row in per_horizon.items():
            for seed, members in row["origins_in_each_block"].items():
                assert set(members) <= set(expected[seed]), (key, horizon)
                assert set(members) == set(expected[seed]) & set(
                    row["admissible_origins"]
                )


def test_leg_2_admissible_origins_recompute(artifact):
    """The exact origin list per horizon, from the exclusion rule."""
    excluded = set(artifact["protocol"]["excluded_target_years"])
    rolling = artifact["rolling_origin_provenance"]
    for horizon in HORIZONS:
        expected = [
            origin
            for origin in range(2004, 2013)
            if (origin + horizon) not in excluded
        ]
        assert (
            rolling["admissible_origins_by_horizon"][f"h{horizon}"] == expected
        )
        assert len(expected) == 8
    # and every cell agrees with the global list
    for key, per_horizon in rolling["cells"].items():
        for horizon, row in per_horizon.items():
            assert (
                row["admissible_origins"]
                == rolling["admissible_origins_by_horizon"][horizon]
            ), (key, horizon)


def test_no_leg_2_block_is_free_under_the_fence(artifact):
    rolling = artifact["rolling_origin_provenance"]
    excluded = set(artifact["protocol"]["excluded_target_years"])
    assert rolling["no_block_is_free_under_the_fence"] is True
    for seed, entry in rolling["block_reach_under_the_fence"].items():
        post = [
            (origin, horizon)
            for origin in entry["origins"]
            for horizon in HORIZONS
            if (origin + horizon) not in excluded and origin + horizon > T_STAR
        ]
        assert entry["n_with_a_post_T_star_target"] == len(post), seed
        assert post, seed


def test_the_pass_rule_states_one_block_rule_in_both_texts(artifact):
    rule = artifact["pass_rule_draft"]["pass_rule"]
    assert "partitioned ONCE" in rule
    assert "does not depend on the cell" in rule
    assert "imposes NO CONSTRAINT" in rule
    assert "at least 4 of the 5 blocks" in rule
    for cure in ("A", "B"):
        tranche = yaml.safe_load(
            "gates:\n"
            + artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
        )["gates"]["gate_3"]["gate_3a_retrodiction_claiming"]
        assert tranche["scoring"]["pass_rule"] == rule
        assert tranche["scoring"]["block_shape"] == "(2, 2, 2, 2, 1)"
        assert tranche["scoring"]["n_rolling_origins"] == 9
        for horizon in HORIZONS:
            assert (
                tranche["scoring"]["admissible_origins_by_horizon"][
                    f"h{horizon}"
                ]
                == artifact["rolling_origin_provenance"][
                    "admissible_origins_by_horizon"
                ][f"h{horizon}"]
            )


# --------------------------------------------------------------------------
# FINDING 3 -- the report's counts come from the artifact
# --------------------------------------------------------------------------
def test_every_report_count_resolves_to_its_artifact_path(artifact):
    counts = artifact["report_counts"]["sentences"]
    assert counts
    for name, entry in counts.items():
        resolved = _dig(artifact, entry["artifact_path"])
        assert entry["value"] == resolved, name
        assert str(resolved) in entry["sentence"], name


def test_the_report_counts_cover_the_numbers_that_moved(artifact):
    counts = artifact["report_counts"]["sentences"]
    for required in (
        "n_gated",
        "n_reported_not_gated",
        "n_panel_rules",
        "worst_probe_n_passed",
        "n_rolling_origins",
        "block_shape",
        "n_registry_cells",
        "n_report_only",
        "n_cap_demotions",
    ):
        assert required in counts, required


def test_the_stale_v1_shaped_counts_appear_only_in_the_forbidden_list(
    artifact,
):
    blob = json.dumps(artifact)
    forbidden = artifact["report_counts"]["forbidden_strings"]
    assert forbidden
    for text in forbidden:
        assert blob.count(text) == 1, (text, blob.count(text))


def test_the_referee_B_misattribution_is_corrected(artifact):
    text = artifact["report_counts"]["misattribution_corrected"]
    assert "Referee B did not write it" in text
    assert "310" in text and "210" in text and "70" in text and "40" in text


# --------------------------------------------------------------------------
# FINDING 4 -- the cell partition
# --------------------------------------------------------------------------
def test_the_cell_partition_covers_the_whole_registry(artifact):
    partition = artifact["cell_partition"]
    v1 = json.loads(V1_ARTIFACT.read_text())
    registry = set(v1["cell_stability"])
    assert len(registry) == 35
    gated = set(partition["gated"])
    eligible_not_gated = set(partition["eligible_not_gated"])
    report_only = set(partition["report_only"])
    assert gated | eligible_not_gated | report_only == registry
    assert not gated & eligible_not_gated
    assert not gated & report_only
    assert not eligible_not_gated & report_only
    assert partition["partition_is_exact"] is True
    assert (
        len(gated) + len(eligible_not_gated) + len(report_only)
        == len(registry)
        == partition["n_registry_cells"]
    )


def test_every_non_eligible_cell_is_named_with_its_reason(artifact):
    partition = artifact["cell_partition"]
    v1 = json.loads(V1_ARTIFACT.read_text())
    non_eligible = sorted(
        key
        for key, entry in v1["cell_stability"].items()
        if not entry["draft_gate_eligible"]
    )
    assert len(non_eligible) == 17
    assert partition["report_only_names"] == non_eligible
    for key in non_eligible:
        entry = partition["report_only"][key]
        assert entry["blocking_reasons"], key
        assert (
            entry["blocking_reasons"]
            == v1["cell_stability"][key]["blocking_reasons"]
        )
    # the two cells v1's globs and v2's enumeration each missed
    assert "di_worker_termination_rate" in partition["report_only"]
    assert "di_stock_average_age" in partition["report_only"]
    assert (
        partition["v1_and_v2_coverage_defect"][
            "n_non_eligible_cells_without_contract_text_v3"
        ]
        == 0
    )


def test_the_fragment_report_only_block_is_an_entry_not_a_comment(artifact):
    for cure in ("A", "B"):
        text = artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
        tranche = yaml.safe_load("gates:\n" + text)["gates"]["gate_3"][
            "gate_3a_retrodiction_claiming"
        ]
        names = [row["cell"] for row in tranche["report_only"]]
        assert names == artifact["cell_partition"]["report_only_names"]
        assert len(names) == 17
        assert "di_worker_termination_rate" in names
        for row in tranche["report_only"]:
            assert row["reasons"], row["cell"]
        # no glob survived
        assert not any("*" in name for name in names)
        assert set(tranche["eligible_not_gated"]) == set(
            artifact["cell_partition"]["eligible_not_gated"]
        )


# --------------------------------------------------------------------------
# FINDING 7 -- A8's two cures, side by side, neither chosen
# --------------------------------------------------------------------------
def test_both_A8_cures_are_written_out(artifact):
    defect = artifact["description_defect_A8"]
    assert "cure_A_referee_A" in defect
    assert "cure_B_referee_B" in defect
    assert "THE_DECISION_THE_RATIFYING_ROUND_MUST_TAKE" in defect
    for cure in ("cure_A_referee_A", "cure_B_referee_B"):
        block = defect[cure]
        for field in (
            "referee",
            "referee_words_verbatim",
            "what_changes_in_the_fragment",
            "proposed_gate_3_description",
            "reason_it_is_right",
            "consequence_D8_sequencing",
            "cost",
        ):
            assert field in block, (cure, field)
    # they are DIFFERENT cures
    assert (
        defect["cure_A_referee_A"]["proposed_gate_3_description"]
        != defect["cure_B_referee_B"]["proposed_gate_3_description"]
    )
    assert (
        defect["cure_B_referee_B"]["proposed_gate_3_description"]
        == defect["current_description_verbatim"]
    )
    assert (
        "v3 implements NEITHER"
        in defect["THE_DECISION_THE_RATIFYING_ROUND_MUST_TAKE"]
    )
    assert "v2 implemented cure B" in defect["what_v2_did"]


def test_the_two_fragment_texts_differ_only_where_the_cure_differs(
    artifact,
):
    fragment = artifact["draft_gates_yaml_fragment"]
    text_a = fragment["text_cure_A"]
    text_b = fragment["text_cure_B"]
    assert text_a != text_b
    parsed_a = yaml.safe_load("gates:\n" + text_a)["gates"]["gate_3"]
    parsed_b = yaml.safe_load("gates:\n" + text_b)["gates"]["gate_3"]
    # cure A narrows gate_3 and declares the sibling; cure B does not
    assert "gate_3b_live_resolution" in parsed_a
    assert "gate_3b_live_resolution" not in parsed_b
    assert parsed_a["description"] != parsed_b["description"]
    assert (
        parsed_b["description"]
        == artifact["description_defect_A8"]["current_description_verbatim"]
    )
    assert parsed_a["thresholds"]["locked"] is False
    assert parsed_b["thresholds"]["locked"] is False
    assert parsed_a["gate_3b_live_resolution"]["thresholds"]["locked"] is (
        False
    )
    # the TRANCHE is identical under both cures except its cure label
    tranche_a = dict(parsed_a["gate_3a_retrodiction_claiming"])
    tranche_b = dict(parsed_b["gate_3a_retrodiction_claiming"])
    assert tranche_a.pop("a8_cure_applied_in_this_text") == "A"
    assert tranche_b.pop("a8_cure_applied_in_this_text") == "B"
    governance_a = tranche_a.pop("governance")
    governance_b = tranche_b.pop("governance")
    assert tranche_a == tranche_b
    assert (
        governance_a["amendment_rules"][
            "description_claims_exactly_the_scored_surface"
        ]["satisfied_how"]
        != governance_b["amendment_rules"][
            "description_claims_exactly_the_scored_surface"
        ]["satisfied_how"]
    )


# --------------------------------------------------------------------------
# the fragment, both texts
# --------------------------------------------------------------------------
@pytest.mark.parametrize("cure", ["A", "B"])
def test_the_draft_fragment_parses_standalone(artifact, cure):
    fragment = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
    )
    gate = fragment["gates"]["gate_3"]
    assert gate["thresholds"]["locked"] is False
    tranche = gate["gate_3a_retrodiction_claiming"]
    assert tranche["locked"] is False
    assert tranche["status"] == "draft_pending_ratifying_round"
    assert tranche["gates_yaml_untouched_by_this_draft"] is True
    for field in (
        "id",
        "kind",
        "covers",
        "holdout_basis",
        "not_certified",
        "protocol",
        "instrument",
        "scoring",
        "cells",
        "reported_not_gated",
        "eligible_not_gated",
        "report_only",
        "candidate_reference_fence",
        "deviation_log",
        "governance",
        "history",
    ):
        assert field in tranche, field
    assert json.dumps(tranche).count('"locked"') == 1


@pytest.mark.parametrize("cure", ["A", "B"])
def test_the_draft_fragment_splices_into_gates_yaml(artifact, cure):
    """Referee A's own check, on a scratch copy. gates.yaml is untouched."""
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
        + artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
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


@pytest.mark.parametrize("cure", ["A", "B"])
def test_the_fragment_carries_exactly_the_artifacts_numbers(artifact, cure):
    tranche = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
    )["gates"]["gate_3"]["gate_3a_retrodiction_claiming"]
    surface = artifact["gated_surface_recommended"]
    flat = {
        f"{key}@{horizon}": tolerance
        for key, row in tranche["cells"].items()
        for horizon, tolerance in row.items()
    }
    assert set(flat) == set(surface["gated"])
    for pair, tolerance in flat.items():
        assert tolerance == surface["gated"][pair]["tolerance"], pair
    assert tranche["scoring"]["n_gated_pairs"] == surface["n_gated"]
    assert (
        tranche["scoring"]["n_gated_cells"]
        == surface["n_cells_with_at_least_one_gated_horizon"]
    )
    assert len(tranche["instrument"]["null_rule_panel"]) == 55
    assert set(tranche["instrument"]["null_rule_panel"]) == set(
        artifact["null_rule_panel"]["rules"]
    )
    for name, formula in tranche["instrument"]["null_rule_panel"].items():
        assert formula == artifact["null_rule_panel"]["rules"][name]["formula"]
    assert tranche["instrument"]["panel_version"] == 3
    demoted = {
        f"{key}@{entry.split()[0]}"
        for key, rows in tranche["reported_not_gated"].items()
        for entry in rows
    }
    assert demoted == set(surface["reported_not_gated"])


@pytest.mark.parametrize("cure", ["A", "B"])
def test_the_fragment_forbids_the_rolling_fallback(artifact, cure):
    """Referee A decision 3, required addition 2 -- absent from v2."""
    tranche = yaml.safe_load(
        "gates:\n" + artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
    )["gates"]["gate_3"]["gate_3a_retrodiction_claiming"]
    text = tranche["instrument"]["rolling_origin_fallback_is_FORBIDDEN"]
    assert "not as a fallback" in text
    assert "REPORTED, NOT GATED" in text


# --------------------------------------------------------------------------
# the fence, re-executed at v3, plus the verifier's two scope limits
# --------------------------------------------------------------------------
def test_the_fence_rebuilds_to_v2s_object(artifact):
    fence = artifact["candidate_reference_fence"]
    assert fence["rebuilt_fence_matches_v2"] is True
    assert fence["fenced_reference"]["fit_window"] == [1998, 2012]
    assert fence["fenced_reference"]["held_out_years"] == list(
        range(2013, 2023)
    )
    rows = fence["fenced_reference"]["rows"]
    for sex in ("female", "male"):
        assert sorted(int(y) for y in rows[sex]) == list(range(1998, 2013))


def test_the_deployed_module_still_fails_the_fence(artifact):
    check = artifact["candidate_reference_fence"][
        "deployed_module_fence_check"
    ]
    assert check["default_reference_is_the_resolution_source"] is True
    assert check["default_branch"]["byte_identical_to_the_answer_key"] is (
        True
    )
    assert artifact["roll_up"]["deployed_module_passes_the_fence"] is False
    assert "STILL FAILS THE FENCE" in (
        artifact["candidate_reference_fence"]["still_open"]
    )


def test_the_fence_names_the_floor_artifacts_too(artifact):
    """Verifier section 1.5: the floors publish all 108 realized values."""
    fence = artifact["candidate_reference_fence"]
    text = fence["also_unreadable_at_run_time"]
    for name in (
        "ssa_claim_ages_2023supplement.json",
        "gate3_retrodiction_floors_v1.json",
        "gate3_retrodiction_floors_v2.json",
        "gate3_retrodiction_floors_v3.json",
    ):
        assert name in text, name
    proof = fence["proof_of_non_readability"]
    assert "FileNotFoundError" in proof
    assert "panel_version" in proof
    for cure in ("A", "B"):
        assert (
            "FileNotFoundError"
            in artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
        )


def test_the_realized_values_are_still_published_here(artifact):
    """The exposure the fence clause names is real, and measured."""
    published = [
        row["realized"]
        for entry in artifact["F2_panel_deviations"].values()
        for row in entry["by_horizon"].values()
    ]
    assert len(published) == 108


def _strings(node):
    """Yield every string in a parsed YAML/JSON tree."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


def test_the_v1_leak_census_is_measured_not_asserted(artifact):
    """The fence clause named a path v1 does not have.

    Fourth-sitting finding: ``also_unreadable_at_run_time`` claimed that
    v1, v2 and v3 each publish the 108 realized values at
    ``F2_panel_deviations[cell].by_horizon[h].realized``.  v1 has no such
    block.  It is not cleaner for that -- it publishes a wider answer key
    at another path -- so the clause now carries a census recomputed
    here, from v1's own bytes, by a route that does not use the builder.
    """
    v1 = json.loads(V1_ARTIFACT.read_text())
    fence = artifact["candidate_reference_fence"]
    census = fence["v1_publishes_the_answer_key_by_another_path"]

    assert "F2_panel_deviations" not in v1
    assert census["v1_has_an_F2_panel_deviations_block"] is False
    assert census["path"] == (
        "reference_values[cell].resolution_vintage_series"
    )

    series = {
        cell: entry["resolution_vintage_series"]
        for cell, entry in v1["reference_values"].items()
    }
    years = sorted({int(year) for s in series.values() for year in s})
    assert census["n_cells"] == len(series)
    assert census["n_values"] == sum(len(s) for s in series.values())
    assert census["year_span"] == [years[0], years[-1]]
    assert census["n_values_after_t_star"] == sum(
        1 for s in series.values() for year in s if int(year) > T_STAR
    )

    realized = [
        (cell, row["target_year"], row["realized"])
        for cell, entry in artifact["F2_panel_deviations"].items()
        for row in entry["by_horizon"].values()
    ]
    assert census["n_realized_in_the_v3_panel"] == len(realized)
    assert census["n_reproduced_exactly_by_v1"] == sum(
        1
        for cell, year, value in realized
        if abs(series.get(cell, {}).get(str(year), 1e9) - value) < 1e-12
    )

    # the clause states the census rather than a family resemblance, and
    # every number in it is one the census measured
    text = fence["also_unreadable_at_run_time"]
    assert "NO F2_panel_deviations block" in text
    assert census["path"] in text
    for value in (
        census["n_cells"],
        census["n_values"],
        census["n_values_after_t_star"],
        census["n_realized_in_the_v3_panel"],
        census["year_span"][0],
        census["year_span"][1],
    ):
        assert str(value) in text, value

    # and both fragment texts carry the corrected clause, not the old one
    for cure in ("A", "B"):
        block = yaml.safe_load(
            artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
        )
        carried = [s for s in _strings(block) if census["path"] in s]
        assert len(carried) == 1, cure
        assert "NO F2_panel_deviations block" in carried[0], cure


# --------------------------------------------------------------------------
# the sensitivity grid and the margins
# --------------------------------------------------------------------------
def test_the_sensitivity_grid_covers_four_panels_and_three_rhos(artifact):
    grid = artifact["gated_surface_sensitivity"]
    assert set(grid) == {
        "panel_v1_registered",
        "panel_v2_eleven",
        "panel_v3_registered",
        "panel_v3_plus_probe_set",
    }
    for by_rho in grid.values():
        assert set(by_rho) == {"0.5", "0.75", "0.9"}
    # the panels are nested, so at a fixed rho a wider panel gates no more
    for rho in ("0.5", "0.75", "0.9"):
        widths = [
            grid[name][rho]["n_gated"]
            for name in (
                "panel_v2_eleven",
                "panel_v3_registered",
                "panel_v3_plus_probe_set",
            )
        ]
        assert widths == sorted(widths, reverse=True), rho
    assert (
        grid["panel_v3_registered"]["0.75"]["n_gated"]
        == artifact["gated_surface_recommended"]["n_gated"]
    )


def test_rho_is_published_but_not_chosen(artifact):
    assert artifact["protocol"]["rho"] == 0.75
    assert artifact["protocol"]["rho_sensitivity"] == [0.5, 0.75, 0.9]
    assert "must set it" in artifact["protocol"]["rho_is_not_chosen_here"]
    for cure in ("A", "B"):
        tranche = yaml.safe_load(
            "gates:\n"
            + artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"]
        )["gates"]["gate_3"]["gate_3a_retrodiction_claiming"]
        assert "MUST SET IT" in (
            tranche["instrument"]["rho_is_a_policy_constant"]
        )


def test_the_margins_carry_v2s_text_where_nothing_moved(artifact):
    v2 = json.loads(V2_ARTIFACT.read_text())
    carried = {row["margin"]: row["detail"] for row in v2["not_certified"]}
    seen = 0
    for row in artifact["not_certified"]:
        if row.get("carried_verbatim_from_v2"):
            assert row["detail"] == carried[row["margin"]], row["margin"]
            seen += 1
    assert seen == 11
    names = {row["margin"] for row in artifact["not_certified"]}
    assert {
        "residual_null_rule_exposure",
        "the_panel_was_assembled_with_the_answer_in_hand",
        "the_gateable_surface_is_small_and_got_smaller",
        "the_panel_is_open_not_complete",
        "leg_2_blocks_are_unequal",
    } <= names


def test_every_verifier_finding_is_answered(artifact):
    answers = artifact["answers_the_verifier"]
    assert len(answers) == 7
    for block in answers.values():
        assert block["verdict_in_the_verifier_report"]
        assert block["closed_by"]
    assert answers["7_A8_two_referee_cures_disagree"]["v3_chooses"] == (
        "NEITHER, deliberately"
    )
    assert (
        artifact["supersedes"]["verifier_verdict_on_v2"]["verdict"]
        == "NOT VERIFIED as lock-ready"
    )
    assert (
        artifact["supersedes"]["verifier_verdict_on_v2"][
            "blocking_referee_findings"
        ]
        == "all three VERIFIED CLOSED"
    )
