"""Trustees Table V.A2 immigration control reader (offline, hash-pinned).

The **entry control** for a scheduled-entrant cohort: SSA Office of the Chief
Actuary, *The 2026 Annual Report of the Board of Trustees of the Federal OASI
and DI Trust Funds*, supplemental single-year Table V.A2, "Immigration
Assumptions, Calendar Years 1940-2100" (in thousands).

The reader is deliberately offline.  It verifies the committed capture
manifest and the raw snapshot bytes before parsing any HTML, exactly as
:mod:`scripts.build_ssa_level_anchors` does for the vintage-1 level anchors.
``ssa.gov`` answers HTTP 403 to ``curl`` from this environment, so the
snapshot was acquired by browser network-response capture -- the route already
documented at ``scripts/extract_ssa_tr_ultimate_assumptions_2014.py:1-11``.
See ``data/external/trustees2026_lr5a2.source.provenance.json``.

**Why this module does not reuse the level-anchor parser.**  The V.A2 page's
data rows carry an UNCLOSED ``<td>`` around the calendar-year cell::

    <td style="text-align:left; border:none;">2026  <td style=...>&nbsp;</td>

``_AllTablesParser`` in ``scripts/build_ssa_level_anchors.py`` raises
``"nested table cell"`` on that markup.  :class:`_ImmigrationTableParser`
below closes an open cell implicitly when the next cell starts, which is what
a browser does and what recovers the year.

**What the table means, and the three constraints on using it.**

1. Table V.A2 reports, separately for the lawful-permanent-resident (LPR)
   stock and the temporary-or-unlawfully-present stock: ``inflow``,
   ``outflow``, ``adjustment of status`` and ``net change``; then one
   ``total net change`` column.  An *entry* seam consumes
   :attr:`ImmigrationYear.positive_inflow` -- the sum of the two inflow
   columns -- and NOT the total net change.  Adjustment of status is the same
   person moving between the two stocks and is never a new person: it enters
   the LPR stock and leaves the other with opposite signs, and the reader
   checks that identity per row.
2. The table's universe is the **Social Security area** (territories, certain
   people abroad), not the Census resident population the certified frame
   represents.  Nothing here bridges those universes; consumers must label a
   schedule aligned to V.A2 ``ssa_area_proxy`` and keep it report-only.
3. With no emigration law in the engine, an entry-only schedule cannot claim
   alignment to a *net* path.  :attr:`ImmigrationYear.entry_only_minus_net_gap`
   is published as a named audit line so the structural gap is stated rather
   than hidden.

Table V.A2 carries **no age or sex detail**: it sizes cohorts only.  All
composition must come from a donor artifact (see
:mod:`populace_dynamics.data.nativity_frame`).
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT_DIR = (
    ROOT / "data" / "external" / "snapshots" / "trustees_va2_vintage1"
)
SNAPSHOT_FILENAME = "trustees2026_lr5a2.html"
MANIFEST_FILENAME = "capture_manifest.txt"

#: The committed manifest's own digest.  A source reissue fails closed.
CAPTURE_MANIFEST_SHA256 = (
    "d6e445ed8dd9deedae9ee9b221d841003230ea9b0e4bad03ded3716cec08176f"
)
#: The content-decoded HTTP 200 response body this reader was written against.
SNAPSHOT_SHA256 = (
    "5dfd05e5c5d4bbe413dd97f2256db24d5595e561623455edca3761bbfece89da"
)

SOURCE_URL = "https://www.ssa.gov/oact/TR/2026/lr5a2.html"
PUBLICATION = "2026 OASDI Trustees Report"
TABLE_ID = "V.A2"
SOURCE_DOCUMENT_ID = "ssa_trustees_2026_lr5a2"
UNITS = "thousands_of_persons"
UNIVERSE = "social_security_area"

#: The caption text the snapshot must carry, normalized.
EXPECTED_CAPTION = (
    "Table V.A2.—Immigration Assumptions,a Calendar Years 1940-2100 "
    "[In thousands]"
)

#: In-table anchor id -> scenario name.  The four scenarios are one table
#: separated by full-width header rows, not four tables.
SCENARIO_ANCHORS: dict[str, str] = {
    "alt_h": "historical",
    "alt_2": "intermediate",
    "alt_1": "low_cost",
    "alt_3": "high_cost",
}

#: The nine numeric columns, in the order the table lays them out.
VALUE_FIELDS: tuple[str, ...] = (
    "lpr_inflow",
    "lpr_outflow",
    "lpr_adjustment_of_status",
    "lpr_net_change",
    "other_inflow",
    "other_outflow",
    "other_adjustment_of_status",
    "other_net_change",
    "total_net_change",
)

#: Published values are rounded to whole thousands, so each derived identity
#: is checked against the sum of its terms' rounding half-widths.
_IDENTITY_TOLERANCE = 2.0

_MANIFEST_LINE = re.compile(
    r"(?P<retrieved>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) "
    r"(?P<sha256>[0-9a-f]{64}) "
    r"(?P<size>[1-9]\d*) "
    r"(?P<filename>[A-Za-z0-9_.-]+)"
)

#: An em dash (or a plain hyphen) is the table's not-applicable marker.
_NOT_APPLICABLE = {"—", "-", "--", ""}


@dataclass(frozen=True)
class ImmigrationYear:
    """One calendar-year row of Table V.A2, in thousands of persons."""

    year: int
    scenario: str
    lpr_inflow: float | None
    lpr_outflow: float | None
    lpr_adjustment_of_status: float | None
    lpr_net_change: float | None
    other_inflow: float | None
    other_outflow: float | None
    other_adjustment_of_status: float | None
    other_net_change: float | None
    total_net_change: float | None

    @property
    def positive_inflow(self) -> float | None:
        """LPR + other gross inflow: the only entry-seam control.

        Returns ``None`` when either component is not published for the year
        (the early historical rows report LPR only).
        """
        if self.lpr_inflow is None or self.other_inflow is None:
            return None
        return self.lpr_inflow + self.other_inflow

    @property
    def entry_only_minus_net_gap(self) -> float | None:
        """Gross entries minus the published total net change.

        The structural gap an entry-only module cannot close: it is the
        emigration plus mortality-of-the-foreign-born the engine has no law
        for.  Published as an audit line, never minimized to zero.
        """
        inflow = self.positive_inflow
        if inflow is None or self.total_net_change is None:
            return None
        return inflow - self.total_net_change

    def as_dict(self) -> dict[str, Any]:
        """A JSON-safe record including both derived audit quantities."""
        record: dict[str, Any] = {
            "year": self.year,
            "scenario": self.scenario,
        }
        for field in VALUE_FIELDS:
            record[field] = getattr(self, field)
        record["positive_inflow"] = self.positive_inflow
        record["entry_only_minus_net_gap"] = self.entry_only_minus_net_gap
        return record


@dataclass(frozen=True)
class _Cell:
    tag: str
    text: str
    anchor_ids: tuple[str, ...]
    colspan: int


class _ImmigrationTableParser(HTMLParser):
    """Collect caption, rows and cells, closing unclosed cells implicitly.

    The V.A2 page leaves the calendar-year ``<td>`` unclosed on every data
    row.  A parser that raises on a nested cell (the level-anchor builder's)
    cannot read the page at all; a parser that silently restarts the cell
    loses the year.  This one closes the open cell when the next cell or the
    row ends, which is the browser's own recovery and preserves the year.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.caption: str | None = None
        self.rows: list[tuple[_Cell, ...]] = []
        self._caption_chunks: list[str] | None = None
        self._row: list[_Cell] | None = None
        self._cell: list[str] | None = None
        self._cell_tag: str | None = None
        self._cell_anchors: list[str] = []
        self._cell_colspan: int = 1
        self._depth = 0

    def _close_cell(self) -> None:
        if self._cell is None or self._row is None:
            return
        self._row.append(
            _Cell(
                tag=self._cell_tag or "td",
                text=_normalize("".join(self._cell)),
                anchor_ids=tuple(self._cell_anchors),
                colspan=self._cell_colspan,
            )
        )
        self._cell = None
        self._cell_tag = None
        self._cell_anchors = []
        self._cell_colspan = 1

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = {key: value for key, value in attrs if value is not None}
        if tag == "table":
            self._depth += 1
            return
        if self._depth == 0:
            return
        if tag == "caption":
            self._caption_chunks = []
        elif tag == "tr":
            self._close_cell()
            self._row = []
        elif tag in {"th", "td"} and self._row is not None:
            self._close_cell()
            self._cell = []
            self._cell_tag = tag
            self._cell_anchors = []
            raw_span = attributes.get("colspan")
            self._cell_colspan = (
                int(raw_span) if raw_span and raw_span.isdigit() else 1
            )
        elif tag == "br":
            if self._caption_chunks is not None:
                self._caption_chunks.append(" ")
            if self._cell is not None:
                self._cell.append(" ")
        elif tag == "a" and self._cell is not None:
            anchor = attributes.get("id")
            if anchor:
                self._cell_anchors.append(anchor)

    def handle_data(self, data: str) -> None:
        if self._caption_chunks is not None:
            self._caption_chunks.append(data)
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._depth == 0:
            return
        if tag in {"th", "td"}:
            self._close_cell()
        elif tag == "tr":
            self._close_cell()
            if self._row is not None:
                self.rows.append(tuple(self._row))
                self._row = None
        elif tag == "caption" and self._caption_chunks is not None:
            self.caption = _normalize("".join(self._caption_chunks))
            self._caption_chunks = None
        elif tag == "table":
            self._close_cell()
            if self._row is not None:
                self.rows.append(tuple(self._row))
                self._row = None
            self._depth -= 1


def _normalize(text: str) -> str:
    """Collapse presentation whitespace while preserving visible content."""
    return " ".join(text.replace("\xa0", " ").split())


def _parse_value(literal: str, *, where: str) -> float | None:
    """Parse one published cell: a signed integer, or a not-applicable dash."""
    token = literal.strip()
    # Footnote markers are single letters appended to the value; drop them.
    token = re.sub(r"(?<=\d)\s*[a-z]$", "", token)
    token = re.sub(r"^[a-z]\s+(?=[-\d])", "", token)
    token = token.replace(",", "").strip()
    if token in _NOT_APPLICABLE:
        return None
    if not re.fullmatch(r"-?\d+", token):
        raise ValueError(f"unparsable V.A2 value {literal!r} at {where}")
    return float(token)


def read_manifest(snapshot_dir: Path | None = None) -> dict[str, Any]:
    """Verify and parse the committed one-line capture manifest."""
    directory = Path(snapshot_dir) if snapshot_dir else SNAPSHOT_DIR
    raw = (directory / MANIFEST_FILENAME).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != CAPTURE_MANIFEST_SHA256:
        raise ValueError(
            f"capture manifest sha256 {digest} != pinned "
            f"{CAPTURE_MANIFEST_SHA256}; source manifest drift"
        )
    text = raw.decode("utf-8")
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise ValueError("capture manifest must have one trailing newline")
    lines = text.splitlines()
    if len(lines) != 1:
        raise ValueError("capture manifest must carry exactly one entry")
    match = _MANIFEST_LINE.fullmatch(lines[0])
    if match is None:
        raise ValueError(f"malformed capture manifest line: {lines[0]!r}")
    return {
        "retrieval_timestamp": match.group("retrieved"),
        "sha256": match.group("sha256"),
        "size_bytes": int(match.group("size")),
        "filename": match.group("filename"),
    }


def load_snapshot(snapshot_dir: Path | None = None) -> bytes:
    """Return the manifest-verified raw snapshot bytes."""
    directory = Path(snapshot_dir) if snapshot_dir else SNAPSHOT_DIR
    entry = read_manifest(directory)
    if entry["filename"] != SNAPSHOT_FILENAME:
        raise ValueError(
            f"capture manifest names {entry['filename']!r}, expected "
            f"{SNAPSHOT_FILENAME!r}"
        )
    raw = (directory / SNAPSHOT_FILENAME).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != entry["sha256"]:
        raise ValueError(
            f"snapshot sha256 {digest} != manifest {entry['sha256']}"
        )
    if digest != SNAPSHOT_SHA256:
        raise ValueError(
            f"snapshot sha256 {digest} != pinned {SNAPSHOT_SHA256}; the "
            "reader was written against different source bytes"
        )
    if len(raw) != entry["size_bytes"]:
        raise ValueError("snapshot length disagrees with the capture manifest")
    return raw


def _check_row_identities(record: ImmigrationYear) -> None:
    """Assert V.A2's own published accounting identities on one row.

    Three checks, each a property of the table rather than of this reader:
    the two stock net-change identities, and the reclassification identity
    that makes adjustment of status a transfer and never a new person.
    """
    if (
        record.lpr_inflow is not None
        and record.lpr_outflow is not None
        and record.lpr_adjustment_of_status is not None
        and record.lpr_net_change is not None
    ):
        implied = (
            record.lpr_inflow
            - record.lpr_outflow
            + record.lpr_adjustment_of_status
        )
        if abs(implied - record.lpr_net_change) > _IDENTITY_TOLERANCE:
            raise ValueError(
                f"V.A2 {record.scenario} {record.year}: LPR net change "
                f"{record.lpr_net_change} != inflow - outflow + adjustment "
                f"({implied})"
            )
    if (
        record.other_inflow is not None
        and record.other_outflow is not None
        and record.other_adjustment_of_status is not None
        and record.other_net_change is not None
    ):
        implied = (
            record.other_inflow
            - record.other_outflow
            - record.other_adjustment_of_status
        )
        if abs(implied - record.other_net_change) > _IDENTITY_TOLERANCE:
            raise ValueError(
                f"V.A2 {record.scenario} {record.year}: other net change "
                f"{record.other_net_change} != inflow - outflow - adjustment "
                f"({implied})"
            )
    if (
        record.lpr_adjustment_of_status is not None
        and record.other_adjustment_of_status is not None
        and record.lpr_adjustment_of_status
        != record.other_adjustment_of_status
    ):
        raise ValueError(
            f"V.A2 {record.scenario} {record.year}: adjustment of status is "
            "not a transfer between the two stocks "
            f"({record.lpr_adjustment_of_status} vs "
            f"{record.other_adjustment_of_status})"
        )
    if (
        record.lpr_net_change is not None
        and record.other_net_change is not None
        and record.total_net_change is not None
    ):
        implied = record.lpr_net_change + record.other_net_change
        if abs(implied - record.total_net_change) > _IDENTITY_TOLERANCE:
            raise ValueError(
                f"V.A2 {record.scenario} {record.year}: total net change "
                f"{record.total_net_change} != LPR + other ({implied})"
            )


def parse_table(raw: bytes) -> dict[str, tuple[ImmigrationYear, ...]]:
    """Parse every scenario section of Table V.A2 from the snapshot bytes."""
    parser = _ImmigrationTableParser()
    parser.feed(raw.decode("utf-8"))
    if parser.caption != EXPECTED_CAPTION:
        raise ValueError(
            f"V.A2 caption {parser.caption!r} != expected "
            f"{EXPECTED_CAPTION!r}"
        )

    scenarios: dict[str, list[ImmigrationYear]] = {}
    current: str | None = None
    for row in parser.rows:
        anchors = {anchor for cell in row for anchor in cell.anchor_ids} & set(
            SCENARIO_ANCHORS
        )
        if anchors:
            if len(anchors) != 1:
                raise ValueError(
                    f"row carries {len(anchors)} scenario anchors"
                )
            current = SCENARIO_ANCHORS[anchors.pop()]
            if current in scenarios:
                raise ValueError(f"scenario {current} opened twice")
            scenarios[current] = []
            continue
        if current is None:
            continue
        values = [cell.text for cell in row if cell.text != ""]
        if not values:
            continue
        head = values[0]
        if not re.fullmatch(r"(19|20|21)\d\d", head):
            continue
        year = int(head)
        rest = values[1:]
        if len(rest) != len(VALUE_FIELDS):
            raise ValueError(
                f"V.A2 {current} {year}: {len(rest)} value cells, expected "
                f"{len(VALUE_FIELDS)}"
            )
        parsed = {
            field: _parse_value(token, where=f"{current} {year} {field}")
            for field, token in zip(VALUE_FIELDS, rest, strict=True)
        }
        record = ImmigrationYear(year=year, scenario=current, **parsed)
        _check_row_identities(record)
        scenarios[current].append(record)

    missing = set(SCENARIO_ANCHORS.values()) - set(scenarios)
    if missing:
        raise ValueError(f"V.A2 is missing scenario(s) {sorted(missing)}")
    for name, rows in scenarios.items():
        years = [record.year for record in rows]
        if years != sorted(set(years)):
            raise ValueError(f"V.A2 {name} years are not strictly increasing")
    return {name: tuple(rows) for name, rows in scenarios.items()}


@dataclass(frozen=True)
class TrusteesImmigrationControl:
    """The parsed, identity-checked V.A2 control for one scenario."""

    scenario: str
    rows: tuple[ImmigrationYear, ...]
    manifest: dict[str, Any]

    def by_year(self) -> dict[int, ImmigrationYear]:
        return {record.year: record for record in self.rows}

    def positive_inflow(self, years: Sequence[int]) -> dict[int, float]:
        """Gross entries, in thousands, for each requested calendar year.

        This is the quantity a scheduled-entrant cohort is sized to.  It
        deliberately excludes outflow (there is no exit law) and adjustment of
        status (a reclassification, not a new person).
        """
        table = self.by_year()
        out: dict[int, float] = {}
        for year in years:
            record = table.get(int(year))
            if record is None:
                raise KeyError(
                    f"V.A2 {self.scenario} does not cover year {year}"
                )
            value = record.positive_inflow
            if value is None:
                raise ValueError(
                    f"V.A2 {self.scenario} {year} publishes no gross inflow "
                    "for one or both stocks"
                )
            out[int(year)] = value
        return out

    def provenance(self) -> dict[str, Any]:
        """The source identity a consuming artifact must republish."""
        return {
            "publication": PUBLICATION,
            "table_id": TABLE_ID,
            "source_document_id": SOURCE_DOCUMENT_ID,
            "source_url": SOURCE_URL,
            "scenario": self.scenario,
            "units": UNITS,
            "universe": UNIVERSE,
            "snapshot_sha256": SNAPSHOT_SHA256,
            "capture_manifest_sha256": CAPTURE_MANIFEST_SHA256,
            "retrieval_timestamp": self.manifest["retrieval_timestamp"],
            "network_access": (
                "none; reads only the committed, hash-verified snapshot"
            ),
            "universe_bridge_status": (
                "unbridged: V.A2 counts the Social Security area, the "
                "certified frame counts the Census resident population; any "
                "schedule aligned to this control is an ssa_area_proxy"
            ),
            "net_alignment_status": (
                "unachievable by construction: the engine has no emigration "
                "law, so an entry-only schedule is aligned to gross inflow "
                "and its distance from the published net path is reported as "
                "entry_only_minus_net_gap"
            ),
        }


def load_control(
    scenario: str = "intermediate", snapshot_dir: Path | None = None
) -> TrusteesImmigrationControl:
    """Load one scenario of Table V.A2 from the committed snapshot."""
    if scenario not in set(SCENARIO_ANCHORS.values()):
        raise ValueError(
            f"unknown V.A2 scenario {scenario!r}; expected one of "
            f"{sorted(set(SCENARIO_ANCHORS.values()))}"
        )
    directory = Path(snapshot_dir) if snapshot_dir else SNAPSHOT_DIR
    raw = load_snapshot(directory)
    scenarios = parse_table(raw)
    return TrusteesImmigrationControl(
        scenario=scenario,
        rows=scenarios[scenario],
        manifest=read_manifest(directory),
    )
