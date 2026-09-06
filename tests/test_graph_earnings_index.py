"""The earnings path's index answers exactly what the old scans did.

Every case here is invented. Nothing in this module fits, projects, or
imputes earnings, and no value comes from a survey or an administrative
record.

Two things are checked. First, parity: an independent reference copy of
the pre-index ``history``, ``at``, ``people``, ``closed_people``,
``prefix_total`` and ``known_total`` is run beside the artifact's own on
signed, known-zero, unknown, absent and cancelling paths, and the two
must agree object-for-object -- including the exact floating-point sum,
which a cumulative running total would not reproduce. Second, cost: a
lookup must not touch rows belonging to other people, so the same lookup
on a 100-person and a 1000-person path must touch the same rows.
"""

import math

import pytest

from populace_dynamics.graph.earnings import EarningsPathArtifact

FIXED = dict(
    source="invented",
    unit="XTS",
    price_basis="fixed@2000",
    calendar="calendar_year",
)


# --- The pre-index implementation, kept verbatim as the reference. ------


def reference_history(artifact, person_id):
    return tuple(
        (period, origin, status, value)
        for person, period, origin, status, value in sorted(
            artifact.rows, key=lambda row: (row[0], row[1])
        )
        if person == person_id
    )


def reference_at(artifact, person_id, period):
    for person, own, origin, status, value in artifact.rows:
        if person == person_id and own == period:
            return (origin, status, value)
    return None


def reference_people(artifact):
    return tuple(sorted({person for person, *_ in artifact.rows}))


def reference_closed_people(artifact):
    return frozenset(person for person, _ in artifact.closed)


def reference_prefix_total(artifact, person_id, through_period):
    rows = [
        row
        for row in reference_history(artifact, person_id)
        if row[0] <= through_period
    ]
    if not rows:
        return None
    if any(status == "unknown" for _, _, status, _ in rows):
        return None
    return float(sum(value for _, _, _, value in rows))


def reference_known_total(artifact, person_id):
    rows = reference_history(artifact, person_id)
    if not rows:
        return None
    return reference_prefix_total(artifact, person_id, rows[-1][0])


# --- Invented paths. ---------------------------------------------------


def signed_path():
    """Losses, gains, and a person whose whole path is negative."""
    return EarningsPathArtifact(
        **{**FIXED, "sign_domain": "signed"},
        rows=(
            (10, 2001, "observed", "known", 4000.0),
            (10, 2002, "observed", "known", -1500.0),
            (10, 2003, "observed", "known", 2500.0),
            (11, 2001, "observed", "known", -900.0),
            (11, 2002, "observed", "known", -100.0),
        ),
    )


def zero_path():
    """Known zeros, which are values and not missingness."""
    return EarningsPathArtifact(
        **{**FIXED, "sign_domain": "nonnegative"},
        rows=(
            (20, 2001, "observed", "known", 0.0),
            (20, 2002, "observed", "known", 0),
            (20, 2003, "observed", "known", 1200.0),
            (21, 2001, "observed", "known", 0.0),
        ),
    )


def unknown_path():
    """Unknown periods, which poison a total rather than count as zero."""
    return EarningsPathArtifact(
        **{**FIXED, "sign_domain": "nonnegative"},
        rows=(
            (30, 2001, "observed", "known", 700.0),
            (30, 2002, "observed", "unknown", None),
            (30, 2003, "observed", "known", 800.0),
            (31, 2001, "observed", "unknown", None),
        ),
    )


def absent_path():
    """Gaps between periods, and people the path never mentions."""
    return EarningsPathArtifact(
        **{**FIXED, "sign_domain": "nonnegative"},
        rows=(
            (40, 2001, "observed", "known", 100.0),
            (40, 2005, "observed", "known", 200.0),
            (42, 2003, "observed", "known", 300.0),
        ),
        closed=((42, 2003),),
    )


def cancelling_path():
    """A prefix a running total would get wrong.

    ``1e16 + 1.0`` rounds back to ``1e16`` in binary floating point, so a
    cumulative total carried forward row by row loses the ``1.0`` and
    ends at ``0.0``. Python's ``sum`` compensates, and answers ``1.0``.
    The pre-index code called ``sum`` over the prefix rows; so does the
    indexed code, so both answer ``1.0``.
    """
    return EarningsPathArtifact(
        **{**FIXED, "sign_domain": "signed"},
        rows=(
            (50, 2001, "observed", "known", 1e16),
            (50, 2002, "observed", "known", 1.0),
            (50, 2003, "observed", "known", -1e16),
            (51, 2001, "observed", "known", 1.0),
            (51, 2002, "observed", "known", 1e16),
            (51, 2003, "observed", "known", -1e16),
        ),
    )


def unordered_path():
    """The same rows, handed over in no particular order."""
    return EarningsPathArtifact(
        **{**FIXED, "sign_domain": "signed"},
        rows=(
            (61, 2002, "observed", "known", -5.0),
            (60, 2003, "observed", "known", 3.0),
            (61, 2001, "observed", "unknown", None),
            (60, 2001, "observed", "known", 0.0),
            (60, 2002, "observed", "known", 7.0),
        ),
    )


PATHS = {
    "signed": signed_path,
    "zero": zero_path,
    "unknown": unknown_path,
    "absent": absent_path,
    "cancelling": cancelling_path,
    "unordered": unordered_path,
}

#: People and periods to probe, including ones no path mentions.
PROBE_PEOPLE = (10, 11, 20, 21, 30, 31, 40, 41, 42, 50, 51, 60, 61, 999)
PROBE_PERIODS = (1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006)


@pytest.mark.parametrize("name", sorted(PATHS))
def test_the_index_answers_what_the_old_scans_answered(name):
    artifact = PATHS[name]()
    assert artifact.people == reference_people(artifact)
    assert artifact.closed_people == reference_closed_people(artifact)
    for person in PROBE_PEOPLE:
        assert artifact.history(person) == reference_history(
            artifact, person
        )
        assert artifact.known_total(person) == reference_known_total(
            artifact, person
        )
        for period in PROBE_PERIODS:
            assert artifact.at(person, period) == reference_at(
                artifact, person, period
            )
            assert artifact.prefix_total(
                person, period
            ) == reference_prefix_total(artifact, person, period)


def naive_running_total(artifact, person_id, through_period):
    """What a cumulative column carried row by row would have said."""
    total = 0.0
    seen = False
    for period, _, status, value in artifact.history(person_id):
        if period > through_period:
            break
        if status == "unknown":
            return None
        total += value
        seen = True
    return total if seen else None


def test_a_cancelling_prefix_keeps_the_sums_association():
    artifact = cancelling_path()
    for person in (50, 51):
        for period in (2001, 2002, 2003):
            assert artifact.prefix_total(
                person, period
            ) == reference_prefix_total(artifact, person, period)
        assert artifact.known_total(person) == reference_known_total(
            artifact, person
        )
    # The point of the case: a running total loses the 1.0 that the
    # prefix sum keeps, so the two disagree and only one of them is what
    # the pre-index code answered.
    assert artifact.prefix_total(50, 2003) == 1.0
    assert naive_running_total(artifact, 50, 2003) == 0.0
    assert artifact.prefix_total(51, 2003) == 1.0
    assert naive_running_total(artifact, 51, 2003) == 0.0
    assert artifact.prefix_total(50, 2002) == 1e16


def test_an_unknown_period_still_withholds_the_total():
    artifact = unknown_path()
    assert artifact.prefix_total(30, 2001) == 700.0
    assert artifact.prefix_total(30, 2002) is None
    assert artifact.prefix_total(30, 2003) is None
    assert artifact.known_total(31) is None


def test_a_known_zero_is_a_value_and_an_absent_period_is_not():
    artifact = zero_path()
    assert artifact.at(20, 2001) == ("observed", "known", 0.0)
    assert artifact.at(20, 2004) is None
    assert artifact.prefix_total(20, 2002) == 0.0
    assert artifact.prefix_total(21, 2002) == 0.0
    assert artifact.prefix_total(21, 2000) is None


def test_a_carry_indexes_the_rows_it_added():
    artifact = zero_path()
    carried = artifact.carried(
        ((20, 2004, "scenario", "known", 5.0),),
        closed=((21, 2001),),
        through_period=2004,
    )
    assert carried.at(20, 2004) == ("scenario", "known", 5.0)
    assert carried.history(20) == reference_history(carried, 20)
    assert carried.closed_people == frozenset({21})
    assert carried.prefix_total(20, 2004) == reference_prefix_total(
        carried, 20, 2004
    )
    # The original is untouched by the carry.
    assert artifact.at(20, 2004) is None


def test_editing_a_list_handed_to_the_constructor_cannot_stale_the_index():
    rows = [
        [70, 2001, "observed", "known", 10.0],
        [70, 2002, "observed", "known", 20.0],
    ]
    closed = [[70, 2002]]
    artifact = EarningsPathArtifact(
        **{**FIXED, "sign_domain": "signed"}, rows=rows, closed=closed
    )
    rows[0][4] = 999.0
    rows.append([71, 2001, "observed", "known", 1.0])
    closed.append([71, 2001])
    assert artifact.rows == (
        (70, 2001, "observed", "known", 10.0),
        (70, 2002, "observed", "known", 20.0),
    )
    assert artifact.closed == ((70, 2002),)
    assert artifact.people == (70,)
    assert artifact.at(70, 2001) == ("observed", "known", 10.0)
    assert artifact.at(71, 2001) is None
    assert artifact.prefix_total(70, 2002) == 30.0
    assert artifact.history(70) == reference_history(artifact, 70)
    assert artifact.closed_people == frozenset({70})


def test_a_carry_copies_the_rows_it_was_handed():
    added = [[80, 2002, "scenario", "known", 4.0]]
    artifact = EarningsPathArtifact(
        **{**FIXED, "sign_domain": "signed"},
        rows=((80, 2001, "observed", "known", 1.0),),
    )
    carried = artifact.carried(added, closed=(), through_period=2002)
    added[0][4] = 999.0
    assert carried.at(80, 2002) == ("scenario", "known", 4.0)
    assert carried.prefix_total(80, 2002) == 5.0


def test_serialized_bytes_do_not_depend_on_how_the_rows_arrived():
    tuples = EarningsPathArtifact(
        **{**FIXED, "sign_domain": "signed"},
        rows=(
            (60, 2002, "observed", "known", 7.0),
            (60, 2001, "observed", "known", 0.0),
        ),
        closed=((60, 2002),),
    )
    lists = EarningsPathArtifact(
        **{**FIXED, "sign_domain": "signed"},
        rows=[
            [60, 2001, "observed", "known", 0.0],
            [60, 2002, "observed", "known", 7.0],
        ],
        closed=[[60, 2002]],
    )
    assert tuples.to_bytes() == lists.to_bytes()
    # A path built from lists is equal to, and hashes with, one built
    # from tuples; row order is preserved as given, so the round trip
    # matches the ascending-order one.
    assert EarningsPathArtifact.from_bytes(tuples.to_bytes()) == lists
    assert hash(lists) == hash(EarningsPathArtifact.from_bytes(
        tuples.to_bytes()
    ))


# --- Cost. -------------------------------------------------------------


class CountingRows(tuple):
    """A person's rows that records every row an iteration consumes."""

    def __new__(cls, rows, counter):
        self = super().__new__(cls, rows)
        self.counter = counter
        return self

    def __iter__(self):
        for row in tuple.__iter__(self):
            self.counter["rows"] += 1
            yield row


class CountingCells(dict):
    """A coordinate index that records every lookup made against it."""

    def __init__(self, cells, counter):
        super().__init__(cells)
        self.counter = counter

    def get(self, key, default=None):
        self.counter["cells"] += 1
        return super().get(key, default)


def instrument(artifact):
    """Attach counters to one artifact's index and return the counter."""
    counter = {"rows": 0, "cells": 0, "people": 0}

    class CountingByPerson(dict):
        def get(self, key, default=()):
            counter["people"] += 1
            return super().get(key, default)

    object.__setattr__(
        artifact,
        "_by_person",
        CountingByPerson(
            {
                person: CountingRows(rows, counter)
                for person, rows in artifact._by_person.items()
            }
        ),
    )
    object.__setattr__(
        artifact, "_cells", CountingCells(artifact._cells, counter)
    )
    return counter


def population_path(people, periods, first_person=100, first_period=1980):
    """An invented path: ``people`` people, each with ``periods`` rows."""
    rows = []
    for index in range(people):
        person = first_person + index
        for offset in range(periods):
            period = first_period + offset
            if offset == periods // 2:
                rows.append((person, period, "observed", "unknown", None))
            else:
                rows.append(
                    (
                        person,
                        period,
                        "observed",
                        "known",
                        float(1000 + 10 * index + offset),
                    )
                )
    return EarningsPathArtifact(
        **{**FIXED, "sign_domain": "nonnegative"}, rows=tuple(rows)
    )


PEOPLE = 1000
PERIODS = 35


def test_a_lookup_does_not_grow_with_the_population():
    small = population_path(100, PERIODS)
    large = population_path(PEOPLE, PERIODS)
    assert len(large.rows) == PEOPLE * PERIODS
    assert len(small.rows) == 100 * PERIODS

    counts = []
    for artifact in (small, large):
        counter = instrument(artifact)
        artifact.at(150, 1990)
        assert counter == {"rows": 0, "cells": 1, "people": 0}
        counter.update({"rows": 0, "cells": 0, "people": 0})
        tuple(artifact.history(150))
        assert counter["people"] == 1
        assert counter["rows"] == PERIODS
        counter.update({"rows": 0, "cells": 0, "people": 0})
        artifact.prefix_total(150, 1990)
        counts.append(dict(counter))
    # Same rows touched at ten times the population.
    assert counts[0] == counts[1]
    # And never more rows than that one person holds.
    assert counts[0]["rows"] <= 2 * PERIODS


def test_a_whole_population_pass_touches_each_persons_rows_only():
    artifact = population_path(PEOPLE, PERIODS)
    counter = instrument(artifact)
    last = 1980 + PERIODS - 1
    for person in artifact.people:
        artifact.at(person, last)
        artifact.prefix_total(person, last)
    # One coordinate lookup per at(), one per-person lookup per
    # prefix_total, and that person's own rows -- not the population's.
    assert counter["cells"] == PEOPLE
    assert counter["people"] == PEOPLE
    assert counter["rows"] == PEOPLE * PERIODS == len(artifact.rows)
    # The pre-index code sorted and walked all 35,000 rows once per
    # prefix_total, so the same pass visited 35,000,000 rows. Each row
    # here is visited once, by the one person who holds it.
    assert counter["rows"] * PEOPLE == len(artifact.rows) * PEOPLE
    assert counter["rows"] < len(artifact.rows) * PEOPLE


def test_the_index_is_built_once_and_not_rebuilt_per_lookup():
    artifact = population_path(PEOPLE, PERIODS)
    first = artifact.history(150)
    assert artifact.history(150) is first
    assert artifact.people is artifact.people
    assert artifact.closed_people is artifact.closed_people


def test_a_population_pass_agrees_with_the_reference_on_a_sample():
    artifact = population_path(PEOPLE, PERIODS)
    last = 1980 + PERIODS - 1
    for person in (100, 500, 1099, 2000):
        assert artifact.history(person) == reference_history(
            artifact, person
        )
        assert artifact.at(person, last) == reference_at(
            artifact, person, last
        )
        assert artifact.prefix_total(
            person, last
        ) == reference_prefix_total(artifact, person, last)
        # The unknown period in the middle withholds any total past it.
        assert artifact.prefix_total(person, last) is None
    assert artifact.prefix_total(100, 1980) == 1000.0
    assert math.isclose(artifact.prefix_total(100, 1981), 2001.0)
