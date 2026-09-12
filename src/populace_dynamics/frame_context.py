"""Optional, source-only household context boundary for Microcosm Frame v2.

This module never advances a population, maps weights, or changes an existing
Dynamics reader. Callers must supply independently established artifact and
complete-household roster bindings. Passing these checks is not data admission.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from microcosm.frame import Frame, WeightKind
    from microcosm.graph import Population


class ContextContractError(ValueError):
    """The requested context does not match its explicit boundary contract."""


def _runtime():
    try:
        store = importlib.import_module("microcosm.graph.store")
        population = importlib.import_module("microcosm.graph.population")
        frame = importlib.import_module("microcosm.frame")
    except (ImportError, SyntaxError) as error:
        raise ImportError(
            "Household context requires reviewed Microcosm Frame v2 packages "
            "together on Python >=3.13. Legacy Dynamics is unchanged."
        ) from error
    # Package versions alone do not distinguish the old and new codecs.
    if getattr(store, "_FRAME_FORMAT", None) != "microcosm-graph-frame-v2":
        raise ImportError(
            "Household context requires the shared Frame v2 codec."
        )
    return store, population, frame


def _validate_households(frame, *, membership, household_ids, weight_kinds):
    _, _, runtime = _runtime()
    if not isinstance(frame, runtime.Frame):
        raise ContextContractError("Expected a Microcosm Frame.")
    frame.revalidate()
    if (
        frame.schema.person_entity != "person"
        or "household" not in frame.entities
    ):
        raise ContextContractError("Expected person and household entities.")
    if not isinstance(membership, pd.DataFrame):
        raise ContextContractError(
            "Expected an explicit complete membership roster."
        )
    if not isinstance(household_ids, pd.Series):
        raise ContextContractError("Expected an explicit household roster.")
    columns = ["person_id", "person_household_id"]
    actual = frame.table("person")[columns]
    try:
        pd.testing.assert_frame_equal(actual, membership, check_exact=True)
    except AssertionError as error:
        raise ContextContractError(
            "Complete membership roster differs."
        ) from error
    try:
        pd.testing.assert_series_equal(
            frame.table("household")["household_id"],
            household_ids,
            check_exact=True,
        )
    except AssertionError as error:
        raise ContextContractError(
            "Complete household roster differs."
        ) from error
    # Preserve every explicit vector. No implicit person weights or backward
    # kind conversion is allowed, including for zero-weight households.
    actual_kinds = {
        entity: frame.weights_for(entity).kind
        for entity in frame.weighted_entities
    }
    if (
        not isinstance(weight_kinds, Mapping)
        or "household" not in actual_kinds
        or not all(
            isinstance(kind, runtime.WeightKind)
            for kind in weight_kinds.values()
        )
        or dict(weight_kinds) != actual_kinds
    ):
        raise ContextContractError(
            "Explicit weight kinds differ from the contract."
        )


def read_baseline_frame(
    path: str | Path,
    *,
    metadata_sha256: str,
    expected_key: str,
    expected_node_key: str,
    membership: pd.DataFrame,
    household_ids: pd.Series,
    weight_kinds: Mapping[str, WeightKind],
    interpretation: str = "baseline_frame",
) -> Frame:
    """Read a pinned baseline through the real shared Frame v2 decoder.

    ``metadata_sha256`` binds meta.json, including its complete payload hash
    table; a store key alone is insufficient publisher authority. This reader
    retains tables, links, metadata, strata, mass log and typed weights. It
    does not manufacture a Population version or interpret period metadata.
    The caller must establish the producer, period and complete roster before
    calling. A continuing Population file requires a separate envelope API.
    """
    if interpretation != "baseline_frame":
        raise ContextContractError(
            "A continuing Population envelope is required; a Frame is insufficient."
        )
    store, _, _ = _runtime()
    path = Path(path)
    for value in (metadata_sha256, expected_key, expected_node_key):
        if (
            not isinstance(value, str)
            or re.fullmatch("[0-9a-f]{64}", value) is None
        ):
            raise ContextContractError(
                "Artifact identity must be a SHA-256 key."
            )
    metadata_path = path / "meta.json"
    if path.is_symlink() or metadata_path.is_symlink():
        raise ContextContractError(
            "Artifact identity cannot use symlinked objects."
        )
    raw = metadata_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != metadata_sha256:
        raise ContextContractError("Artifact metadata identity differs.")
    metadata = json.loads(raw)
    if (
        not isinstance(metadata, dict)
        or metadata.get("key") != expected_key
        or path.name != expected_key
        or metadata.get("node_key") != expected_node_key
    ):
        raise ContextContractError(
            "Artifact key or producer-node identity differs."
        )
    # The shared decoder owns format, payload inventory, dtype and link checks.
    frame = store.ContentStore.load_frame_path(path)
    if metadata_path.read_bytes() != raw:
        raise ContextContractError(
            "Artifact metadata identity changed while reading."
        )
    _validate_households(
        frame,
        membership=membership,
        household_ids=household_ids,
        weight_kinds=weight_kinds,
    )
    return frame


def retain_population(
    population: Population,
    *,
    membership: pd.DataFrame,
    household_ids: pd.Series,
    weight_kinds: Mapping[str, WeightKind],
) -> Population:
    """Check and retain an existing in-memory Population without reconstruction.

    Its exact object carries version, owners, mass ledger, original design
    anchors and Frame metadata. External graph receipts remain caller-owned;
    this adapter neither serializes them nor claims a complete export format.
    """
    _, runtime, _ = _runtime()
    if not isinstance(population, runtime.Population):
        raise ContextContractError(
            "Expected an existing Population, not a bare Frame."
        )
    _validate_households(
        population.frame,
        membership=membership,
        household_ids=household_ids,
        weight_kinds=weight_kinds,
    )
    # Recheck structural invariants in case a caller mutated exposed tables.
    # Discard this validation copy: the returned object and its history stay intact.
    runtime.Population(
        population.frame,
        population.version,
        population.owners,
        population.weight_kind,
        population.mass_ledger,
        population.design_weights,
    )
    return population
