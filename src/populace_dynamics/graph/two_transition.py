"""Chain a second transition onto the existing one-shot mortality graph.

This is a sibling of :mod:`populace_dynamics.graph.runtime`, not a
replacement. It calls that module's :func:`build_graph`, keeps every node
and kernel it returns, and adds four more: a second application of the
*same* fitted law, a second expansion, a second age claim, and a second
earnings carry. The result is one compiled graph holding two chained
transitions, so the second period's rows are produced inside the same
execution as the first's rather than by feeding one run into another.

Nothing here fits a second model. ``fit`` runs once, at the fixed
boundary year, and both application nodes read its artifact through the
same declared edge. The second application draws at the second
transition's own period, so the two transitions cannot share a draw.

The holdout gate is the first transition's and stays that way. Nothing
in this module evaluates the second period against held-out outcomes,
and no accuracy claim is made for it. What the tests check about the
second transition is engineering parity: that it agrees with directly
coordinated calls to the same mortality and ageing operations under the
same fitted model and the same keyed uniforms.

Everything the module reads is hand-specified. No survey, panel, or
administrative file is opened, and no statutory quantity is computed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from microcosm.frame import Weights
from microcosm.graph.decl import (
    ArtifactInput,
    ArtifactOutput,
    Graph,
    Node,
    Owned,
    Slice,
    SourceRef,
    StructuralDelta,
    compile_graph,
)
from microcosm.graph.executor import run_graph
from microcosm.graph.kernel import KernelResult
from microcosm.graph.store import ContentStore

from populace_dynamics.engine.steps import advance_age, apply_mortality

from . import earnings as earnings_module
from . import runtime as runtime_module
from .earnings import EarningsPathArtifact
from .model import MortalityArtifact, json_bytes, parse_json
from .runtime import (
    ACCUMULATOR,
    CODEC,
    EARNINGS_TYPE,
    MODEL_TYPE,
    OBS,
    OID,
    PERIOD_ID,
    PID,
)

#: The second period's supplied values arrive as their own declared
#: source, so editing them cannot reach the first transition.
SCENARIO_SOURCE = "scenario2"

#: The node ids this module adds. Everything else in the graph is what
#: :func:`populace_dynamics.graph.runtime.build_graph` already declared.
SECOND_NODES = ("apply2", "advance2", "age2", "earnings2")

_LIMITATIONS = (
    "Synthetic engineering fixture; no scientific or national-population"
    " certification, and no genuine panel is read.",
    "The holdout gate evaluates the first transition only. Nothing here"
    " evaluates the second period against held-out outcomes, and no"
    " second-period accuracy is claimed.",
    "One mortality law is fitted once, at the fixed boundary year, and"
    " applied to both transitions. No second fit and no drift is modelled.",
    "Earnings are retained, never fitted, projected, or imputed. A"
    " scenario value is a supplied fixture input.",
    "Births, immigration, household accounting, and the rest of the M6"
    " loop are outside this slice.",
)


def _series(values, ids, entity=OBS, dtype="int64"):
    return runtime_module._series(values, ids, entity=entity, dtype=dtype)


def _periods(context, observations):
    return runtime_module._periods(context, observations)


def _slice(context, observations=None):
    return runtime_module._slice(context, observations)


class _SecondPeriodContext:
    """The existing draw adapter, addressed at the second transition.

    The first application asks the registered generator for the period
    after the boundary; this one asks for the period after that. Nothing
    else differs, so the two transitions read disjoint coordinates of the
    same keyed stream and can never share a draw.
    """

    def __init__(self, params):
        self.year = int(params["boundary_year"]) + 2
        self.metadata = {}
        self.rng_registry = self  # Existing apply_mortality tests for None.
        self.stream = tuple(params["stream"])

    def person_generator(self, module, person_id):
        return runtime_module._PersonGenerator(
            person_id, module, self.year, self.stream
        )


def _apply_second(context):
    """Apply the same fitted law again, at the transition period's rows.

    Only rows at the transition period are touched. Every other period
    keeps the survival and probability it already carries, so the first
    transition's values are preserved even though this node now owns the
    two columns in the expanded version.
    """
    artifact = MortalityArtifact.from_bytes(context.artifacts["model"].payload)
    boundary = int(context.params["boundary_year"])
    if artifact.boundary_year != boundary:
        raise ValueError("mortality fit and application boundary years differ")
    model = artifact.model
    observations = context.tables[OBS]
    periods = _periods(context, observations).to_numpy()
    transition = boundary + 1
    active = periods == transition
    moving = observations.loc[active]
    frame = _slice(context, moving)
    survived = apply_mortality(
        frame,
        _SecondPeriodContext(context.params),
        context.rng,
        model=model,
    )
    probability = observations.death_probability.to_numpy(
        dtype=np.float64
    ).copy()
    survives = observations.survives.to_numpy(dtype=bool).copy()
    probability[active] = model.probabilities(frame)
    survives[active] = frame.person_id.isin(survived.person_id).to_numpy()
    ids = observations[OID].tolist()
    return KernelResult(
        columns={
            (OBS, "death_probability"): _series(
                probability, ids, dtype="float64"
            ),
            (OBS, "survives"): _series(survives, ids, dtype="bool"),
        }
    )


def _multiyear_mass(weights, periods, strata, mask, advanced):
    """A declared mass receipt over a base that already holds two periods.

    The one-period helper in ``runtime`` names a single before partition,
    which is right for a base that holds only the boundary year and wrong
    here: this base holds the boundary year and the transition period,
    and the receipt has to name both.
    """
    weights = np.asarray(weights, dtype=np.float64)
    periods = np.asarray(periods, dtype=np.int64)
    strata = np.asarray(list(strata), dtype=object)
    added_weights = weights[mask]
    added_strata = strata[mask]
    added_periods = np.full(len(added_weights), advanced, dtype=np.int64)

    def totals(values, labels):
        if not len(values):
            return {}
        frame = pd.DataFrame(
            {"weight": np.asarray(values, dtype=np.float64), "stratum": labels}
        )
        return {
            str(label): float(value)
            for label, value in frame.groupby("stratum", observed=True)
            .weight.sum()
            .items()
        }

    def partitioned(values, at_periods, labels):
        if not len(values):
            return {}
        frame = pd.DataFrame(
            {
                "weight": np.asarray(values, dtype=np.float64),
                "period": at_periods,
                "stratum": labels,
            }
        )
        return {
            str(int(period)): totals(block.weight, block.stratum)
            for period, block in frame.groupby("period", observed=True)
        }

    after_weights = np.concatenate([weights, added_weights])
    after_periods = np.concatenate([periods, added_periods])
    after_strata = np.concatenate([strata, added_strata])
    return {
        "policy": "declared",
        "before": float(weights.sum()),
        "after": float(after_weights.sum()),
        "stratum_before": totals(weights, strata),
        "stratum_after": totals(after_weights, after_strata),
        "partition": {
            "entity": "period",
            "column": "period",
            "stratum_before": partitioned(weights, periods, strata),
            "stratum_after": partitioned(
                after_weights, after_periods, after_strata
            ),
        },
    }


def _advance_second(context):
    """Copy the transition period's survivors into the advanced period."""
    observations = context.tables[OBS]
    boundary = int(context.params["boundary_year"])
    transition = boundary + 1
    advanced = boundary + 2
    periods = _periods(context, observations).to_numpy()
    mask = (periods == transition) & observations.survives.to_numpy(dtype=bool)
    surviving = observations.loc[mask]
    # The adapter's year names the entrant period group; it is never
    # written back onto an incumbent observation.
    aged = advance_age(
        _slice(context, surviving),
        SimpleNamespace(year=advanced, metadata={}),
        context.rng,
    )
    old_ids = observations[OID].tolist()
    new_ids = list(range(max(old_ids) + 1, max(old_ids) + 1 + len(surviving)))
    target_ids = old_ids + new_ids
    period_ids = context.tables["period"].period_id.tolist()
    period_values = context.tables["period"].period.tolist()
    next_period = [advanced] if new_ids else []
    weights = context.weights[OBS].values
    return KernelResult(
        expand={
            OBS: _series(surviving[OID].tolist(), new_ids),
            "person": _series([], [], "person"),
            "period": _series(
                [pd.NA] * len(next_period), next_period, "period", "Int64"
            ),
        },
        columns={
            (OBS, PERIOD_ID): _series(
                observations[PERIOD_ID].tolist() + [advanced] * len(new_ids),
                target_ids,
            ),
            (OBS, "age"): _series(
                observations.age.tolist() + aged.age.tolist(), target_ids
            ),
            ("period", "period"): _series(
                period_values + next_period,
                period_ids + next_period,
                "period",
            ),
        },
        weights=Weights(
            np.concatenate([weights, weights[mask]]),
            context.weights[OBS].kind,
        ),
        receipt={
            "mass": _multiyear_mass(
                weights, periods, context.strata, mask, advanced
            )
        },
    )


def _checked_scenario(payload, params, advanced):
    """Parse the supplied second-period source and check what it is.

    It is an earnings path in its own right, so it carries the same
    declared measurement terms and the same known/unknown/absent
    discipline as the history source. What makes it a *scenario* source
    is checked here: it has not been carried, it closes nobody, and every
    row it holds is a scenario row at the one advanced period.
    """
    artifact = runtime_module._checked_path(payload, params)
    if artifact.carried_through_period is not None:
        raise ValueError("a supplied scenario source has not been carried yet")
    if artifact.closed:
        raise ValueError("a supplied scenario source closes nobody")
    for _, period, origin, _, _ in artifact.rows:
        if origin != "scenario":
            raise ValueError(
                f"the {advanced} source holds an {origin!r} row; it supplies "
                "scenario values only"
            )
        if period != advanced:
            raise ValueError(
                f"scenario period {period} is not the advanced period "
                f"{advanced}"
            )
    return artifact


def _earnings_second(context):
    """Carry the first transition's path onto the second period's rows.

    The prior path arrives as a typed artifact edge, not as a file, so
    nothing about it has to be re-authenticated here beyond what it
    declares. Every row it holds is kept; the only rows added are the
    supplied values for people who survived this transition. Supplied
    rows for anybody else are withheld and counted, never appended and
    never a reason to give a closed person another period.
    """
    params = context.params
    boundary = int(params["boundary_year"])
    transition = boundary + 1
    advanced = boundary + 2
    prior = runtime_module._checked_path(
        context.artifacts["prior"].payload, params
    )
    if prior.carried_through_period != transition:
        raise ValueError(
            f"the prior earnings path is carried through "
            f"{prior.carried_through_period}, not {transition}"
        )
    supplied = _checked_scenario(
        context.sources[SCENARIO_SOURCE].read_bytes(), params, advanced
    )
    observations = context.tables[OBS]
    periods = _periods(context, observations).to_numpy()
    people = observations[PID].to_numpy(dtype=np.int64)
    survives = observations.survives.to_numpy(dtype=bool)
    population = {int(person) for person in people}
    active = periods == transition
    living = sorted({int(person) for person in people[active]})
    survivors = sorted({int(person) for person in people[active & survives]})
    decedents = sorted({int(person) for person in people[active & ~survives]})
    if sorted({int(p) for p in people[periods == advanced]}) != survivors:
        raise ValueError("the advanced rows and the survivors disagree")
    reopened = sorted(set(living) & set(prior.closed_people))
    if reopened:
        raise ValueError(
            f"people {reopened} are closed and still active at {transition}"
        )
    for person, period, _, _, _ in supplied.rows:
        if person not in population:
            raise ValueError(
                f"the scenario source holds person {person}, "
                "who is not in this population"
            )
        if prior.at(person, period) is not None:
            raise ValueError(
                f"person {person} period {period} already has a value; "
                "an earnings path is never overwritten"
            )
    scenario = {row[0]: row for row in supplied.rows}
    unsupplied = [person for person in survivors if person not in scenario]
    if unsupplied:
        raise ValueError(
            f"survivors {unsupplied} have no supplied {advanced} value"
        )
    living_set = set(survivors)
    withheld_closed = sorted(
        person for person in scenario if person in prior.closed_people
    )
    withheld_decedents = sorted(
        person for person in scenario if person in set(decedents)
    )
    withheld = sorted(
        person for person in scenario if person not in living_set
    )
    # A decedent keeps every period it already held and takes no new one.
    # Its closure sits on its last row, which the first carry gave it at
    # the transition period. Prior closures are merged, never dropped.
    carried = prior.carried(
        [scenario[person] for person in survivors],
        closed=tuple(prior.closed)
        + tuple((person, transition) for person in decedents),
        through_period=advanced,
    )
    cells = {(row[0], row[1]): row[2:] for row in carried.rows}
    accumulate = bool(params["earnings_accumulate"])
    values = np.full(len(observations), np.nan)
    totals = np.full(len(observations), np.nan)
    statuses = []
    origins = []
    for position, (person, period) in enumerate(
        zip(people, periods, strict=True)
    ):
        cell = cells.get((int(person), int(period)))
        if cell is None:
            statuses.append("absent")
            origins.append("absent")
        else:
            origin, status, value = cell
            statuses.append(status)
            origins.append(origin)
            if status == "known":
                values[position] = float(value)
        if accumulate:
            total = carried.prefix_total(int(person), int(period))
            if total is not None:
                totals[position] = total
    ids = observations[OID].tolist()
    columns = {
        (OBS, "period_earnings"): _series(values, ids, dtype="float64"),
        (OBS, "period_earnings_status"): _series(
            statuses, ids, dtype="string"
        ),
        (OBS, "period_earnings_origin"): _series(origins, ids, dtype="string"),
    }
    if accumulate:
        columns[(OBS, ACCUMULATOR)] = _series(totals, ids, dtype="float64")
    evidence = {
        "scope": "synthetic_engineering",
        "boundary_year": boundary,
        "transition_period": transition,
        "carried_through_period": advanced,
        "people": len(carried.people),
        "prior_rows": len(prior.rows),
        "carried_rows": len(carried.rows),
        "survivors_carried": len(survivors),
        "decedents_closed": len(decedents),
        "closures_total": len(carried.closed),
        "scenario_rows_supplied": len(supplied.rows),
        "scenario_rows_withheld": withheld,
        "scenario_rows_withheld_known_closed": withheld_closed,
        "scenario_rows_withheld_new_decedents": withheld_decedents,
        "unknown_rows": sum(1 for row in carried.rows if row[3] == "unknown"),
        "known_zero_rows": sum(
            1 for row in carried.rows if row[3] == "known" and row[4] == 0.0
        ),
        "accumulated": accumulate,
        "unit": carried.unit,
        "price_basis": carried.price_basis,
        "calendar": carried.calendar,
        "sign_domain": carried.sign_domain,
        "limitations": list(_LIMITATIONS),
    }
    return KernelResult(
        artifacts={
            "carried": carried.to_bytes(),
            "summary": json_bytes(evidence),
        },
        columns=columns,
        receipt=evidence,
    )


def _second_nodes(*, boundary_year, params, earnings):
    """The four nodes this module adds to the one-shot declaration."""
    binding = (ArtifactInput("model", "fit", "model", MODEL_TYPE),)
    nodes = (
        Node(
            "apply2",
            "dynamics.mortality.apply2@1",
            population="advance",
            artifact_inputs=binding,
            inputs=(Slice(OBS, ("age", "sex")), Slice("period", ("period",))),
            params=params,
            outputs=(
                Owned(OBS, "death_probability", "float64", rewrite=True),
                Owned(OBS, "survives", "bool", rewrite=True),
            ),
        ),
        Node(
            "advance2",
            "dynamics.advance2@1",
            base="advance",
            structural=StructuralDelta.EXPAND,
            entrants=True,
            mass="declared",
            inputs=(
                Slice(OBS, ("age", "sex", "survives")),
                Slice("period", ("period",)),
            ),
            params={
                "boundary_year": boundary_year,
                "expand_cells": (
                    (OBS, PERIOD_ID, "int64"),
                    (OBS, "age", "int64"),
                    ("period", "period", "int64"),
                ),
                "expand_weight_entity": OBS,
                "expand_weight_kind": "design",
            },
        ),
        Node(
            "age2",
            "dynamics.age-claim@1",
            population="advance2",
            inputs=(Slice(OBS, ("age",)),),
            outputs=(Owned(OBS, "age", "int64", rewrite=True),),
        ),
    )
    if earnings is None:
        return nodes
    terms = {**earnings, "boundary_year": boundary_year}
    return nodes + (
        Node(
            "earnings2",
            "dynamics.earnings.carry2@1",
            population="advance2",
            sources=(SCENARIO_SOURCE,),
            artifact_inputs=(
                ArtifactInput("prior", "earnings", "carried", EARNINGS_TYPE),
            ),
            inputs=(
                Slice(OBS, ("survives",)),
                Slice("period", ("period",)),
            ),
            params=terms,
            outputs=(
                Owned(OBS, "period_earnings", "float64", rewrite=True),
                Owned(OBS, "period_earnings_status", "string", rewrite=True),
                Owned(OBS, "period_earnings_origin", "string", rewrite=True),
            )
            + (
                (Owned(OBS, ACCUMULATOR, "float64", rewrite=True),)
                if earnings["earnings_accumulate"]
                else ()
            ),
            artifact_outputs=(
                ArtifactOutput("carried", EARNINGS_TYPE),
                ArtifactOutput("summary", EARNINGS_TYPE),
            ),
        ),
    )


def build_two_transition_graph(
    *,
    boundary_year=2014,
    external_vintage_year=2014,
    experiment_id="mortality",
    replicate=0,
    base_seed=0,
    earnings=None,
):
    """Return the one-shot graph extended by a second chained transition.

    The one-shot declaration is not rebuilt here. Every node, kernel, and
    source it carries comes back from
    :func:`populace_dynamics.graph.runtime.build_graph` unchanged; this
    adds four nodes, three kernels, and one source to them.

    The second age claim names the already-registered claim kernel by its
    reference rather than registering a second object under it, which the
    registry refuses.
    """
    graph, registry = runtime_module.build_graph(
        boundary_year=boundary_year,
        external_vintage_year=external_vintage_year,
        experiment_id=experiment_id,
        replicate=replicate,
        base_seed=base_seed,
        earnings=earnings,
    )
    params = {
        "boundary_year": boundary_year,
        "stream": (
            "sha256-u53-v1",
            experiment_id,
            replicate,
            base_seed,
        ),
    }
    for kernel in (
        runtime_module._Kernel(
            "dynamics.mortality.apply2@1", _apply_second, seeded=True
        ),
        runtime_module._Kernel(
            "dynamics.advance2@1",
            _advance_second,
            structural=StructuralDelta.EXPAND,
        ),
    ):
        registry.register(kernel)
    if earnings is not None:
        registry.register(
            runtime_module._Kernel(
                "dynamics.earnings.carry2@1",
                _earnings_second,
                extra=(earnings_module,),
            )
        )
    sources = graph.sources
    if earnings is not None:
        sources += (SourceRef(SCENARIO_SOURCE, CODEC),)
    return (
        Graph(
            graph.country,
            sources,
            graph.nodes
            + _second_nodes(
                boundary_year=boundary_year, params=params, earnings=earnings
            ),
            mass_partition=graph.mass_partition,
        ),
        registry,
    )


@dataclass(frozen=True)
class TwoTransitionRun:
    """What one chained execution produced."""

    manifest: object
    report: dict
    model_payload: bytes
    population: pd.DataFrame
    slices: dict
    first_earnings_payload: bytes | None = None
    earnings_payload: bytes | None = None


def _population_frame(population, boundary_year, terms):
    """The retained rows, with the sex and weights the graph actually holds."""
    observations = population.table(OBS)
    frame = pd.DataFrame(
        {
            "person_id": observations[PID].to_numpy(dtype=np.int64),
            "year": observations[PERIOD_ID].to_numpy(dtype=np.int64),
            "age": observations.age.to_numpy(dtype=np.int64),
            "sex": observations.sex.astype(str).to_numpy(),
            "weight": population.weights_for(OBS).values,
            "survives": observations.survives.to_numpy(dtype=bool),
            "death_probability": observations.death_probability.to_numpy(
                dtype=np.float64
            ),
        }
    )
    if terms is not None:
        for column in (
            "period_earnings",
            "period_earnings_status",
            "period_earnings_origin",
        ) + ((ACCUMULATOR,) if terms["earnings_accumulate"] else ()):
            frame[column] = observations[column].to_numpy()
    del boundary_year
    return frame.sort_values(["year", "person_id"]).reset_index(drop=True)


def _plain(value):
    """Copy a manifest receipt out of its immutable containers.

    A receipt reaches the manifest frozen: mappings become
    ``mappingproxy`` and lists become tuples, neither of which the JSON
    encoder writes. The report holds a plain copy so what is written and
    what is returned are the same data.
    """
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _gate_diagnostic(node, boundary_year):
    """Keep a failed gate as evidence instead of losing the whole run."""
    return {
        "scope": "synthetic_engineering",
        "boundary_year": boundary_year,
        "next_period": boundary_year + 1,
        "engineering_verdict": "not_evaluated",
        "fixture_verdict": "not_evaluated",
        "evaluation_gate": {
            "node_id": "evaluate",
            "kernel_ref": node.kernel_ref,
            "outcome": "fail",
            "evidence": _plain(node.receipt.get("evidence", {})),
        },
    }


def run_two_transition_graph(
    *,
    training,
    rates,
    initial,
    holdout,
    output_dir,
    scenario2=None,
    boundary_year=2014,
    external_vintage_year=2014,
    experiment_id="mortality",
    replicate=0,
    base_seed=0,
    earnings=None,
    earnings_unit=None,
    earnings_price_basis=None,
    earnings_calendar=None,
    earnings_sign_domain="nonnegative",
    earnings_accumulate=False,
):
    """Run the chained graph and write artifacts in the given directory.

    ``earnings`` and ``scenario2`` are supplied together or not at all:
    the second earnings node exists only when there is a first one to
    carry from, and it needs its own declared second-period source.

    The first transition's holdout gate can fail without stopping the
    run. The executor records the failure as a receipt and completes the
    later nodes, so the second transition is still present in the
    manifest and in the report when the gate has failed.
    """
    declared = (
        earnings_unit,
        earnings_price_basis,
        earnings_calendar,
        earnings_sign_domain,
        earnings_accumulate,
    )
    if (earnings is None) != (scenario2 is None):
        raise ValueError(
            "a second-period scenario source and an earnings path are "
            "supplied together or not at all"
        )
    if earnings is None:
        if declared != (None, None, None, "nonnegative", False):
            raise ValueError(
                "earnings terms were declared without an earnings path"
            )
        terms = None
    else:
        terms = runtime_module.earnings_params(
            unit=earnings_unit,
            price_basis=earnings_price_basis,
            calendar=earnings_calendar,
            sign_domain=earnings_sign_domain,
            accumulate=earnings_accumulate,
        )
    output = Path(output_dir).resolve()
    named = (
        ("training", training),
        ("rates", rates),
        ("initial", initial),
        ("holdout", holdout),
    )
    if terms is not None:
        named += (("earnings", earnings), (SCENARIO_SOURCE, scenario2))
    sources = {name: Path(path).resolve() for name, path in named}
    graph, registry = build_two_transition_graph(
        boundary_year=boundary_year,
        external_vintage_year=external_vintage_year,
        experiment_id=experiment_id,
        replicate=replicate,
        base_seed=base_seed,
        earnings=terms,
    )
    output.mkdir(parents=True, exist_ok=True)
    store = ContentStore(output / "store")
    manifest = run_graph(
        compile_graph(graph), sources=sources, store=store, kernels=registry
    )
    (output / "manifest.json").write_text(manifest.to_json(), encoding="utf-8")
    model_payload = store.load_bytes(
        manifest.nodes["fit"].opaque_artifacts["model"]
    )
    evaluation = manifest.nodes["evaluate"]
    report_key = evaluation.opaque_artifacts.get("report")
    if report_key is not None:
        first = parse_json(store.load_bytes(report_key))
    elif evaluation.receipt.get("outcome") == "fail":
        first = _gate_diagnostic(evaluation, boundary_year)
    else:
        raise ValueError(
            "evaluation report is absent without a failed gate receipt"
        )
    report = {
        "scope": "synthetic_engineering",
        "boundary_year": boundary_year,
        "transition_period": boundary_year + 1,
        "advanced_period": boundary_year + 2,
        "first_transition": first,
        "node_keys": {name: node.key for name, node in manifest.nodes.items()},
        "cache_hits": {
            name: node.hit for name, node in manifest.nodes.items()
        },
        "model_artifact_key": manifest.nodes["fit"].opaque_artifacts["model"],
        "limitations": list(_LIMITATIONS),
    }
    first_payload = None
    earnings_payload = None
    if terms is not None:
        carry = manifest.nodes["earnings"]
        first_payload = store.load_bytes(carry.opaque_artifacts["carried"])
        report["first_transition"]["earnings"] = parse_json(
            store.load_bytes(carry.opaque_artifacts["summary"])
        )
        report["first_transition"]["earnings"]["artifact_key"] = (
            carry.opaque_artifacts["carried"]
        )
        second = manifest.nodes["earnings2"]
        earnings_payload = store.load_bytes(second.opaque_artifacts["carried"])
    population = manifest.population("advance2")
    frame = _population_frame(population, boundary_year, terms)
    report["second_transition"] = {
        "scope": "synthetic_engineering",
        "mass": _plain(manifest.nodes["advance2"].receipt["mass"]),
        "periods": {
            str(int(year)): int(count)
            for year, count in frame.year.value_counts().sort_index().items()
        },
        "holdout": "first transition only; the second period is not evaluated",
    }
    if terms is not None:
        report["second_transition"]["earnings"] = parse_json(
            store.load_bytes(
                manifest.nodes["earnings2"].opaque_artifacts["summary"]
            )
        )
        report["second_transition"]["earnings"]["artifact_key"] = (
            manifest.nodes["earnings2"].opaque_artifacts["carried"]
        )
    slices = {
        int(year): block.reset_index(drop=True)
        for year, block in frame.groupby("year", sort=True)
    }
    (output / "report.json").write_bytes(json_bytes(report))
    (output / "model.json").write_bytes(model_payload)
    if first_payload is not None:
        (output / "earnings-first-transition.json").write_bytes(first_payload)
    if earnings_payload is not None:
        (output / "earnings.json").write_bytes(earnings_payload)
    for entity in (OBS, "person", "period"):
        population.table(entity).to_csv(output / f"{entity}.csv", index=False)
    frame.to_csv(output / "population.csv", index=False)
    for year, block in slices.items():
        block.to_csv(output / f"period-{year}.csv", index=False)
    return TwoTransitionRun(
        manifest,
        report,
        model_payload,
        frame,
        slices,
        first_payload,
        earnings_payload,
    )


def second_transition_uniforms(person_ids, **kwargs):
    """The draws the second application reads, addressed independently.

    A caller that wants to check the second transition without running it
    asks for the same coordinates the kernel asks for: the same keyed
    stream at the advanced period.
    """
    boundary_year = kwargs.pop("boundary_year", 2014)
    return runtime_module.mortality_uniforms(
        person_ids, period=boundary_year + 2, **kwargs
    )


__all__ = [
    "SCENARIO_SOURCE",
    "SECOND_NODES",
    "TwoTransitionRun",
    "build_two_transition_graph",
    "run_two_transition_graph",
    "second_transition_uniforms",
    "EarningsPathArtifact",
]
