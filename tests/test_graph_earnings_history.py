"""Synthetic engineering tests for optional earnings-history retention.

Nothing here fits, projects, or imputes earnings. Every value is either
hand-specified or carried from a hand-specified one, and the next-period
values are declared fixture inputs rather than forecasts.
"""

import copy
import json
from dataclasses import replace

import numpy as np
import pytest

from populace_dynamics.graph.earnings import (
    EarningsPathArtifact,
    parse_price_basis,
)
from populace_dynamics.graph.synthetic import (
    synthetic_earnings_path,
    write_synthetic_earnings,
    write_synthetic_inputs,
)

#: A kernel refusal reaches the caller as the executor's node rejection.
REFUSED = (ValueError, RuntimeError)

NOMINAL = dict(
    earnings_unit="XTS",
    earnings_price_basis="nominal",
    earnings_calendar="calendar_year",
)
FIXED = {**NOMINAL, "earnings_price_basis": "fixed@2014"}


@pytest.fixture
def inputs(tmp_path):
    return write_synthetic_inputs(tmp_path / "inputs")


@pytest.fixture
def runtime():
    from populace_dynamics.graph._compat import require_graph

    try:
        require_graph()
    except ImportError as error:
        pytest.skip(str(error))
    from populace_dynamics.graph import runtime

    return runtime


def _path(tmp_path, name="earnings", **kwargs):
    return write_synthetic_earnings(tmp_path / "inputs", name=name, **kwargs)


def _run(runtime, inputs, tmp_path, path=None, out="output", **kwargs):
    extra = {} if path is None else {"earnings": path, **kwargs}
    return runtime.run_mortality_graph(
        **inputs, output_dir=tmp_path / out, **extra
    )


def _rows(artifact, person):
    return artifact.history(person)


# --------------------------------------------------------------------------
# The artifact contract, which needs no graph core installed
# --------------------------------------------------------------------------
def test_path_roundtrips_and_orders_its_rows():
    artifact = synthetic_earnings_path()
    restored = EarningsPathArtifact.from_bytes(artifact.to_bytes())
    assert restored.to_bytes() == artifact.to_bytes()
    assert restored.rows == tuple(sorted(artifact.rows, key=lambda r: r[:2]))
    assert restored.people == tuple(range(100, 120))


def test_row_order_does_not_change_the_serialized_path():
    artifact = synthetic_earnings_path()
    shuffled = replace(artifact, rows=tuple(reversed(artifact.rows)))
    assert shuffled.to_bytes() == artifact.to_bytes()
    for person in artifact.people:
        assert _rows(shuffled, person) == _rows(artifact, person)


def test_known_zero_unknown_and_absent_stay_distinct():
    artifact = synthetic_earnings_path()
    assert artifact.at(101, 2013) == ("observed", "known", 0.0)
    assert artifact.at(103, 2013) == ("observed", "unknown", None)
    assert artifact.at(107, 2013) is None
    assert [period for period, *_ in _rows(artifact, 107)] == [
        2012,
        2014,
        2015,
    ]


def test_a_negative_period_needs_a_signed_path():
    signed = synthetic_earnings_path(sign_domain="signed")
    assert signed.at(109, 2013) == ("observed", "known", -2500.0)
    with pytest.raises(ValueError, match="nonnegative"):
        replace(signed, sign_domain="nonnegative")


@pytest.mark.parametrize(
    "mutation",
    ["duplicate", "unknown_value", "nonfinite", "origin", "status", "closure"],
)
def test_path_fails_closed(mutation):
    artifact = synthetic_earnings_path()
    rows = list(artifact.rows)
    closed = ()
    if mutation == "duplicate":
        rows.append(rows[0])
    elif mutation == "unknown_value":
        rows[0] = (*rows[0][:3], "unknown", rows[0][4])
    elif mutation == "nonfinite":
        rows[0] = (*rows[0][:4], float("inf"))
    elif mutation == "origin":
        rows[0] = (*rows[0][:2], "imputed", *rows[0][3:])
    elif mutation == "status":
        rows[0] = (*rows[0][:3], "assumed", rows[0][4])
    else:
        closed = ((rows[0][0], 1900),)
    with pytest.raises(ValueError):
        replace(artifact, rows=tuple(rows), closed=closed)


@pytest.mark.parametrize("field", ["unit", "calendar", "sign_domain"])
def test_measurement_terms_must_be_present(field):
    with pytest.raises(ValueError, match=field.split("_")[0]):
        replace(synthetic_earnings_path(), **{field: ""})


@pytest.mark.parametrize("basis", ["", "real", "fixed@", "fixed@20x4", 2014])
def test_unsupported_price_bases_are_refused(basis):
    with pytest.raises(ValueError):
        parse_price_basis(basis)


def test_path_rejects_duplicate_json_members():
    payload = (
        synthetic_earnings_path()
        .to_bytes()
        .replace(b'"unit":"XTS"', b'"unit":"XTS","unit":"XTS"')
    )
    with pytest.raises(ValueError, match="duplicate"):
        EarningsPathArtifact.from_bytes(payload)


@pytest.mark.parametrize("mutation", ["schema", "format", "fields", "row"])
def test_payload_fails_closed(mutation):
    raw = json.loads(synthetic_earnings_path().to_bytes())
    if mutation == "schema":
        raw["schema_version"] = 99
    elif mutation == "format":
        raw["format"] = "populace-dynamics.mortality"
    elif mutation == "fields":
        raw.pop("calendar")
    else:
        raw["rows"][0] = copy.deepcopy(raw["rows"][0]) | {"note": "extra"}
    with pytest.raises(ValueError):
        EarningsPathArtifact.from_bytes(json.dumps(raw).encode())


def test_a_nominal_path_refuses_to_be_summed():
    artifact = synthetic_earnings_path()
    assert not artifact.accumulable
    with pytest.raises(ValueError, match="mixes price periods"):
        artifact.known_total(100)


def test_a_fixed_basis_path_accumulates_over_known_periods():
    artifact = synthetic_earnings_path(price_basis="fixed@2014")
    assert artifact.accumulable
    assert artifact.prefix_total(100, 2012) == 30000.0
    assert artifact.prefix_total(101, 2014) == 30500.0 + 0.0 + 32500.0
    assert artifact.prefix_total(103, 2014) is None  # An unknown period.
    assert artifact.prefix_total(107, 2014) == 33500.0 + 35500.0
    assert artifact.prefix_total(100, 1900) is None


def test_carrying_refuses_to_overwrite_an_existing_period():
    artifact = synthetic_earnings_path()
    with pytest.raises(ValueError, match="never overwritten"):
        replace(artifact, rows=artifact.rows).carried(
            [(100, 2014, "scenario", "known", 1.0)],
            closed=(),
            through_period=2015,
        )


def test_a_carried_path_cannot_hold_a_later_period():
    artifact = synthetic_earnings_path()
    with pytest.raises(ValueError, match="past the carried period"):
        replace(artifact, carried_through_period=2014)


# --------------------------------------------------------------------------
# The graph node
# --------------------------------------------------------------------------
def test_history_is_optional_and_absent_by_default(runtime, inputs, tmp_path):
    run = _run(runtime, inputs, tmp_path)
    assert "earnings" not in run.report
    assert run.earnings_payload is None
    assert set(run.next_slice.columns) == {"person_id", "age", "year"}
    assert set(run.report["node_keys"]) == {
        "training",
        "fit",
        "initial",
        "apply",
        "advance",
        "age",
        "evaluate",
    }


def test_declared_terms_without_a_path_are_refused(runtime, inputs, tmp_path):
    with pytest.raises(ValueError, match="without an earnings path"):
        runtime.run_mortality_graph(
            **inputs, output_dir=tmp_path / "output", earnings_unit="XTS"
        )


def test_survivors_carry_and_decedents_close(runtime, inputs, tmp_path):
    run = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    carried = EarningsPathArtifact.from_bytes(run.earnings_payload)
    source = synthetic_earnings_path()
    summary = run.report["earnings"]
    assert carried.carried_through_period == 2015
    assert summary["survivors_carried"] + summary["decedents_closed"] == 20
    survivors = set(run.next_slice.person_id.tolist())
    assert len(survivors) == summary["survivors_carried"]
    for person in carried.people:
        observed = [
            row for row in _rows(source, person) if row[1] != "scenario"
        ]
        held = _rows(carried, person)
        assert held[: len(observed)] == tuple(observed)
        if person in survivors:
            assert held[-1] == (
                2015,
                "scenario",
                "known",
                33000.0 + 500 * (person - 100),
            )
            assert person not in carried.closed_people
        else:
            assert tuple(held) == tuple(observed)
            assert (person, 2014) in carried.closed
    assert sorted(summary["scenario_rows_withheld"]) == sorted(
        set(carried.people) - survivors
    )


def test_every_historical_period_survives_the_carry(runtime, inputs, tmp_path):
    run = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    carried = EarningsPathArtifact.from_bytes(run.earnings_payload)
    source = synthetic_earnings_path()
    observed = [row for row in source.rows if row[2] == "observed"]
    assert len(observed) == 59
    for row in observed:
        assert carried.at(row[0], row[1]) == row[2:]
    assert run.report["earnings"]["unknown_rows"] == 1
    assert run.report["earnings"]["known_zero_rows"] == 2


def test_period_columns_report_known_zero_unknown_and_absent(
    runtime, inputs, tmp_path
):
    run = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    table = run.manifest.population("advance").table("person_period")
    table = table.set_index(
        ["person_period_person_id", "person_period_period_id"]
    )
    assert table.loc[(105, 2014), "period_earnings"] == 0.0
    assert table.loc[(105, 2014), "period_earnings_status"] == "known"
    assert table.loc[(105, 2014), "period_earnings_origin"] == "observed"
    assert set(table.period_earnings_status) <= {"known", "unknown", "absent"}
    # 2013 is not a period this population holds, so no row shows it.
    assert 2013 not in table.index.get_level_values(1)


def test_the_accumulator_adds_the_carried_period(runtime, inputs, tmp_path):
    run = _run(
        runtime,
        inputs,
        tmp_path,
        _path(tmp_path, name="fixed", price_basis="fixed@2014"),
        **FIXED,
        earnings_accumulate=True,
    )
    table = run.manifest.population("advance").table("person_period")
    table = table.set_index(
        ["person_period_person_id", "person_period_period_id"]
    )
    source = synthetic_earnings_path(price_basis="fixed@2014")
    for person in run.next_slice.person_id.tolist():
        before = table.loc[(person, 2014), "cumulative_known_earnings"]
        after = table.loc[(person, 2015), "cumulative_known_earnings"]
        step = table.loc[(person, 2015), "period_earnings"]
        expected = source.prefix_total(person, 2014)
        if expected is None:
            assert np.isnan(before) and np.isnan(after)
        else:
            assert before == pytest.approx(expected)
            assert after == pytest.approx(before + step)


def test_a_nominal_path_refuses_the_cumulative_column(
    runtime, inputs, tmp_path
):
    with pytest.raises(ValueError, match="mixes price periods"):
        _run(
            runtime,
            inputs,
            tmp_path,
            _path(tmp_path),
            **NOMINAL,
            earnings_accumulate=True,
        )


@pytest.mark.parametrize(
    "term,value",
    [
        ("earnings_unit", "GBP"),
        ("earnings_price_basis", "fixed@2014"),
        ("earnings_calendar", "fiscal_year"),
        ("earnings_sign_domain", "signed"),
    ],
)
def test_undeclared_measurement_terms_are_refused(
    runtime, inputs, tmp_path, term, value
):
    with pytest.raises(REFUSED, match="the run declares"):
        _run(
            runtime,
            inputs,
            tmp_path,
            _path(tmp_path),
            **{**NOMINAL, term: value},
        )


@pytest.mark.parametrize(
    "mutation,message",
    [
        ("stranger", "not in this population"),
        ("missing", "no observed earnings period"),
        ("late_observation", "past the boundary"),
        ("early_scenario", "not the advanced period"),
        ("carried", "has not been carried yet"),
    ],
)
def test_a_mismatched_path_is_refused(
    runtime, inputs, tmp_path, mutation, message
):
    source = synthetic_earnings_path()
    rows = list(source.rows)
    carried_through = None
    if mutation == "stranger":
        rows.append((999, 2014, "observed", "known", 1.0))
    elif mutation == "missing":
        rows = [row for row in rows if row[0] != 119 or row[1] == 2015]
    elif mutation == "late_observation":
        rows = [row for row in rows if row[:2] != (100, 2015)]
        rows.append((100, 2015, "observed", "known", 1.0))
    elif mutation == "early_scenario":
        rows = [row for row in rows if row[:2] != (100, 2012)]
        rows.append((100, 2012, "scenario", "known", 1.0))
    else:
        carried_through = 2015
    path = tmp_path / "inputs" / "broken.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        replace(
            source, rows=tuple(rows), carried_through_period=carried_through
        ).to_bytes()
    )
    with pytest.raises(REFUSED, match=message):
        _run(runtime, inputs, tmp_path, path, **NOMINAL)


def test_a_reordered_source_gives_the_same_path(runtime, inputs, tmp_path):
    """Row order is presentation, not identity -- for the path.

    The two source files differ byte for byte, so the two earnings nodes
    have different keys and recompute; what must not differ is anything
    they produce, or any mortality node.
    """
    first = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    raw = json.loads(synthetic_earnings_path().to_bytes())
    other = tmp_path / "inputs" / "reordered.json"
    other.write_bytes(
        json.dumps(raw | {"rows": list(reversed(raw["rows"]))}).encode()
    )
    second = _run(runtime, inputs, tmp_path, other, **NOMINAL)
    assert second.earnings_payload == first.earnings_payload
    # The artifact key is a store address derived from the node key, so
    # it moves with the source bytes; the summary itself must not.
    summary = [
        {
            key: value
            for key, value in run.report["earnings"].items()
            if key != "artifact_key"
        }
        for run in (first, second)
    ]
    assert summary[1] == summary[0]
    for node, key in first.report["node_keys"].items():
        if node not in {"earnings", "earnings-history"}:
            assert second.report["node_keys"][node] == key
            assert second.report["cache_hits"][node]
    columns = ["period_earnings", "period_earnings_status"]
    table = second.manifest.population("advance").table("person_period")
    before = first.manifest.population("advance").table("person_period")
    assert table[columns].equals(before[columns])


def test_an_edited_path_invalidates_only_its_own_descendants(
    runtime, inputs, tmp_path
):
    first = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    source = synthetic_earnings_path()
    edited = [
        (*row[:4], 1.0) if row[:2] == (117, 2012) else row
        for row in source.rows
    ]
    other = tmp_path / "inputs" / "edited.json"
    other.write_bytes(replace(source, rows=tuple(edited)).to_bytes())
    second = _run(runtime, inputs, tmp_path, other, **NOMINAL)
    keys, hits = second.report["node_keys"], second.report["cache_hits"]
    changed = {"earnings-history", "earnings"}
    for node, key in first.report["node_keys"].items():
        assert (keys[node] == key) is (node not in changed)
        assert hits[node] is (node not in changed)
    assert second.earnings_payload != first.earnings_payload
    table = second.manifest.population("advance").table("person_period")
    unrelated = table.person_period_person_id != 117
    before = first.manifest.population("advance").table("person_period")
    assert table.loc[unrelated, "period_earnings"].to_numpy() == pytest.approx(
        before.loc[unrelated, "period_earnings"].to_numpy()
    )


def test_the_mortality_mass_receipt_is_untouched_by_history(
    runtime, inputs, tmp_path
):
    plain = _run(runtime, inputs, tmp_path, out="plain")
    with_history = _run(
        runtime, inputs, tmp_path, _path(tmp_path), out="history", **NOMINAL
    )
    assert with_history.report["mass"] == plain.report["mass"]
    assert with_history.model_payload == plain.model_payload
    for node in plain.report["node_keys"]:
        assert (
            with_history.report["node_keys"][node]
            == plain.report["node_keys"][node]
        )
    assert with_history.next_slice.person_id.tolist() == (
        plain.next_slice.person_id.tolist()
    )


def test_a_cold_history_run_recomputes_and_a_warm_one_does_not(
    runtime, inputs, tmp_path
):
    cold = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    warm = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    assert not any(cold.report["cache_hits"].values())
    assert all(warm.report["cache_hits"].values())
    assert warm.earnings_payload == cold.earnings_payload
    assert warm.report["earnings"] == cold.report["earnings"]


def test_a_failed_history_leaves_the_earlier_nodes_visible(
    runtime, inputs, tmp_path
):
    good = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    source = synthetic_earnings_path()
    broken = tmp_path / "inputs" / "stranger.json"
    broken.write_bytes(
        replace(
            source, rows=source.rows + ((999, 2014, "observed", "known", 1.0),)
        ).to_bytes()
    )
    failed = tmp_path / "refused"
    with pytest.raises(REFUSED, match="not in this population") as raised:
        _run(runtime, inputs, tmp_path, broken, out="refused", **NOMINAL)
    # The refusal names the node and the kernel that refused.
    assert "earnings-history" in str(raised.value)
    assert "dynamics.earnings.history@1" in str(raised.value)
    # It writes no manifest, no report, and no columns: there is no
    # partial output to mistake for a finished one. What it leaves is
    # the store, holding the nodes that ran before the refusal.
    assert sorted(entry.name for entry in failed.iterdir()) == ["store"]
    assert any((failed / "store").rglob("*"))
    again = _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    assert all(again.report["cache_hits"].values())
    assert again.earnings_payload == good.earnings_payload


def test_the_run_reads_no_engine_earnings_model(runtime, inputs, tmp_path):
    import populace_dynamics.engine.steps as steps

    calls = []
    original = steps.apply_earnings
    steps.apply_earnings = lambda *a, **k: calls.append(a)
    try:
        _run(runtime, inputs, tmp_path, _path(tmp_path), **NOMINAL)
    finally:
        steps.apply_earnings = original
    assert calls == []
