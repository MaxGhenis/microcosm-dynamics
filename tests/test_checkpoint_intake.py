"""Small invented exports through the actual Microcosm checkpoint software."""

import copy
import hashlib

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("microcosm.build.frame_checkpoint")
pytest.importorskip("h5py")
from microcosm.build import frame_checkpoint
from microcosm.frame import EntitySchema, Frame, WeightKind, Weights

from populace_dynamics.checkpoint_intake import (
    InputColumn,
    read_baseline_checkpoint,
)
from populace_dynamics.frame_context import ContextContractError


@pytest.fixture
def exported(tmp_path):
    person_ids = np.array([2**63 + 1, 2**63 + 2, 2**63 + 3], dtype="uint64")
    household_ids = np.array([2**63 + 10, 2**63 + 20], dtype="uint64")
    people = pd.DataFrame(
        {
            "person_id": person_ids,
            "person_household_id": household_ids[[0, 0, 1]],
            "person_tax_unit_id": np.array([100, 101, 200], dtype="int64"),
            "age": np.array([40, 39, 70], dtype="int16"),
            "relationship": pd.Series([1, 2, pd.NA], dtype="Int64"),
            "reported": pd.Series([True, pd.NA, False], dtype="boolean"),
            "source_person_id": person_ids + np.uint64(100),
        }
    )
    homes = pd.DataFrame(
        {
            "household_id": household_ids,
            "source_household_id": household_ids + np.uint64(100),
            "clone": np.array([0, 1], dtype="int8"),
            "origin": pd.Series(["invented-a", "invented-b"], dtype="string"),
            "block": pd.Series(
                ["001000000000001", "002000000000002"], dtype="string"
            ),
        }
    )
    tax = pd.DataFrame(
        {"tax_unit_id": np.array([100, 101, 200], dtype="int64")}
    )
    manifest = {
        "protocol": "populace-dynamics.baseline-checkpoint-intake.v1",
        "interpretation": "baseline_frame",
        "producer_revision": "1" * 40,
        "period": "2026-01-01",
        "household_scope": "complete_households",
        "frame_metadata": {
            "fixture": "invented only",
            "origin_binding": "invented-parent",
        },
    }
    frame = Frame(
        {"person": people, "household": homes, "tax_unit": tax},
        EntitySchema(group_entities=("household", "tax_unit")),
        {
            "household": Weights([0, 7], WeightKind.CALIBRATED),
            "tax_unit": Weights([1, 2, 3], WeightKind.DESIGN),
        },
        pd.Series(["a", "a", "b"], dtype="string"),
        metadata=manifest["frame_metadata"],
    )
    args = {
        "expected_manifest": copy.deepcopy(manifest),
        "membership": people[["person_id", "person_household_id"]].copy(),
        "household_ids": homes.household_id.copy(),
        "relationships": people[
            ["person_id", "person_household_id", "person_tax_unit_id"]
        ].copy(),
        "weight_kinds": {
            "household": WeightKind.CALIBRATED,
            "tax_unit": WeightKind.DESIGN,
        },
        "required_inputs": {
            "person": {
                "age": InputColumn("int16", nullable=False),
                "relationship": InputColumn("Int64", nullable=True),
                "reported": InputColumn("boolean", nullable=True),
            },
            "household": {"block": InputColumn("string", nullable=False)},
            "tax_unit": {"tax_unit_id": InputColumn("int64", nullable=False)},
        },
        "clone_provenance": {
            "person": people[["person_id", "source_person_id"]].copy(),
            "household": homes[
                ["household_id", "source_household_id", "clone", "origin"]
            ].copy(),
        },
    }
    path = tmp_path / "invented-export.h5"
    frame_checkpoint.write_frame_checkpoint(path, frame, metadata=manifest)
    args["checkpoint_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return frame, manifest, path, args


def rewrite(frame, manifest, path, args):
    frame_checkpoint.write_frame_checkpoint(path, frame, metadata=manifest)
    args["checkpoint_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()


def test_actual_export_preserves_context(exported):
    frame, _, path, args = exported
    loaded = read_baseline_checkpoint(path, **args)
    for entity in frame.entities:
        pd.testing.assert_frame_equal(
            loaded.table(entity), frame.table(entity)
        )
    pd.testing.assert_series_equal(loaded.strata, frame.strata)
    assert loaded.metadata == frame.metadata
    assert loaded.mass_log == frame.mass_log
    assert loaded.n("person") == 3
    for entity in frame.weighted_entities:
        assert (
            loaded.weights_for(entity).kind is frame.weights_for(entity).kind
        )
        np.testing.assert_array_equal(
            loaded.weights_for(entity).values, frame.weights_for(entity).values
        )


@pytest.mark.parametrize(
    "field",
    ["producer_revision", "period", "household_scope", "frame_metadata"],
)
def test_mismatched_embedded_manifest_refuses(exported, field):
    frame, manifest, path, args = exported
    manifest[field] = (
        {"changed": True} if field == "frame_metadata" else "different"
    )
    rewrite(frame, manifest, path, args)
    with pytest.raises(ContextContractError, match="manifest differs"):
        read_baseline_checkpoint(path, **args)


def test_manifest_equality_preserves_json_types(exported):
    frame, manifest, path, args = exported
    args["expected_manifest"]["extra"] = True
    manifest["extra"] = 1
    rewrite(frame, manifest, path, args)
    with pytest.raises(ContextContractError, match="manifest differs"):
        read_baseline_checkpoint(path, **args)


@pytest.mark.parametrize("change", ["missing", "dtype", "null"])
def test_required_inputs_refuse_before_returning_frame(exported, change):
    frame, manifest, path, args = exported
    if change == "missing":
        frame.person.drop(columns="age", inplace=True)
    elif change == "dtype":
        frame.person["age"] = frame.person.age.astype("float64")
    else:
        frame.table("household").loc[0, "block"] = pd.NA
    rewrite(frame, manifest, path, args)
    with pytest.raises(ContextContractError, match="Required input"):
        read_baseline_checkpoint(path, **args)


@pytest.mark.parametrize(
    "change",
    [
        "person_origin",
        "household_origin",
        "clone",
        "partial_household",
        "tax_membership",
        "weight_kind",
    ],
)
def test_identity_scope_and_kind_changes_refuse(exported, change):
    frame, manifest, path, args = exported
    if change == "person_origin":
        frame.person.loc[0, "source_person_id"] += np.uint64(1)
    elif change == "household_origin":
        frame.table("household").loc[0, "origin"] = "invented-c"
    elif change == "clone":
        frame.table("household").loc[0, "clone"] = 2
    elif change == "partial_household":
        frame = frame.select(np.array([False, True, True]))
    elif change == "tax_membership":
        # Keep every group referenced so the intake, not Frame validation,
        # detects the changed relationships.
        frame.person["person_tax_unit_id"] = np.array(
            [101, 100, 200], dtype="int64"
        )
    else:
        args["weight_kinds"]["household"] = WeightKind.DESIGN
    rewrite(frame, manifest, path, args)
    match = (
        "Group relationships differ" if change == "tax_membership" else None
    )
    with pytest.raises(ContextContractError, match=match):
        read_baseline_checkpoint(path, **args)


@pytest.mark.parametrize(
    "change",
    [
        "digest",
        "continuing",
        "empty_requirements",
        "missing_manifest",
        "missing_provenance",
    ],
)
def test_invalid_contract_refuses_before_decoder(
    exported, monkeypatch, change
):
    _, _, path, args = exported

    def forbidden(*a, **kw):
        pytest.fail("Decoder ran before intake preflight")

    monkeypatch.setattr(frame_checkpoint, "load_frame_checkpoint", forbidden)
    if change == "digest":
        args["checkpoint_sha256"] = "f" * 64
    elif change == "continuing":
        args["expected_manifest"]["interpretation"] = "continuing_population"
    elif change == "empty_requirements":
        args["required_inputs"] = {}
    elif change == "missing_manifest":
        del args["expected_manifest"]["producer_revision"]
    else:
        args["clone_provenance"] = {}
    with pytest.raises(ContextContractError):
        read_baseline_checkpoint(path, **args)


def test_file_changed_during_loader_refuses(exported, monkeypatch):
    _, _, path, args = exported
    original = frame_checkpoint.load_frame_checkpoint

    def changed(*a, **kw):
        loaded = original(*a, **kw)
        with path.open("ab") as out:
            out.write(b"changed")
        return loaded

    monkeypatch.setattr(frame_checkpoint, "load_frame_checkpoint", changed)
    with pytest.raises(ContextContractError, match="changed while reading"):
        read_baseline_checkpoint(path, **args)
