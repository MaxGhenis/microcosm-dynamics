"""Prove the published d1408 diagnostic reveals no group under ten.

Verification class: labelled diagnostic publication guard. The committed
JSON is read as an aggregate artifact; no microdata is opened. The
invented-input properties show that the enumeration finds every planted
small difference of up to four published counts, and the regressions
replay the three differencing routes found in review round 1 (COLA rows,
nested role subtotals, Track M's two readings) on invented aggregates.
"""

import itertools
import json
import re
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from scripts import d1408_diagnostic
from scripts.d1408_publication_view import (
    FAMILIES,
    PEOPLE_KEYS,
    RECORD_KEYS,
    differencing_violations,
    minimum_view,
    path_category,
    projection_view,
    published_counts,
)

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = (
    ROOT / "docs/errata/2026-10-11-delayed-credit-window-diagnostic.json"
)
ERRATUM = ROOT / "docs/errata/2026-10-11-delayed-credit-window.md"
FIRST_ESTIMATES = ROOT / "runs/first_estimates_v1.json"


def _document():
    return json.loads(PUBLISHED.read_text())


def _count_leaves(value, exempt=False):
    """Independently count integer leaves under count keys."""
    total = 0
    if isinstance(value, dict):
        for key, item in value.items():
            skip = exempt or key == "committed_admitted_denominators"
            if (
                key in PEOPLE_KEYS | RECORD_KEYS
                and isinstance(item, int)
                and not isinstance(item, bool)
                and not skip
            ):
                total += 1
            else:
                total += _count_leaves(item, skip)
    elif isinstance(value, list):
        total += sum(_count_leaves(item, exempt) for item in value)
    return total


def test_every_published_subtraction_is_zero_negative_or_at_least_ten():
    document = _document()
    cells = list(published_counts(document))
    # The walker sees every published count, across every row, wave and
    # Track M reading; none is skipped.
    assert len(cells) == _count_leaves(document)
    paths = [path for _, _, path, _ in cells]
    assert any("admitted_by_row" in path for path in paths)
    assert any("readings/scored" in path for path in paths)
    assert any("readings/d430_sensitivity" in path for path in paths)
    # Exhaustive enumeration, recomputed here rather than trusted.
    pools = {}
    for family, unit, _, value in cells:
        if value > 0:
            pools.setdefault((family, unit), []).append(int(value))
    for (family, unit), values in pools.items():
        for size in range(2, 5):
            for combo in itertools.combinations(values, size):
                for signs in itertools.product((1, -1), repeat=size):
                    if 1 in signs and -1 in signs:
                        total = sum(
                            s * v for s, v in zip(signs, combo, strict=True)
                        )
                        assert not 0 < total < 10, (family, unit, combo)
    assert differencing_violations(document) == []


def test_no_published_count_is_a_small_cell():
    for _, _, path, value in published_counts(_document()):
        assert value == 0 or value >= 10, path


def test_every_family_is_pooled():
    families = {family for family, *_ in published_counts(_document())}
    assert families == set(FAMILIES.values())


def test_exempt_denominators_are_copied_from_the_committed_artifact():
    committed = FIRST_ESTIMATES.read_text()
    (first,) = [
        r for r in _document()["results"] if r["result"] == "first_estimates"
    ]
    rows = first["counts"]["committed_admitted_denominators"]
    assert rows
    for row in rows:
        assert re.search(rf"\b{row['people']}\b", committed)
        assert re.search(rf"\b{int(row['weight'])}(\.0)?\b", committed)


def test_erratum_table_publishes_nothing_beyond_the_json():
    text = ERRATUM.read_text()
    section = text[text.index("## The d1408 diagnostic") :]
    section = section[: section.index("\n## ", 5)]
    table = [line for line in section.splitlines() if line.startswith("|")]
    published = set()
    for _, _, _, value in published_counts(_document()):
        published.add(int(value))

    def numbers(value):
        if isinstance(value, dict):
            for item in value.values():
                yield from numbers(item)
        elif isinstance(value, list):
            for item in value:
                yield from numbers(item)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            yield value

    weights = {int(v) for v in numbers(_document()) if float(v).is_integer()}
    for line in table:
        # Age-group labels (50–61, 80+) are adjacent to a dash or plus.
        pattern = r"(?<![\w.%–])\d[\d,]*(?![\d.%–+]|\w)"
        # The first column names the result (for example "FRA 68").
        counted = "|".join(line.split("|")[2:])
        for token in re.findall(pattern, counted):
            value = int(token.replace(",", ""))
            if value < 10 or 1900 <= value <= 2100:
                continue  # single digits and years
            assert value in published | weights, (token, line)


# ---- invented-input properties of the enumeration ----


def _invented(counts):
    return {
        "results": [
            {
                "result": "cola",
                "waves": {
                    str(index): {"flagged_supported": {"people": value}}
                    for index, value in enumerate(counts)
                },
            }
        ]
    }


_SPACED = st.lists(
    st.integers(min_value=0, max_value=400), min_size=1, max_size=6
).map(lambda xs: sorted({10 * x + 10 for x in xs}))


@settings(deadline=None, max_examples=200)
@given(_SPACED, st.integers(1, 9), st.integers(1, 3), st.randoms())
def test_planted_small_difference_is_found(base, small, subtrahends, rnd):
    # A total equal to `small` plus up to three published subtotals.
    # Distinct published subtotals: a cell is subtracted at most once.
    parts = rnd.sample(base, min(subtrahends, len(base)))
    counts = base + [small + sum(parts)]
    rnd.shuffle(counts)
    violations = differencing_violations(_invented(counts))
    assert any(v["value"] == small for v in violations)


@settings(deadline=None, max_examples=200)
@given(st.lists(st.integers(0, 300), min_size=1, max_size=6), st.randoms())
def test_counts_spaced_by_at_least_ten_never_violate(multiples, rnd):
    # Multiples of ten: every signed sum is a multiple of ten.
    counts = [10 * m for m in multiples]
    rnd.shuffle(counts)
    assert differencing_violations(_invented(counts)) == []


@settings(deadline=None)
@given(_SPACED, st.integers(1, 9), st.randoms())
def test_enumeration_is_order_independent(base, small, rnd):
    counts = base + [base[0] + small]
    shuffled = list(counts)
    rnd.shuffle(shuffled)
    values = sorted(
        v["value"] for v in differencing_violations(_invented(counts))
    )
    again = sorted(
        v["value"] for v in differencing_violations(_invented(shuffled))
    )
    assert values == again and small in values


def test_different_families_and_units_are_not_pooled():
    document = {
        "results": [
            {"result": "cola", "waves": {"2011": {"people": 21}}},
            {"result": "r7_sharing", "flagged": {"people": 12}},
            {"result": "cola", "w": {"worker_records": 15}},
        ]
    }
    assert differencing_violations(document) == []


# ---- regressions for review round 1's three routes ----


def _cell(people, records, weight):
    return {
        "people": people,
        "worker_records": records,
        "weight": weight,
        "admitted_weight_share": weight / 1e6,
    }


def _invented_projection():
    wave = {
        "seed_cohort_weight": 1e6,
        "denominator": "invented",
        "supported/factor_evaluation": _cell(75, 75, 9000.0),
        "supported/deceased_auxiliary_basis": _cell(19, 19, 3000.0),
        "supported/positive_survivor_payment": _cell(10, 10, 1700.0),
        "supported/linked_spouse_basis": _cell(13, 13, 1900.0),
    }
    row = {
        "admitted_people": 9750,
        "admitted_weight": 1.4e6,
        "supported/factor_evaluation": _cell(60, 57, 900.0),
        "supported/linked_spouse_basis": _cell(19, 19, 300.0),
    }
    restricted = {
        "admitted_people": 9453,
        "admitted_weight": 1.3e6,
        "supported/factor_evaluation": _cell(57, 56, 880.0),
        "supported/linked_spouse_basis": _cell(17, 17, 280.0),
    }
    return {
        "result": "cola",
        "artifact": "runs/replication_urban2010_cola_v1.json",
        "counts": {"2011": wave},
        "admitted_beneficiary_counts_by_row": {"R0": row, "R5": restricted},
        "headline_changes": {},
    }


def test_round1_row_and_role_routes_are_present_raw_and_gone_public():
    raw = _invented_projection()
    raw_doc = {"results": [raw]}
    # The raw aggregate leaks exactly as the review found.
    leaked = {v["value"] for v in differencing_violations(raw_doc)}
    assert {3, 1, 2, 9} <= leaked
    public = {"results": [projection_view(raw)]}
    assert differencing_violations(public) == []
    row = public["results"][0]["admitted_by_row"]["R0"]
    assert set(row) == {"admitted_people", "admitted_weight"}
    paths = public["results"][0]["waves"]["2011"]["paths"]
    assert paths["deceased_auxiliary_basis"] == "ten or more"
    assert paths["positive_survivor_payment"] == "ten or more"
    assert paths["own_record"] == "none"


def _reading(records, flagged):
    zero = {
        "admitted_people": 2135,
        "admitted_weight": 4.5e7,
        "changed_receiving_people": 0,
        "supported_subset_change_percentage_points": 0.0,
        "change_in_admitted_people": 0,
    }
    small = {"people": "<10", "worker_records": "<10", "weight": "<10"}
    return {
        "admitted_people": 2135,
        "admitted_worker_records": records,
        "admitted_weight": 4.5e7,
        "supported": {
            "all_flagged_evaluations": flagged,
            "admitted_flagged_worker_owners": small,
            "linked_auxiliary_basis": small,
            "factor_entered_survivor_payment_gate": small,
            "factor_entered_inverse_ms5_pia": small,
        },
        "pre1917_unsupported": {"all_flagged_evaluations": {"people": 0}},
        "rows": {
            "MS0": {
                "changes": {"option_2/all": zero},
                "legacy_reproduction": {"option_2/all": {"exact_match": True}},
            }
        },
        "legacy_reproduction_verified": True,
    }


def test_round1_track_m_reading_route_is_present_raw_and_gone_public():
    raw = {
        "result": "track_m_minimum_benefit",
        "readings": {
            "scored": _reading(2391, _cell(34, 30, 776587.0)),
            "d430_sensitivity": _reading(
                2384,
                {
                    "people": "suppressed_complementary",
                    "worker_records": "suppressed_complementary",
                },
            ),
        },
    }
    leaked = {v["value"] for v in differencing_violations({"results": [raw]})}
    assert 7 in leaked
    public = minimum_view(raw)
    assert (
        "admitted_worker_records" not in public["readings"]["d430_sensitivity"]
    )
    assert public["readings"]["d430_sensitivity"]["flagged_supported"] == (
        "withheld"
    )
    assert differencing_violations({"results": [public]}) == []


def test_nonzero_track_m_change_is_refused_not_summarized():
    reading = _reading(2391, _cell(34, 30, 776587.0))
    reading["rows"]["MS0"]["changes"]["option_2/all"][
        "supported_subset_change_percentage_points"
    ] = 0.1
    with pytest.raises(ValueError, match="nonzero Track M change"):
        minimum_view(
            {
                "result": "track_m_minimum_benefit",
                "readings": {"scored": reading},
            }
        )


@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        (None, "none"),
        ({"people": 0}, "none"),
        ({"people": 1}, "fewer than ten"),
        ({"people": 9}, "fewer than ten"),
        ({"people": 10}, "ten or more"),
        ({"people": "<10"}, "fewer than ten"),
        ({"people": "suppressed_complementary"}, "withheld"),
    ],
)
def test_path_category_never_publishes_a_count(cell, expected):
    assert path_category(cell) == expected


def test_assembler_refuses_a_document_with_a_small_difference(monkeypatch):
    def fake(results):
        return {
            "result": results["result"],
            "waves": {"a": {"people": 40}, "b": {"people": 37}},
        }

    monkeypatch.setattr(d1408_diagnostic, "public_view", fake)
    monkeypatch.setattr(d1408_diagnostic, "validate_result_scope", lambda r: 0)
    monkeypatch.setattr(
        d1408_diagnostic, "validate_projection_publication", lambda r: 0
    )
    monkeypatch.setattr(d1408_diagnostic, "DESTINATION", Path("/dev/null/x"))

    class Scratch:
        def __truediv__(self, name):
            return _Aggregate(name)

    class _Aggregate:
        def __init__(self, name):
            self.name = name

        def is_file(self):
            return True

        def read_text(self):
            if "sharing" in self.name:
                return json.dumps({"results": [{"result": "r7_sharing"}]})
            return json.dumps({"result": "cola"})

    monkeypatch.setattr(d1408_diagnostic, "SCRATCH", Scratch())
    with pytest.raises(ValueError, match="reveal a group under ten"):
        d1408_diagnostic.assemble()
