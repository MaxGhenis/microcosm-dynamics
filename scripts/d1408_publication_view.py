"""Reduce d1408 aggregates to the public schema and prove it differences safely.

Verification class: labelled diagnostic publication guard under ruling
d1408. It reads only already-suppressed aggregate dictionaries, never
microdata. The first review round showed that publishing many nested
subtotals let a reader recover groups of fewer than ten people by
subtraction. The public view therefore keeps, per result and wave, one
flagged subtotal and the admitted denominators; it reports each payment
path only as "none", "fewer than ten", "ten or more" or "withheld"; and
``differencing_violations`` enumerates every signed combination of up to
four published counts within a population family and refuses any that
equals one through nine.
"""

from __future__ import annotations

import itertools
import math

SMALL = "<10"
NONE = "none"
FEWER_THAN_TEN = "fewer than ten"
TEN_OR_MORE = "ten or more"
WITHHELD = "withheld"

# Results that describe the same people are differenced together.
FAMILIES = {
    "first_estimates": "first_estimates",
    "track_m_minimum_benefit": "track_m",
    "r7_sharing": "r7",
    "cost_ordering_r7": "r7",
    "cola": "projection",
    "fra68": "projection",
}
PEOPLE_KEYS = frozenset(
    {
        "people",
        "admitted_people",
        "changed_recipients",
        "changed_receiving_people",
        "people_upper_bound",
        "real_roster_people",
        "pre1917_flagged_people",
        "pre1917_evaluations",
        "pre1917_flagged_evaluations",
    }
)
RECORD_KEYS = frozenset({"worker_records", "admitted_worker_records"})
# Copied verbatim from the committed artifact; already public.
EXEMPT_KEYS = frozenset({"committed_admitted_denominators"})
MAX_TERMS = 4


def path_category(cell) -> str:
    """Describe a payment-path cell without publishing its count."""
    if cell is None:
        return NONE
    people = cell.get("people") if isinstance(cell, dict) else cell
    if isinstance(people, bool):
        raise ValueError("boolean is not a people count")
    if isinstance(people, int):
        if people < 0:
            raise ValueError("negative people count")
        return (
            NONE
            if people == 0
            else (FEWER_THAN_TEN if people < 10 else TEN_OR_MORE)
        )
    if people == SMALL:
        return FEWER_THAN_TEN
    if isinstance(people, str):
        return WITHHELD
    raise ValueError(f"unrecognized path cell: {cell!r}")


def flagged_cell(cell) -> dict:
    """Keep a flagged subtotal's count, records, weight and share only."""
    keys = ("people", "worker_records", "weight", "admitted_weight_share")
    return {key: cell[key] for key in keys if key in cell}


def _copy(result, keys):
    return {key: result[key] for key in keys if key in result}


IDENTITY = (
    "header",
    "label",
    "result",
    "artifact",
    "code_commit",
    "code_commit_basis",
    "commit_basis",
    "code_commit_reason",
    "parameter_commit",
    "verification",
    "method",
    "real_data_files_read",
    "guard_findings",
    "pre_1917_refusal",
    "historical_source_identity",
)


def first_estimates_view(result) -> dict:
    counts = result["counts"]
    view = _copy(
        result,
        IDENTITY
        + (
            "reproduction_check",
            "headline_changes",
            "headline_changes_reason",
            "parameter_bundle_verified",
            "registration_configurations",
        ),
    )
    view["counts"] = {
        "real_roster_people": counts["real_roster_people"],
        "real_roster_weight": counts["real_roster_weight"],
        "support_upper_bound": counts["support_upper_bound"],
        "actual_person_upper_bound": counts["actual_person_upper_bound"],
        "expected_support_bound": counts["expected_support_bound"],
        "upper_bounds_with_committed_admitted_denominators": counts[
            "upper_bounds_with_committed_admitted_denominators"
        ],
        "committed_admitted_denominators": counts[
            "committed_admitted_denominators"
        ],
        "pre1917_evaluations": counts["pre1917_evaluations"],
        "pre1917_reason": counts["pre1917_reason"],
    }
    return view


def _zero_change_summary(rows) -> dict:
    """Summarize Track M's row changes; refuse anything but exact zeros."""
    cells = 0
    for row in rows.values():
        for change in row["changes"].values():
            cells += 1
            if (
                change["changed_receiving_people"] != 0
                or change["supported_subset_change_percentage_points"] != 0
                or change["change_in_admitted_people"] != 0
            ):
                raise ValueError(
                    "a nonzero Track M change needs a reviewed public form"
                )
    exact = all(
        cell["exact_match"]
        for row in rows.values()
        for cell in row["legacy_reproduction"].values()
    )
    return {
        "cells": cells,
        "legacy_reproduction_exact_in_every_cell": exact,
        "changed_receiving_people_in_every_cell": 0,
        "model_share_change_percentage_points_in_every_cell": 0.0,
    }


def minimum_view(result) -> dict:
    view = _copy(
        result,
        IDENTITY
        + ("psid_files_match_artifact_sha256", "legacy_reproduction_verified"),
    )
    readings = {}
    for name, reading in result["readings"].items():
        supported = reading["supported"]
        public = {
            "flagged_supported": (
                flagged_cell(supported["all_flagged_evaluations"])
                if name == "scored"
                else WITHHELD
            ),
            "paths": {
                key: path_category(supported[key])
                for key in (
                    "admitted_flagged_worker_owners",
                    "linked_auxiliary_basis",
                    "factor_entered_survivor_payment_gate",
                    "factor_entered_inverse_ms5_pia",
                )
            },
            "pre1917_flagged_people": reading["pre1917_unsupported"][
                "all_flagged_evaluations"
            ]["people"],
            "changes": _zero_change_summary(reading["rows"]),
            "legacy_reproduction_verified": reading[
                "legacy_reproduction_verified"
            ],
        }
        public["admitted_people"] = reading["admitted_people"]
        public["admitted_weight"] = reading["admitted_weight"]
        if name == "scored":
            # The sensitivity reading's record total differs by a small
            # removed-record group, so only the scored total is public.
            public["admitted_worker_records"] = reading[
                "admitted_worker_records"
            ]
        readings[name] = public
    view["readings"] = readings
    return view


def _share_cells(model_shares) -> dict:
    out = {}
    for package, cells in model_shares.items():
        out[package] = {}
        for cell, value in cells.items():
            if value["affected_people"] == 0:
                changes = [
                    leaf
                    for group in (
                        "model_bucket_changes_pp",
                        "model_threshold_changes_pp",
                    )
                    for leaf in value.get(group, {}).values()
                ]
                if any(change != 0 for change in changes):
                    raise ValueError("unaffected cell reports a change")
                out[package][cell] = "no change"
            else:
                out[package][cell] = WITHHELD
    return out


def sharing_view(result) -> dict:
    view = _copy(result, IDENTITY + ("reproduction",))
    view["admitted"] = result["admitted"]
    view["flagged_supported"] = flagged_cell(
        result["flagged_supported"]["admitted_recipients"]
    )
    view["pre1917_flagged_people"] = result["flagged_pre_1917"][
        "admitted_recipients"
    ]["people"]
    flow = result["flow"]
    view["paths"] = {
        key: path_category(flow[key]["admitted_recipients"])
        for key in (
            "entered_changed_computed_payment",
            "computed_own_payment",
            "linked_survivor_basis",
        )
    }
    view["paths"]["inverse_ms5_pia"] = flow["inverse_ms5_pia"]
    view["paths"]["disability_basis"] = flow["disability_basis"]
    changes = result["changes"]
    view["changes"] = {
        "status": changes["status"],
        "aggregate_cost_change_pp": changes["aggregate_cost_change_pp"],
        "model_share_cells": _share_cells(changes["model_shares"]),
    }
    return view


PROJECTION_PATHS = (
    "own_record",
    "linked_spouse_basis",
    "deceased_auxiliary_basis",
    "opening_stock_adjustment",
    "positive_worker_payment",
    "positive_survivor_payment",
    "positive_spouse_basis_factor_unused",
    "positive_opening_stock_adjustment",
)


def projection_pre1917(result) -> int | str:
    """Zero only when no wave or row emits a positive pre-1917 cell."""
    cells = [
        value
        for wave in result.get("counts", {}).values()
        for key, value in wave.items()
        if key.startswith("unsupported_pre1917/")
    ] + [
        value
        for row in result.get(
            "admitted_beneficiary_counts_by_row", {}
        ).values()
        for key, value in row.items()
        if key.startswith("unsupported_pre1917/")
    ]
    if all(
        isinstance(cell, dict) and cell.get("people") == 0 for cell in cells
    ):
        return 0
    return WITHHELD


def projection_view(result) -> dict:
    view = _copy(
        result,
        IDENTITY
        + (
            "reproduction_check",
            "changed_recipient_definition",
            "counts_verified",
            "cross_result_publication_audit",
            "headline_changes",
        ),
    )
    view["pre1917_flagged_evaluations"] = projection_pre1917(result)
    waves = {}
    for wave, counts in result["counts"].items():
        flagged = counts.get("supported/factor_evaluation")
        waves[wave] = {
            "seed_cohort_weight": counts["seed_cohort_weight"],
            "flagged_supported": (
                flagged_cell(flagged)
                if flagged is not None
                else {"people": 0, "worker_records": 0, "weight": 0}
            ),
            "paths": {
                role: path_category(counts.get(f"supported/{role}"))
                for role in PROJECTION_PATHS
            },
        }
    view["waves"] = waves
    view["admitted_by_row"] = {
        row: {
            "admitted_people": value["admitted_people"],
            "admitted_weight": value["admitted_weight"],
        }
        for row, value in result["admitted_beneficiary_counts_by_row"].items()
    }
    return view


VIEWS = {
    "first_estimates": first_estimates_view,
    "track_m_minimum_benefit": minimum_view,
    "r7_sharing": sharing_view,
    "cost_ordering_r7": sharing_view,
    "cola": projection_view,
    "fra68": projection_view,
}


def public_view(result) -> dict:
    """Return the reviewed public schema for one diagnostic result."""
    return VIEWS[result["result"]](result)


def published_counts(document):
    """Yield (family, unit, path, value) for every published integer count."""
    for index, result in enumerate(document["results"]):
        family = FAMILIES[result["result"]]
        yield from _walk(result, family, (f"results[{index}]",))


def _walk(value, family, path):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in EXEMPT_KEYS:
                continue
            here = path + (key,)
            if (key in PEOPLE_KEYS or key in RECORD_KEYS) and _is_count(item):
                unit = "people" if key in PEOPLE_KEYS else "worker_records"
                yield family, unit, "/".join(here), item
            else:
                yield from _walk(item, family, here)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, family, path + (str(index),))


def _is_count(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and float(value).is_integer()
    )


def differencing_violations(document, max_terms: int = MAX_TERMS):
    """Every signed sum of 2..max_terms distinct published counts, with at
    least one added and one subtracted, that equals one through nine.

    Counts are pooled by population family and unit. Cells with equal
    values are kept distinct, so aliases are enumerated too.
    """
    pools = {}
    for family, unit, path, value in published_counts(document):
        pools.setdefault((family, unit), []).append((path, int(value)))
    violations = []
    for (family, unit), cells in sorted(pools.items()):
        positive = [cell for cell in cells if cell[1] > 0]
        for size in range(2, max_terms + 1):
            for combo in itertools.combinations(positive, size):
                for signs in itertools.product((1, -1), repeat=size):
                    if 1 not in signs or -1 not in signs:
                        continue
                    total = sum(
                        sign * value
                        for sign, (_, value) in zip(signs, combo, strict=True)
                    )
                    if 0 < total < 10:
                        violations.append(
                            {
                                "family": family,
                                "unit": unit,
                                "terms": [
                                    ("+" if sign > 0 else "-") + path
                                    for sign, (path, _) in zip(
                                        signs, combo, strict=True
                                    )
                                ],
                                "value": total,
                            }
                        )
    return violations
