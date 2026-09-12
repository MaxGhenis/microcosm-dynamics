"""Invented complete households; no survey or benchmark inputs."""

import hashlib
import json

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("microcosm.graph.store")
from microcosm.frame import (
    EntitySchema,
    Frame,
    LinkSpec,
    MassChange,
    WeightKind,
    Weights,
)
from microcosm.graph import ContentStore, Population
from microcosm.graph.population import MassRecord
from microcosm.graph.store import StoreCorrupt, StoreUnavailable

from populace_dynamics.frame_context import (
    ContextContractError,
    read_baseline_frame,
    retain_population,
)


@pytest.fixture
def case(tmp_path):
    # Large integer IDs and leading-zero geography must survive storage.
    people = pd.DataFrame(
        {
            "person_id": np.array([2**53 + 1, 2**53 + 2, 2**53 + 3]),
            "person_household_id": np.array([10, 10, 20], dtype="int64"),
            "relationship": pd.Series([1, 2, pd.NA], dtype="Int64"),
            "flag": pd.Series([True, pd.NA, False], dtype="boolean"),
        }
    )
    homes = pd.DataFrame(
        {
            "household_id": np.array([10, 20], dtype="int64"),
            "census_block_geoid": pd.Series(
                ["010010201001001", "020130001001002"], dtype="string"
            ),
        }
    )
    frame = Frame(
        {"person": people, "household": homes},
        EntitySchema(group_entities=("household",)),
        {"household": Weights([0.0, 7.0], WeightKind.IMPORTANCE)},
        pd.Series(["a", "a", "b"], dtype="string"),
        metadata={"source": {"labels": ("invented",)}, "period": 2026},
    )
    key, node = "a" * 64, "b" * 64
    path = ContentStore(tmp_path / "store").put_frame(
        key, frame, node_key=node
    )
    args = {
        "metadata_sha256": hashlib.sha256(
            (path / "meta.json").read_bytes()
        ).hexdigest(),
        "expected_key": key,
        "expected_node_key": node,
        "membership": people[["person_id", "person_household_id"]].copy(),
        "household_ids": homes["household_id"].copy(),
        "weight_kinds": {"household": WeightKind.IMPORTANCE},
    }
    return frame, path, args


def test_reader_preserves_complete_frame_and_zero_weight_members(case):
    frame, path, args = case
    loaded = read_baseline_frame(path, **args)
    for entity in frame.entities:
        pd.testing.assert_frame_equal(
            loaded.table(entity), frame.table(entity)
        )
    pd.testing.assert_series_equal(loaded.strata, frame.strata)
    assert loaded.metadata == frame.metadata
    assert loaded.mass_log == frame.mass_log
    assert loaded.weighted_entities == ("household",)
    assert loaded.weights_for("household").kind is WeightKind.IMPORTANCE
    np.testing.assert_array_equal(
        loaded.weights_for("household").values, [0, 7]
    )
    assert loaded.n("person") == 3
    assert not isinstance(loaded, Population)


@pytest.mark.parametrize(
    "field", ["metadata_sha256", "expected_key", "expected_node_key"]
)
def test_refuses_wrong_artifact_binding(case, field):
    _, path, args = case
    args[field] = "c" * 64
    with pytest.raises(ContextContractError, match="identity"):
        read_baseline_frame(path, **args)


@pytest.mark.parametrize(
    "change", ["missing", "reordered", "rounded", "different_household"]
)
def test_refuses_membership_changes_without_filtering(case, change):
    frame, path, args = case
    before = frame.table("person").copy(deep=True)
    roster = args["membership"]
    if change == "missing":
        args["membership"] = roster.iloc[1:]
    elif change == "reordered":
        args["membership"] = roster.iloc[::-1]
    elif change == "rounded":
        args["membership"] = roster.astype("float64")
    else:
        roster.loc[0, "person_household_id"] = 20
    with pytest.raises(ContextContractError, match="membership"):
        read_baseline_frame(path, **args)
    pd.testing.assert_frame_equal(frame.table("person"), before)


def test_refuses_household_roster_change(case):
    _, path, args = case
    args["household_ids"] = args["household_ids"].iloc[::-1]
    with pytest.raises(ContextContractError, match="household roster"):
        read_baseline_frame(path, **args)


@pytest.mark.parametrize(
    "kinds",
    [
        {},
        {"household": "importance"},
        {"household": WeightKind.DESIGN},
        {"household": WeightKind.IMPORTANCE, "person": WeightKind.IMPORTANCE},
    ],
)
def test_refuses_missing_mistyped_or_relabelled_weight_kinds(case, kinds):
    _, path, args = case
    args["weight_kinds"] = kinds
    with pytest.raises(ContextContractError, match="weight"):
        read_baseline_frame(path, **args)


def test_refuses_continuing_population_file_before_reading(case):
    _, path, args = case
    with pytest.raises(ContextContractError, match="Population envelope"):
        read_baseline_frame(
            path / "absent", interpretation="continuing_population", **args
        )


def test_shared_codec_refuses_tampered_payload(case):
    _, path, args = case
    (path / "frame.json").write_text("{}")
    with pytest.raises(StoreCorrupt):
        read_baseline_frame(path, **args)


def test_v1_object_refuses_without_downgrade(case):
    _, path, args = case
    meta = json.loads((path / "meta.json").read_text())
    meta["frame_format"] = "microcosm-graph-frame-v1"
    raw = json.dumps(meta).encode()
    (path / "meta.json").write_bytes(raw)
    args["metadata_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(StoreUnavailable):
        read_baseline_frame(path, **args)


def test_v1_runtime_refuses_explicitly(case, monkeypatch):
    import microcosm.graph.store as store

    _, path, args = case
    monkeypatch.setattr(store, "_FRAME_FORMAT", "microcosm-graph-frame-v1")
    with pytest.raises(ImportError, match="Frame v2"):
        read_baseline_frame(path, **args)


def test_population_adapter_retains_ownership_ledger_and_design_anchors(case):
    frame, _, args = case
    owners = {
        (entity, column): f"original-{entity}"
        for entity in frame.entities
        for column in frame.table(entity).columns
    }
    ledger = (
        MassRecord("invented-node", "reweight", "conserve", 7, 7, (), ()),
    )
    population = Population.from_frame(
        frame,
        "original-version",
        owners,
        mass_ledger=ledger,
        design_weights={"household": np.array([3.0, 4.0])},
    )
    result = retain_population(
        population,
        **{
            key: args[key]
            for key in ("membership", "household_ids", "weight_kinds")
        },
    )
    assert result is population
    assert result.frame is frame
    assert result.owners is population.owners
    assert result.mass_ledger is population.mass_ledger
    assert result.version == "original-version"
    np.testing.assert_array_equal(result.design_weights["household"], [3, 4])
    assert result.weight_kind["household"] is WeightKind.IMPORTANCE
    assert frame.n("person") == 3


def test_frame_cannot_be_silently_promoted_to_population(case):
    frame, _, args = case
    with pytest.raises(ContextContractError, match="existing Population"):
        retain_population(
            frame,
            **{
                key: args[key]
                for key in ("membership", "household_ids", "weight_kinds")
            },
        )


@pytest.mark.parametrize("kind", list(WeightKind))
def test_all_weight_kinds_are_preserved_as_declared(case, tmp_path, kind):
    frame, _, args = case
    frame = Frame(
        {entity: frame.table(entity) for entity in frame.entities},
        frame.schema,
        {"household": Weights([0, 7], kind)},
        frame.strata,
        metadata=frame.metadata,
    )
    path = ContentStore(tmp_path / "kind-store").put_frame(
        args["expected_key"], frame, node_key=args["expected_node_key"]
    )
    args["metadata_sha256"] = hashlib.sha256(
        (path / "meta.json").read_bytes()
    ).hexdigest()
    args["weight_kinds"] = {"household": kind}
    loaded = read_baseline_frame(path, **args)
    assert loaded.weights_for("household").kind is kind
    np.testing.assert_array_equal(
        loaded.weights_for("household").values, [0, 7]
    )


def test_links_and_existing_mass_history_survive_read(case, tmp_path):
    frame, _, args = case
    link = pd.DataFrame(
        {
            "person_id": np.array([2**53 + 1, 2**53 + 3]),
            "household_id": np.array([10, 20], dtype="int64"),
            "label": pd.Series(["invented", pd.NA], dtype="string"),
        }
    )
    frame = Frame(
        {
            **{entity: frame.table(entity) for entity in frame.entities},
            "association": link,
        },
        EntitySchema(
            group_entities=("household",),
            links=(LinkSpec("association", "person", "household"),),
        ),
        {"household": frame.weights_for("household")},
        frame.strata,
        metadata=frame.metadata,
    ).with_weights(
        "household",
        Weights([0, 14], WeightKind.IMPORTANCE),
        mass=MassChange(factor=2, reason="Invented fixture weight history"),
    )
    path = ContentStore(tmp_path / "history-store").put_frame(
        args["expected_key"], frame, node_key=args["expected_node_key"]
    )
    args["metadata_sha256"] = hashlib.sha256(
        (path / "meta.json").read_bytes()
    ).hexdigest()
    loaded = read_baseline_frame(path, **args)
    assert len(loaded.mass_log) == 1
    assert loaded.mass_log == frame.mass_log
    pd.testing.assert_frame_equal(loaded.link("association"), link)
    assert loaded.metadata == frame.metadata
