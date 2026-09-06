"""A typed, strictly serialized earnings path for the optional graph.

This is retention, not estimation. The artifact carries values that some
other process already produced -- observed history, or an explicitly
labelled scenario value -- together with the units, calendar, and price
basis needed to read them. It fits no earnings model, applies no wage
base, and indexes nothing; a Social Security computation would need all
three and is deliberately absent.

Three states are distinguished and never collapsed: a *known* value
(including a known zero), an explicit *unknown* value, and a period that
is simply *absent* from the path. Nothing is filled in quietly.

The artifact is immutable, so it indexes its own rows by person and by
person-period once, when it is built, and answers every later lookup out
of that index. Reading one person's path or one coordinate therefore
costs nothing that grows with the size of the population.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .model import json_bytes, parse_json

_FORMAT = "populace-dynamics.earnings-path"
_SCHEMA_VERSION = 1

#: Where a row's value came from. ``observed`` is a value the path was
#: given for a period that already happened; ``scenario`` is a supplied
#: fixture value for a period the run is advancing into. A scenario value
#: is an input to this graph, never a forecast produced by it.
ORIGINS = ("observed", "scenario")

#: ``known`` carries a finite value, ``unknown`` carries none. A period
#: with no row at all is absent, which is a third, distinct state.
STATUSES = ("known", "unknown")

#: ``nonnegative`` refuses negative values; ``signed`` permits them (a
#: net self-employment loss, say). The path declares which it is.
SIGN_DOMAINS = ("nonnegative", "signed")

_NOMINAL = "nominal"
_FIXED = "fixed@"


def parse_price_basis(basis):
    """Split a price-basis token into its kind and reference period.

    ``"nominal"`` means each period's value is in that period's own
    prices, so values from different periods are not addable.
    ``"fixed@<period>"`` means every value is already expressed in one
    reference period's prices, which is the only case where a plain sum
    is well defined.
    """
    if not isinstance(basis, str) or not basis:
        raise ValueError("price basis must be a nonempty string")
    if basis == _NOMINAL:
        return (_NOMINAL, None)
    if basis.startswith(_FIXED):
        digits = basis[len(_FIXED) :]
        if not digits.isdigit():
            raise ValueError(f"invalid fixed price basis {basis!r}")
        return ("fixed", int(digits))
    raise ValueError(f"unsupported price basis {basis!r}")


def _token(value, label, allowed=None):
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a nonempty string")
    if allowed is not None and value not in allowed:
        raise ValueError(f"{label} must be one of {list(allowed)}")
    return value


def _period(value, label):
    if type(value) is not int:
        raise ValueError(f"{label} must be an integer period")
    return value


@dataclass(frozen=True)
class EarningsPathArtifact:
    """An ordered per-person earnings path with explicit measurement terms.

    Attributes:
        source: Provenance label for the whole path.
        unit: The measure the values are in, carried verbatim. Nothing
            here knows what any particular token means, which is what
            lets a non-US path use its own.
        price_basis: ``"nominal"`` or ``"fixed@<period>"``.
        calendar: The period calendar the integer periods count in.
        sign_domain: ``"nonnegative"`` or ``"signed"``.
        rows: ``(person_id, period, origin, status, value)`` tuples.
        closed: ``(person_id, last_period)`` for people whose path takes
            no further periods.
        carried_through_period: The last period this path has been
            carried through, or ``None`` if it has not been carried.
    """

    source: str
    unit: str
    price_basis: str
    calendar: str
    sign_domain: str
    rows: tuple[tuple[int, int, str, str, float | None], ...]
    closed: tuple[tuple[int, int], ...] = ()
    carried_through_period: int | None = None

    def __post_init__(self):
        _token(self.source, "source")
        _token(self.unit, "unit")
        _token(self.calendar, "calendar")
        _token(self.sign_domain, "sign_domain", SIGN_DOMAINS)
        parse_price_basis(self.price_basis)
        if not self.rows:
            raise ValueError("an earnings path needs at least one row")
        # Rows and closures are copied into tuples before anything is
        # indexed off them. A caller who hands in a list and then edits
        # it is editing their own list, not this path, so the index can
        # never describe rows the artifact no longer holds.
        frozen_rows = []
        cells = {}
        by_person = {}
        last = {}
        for row in self.rows:
            if len(row) != 5:
                raise ValueError("each earnings row needs five fields")
            person, period, origin, status, value = row
            _period(person, "person_id")
            _period(period, "period")
            _token(origin, "origin", ORIGINS)
            _token(status, "status", STATUSES)
            if (person, period) in cells:
                raise ValueError(
                    f"earnings path repeats person {person} period {period}"
                )
            last[person] = max(last.get(person, period), period)
            if status == "unknown":
                if value is not None:
                    raise ValueError("an unknown period carries no value")
            elif isinstance(value, bool) or not isinstance(
                value, (int, float)
            ):
                raise ValueError("a known period must carry a number")
            elif not math.isfinite(value):
                raise ValueError("a known period must be finite")
            elif value < 0 and self.sign_domain == "nonnegative":
                raise ValueError(
                    "this path declares nonnegative earnings; "
                    f"person {person} period {period} is negative"
                )
            frozen_rows.append((person, period, origin, status, value))
            cells[(person, period)] = (origin, status, value)
            by_person.setdefault(person, []).append(
                (period, origin, status, value)
            )
        closed_people = set()
        frozen_closed = []
        for entry in self.closed:
            if len(entry) != 2:
                raise ValueError("each closure needs a person and a period")
            person, period = entry
            _period(person, "person_id")
            _period(period, "period")
            if person in closed_people:
                raise ValueError(f"person {person} is closed twice")
            closed_people.add(person)
            if person not in last:
                raise ValueError(f"closed person {person} has no rows")
            if period != last[person]:
                raise ValueError(
                    f"person {person} is closed after {period} but holds "
                    f"a row at {last[person]}"
                )
            frozen_closed.append((person, period))
        if self.carried_through_period is not None:
            _period(self.carried_through_period, "carried_through_period")
            beyond = [
                period
                for _, period, _, _, _ in frozen_rows
                if period > self.carried_through_period
            ]
            if beyond:
                raise ValueError(
                    f"period {max(beyond)} is past the carried period "
                    f"{self.carried_through_period}"
                )
        object.__setattr__(self, "rows", tuple(frozen_rows))
        object.__setattr__(self, "closed", tuple(frozen_closed))
        object.__setattr__(
            self,
            "_by_person",
            {
                person: tuple(sorted(rows, key=lambda row: row[0]))
                for person, rows in by_person.items()
            },
        )
        object.__setattr__(self, "_cells", cells)
        object.__setattr__(self, "_people", tuple(sorted(by_person)))
        object.__setattr__(self, "_closed_people", frozenset(closed_people))

    @property
    def accumulable(self):
        """Whether a plain sum over periods is a defined quantity here.

        Only under a single fixed price basis. Summing nominal values
        adds different periods' prices together, which is not a total of
        anything, so this refuses rather than producing a number.
        """
        return parse_price_basis(self.price_basis)[0] == "fixed"

    @property
    def people(self):
        return self._people

    @property
    def closed_people(self):
        return self._closed_people

    def history(self, person_id):
        """This person's rows, ordered by period; empty if absent."""
        return self._by_person.get(person_id, ())

    def at(self, person_id, period):
        """``(origin, status, value)`` for a coordinate, or ``None``."""
        return self._cells.get((person_id, period))

    def prefix_total(self, person_id, through_period):
        """The bookkeeping sum of known values up to and including a period.

        A sum of the values recorded in one declared unit and one fixed
        price basis, and nothing more: no wage base, no indexation, no
        selection of high years. It is ``None`` when any period in range
        is unknown, because the total is then unknown too, and when the
        person has no rows in range at all.
        """
        if not self.accumulable:
            raise ValueError(
                f"a {self.price_basis!r} path mixes price periods; "
                "no total is defined over it"
            )
        _period(through_period, "through_period")
        rows = [
            row for row in self.history(person_id) if row[0] <= through_period
        ]
        if not rows:
            return None
        if any(status == "unknown" for _, _, status, _ in rows):
            return None
        return float(sum(value for _, _, _, value in rows))

    def known_total(self, person_id):
        """The bookkeeping sum over this person's whole recorded path."""
        rows = self.history(person_id)
        if not rows:
            return None
        return self.prefix_total(person_id, rows[-1][0])

    def carried(self, rows, *, closed, through_period):
        """Return this path extended, refusing any overwrite.

        New coordinates only: a row that would replace an existing
        person-period is a retroactive overwrite and is refused, not
        merged. Existing rows keep their values, statuses, and order.
        """
        _period(through_period, "through_period")
        existing = set(self._cells)
        added = []
        for row in rows:
            person, period = row[0], row[1]
            if (person, period) in existing:
                raise ValueError(
                    f"person {person} period {period} already has a value; "
                    "an earnings path is never overwritten"
                )
            existing.add((person, period))
            added.append(tuple(row))
        return EarningsPathArtifact(
            source=self.source,
            unit=self.unit,
            price_basis=self.price_basis,
            calendar=self.calendar,
            sign_domain=self.sign_domain,
            rows=tuple(self.rows) + tuple(added),
            closed=tuple(closed),
            carried_through_period=through_period,
        )

    def to_bytes(self):
        return json_bytes(
            {
                "format": _FORMAT,
                "schema_version": _SCHEMA_VERSION,
                "source": self.source,
                "unit": self.unit,
                "price_basis": self.price_basis,
                "calendar": self.calendar,
                "sign_domain": self.sign_domain,
                "carried_through_period": self.carried_through_period,
                "rows": [
                    {
                        "person_id": person,
                        "period": period,
                        "origin": origin,
                        "status": status,
                        "value": value,
                    }
                    for person, period, origin, status, value in sorted(
                        self.rows, key=lambda row: (row[0], row[1])
                    )
                ],
                "closed": [
                    {"person_id": person, "last_period": period}
                    for person, period in sorted(self.closed)
                ],
            }
        )

    @classmethod
    def from_bytes(cls, payload):
        raw = parse_json(payload)
        expected = {
            "format",
            "schema_version",
            "source",
            "unit",
            "price_basis",
            "calendar",
            "sign_domain",
            "carried_through_period",
            "rows",
            "closed",
        }
        if not isinstance(raw, dict) or set(raw) != expected:
            raise ValueError("earnings path has an invalid field set")
        if raw["format"] != _FORMAT:
            raise ValueError("invalid earnings path format")
        if type(raw["schema_version"]) is not int:
            raise ValueError("earnings schema version must be an integer")
        if raw["schema_version"] != _SCHEMA_VERSION:
            raise ValueError("unsupported earnings path schema version")
        if not isinstance(raw["rows"], list) or not isinstance(
            raw["closed"], list
        ):
            raise ValueError("earnings rows and closures must be arrays")
        for row in raw["rows"]:
            if not isinstance(row, dict) or set(row) != {
                "person_id",
                "period",
                "origin",
                "status",
                "value",
            }:
                raise ValueError("invalid earnings row fields")
        for entry in raw["closed"]:
            if not isinstance(entry, dict) or set(entry) != {
                "person_id",
                "last_period",
            }:
                raise ValueError("invalid earnings closure fields")
        return cls(
            source=raw["source"],
            unit=raw["unit"],
            price_basis=raw["price_basis"],
            calendar=raw["calendar"],
            sign_domain=raw["sign_domain"],
            rows=tuple(
                (
                    row["person_id"],
                    row["period"],
                    row["origin"],
                    row["status"],
                    row["value"],
                )
                for row in raw["rows"]
            ),
            closed=tuple(
                (entry["person_id"], entry["last_period"])
                for entry in raw["closed"]
            ),
            carried_through_period=raw["carried_through_period"],
        )
