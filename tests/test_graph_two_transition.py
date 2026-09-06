"""Synthetic engineering tests for two transitions in one graph.

Nothing here is a forecast. One mortality law is fitted once at the fixed
boundary year and applied twice; every earnings value is either
hand-specified or carried from a hand-specified one. The second period's
survivors, ages, and earnings are checked against directly coordinated
calls to the same operations the graph calls, not against any held-out
outcome: the holdout gate covers the first transition only, and no
second-period accuracy is claimed anywhere in this module.

No survey, panel, or administrative file is opened.
"""

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from populace_dynamics.graph.earnings import EarningsPathArtifact
from populace_dynamics.graph.model import MortalityArtifact
from populace_dynamics.graph.synthetic import (
    synthetic_earnings_path,
    write_synthetic_earnings,
    write_synthetic_inputs,
)
from populace_dynamics.graph.two_transition_synthetic import (
    synthetic_second_scenario,
    write_second_scenario,
)

#: A kernel refusal reaches the caller as the executor's node rejection.
REFUSED = (ValueError, RuntimeError)

OBS = "person_period"
PID = "person_period_person_id"
PERIOD_ID = "person_period_period_id"

NOMINAL = dict(
    earnings_unit="XTS",
    earnings_price_basis="nominal",
    earnings_calendar="calendar_year",
)
FIXED = {**NOMINAL, "earnings_price_basis": "fixed@2014"}

#: With every training row a death over a unit of exposure the fitted
#: annual probability is ``-expm1(-1)``, high enough that some seed kills
#: the whole second transition. This one does, and leaves the first with
#: survivors, which is the terminal case the plan asks for.
ALL_DIE_SECOND = {"death": 1.0, "exposure": 1.0}
ALL_DIE_SECOND_SEED = 28
#: Effectively infinite hazard: nobody reaches the transition period at
#: all, so the second application sees no active rows.
ALL_DIE_FIRST = {"death": 1.0, "exposure": 1e-9}


@pytest.fixture
def runtime():
    from populace_dynamics.graph._compat import require_graph

    try:
        require_graph()
    except ImportError as error:
        pytest.skip(str(error))
    from populace_dynamics.graph import runtime

    return runtime


@pytest.fixture
def chained():
    from populace_dynamics.graph._compat import require_graph

    try:
        require_graph()
    except ImportError as error:
        pytest.skip(str(error))
    from populace_dynamics.graph import two_transition

    return two_transition


@pytest.fixture
def inputs(tmp_path):
    return write_synthetic_inputs(tmp_path / "inputs")


def _read(path):
    return json.loads(Path(path).read_text())


def _write(path, value):
    Path(path).write_text(json.dumps(value))


def _kill(inputs, mutation):
    training = _read(inputs["training"])
    for row in training:
        row.update(mutation)
    _write(inputs["training"], training)


def _sources(tmp_path, **kwargs):
    """The optional earnings pair: a history source and a second scenario."""
    return {
        "earnings": write_synthetic_earnings(tmp_path / "inputs", **kwargs),
        "scenario2": write_second_scenario(tmp_path / "inputs", **kwargs),
    }


def _run(chained, inputs, tmp_path, out="output", earnings=None, **kwargs):
    return chained.run_two_transition_graph(
        **inputs,
        output_dir=tmp_path / out,
        **({} if earnings is None else earnings),
        **kwargs,
    )


def _plain(chained, inputs, tmp_path, **kwargs):
    return _run(chained, inputs, tmp_path, **kwargs)


def _with_earnings(chained, inputs, tmp_path, out="output", **kwargs):
    return _run(
        chained,
        inputs,
        tmp_path,
        out=out,
        earnings=_sources(tmp_path, price_basis="fixed@2014"),
        **FIXED,
        earnings_accumulate=True,
        **kwargs,
    )


class _FixedUniforms:
    """Hand the existing operation exactly the draws it would have asked."""

    def __init__(self, values):
        self.values = np.asarray(values, dtype=np.float64)

    def random(self, count):
        assert count == len(self.values)
        return self.values.copy()


def _oracle(runtime, chained, inputs, model, **coordinates):
    """Coordinate the existing operations for both transitions directly.

    This calls ``apply_mortality`` and ``advance_age`` itself, at the two
    periods, under the same fitted model and the same keyed stream the
    graph uses. It never imports a graph kernel.
    """
    from populace_dynamics.engine.steps import advance_age, apply_mortality

    frame = pd.DataFrame(_read(inputs["initial"])).sort_values("person_id")
    frame["year"] = 2014
    context = SimpleNamespace(rng_registry=None, year=2015, metadata={})
    first = apply_mortality(
        frame,
        context,
        _FixedUniforms(
            runtime.mortality_uniforms(
                frame.person_id.tolist(), period=2015, **coordinates
            )
        ),
        model=model,
    )
    aged = advance_age(first, context, np.random.default_rng(0))
    later = SimpleNamespace(rng_registry=None, year=2016, metadata={})
    second = apply_mortality(
        aged,
        later,
        _FixedUniforms(
            chained.second_transition_uniforms(
                aged.person_id.tolist(), **coordinates
            )
        ),
        model=model,
    )
    return aged, advance_age(second, later, np.random.default_rng(0))


def _fitted(runtime, inputs):
    from populace_dynamics.graph.model import fit_mortality

    return fit_mortality(
        pd.DataFrame(_read(inputs["training"])),
        pd.DataFrame(_read(inputs["rates"])),
        boundary_year=2014,
        external_vintage_year=2014,
    )


# --------------------------------------------------------------------------
# The second transition against independently coordinated operations
# --------------------------------------------------------------------------
def test_the_second_period_matches_directly_coordinated_operations(
    runtime, chained, inputs, tmp_path
):
    run = _plain(chained, inputs, tmp_path)
    model = _fitted(runtime, inputs).model
    first, second = _oracle(runtime, chained, inputs, model)
    graph_2015 = run.slices[2015]
    graph_2016 = run.slices[2016]
    assert graph_2015.person_id.tolist() == first.person_id.tolist()
    assert graph_2016.person_id.tolist() == second.person_id.tolist()
    assert graph_2015.age.tolist() == first.age.tolist()
    assert graph_2016.age.tolist() == second.age.tolist()
    assert graph_2016.year.tolist() == second.year.tolist()
    assert graph_2016.sex.tolist() == second.sex.astype(str).tolist()


@pytest.mark.parametrize(
    "coordinates",
    [
        {"experiment_id": "independent-stream"},
        {"replicate": 5},
        {"base_seed": 97},
    ],
)
def test_a_nondefault_stream_moves_both_transitions_together(
    runtime, chained, inputs, tmp_path, coordinates
):
    """A hard-coded default cannot pass both sides of this parity."""
    baseline = _plain(chained, inputs, tmp_path, out="baseline")
    changed = _plain(chained, inputs, tmp_path, out="changed", **coordinates)
    model = _fitted(runtime, inputs).model
    _, second = _oracle(runtime, chained, inputs, model, **coordinates)
    assert changed.slices[2016].person_id.tolist() == (
        second.person_id.tolist()
    )
    assert changed.slices[2016].person_id.tolist() != (
        baseline.slices[2016].person_id.tolist()
    )
    assert changed.model_payload == baseline.model_payload


def test_the_two_transitions_never_share_a_draw(runtime, chained):
    people = [100, 101, 102, 103]
    first = runtime.mortality_uniforms(people, period=2015)
    second = chained.second_transition_uniforms(people)
    assert not np.array_equal(first, second)
    np.testing.assert_array_equal(
        second, runtime.mortality_uniforms(people, period=2016)
    )


def test_a_person_carries_its_sex_and_weight_into_the_second_period(
    chained, inputs, tmp_path
):
    run = _plain(chained, inputs, tmp_path)
    declared = {
        row["person_id"]: (row["sex"], float(row["weight"]))
        for row in _read(inputs["initial"])
    }
    for year, block in run.slices.items():
        for row in block.itertuples(index=False):
            assert (row.sex, float(row.weight)) == declared[row.person_id]
        assert (block.year == year).all()
    assert run.slices[2016].person_id.is_unique


def test_the_second_period_ages_every_survivor_by_exactly_one(
    chained, inputs, tmp_path
):
    run = _plain(chained, inputs, tmp_path)
    ages = run.population.set_index(["person_id", "year"]).age
    for person in run.slices[2016].person_id:
        assert ages[(person, 2016)] == ages[(person, 2015)] + 1
        assert ages[(person, 2015)] == ages[(person, 2014)] + 1


# --------------------------------------------------------------------------
# What the first transition keeps
# --------------------------------------------------------------------------
def test_the_first_transition_is_preserved_by_the_second(
    runtime, chained, inputs, tmp_path
):
    once = runtime.run_mortality_graph(
        **inputs, output_dir=tmp_path / "once", **_only_earnings(tmp_path)
    )
    twice = _with_earnings(chained, inputs, tmp_path, out="twice")
    assert twice.model_payload == once.model_payload
    assert twice.first_earnings_payload == once.earnings_payload
    assert twice.report["first_transition"]["mass"] == once.report["mass"]
    summary = [
        {
            key: value
            for key, value in report["earnings"].items()
            if key != "artifact_key"
        }
        for report in (once.report, twice.report["first_transition"])
    ]
    assert summary[1] == summary[0]
    for year in (2014, 2015):
        before = once.manifest.population("advance").table(OBS)
        after = twice.manifest.population("advance2").table(OBS)
        columns = ["age", "sex", "period_earnings", "period_earnings_status"]
        pd.testing.assert_frame_equal(
            before.loc[before[PERIOD_ID] == year, columns].reset_index(
                drop=True
            ),
            after.loc[after[PERIOD_ID] == year, columns].reset_index(
                drop=True
            ),
        )


def _only_earnings(tmp_path):
    """The one-shot run's earnings arguments, without the second source."""
    return {
        "earnings": write_synthetic_earnings(
            tmp_path / "inputs", price_basis="fixed@2014"
        ),
        **FIXED,
        "earnings_accumulate": True,
    }


def test_the_second_application_leaves_the_boundary_year_alone(
    runtime, chained, inputs, tmp_path
):
    once = runtime.run_mortality_graph(**inputs, output_dir=tmp_path / "once")
    twice = _plain(chained, inputs, tmp_path, out="twice")
    before = once.manifest.population("advance").table(OBS)
    after = twice.manifest.population("advance2").table(OBS)
    for year in (2014, 2015):
        columns = ["survives", "death_probability"]
        left = before.loc[before[PERIOD_ID] == year]
        right = after.loc[after[PERIOD_ID] == year]
        if year == 2014:
            pd.testing.assert_frame_equal(
                left[columns].reset_index(drop=True),
                right[columns].reset_index(drop=True),
            )
        else:
            # The transition period is exactly what the second
            # application rewrites, and it did rewrite it.
            assert (
                not left[columns]
                .reset_index(drop=True)
                .equals(right[columns].reset_index(drop=True))
            )


def test_only_the_survival_readers_move_their_keys(
    runtime, chained, inputs, tmp_path
):
    once = runtime.run_mortality_graph(
        **inputs, output_dir=tmp_path / "once", **_only_earnings(tmp_path)
    )
    twice = _with_earnings(chained, inputs, tmp_path, out="twice")
    before = once.report["node_keys"]
    after = twice.report["node_keys"]
    assert set(after) - set(before) == set(chained.SECOND_NODES)
    moved = {node for node in before if after[node] != before[node]}
    # Both read ``survives`` in the expanded version, whose owner is now
    # the second application, so their input artifact keys move. Their
    # values do not; the assertions above pin that.
    assert moved == {"earnings", "evaluate"}


# --------------------------------------------------------------------------
# Mass over a base that already holds two periods
# --------------------------------------------------------------------------
def test_the_mass_receipt_names_every_period_the_base_holds(
    chained, inputs, tmp_path
):
    run = _plain(chained, inputs, tmp_path)
    mass = run.report["second_transition"]["mass"]
    before = mass["partition"]["stratum_before"]
    after = mass["partition"]["stratum_after"]
    assert set(before) == {"2014", "2015"}
    assert set(after) == {"2014", "2015", "2016"}
    for year in before:
        assert after[year] == before[year]
    assert mass["after"] == pytest.approx(
        mass["before"] + after["2016"]["synthetic"]
    )
    weights = run.population.groupby("year").weight.sum()
    assert after["2016"]["synthetic"] == pytest.approx(weights[2016])
    assert mass["before"] == pytest.approx(weights[2014] + weights[2015])


# --------------------------------------------------------------------------
# The second earnings carry
# --------------------------------------------------------------------------
def test_every_earlier_row_survives_the_second_carry(
    chained, inputs, tmp_path
):
    run = _with_earnings(chained, inputs, tmp_path)
    first = EarningsPathArtifact.from_bytes(run.first_earnings_payload)
    second = EarningsPathArtifact.from_bytes(run.earnings_payload)
    assert first.carried_through_period == 2015
    assert second.carried_through_period == 2016
    for person, period, origin, status, value in first.rows:
        assert second.at(person, period) == (origin, status, value)
    added = set(second.rows) - set(first.rows)
    assert {row[1] for row in added} == {2016}
    assert sorted(row[0] for row in added) == (
        run.slices[2016].person_id.tolist()
    )


def test_new_decedents_close_and_earlier_closures_are_kept(
    chained, inputs, tmp_path
):
    run = _with_earnings(chained, inputs, tmp_path)
    first = EarningsPathArtifact.from_bytes(run.first_earnings_payload)
    second = EarningsPathArtifact.from_bytes(run.earnings_payload)
    survivors = set(run.slices[2016].person_id.tolist())
    living = set(run.slices[2015].person_id.tolist())
    fresh = sorted(living - survivors)
    assert fresh, "the fixture needs a second-transition decedent"
    assert dict(first.closed).items() <= dict(second.closed).items()
    for person in fresh:
        assert (person, 2015) in second.closed
        assert second.history(person)[-1][0] == 2015
    assert second.closed_people == first.closed_people | set(fresh)
    assert not survivors & second.closed_people


def test_supplied_rows_for_the_dead_are_withheld_and_counted(
    chained, inputs, tmp_path
):
    run = _with_earnings(chained, inputs, tmp_path)
    summary = run.report["second_transition"]["earnings"]
    second = EarningsPathArtifact.from_bytes(run.earnings_payload)
    survivors = set(run.slices[2016].person_id.tolist())
    supplied = {row[0] for row in synthetic_second_scenario().rows}
    assert summary["scenario_rows_supplied"] == len(supplied)
    assert set(summary["scenario_rows_withheld"]) == supplied - survivors
    known_closed = set(
        EarningsPathArtifact.from_bytes(
            run.first_earnings_payload
        ).closed_people
    )
    assert set(summary["scenario_rows_withheld_known_closed"]) == known_closed
    assert set(summary["scenario_rows_withheld_new_decedents"]) == (
        supplied - survivors - known_closed
    )
    for person in summary["scenario_rows_withheld"]:
        assert second.at(person, 2016) is None


def test_known_zero_unknown_and_absent_stay_distinct_after_two_carries(
    chained, inputs, tmp_path
):
    run = _with_earnings(chained, inputs, tmp_path)
    table = run.population.set_index(["person_id", "year"])
    assert table.loc[(105, 2014), "period_earnings"] == 0.0
    assert table.loc[(105, 2014), "period_earnings_status"] == "known"
    assert table.loc[(105, 2016), "period_earnings"] == 0.0
    assert table.loc[(105, 2016), "period_earnings_status"] == "known"
    assert table.loc[(103, 2016), "period_earnings_status"] == "unknown"
    assert np.isnan(table.loc[(103, 2016), "period_earnings"])
    assert set(table.period_earnings_status) <= {
        "known",
        "unknown",
        "absent",
    }
    assert set(table.period_earnings_origin) == {"observed", "scenario"}
    # 2013 is absent from person 107's path but the population never
    # holds a 2013 row, so absence shows in the path, not the columns.
    source = synthetic_earnings_path(price_basis="fixed@2014")
    assert source.at(107, 2013) is None


def test_the_accumulator_adds_the_second_period(chained, inputs, tmp_path):
    run = _with_earnings(chained, inputs, tmp_path)
    table = run.population.set_index(["person_id", "year"])
    for person in run.slices[2016].person_id:
        before = table.loc[(person, 2015), "cumulative_known_earnings"]
        after = table.loc[(person, 2016), "cumulative_known_earnings"]
        step = table.loc[(person, 2016), "period_earnings"]
        if np.isnan(before) or np.isnan(step):
            assert np.isnan(after)
        else:
            assert after == pytest.approx(before + step)


def test_a_nominal_path_still_refuses_a_cumulative_column(
    chained, inputs, tmp_path
):
    with pytest.raises(ValueError, match="mixes price periods"):
        _run(
            chained,
            inputs,
            tmp_path,
            earnings=_sources(tmp_path),
            **NOMINAL,
            earnings_accumulate=True,
        )


def test_a_signed_second_period_can_cancel_a_total_to_a_known_zero(
    chained, inputs, tmp_path
):
    """A cancelling total is a known zero, not an unknown and not absent."""
    history = synthetic_earnings_path(
        price_basis="fixed@2014", sign_domain="signed"
    )
    directory = tmp_path / "inputs"
    directory.mkdir(parents=True, exist_ok=True)
    first = directory / "signed.json"
    first.write_bytes(history.to_bytes())
    totals = {
        person: history.prefix_total(person, 2015) for person in history.people
    }
    scenario = replace(
        synthetic_second_scenario(
            price_basis="fixed@2014", sign_domain="signed"
        ),
        rows=tuple(
            (
                (person, 2016, "scenario", "known", -totals[person])
                if totals[person] is not None
                else (person, 2016, "scenario", "unknown", None)
            )
            for person in history.people
        ),
    )
    second = directory / "signed-scenario.json"
    second.write_bytes(scenario.to_bytes())
    run = _run(
        chained,
        inputs,
        tmp_path,
        earnings={"earnings": first, "scenario2": second},
        **{**FIXED, "earnings_sign_domain": "signed"},
        earnings_accumulate=True,
    )
    table = run.population.set_index(["person_id", "year"])
    cancelled = 0
    for person in run.slices[2016].person_id:
        status = table.loc[(person, 2016), "period_earnings_status"]
        total = table.loc[(person, 2016), "cumulative_known_earnings"]
        if status == "unknown":
            assert np.isnan(total)
        else:
            assert total == pytest.approx(0.0, abs=1e-9)
            assert table.loc[(person, 2016), "period_earnings"] < 0
            cancelled += 1
    assert cancelled, "the fixture needs a cancelling survivor"
    assert EarningsPathArtifact.from_bytes(
        run.earnings_payload
    ).sign_domain == ("signed")


# --------------------------------------------------------------------------
# Terminal cases
# --------------------------------------------------------------------------
def test_an_all_dead_second_transition_adds_no_row_and_keeps_history(
    chained, inputs, tmp_path
):
    _kill(inputs, ALL_DIE_SECOND)
    run = _with_earnings(
        chained, inputs, tmp_path, base_seed=ALL_DIE_SECOND_SEED
    )
    assert set(run.slices) == {2014, 2015}
    assert 2016 not in run.report["second_transition"]["periods"]
    mass = run.report["second_transition"]["mass"]
    assert mass["after"] == pytest.approx(mass["before"])
    assert "2016" not in mass["partition"]["stratum_after"]
    first = EarningsPathArtifact.from_bytes(run.first_earnings_payload)
    second = EarningsPathArtifact.from_bytes(run.earnings_payload)
    assert second.rows == first.rows
    assert second.carried_through_period == 2016
    assert second.closed_people == set(second.people)
    summary = run.report["second_transition"]["earnings"]
    assert summary["survivors_carried"] == 0
    assert summary["decedents_closed"] == len(run.slices[2015])
    assert summary["carried_rows"] == summary["prior_rows"]


def test_an_all_dead_first_transition_leaves_the_second_nothing_to_do(
    chained, inputs, tmp_path
):
    _kill(inputs, ALL_DIE_FIRST)
    run = _with_earnings(chained, inputs, tmp_path)
    assert set(run.slices) == {2014}
    summary = run.report["second_transition"]["earnings"]
    assert summary["survivors_carried"] == 0
    assert summary["decedents_closed"] == 0
    first = EarningsPathArtifact.from_bytes(run.first_earnings_payload)
    second = EarningsPathArtifact.from_bytes(run.earnings_payload)
    assert second.rows == first.rows
    assert second.closed == first.closed
    assert run.report["second_transition"]["periods"] == {"2014": 20}


def test_a_terminal_run_still_reuses_its_own_store(chained, inputs, tmp_path):
    _kill(inputs, ALL_DIE_SECOND)
    cold = _with_earnings(
        chained, inputs, tmp_path, base_seed=ALL_DIE_SECOND_SEED
    )
    warm = _with_earnings(
        chained, inputs, tmp_path, base_seed=ALL_DIE_SECOND_SEED
    )
    assert not any(cold.report["cache_hits"].values())
    assert all(warm.report["cache_hits"].values())
    assert warm.earnings_payload == cold.earnings_payload


# --------------------------------------------------------------------------
# Cache identity: what an edit reaches
# --------------------------------------------------------------------------
def test_a_cold_run_recomputes_and_a_warm_one_does_not(
    chained, inputs, tmp_path
):
    cold = _with_earnings(chained, inputs, tmp_path)
    warm = _with_earnings(chained, inputs, tmp_path)
    assert not any(cold.report["cache_hits"].values())
    assert all(warm.report["cache_hits"].values())
    assert warm.report["node_keys"] == cold.report["node_keys"]
    assert warm.earnings_payload == cold.earnings_payload
    assert warm.model_payload == cold.model_payload
    pd.testing.assert_frame_equal(warm.population, cold.population)


def test_editing_the_second_scenario_reaches_only_its_reader(
    chained, inputs, tmp_path
):
    first = _with_earnings(chained, inputs, tmp_path)
    scenario = synthetic_second_scenario(price_basis="fixed@2014")
    person = int(first.slices[2016].person_id.iloc[0])
    edited = tmp_path / "inputs" / "scenario-edited.json"
    edited.write_bytes(
        replace(
            scenario,
            rows=tuple(
                (*row[:4], 1.0) if row[0] == person else row
                for row in scenario.rows
            ),
        ).to_bytes()
    )
    second = _run(
        chained,
        inputs,
        tmp_path,
        earnings={
            "earnings": write_synthetic_earnings(
                tmp_path / "inputs", price_basis="fixed@2014"
            ),
            "scenario2": edited,
        },
        **FIXED,
        earnings_accumulate=True,
    )
    keys, hits = second.report["node_keys"], second.report["cache_hits"]
    for node, key in first.report["node_keys"].items():
        assert (keys[node] == key) is (node != "earnings2")
        assert hits[node] is (node != "earnings2")
    assert second.earnings_payload != first.earnings_payload
    assert second.first_earnings_payload == first.first_earnings_payload
    table = second.population.set_index(["person_id", "year"])
    before = first.population.set_index(["person_id", "year"])
    assert table.loc[(person, 2016), "period_earnings"] == 1.0
    others = [p for p in second.slices[2016].person_id if p != person]
    coordinates = [(other, 2016) for other in others]
    np.testing.assert_array_equal(
        table.loc[coordinates, "period_earnings"].to_numpy(),
        before.loc[coordinates, "period_earnings"].to_numpy(),
    )
    np.testing.assert_array_equal(
        table.period_earnings_status.to_numpy(),
        before.period_earnings_status.to_numpy(),
    )


def test_editing_the_holdout_cascades_but_changes_no_value(
    chained, inputs, tmp_path
):
    """The gate is a member of the base, so later versions rekey.

    Every node that lives in or below the expanded version binds the
    gate's key through structural base membership. That moves keys; it
    changes nothing the run produces.
    """
    first = _with_earnings(chained, inputs, tmp_path)
    holdout = _read(inputs["holdout"])
    for row in holdout["outcomes"]:
        row["death"] = 1
    _write(inputs["holdout"], holdout)
    second = _with_earnings(chained, inputs, tmp_path)
    keys = second.report["node_keys"]
    moved = {
        node
        for node, key in first.report["node_keys"].items()
        if keys[node] != key
    }
    assert moved == {"evaluate", "advance2", "age2", "earnings2"}
    assert second.report["first_transition"]["fixture_verdict"] == "fail"
    assert second.report["first_transition"]["engineering_verdict"] == "pass"
    assert second.model_payload == first.model_payload
    assert second.earnings_payload == first.earnings_payload
    pd.testing.assert_frame_equal(second.population, first.population)


def test_a_failed_gate_is_a_diagnostic_and_the_run_still_finishes(
    chained, inputs, tmp_path
):
    holdout = _read(inputs["holdout"])
    holdout["outcomes"].pop()
    _write(inputs["holdout"], holdout)
    run = _with_earnings(chained, inputs, tmp_path)
    gate = run.manifest.nodes["evaluate"]
    assert gate.receipt["outcome"] == "fail"
    assert "report" not in gate.opaque_artifacts
    diagnostic = run.report["first_transition"]["evaluation_gate"]
    assert diagnostic["node_id"] == "evaluate"
    assert diagnostic["kernel_ref"] == "dynamics.mortality.evaluate@1"
    assert (
        "held-out identities must match" in diagnostic["evidence"]["message"]
    )
    assert run.report["first_transition"]["engineering_verdict"] == (
        "not_evaluated"
    )
    # The later nodes are present, and produced their outputs.
    for node in ("advance2", "age2", "earnings2"):
        assert node in run.report["node_keys"]
    assert set(run.slices) == {2014, 2015, 2016}
    assert run.earnings_payload is not None
    assert _read(tmp_path / "output" / "report.json") == run.report


# --------------------------------------------------------------------------
# What the run writes
# --------------------------------------------------------------------------
def test_the_runner_writes_a_slice_for_every_period_it_holds(
    chained, inputs, tmp_path
):
    run = _with_earnings(chained, inputs, tmp_path)
    output = tmp_path / "output"
    for year in run.slices:
        written = pd.read_csv(output / f"period-{year}.csv")
        pd.testing.assert_frame_equal(
            written, run.slices[year], check_dtype=False
        )
        assert {"person_id", "age", "sex", "weight", "year"} <= set(
            written.columns
        )
    assert (output / "model.json").read_bytes() == run.model_payload
    assert (output / "earnings.json").read_bytes() == run.earnings_payload
    assert (output / "earnings-first-transition.json").read_bytes() == (
        run.first_earnings_payload
    )
    assert _read(output / "manifest.json") == json.loads(
        run.manifest.to_json()
    )


def test_the_report_claims_no_second_period_accuracy(
    chained, inputs, tmp_path
):
    run = _with_earnings(chained, inputs, tmp_path)
    second = run.report["second_transition"]
    assert "first transition only" in second["holdout"]
    assert not any(
        key.endswith("verdict") or "accuracy" in key for key in second
    )
    joined = " ".join(run.report["limitations"])
    assert "no second-period accuracy is claimed" in joined
    assert "never fitted, projected, or imputed" in joined


def test_an_earnings_path_without_a_second_scenario_is_refused(
    chained, inputs, tmp_path
):
    with pytest.raises(ValueError, match="supplied together or not at all"):
        chained.run_two_transition_graph(
            **inputs,
            output_dir=tmp_path / "output",
            earnings=write_synthetic_earnings(tmp_path / "inputs"),
            **NOMINAL,
        )


def test_a_mortality_only_chained_run_declares_no_earnings_node(
    chained, inputs, tmp_path
):
    run = _plain(chained, inputs, tmp_path)
    assert "earnings2" not in run.report["node_keys"]
    assert run.earnings_payload is None
    assert "earnings" not in run.report["second_transition"]
    assert set(run.report["node_keys"]) == {
        "training",
        "fit",
        "initial",
        "apply",
        "advance",
        "age",
        "evaluate",
        "apply2",
        "advance2",
        "age2",
    }


# --------------------------------------------------------------------------
# Refusals through the declared second source
# --------------------------------------------------------------------------
def _broken_scenario(tmp_path, mutation, survivors):
    scenario = synthetic_second_scenario(price_basis="fixed@2014")
    rows = list(scenario.rows)
    if mutation == "stranger":
        rows.append((999, 2016, "scenario", "known", 1.0))
    elif mutation == "missing_survivor":
        rows = [row for row in rows if row[0] != survivors[0]]
    elif mutation == "wrong_period":
        rows[0] = (rows[0][0], 2017, *rows[0][2:])
    elif mutation == "observed_origin":
        rows[0] = (*rows[0][:2], "observed", *rows[0][3:])
    path = tmp_path / "inputs" / f"scenario-{mutation}.json"
    path.write_bytes(replace(scenario, rows=tuple(rows)).to_bytes())
    return path


@pytest.mark.parametrize(
    "mutation,message",
    [
        ("stranger", "not in this population"),
        ("missing_survivor", "no supplied 2016 value"),
        ("wrong_period", "not the advanced period"),
        ("observed_origin", "supplies scenario values only"),
    ],
)
def test_a_mismatched_second_scenario_is_refused(
    chained, inputs, tmp_path, mutation, message
):
    good = _with_earnings(chained, inputs, tmp_path, out="good")
    survivors = good.slices[2016].person_id.tolist()
    path = _broken_scenario(tmp_path, mutation, survivors)
    with pytest.raises(REFUSED, match=message):
        _run(
            chained,
            inputs,
            tmp_path,
            out="refused",
            earnings={
                "earnings": write_synthetic_earnings(
                    tmp_path / "inputs", price_basis="fixed@2014"
                ),
                "scenario2": path,
            },
            **FIXED,
            earnings_accumulate=True,
        )


@pytest.mark.parametrize(
    "mutation,message",
    [
        ("carried", "has not been carried yet"),
        ("closes", "closes nobody"),
        ("duplicate", "repeats person"),
    ],
)
def test_a_second_scenario_that_is_not_a_scenario_is_refused(
    chained, inputs, tmp_path, mutation, message
):
    scenario = synthetic_second_scenario(price_basis="fixed@2014")
    path = tmp_path / "inputs" / f"scenario-{mutation}.json"
    if mutation == "duplicate":
        raw = json.loads(scenario.to_bytes())
        raw["rows"].append(dict(raw["rows"][0]))
        path.write_bytes(json.dumps(raw).encode())
    elif mutation == "closes":
        path.write_bytes(
            replace(scenario, closed=((scenario.rows[0][0], 2016),)).to_bytes()
        )
    else:
        path.write_bytes(
            replace(scenario, carried_through_period=2016).to_bytes()
        )
    with pytest.raises(REFUSED, match=message):
        _run(
            chained,
            inputs,
            tmp_path,
            earnings={
                "earnings": write_synthetic_earnings(
                    tmp_path / "inputs", price_basis="fixed@2014"
                ),
                "scenario2": path,
            },
            **FIXED,
            earnings_accumulate=True,
        )


@pytest.mark.parametrize(
    "term,value",
    [
        ("earnings_unit", "GBP"),
        ("earnings_calendar", "fiscal_year"),
        ("earnings_sign_domain", "signed"),
    ],
)
def test_an_undeclared_second_scenario_term_is_refused(
    chained, inputs, tmp_path, term, value
):
    scenario = write_second_scenario(
        tmp_path / "inputs",
        name="scenario-term",
        price_basis="fixed@2014",
        **{term.removeprefix("earnings_"): value},
    )
    with pytest.raises(REFUSED, match="the run declares"):
        _run(
            chained,
            inputs,
            tmp_path,
            earnings={
                "earnings": write_synthetic_earnings(
                    tmp_path / "inputs", price_basis="fixed@2014"
                ),
                "scenario2": scenario,
            },
            **FIXED,
            earnings_accumulate=True,
        )


# --------------------------------------------------------------------------
# Refusals the graph's own invariants keep out of reach, checked directly
# --------------------------------------------------------------------------
def _kernel_context(run, *, params, artifacts=(), sources=(), version):
    """Give a kernel the tables an actual run produced."""
    population = run.manifest.population(version)
    return SimpleNamespace(
        tables={
            OBS: population.table(OBS),
            "period": population.table("period"),
        },
        weights={OBS: population.weights_for(OBS)},
        strata=population.strata,
        params=params,
        artifacts={
            name: SimpleNamespace(payload=payload)
            for name, payload in dict(artifacts).items()
        },
        sources=dict(sources),
        rng=np.random.default_rng(0),
    )


def _terms(boundary_year=2014):
    return {
        "boundary_year": boundary_year,
        "stream": ("sha256-u53-v1", "mortality", 0, 0),
        "earnings_unit": "XTS",
        "earnings_price_basis": "fixed@2014",
        "earnings_calendar": "calendar_year",
        "earnings_sign_domain": "nonnegative",
        "earnings_accumulate": True,
    }


def test_a_model_fitted_at_another_boundary_is_refused(
    chained, runtime, inputs, tmp_path
):
    run = _plain(chained, inputs, tmp_path)
    artifact = MortalityArtifact.from_bytes(run.model_payload)
    context = _kernel_context(
        run,
        version="advance",
        params={**_terms(), "boundary_year": 2013},
        artifacts={"model": artifact.to_bytes()},
    )
    with pytest.raises(ValueError, match="boundary years differ"):
        chained._apply_second(context)


def test_a_person_closed_in_the_prior_path_cannot_still_be_active(
    chained, inputs, tmp_path
):
    run = _with_earnings(chained, inputs, tmp_path)
    prior = EarningsPathArtifact.from_bytes(run.first_earnings_payload)
    living = int(run.slices[2015].person_id.iloc[0])
    reopened = replace(
        prior,
        closed=prior.closed
        + ((living, max(row[0] for row in prior.history(living))),),
    )
    scenario = tmp_path / "inputs" / "scenario2.json"
    context = _kernel_context(
        run,
        version="advance2",
        params=_terms(),
        artifacts={"prior": reopened.to_bytes()},
        sources={"scenario2": scenario},
    )
    with pytest.raises(ValueError, match="closed and still active"):
        chained._earnings_second(context)


def test_a_prior_path_carried_to_the_wrong_period_is_refused(
    chained, inputs, tmp_path
):
    """A path carried through some other period is not this run's prior."""
    run = _with_earnings(chained, inputs, tmp_path)
    prior = EarningsPathArtifact.from_bytes(run.first_earnings_payload)
    context = _kernel_context(
        run,
        version="advance2",
        params={**_terms(), "boundary_year": 2015},
        artifacts={"prior": prior.to_bytes()},
        sources={"scenario2": tmp_path / "inputs" / "scenario2.json"},
    )
    with pytest.raises(ValueError, match="carried through 2015, not 2016"):
        chained._earnings_second(context)


def test_advanced_rows_that_disagree_with_the_survivors_are_refused(
    chained, inputs, tmp_path
):
    run = _with_earnings(chained, inputs, tmp_path)
    prior = EarningsPathArtifact.from_bytes(run.first_earnings_payload)
    context = _kernel_context(
        run,
        version="advance2",
        params=_terms(),
        artifacts={"prior": prior.to_bytes()},
        sources={"scenario2": tmp_path / "inputs" / "scenario2.json"},
    )
    observations = context.tables[OBS].copy()
    survives = observations.survives.to_numpy(dtype=bool).copy()
    periods = observations[PERIOD_ID].to_numpy()
    survives[periods == 2015] = ~survives[periods == 2015]
    observations["survives"] = survives
    context.tables[OBS] = observations
    with pytest.raises(ValueError, match="advanced rows and the survivors"):
        chained._earnings_second(context)


def test_an_expansion_with_no_survivors_is_a_valid_terminal_operation(
    chained, inputs, tmp_path
):
    run = _plain(chained, inputs, tmp_path)
    context = _kernel_context(run, version="advance", params=_terms())
    observations = context.tables[OBS].copy()
    observations["survives"] = False
    context.tables[OBS] = observations
    result = chained._advance_second(context)
    assert len(result.expand[OBS]) == 0
    assert len(result.expand["period"]) == 0
    mass = result.receipt["mass"]
    assert mass["after"] == pytest.approx(mass["before"])
    assert set(mass["partition"]["stratum_after"]) == {"2014", "2015"}


def test_an_application_with_no_active_rows_writes_the_incumbents_back(
    chained, inputs, tmp_path
):
    _kill(inputs, ALL_DIE_FIRST)
    run = _plain(chained, inputs, tmp_path)
    context = _kernel_context(
        run,
        version="advance",
        params=_terms(),
        artifacts={"model": run.model_payload},
    )
    observations = context.tables[OBS]
    assert 2015 not in set(observations[PERIOD_ID])
    result = chained._apply_second(context)
    np.testing.assert_array_equal(
        result.columns[(OBS, "survives")].to_numpy(),
        observations.survives.to_numpy(dtype=bool),
    )
    np.testing.assert_allclose(
        result.columns[(OBS, "death_probability")].to_numpy(),
        observations.death_probability.to_numpy(dtype=np.float64),
    )


def test_the_second_age_claim_reuses_the_registered_kernel(chained):
    graph, registry = chained.build_two_transition_graph()
    assert graph.node("age2").kernel == "dynamics.age-claim@1"
    assert graph.node("age").kernel == "dynamics.age-claim@1"
    assert registry.get("dynamics.age-claim@1") is registry.get(
        "dynamics.age-claim@1"
    )
    refs = set(registry.refs())
    assert {
        "dynamics.mortality.apply2@1",
        "dynamics.advance2@1",
    } <= refs
    assert "dynamics.earnings.carry2@1" not in refs


def test_the_second_kernels_hash_their_own_module(chained, monkeypatch):
    from populace_dynamics.graph import two_transition

    _, registry = chained.build_two_transition_graph()
    kernel = registry.get("dynamics.mortality.apply2@1")
    before = kernel.implementation_hash()
    source = Path(two_transition.__file__).resolve()
    original = Path.read_bytes

    def changed(path):
        payload = original(path)
        if path.resolve() == source:
            payload += b"\n# a second-transition change\n"
        return payload

    monkeypatch.setattr(Path, "read_bytes", changed)
    assert kernel.implementation_hash() != before


def test_the_graph_keeps_every_node_the_one_shot_graph_declared(
    runtime, chained
):
    terms = runtime.earnings_params(
        unit="XTS",
        price_basis="fixed@2014",
        calendar="calendar_year",
        sign_domain="nonnegative",
        accumulate=True,
    )
    once, _ = runtime.build_graph(earnings=terms)
    twice, _ = chained.build_two_transition_graph(earnings=terms)
    assert twice.nodes[: len(once.nodes)] == once.nodes
    assert twice.country == once.country
    assert twice.mass_partition == once.mass_partition
    assert [source.name for source in twice.sources] == [
        source.name for source in once.sources
    ] + ["scenario2"]
