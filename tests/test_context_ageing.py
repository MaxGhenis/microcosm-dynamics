"""Actual graph ageing with invented household context; no native inputs."""

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("microcosm.graph.executor")
from microcosm.frame import EntitySchema, Frame, WeightKind, Weights
from microcosm.graph.codecs import load_source
from microcosm.graph.decl import (
    Graph,
    Node,
    SourceRef,
    StructuralDelta,
    compile_graph,
)
from microcosm.graph.executor import run_graph
from microcosm.graph.kernel import (
    Capabilities,
    Determinism,
    KernelBase,
    KernelRegistry,
    KernelResult,
)
from microcosm.graph.store import ContentStore

from populace_dynamics.context_ageing import (
    AgeContextKernel,
    CarryContextKernel,
    annual_ageing_nodes,
    baseline_graph_outputs,
)


class InventedSource(KernelBase):
    ref = "test.invented-context@1"
    capabilities = Capabilities(
        Determinism.DETERMINISTIC, structural=StructuralDelta.CREATE
    )

    def run(self, context):
        return KernelResult(
            frame=load_source("frame-store", context.sources["baseline"])
        )


@pytest.fixture
def baseline():
    return Frame(
        {
            "person": pd.DataFrame(
                {
                    "person_id": np.array(
                        [2**53 + 1, 2**53 + 2, 2**53 + 3], dtype="int64"
                    ),
                    "person_household_id": np.array(
                        [10, 10, 20], dtype="int64"
                    ),
                    "person_tax_unit_id": np.array(
                        [100, 101, 200], dtype="int64"
                    ),
                    "age": np.array([39, 40, 70], dtype="int64"),
                    "year": np.array([2026, 2026, 2026], dtype="int64"),
                    "source_person_id": np.array(
                        [2**53 + 101, 2**53 + 102, 2**53 + 103], dtype="int64"
                    ),
                    "relationship": pd.Series([1, 2, pd.NA], dtype="Int64"),
                    "flag": pd.Series([True, pd.NA, False], dtype="boolean"),
                }
            ),
            "household": pd.DataFrame(
                {
                    "household_id": np.array([10, 20], dtype="int64"),
                    "clone": np.array([0, 1], dtype="int64"),
                    "origin": pd.Series(
                        ["invented-a", "invented-b"], dtype="string"
                    ),
                    "block": pd.Series(
                        ["001000000000001", "002000000000002"], dtype="string"
                    ),
                }
            ),
            "tax_unit": pd.DataFrame(
                {"tax_unit_id": np.array([100, 101, 200], dtype="int64")}
            ),
        },
        EntitySchema(group_entities=("household", "tax_unit")),
        {
            "person": Weights([0, 0, 7], WeightKind.DESIGN),
            "household": Weights([0, 7], WeightKind.CALIBRATED),
            "tax_unit": Weights([1, 2, 3], WeightKind.DESIGN),
        },
        pd.Series(["a", "a", "b"], dtype="string"),
        metadata={"fixture": "invented", "baseline_period": "2026-01-01"},
    )


def graph_for(frame, years=(2026, 2027)):
    nodes = [
        Node(
            "initial",
            InventedSource.ref,
            structural=StructuralDelta.CREATE,
            sources=("baseline",),
            outputs=baseline_graph_outputs(frame),
        )
    ]
    base = "initial"
    for year in years:
        pair = annual_ageing_nodes(
            base=base,
            from_year=year,
            to_year=year + 1,
            prefix=f"y{year+1}",
            membership_policy="unchanged",
        )
        nodes.extend(pair)
        base = pair[0].id
    return compile_graph(
        Graph(
            "invented-context-ageing",
            (SourceRef("baseline", "frame-store"),),
            tuple(nodes),
        )
    )


def registry():
    kernels = KernelRegistry()
    for kernel in (InventedSource(), CarryContextKernel(), AgeContextKernel()):
        kernels.register(kernel)
    return kernels


def assert_context(before, after, years):
    for entity in before.entities:
        expected = before.table(entity).copy(deep=True)
        if entity == "person":
            expected["age"] += years
            expected["year"] += years
        pd.testing.assert_frame_equal(after.table(entity), expected)
    pd.testing.assert_series_equal(after.strata, before.strata)
    # JSON object key ordering is not metadata meaning; the HDF intake
    # snapshots its manifest with sorted keys.
    assert dict(after.metadata) == dict(before.metadata)
    assert after.weighted_entities == before.weighted_entities
    for entity in before.weighted_entities:
        assert (
            after.weights_for(entity).kind is before.weights_for(entity).kind
        )
        np.testing.assert_array_equal(
            after.weights_for(entity).values, before.weights_for(entity).values
        )


def test_two_year_graph_cold_and_cache_preserve_household_context(
    baseline, tmp_path
):
    source = ContentStore(tmp_path / "source").put_frame(
        "a" * 64, baseline, node_key="b" * 64
    )
    store = ContentStore(tmp_path / "run")
    compiled = graph_for(baseline)
    snapshots = {}
    cold = run_graph(
        compiled,
        sources={"baseline": source},
        store=store,
        kernels=registry(),
        resume="forbid",
        _population_observer=lambda node, pop: snapshots.__setitem__(
            node, pop
        ),
    )
    assert_context(baseline, cold.populations["y2028.carry"], 2)
    final = snapshots["y2028.age"]
    assert final.owners[("person", "age")] == "y2028.age"
    # The structural carry owns carried cells in its new version; ageing
    # must not claim provenance columns for itself.
    assert (
        final.owners[("person", "source_person_id")]
        == snapshots["y2028.carry"].owners[("person", "source_person_id")]
    )
    np.testing.assert_array_equal(final.design_weights["tax_unit"], [1, 2, 3])
    assert len(final.mass_ledger) == 2
    assert_context(baseline, snapshots["initial"].frame, 0)
    warm = run_graph(
        compiled,
        sources={"baseline": source},
        store=store,
        kernels=registry(),
        resume="require",
    )
    assert_context(baseline, warm.populations["y2028.carry"], 2)
    assert all(node.hit for node in warm.nodes.values())


def test_checkpoint_intake_then_actual_graph_ageing(baseline, tmp_path):
    import hashlib

    checkpoint = pytest.importorskip("microcosm.build.frame_checkpoint")
    pytest.importorskip("h5py")
    from populace_dynamics.checkpoint_intake import (
        InputColumn,
        read_baseline_checkpoint,
    )

    manifest = {
        "protocol": "populace-dynamics.baseline-checkpoint-intake.v1",
        "interpretation": "baseline_frame",
        "producer_revision": "1" * 40,
        "period": "2026-01-01",
        "household_scope": "complete_households",
        "frame_metadata": dict(baseline.metadata),
    }
    path = checkpoint.write_frame_checkpoint(
        tmp_path / "invented.h5", baseline, metadata=manifest
    )
    loaded = read_baseline_checkpoint(
        path,
        checkpoint_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        expected_manifest=manifest,
        membership=baseline.person[
            ["person_id", "person_household_id"]
        ].copy(),
        household_ids=baseline.table("household").household_id.copy(),
        relationships=baseline.person[
            ["person_id", "person_household_id", "person_tax_unit_id"]
        ].copy(),
        weight_kinds={
            entity: baseline.weights_for(entity).kind
            for entity in baseline.weighted_entities
        },
        required_inputs={
            "person": {
                "age": InputColumn("int64", False),
                "year": InputColumn("int64", False),
            },
            "household": {"block": InputColumn("string", False)},
        },
        clone_provenance={
            "person": baseline.person[
                ["person_id", "source_person_id"]
            ].copy(),
            "household": baseline.table("household")[
                ["household_id", "clone", "origin"]
            ].copy(),
        },
    )
    source = ContentStore(tmp_path / "source").put_frame(
        "c" * 64, loaded, node_key="d" * 64
    )
    result = run_graph(
        graph_for(loaded, years=(2026,)),
        sources={"baseline": source},
        store=ContentStore(tmp_path / "run"),
        kernels=registry(),
    )
    assert_context(baseline, result.populations["y2027.carry"], 1)


def test_household_only_weights_use_shared_resolution(baseline, tmp_path):
    frame = Frame(
        {entity: baseline.table(entity) for entity in baseline.entities},
        baseline.schema,
        {"household": baseline.weights_for("household")},
        baseline.strata,
        metadata=baseline.metadata,
    )
    source = ContentStore(tmp_path / "source").put_frame(
        "e" * 64, frame, node_key="f" * 64
    )
    result = run_graph(
        graph_for(frame, years=(2026,)),
        sources={"baseline": source},
        store=ContentStore(tmp_path / "run"),
        kernels=registry(),
    )
    assert_context(frame, result.populations["y2027.carry"], 1)
    assert result.populations["y2027.carry"].weighted_entities == (
        "household",
    )


@pytest.mark.parametrize(
    "column,dtype",
    [("source_person_id", "uint64"), ("age", "int16"), ("age", "Float64")],
)
def test_unsupported_owned_dtype_refuses_without_coercion(
    baseline, column, dtype
):
    baseline.person[column] = baseline.person[column].astype(dtype)
    before = baseline.person.copy(deep=True)
    with pytest.raises(ValueError, match=f"person.{column}"):
        baseline_graph_outputs(baseline)
    pd.testing.assert_frame_equal(before, baseline.person)


def test_ambiguous_group_weights_refuse_without_person_weight_inference(
    baseline,
):
    ambiguous = Frame(
        {entity: baseline.table(entity) for entity in baseline.entities},
        baseline.schema,
        {
            entity: baseline.weights_for(entity)
            for entity in ("household", "tax_unit")
        },
        baseline.strata,
        metadata=baseline.metadata,
    )
    with pytest.raises(ValueError, match="unambiguous declared weights"):
        baseline_graph_outputs(ambiguous)
    assert ambiguous.weighted_entities == ("household", "tax_unit")


@pytest.mark.parametrize(
    "from_year,to_year,policy",
    [
        (2026, 2028, "unchanged"),
        (True, 2, "unchanged"),
        (2026, 2027, "mortality"),
    ],
)
def test_explicit_annual_unchanged_membership_contract(
    from_year, to_year, policy
):
    with pytest.raises(ValueError):
        annual_ageing_nodes(
            base="initial",
            from_year=from_year,
            to_year=to_year,
            prefix="next",
            membership_policy=policy,
        )


@pytest.mark.parametrize(
    "change",
    [
        "wrong_year",
        "missing_year",
        "negative_age",
        "overflow_age",
        "float_age",
    ],
)
def test_invalid_ageing_inputs_refuse(baseline, change):
    table = baseline.person.copy(deep=True)
    if change == "wrong_year":
        table.loc[0, "year"] = 2025
    elif change == "missing_year":
        table.drop(columns="year", inplace=True)
    elif change == "negative_age":
        table.loc[0, "age"] = -1
    elif change == "overflow_age":
        table.loc[0, "age"] = np.iinfo(np.int64).max
    else:
        table["age"] = table.age.astype("float64")
    context = SimpleNamespace(
        tables={"person": table},
        params={
            "from_year": 2026,
            "to_year": 2027,
            "membership_policy": "unchanged",
        },
        rng=np.random.default_rng(0),
    )
    with pytest.raises(ValueError):
        AgeContextKernel().run(context)
