"""gate_3 retrodiction arm, floors v2: the answer to the referee round.

PRE-LOCK EVIDENCE, NOT A GATE RUN. ``gates.yaml`` gate_3 still carries
``locked: false`` and no thresholds. This script writes no gate, edits no
gate, scores no candidate, and does not rewrite v1.
``runs/gate3_retrodiction_floors_v1.json`` is read only, and pinned by
digest.

Two independent referees read the v1 package (branch
``gate3/retrodiction-floors``, head e96e06f) and both returned NOT
LOCK-READY. Neither contested the arithmetic: referee A reproduced all
108 tolerances, all 18 rule selections and all 8 reference series;
referee B recomputed 500 reference values, 240 registered-origin
deviations and all 23 deviation-log entries from the raw printings on an
independent implementation. Both found zero discrepancies. What both
refused to ratify is the INSTRUMENT and the CONTRACT.

The three blocking findings this artifact answers
-------------------------------------------------
B1 (referee B, finding 1) -- LEAKAGE BY CONSTRUCTION. The arm's truth
table is the model's default input. ``claiming._DEFAULT_REFERENCE`` is
``data/external/ssa_claim_ages_2023supplement.json`` -- the resolution
source of this very gate -- and ``MIN_YEAR``/``MAX_YEAR`` (1998/2022)
admit every gated target year as in range. Run live, ``claim_age_
distribution('male', 2019)`` returns the 2023 printing's 2019 row
byte-identically, with ``nearest_year_used = False``. A candidate that
reads claiming through the module scores deviation 0 at every gated
pair. ``candidate_reference_fence`` below specifies the fence that
closes this -- a fit-window-restricted reference artifact the candidate
protocol must load -- and records, as a MEASUREMENT, that the deployed
module fails that fence today.

A6 / B2 -- TOLERANCES A NULL RULE PASSES. The artifact's own law
(``floor_design.three_quantities.F2_naive_baseline``) says "a tolerance
at or above it certifies nothing, because a rule carrying no information
past T* already passes". v1 enforced that against exactly two registered
rules and selected between them per CELL on a pooled-over-horizons mean,
so at an individual horizon the chosen rule could be the worse of the
two. Measured: persistence passes 5 of the 108 proposed pairs outright
(referee A) and the textbook drift rule passes 68 of 108 and 9 of 18
cells at every horizon (referee B). v2 registers a PANEL of eleven
information-null rules, takes the baseline as the panel MINIMUM at the
registered origin, and gates a pair only if a tolerance fits STRICTLY
between the measurement lower bound and that minimum. No registered
rule can pass a gated pair, by construction.

A7 / B3 -- NO PASS RULE. v1 published 108 tolerances and no statement of
what passing means. ``pass_rule_draft`` below states the conjunction in
the locked gates' grammar and names the replication basis the
recommended instrument actually has (there are no seeds), with counts.

A8 -- DESCRIPTION BROADER THAN THE SCORED SURFACE. ``description_claims_
exactly_the_scored_surface`` (``gates.yaml:1060-1080``) names gate_3 in
its ``applies_to`` list and calls a broad headline a lock defect.
``description_defect_A8`` below carries the narrowed description and the
missing ``not_certified`` margin AS TEXT. Nothing is applied.

Every other correction both referees made to v1's prose and numbers is
recomputed here and carried in ``referee_corrections``, each with the
measurement that settles it.

What this artifact still does NOT do
------------------------------------
It does not lock, choose rho, or score a candidate. It publishes the
gated count HONESTLY under three nested panels and three values of rho
so the ceremony can see what each choice costs, and it publishes the
residual leave-one-out exposure to a twelfth, unregistered rule.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
V1_BUILDER = REPO / "scripts" / "build_gate3_retrodiction_floors.py"
V1_ARTIFACT = REPO / "runs" / "gate3_retrodiction_floors_v1.json"
ARTIFACT = REPO / "runs" / "gate3_retrodiction_floors_v2.json"
ENV_SIDECAR = ARTIFACT.with_suffix(".env.json")
INPUT_SIDECAR = ARTIFACT.with_suffix(".inputs.json")

#: v1 is READ, never rewritten. Pinned so a moved v1 is a loud failure.
V1_ARTIFACT_SHA256 = (
    "d78721185856650b1898a7e21d31203c4f0cf0f29e5c79e989f676aec1c78875"
)
V1_BUILDER_SHA256 = (
    "eedf2485c48daee3a8d52d214b52f98a17892e466a508400c7281856d1fae720"
)

SCHEMA_VERSION = "gate3_retrodiction_floors.v2"
RUN = "gate3_retrodiction_floors_v2"


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_obj(obj) -> str:
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def _load_v1_builder():
    """Import the v1 builder WITHOUT modifying it.

    v1's builder file is byte-identical to e96e06f on this branch and its
    own test suite still pins it. Everything reusable -- the cell
    registry, the label-verified vintage readers, the metrics -- is taken
    from there rather than re-implemented, so the two artifacts cannot
    drift on a shared definition.
    """
    if _sha256_path(V1_BUILDER) != V1_BUILDER_SHA256:
        raise ValueError(
            "v1 builder digest moved: refusing to build v2 against a "
            "different v1 than the one the referees reviewed"
        )
    spec = importlib.util.spec_from_file_location(
        "build_gate3_retrodiction_floors", V1_BUILDER
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v1b = _load_v1_builder()

T_STAR = v1b.T_STAR  # 2012
FIT_FIRST_YEAR = v1b.FIT_FIRST_YEAR  # 1998
SEEDS = v1b.SEEDS
CLAIM_2014 = v1b.CLAIM_2014
CLAIM_2023 = v1b.CLAIM_2023
METRICS = v1b.METRICS
SEXES = v1b.SEXES
CLAIM_CATEGORIES = v1b.CLAIM_CATEGORIES

#: The gated horizon band, unchanged from v1: targets 2014-2019.
GATED_HORIZONS = (2, 3, 4, 5, 6, 7)

#: rho is a POLICY CONSTANT and is not chosen here. Published at three
#: values, exactly as v1 did, so the ceremony sees what each costs.
RHO_SENSITIVITY = (0.5, 0.75, 0.9)
DRAFT_RHO = 0.75
DRAFT_ROUNDING = 3
DRAFT_K = 4

#: A4 (referee A) / R6 (referee B). gate_m6's own margin partitions
#: 2020-2022, not 2020-2021. v1's data said 2020-2021 while v1's own
#: shock_window_rule string said gate_m6 partitions 2020-2022.
SHOCK_YEARS_V2 = (2020, 2021, 2022)

#: A2 (referee A). "Settled" was measured only at printing age >= 9; the
#: youngest scored row (2019) is 4 printings old at the 2023 resolution
#: vintage. Pinned so a later T* move cannot score a 1-year-old row
#: while citing this arm's settlement finding.
MIN_SETTLEMENT_AGE_PRINTINGS = 4


# --------------------------------------------------------------------------
# ddof: R9 (referee B). Every other floor builder in this repository uses
# ddof=1 and build_disability_floors.py calls it "the floor convention
# shared with the other runs/ artifacts". v1 used ddof=0 -- the only
# ddof=0 site in scripts/ -- and had no size>1 guard. v2 adopts the
# convention and guards.
# --------------------------------------------------------------------------
def _summarize(values: list[float]) -> dict:
    array = np.asarray(values, dtype=float)
    sd = float(array.std(ddof=1)) if array.size > 1 else 0.0
    return {
        "mean": round(float(array.mean()), 6),
        "sd": round(sd, 6),
        "min": round(float(array.min()), 6),
        "max": round(float(array.max()), 6),
        "n_blocks": int(array.size),
        "ddof": 1,
        "values": [round(float(v), 6) for v in array],
    }


# --------------------------------------------------------------------------
# The REGISTERED PANEL of information-null rules (A6 / B2).
#
# A rule is information-null iff it reads only rows of the FIT SOURCE at
# or before the origin. Every rule below satisfies that by construction:
# each receives only (fit_years, values) truncated at the origin, and the
# target year, and cannot see the resolution vintage at all.
#
# The panel is enumerated HERE and mirrored into the contract fragment by
# name and formula, because referee B's D7.3 is correct: a mutable module
# dict that determines every tolerance is not a contract.
# --------------------------------------------------------------------------
def _persistence(years, values, target):
    return float(values[-1])


def _linear_trend(years, values, target):
    slope, intercept = np.polyfit(
        np.asarray(years, dtype=float), np.asarray(values, dtype=float), 1
    )
    return float(slope * target + intercept)


def _drift(lag: int):
    """Classical drift: extend the average slope of the last `lag` years."""

    def rule(years, values, target):
        if len(values) < lag + 1:
            return None
        slope = (values[-1] - values[-1 - lag]) / lag
        return float(values[-1] + (target - years[-1]) * slope)

    return rule


def _trend_last(window: int):
    """OLS on the last `window` fit rows only."""

    def rule(years, values, target):
        if len(values) < window:
            return None
        slope, intercept = np.polyfit(
            np.asarray(years[-window:], dtype=float),
            np.asarray(values[-window:], dtype=float),
            1,
        )
        return float(slope * target + intercept)

    return rule


def _damped(phi: float, window: int | None = None):
    """Damped trend: level + slope * sum(phi^j), j = 1..h."""

    def rule(years, values, target):
        use_y = years if window is None else years[-window:]
        use_v = values if window is None else values[-window:]
        if len(use_v) < 2:
            return None
        slope, _ = np.polyfit(
            np.asarray(use_y, dtype=float),
            np.asarray(use_v, dtype=float),
            1,
        )
        horizon = target - years[-1]
        damping = sum(phi**j for j in range(1, horizon + 1))
        return float(values[-1] + slope * damping)

    return rule


def _mean_last3(years, values, target):
    if len(values) < 3:
        return None
    return float(np.mean(values[-3:]))


NULL_RULE_PANEL = {
    "persistence": (
        _persistence,
        "pred(T*+h) = v(T*)",
        "registered in v1",
    ),
    "linear_trend": (
        _linear_trend,
        "pred(T*+h) = OLS(v on year, fit window 1998..T*) at T*+h",
        "registered in v1",
    ),
    "drift3": (
        _drift(3),
        "pred(T*+h) = v(T*) + h * (v(T*) - v(T*-3)) / 3",
        "referee B finding 2: passes 68 of v1's 108 pairs",
    ),
    "drift5": (
        _drift(5),
        "pred(T*+h) = v(T*) + h * (v(T*) - v(T*-5)) / 5",
        "referee B: passes 54 of v1's 108 pairs",
    ),
    "trend_last5": (
        _trend_last(5),
        "pred(T*+h) = OLS on the last 5 fit rows, at T*+h",
        "referee B: passes 58 of v1's 108 pairs",
    ),
    "trend_last8": (
        _trend_last(8),
        "pred(T*+h) = OLS on the last 8 fit rows, at T*+h",
        "referee B: passes 38 of v1's 108 pairs",
    ),
    "trend_last10": (
        _trend_last(10),
        "pred(T*+h) = OLS on the last 10 fit rows, at T*+h",
        "referee B: passes 41 of v1's 108 pairs",
    ),
    "damped0.7_last10": (
        _damped(0.7, 10),
        "pred(T*+h) = v(T*) + slope_last10 * sum(0.7^j, j=1..h)",
        "referee B: passes 53 of v1's 108 pairs",
    ),
    "damped0.8": (
        _damped(0.8),
        "pred(T*+h) = v(T*) + slope_fitwindow * sum(0.8^j, j=1..h)",
        "referee B: passes 43 of v1's 108 pairs",
    ),
    "damped0.9": (
        _damped(0.9),
        "pred(T*+h) = v(T*) + slope_fitwindow * sum(0.9^j, j=1..h)",
        "referee B: passes 51 of v1's 108 pairs",
    ),
    "mean_last3": (
        _mean_last3,
        "pred(T*+h) = mean(v(T*-2), v(T*-1), v(T*))",
        "referee B: passes 12 of v1's 108 pairs",
    ),
}

#: Three NESTED panels, so the ceremony sees the cost of each. The
#: BINDING panel is `panel_full`; the other two are published for
#: comparison, not offered as alternatives that close the hole.
PANEL_DEFINITIONS = {
    "panel_v1_registered": ("persistence", "linear_trend"),
    "panel_brief_minimum": ("persistence", "drift3"),
    "panel_full": tuple(NULL_RULE_PANEL),
}
BINDING_PANEL = "panel_full"


# --------------------------------------------------------------------------
# Series, cells and the measurement lower bound
# --------------------------------------------------------------------------
def _gated_cells(registry: dict) -> list[str]:
    """The 18 draft-eligible claiming cells v1 proposed, in sorted order.

    Taken from v1's own cell_stability rather than re-derived, so v2
    cannot silently widen or narrow the surface it is re-flooring.
    """
    v1 = json.loads(V1_ARTIFACT.read_text())
    return sorted(
        key
        for key, entry in v1["cell_stability"].items()
        if entry["draft_gate_eligible"]
    )


def _lower_bounds(v1: dict, cells: list[str]) -> dict:
    """max(F0, instrument A) per cell, RECOMPUTED at ddof=1 (R9).

    v1 published instrument A at ddof=0. The only cell the convention
    moves is claim_share.age67_69|male (0.060 -> 0.066); the collapse
    finding survives either way, and this records both.
    """
    out = {}
    for key in cells:
        floor_block = v1["floor_vintage_revision"]["cells"][key]
        blocks = floor_block["blocks"]
        means = [blocks[seed]["mean"] for seed in sorted(blocks)]
        summary = _summarize(means)
        f0 = v1["floor_publication_rounding"][key]["floor"]
        instrument_a_ddof1 = max(
            round(summary["mean"] + DRAFT_K * summary["sd"], DRAFT_ROUNDING),
            round(f0, DRAFT_ROUNDING),
        )
        instrument_a_v1 = v1["draft_thresholds"]["cells"][key][
            "instrument_a_mean_k_sd"
        ]["tolerance"]
        out[key] = {
            "publication_rounding_floor_F0": f0,
            "instrument_a_mean_k_sd_ddof1": instrument_a_ddof1,
            "instrument_a_mean_k_sd_v1_ddof0": instrument_a_v1,
            "ddof_changes_this_cell": instrument_a_ddof1 != instrument_a_v1,
            "lower_bound_used": instrument_a_ddof1,
            "F1_block_summary_ddof1": summary,
        }
    return out


def panel_deviations(
    cells: list[str],
    fit_series: dict,
    resolution_series: dict,
    registry: dict,
) -> dict:
    """Every panel rule's deviation at the REGISTERED origin T* = 2012.

    This is the only basis v2 uses for a tolerance. Referee A's decision
    3 and referee B's decision 3 agree: the rolling origins are nested
    prefixes off one realized series, so their block sd is not a
    replication dispersion and cannot carry a mean+k*sd. They are kept
    below as a PROVENANCE record with their true block sizes, and enter
    no tolerance.
    """
    out = {}
    for key in cells:
        metric = METRICS[registry[key]["metric"]]
        fit = fit_series[key]
        realized = resolution_series[key]
        years = [y for y in sorted(fit) if FIT_FIRST_YEAR <= y <= T_STAR]
        values = [fit[y] for y in years]
        per_horizon = {}
        for horizon in GATED_HORIZONS:
            target = T_STAR + horizon
            if target not in realized:
                continue
            rules = {}
            for name, (fn, formula, _why) in NULL_RULE_PANEL.items():
                try:
                    prediction = fn(years, values, target)
                except (ValueError, np.linalg.LinAlgError):
                    prediction = None
                if prediction is None:
                    continue
                rules[name] = {
                    "prediction": round(float(prediction), 6),
                    "deviation": round(
                        float(metric(prediction, realized[target])), 6
                    ),
                    "formula": formula,
                }
            per_horizon[f"h{horizon}"] = {
                "target_year": target,
                "realized": round(float(realized[target]), 6),
                "rules": rules,
                "n_rules_defined": len(rules),
            }
        out[key] = {
            "metric": registry[key]["metric"],
            "unit": registry[key]["unit"],
            "registered_origin": T_STAR,
            "fit_window": [FIT_FIRST_YEAR, T_STAR],
            "by_horizon": per_horizon,
        }
    return out


def _panel_min(entry: dict, panel: tuple[str, ...]) -> tuple[float, str]:
    """Smallest deviation over the panel, and which rule achieves it."""
    candidates = {
        name: row["deviation"]
        for name, row in entry["rules"].items()
        if name in panel
    }
    best = min(candidates, key=lambda name: candidates[name])
    return candidates[best], best


# --------------------------------------------------------------------------
# The v2 tolerance law and the honest gated count (A6 / B2)
# --------------------------------------------------------------------------
TOLERANCE_LAW = (
    "tolerance(cell, h) = round(rho * F2_panel_min(cell, h), 3), where "
    "F2_panel_min is the SMALLEST deviation, at the registered origin "
    "T* = 2012, over EVERY rule in the registered information-null "
    "panel. A (cell, horizon) pair is GATED only if "
    "lower_bound(cell) < tolerance(cell, h) < F2_panel_min(cell, h), "
    "both inequalities STRICT, where lower_bound = max(F0, instrument "
    "A). A pair failing either inequality is REPORTED, NOT GATED, with "
    "the reason recorded. There is no per-cell rule selection: the "
    "minimum is both the selection and the basis, which is what referee "
    "A's decision 3 and referee B's decision 3 independently required."
)

DEMOTION_EXACT = "a_registered_null_rule_is_EXACT_at_this_pair"
DEMOTION_NO_ROOM = "no_strict_room_below_the_null_panel"
DEMOTION_BELOW_FLOOR = (
    "tolerance_not_strictly_above_the_measurement_lower_bound"
)


def gated_surface(
    deviations: dict,
    bounds: dict,
    *,
    panel: tuple[str, ...],
    rho: float,
) -> dict:
    """Apply the tolerance law. Returns gated pairs AND demotions."""
    gated, demoted = {}, {}
    for key, entry in deviations.items():
        lower = bounds[key]["lower_bound_used"]
        for horizon, row in entry["by_horizon"].items():
            if not row["rules"]:
                continue
            floor_value, best_rule = _panel_min(row, panel)
            tolerance = round(rho * floor_value, DRAFT_ROUNDING)
            pair = f"{key}@{horizon}"
            if floor_value <= 0.0:
                demoted[pair] = {
                    "reason": DEMOTION_EXACT,
                    "detail": (
                        f"{best_rule} reproduces the realized value "
                        f"exactly at {row['target_year']}; no positive "
                        "tolerance can sit strictly below zero, so no "
                        "tolerance at this pair can certify skill"
                    ),
                    "F2_panel_min": floor_value,
                    "achieved_by": best_rule,
                    "tolerance_would_be": tolerance,
                    "lower_bound": lower,
                }
                continue
            if not tolerance < floor_value:
                demoted[pair] = {
                    "reason": DEMOTION_NO_ROOM,
                    "detail": (
                        "rounding lifts rho * F2_panel_min to or above "
                        "the panel minimum itself"
                    ),
                    "F2_panel_min": floor_value,
                    "achieved_by": best_rule,
                    "tolerance_would_be": tolerance,
                    "lower_bound": lower,
                }
                continue
            if not lower < tolerance:
                demoted[pair] = {
                    "reason": DEMOTION_BELOW_FLOOR,
                    "detail": (
                        "the panel minimum is so small that rho times "
                        "it lands at or below max(F0, instrument A) -- "
                        "the truth side cannot resolve the difference "
                        "between the candidate and a null rule here"
                    ),
                    "F2_panel_min": floor_value,
                    "achieved_by": best_rule,
                    "tolerance_would_be": tolerance,
                    "lower_bound": lower,
                }
                continue
            gated[pair] = {
                "tolerance": tolerance,
                "F2_panel_min": floor_value,
                "achieved_by": best_rule,
                "lower_bound": lower,
                "target_year": row["target_year"],
                "room_ratio": round(floor_value / lower, 4),
            }
    cells_gated = sorted({pair.split("@")[0] for pair in gated})
    all_horizons = sorted(
        key
        for key in deviations
        if all(
            f"{key}@h{h}" in gated
            for h in GATED_HORIZONS
            if f"h{h}" in deviations[key]["by_horizon"]
        )
        and any(f"{key}@h{h}" in gated for h in GATED_HORIZONS)
    )
    return {
        "panel": list(panel),
        "rho": rho,
        "n_pairs_considered": sum(
            1
            for entry in deviations.values()
            for row in entry["by_horizon"].values()
            if row["rules"]
        ),
        "n_gated": len(gated),
        "n_reported_not_gated": len(demoted),
        "n_cells_with_at_least_one_gated_horizon": len(cells_gated),
        "n_cells_gated_at_every_horizon": len(all_horizons),
        "cells_gated_at_every_horizon": all_horizons,
        "sum_of_tolerances": round(
            sum(row["tolerance"] for row in gated.values()), 3
        ),
        "gated": dict(sorted(gated.items())),
        "reported_not_gated": dict(sorted(demoted.items())),
    }


def null_rule_exposure(
    deviations: dict, surface: dict, bounds: dict, *, panel: tuple[str, ...]
) -> dict:
    """Two proofs that the law does what it claims.

    `in_panel`: every registered rule's pass count against the GATED
    surface. It is 0 for every rule by construction -- a rule in the
    panel cannot beat rho times the panel minimum at rho < 1 -- and is
    computed rather than asserted.

    `leave_one_out`: the honest residual. Hold each rule out of the
    panel, re-derive the surface from the other ten, and count the pairs
    the held-out rule then passes. This is the artifact's estimate of
    exposure to a TWELFTH rule nobody registered, and it is NOT zero.
    """
    in_panel = {}
    for name in panel:
        passes = 0
        for pair, row in surface["gated"].items():
            key, horizon = pair.split("@")
            rules = deviations[key]["by_horizon"][horizon]["rules"]
            if name in rules and rules[name]["deviation"] <= row["tolerance"]:
                passes += 1
        in_panel[name] = passes

    leave_one_out = {}
    for held in panel:
        reduced = tuple(name for name in panel if name != held)
        sub = gated_surface(
            deviations, bounds, panel=reduced, rho=surface["rho"]
        )
        passes = [
            pair
            for pair, row in sub["gated"].items()
            if held
            in deviations[pair.split("@")[0]]["by_horizon"][
                pair.split("@")[1]
            ]["rules"]
            and deviations[pair.split("@")[0]]["by_horizon"][
                pair.split("@")[1]
            ]["rules"][held]["deviation"]
            <= row["tolerance"]
        ]
        leave_one_out[held] = {
            "n_gated_without_this_rule": sub["n_gated"],
            "n_passed_by_the_held_out_rule": len(passes),
            "pairs": sorted(passes),
        }
    return {
        "what_in_panel_proves": (
            "a rule inside the registered panel passes ZERO gated pairs. "
            "This is true by construction at rho < 1 and is computed "
            "here rather than asserted, because v1's equivalent claim "
            "('a carried candidate would score EXACTLY the naive "
            "baseline, by construction') was false as bytes."
        ),
        "what_leave_one_out_measures": (
            "the residual exposure to an information-null rule NOBODY "
            "REGISTERED. Hold a rule out, re-derive the surface from the "
            "other ten, and count what the held-out rule passes. This is "
            "the honest upper bound on how much a twelfth trivial rule "
            "could collect, and it is not zero. It is the reason "
            "`residual_null_rule_exposure` is a not_certified margin "
            "rather than a solved problem."
        ),
        "in_panel_pass_counts": in_panel,
        "leave_one_out": leave_one_out,
        "worst_leave_one_out_rule": max(
            leave_one_out,
            key=lambda name: leave_one_out[name][
                "n_passed_by_the_held_out_rule"
            ],
        ),
    }


# --------------------------------------------------------------------------
# B1: the candidate reference fence
#
# The blocking finding is that the arm's truth table is the model's
# DEFAULT input. The cure cannot be a declaration ("candidates must not
# read the 2023 printing") because a declaration is unenforceable and
# referee A's decision 6 says so. The cure is PHYSICAL: the candidate
# protocol loads a reference object that does not contain the held-out
# rows at all, and whose in-range path raises rather than snapping when
# a held-out year is requested.
# --------------------------------------------------------------------------
class FenceViolation(LookupError):
    """A held-out entitlement year was requested from a fenced reference."""


FENCE_LAW = (
    "A gate-3 retrodiction candidate MUST load its claiming reference "
    "through a FIT-WINDOW-RESTRICTED reference artifact whose rows stop "
    "at T* = 2012, and whose year-resolution path RAISES on any "
    "entitlement year after T* instead of returning a value or snapping "
    "to a nearest year. The resolution vintage "
    "(ssa_claim_ages_2023supplement.json) must not be readable from the "
    "candidate process at all. The fence is a property of the object "
    "the candidate loads, not a rule the candidate promises to obey: "
    "referee A's decision 6 establishes that a declaration rule is "
    "unenforceable at the margin, because a behaviourally motivated "
    "module that happens to be numerically near-persistent is not "
    "'carried' by any declaration."
)


def build_fenced_reference() -> dict:
    """The fit-window-restricted reference artifact, built from bytes.

    Rows are taken from the 2014 printing and truncated at T* = 2012, so
    the object PHYSICALLY cannot answer a question about 2013-2022. The
    2013 row is dropped as well as 2014-2022: it is the fit vintage's
    provisional terminal row, which the settlement finding excluded.
    """
    document = json.loads(CLAIM_2014.read_text())
    rows: dict[str, dict[str, dict]] = {}
    for sex in SEXES:
        for year_key, row in sorted(document["data"][sex].items()):
            year = int(year_key)
            if not FIT_FIRST_YEAR <= year <= T_STAR:
                continue
            rows.setdefault(sex, {})[str(year)] = {
                "categories": {
                    category: row["categories"].get(category)
                    for category in CLAIM_CATEGORIES
                },
                "average_age": row["average_age"],
                "number_thousands": row["number_thousands"],
            }
    admissible = list(range(FIT_FIRST_YEAR, T_STAR + 1))
    held_out = list(range(T_STAR + 1, 2023))
    return {
        "artifact_id": "gate3_retrodiction.fenced_claim_age_reference.v1",
        "law": FENCE_LAW,
        "source": str(CLAIM_2014.relative_to(REPO)),
        "source_sha256": _sha256_path(CLAIM_2014),
        "source_table": "SSA Annual Statistical Supplement Table 6.B5.1",
        "source_edition": 2014,
        "fit_window": [FIT_FIRST_YEAR, T_STAR],
        "admissible_years": admissible,
        "held_out_years": held_out,
        "held_out_reason": {
            "2013": (
                "the 2014 printing's PROVISIONAL TERMINAL ROW: 16 of 16 "
                "shares move between printings, by up to 1.1 pp"
            ),
            "2014-2022": (
                "after T*; these are the years the arm scores, and are "
                "the answer key"
            ),
        },
        "rows": rows,
        "rows_sha256": _sha256_obj(rows),
        "n_admissible_years": len(admissible),
        "n_rows": sum(len(v) for v in rows.values()),
        "resolution_vintage_must_not_be_readable": str(
            CLAIM_2023.relative_to(REPO)
        ),
        "loader_contract": (
            "fenced_row(reference, sex, year) returns the row for an "
            "admissible year and RAISES FenceViolation for every "
            "held-out year. There is no nearest-year fallback: snapping "
            "is exactly the failure mode the deployed module exhibits."
        ),
    }


def fenced_row(reference: dict, sex: str, year: int) -> dict:
    """Reference implementation of the fenced in-range path.

    RAISES rather than returning for any year the fit window excludes.
    Pinned by tests/test_gate3_retrodiction_floors_v2.py.
    """
    if (
        year in reference["held_out_years"]
        or year not in reference["admissible_years"]
    ):
        raise FenceViolation(
            f"entitlement year {year} is outside the gate-3 fit window "
            f"{reference['fit_window']}; a retrodiction candidate may "
            "not read it"
        )
    return reference["rows"][sex][str(year)]


def deployed_module_fence_check() -> dict:
    """MEASURE whether the deployed module passes the fence. It does not.

    Executed live against src/populace_dynamics/claiming.py. Both
    branches are recorded, because referee B established that v1's
    disclosure was false in BOTH: the default path returns the answer
    key, and the 2014-reference path raises a bare KeyError rather than
    a named fence error.
    """
    from populace_dynamics import claiming

    truth = json.loads(CLAIM_2023.read_text())["data"]
    probe_year = 2019
    default_row = claiming.claim_age_distribution("male", probe_year)
    truth_row = truth["male"][str(probe_year)]
    leaks = (
        default_row.average_age == truth_row["average_age"]
        and default_row.categories["age62"] == truth_row["categories"]["age62"]
        and default_row.nearest_year_used is False
    )
    reference_2014 = claiming.load_claim_age_reference(CLAIM_2014)
    try:
        claiming.claim_age_distribution(
            "male", probe_year, reference=reference_2014
        )
        fit_vintage_branch = {
            "outcome": "RETURNED_A_VALUE",
            "verdict": "FENCE FAILS: the fit-vintage path answered",
        }
    except Exception as error:  # noqa: BLE001 - the class is the finding
        fit_vintage_branch = {
            "outcome": "RAISED",
            "exception_type": type(error).__name__,
            "exception_repr": repr(error),
            "verdict": (
                "raises, but with a BARE KeyError from a missing dict "
                "key -- not a named fence error. A candidate cannot "
                "distinguish this from an unrelated data fault, and "
                "MIN_YEAR/MAX_YEAR still admit the year as in range, so "
                "the nearest-year resolver reached a lookup it could "
                "not satisfy instead of refusing the question"
            ),
        }
    return {
        "status": "MEASURED THIS BUILD, NOT ASSERTED",
        "module": "src/populace_dynamics/claiming.py",
        "module_sha256": _sha256_path(
            REPO / "src" / "populace_dynamics" / "claiming.py"
        ),
        "default_reference_is_the_resolution_source": (
            claiming._DEFAULT_REFERENCE.name == CLAIM_2023.name
        ),
        "default_reference_name": claiming._DEFAULT_REFERENCE.name,
        "MIN_YEAR": claiming.MIN_YEAR,
        "MAX_YEAR": claiming.MAX_YEAR,
        "every_gated_target_year_is_in_range": all(
            claiming.MIN_YEAR <= T_STAR + h <= claiming.MAX_YEAR
            for h in GATED_HORIZONS
        ),
        "default_branch": {
            "call": f"claim_age_distribution('male', {probe_year})",
            "returned_average_age": default_row.average_age,
            "returned_age62_share": default_row.categories["age62"],
            "nearest_year_used": default_row.nearest_year_used,
            "resolution_vintage_average_age": truth_row["average_age"],
            "resolution_vintage_age62_share": truth_row["categories"]["age62"],
            "byte_identical_to_the_answer_key": bool(leaks),
        },
        "fit_vintage_branch": fit_vintage_branch,
        "verdict": (
            "THE DEPLOYED MODULE FAILS THIS FENCE TODAY. Its default "
            "reference IS this gate's resolution source and its year "
            "bounds admit every gated target year, so the default path "
            "returns the answer key with nearest_year_used = False. The "
            "fit-vintage branch raises a bare KeyError rather than a "
            "named refusal. Closing this is a CANDIDATE-SIDE "
            "PRECONDITION recorded here; no module was changed by this "
            "build, and changing claiming.py is out of scope for a "
            "floors artifact."
        ),
        "required_module_change": (
            "make MIN_YEAR/MAX_YEAR per-reference (derived from the "
            "loaded reference's own year span) so an out-of-span year "
            "is a named error rather than a snap into a KeyError, and "
            "require the reference argument explicitly on any gate-3 "
            "path rather than defaulting to the 2023 printing"
        ),
    }


# --------------------------------------------------------------------------
# A5 / D7.8: the rolling-origin blocks, with their TRUE sizes
#
# v1 reported `n_seeds: 5` for every block set. Referee B measured the
# actual shapes: (2,2,2,1,1) at 252 of 324 cell x rule x horizon
# combinations, (2,2,1,1,1) at 36 and (2,1,1,1,1) at 36. Two to four of
# the five "seeds" are single observations, summarised with equal
# weight. Referee A added that the origins are NESTED PREFIXES -- origin
# 2004's fit rows are a subset of 2005's and of every later origin's --
# so the across-block sd is not a between-replication dispersion at all.
#
# v2 therefore uses them for NOTHING numeric. They are published as
# provenance and as the robustness leg of the pass rule, with their real
# sizes, and the nesting is stated.
# --------------------------------------------------------------------------
ROLLING_ORIGIN_FIRST = v1b.ROLLING_ORIGIN_FIRST  # 2004
EXCLUDED_TARGET_YEARS = (2013, 2020, 2021, 2022)


def rolling_origin_provenance(
    cells: list[str],
    fit_series: dict,
    resolution_series: dict,
    registry: dict,
    *,
    panel: tuple[str, ...],
) -> dict:
    """Panel-minimum deviation at every rolling origin, blocks and all."""
    out = {}
    shapes: dict[str, int] = {}
    for key in cells:
        metric = METRICS[registry[key]["metric"]]
        fit = fit_series[key]
        realized = resolution_series[key]
        origins = [
            year
            for year in range(ROLLING_ORIGIN_FIRST, T_STAR + 1)
            if year in fit
        ]
        per_horizon = {}
        for horizon in GATED_HORIZONS:
            by_origin = {}
            for origin in origins:
                target = origin + horizon
                if target in EXCLUDED_TARGET_YEARS:
                    continue
                if target not in realized:
                    continue
                years = [
                    y for y in sorted(fit) if FIT_FIRST_YEAR <= y <= origin
                ]
                values = [fit[y] for y in years]
                best = None
                for name in panel:
                    fn = NULL_RULE_PANEL[name][0]
                    try:
                        prediction = fn(years, values, target)
                    except (ValueError, np.linalg.LinAlgError):
                        continue
                    if prediction is None:
                        continue
                    deviation = float(metric(prediction, realized[target]))
                    if best is None or deviation < best:
                        best = deviation
                if best is not None:
                    by_origin[origin] = round(best, 6)
            if not by_origin:
                continue
            ordered = sorted(by_origin)
            blocks = {str(seed): ordered[seed :: len(SEEDS)] for seed in SEEDS}
            sizes = tuple(len(blocks[str(seed)]) for seed in SEEDS)
            shapes[str(sizes)] = shapes.get(str(sizes), 0) + 1
            per_horizon[f"h{horizon}"] = {
                "n_origins": len(ordered),
                "origin_range": [ordered[0], ordered[-1]],
                "panel_min_by_origin": {
                    str(origin): by_origin[origin] for origin in ordered
                },
                "blocks": {
                    seed: {
                        "origins": members,
                        "n_origins_in_block": len(members),
                        "panel_min_mean": (
                            round(
                                float(
                                    np.mean([by_origin[o] for o in members])
                                ),
                                6,
                            )
                            if members
                            else None
                        ),
                    }
                    for seed, members in blocks.items()
                },
                "block_sizes": list(sizes),
                "blocks_are_equal_sized": len(set(sizes)) == 1,
                "n_single_observation_blocks": sum(
                    1 for size in sizes if size == 1
                ),
            }
        out[key] = per_horizon
    return {
        "status": (
            "PROVENANCE AND ROBUSTNESS ONLY. No tolerance in this "
            "artifact reads any number in this block."
        ),
        "why_no_dispersion_is_taken_from_it": (
            "the origins are NESTED PREFIXES (referee A 3.2): origin "
            "2004 fits 1998-2004, origin 2009 fits 1998-2009 and "
            "contains all of it, origin 2012 contains both. The stride-5 "
            "blocks are disjoint in ORIGIN LABEL only; the underlying "
            "fit rows are maximally overlapping and the targets are "
            "adjacent years of one autocorrelated series. An across-"
            "block sd computed on these is not a between-replication "
            "dispersion, and its bias relative to a true replication sd "
            "is UNDETERMINED IN SIGN from what is committed. v1 "
            "described these blocks as disjointness 'stronger than a "
            "half-split'; that is false for this leg and is corrected "
            "in referee_corrections."
        ),
        "why_v1_n_seeds_5_was_misleading": (
            "v1 reported n_seeds: 5 for every block set regardless of "
            "how many origins each block held. Measured block shapes "
            "are below: most block sets contain two SINGLE-OBSERVATION "
            "blocks, summarised with equal weight beside blocks of two. "
            "A verifier reading `n_seeds: 5` beside gate_2's five "
            "person-disjoint seeds is reading a different object."
        ),
        "block_shape_census": dict(sorted(shapes.items())),
        "cells": out,
    }


# --------------------------------------------------------------------------
# A7 / B3: the pass rule
# --------------------------------------------------------------------------
def pass_rule_draft(surface: dict, rolling: dict) -> dict:
    """A conjunction in the locked gates' grammar, with real counts.

    Every locked gate states a conjunction over SEEDS: gate_1 "at least
    4 of 5 locked seeds", gate_2 ">=4 of 5 gate seeds",
    gate_m6 `conjunction: 4 of 5 seeds`. This arm HAS NO SEEDS -- the
    recommended instrument reads one registered origin against one
    realized history. So the seed leg has to be replaced by something
    the instrument actually has, and named as a replacement rather than
    borrowed.
    """
    gated_cells: dict[str, list[str]] = {}
    for pair in surface["gated"]:
        key, horizon = pair.split("@")
        gated_cells.setdefault(key, []).append(horizon)
    origin_counts = sorted(
        {
            entry["n_origins"]
            for cell in rolling["cells"].values()
            for entry in cell.values()
        }
    )
    n_blocks_per_pair = len(SEEDS)
    return {
        "status": "DRAFT FOR THE REFEREE ROUND. Not locked, not applied.",
        "why_the_seed_leg_cannot_be_inherited": (
            "gate_1, gate_2, gate_2b, gate_2c, gate_w1, gate_m4 and "
            "gate_m6 all state an n-of-5-SEED conjunction over "
            "person- or household-disjoint splits. This arm's truth "
            "side is a 100-percent MBR census, so there is no split to "
            "seed, and the recommended instrument reads ONE registered "
            "origin. Referee A 3.3 established that under "
            "`basis: registered_origin` the five stride-5 blocks "
            "contribute nothing to any tolerance. A pass rule that "
            "cited '4 of 5 seeds' here would be citing an object this "
            "arm does not have."
        ),
        "replacement_for_the_seed_leg": (
            "REGISTERED ORIGIN (leg 1) plus ROLLING-ORIGIN BLOCKS "
            "(leg 2). Leg 1 is the number a candidate actually competes "
            "against and is one realization (n = 1), stated as such. "
            "Leg 2 requires the candidate to be RE-FIT at each rolling "
            "origin and re-scored, which converts the nested-prefix "
            "origins from a dispersion claim they cannot support into a "
            "STABILITY requirement they can: a candidate that passes "
            "only from the single registered origin has not shown its "
            "pass survives moving the origin."
        ),
        "pass_rule": (
            "Pair-level conjunction with a rolling-origin stability "
            "leg. LEG 1 (registered origin, T* = 2012): the candidate "
            "passes leg 1 iff EVERY gated (cell, horizon) pair is in "
            "band -- deviation(candidate, cell, h) <= tolerance(cell, "
            "h) -- with no n-of-m allowance over pairs, cells or "
            "horizons. LEG 2 (rolling-origin stability): the candidate "
            "is re-fit at each rolling origin 2004-2012 and re-scored "
            "against the same panel-derived tolerances; origins are "
            "partitioned into the five stride-5 blocks, a block passes "
            "iff every gated pair is in band at every origin in that "
            "block, and leg 2 passes iff at least 4 of the 5 blocks "
            "pass. THE GATE PASSES IFF LEG 1 AND LEG 2 BOTH PASS. A "
            "single breach of leg 1 fails the gate."
        ),
        "why_leg_1_is_all_pairs_not_n_of_m": (
            "gate_2's conjunction is 'every gate-eligible cell ... at "
            "seed s' AND '>=4 of 5 seeds': the n-of-m allowance is over "
            "SEEDS, never over cells. There is no seed axis here, so "
            "the only faithful transcription of that grammar is "
            "all-cells-all-horizons on leg 1, with the n-of-m allowance "
            "moved to the axis that replaced seeds."
        ),
        "counts": {
            "n_gated_pairs": surface["n_gated"],
            "n_gated_cells": len(gated_cells),
            "n_cells_gated_at_every_horizon": surface[
                "n_cells_gated_at_every_horizon"
            ],
            "gated_horizons": list(GATED_HORIZONS),
            "gated_target_years": [T_STAR + h for h in GATED_HORIZONS],
            "registered_origin": T_STAR,
            "n_registered_origin_realizations": 1,
            "rolling_origins": [ROLLING_ORIGIN_FIRST, T_STAR],
            "n_rolling_origins_per_pair_observed": origin_counts,
            "n_rolling_origin_blocks": n_blocks_per_pair,
            "leg_2_conjunction": f"4 of {n_blocks_per_pair} blocks",
            "cells_and_their_gated_horizons": {
                key: sorted(horizons, key=lambda h: int(h[1:]))
                for key, horizons in sorted(gated_cells.items())
            },
        },
        "publishes_regardless": (
            "`publishes_regardless` is NOT a gates.yaml key -- it "
            "appears zero times in the file and lives in the RUN "
            "contract (paper/paper.qmd:2257, "
            "docs/design/anchor_context_extraction.md:978-981, and each "
            "candidate run artifact's protocol block). Referee A 5.5 "
            "verified this. So it belongs in the fragment's "
            "`governance.registration` and `fresh_run_artifact_schema`, "
            "not beside the pass rule: a registered gate-3 retrodiction "
            "run publishes its artifact and its verdict whatever the "
            "verdict is, and a first pass must come from a fresh "
            "registration run."
        ),
        "no_self_rescue": (
            "Inherited verbatim from gate_1.amendment_rules: no "
            "candidate's committed run verdict changes under a rule "
            "proposed after that run; a gate rule amendment applies "
            "only to runs registered after its ratification. This bites "
            "hard here, because the panel is amendable: adding a "
            "twelfth null rule TIGHTENS every tolerance it touches, and "
            "no_self_rescue means a candidate that has already failed "
            "cannot be rescued by a later panel change, nor can a "
            "candidate that has already passed be retroactively failed "
            "by one."
        ),
    }


# --------------------------------------------------------------------------
# A8: the description defect
# --------------------------------------------------------------------------
def description_defect() -> dict:
    """The narrowed description and the missing margin, AS TEXT ONLY."""
    gates_text = (REPO / "gates.yaml").read_text()
    current = (
        "Tier-2 near-term components resolve against administrative "
        "publications on named resolution rules; retrodiction backtests "
        "grade as pseudo-vintage with a published deviation log."
    )
    return {
        "status": "PROPOSED TEXT. NOT APPLIED. gates.yaml is untouched.",
        "binding_rule": (
            "description_claims_exactly_the_scored_surface, promoted "
            "into gate_2.governance.amendment_rules by amendment 2. Its "
            "`applies_to` list names gate_3 explicitly, and "
            "gates.yaml:2889 records the binding in words."
        ),
        "binding_rule_applies_to_gate_3": (
            "gate_3" in gates_text and "applies_to" in gates_text
        ),
        "rule_text_verbatim": (
            "A gate or tranche's description and holdout_basis must "
            "claim EXACTLY the surface its gated cells score at lock "
            "time -- no provision class, holdout, or transition named "
            "in the headline beyond what the cells actually gate. A "
            "headline broader than the scored surface is a lock defect, "
            "to be corrected before ratification."
        ),
        "current_description_verbatim": current,
        "current_description_is_in_gates_yaml": current
        in " ".join(gates_text.split()),
        "the_defect": (
            "gate_3's description has two clauses. Clause (a), 'Tier-2 "
            "near-term components resolve against administrative "
            "publications on named resolution rules', is the "
            "LIVE-RESOLUTION arm -- which this artifact's own "
            "arm_scope.out_of_scope declares out of scope, which binds "
            "FUTURE publications, and which NO CELL SCORES. Clause (b) "
            "is the retrodiction arm, and even that is scored for one "
            "quantity family from one table. v1 left the description "
            "unchanged and its six not_certified margins say nothing "
            "about the live-resolution arm. Under the rule above, that "
            "is a lock defect."
        ),
        "cure_i_narrowed_description": (
            "gate_3 retrodiction arm (tranche): the PSEUDO-VINTAGE "
            "retrodiction of the claiming-age distribution of "
            "retired-worker awards, SSA Annual Statistical Supplement "
            "Table 6.B5.1, fit only on rows the 2014 Supplement printed "
            "and settled (entitlement years 1998-2012) and scored "
            "against the 2023 Supplement's settled rows for entitlement "
            "years 2014-2019, with a published deviation log. No other "
            "Tier-2 quantity, no live resolution, and no other table is "
            "claimed."
        ),
        "cure_i_pattern": (
            "the gate_2 -> gate_2b / gate_2c split (gates.yaml:"
            "2870-2884) is the campaign's own precedent for locking "
            "narrow and adding tranches. Referee A 6.9 and referee B "
            "D9 both recommend it over holding the lock on a "
            "data-staging dependency with no owner and no date."
        ),
        "cure_ii_required_margin": {
            "margin": "tier2_live_resolution_arm_unscored",
            "detail": (
                "The tier-2 LIVE-RESOLUTION arm of gate_3 is NOT "
                "certified and is NOT scored by any cell in this "
                "surface. It binds future annual SSA publications and "
                "its clock cannot start until thresholds lock. Both "
                "source documents close scoring surface 3 with the "
                "sentence this margin exists to carry -- "
                "docs/scoring-and-resolution.md: 'Retrodictive scores "
                "are necessary but not sufficient -- calibration under "
                "the historical regime does not guarantee calibration "
                "under a new one -- so they complement, and NEVER "
                "SUBSTITUTE FOR, the live annual cells in surface 1'; "
                "and paper/paper.qmd: 'backtests complement rather than "
                "substitute for live resolution'. A PASS on this "
                "surface is a retrodiction result and may never be "
                "reported as evidence about live resolution."
            ),
        },
        "why_the_margin_alone_does_not_cure_it": (
            "the ratified rule governs the DESCRIPTION, not the margin "
            "list. Adding a margin under an unchanged broad headline "
            "leaves the headline broad. Referee A 6.9: cure (i) is what "
            "the rule asks for; (ii) is the candour standard that "
            "should accompany it. BOTH are required."
        ),
        "sequencing_consequence_D8": (
            "v1's test_the_gate_3_description_is_quoted_verbatim "
            "requires artifact['arm_scope']['gate_3_text_verbatim'] to "
            "appear in gates.yaml. Narrowing the description therefore "
            "invalidates the committed v1 artifact and forces a rebuild "
            "and a new sha256 -- which is one more reason "
            "floor_run_sha256 cannot be left as the placeholder string "
            "v1 carried."
        ),
    }


# --------------------------------------------------------------------------
# Every other correction both referees made, RECOMPUTED
# --------------------------------------------------------------------------
def _pooled_year_over_year(resolution_series: dict, cells: list[str]) -> dict:
    pooled: dict[int, list[float]] = {}
    for key in cells:
        series = resolution_series[key]
        for year in sorted(series):
            if year - 1 in series:
                pooled.setdefault(year, []).append(
                    abs(series[year] - series[year - 1])
                )
    return {year: float(np.mean(v)) for year, v in pooled.items()}


def quietest_window_ranking(resolution_series: dict, cells: list[str]) -> dict:
    """A3: rank every 6-year window in the panel by pooled |year-on-year|."""
    pooled = _pooled_year_over_year(resolution_series, cells)
    windows = []
    for start in range(1999, 2018):
        years = list(range(start, start + 6))
        if all(year in pooled for year in years):
            windows.append(
                (start, round(float(np.mean([pooled[y] for y in years])), 6))
            )
    windows.sort(key=lambda row: row[1])
    scored_rank = [row[0] for row in windows].index(2014) + 1
    return {
        "measure": (
            "pooled mean |value(y) - value(y-1)| across the 18 "
            "gate-eligible cells, in the 2023 printing"
        ),
        "n_windows_compared": len(windows),
        "ranking": [
            {"window": f"{s}-{s + 5}", "pooled_mean_abs_change": v}
            for s, v in windows
        ],
        "scored_window": "2014-2019",
        "scored_window_rank": scored_rank,
        "scored_window_is_the_quietest": scored_rank == 1,
        "quietest_value": windows[0][1],
        "noisiest_window": f"{windows[-1][0]}-{windows[-1][0] + 5}",
        "noisiest_value": windows[-1][1],
        "ratio_noisiest_to_scored": round(windows[-1][1] / windows[0][1], 4),
        "direction_of_the_effect": (
            "under instrument B a quiet window gives a SMALL naive "
            "baseline and therefore a TIGHT tolerance, so this does not "
            "flatter a candidate on the pass test. What it damages is "
            "the certificate's REACH: a gate named forward projection "
            "would certify claiming-share projection on the single "
            "flattest stretch the source contains. gate_m6 sets the "
            "precedent for exactly this disclosure class "
            "(not_certified.spec_selection_in_sample, "
            "gates.yaml:5440-5444)."
        ),
    }


def shock_partition_asymmetry(
    resolution_series: dict, cells: list[str]
) -> dict:
    """A4: the partition is scored-side-only, and 2009 is unpartitioned."""
    pooled = _pooled_year_over_year(resolution_series, cells)
    window = [pooled[year] for year in range(2014, 2020)]
    mean = float(np.mean(window))
    sd = float(np.std(window, ddof=1))
    sigmas = sorted(
        (
            {
                "year": year,
                "pooled_mean_abs_change": round(value, 6),
                "sigma_vs_scored_window": round((value - mean) / sd, 4),
                "in_fit_window": year <= T_STAR,
                "partitioned_as_shock": year in SHOCK_YEARS_V2,
            }
            for year, value in pooled.items()
        ),
        key=lambda row: -row["sigma_vs_scored_window"],
    )
    worst_fit = next(row for row in sigmas if row["in_fit_window"])
    return {
        "scored_window_mean": round(mean, 6),
        "scored_window_sd_ddof1": round(sd, 6),
        "top_excursions": sigmas[:10],
        "worst_year_inside_the_fit_window": worst_fit,
        "finding": (
            "the shock partition is applied to the SCORED side only. "
            "SHOCK_YEARS is consulted for the TARGET year; the fit "
            f"window and every rolling origin's OLS still contain "
            f"{worst_fit['year']}, which sits at "
            f"{worst_fit['sigma_vs_scored_window']:+} sigma against the "
            "scored window on the same measure -- far beyond either "
            "partitioned year. A rule that removes a mildly elevated "
            "year from the scored side while the single most disrupted "
            "year in the panel drives the fit and the dispersion is not "
            "a shock rule; it is a scored-side-only convention, and it "
            "is recorded here as one."
        ),
        "shock_years_v1": [2020, 2021],
        "shock_years_v2": list(SHOCK_YEARS_V2),
        "why_v2_adds_2022": (
            "gate_m6's own margin is named shock_window_2020_2022 and "
            "its block reads flow_shock_event_years [2020, 2021] with "
            "earnings_shock_reference_years [2020, 2022]; the margin "
            "partitions 2020-2022 out of every gated set "
            "(gates.yaml:5411-5416). v1's DATA said [2020, 2021] while "
            "v1's own shock_window_rule STRING said gate_m6 partitions "
            "2020-2022. No gated pair moves today, because 2022 is "
            "excluded anyway as the 2023 printing's provisional "
            "terminal row. It becomes material the moment a later "
            "Supplement settles 2022: under v1's encoding the "
            "terminal-row reason lapses and 2022 becomes scoreable, "
            "under a contract whose cited precedent partitions it out "
            "permanently. v2 gives 2022 BOTH reasons so neither can "
            "lapse alone."
        ),
    }


def settlement_corrections(v1: dict) -> dict:
    """A section 1 and B sections 1.2-1.4 and 3A.1, all recomputed."""
    fit_doc = json.loads(CLAIM_2014.read_text())
    res_doc = json.loads(CLAIM_2023.read_text())
    awards_settled = []
    average_age_terminal = []
    for sex in SEXES:
        for year_key, row in fit_doc["data"][sex].items():
            year = int(year_key)
            other = res_doc["data"][sex].get(year_key)
            if other is None:
                continue
            if year <= T_STAR:
                a, b = row["number_thousands"], other["number_thousands"]
                if a != b:
                    awards_settled.append(
                        {
                            "cell": f"claim_awards_thousands|{sex}",
                            "year": year,
                            "printed_2014": a,
                            "printed_2023": b,
                            "absolute_thousands": abs(b - a),
                            "relative_percent": round(abs(b - a) / a * 100, 6),
                        }
                    )
            else:
                average_age_terminal.append(
                    {
                        "cell": f"claim_average_age|{sex}",
                        "year": year,
                        "printed_2014": row["average_age"],
                        "printed_2023": other["average_age"],
                        "differs": row["average_age"] != other["average_age"],
                    }
                )
    worst_award = max(awards_settled, key=lambda r: r["relative_percent"])

    notes_2014 = " ".join(json.dumps(fit_doc.get("provenance", {})).split())
    notes_2023 = " ".join(json.dumps(res_doc.get("provenance", {})).split())
    revision_sentence = (
        "Because entitlements can be awarded retroactively, data for "
        "current and prior years are subject to revision with each "
        "annual update of this table."
    )
    v1_text = json.dumps(v1)

    confirmation = v1["settlement_analysis"]["independent_confirmation"]
    settled_b, terminal_b, settled_a, terminal_a = [], [], [], []
    for row in confirmation["rows"]:
        b5 = row["supplement_6b5_1_thousands"]
        a1 = row["supplement_6a1_awards_thousands"]
        gap = abs(b5 - a1)
        if row["terminal_row_of_2023_vintage"]:
            terminal_b.append(gap / b5)
            terminal_a.append(gap / a1)
        else:
            settled_b.append(gap / b5)
            settled_a.append(gap / a1)

    return {
        "A1_the_notes_most_on_point_sentences": {
            "finding": (
                "v1's settlement_analysis.mechanism_quoted_from_the_"
                "table quotes the sentence that distinguishes 6.B5.1 "
                "from 6.B5 -- a CONCEPT note establishing the "
                "entitlement-year BASIS. The sentences that state the "
                "revision mechanism directly, and that contradict the "
                "settled/terminal dichotomy as a general rule, are "
                "quoted nowhere in v1's 1.85 MB."
            ),
            "revision_sentence_verbatim": revision_sentence,
            "present_in_the_2014_printing": revision_sentence.replace(
                "  ", " "
            )
            in notes_2014.replace("\\u2014", "-"),
            "present_in_the_2023_printing": revision_sentence.replace(
                "  ", " "
            )
            in notes_2023.replace("\\u2014", "-"),
            "absent_from_the_v1_artifact": revision_sentence not in v1_text,
            "why_it_cuts_both_ways": (
                "IN THE ARTIFACT'S FAVOUR, the revision mechanism IS "
                "the table's own note, and more explicitly than v1 "
                "claimed -- v1 undersold its own provenance, and it "
                "makes T* = 2012 reconstructible AT TRUE VINTAGE (a "
                "2014 analyst reading their own table's note would drop "
                "the terminal row), so the T* choice's leakage class is "
                "true_vintage_artifact rather than an unpinned "
                "after-the-fact selection. AGAINST IT, the publisher "
                "says revision reaches 'current AND PRIOR years'. The "
                "table's own note therefore does NOT support a "
                "settled/terminal dichotomy; it asserts open-ended "
                "revisability of the whole column. The sharp two-regime "
                "partition is the AUTHOR'S EMPIRICAL INFERENCE from one "
                "vintage pair, held AGAINST the literal reading of the "
                "publisher's own note. That is a stronger and more "
                "honest framing than 'the mechanism is in the table's "
                "own note', and it is the one this artifact adopts."
            ),
            "also_omitted_from_v1": (
                "the 2023 printing adds a sentence the 2014 printing "
                "does not: 'Because of differences in data sources and "
                "calculation methods, statistics reported in this table "
                "may differ from those reported by the Office of the "
                "Chief Actuary.' The publisher explicitly warns that "
                "cross-source comparisons of this table carry a method "
                "gap -- and the 6.A1 'independent confirmation' is "
                "exactly such a comparison."
            ),
        },
        "A1_award_relative_deviation": {
            "v1_report_said": "0.15%",
            "measured_max_relative_percent": worst_award["relative_percent"],
            "presents_as": "0.141%",
            "correction": (
                "the maximum RELATIVE award deviation on settled rows "
                f"is {worst_award['cell']} at {worst_award['year']}, "
                f"{worst_award['printed_2014']} -> "
                f"{worst_award['printed_2023']} = "
                f"{worst_award['relative_percent']:.6f}%, which presents "
                "as 0.141%, not 0.15%. v1's figure rounded in the "
                "direction of overstatement."
            ),
            "all_settled_award_movers": awards_settled,
        },
        "B1_4_terminal_average_age_does_not_move": {
            "finding": (
                "v1 reported that average age does not move on the 30 "
                "SETTLED cell-years and was silent on the terminal row. "
                "It does not move there either: 0 of 2."
            ),
            "rows": average_age_terminal,
            "n_terminal_average_age_cellyears": len(average_age_terminal),
            "n_differing": sum(
                1 for row in average_age_terminal if row["differs"]
            ),
            "consequence": (
                "for claim_average_age|female and claim_average_age|"
                "male there is NO EVIDENCE AT ALL that the 2013 row is "
                "provisional, so excluding it is UNFORCED for those two "
                "cells -- and not neutral: average age rises "
                "monotonically, so persisting from 2012 rather than "
                "2013 makes the naive baseline LARGER and every "
                "tolerance for those pairs LOOSER. v1's "
                "provisional_terminal_rows margin says '16 of 16 "
                "terminal SHARES move', which is literally true and "
                "rhetorically complete-sounding while omitting the half "
                "of the evidence that does not support the exclusion. "
                "v2 keeps the uniform T* = 2012 protocol -- a "
                "per-cell T* would be a new after-the-fact selection -- "
                "and PRICES the choice instead (see "
                "t_star_2013_counterfactual), which is the disclosure "
                "referee B's R5 offers as the alternative to refitting."
            ),
            "vintage_revision_floor_is_identically_zero_for_these_cells": (
                "average age moves in NEITHER regime, so its "
                "vintage-revision floor is zero in both. v1's regime "
                "story therefore supports 16 of its 18 gate-eligible "
                "cells and not the other 2, and v1 did not say so."
            ),
        },
        "B3A1_6A1_relative_gap_denominator": {
            "finding": (
                "v1 divides the |6.B5.1 - 6.A1| gap by the 6.B5.1 "
                "value, not by the 6.A1 reference, and states the "
                "convention nowhere. The chosen denominator is the one "
                "that makes the terminal gap look larger."
            ),
            "settled_max_over_6b5_1_denominator": round(max(settled_b), 6),
            "settled_max_over_6a1_denominator": round(max(settled_a), 6),
            "terminal_over_6b5_1_denominator": round(max(terminal_b), 6),
            "terminal_over_6a1_denominator": round(max(terminal_a), 6),
            "terminal_percent_as_published": round(max(terminal_b) * 100, 2),
            "terminal_percent_on_the_reference": round(
                max(terminal_a) * 100, 2
            ),
            "ratio_terminal_over_settled_as_published": round(
                max(terminal_b) / max(settled_b), 4
            ),
            "ratio_terminal_over_settled_on_the_reference": round(
                max(terminal_a) / max(settled_a), 4
            ),
            "correction": (
                "8.60% on the published convention; 7.92% on the 6.A1 "
                "reference denominator. The direction and the "
                "order-of-magnitude jump survive either way, so the "
                "finding stands -- but the convention must be declared, "
                "and v1's test asserting terminal > 6 * settled sits at "
                "6.638x on the published convention and 6.034x on the "
                "reference convention: one undeclared convention change "
                "from failing."
            ),
        },
        "A1_2_independent_confirmation_is_corroboration_not_confirmation": {
            "finding": (
                "v1 calls the 6.A1 comparison 'independent "
                "confirmation, different table, other end of the "
                "panel'. The 6.A1 side comes from the 2025 Supplement "
                "level-anchor artifact, on an AWARD-ACTION year basis, "
                "against 6.B5.1's ENTITLEMENT year basis as printed in "
                "2023. One observation cannot separate the two-years-"
                "later vintage from the different tabulation basis, and "
                "a genuine surge in award ACTIONS in 2022 (post-2020 "
                "backlog clearance) would produce the same gap with no "
                "accrual story at all."
            ),
            "standing_problem": (
                "the level-anchor artifact carries "
                "artifact_role 'official_context_only', "
                "official_concept.comparison_status 'context_only', a "
                "per-observation verified_against of 'Exact source-cell "
                "transcription only; this does not verify conceptual "
                "equivalence', and a certifies_nothing list whose first "
                "entry is 'This extraction creates no gate, floor, "
                "threshold, verdict...'. v1 used it as the load-bearing "
                "corroboration of a protocol conclusion that fixes T*, "
                "the scored window and the tolerance basis. It is also "
                "a LEVEL comparison, and v1's own rule marks every "
                "level cell report-only pre-W1."
            ),
            "required_relabel": (
                "demote from 'independent confirmation' to 'CONSISTENT "
                "CONTEXT', or demonstrate concept equivalence to the "
                "standard v1 itself met for the TR / 4.A3 pair (44 "
                "overlapping years, max relative gap 0.001777, with a "
                "guard at 0.005 that has already fired). No equivalent "
                "demonstration exists for 6.A1 vs 6.B5.1."
            ),
        },
    }


def t_star_2013_counterfactual(
    v1: dict, cells: list[str], fit_series: dict, resolution_series: dict
) -> dict:
    """B 2.1 / R5: price the uniform T* = 2012 protocol."""
    v1_cells = v1["draft_thresholds"]["cells"]
    baselines = v1["naive_baseline_pseudo_vintage"]["cells"]
    rules = {"persistence": _persistence, "linear_trend": _linear_trend}
    total_2012 = total_2013 = 0.0
    looser = 0
    per_cell = {}
    for key in cells:
        rule = rules[baselines[key]["baseline_rule"]]
        years = [
            y for y in sorted(fit_series[key]) if FIT_FIRST_YEAR <= y <= 2013
        ]
        values = [fit_series[key][y] for y in years]
        rows = {}
        for horizon in GATED_HORIZONS:
            target = T_STAR + horizon
            built = v1_cells[key]["instrument_b_skill_ratio"]["by_horizon"][
                f"h{horizon}"
            ]["tolerance"]
            counterfactual = round(
                DRAFT_RHO
                * abs(
                    rule(years, values, target)
                    - resolution_series[key][target]
                ),
                DRAFT_ROUNDING,
            )
            total_2012 += built
            total_2013 += counterfactual
            if built > counterfactual:
                looser += 1
            rows[f"h{horizon}"] = {
                "target_year": target,
                "as_built_T_star_2012": built,
                "counterfactual_T_star_2013": counterfactual,
                "ratio": (
                    round(built / counterfactual, 4)
                    if counterfactual
                    else None
                ),
            }
        per_cell[key] = rows
    ages = [key for key in cells if key.startswith("claim_average_age")]
    age_ratios = [
        row["ratio"]
        for key in ages
        for row in per_cell[key].values()
        if row["ratio"] is not None
    ]
    return {
        "what_is_held_fixed": (
            "the TARGET YEARS 2014-2019. The origin moves from 2012 to "
            "2013 and the fit window gains the 2013 row; the scored "
            "targets are identical, so the two sums are comparable. "
            "(Matching on horizon LABELS instead moves the targets to "
            "2015-2020 and answers a different question -- the sums "
            "then differ by 0.02 percent and say nothing.)"
        ),
        "sum_of_tolerances_T_star_2012": round(total_2012, 3),
        "sum_of_tolerances_T_star_2013": round(total_2013, 3),
        "ratio": round(total_2012 / total_2013, 4),
        "n_pairs_looser_under_T_star_2012": looser,
        "n_pairs": len(cells) * len(GATED_HORIZONS),
        "verdict_for_the_16_share_cells": (
            "FORCED and PAID FOR. The 2013 row moves by up to 1.1 pp, "
            "twenty-two times the entire settled floor; fitting on a "
            "row measured to be wrong is indefensible."
        ),
        "verdict_for_the_2_average_age_cells": (
            "NOT PAID FOR. Their terminal row is identical across "
            "printings (0 of 2), so the exclusion rests on no evidence "
            "for them, and it LOOSENS their tolerances by a factor of "
            f"{min(age_ratios)} to {max(age_ratios)}. v2 keeps the "
            "uniform protocol -- a per-cell T* chosen in 2026 would be "
            "a fresh after-the-fact selection, which is the class of "
            "move this whole round is closing -- and discloses the "
            "price here instead. This is referee B's R5 second branch, "
            "taken deliberately."
        ),
        "average_age_ratio_range": [min(age_ratios), max(age_ratios)],
        "per_cell": per_cell,
    }


def instrument_and_prose_corrections(
    v1: dict, cells: list[str], bounds: dict, deviations: dict
) -> dict:
    """The remaining corrections: instrument, prose and contract hygiene."""
    v1_cells = v1["draft_thresholds"]["cells"]

    # A 4.2 / B 4.2(b) / B 5.2: v1's stated rule vs v1's committed numbers
    rules = {"persistence": _persistence, "linear_trend": _linear_trend}
    committed = natural = 0.0
    differing = []
    for key in cells:
        for horizon in GATED_HORIZONS:
            row = deviations[key]["by_horizon"][f"h{horizon}"]["rules"]
            as_built = v1_cells[key]["instrument_b_skill_ratio"]["by_horizon"][
                f"h{horizon}"
            ]["tolerance"]
            as_written = round(
                DRAFT_RHO
                * min(row[name]["deviation"] for name in rules if name in row),
                DRAFT_ROUNDING,
            )
            committed += as_built
            natural += as_written
            if abs(as_built - as_written) > 1e-9:
                differing.append(
                    {
                        "pair": f"{key}@h{horizon}",
                        "printed": as_built,
                        "the_rule_as_written": as_written,
                    }
                )

    # A 3.1: instrument A sits BELOW a revision the table actually made
    observed_settled_max = max(
        row["deviation"]
        for row in v1["deviation_log_vintage_revision"]["entries"]
        if row["regime"] == "settled"
        and row["cell"].startswith("claim_share.")
    )
    below_the_observed_revision = sorted(
        key
        for key in cells
        if bounds[key]["instrument_a_mean_k_sd_ddof1"] < observed_settled_max
    )

    # A 5.8 / D6: the report_only globs
    registry_keys = sorted(v1["cells"].keys())
    covered_glob = [
        k for k in registry_keys if k.startswith("covered_earnings.")
    ]
    di_glob = [k for k in registry_keys if k.startswith("di_stock_")]
    di_family = sorted(
        k
        for k, spec in v1["cells"].items()
        if spec.get("family") == "disability"
    )
    explicit_v1 = [
        "claim_awards_thousands|female",
        "claim_awards_thousands|male",
    ]
    covered_actual = sorted(
        k
        for k, spec in v1["cells"].items()
        if spec.get("family") == "covered_earnings"
    )
    uncovered = sorted(
        set(registry_keys)
        - set(cells)
        - set(explicit_v1)
        - set(covered_glob)
        - set(di_glob)
    )

    return {
        "A4_2_B4_2b_the_stated_rule_does_not_produce_the_printed_numbers": {
            "v1_rule_text": (
                "tolerance(cell, h) = round(rho * naive_baseline(cell, "
                "h), 3), where naive_baseline is the deviation, at the "
                "registered origin T*=2012, of the per-cell BETTER of "
                "two registered information-null rules"
            ),
            "what_v1_actually_computed": (
                "the rule was selected by pooled_mean_over_horizons "
                "across the ROLLING origins and then read at the "
                "REGISTERED origin -- which the rule text never says."
            ),
            "sum_as_committed": round(committed, 3),
            "sum_under_the_rule_as_written": round(natural, 3),
            "ratio": round(committed / natural, 4),
            "n_pairs_that_change": len(differing),
            "every_change_is_downward": all(
                row["printed"] > row["the_rule_as_written"]
                for row in differing
            ),
            "worked_examples": differing[:6],
            "which_reading_is_law_in_v2": (
                "NEITHER. v2 removes the question by removing the "
                "selection: the tolerance basis is the MINIMUM over the "
                "registered panel at the registered origin, so the "
                "minimum is both the selection and the basis and there "
                "is nothing left to disagree about. Referee A's "
                "decision 3 and referee B's decision 3 reach this "
                "independently. The rule text in the v2 fragment "
                "reproduces the v2 numbers exactly, and "
                "tests/test_gate3_retrodiction_floors_v2.py re-derives "
                "them from the stated formula rather than pinning them."
            ),
            "leakage_v1_incurred_by_selecting": (
                "48 percent of the targets feeding v1's selection "
                "statistic lie inside the gated window 2014-2019, so "
                "the choice of which information-null rule sets the "
                "tolerance was made by looking at how the two rules "
                "perform on the very years that would be gated. Each "
                "rule is individually information-null; the SELECTION "
                "between them was not. v1's fragment called them 'two "
                "registered information-null rules' and its PR body "
                "called the result 'a PRE-REGISTERED naive baseline'. "
                "Nothing about the per-cell winner was pre-registered."
            ),
        },
        "A3_1_no_measurable_noise_is_refuted_by_the_artifacts_own_numbers": {
            "v1_phrasing": (
                "the truth side 'carries no measurable noise once "
                "provisional rows are excluded' (commit message, PR "
                "body, report section 3)"
            ),
            "measured": (
                "1 of 240 settled share cell-years moved, by 0.100 pp, "
                "and 4 of 30 settled award cell-years moved. Revision "
                "on settled rows is RARE AND SMALL, not absent."
            ),
            "observed_settled_share_revision_max": observed_settled_max,
            "instrument_a_tolerances_ddof1": {
                key: bounds[key]["instrument_a_mean_k_sd_ddof1"]
                for key in cells
            },
            "cells_whose_instrument_a_tolerance_is_below_that_revision": (
                below_the_observed_revision
            ),
            "n_such_cells": len(below_the_observed_revision),
            "why_this_matters": (
                "instrument A would set a tolerance BELOW a revision "
                "that actually occurred in this very table, on every "
                "one of the eligible cells including the one where it "
                "occurred (claim_share.age67_69|male, whose own "
                "floor_vintage_revision.settled_max is 0.1 pp). That is "
                "a stronger and more defensible retirement of "
                "instrument A than 'no measurable noise', and v1 did "
                "not make it. It also corrects v1's fragment text "
                "'fails every candidate BY CONSTRUCTION': at 0.05 pp "
                "against a printed granularity of 0.1 pp, instrument A "
                "admits exactly the candidate that reproduces the "
                "printed digit -- a very strong demand, not a logical "
                "impossibility."
            ),
        },
        "B3_1_the_vintage_disjoint_analogue_overstated": {
            "v1_claim": (
                "disjointness is structural (two separate "
                "publications), 'which is stronger than the seeded "
                "disjointness of a half-split, not weaker'"
            ),
            "correction": (
                "BOTH HALVES MUST BE SAID. Structurally stronger: two "
                "separate publications, no seed needed. Metrologically "
                "WEAKER in three specific ways. (1) CENSORED: shares "
                "print to one decimal, so any settled revision below "
                "0.05 pp is invisible; F1 = 0 means 'below the "
                "detection limit', not 'zero'. (2) n = 1 PAIR, not 100 "
                "seeds: gate_2 prices 100 person-disjoint splits, "
                "gate_m4 100; this arm has exactly one vintage pair, "
                "and the five blocks partition that ONE pair's 15 "
                "settled years rather than being five realizations. "
                "(3) DIFFERENT ESTIMAND: a half-split prices SAMPLING "
                "variability; a vintage pair prices REVISION of a "
                "census figure, and a candidate's error is not drawn "
                "from the revision distribution. Also unresolvable from "
                "two printings: whether the later printing RECOMPUTES "
                "settled rows or CARRIES THEM FORWARD. Under the "
                "carry-forward reading F1 is identically zero for a "
                "reason that says nothing about measurement accuracy. "
                "v1 asserted the recompute reading; the bytes do not "
                "settle it."
            ),
        },
        "A5_min_replications_for_gate_is_ambiguous": {
            "finding": (
                "v1's floor_design publishes min_replications_for_gate: "
                "10 and required_defined_seeds: 5. The 10 is applied "
                "ONLY to F1's n_settled_years (15, passes) and never to "
                "F2's origin count (6-8, would fail); F2 is checked "
                "against 5. So v1 published a threshold that appears to "
                "bind both instruments and binds only the one that "
                "passes it."
            ),
            "resolution_in_v2": (
                "v2 takes NO dispersion from the rolling origins at "
                "all, so there is nothing for a replication minimum to "
                "bind on that leg. min_replications_for_gate is stated "
                "to bind F1's settled-overlap years ONLY, and the "
                "rolling origins are relabelled as what they are: "
                "nested-prefix robustness units, entering the pass rule "
                "as a stability conjunction and no tolerance."
            ),
        },
        "A9_the_TR_anchor_is_true_vintage_not_pseudo_vintage": {
            "v1_label": (
                "'the official forecaster's own pseudo-vintage-2014 "
                "retrodiction'"
            ),
            "correction": (
                "the 2014 OASDI Trustees Report was PUBLISHED "
                "2014-07-28 -- a genuine contemporaneous forecast with "
                "ZERO outcome knowledge of 2015-2024. That is the "
                "opposite of pseudo-vintage as v1's own "
                "definitions.pseudo_vintage defines it. Its ~1.5 "
                "percent mean / 5.3 percent max ten-year error was "
                "achieved under STRICTLY HARDER conditions than this "
                "arm's candidate faces, because this arm's candidate "
                "operates with full outcome knowledge in its structure "
                "(v1's own outcome_knowledge_in_specification entry "
                "says so). Calibrating a frame of reference from a "
                "benchmark achieved without leakage sets the bar "
                "FAVOURABLY to a candidate carrying leakage. Relabel as "
                "TRUE-VINTAGE and state that it is not a like-for-like "
                "benchmark."
            ),
        },
        "D6_report_only_globs_match_nothing": {
            "v1_globs": ["covered_earnings.*", "di_stock_*"],
            "covered_earnings_glob_matches": covered_glob,
            "n_covered_earnings_glob_matches": len(covered_glob),
            "actual_covered_earnings_cell_names": covered_actual,
            "di_stock_glob_matches": len(di_glob),
            "disability_family_size": len(di_family),
            "disability_cells_the_glob_misses": sorted(
                set(di_family) - set(di_glob)
            ),
            "non_eligible_cells_covered_by_no_contract_text": uncovered,
            "n_uncovered": len(uncovered),
            "correction": (
                "covered_earnings.* matches ZERO of the registry keys "
                "-- the four covered-earnings cells are named "
                "covered_contributions_per_worker, "
                "covered_taxable_earnings_per_worker, "
                "covered_taxable_earnings_total and "
                "covered_workers_total, none of which begins "
                "'covered_earnings.'. di_stock_* misses "
                "di_worker_termination_rate. No locked gate uses glob "
                "patterns in report_only; gate_2's is an explicit "
                "enumeration. The v2 fragment enumerates explicitly."
            ),
        },
        "B4_5_the_horizon_diagnostic_mixes_units": {
            "finding": (
                "v1's horizon_monotonicity.pooled_mean_across_eligible_"
                "cells averages 16 cells in PERCENTAGE POINTS with 2 in "
                "YEARS, and v1's report prints that mixed mean labelled "
                "'a naive baseline of 1.4-3.0 pp'. The monotonicity "
                "conclusion survives on homogeneous series; the "
                "published figure is dimensionally incoherent and the "
                "'pp' label is wrong."
            ),
            "republished_per_unit": "see horizon_monotonicity_by_unit",
        },
        "D7_9_R16_instrument_B_was_not_floored_at_F0": {
            "finding": (
                "v1 applied max(..., rounding_floor) to instrument A "
                "and to the lower bound, but instrument B was "
                "round(rho * basis, 3) with NO F0 floor -- while the "
                "fragment printed publication_rounding_floor_pp: 0.05 "
                "inside the instrument block as though it were applied. "
                "It did not bind on v1's numbers. It binds on v2's: the "
                "panel minimum is far smaller, and 17 of the 108 pairs "
                "are demoted precisely because rho times it lands at or "
                "below max(F0, instrument A)."
            ),
            "resolution_in_v2": (
                "F0 is not a floor to raise a tolerance TO; it is a "
                "GATE-ELIGIBILITY BOUND. A tolerance below the "
                "measurement lower bound does not get lifted -- the "
                "pair is demoted to reported-not-gated, because the "
                "truth side cannot resolve the difference between the "
                "candidate and a null rule there. Lifting it instead "
                "would manufacture room that the printing granularity "
                "does not contain."
            ),
        },
        "D7_11_the_inverted_prose_assertion": {
            "finding": (
                "v1's test asserts \"'never' not in cell["
                "'pooled_including_terminal_row']['note']\". The note "
                "reads 'not used for any tolerance'; STRENGTHENING it "
                "to 'never used for any tolerance' would FAIL the "
                "suite. An inverted string assertion on prose is a trap "
                "for the next editor."
            ),
            "resolution_in_v2": (
                "v2's suite asserts the SUBSTANCE (that no tolerance "
                "path reads the unpartitioned number) and carries no "
                "negative string assertion on prose."
            ),
        },
        "D7_6_R11_reader_commit_is_a_git_history_dependency": {
            "finding": (
                "v1's artifact embeds data.claiming.reader_commit, "
                "obtained by shelling out to `git log -1 --format=%H`. "
                "So v1's claim that re-running the builder on the same "
                "committed INPUTS reproduces it byte for byte is false "
                "as stated: reproduction also needs the ambient "
                "repository's HISTORY for one file, which is not an "
                "input and is not in .inputs.json. In a shallow clone "
                "or a git-less export the helper swallows every "
                "exception and returns 'unknown', so the rebuild "
                "silently yields different bytes. Worse, the module "
                "change the B1 fence requires would itself move "
                "reader_commit and break v1's own reproduction test."
            ),
            "resolution_in_v2": (
                "the v2 artifact carries NO git-derived value. The "
                "claiming module is pinned by CONTENT DIGEST "
                "(candidate_reference_fence.deployed_module_fence_check"
                ".module_sha256), which is an input, and the commit "
                "hash moves to the .env.json sidecar, which is excluded "
                "from the byte comparison."
            ),
        },
        "A4_4_the_surface_is_one_table_one_family": {
            "finding": (
                "35 cells are defined, 18 are draft-eligible, 17 are "
                "excluded for substantive reasons. But the surviving 18 "
                "are ALL from one table, one sex-split, one quantity "
                "family. v1's covers text and not_certified list say "
                "what is not certified by QUANTITY; nothing says that "
                "the arm gating a gate named 'forward projection' "
                "scores the claiming-age distribution and nothing else."
            ),
            "resolution_in_v2": (
                "carried by the narrowed description (cure i of the A8 "
                "block) and by the single_table_single_family margin."
            ),
        },
    }


def horizon_monotonicity_by_unit(
    deviations: dict, cells: list[str], *, panel: tuple[str, ...]
) -> dict:
    """R14: republish the horizon diagnostic per unit, never mixed."""
    groups = {
        "shares_percentage_points": [
            key for key in cells if key.startswith("claim_share.")
        ],
        "average_age_years": [
            key for key in cells if key.startswith("claim_average_age")
        ],
    }
    out = {}
    for label, members in groups.items():
        row = {}
        for horizon in GATED_HORIZONS:
            values = [
                _panel_min(
                    deviations[key]["by_horizon"][f"h{horizon}"], panel
                )[0]
                for key in members
                if f"h{horizon}" in deviations[key]["by_horizon"]
            ]
            row[f"h{horizon}"] = round(float(np.mean(values)), 6)
        series = list(row.values())
        out[label] = {
            "n_cells": len(members),
            "unit": (
                "percentage points of share (0-100 scale)"
                if "shares" in label
                else "years"
            ),
            "pooled_F2_panel_min_by_horizon": row,
            "monotone_non_decreasing": all(
                series[i] <= series[i + 1] for i in range(len(series) - 1)
            ),
        }
    return {
        "why_two_tables_and_never_one": (
            "v1 averaged 16 percentage-point cells with 2 year cells "
            "into a single series and its report labelled the result "
            "'pp'. The number was dimensionally incoherent. These are "
            "the same diagnostic, computed per unit, on the v2 "
            "panel-minimum basis."
        ),
        "basis": "F2_panel_min at the registered origin",
        "groups": out,
    }


def not_certified_margins(
    surface: dict, exposure: dict, quiet: dict, shock: dict
) -> list[dict]:
    """The v2 margin list: v1's six, corrected, plus what was missing."""
    worst = exposure["worst_leave_one_out_rule"]
    worst_n = exposure["leave_one_out"][worst]["n_passed_by_the_held_out_rule"]
    return [
        {
            "margin": "tier2_live_resolution_arm_unscored",
            "new_in_v2": True,
            "answers": "A8",
            "detail": (
                "The tier-2 LIVE-RESOLUTION arm of gate_3 is NOT "
                "certified and is scored by NO cell here. It binds "
                "future annual SSA publications and its clock cannot "
                "start until thresholds lock. Both source documents "
                "close scoring surface 3 with the same sentence: "
                "docs/scoring-and-resolution.md -- 'Retrodictive scores "
                "are necessary but not sufficient ... so they "
                "complement, and NEVER SUBSTITUTE FOR, the live annual "
                "cells in surface 1'; paper/paper.qmd -- 'backtests "
                "complement rather than substitute for live "
                "resolution'. A PASS here may never be reported as "
                "evidence about live resolution."
            ),
        },
        {
            "margin": "residual_null_rule_exposure",
            "new_in_v2": True,
            "answers": "A6 / B2 (the part the panel does NOT close)",
            "detail": (
                "The panel minimum closes the hole for every rule IN "
                "the panel: a registered null rule passes zero gated "
                "pairs, computed not asserted. It does NOT close the "
                "hole for a rule nobody registered. Leave-one-out on "
                f"the eleven-rule panel: holding out `{worst}` and "
                "re-deriving the surface from the other ten, the "
                f"held-out rule then passes {worst_n} gated pairs. That "
                "is the honest residual, and it is the reason the panel "
                "is enumerated in the contract by name and formula: "
                "amending it is a ceremony act, not a builder edit."
            ),
        },
        {
            "margin": "the_panel_was_assembled_with_the_answer_in_hand",
            "new_in_v2": True,
            "answers": "self-disclosure of v2's own leakage",
            "detail": (
                "Nine of the eleven registered rules were exhibited by "
                "referee B AFTER reading the resolution vintage, "
                "specifically because they passed v1's tolerances. So "
                "the panel is not pre-registered either; it is an "
                "after-the-fact hardening, chosen with 2014-2022 in "
                "hand. This TIGHTENS every tolerance it touches, so it "
                "cannot flatter a candidate -- but it is the same "
                "leakage class v1's own deviation log names, and it "
                "must be logged rather than presented as a "
                "pre-registration this artifact does not have."
            ),
        },
        {
            "margin": "scored_window_is_the_quietest_in_the_panel",
            "new_in_v2": True,
            "answers": "A3",
            "detail": (
                "The scored window 2014-2019 is the QUIETEST six-year "
                "window in the entire 1999-2022 panel -- pooled mean "
                f"|year-on-year| {quiet['quietest_value']} against "
                f"{quiet['noisiest_value']} for the noisiest "
                f"({quiet['noisiest_window']}), a factor of "
                f"{quiet['ratio_noisiest_to_scored']}, ranked "
                f"{quiet['scored_window_rank']} of "
                f"{quiet['n_windows_compared']}. Nothing is certified "
                "about claiming-share projection through a turbulent "
                "stretch. The window was not chosen for its calm -- it "
                "falls out mechanically from the exclusions -- but the "
                "certificate's reach is bounded by it either way."
            ),
        },
        {
            "margin": "shock_window_2020_2022",
            "corrected_in_v2": True,
            "answers": "A4 / R6",
            "detail": (
                "exogenous_shock_outside_model_class, following "
                "gate_m6's own margin, which partitions 2020-2022 "
                "(gates.yaml:5411-5416) -- NOT 2020-2021, which is what "
                "v1's data said while v1's own rule text cited "
                "2020-2022. 2022 carries BOTH this reason and the "
                "provisional-terminal-row reason, so a later Supplement "
                "that settles 2022 cannot readmit it by lapsing one."
            ),
        },
        {
            "margin": "shock_partition_is_scored_side_only",
            "new_in_v2": True,
            "answers": "A4(ii)",
            "detail": (
                "The partition is consulted for the TARGET year only. "
                "The fit window and every rolling origin's fit still "
                f"contain "
                f"{shock['worst_year_inside_the_fit_window']['year']}, "
                "which sits at "
                f"{shock['worst_year_inside_the_fit_window']['sigma_vs_scored_window']:+}"
                " sigma against the scored window on the same measure "
                "-- the largest excursion in the panel, and larger than "
                "either partitioned year. This is a scored-side-only "
                "convention, not a shock rule, and it is disclosed as "
                "one rather than extended, because extending it would "
                "be a fresh after-the-fact selection."
            ),
        },
        {
            "margin": "provisional_terminal_rows",
            "corrected_in_v2": True,
            "answers": "B 1.4 / R5",
            "detail": (
                "Entitlement years 2013 and 2022 are excluded. 16 of 16 "
                "terminal SHARES move between printings (max 1.1 pp) "
                "against 1 of 240 settled ones (0.1 pp). THE OTHER HALF "
                "OF THE EVIDENCE, which v1 omitted: terminal "
                "AVERAGE AGE moves 0 of 2, so for "
                "claim_average_age|{female,male} the exclusion rests on "
                "no evidence and loosens their tolerances by 1.14x to "
                "2.00x. v2 keeps the uniform protocol and prices the "
                "choice (t_star_2013_counterfactual) rather than "
                "refitting those two cells at T* = 2013."
            ),
        },
        {
            "margin": "settlement_is_measured_only_at_printing_age_4_plus",
            "new_in_v2": True,
            "answers": "A2",
            "detail": (
                "'Settled' is measured at printing age >= 9 (the "
                "observed pair is nine printings apart) and the "
                "youngest scored row, 2019, is 4 printings old at the "
                "2023 resolution vintage. NOTHING is observed about "
                "rows aged 1-8 printings, and the publisher's own note "
                "says revision reaches 'current AND PRIOR years'. "
                f"min_settlement_age_printings = "
                f"{MIN_SETTLEMENT_AGE_PRINTINGS} is pinned as a "
                "protocol constant so a later T* move cannot score a "
                "one-year-old row while citing this arm's settlement "
                "finding."
            ),
        },
        {
            "margin": "single_table_single_family",
            "new_in_v2": True,
            "answers": "A4.4 / D9",
            "detail": (
                "All gated cells come from ONE table (6.B5.1), one "
                "sex-split, one quantity family, one vintage pair, one "
                "fit source and one realized history. Covered earnings "
                "(4.B11), the DI ASR quantities, beneficiary counts and "
                "average benefits are NOT certified: the repository "
                "holds one publication vintage of each, or none, so "
                "their pre-T* rows are post-T* revisions of themselves."
            ),
        },
        {
            "margin": "level_cells",
            "detail": (
                "Award COUNTS and every other level cell are "
                "report-only pre-W1; the frame is not nationalized and "
                "the ratified anchor-context law publishes only "
                "scale-invariant comparisons."
            ),
        },
        {
            "margin": "specification_leakage",
            "corrected_in_v2": True,
            "detail": (
                "Cells, rules, T*, the shock partition, the provisional "
                "exclusions AND NOW THE NULL-RULE PANEL were all chosen "
                "in 2026 with 2014-2022 in hand; the settlement finding "
                "was DISCOVERED, not pre-registered. A PASS is "
                "conditional on the whole deviation log and may never "
                "be stated as an unconditional out-of-sample result."
            ),
        },
        {
            "margin": "carried_claiming_path",
            "corrected_in_v2": True,
            "answers": "B1 / A6 (v1's version of this margin was FALSE)",
            "detail": (
                "v1 asserted that a candidate calling "
                "populace_dynamics.claiming 'would score EXACTLY the "
                "naive baseline, by construction'. That is false in "
                "BOTH branches. The default branch returns THE ANSWER "
                "KEY -- claiming's default reference IS this gate's "
                "resolution source and its year bounds admit every "
                "gated target year, so a carried candidate scores "
                "deviation 0 everywhere. The fit-vintage branch raises "
                "a bare KeyError. The cure is the physical fence in "
                "candidate_reference_fence, not a declaration: a "
                "behaviourally motivated module that happens to be "
                "numerically near-persistent is not 'carried' by any "
                "declaration. The declaration requirement is retained "
                "in the registration clause as the SECOND line."
            ),
        },
        {
            "margin": "the_TR_anchor_is_true_vintage",
            "new_in_v2": True,
            "answers": "A9",
            "detail": (
                "The 2014 Trustees Report anchor was published "
                "2014-07-28 with zero outcome knowledge. Its error is "
                "NOT a like-for-like frame of reference for a "
                "pseudo-vintage backtest whose specification carries "
                "full outcome knowledge; the two were achieved under "
                "different leakage."
            ),
        },
        {
            "margin": "no_replication",
            "new_in_v2": True,
            "answers": "A3.3 / B3.2 / A7",
            "detail": (
                "The tolerance basis is a SINGLE REALIZATION (n = 1) at "
                "the registered origin. There are no seeds: the truth "
                "side is a 100-percent MBR census with no sampling "
                "frame to split. The rolling origins are NESTED "
                "PREFIXES of one realized series and supply no "
                "dispersion; they enter the pass rule as a stability "
                "conjunction and no tolerance. Any reading of "
                "`n_blocks: 5` as gate_2's five person-disjoint seeds "
                "is a category error."
            ),
        },
    ]


# --------------------------------------------------------------------------
# The draft gates.yaml fragment, GENERATED from the computed surface
#
# v1 hand-wrote its fragment, and referee B found that the fragment's own
# rule text did not reproduce the fragment's own numbers on 28 of 108
# pairs. That cannot happen here: every tolerance below is emitted from
# `gated_surface_recommended`, so the fragment and the artifact are the
# same numbers by construction, and the test suite re-derives them from
# the STATED FORMULA rather than pinning them.
#
# Fragment grammar follows the LOCKED gates (gate_m4 / gate_m6): lock
# content at the top level of the gate block -- id, status, locked, kind,
# covers, holdout_basis, scoring, governance, history -- never nested
# under an arm sub-key, and never a third `locked` flag.
# --------------------------------------------------------------------------
def _yaml_block(text: str, indent: int) -> str:
    """Fold a prose string into a YAML block scalar at `indent` spaces."""
    pad = " " * indent
    words, lines, current = text.split(), [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > 66:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return ">-\n" + "\n".join(f"{pad}{line}" for line in lines)


def draft_fragment(
    artifact_body: dict,
    surface: dict,
    exposure: dict,
    fence: dict,
    defect: dict,
    passrule: dict,
) -> str:
    """Emit the proposed gate_3 tranche block. TEXT ONLY -- never written."""
    by_cell: dict[str, dict[str, float]] = {}
    for pair, row in surface["gated"].items():
        key, horizon = pair.split("@")
        by_cell.setdefault(key, {})[horizon] = row["tolerance"]
    demoted_by_cell: dict[str, list[str]] = {}
    for pair, row in surface["reported_not_gated"].items():
        key, horizon = pair.split("@")
        demoted_by_cell.setdefault(key, []).append(
            f"{horizon} ({row['reason']})"
        )

    lines: list[str] = []
    add = lines.append
    add("  gate_3:")
    add("    name: forward projection")
    add("    # UNCHANGED at gate level. The retrodiction surface locks as a")
    add("    # TRANCHE below, on the gate_2 -> gate_2b/2c pattern, so that")
    add("    # gate_3's own headline is not claimed by a surface that does")
    add("    # not score it. Cure (i) of finding A8.")
    add(
        "    description: "
        + _yaml_block(defect["current_description_verbatim"], 6)
    )
    add("    thresholds:")
    add("      locked: false")
    add("")
    add("    # ---- PROPOSAL ONLY. Not locked, not ratified, not scored. ----")
    add("    # gates.yaml is byte-identical to origin/master at this commit.")
    add("    gate_3a_retrodiction_claiming:")
    add("      id: gate_3a_retrodiction_claiming")
    add("      status: draft_pending_referee_round")
    add("      locked: false")
    add("      kind: pseudo_vintage_backtest")
    add("      gates_yaml_untouched_by_this_draft: true")
    add(
        "      description: "
        + _yaml_block(defect["cure_i_narrowed_description"], 8)
    )
    add("      floor_run: runs/gate3_retrodiction_floors_v2.json")
    add("      floor_run_sha256: <FILLED AT RATIFICATION -- see the report")
    add("        footer; the v2 artifact digest is stated there and must be")
    add("        pasted here, never left as a placeholder string>")
    add("      superseded_floor_run: runs/gate3_retrodiction_floors_v1.json")
    add(f"      superseded_floor_run_sha256: {V1_ARTIFACT_SHA256}")
    add(
        "      covers: "
        + _yaml_block(
            "the PSEUDO-VINTAGE retrodiction of the claiming-age "
            "distribution of retired-worker awards (SSA Annual Statistical "
            "Supplement Table 6.B5.1) ONLY: fit only on rows the 2014 "
            "Supplement printed and settled (entitlement years 1998-2012), "
            "project entitlement years 2014-2019, score against the 2023 "
            f"Supplement's settled rows. {surface['n_gated']} gated (cell, "
            f"horizon) pairs over "
            f"{surface['n_cells_with_at_least_one_gated_horizon']} cells; the "
            f"remaining {surface['n_reported_not_gated']} pairs are REPORTED, "
            "NOT GATED, each with its reason.",
            8,
        )
    )
    add("      holdout_basis:")
    add(
        "        - "
        + _yaml_block(
            "PUBLICATION VINTAGE, not persons. The truth side is a "
            "100-percent MBR census (SSA: 'Master Beneficiary Record, 100 "
            "percent data (not a sample)'), so a person-disjoint half-split "
            "is unavailable IN PRINCIPLE and a bootstrap over published "
            "shares would invent a variance the source does not have.",
            10,
        )
    )
    add(
        "        - "
        + _yaml_block(
            "The held-out object is every row after T* = 2012. A candidate "
            "loads the FENCED reference defined in "
            "candidate_reference_fence and cannot read the resolution "
            "vintage at all.",
            10,
        )
    )
    add(
        "        - "
        + _yaml_block(
            "ONE vintage pair, ONE realized history, NO seeds. The "
            "tolerance basis is a single realization at the registered "
            "origin (n = 1). Any reading of a block count as gate_2's five "
            "person-disjoint seeds is a category error.",
            10,
        )
    )
    add("      not_certified:")
    for margin in artifact_body["not_certified"]:
        add(f"        - margin: {margin['margin']}")
        add("          detail: " + _yaml_block(margin["detail"], 12))
    add("      protocol:")
    protocol = artifact_body["protocol"]
    add(f"        vintage_boundary_year: {protocol['vintage_boundary_year']}")
    add(f"        T_star: {protocol['T_star']}")
    add(f"        T_star_leakage_class: {protocol['T_star_leakage_class']}")
    add(f"        fit_window: {protocol['fit_window']}")
    add(f"        fit_source: {protocol['fit_source']}")
    add(f"        fit_source_sha256: {protocol['fit_source_sha256']}")
    add(f"        resolution_source: {protocol['resolution_source']}")
    add(
        "        resolution_source_sha256: "
        f"{protocol['resolution_source_sha256']}"
    )
    add(f"        scored_years: {protocol['scored_years']}")
    add(f"        horizons: {protocol['horizons']}")
    add(
        f"        excluded_years: {protocol['excluded_years']}"
        "   # provisional terminal rows"
    )
    add(
        f"        shock_years: {protocol['shock_years']}"
        "   # gate_m6 partitions 2020-2022"
    )
    add(
        "        min_settlement_age_printings: "
        f"{protocol['min_settlement_age_printings']}"
    )
    add("      instrument:")
    add("        chosen: skill_ratio_against_a_registered_null_panel")
    add(f"        rho: {surface['rho']}")
    add(f"        rho_sensitivity: {list(RHO_SENSITIVITY)}")
    add("        basis: registered_origin_panel_minimum")
    add("        horizon_shape: as_measured")
    add("        rule: " + _yaml_block(TOLERANCE_LAW, 10))
    add(
        "        authoritative: "
        + _yaml_block(
            "THE FORMULA, not the literals. The per-cell tables below are "
            "emitted from the formula and are re-derived from it by "
            "tests/test_gate3_retrodiction_floors_v2.py; where they ever "
            "disagreed the formula would govern. This resolves the "
            "formula-vs-literal ambiguity referee B raised as D7.2, and "
            "the disagreement it found in v1 (28 of 108 pairs) cannot "
            "recur.",
            10,
        )
    )
    add("        null_rule_panel:")
    add("          # D7.3: the panel is CONTRACT, not a module dict.")
    add("          # Adding, removing or reordering a rule is an amendment")
    add("          # and, under no_self_rescue, binds only runs registered")
    add("          # after ratification.")
    for name, (_fn, formula, _why) in NULL_RULE_PANEL.items():
        add(f"          {name}: {formula}")
    add("        panel_minimum_is_both_selection_and_basis: true")
    add(
        "        publication_rounding_floor: "
        + _yaml_block(
            "0.05 for every gated cell (half of the 0.1 printed "
            "granularity). UNITS ARE PER CELL: percentage points of share "
            "for the 16 claim_share cells, YEARS for the two "
            "claim_average_age cells. It is an ELIGIBILITY BOUND, not a "
            "floor a tolerance is raised to: a tolerance below "
            "max(F0, instrument A) demotes its pair to reported-not-gated, "
            "because the truth side cannot resolve the difference between "
            "the candidate and a null rule there.",
            10,
        )
    )
    add("        rejected_instrument:")
    add("          name: mean_plus_k_sd")
    add("          k: 4")
    add("          ddof: 1   # the repo floor convention; v1 used ddof=0")
    add(
        "          why_rejected: "
        + _yaml_block(
            "the truth side is a 100-percent MBR census with no sampling "
            "noise, so the vintage-revision floor is degenerate on settled "
            "rows (1 of 240 share cell-years differs, by one printing "
            "unit) and this collapses onto the publication-rounding floor "
            "of 0.05 for 17 of the 18 eligible cells. The DECISIVE fact is "
            "not that it 'fails every candidate by construction' -- it "
            "admits exactly the candidate that reproduces the printed "
            "digit -- but that its 0.05/0.066 tolerance sits BELOW the "
            "0.1 pp revision this very table demonstrably made.",
            12,
        )
    )
    add("      scoring:")
    add("        pass_rule: " + _yaml_block(passrule["pass_rule"], 10))
    add("        conjunction_leg_1: every gated (cell, horizon) pair")
    add(
        "        conjunction_leg_2: "
        f"{passrule['counts']['leg_2_conjunction']}"
    )
    add(f"        n_gated_pairs: {surface['n_gated']}")
    add(
        "        n_gated_cells: "
        f"{surface['n_cells_with_at_least_one_gated_horizon']}"
    )
    add(
        f"        registered_origin: {passrule['counts']['registered_origin']}"
    )
    add("        n_registered_origin_realizations: 1")
    add("        rolling_origins: " f"{passrule['counts']['rolling_origins']}")
    add(
        "        n_rolling_origins_per_pair: "
        f"{passrule['counts']['n_rolling_origins_per_pair_observed']}"
    )
    add(
        "        n_rolling_origin_blocks: "
        f"{passrule['counts']['n_rolling_origin_blocks']}"
    )
    add(
        "        why_no_seed_conjunction: "
        + _yaml_block(passrule["why_the_seed_leg_cannot_be_inherited"], 10)
    )
    add(
        "        replacement_for_the_seed_leg: "
        + _yaml_block(passrule["replacement_for_the_seed_leg"], 10)
    )
    add("      cells:")
    add("        # DRAFT per-cell x horizon tolerances. Units: percentage")
    add("        # points of share (0-100 scale), except claim_average_age,")
    add("        # which is YEARS. Emitted from the formula above.")
    for key in sorted(by_cell):
        row = by_cell[key]
        body = ", ".join(
            f"{h}: {row[h]}"
            for h in sorted(row, key=lambda name: int(name[1:]))
        )
        add(f"        {key + ':':<42}" + "{" + body + "}")
    add("      reported_not_gated:")
    add("        # NOT gated, with the reason. These pairs have no room")
    add("        # strictly between the measurement lower bound and the")
    add("        # null panel's minimum, so no tolerance there can certify")
    add("        # skill. Published, never scored.")
    for key in sorted(demoted_by_cell):
        add(f"        {key}:")
        for entry in sorted(demoted_by_cell[key]):
            add(f"          - {entry}")
    add("      report_only:")
    add("        # Explicit enumeration. v1 used glob patterns and referee")
    add("        # A measured that covered_earnings.* matched ZERO registry")
    add("        # keys and di_stock_* missed di_worker_termination_rate.")
    for key in artifact_body["referee_corrections"]["instrument_and_prose"][
        "D6_report_only_globs_match_nothing"
    ]["actual_covered_earnings_cell_names"]:
        add(f"        - {key}")
    add("        - claim_awards_thousands|female")
    add("        - claim_awards_thousands|male")
    add("      candidate_reference_fence:")
    add("        law: " + _yaml_block(fence["law"], 10))
    add(
        "        fenced_reference_rows_sha256: "
        f"{fence['fenced_reference']['rows_sha256']}"
    )
    add(
        "        admissible_years: "
        f"{fence['fenced_reference']['fit_window']}"
    )
    add("        deployed_module_passes_this_fence_today: false")
    add(
        "        required_module_change: "
        + _yaml_block(
            fence["deployed_module_fence_check"]["required_module_change"], 10
        )
    )
    add("      deviation_log:")
    add("        vintage_revision: floor_run.referee_corrections.settlement")
    add(
        "        specification_leakage: "
        "floor_run.not_certified[specification_leakage]"
    )
    add(
        "        panel_selection_leakage: "
        "floor_run.not_certified"
        "[the_panel_was_assembled_with_the_answer_in_hand]"
    )
    add("      governance:")
    add(
        "        registration: "
        + _yaml_block(
            "Pre-registered on issue #42, exactly as every gate-1 and "
            "gate-2 candidate run. A gate-3 retrodiction candidate "
            "registers, BEFORE scoring: its spec; its claiming path "
            "declared as BEHAVIOURAL or CARRIED; the fenced reference "
            "digest it will load; its COLA / wage-index source, which MUST "
            "be the T*-vintage Trustees assumptions "
            "(data/external/ssa_tr_ultimate_assumptions_2014.json) and NOT "
            "realized post-T* COLAs; and its simulation seeds. Outer runs "
            "are one-shot: a first pass must come from a fresh "
            "registration run. The run PUBLISHES REGARDLESS of verdict, "
            "with at most one disclosed re-execution.",
            10,
        )
    )
    add(
        "        fresh_run_artifact_schema: "
        + _yaml_block(
            "a registered gate-3 retrodiction run artifact carries "
            "protocol.publishes_regardless, the fenced reference digest it "
            "actually loaded, a proof that the resolution vintage was not "
            "readable from the candidate process, the per-pair deviations, "
            "and its verdict under the pass rule above.",
            10,
        )
    )
    add("        amendment_rules:")
    add("          inherits: gate_1")
    add(
        "          no_self_rescue: "
        + _yaml_block(
            "Inherited verbatim from gate_1.amendment_rules: no "
            "candidate's committed run verdict changes under a rule "
            "proposed after that run; a gate rule amendment applies only "
            "to runs registered after its ratification. This binds the "
            "null-rule panel: adding a twelfth rule TIGHTENS tolerances, "
            "and no already-scored run moves either way.",
            12,
        )
    )
    add(
        "          amendments_only_via: "
        + _yaml_block(
            "public proposal + adversarial referee round + verification + "
            "maintainer ratification by merge -- the same ceremony gate 1's "
            "amendments follow.",
            12,
        )
    )
    add("          description_claims_exactly_the_scored_surface:")
    add("            rule: " + _yaml_block(defect["rule_text_verbatim"], 14))
    add(
        "            satisfied_how: "
        + _yaml_block(
            "this tranche's description names exactly Table 6.B5.1's "
            "claiming-age distribution and entitlement years 2014-2019, "
            "and gate_3's own description is left to the LIVE-RESOLUTION "
            "arm it actually describes, which remains unlocked. The "
            "tier2_live_resolution_arm_unscored margin carries the two "
            "source sentences that say backtests never substitute for live "
            "resolution.",
            14,
        )
    )
    add("      history:")
    add(
        "        - "
        + _yaml_block(
            "floors v1 (runs/gate3_retrodiction_floors_v1.json, "
            f"sha256 {V1_ARTIFACT_SHA256}) proposed 108 gated pairs under "
            "a two-rule baseline with a per-cell selection. Two "
            "independent referees returned NOT LOCK-READY without "
            "disputing a single number: the arithmetic reproduced exactly "
            "on both independent implementations.",
            10,
        )
    )
    add(
        "        - "
        + _yaml_block(
            "floors v2 answers them. The baseline became the MINIMUM over "
            "an eleven-rule registered panel, which removes the per-cell "
            "selection entirely and drops the gated surface from 108 pairs "
            f"to {surface['n_gated']} and the tolerance sum from 184.052 "
            f"to {surface['sum_of_tolerances']} (a factor of "
            f"{round(184.052 / surface['sum_of_tolerances'], 4)}). Every "
            "registered null rule now passes ZERO gated pairs, computed "
            "rather than asserted. Residual leave-one-out exposure to an "
            "UNREGISTERED twelfth rule is "
            f"{exposure['leave_one_out'][exposure['worst_leave_one_out_rule']]['n_passed_by_the_held_out_rule']}"
            f" pairs (worst held-out rule: "
            f"{exposure['worst_leave_one_out_rule']}), and is a "
            "not_certified margin, not a solved problem.",
            10,
        )
    )
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------
def build() -> dict:
    if _sha256_path(V1_ARTIFACT) != V1_ARTIFACT_SHA256:
        raise ValueError(
            "v1 artifact digest moved: v2 re-floors the package the "
            "referees actually reviewed, or it re-floors nothing"
        )
    v1 = json.loads(V1_ARTIFACT.read_text())
    registry = v1b.cell_registry()
    cells = _gated_cells(registry)
    fit_series = v1b.claiming_series(CLAIM_2014)
    resolution_series = v1b.claiming_series(CLAIM_2023)

    bounds = _lower_bounds(v1, cells)
    deviations = panel_deviations(
        cells, fit_series, resolution_series, registry
    )
    binding = PANEL_DEFINITIONS[BINDING_PANEL]

    surfaces = {
        panel_name: {
            str(rho): gated_surface(deviations, bounds, panel=panel, rho=rho)
            for rho in RHO_SENSITIVITY
        }
        for panel_name, panel in PANEL_DEFINITIONS.items()
    }
    recommended = surfaces[BINDING_PANEL][str(DRAFT_RHO)]
    exposure = null_rule_exposure(
        deviations, recommended, bounds, panel=binding
    )
    rolling = rolling_origin_provenance(
        cells, fit_series, resolution_series, registry, panel=binding
    )
    quiet = quietest_window_ranking(resolution_series, cells)
    shock = shock_partition_asymmetry(resolution_series, cells)
    fenced = build_fenced_reference()

    artifact = {
        "schema_version": SCHEMA_VERSION,
        "run": RUN,
        "status": (
            "PRE-LOCK EVIDENCE, SECOND PASS. NOT A GATE RUN, NOT A "
            "LOCK, NOT A CANDIDATE SCORE. gates.yaml is byte-identical "
            "to origin/master and carries gate_3 locked: false with no "
            "thresholds."
        ),
        "supersedes": {
            "artifact": str(V1_ARTIFACT.relative_to(REPO)),
            "sha256": V1_ARTIFACT_SHA256,
            "relationship": (
                "v1 is READ, never rewritten. Its file, its builder and "
                "its 31-test suite are byte-identical on this branch "
                "and still pass. v2 re-floors the same surface under "
                "the instrument the referee round demanded and carries "
                "every correction both referees made."
            ),
            "referee_verdicts": {
                "lens_A_protocol_and_record": "NOT LOCK-READY",
                "lens_B_numbers_and_statistics": "NOT LOCK-READY",
                "arithmetic_disputed": False,
                "central_settlement_finding_disputed": False,
            },
        },
        "answers": {
            "B1": "candidate_reference_fence",
            "A6_B2": (
                "null_rule_panel + tolerance_law + gated_surface + "
                "null_rule_exposure"
            ),
            "A7_B3": "pass_rule_draft",
            "A8": "description_defect_A8",
            "everything_else": "referee_corrections",
        },
        "protocol": {
            "vintage_boundary_year": v1b.VINTAGE_BOUNDARY_YEAR,
            "T_star": T_STAR,
            "T_star_leakage_class": "true_vintage_artifact",
            "T_star_leakage_class_reason": (
                "the 2014 Supplement's OWN note says data for current "
                "and prior years are subject to revision with each "
                "annual update, so a 2014 analyst reading their own "
                "table would drop the terminal row. T* = 2012 is "
                "reconstructible at true vintage and is not an "
                "after-the-fact selection. v1 logged it as unpinned "
                "leakage because it never quoted that sentence."
            ),
            "fit_window": [FIT_FIRST_YEAR, T_STAR],
            "fit_source": str(CLAIM_2014.relative_to(REPO)),
            "fit_source_sha256": _sha256_path(CLAIM_2014),
            "resolution_source": str(CLAIM_2023.relative_to(REPO)),
            "resolution_source_sha256": _sha256_path(CLAIM_2023),
            "scored_years": [T_STAR + h for h in GATED_HORIZONS],
            "horizons": list(GATED_HORIZONS),
            "excluded_years": [2013, 2022],
            "shock_years": list(SHOCK_YEARS_V2),
            "min_settlement_age_printings": MIN_SETTLEMENT_AGE_PRINTINGS,
            "why_the_source_digests_are_here": (
                "D2 (referee A) and D7.1 (referee B): v1's fragment "
                "named both sources by PATH ONLY. Restage "
                "ssa_claim_ages_2023supplement.json -- same path, later "
                "printing -- and every tolerance moves with no contract "
                "text violated. The digests belong in the contract, "
                "not only in the artifact."
            ),
        },
        "null_rule_panel": {
            "law": TOLERANCE_LAW,
            "why_a_panel": (
                "v1 enforced its own disqualifying law -- 'a tolerance "
                "at or above the naive baseline certifies nothing' -- "
                "against exactly two rules, and selected between them "
                "per CELL on a pooled-over-horizons mean, so at an "
                "individual horizon the chosen rule could be the worse "
                "of the two and the OTHER information-null rule then "
                "fitted inside the band. Measured on v1's committed "
                "tolerances: persistence passes 5 of 108, linear_trend "
                "12 of 108, and the classical drift rule 68 of 108 with "
                "9 of 18 cells clean at every horizon. rho cannot "
                "repair this -- drift3's deviation/basis ratio has "
                "minimum 0.0000, so no positive rho excludes it "
                "everywhere. Only the BASELINE can be repaired."
            ),
            "binding_panel": BINDING_PANEL,
            "panels": {
                name: list(panel) for name, panel in PANEL_DEFINITIONS.items()
            },
            "rules": {
                name: {
                    "formula": formula,
                    "why_registered": why,
                    "information_null": True,
                    "reads": (
                        "only rows of the FIT SOURCE at or before the "
                        "origin, plus the target year label"
                    ),
                }
                for name, (_fn, formula, why) in NULL_RULE_PANEL.items()
            },
            "the_panel_is_contract_not_code": (
                "D7.3 (referee B): a mutable module dict that "
                "determines every tolerance is not a contract. The "
                "panel is enumerated in the gates.yaml fragment BY NAME "
                "AND FORMULA; adding, removing or reordering a rule is "
                "an amendment, and under no_self_rescue it applies only "
                "to runs registered after ratification."
            ),
        },
        "measurement_lower_bounds": bounds,
        "F2_panel_deviations": deviations,
        "gated_surface_recommended": recommended,
        "gated_surface_sensitivity": surfaces,
        "null_rule_exposure": exposure,
        "pass_rule_draft": pass_rule_draft(recommended, rolling),
        "candidate_reference_fence": {
            "law": FENCE_LAW,
            "answers": "B1 (referee B, blocking finding 1)",
            "fenced_reference": fenced,
            "deployed_module_fence_check": deployed_module_fence_check(),
            "where_this_belongs_in_the_contract": (
                "governance.registration and "
                "fresh_run_artifact_schema, on the gate_2 model "
                "(gates.yaml:935 and :1035-1040). It is a PRECONDITION "
                "ON CANDIDATE REGISTRATION, not a threshold."
            ),
        },
        "description_defect_A8": description_defect(),
        "rolling_origin_provenance": rolling,
        "horizon_monotonicity_by_unit": horizon_monotonicity_by_unit(
            deviations, cells, panel=binding
        ),
        "referee_corrections": {
            "settlement": settlement_corrections(v1),
            "t_star_2013_counterfactual": t_star_2013_counterfactual(
                v1, cells, fit_series, resolution_series
            ),
            "quietest_window_ranking": quiet,
            "shock_partition_asymmetry": shock,
            "instrument_and_prose": instrument_and_prose_corrections(
                v1, cells, bounds, deviations
            ),
            "ddof_convention": {
                "finding": (
                    "R9 (referee B): every other floor builder in this "
                    "repository uses ddof=1 and "
                    "build_disability_floors.py:130 calls it 'the floor "
                    "convention shared with the other runs/ artifacts'. "
                    "v1 used ddof=0 -- the only ddof=0 site in scripts/ "
                    "-- and was also the only _summarize with no "
                    "size > 1 guard. At n = 5 that made every published "
                    "sd 10.6 percent smaller than the convention."
                ),
                "resolution_in_v2": (
                    "v2 uses ddof=1 with a size > 1 guard. The only "
                    "eligible cell the convention moves is "
                    "claim_share.age67_69|male, whose instrument A goes "
                    "0.060 -> 0.066; it is still at the floor and the "
                    "collapse finding survives either way. No v2 "
                    "tolerance reads an sd at all, so the convention "
                    "affects only the measurement LOWER BOUND."
                ),
                "cells_the_convention_moves": [
                    key
                    for key in cells
                    if bounds[key]["ddof_changes_this_cell"]
                ],
            },
        },
        "not_certified": not_certified_margins(
            recommended, exposure, quiet, shock
        ),
        "roll_up": {
            "n_cells_considered": len(cells),
            "n_pairs_considered": recommended["n_pairs_considered"],
            "n_gated_v2": recommended["n_gated"],
            "n_reported_not_gated_v2": recommended["n_reported_not_gated"],
            "n_gated_v1": 108,
            "sum_of_tolerances_v2": recommended["sum_of_tolerances"],
            "sum_of_tolerances_v1": 184.052,
            "tightening_factor": round(
                184.052 / recommended["sum_of_tolerances"], 4
            ),
            "registered_null_rules_passing_a_gated_pair": sum(
                exposure["in_panel_pass_counts"].values()
            ),
            "worst_leave_one_out_exposure": exposure["leave_one_out"][
                exposure["worst_leave_one_out_rule"]
            ]["n_passed_by_the_held_out_rule"],
            "deployed_module_passes_the_fence": False,
            "gates_yaml_untouched_by_this_draft": True,
            "locked": False,
        },
        "revision_pins": {
            "v1_artifact_sha256": V1_ARTIFACT_SHA256,
            "v1_builder_sha256": V1_BUILDER_SHA256,
            "claim_ages_2014_sha256": _sha256_path(CLAIM_2014),
            "claim_ages_2023_sha256": _sha256_path(CLAIM_2023),
            "claiming_module_sha256": _sha256_path(
                REPO / "src" / "populace_dynamics" / "claiming.py"
            ),
            "gates_yaml_sha256": _sha256_path(REPO / "gates.yaml"),
        },
        "draft_gates_yaml_fragment": {
            "status": (
                "PROPOSAL ONLY. This string is NOT written to "
                "gates.yaml by this or any script. gates.yaml is "
                "byte-identical to origin/master."
            ),
            "generated_from": "gated_surface_recommended",
            "why_generated_not_handwritten": (
                "v1's fragment was hand-written and referee B measured "
                "that its own rule text did not reproduce its own "
                "numbers on 28 of 108 pairs, always in the "
                "candidate-favouring direction. Emitting the fragment "
                "from the computed surface makes that class of defect "
                "impossible, and the v2 test suite re-derives the "
                "tolerances from the STATED FORMULA rather than "
                "pinning them."
            ),
            "text": None,
        },
        "reproducibility": {
            "no_wall_clock": True,
            "no_git_derived_value": (
                "R11: v1 embedded a git commit hash obtained by "
                "shelling out, so its byte-reproduction depended on the "
                "ambient repository's HISTORY, not only on its inputs. "
                "v2 carries no git-derived value in the artifact; the "
                "commit is in the .env.json sidecar, excluded from the "
                "byte comparison."
            ),
            "rebuild_is_byte_identical": (
                "tests/test_gate3_retrodiction_floors_v2.py rebuilds "
                "via build() and compares the full text"
            ),
            "environment": "runs/gate3_retrodiction_floors_v2.env.json",
            "inputs": "runs/gate3_retrodiction_floors_v2.inputs.json",
        },
    }
    artifact["draft_gates_yaml_fragment"]["text"] = draft_fragment(
        artifact,
        recommended,
        exposure,
        artifact["candidate_reference_fence"],
        artifact["description_defect_A8"],
        artifact["pass_rule_draft"],
    )
    return artifact


SOURCE_INPUTS = (
    (
        CLAIM_2014,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2014/6b.html",
    ),
    (
        CLAIM_2023,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2023/6b.html",
    ),
    (V1_ARTIFACT, "in-repository committed evidence artifact (v1, read-only)"),
    (V1_BUILDER, "in-repository committed builder (v1, read-only)"),
    (
        REPO / "src" / "populace_dynamics" / "claiming.py",
        "in-repository module under the B1 fence check",
    ),
    (REPO / "gates.yaml", "in-repository ratified contract (read-only)"),
)


def environment_block() -> dict:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:  # pragma: no cover - provenance best effort
        commit = "unknown"
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "repo_commit": commit,
        "note": (
            "This sidecar is EXCLUDED from the byte comparison. Nothing "
            "here is an input to any number in the artifact."
        ),
    }


def main() -> None:
    artifact = build()
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n")
    INPUT_SIDECAR.write_text(
        json.dumps(
            {
                "artifact": ARTIFACT.name,
                "status": "SOURCE_INPUT_DIGESTS",
                "source_inputs": [
                    {
                        "path": str(path.relative_to(REPO)),
                        "sha256": _sha256_path(path),
                        "bytes": path.stat().st_size,
                        "official_url": url,
                    }
                    for path, url in SOURCE_INPUTS
                ],
            },
            indent=2,
        )
        + "\n"
    )
    ENV_SIDECAR.write_text(
        json.dumps(
            {
                "artifact": ARTIFACT.name,
                "status": "MEASUREMENT_ENVIRONMENT",
                "environment": environment_block(),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {ARTIFACT}")
    for key, value in artifact["roll_up"].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
