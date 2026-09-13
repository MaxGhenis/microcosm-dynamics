"""Optional baseline intake using Microcosm's real HDF checkpoint loader.

This is a consumer integrity contract, not a release issuer. The host must
independently admit the producer, period, scope, file and provenance rosters
and keep the trusted local checkpoint stable during intake. No dynamics run
or continuing Population reconstruction occurs here.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from populace_dynamics.frame_context import (
    ContextContractError,
    _validate_households,
)

if TYPE_CHECKING:
    from microcosm.frame import Frame, WeightKind

PROTOCOL = "populace-dynamics.baseline-checkpoint-intake.v1"


@dataclass(frozen=True)
class InputColumn:
    """Logical pandas dtype name and whether an input may contain missing cells.

    Uses str(series.dtype); string storage backends are not distinguished.
    """

    dtype: str
    nullable: bool


def _manifest_json(value):
    try:
        return json.dumps(value, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ContextContractError("Manifest must be finite JSON.") from error


def _preflight(manifest, required_inputs, clone_provenance):
    if (
        not isinstance(manifest, dict)
        or manifest.get("protocol") != PROTOCOL
        or manifest.get("interpretation") != "baseline_frame"
        or manifest.get("household_scope") != "complete_households"
        or not isinstance(manifest.get("frame_metadata"), dict)
        or not isinstance(manifest.get("producer_revision"), str)
        or re.fullmatch("[0-9a-f]{40}", manifest["producer_revision"]) is None
    ):
        raise ContextContractError("Incomplete baseline intake manifest.")
    period = manifest.get("period")
    try:
        if (
            not isinstance(period, str)
            or date.fromisoformat(period).isoformat() != period
        ):
            raise ValueError("Expected YYYY-MM-DD")
    except ValueError as error:
        raise ContextContractError(
            "Manifest period must be YYYY-MM-DD."
        ) from error
    encoded = _manifest_json(manifest)
    if (
        not isinstance(required_inputs, Mapping)
        or not {"person", "household"} <= required_inputs.keys()
    ):
        raise ContextContractError(
            "Required inputs must name person and household."
        )
    for entity, columns in required_inputs.items():
        if (
            not isinstance(entity, str)
            or not isinstance(columns, Mapping)
            or not columns
        ):
            raise ContextContractError(
                "Required input declarations are incomplete."
            )
        for column, spec in columns.items():
            if (
                not isinstance(column, str)
                or not isinstance(spec, InputColumn)
                or not isinstance(spec.dtype, str)
                or not spec.dtype
                or type(spec.nullable) is not bool
            ):
                raise ContextContractError(
                    "Required input declarations are invalid."
                )
    if (
        not isinstance(clone_provenance, Mapping)
        or not {"person", "household"} <= clone_provenance.keys()
    ):
        raise ContextContractError(
            "Independent person and household clone provenance is required."
        )
    for entity, table in clone_provenance.items():
        if (
            not isinstance(entity, str)
            or not isinstance(table, pd.DataFrame)
            or table.empty
            or table.columns.has_duplicates
            or len(table.columns) < 2
            or f"{entity}_id" not in table
        ):
            raise ContextContractError(
                "Clone provenance must bind IDs and origin columns."
            )
    return encoded


def _file_digest(path):
    if path.is_symlink() or not path.is_file():
        raise ContextContractError("Checkpoint must be a regular local file.")
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_baseline_checkpoint(
    path: str | Path,
    *,
    checkpoint_sha256: str,
    expected_manifest: dict[str, object],
    membership: pd.DataFrame,
    household_ids: pd.Series,
    relationships: pd.DataFrame,
    weight_kinds: Mapping[str, WeightKind],
    required_inputs: Mapping[str, Mapping[str, InputColumn]],
    clone_provenance: Mapping[str, pd.DataFrame],
) -> Frame:
    """Verify a caller-bound baseline file before returning its complete Frame.

    The caller supplies an independently established manifest, full household
    rosters and person-to-group relationships, every explicit weight kind, required column dtype/nullability,
    and ID-aligned clone-origin columns. The manifest is the shared writer's
    external metadata, including separately bound ``frame_metadata``. Its
    producer revision and boundary date are declarations, not authentication.
    A supplied-parent comparison receipt alone cannot authorize this call.

    The shared loader alone decodes tables, relationships, masks and weights.
    No columns, members, zero weights or weight kinds are changed. Unsupported
    or incomplete inputs fail before the Frame reaches downstream dynamics.
    """
    encoded = _preflight(expected_manifest, required_inputs, clone_provenance)
    if not isinstance(relationships, pd.DataFrame) or relationships.empty:
        raise ContextContractError(
            "Independent group relationships are required."
        )
    # Snapshot JSON metadata before I/O, including the separately restored Frame metadata.
    manifest = json.loads(encoded)
    if (
        not isinstance(checkpoint_sha256, str)
        or re.fullmatch("[0-9a-f]{64}", checkpoint_sha256) is None
    ):
        raise ContextContractError("Checkpoint identity must be SHA-256.")
    path = Path(path)
    if _file_digest(path) != checkpoint_sha256:
        raise ContextContractError("Checkpoint identity differs.")
    codec = importlib.import_module("microcosm.build.frame_checkpoint")
    loaded = codec.load_frame_checkpoint(
        path, frame_metadata=manifest["frame_metadata"]
    )
    if _file_digest(path) != checkpoint_sha256:
        raise ContextContractError("Checkpoint changed while reading.")
    if _manifest_json(loaded.metadata) != encoded:
        raise ContextContractError("Embedded intake manifest differs.")
    frame = loaded.frame
    _validate_households(
        frame,
        membership=membership,
        household_ids=household_ids,
        weight_kinds=weight_kinds,
    )
    relationship_columns = [frame.schema.entity_id_column("person")] + [
        frame.schema.membership_column(entity)
        for entity in frame.schema.group_entities
    ]
    try:
        pd.testing.assert_frame_equal(
            frame.person[relationship_columns], relationships, check_exact=True
        )
    except AssertionError as error:
        raise ContextContractError("Group relationships differ.") from error
    for entity, columns in required_inputs.items():
        if entity not in frame.entities:
            raise ContextContractError(
                f"Required input entity is absent: {entity}"
            )
        table = frame.table(entity)
        for column, spec in columns.items():
            if column not in table or str(table[column].dtype) != spec.dtype:
                raise ContextContractError(
                    f"Required input missing or wrong dtype: {entity}.{column}"
                )
            if not spec.nullable and table[column].isna().any():
                raise ContextContractError(
                    f"Required input has missing values: {entity}.{column}"
                )
    for entity, expected in clone_provenance.items():
        if entity not in frame.entities or not set(expected.columns) <= set(
            frame.table(entity).columns
        ):
            raise ContextContractError(
                f"Clone provenance columns are absent: {entity}"
            )
        try:
            pd.testing.assert_frame_equal(
                frame.table(entity)[list(expected.columns)],
                expected,
                check_exact=True,
            )
        except AssertionError as error:
            raise ContextContractError(
                f"Clone provenance differs: {entity}"
            ) from error
    return frame
