"""Optional graph ageing for an explicitly unchanged household membership.

These kernels advance age/year only. The host must separately model events,
economic inputs and benefit timing. Source metadata remains baseline provenance.
No input is admitted here and no continuing Population is reconstructed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from microcosm.graph.decl import Node, Owned, Slice, StructuralDelta
from microcosm.graph.kernel import (
    Capabilities,
    Determinism,
    KernelBase,
    KernelResult,
    source_hash,
)
from microcosm.graph.population import token_for_dtype

from populace_dynamics.engine.loop import PeriodContext
from populace_dynamics.engine.steps import advance_age


def baseline_graph_outputs(frame) -> tuple[Owned, ...]:
    """Declare existing data cells using the shared runtime's exact dtype tokens.

    Unsupported data dtypes refuse before CREATE; nothing is cast, dropped or
    replaced. Entity IDs and group memberships are structural columns carried
    by the shared runtime, not ordinary owned outputs. Separate link tables
    need a separately reviewed graph declaration and refuse in this slice.
    """
    frame.revalidate()
    if (
        frame.schema.person_entity != "person"
        or "household" not in frame.entities
    ):
        raise ValueError("Expected person/household context")
    if frame.links:
        raise ValueError("Separate link-table graph intake is not supported")
    # Structural graph versions record person-level stratum mass. Let the
    # shared Frame resolve declared weights; never invent a person vector or
    # choose silently between multiple weighted groups.
    try:
        frame.stratum_mass()
    except ValueError as error:
        raise ValueError(
            "Graph mass accounting needs unambiguous declared weights"
        ) from error
    outputs = []
    for entity in frame.entities:
        structural = {frame.schema.entity_id_column(entity)}
        if entity == "person":
            structural.update(
                frame.schema.membership_column(group)
                for group in frame.schema.group_entities
            )
        for column in frame.table(entity).columns:
            if column in structural:
                continue
            dtype = frame.table(entity)[column].dtype
            try:
                token = token_for_dtype(dtype)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Graph cannot own {entity}.{column} with dtype {dtype}; no coercion allowed"
                ) from error
            outputs.append(Owned(entity, column, token))
    return tuple(outputs)


def _period(params):
    before, after = params.get("from_year"), params.get("to_year")
    if (
        type(before) is not int
        or type(after) is not int
        or not 1 <= before < 9999
        or after != before + 1
        or params.get("membership_policy") != "unchanged"
    ):
        raise ValueError(
            "Require consecutive calendar years and explicit unchanged membership"
        )
    return before, after


def _people(context):
    before, after = _period(context.params)
    people = context.tables["person"]
    if (
        "year" not in people
        or people.year.dtype != np.dtype("int64")
        or not (people.year == before).all()
    ):
        raise ValueError(
            "Every person's int64 year must match the source year"
        )
    return people, after


class CarryContextKernel(KernelBase):
    """Open a new graph version carrying every member and every context column."""

    ref = "dynamics.context-carry@1"
    capabilities = Capabilities(
        Determinism.DETERMINISTIC,
        structural=StructuralDelta.FILTER,
        dependencies=("numpy", "pandas"),
    )

    def run(self, context):
        people, _ = _people(context)
        return KernelResult(
            keep=pd.Series(
                True,
                index=pd.Index(people.person_id, name="person_id"),
                dtype=bool,
            ),
            receipt={"scope": "unchanged_membership_ageing"},
        )


class AgeContextKernel(KernelBase):
    """Apply the existing age step, letting Microcosm patch only declared cells."""

    ref = "dynamics.context-age@1"
    capabilities = Capabilities(
        Determinism.DETERMINISTIC, dependencies=("numpy", "pandas")
    )

    def implementation_hash(self):
        return source_hash(
            type(self),
            advance_age,
            PeriodContext,
            dependencies=self.capabilities.dependencies,
        )

    def run(self, context):
        people, after = _people(context)
        if (
            "age" not in people
            or people.age.dtype != np.dtype("int64")
            or not people.age.between(0, np.iinfo(np.int64).max - 1).all()
        ):
            raise ValueError(
                "Age must be a nonnegative int64 that can advance without overflow"
            )
        # This component reads no economic fields and cannot claim to uprate them.
        aged = advance_age(
            people[["age", "year"]],
            PeriodContext(
                period_index=0, year=after, draw_index=0, metadata={}
            ),
            context.rng,
        )
        ids = pd.Index(people.person_id, name="person_id")
        return KernelResult(
            columns={
                ("person", column): pd.Series(
                    aged[column].to_numpy(copy=True), index=ids, dtype="int64"
                )
                for column in ("age", "year")
            },
            receipt={
                "scope": "age_and_year_only",
                "from_year": after - 1,
                "to_year": after,
            },
        )


def annual_ageing_nodes(
    *,
    base: str,
    from_year: int,
    to_year: int,
    prefix: str,
    membership_policy: str,
) -> tuple[Node, Node]:
    """Build an explicit carry version and one age/year rewrite within it.

    Unchanged membership is a host-supplied scenario assumption, never a
    mortality estimate. Two consecutive pairs can use the previous carry id
    as base; graph ownership dependencies order each age rewrite first.
    """
    params = {
        "from_year": from_year,
        "to_year": to_year,
        "membership_policy": membership_policy,
    }
    _period(params)
    carry = Node(
        f"{prefix}.carry",
        CarryContextKernel.ref,
        base=base,
        structural=StructuralDelta.FILTER,
        inputs=(Slice("person", ("year",)),),
        params=params,
        mass="conserve",
    )
    age = Node(
        f"{prefix}.age",
        AgeContextKernel.ref,
        population=carry.id,
        inputs=(Slice("person", ("age", "year")),),
        outputs=(
            Owned("person", "age", "int64", rewrite=True),
            Owned("person", "year", "int64", rewrite=True),
        ),
        params=params,
    )
    return carry, age
