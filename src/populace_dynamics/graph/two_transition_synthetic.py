"""The invented second-period source the chained graph reads.

The one-shot graph's fixtures live in :mod:`populace_dynamics.graph.
synthetic`; this is the same kind of thing for the second transition, in
its own module so that editing a fixture cannot move a kernel's
implementation hash. Every value here is hand-specified. Nothing is
observed, forecast, or drawn from any survey or administrative file.

The path deliberately holds a known value, a known zero, an explicit
unknown and, under a signed domain, a negative period, so the three
states stay distinguishable after the second carry. It supplies a row
for every person the population ever held, including people who are
already closed and people who die in the second transition. Those rows
are withheld and counted by the earnings node rather than appended;
supplying them is what lets the all-dead case have a source at all,
since an earnings path needs at least one row.
"""

from pathlib import Path

from .earnings import EarningsPathArtifact


def synthetic_second_scenario(
    *,
    price_basis="nominal",
    sign_domain="nonnegative",
    unit="XTS",
    calendar="calendar_year",
    boundary_year=2014,
    count=20,
    people=None,
):
    """Build the supplied values for the period after the transition.

    Args:
        price_basis: ``"nominal"`` or ``"fixed@<period>"``; must equal
            what the run declares.
        sign_domain: ``"nonnegative"`` or ``"signed"``.
        unit: The measure token, carried verbatim.
        calendar: The period calendar the integer periods count in.
        boundary_year: The fixed fit boundary. The supplied period is two
            years later, which is the period the second expansion opens.
        count: How many of the synthetic people to supply, from 100 up.
        people: An explicit person list, overriding ``count``.
    """
    advanced = boundary_year + 2
    identifiers = (
        list(people) if people is not None else [100 + i for i in range(count)]
    )
    rows = []
    for person in identifiers:
        index = person - 100
        if index == 3:
            rows.append((person, advanced, "scenario", "unknown", None))
        elif index == 5:
            rows.append((person, advanced, "scenario", "known", 0.0))
        elif index == 9 and sign_domain == "signed":
            rows.append((person, advanced, "scenario", "known", -1500.0))
        else:
            rows.append(
                (
                    person,
                    advanced,
                    "scenario",
                    "known",
                    34000.0 + 500 * index,
                )
            )
    return EarningsPathArtifact(
        source="synthetic_engineering",
        unit=unit,
        price_basis=price_basis,
        calendar=calendar,
        sign_domain=sign_domain,
        rows=tuple(rows),
    )


def write_second_scenario(directory, *, name="scenario2", **kwargs):
    """Write one second-period source; an existing file is preserved."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    if not path.exists():
        path.write_bytes(synthetic_second_scenario(**kwargs).to_bytes())
    return path
