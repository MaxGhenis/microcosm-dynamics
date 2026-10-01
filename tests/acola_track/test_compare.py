"""compare_acola.py on INVENTED comparator records only.

Every comparator value here is invented. No sealed record, seal or source
is read. The artifacts are built with stage 1's own summarizers, null gaps
and artifact writer, so the comparison reads the stage-1 layout.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from populace_dynamics.acola_track import nulls as acola_nulls
from populace_dynamics.acola_track import runner
from populace_dynamics.acola_track import statistics as ac
from populace_dynamics.acola_track.config import (
    DEFERRED_ROWS,
    REGISTERED_ROWS,
    REGISTRATION_POINTER,
    RUNNABLE_ROWS,
)

ROOT = Path(__file__).resolve().parents[2]
INVENTED = "INVENTED"


def _script(name):
    spec = importlib.util.spec_from_file_location(
        f"_acola_test_{name}", ROOT / "scripts" / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cmp = _script("compare_acola")
entry = _script("run_acola_registered")


# ---- invented comparator records -----------------------------------------


def mint_cell(html, decimals=1, raw=None, fmt="0.0%", literal=None):
    """An INVENTED MINT5 cell in the registered schema."""

    value_l, count_l = literal if literal is not None else (html, decimals)
    return {
        "html_display": f"{html}%",
        "html_value": html,
        "html_decimals": decimals,
        "xlsx_cell": "INVENTED!Z9",
        "xlsx_raw": raw,
        "xlsx_number_format": fmt,
        "xlsx_value_pct": value_l,
        "xlsx_decimals_pct": count_l,
        "pdf_display": f"{html}%",
    }


def invented_record(**changes):
    """An INVENTED record in schema acola-comparator-v1."""

    bands = {
        "Total": "-15.0",
        "62-69": "-9.0",
        "70-79": "-16.0",
        "80-89": "-18.0",
        "90+": "-19.0",
    }
    record = {
        "schema_version": "acola-comparator-v1",
        "producer": "reconciled",
        "sources": {"sources/invented.html": "0" * 64},
        "oact": {
            "footer_verbatim": (
                "Based on Intermediate Assumptions of the 2026 Trustees "
                "Report."
            ),
            "footer_matches_registration": True,
            "provision_text_matches_registration": True,
            "row_label_verbatim": "2030",
            "columns": [
                {
                    "key": "proposal_income_rate",
                    "header_verbatim": INVENTED,
                    "display": "11.00",
                    "value": "11.00",
                    "decimals": 2,
                },
                {
                    "key": "proposal_cost_rate",
                    "header_verbatim": INVENTED,
                    "display": "10.00",
                    "value": "10.00",
                    "decimals": 2,
                },
                {
                    "key": "change_income_rate",
                    "header_verbatim": INVENTED,
                    "display": "-0.01",
                    "value": "-0.01",
                    "decimals": 2,
                },
                {
                    "key": "change_cost_rate",
                    "header_verbatim": INVENTED,
                    "display": "-0.50",
                    "value": "-0.50",
                    "decimals": 2,
                },
            ],
            "prints_oasi_di_split_2030": False,
            "cost_includes_admin_expenses": "yes",
            "cost_includes_railroad_interchange": "yes",
            "december_2030_timing": {
                "reading": "not_stated",
                "evidence_verbatim": INVENTED,
                "evidence_source": INVENTED,
            },
        },
        "pwbm": {
            "last_modified": INVENTED,
            "last_modified_matches_registration": True,
            "row_2030": {
                "year": "2030",
                "Baseline income rate": "11.000000000000001",
                "Baseline cost rate": "12.000000000000002",
                "A1 income rate": "10.990000000000002",
                "A1 cost rate": "11.640000000000001",
            },
            "stored_decimals": {
                "Baseline income rate": 15,
                "Baseline cost rate": 15,
                "A1 income rate": 15,
                "A1 cost rate": 15,
            },
            "prints_oasi_di_split_2030": False,
            "cost_includes_admin_expenses": "not_stated",
            "cost_includes_railroad_interchange": "not_stated",
            "december_2030_timing": {
                "reading": "not_stated",
                "evidence_verbatim": INVENTED,
                "evidence_source": INVENTED,
            },
        },
        "mint5": {
            "table1": {
                "rows": {
                    band: {
                        "median_diff_pct": mint_cell(value),
                        "median_monthly_scheduled": {"html_display": "$1"},
                        "pct_population_affected": {"html_display": "9%"},
                    }
                    for band, value in bands.items()
                }
            },
            "table2": {"rows": {"Total": {"note": INVENTED}}},
            "median_type": "median_of_individual_differences",
            "start_date_reading": "unsettled",
            "december_2030_timing": {
                "reading": "not_stated",
                "evidence_verbatim": INVENTED,
                "evidence_source": INVENTED,
            },
            "prints_oasi_di_split": False,
        },
    }
    for path, value in changes.items():
        target = record
        keys = path.split(".")
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
    return record


def _column(record, key):
    return next(c for c in record["oact"]["columns"] if c["key"] == key)


# ---- an invented artifact in the stage-1 layout ---------------------------


def _person(pid, draw, age, base, reform, component="retired_worker"):
    return {
        "draw": draw,
        "person_id": pid,
        "family_unit_id": pid,
        "weight": float(pid),
        "birth_year": 2030 - age,
        "beneficiary_base": True,
        "beneficiary_reform": True,
        "benefit_base": float(base),
        "benefit_reform": float(reform),
        "benefit_components": {
            component: {"base": float(base), "reform": float(reform)}
        },
        "spouse_worker_class": "unclassified",
    }


def _people(cut):
    ages = (55, 63, 66, 72, 75, 83, 86, 91, 94, 64)
    return [
        _person(
            pid,
            draw,
            age,
            1000.0 + 10 * pid,
            (1000.0 + 10 * pid) * (1 - cut * (1 + pid % 3) / 3),
            "disabled_worker" if pid % 4 == 0 else "retired_worker",
        )
        for draw in (0, 1)
        for pid, age in enumerate(ages, start=1)
    ]


@lru_cache(maxsize=1)
def _layout_parts():
    nulls = acola_nulls.build_nulls()
    rows = {}
    for row_id in RUNNABLE_ROWS:
        row = REGISTERED_ROWS[row_id]
        records = _people(0.03 if row.sub_row == "cost" else 0.17)
        options = {"draw_indices": (0, 1), "floor_seeds": (0, 1, 2)}
        if row.sub_row == "cost":
            summary = ac.summarize_cost(records, **options)
        else:
            summary = ac.summarize_mint(
                records, age_rule=row.age_rule, **options
            )
        runner._add_null_gaps(summary, row, nulls)
        rows[row_id] = {
            "status": "computed",
            "labels": [INVENTED],
            "row": row.as_dict(),
            "benefit_counters": {},
            "refusals": [],
            "membership_note": runner.MEMBERSHIP_NOTE,
            **summary,
        }
    return json.dumps({"rows": rows, "nulls": nulls}, allow_nan=False)


def invented_artifact(provenance="invented", **changes):
    parts = json.loads(_layout_parts())
    artifact = {
        "header": "INVENTED DATA - NOT A COMPARISON",
        "schema_version": runner.SCHEMA_VERSION,
        "publishes_regardless": True,
        "comparator_seal_opened_before_commit": False,
        "data_provenance": provenance,
        "registration_pointer": REGISTRATION_POINTER,
        "labels": [INVENTED, "report-only"],
        "deferred_rows": deepcopy(DEFERRED_ROWS),
        **parts,
        "run": {
            "registration_pointer": REGISTRATION_POINTER,
            "registered_commit": "a" * 40,
            "git_head": "a" * 40,
            "git_clean": True,
            "command": "INVENTED DATA - pytest",
        },
    }
    artifact.update(changes)
    return artifact


def write_artifact(tmp_path, artifact=None, name="artifact.json"):
    path = tmp_path / name
    entry.write_artifact(path, artifact or invented_artifact(), {})
    return path


def write_sealed(tmp_path, record=None, extra=None):
    """An INVENTED evidence folder with a record and a seal over it."""

    ev = tmp_path / "ev"
    lane = ev / "acola-comparator-20260930"
    lane.mkdir(parents=True)
    files = {
        "acola-comparator-20260930/reconciled.json": json.dumps(
            record or invented_record(), indent=2
        ).encode(),
        "acola-comparator-20260930/sources/invented.html": b"INVENTED",
    }
    files.update(extra or {})
    seal = {"files": {}}
    for relative, raw in files.items():
        target = ev / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        seal["files"][relative] = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
    seal_path = ev / "acola-comparator-seal-20260930.json"
    seal_path.write_text(json.dumps(seal, indent=2))
    return seal_path


def run_compare(tmp_path, record=None, artifact=None, **options):
    return cmp.run(
        seal_path=write_sealed(tmp_path, record),
        artifact_path=write_artifact(tmp_path, artifact),
        allow_invented=options.pop("allow_invented", True),
        **options,
    )


# ---- exact numbers and intervals -----------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Fraction(0), "0"),
        (Fraction(1, 4), "0.25"),
        (Fraction(-5, 2), "-2.5"),
        (Fraction(100), "100"),
        (Fraction(1, 3), "0.33333333333333333333"),
        (Fraction(-2, 3), "-0.66666666666666666667"),
    ],
)
def test_render_terminating_in_full_otherwise_twenty_digits(value, expected):
    assert cmp.render(value) == expected


fractions = st.fractions(
    min_value=-1000, max_value=1000, max_denominator=10**6
)


@given(fractions, fractions, fractions, fractions)
@settings(max_examples=200, deadline=None)
def test_interval_subtraction_is_a_minus_d_to_b_minus_c(a, b, c, d):
    a, b = sorted((a, b))
    c, d = sorted((c, d))
    gap = cmp.subtract(cmp.interval(a, b), cmp.interval(c, d))
    assert gap == {"lo": a - d, "hi": b - c}
    for x in (a, b, (a + b) / 2):
        for y in (c, d, (c + d) / 2):
            assert gap["lo"] <= x - y <= gap["hi"]
    point = cmp.subtract(a, cmp.interval(c, d))
    assert point == {"lo": a - d, "hi": a - c}
    assert cmp.subtract(a, c) == a - c


def test_interval_refuses_reversed_ends():
    with pytest.raises(ValueError):
        cmp.interval(Fraction(1), Fraction(0))


@pytest.mark.parametrize(
    "value", [1.5, None, True, "1.5 ", "", "NaN", "Infinity", "abc"]
)
def test_values_are_parsed_from_strings_never_floats(value):
    with pytest.raises(cmp.RecordError):
        cmp.parse_decimal(value, "invented")


def test_decimal_strings_keep_every_stored_digit():
    assert cmp.parse_decimal("12.000000000000002", "x") == Decimal(
        "12.000000000000002"
    )
    assert cmp.decimals_of(Decimal("1.2E-5")) == 6
    assert cmp.decimals_of(Decimal("12E+1")) == 0
    assert cmp.shortest_decimals(Decimal("5.0")) == 0
    assert cmp.half_unit(2) == Fraction(1, 200)


# ---- OACT ----------------------------------------------------------------

cents = st.integers(-2000, 3000).map(lambda n: Decimal(n).scaleb(-2))


@given(cents, cents, st.integers(0, 4))
@settings(max_examples=300, deadline=None)
def test_oact_corners_contain_the_point_and_verify_monotonicity(p, d, extra):
    """REG relies on monotonicity; check it on the actual boxes."""

    places = 2 + extra
    hp = hd = cmp.half_unit(places)
    p, d = Fraction(p), Fraction(d)
    assume(p - d - hp - hd > 0)
    corners, bounds = cmp.four_corner(cmp.oact_statistic, p, hp, d, hd)
    point = cmp.oact_statistic(p, d)
    assert bounds["lo"] <= point <= bounds["hi"]
    check = cmp.grid_check(cmp.oact_statistic, p, hp, d, hd, bounds)
    assert check["within_corner_bounds"]
    # dC/dd has the sign of p; for fixed d, dC/dp has the sign of -d.
    step = hd / 4
    for cp, _ in corners:
        later = cmp.oact_statistic(cp, d + step) - cmp.oact_statistic(cp, d)
        assert later == 0 if cp == 0 else (later > 0) == (cp > 0)
    shifted = cmp.oact_statistic(p + hp / 4, d) - point
    assert shifted == 0 if d == 0 else (shifted > 0) == (d < 0)


def test_oact_conversion_interval_and_gate_from_recorded_decimals():
    result = cmp.compare_oact(invented_record())
    p, d, h = Fraction(10), Fraction(-1, 2), Fraction(1, 200)
    assert result["defined"]
    assert result["point"] == 100 * d / (p - d)
    corner_values = [
        100 * (d + sd * h) / (p + sp * h - (d + sd * h))
        for sp in (-1, 1)
        for sd in (-1, 1)
    ]
    assert result["interval"] == {
        "lo": min(corner_values),
        "hi": max(corner_values),
    }
    assert result["inputs"]["current_law_cost_rate_cl"] == p - d
    assert result["inputs"]["cl_half_width"] == 2 * h
    assert result["precision_gate"]["primary"] == "OACT"
    assert result["cost_definition"]["dilution"].startswith("toward zero")
    assert result["memo_items"]["proposal_income_rate"]["value"] == "11.00"


def test_oact_half_unit_follows_the_record_not_a_constant():
    record = invented_record()
    _column(record, "proposal_cost_rate").update(value="10.000", decimals=3)
    _column(record, "change_cost_rate").update(value="-0.500", decimals=3)
    result = cmp.compare_oact(record)
    assert result["inputs"]["p_half_unit"] == Fraction(1, 2000)
    assert result["inputs"]["d_half_unit"] == Fraction(1, 2000)


def test_oact_count_disagreeing_with_its_string_is_reported():
    record = invented_record()
    _column(record, "change_cost_rate").update(decimals=3)
    result = cmp.compare_oact(record)
    assert result["inputs"]["d_decimals"]["decimals_consistent"] is False
    assert result["inputs"]["d_half_unit"] == Fraction(1, 2000)
    assert "alternative_interval_from_string_decimals" in result


@pytest.mark.parametrize(
    ("p", "d", "primary"),
    [
        ("10.00", "-0.09", "PWBM"),
        ("0.09", "-0.50", "PWBM"),
        ("10.00", "-0.10", "OACT"),
    ],
)
def test_precision_gate_switches_primary_mechanically(p, d, primary):
    record = invented_record()
    _column(record, "proposal_cost_rate")["value"] = p
    _column(record, "change_cost_rate")["value"] = d
    assert cmp.compare_oact(record)["precision_gate"]["primary"] == primary


def test_oact_nonpositive_denominator_at_a_corner_is_undefined():
    record = invented_record()
    _column(record, "proposal_cost_rate")["value"] = "0.50"
    _column(record, "change_cost_rate")["value"] = "0.49"
    result = cmp.compare_oact(record)
    assert result["defined"] is False
    assert "every corner" in result["undefined_reason"]


def test_oact_null_cell_is_reported_never_guessed():
    record = invented_record()
    _column(record, "change_cost_rate")["value"] = None
    result = cmp.compare_oact(record)
    assert result["defined"] is False
    assert "change_cost_rate" in result["undefined_reason"]
    assert result["precision_gate"]["branch"] == "undefined"


# ---- PWBM ----------------------------------------------------------------


def test_pwbm_point_when_both_values_store_six_or_more_decimals():
    result = cmp.compare_pwbm(invented_record())
    b = Fraction(Decimal("12.000000000000002"))
    r = Fraction(Decimal("11.640000000000001"))
    assert result["point"] == 100 * (r - b) / b
    assert result["interval"] == {"lo": result["point"], "hi": result["point"]}
    assert result["interval_branch"].startswith("point")
    assert result["cost_definition"]["dilution"] == "unsigned"


@given(
    st.integers(500, 3000),
    st.integers(-300, 300),
    st.integers(0, 5),
    st.integers(0, 15),
)
@settings(max_examples=200, deadline=None)
def test_pwbm_branch_and_corners_follow_the_six_decimal_rule(
    b_cents, change, b_places, r_places
):
    b = Decimal(b_cents).scaleb(-2).quantize(Decimal(1).scaleb(-b_places))
    r = (Decimal(b_cents + change).scaleb(-2)).quantize(
        Decimal(1).scaleb(-r_places)
    )
    record = invented_record()
    record["pwbm"]["row_2030"].update(
        {"Baseline cost rate": str(b), "A1 cost rate": str(r)}
    )
    record["pwbm"]["stored_decimals"].update(
        {"Baseline cost rate": b_places, "A1 cost rate": r_places}
    )
    result = cmp.compare_pwbm(record)
    point = 100 * (Fraction(r) - Fraction(b)) / Fraction(b)
    assert result["point"] == point
    assert result["interval"]["lo"] <= point <= result["interval"]["hi"]
    if b_places >= 6 and r_places >= 6:
        assert result["interval"]["lo"] == result["interval"]["hi"]
    else:
        hb, hr = cmp.half_unit(b_places), cmp.half_unit(r_places)
        corners = [
            cmp.pwbm_statistic(Fraction(b) + sb * hb, Fraction(r) + sr * hr)
            for sb in (-1, 1)
            for sr in (-1, 1)
        ]
        assert result["interval"] == {"lo": min(corners), "hi": max(corners)}
        assert result["monotonicity_check"]["within_corner_bounds"]


def test_pwbm_null_value_is_reported():
    record = invented_record()
    record["pwbm"]["row_2030"]["A1 cost rate"] = None
    result = cmp.compare_pwbm(record)
    assert result["defined"] is False
    assert result["undefined_reason"]


# ---- MINT5 ---------------------------------------------------------------


def test_reading_s_shortest_form_of_a_seventeen_digit_expansion():
    cell = mint_cell("-14.2", raw="-0.14199999999999999")
    result = cmp.compare_mint_band(cell)
    s = result["reading_s"]
    assert s["shortest_repr"] == "-0.142"
    assert s["value_percent_units"] == Decimal("-14.2")
    assert s["decimals"] == 1
    assert s["stores_more_decimals_than_display"] is False
    assert result["registered"]["branch"] == "html"
    assert result["registered"]["interval"] == {
        "lo": Fraction(-1425, 100),
        "hi": Fraction(-1415, 100),
    }


def test_reading_s_xlsx_branch_when_more_decimals_round_to_display():
    result = cmp.compare_mint_band(mint_cell("-14.3", raw="-0.14251"))
    assert result["reading_s"]["decimals"] == 3
    assert result["reading_s"]["modes_agree"] is True
    assert result["registered"]["branch"] == "xlsx"
    assert result["registered"]["point"] == Fraction(-14251, 1000)
    assert result["registered"]["half_width"] == Fraction(1, 2000)


def test_rounding_modes_that_disagree_are_reported_with_both_branches():
    result = cmp.compare_mint_band(mint_cell("-14.3", raw="-0.1425"))
    s = result["reading_s"]
    assert s["half_up_rounds_to_display"] is True
    assert s["half_even_rounds_to_display"] is False
    assert s["modes_agree"] is False
    assert result["registered"]["branch"] == "xlsx"
    assert result["rounding_modes_disagree"] == {
        "branch_if_half_up_only": "xlsx",
        "branch_if_half_even_only": "html",
    }


def test_stored_value_that_does_not_round_to_display_uses_html():
    result = cmp.compare_mint_band(mint_cell("-14.2", raw="-0.1436"))
    assert result["reading_s"]["rounds_to_display"] is False
    assert result["registered"]["branch"] == "html"


@pytest.mark.parametrize(
    ("fmt", "percent"),
    [
        ("0.0%", True),
        ("0.0%;-0.0%", True),
        ('0.0"%"', False),
        ("0.0\\%", False),
        ("General", False),
        ("[Red]0.0%", True),
    ],
)
def test_percent_format_detection_ignores_quoted_and_escaped_signs(
    fmt, percent
):
    assert (cmp.percent_signs(fmt, Decimal("-0.1")) == 1) is percent


def test_non_percent_format_reads_the_stored_value_as_percent_units():
    result = cmp.compare_mint_band(mint_cell("-14.3", raw="-14.25", fmt="0.0"))
    assert result["reading_s"]["value_percent_units"] == Decimal("-14.25")
    assert result["reading_s"]["percent_format"] is False


def test_exponent_notation_and_null_xlsx_are_handled():
    exp = cmp.compare_mint_band(mint_cell("-14.3", raw="-1.4251E-1"))
    assert exp["reading_s"]["value_percent_units"] == Decimal("-14.251")
    missing = cmp.compare_mint_band(mint_cell("-14.3", raw=None))
    assert missing["reading_s"]["available"] is False
    assert missing["registered"]["branch"] == "html"
    unknown = cmp.compare_mint_band(mint_cell("-14.3", raw="-0.1", fmt=None))
    # A null format is not a percent format: the value is Decimal(s), whose
    # units then cannot round to the display, so the HTML branch follows.
    assert unknown["reading_s"]["number_format_recorded"] is False
    assert unknown["reading_s"]["percent_format"] is False
    assert unknown["reading_s"]["value_percent_units"] == Decimal("-0.1")
    assert unknown["registered"]["branch"] == "html"
    literal = cmp.compare_mint_band(mint_cell("-14.3", raw="-14.25", fmt=None))
    assert literal["registered"]["branch"] == "xlsx"


def test_reading_l_is_a_separate_sensitivity():
    cell = mint_cell(
        "-14.2",
        raw="-0.14199999999999999",
        literal=("-14.199999999999999", 15),
    )
    result = cmp.compare_mint_band(cell)
    assert result["registered"]["branch"] == "html"
    assert result["sensitivity_reading_l"]["branch"] == "xlsx"
    assert result["sensitivity_reading_l"]["half_width"] == cmp.half_unit(15)


@given(st.integers(-300000, -1), st.integers(1, 3))
@settings(max_examples=200, deadline=None)
def test_registered_band_interval_contains_its_point(raw_e5, places):
    raw = Decimal(raw_e5).scaleb(-5)
    percent = raw.scaleb(2)
    display = percent.quantize(Decimal(1).scaleb(-places))
    cell = mint_cell(str(display), decimals=places, raw=str(raw))
    result = cmp.compare_mint_band(cell)
    registered = result["registered"]
    assert (
        registered["interval"]["lo"]
        <= registered["point"]
        <= registered["interval"]["hi"]
    )
    assert registered["interval"]["hi"] - registered["interval"]["lo"] == (
        2 * registered["half_width"]
    )
    s = result["reading_s"]
    expected_xlsx = s["decimals"] > places and s["rounds_to_display"]
    assert (registered["branch"] == "xlsx") is expected_xlsx


@pytest.mark.parametrize(
    ("median_type", "headline", "beside"),
    [
        (
            "median_of_individual_differences",
            ["median_individual_pct_change"],
            ["difference_of_weighted_medians_pct"],
        ),
        (
            "difference_of_medians",
            ["difference_of_weighted_medians_pct"],
            ["median_individual_pct_change"],
        ),
        (
            "unsettled",
            [],
            [
                "median_individual_pct_change",
                "difference_of_weighted_medians_pct",
            ],
        ),
    ],
)
def test_headline_follows_the_recorded_median_type(
    median_type, headline, beside
):
    record = invented_record(**{"mint5.median_type": median_type})
    mint = cmp.compare_mint(record)
    assert mint["headline_statistics"] == headline
    assert mint["compared_beside"] == beside


def test_start_date_mismatch_is_reported_and_rows_never_swap():
    record = invented_record(**{"mint5.start_date_reading": "M1"})
    mint = cmp.compare_mint(record)
    assert "never swapped" in mint["start_date_note"]


# ---- dilution and split --------------------------------------------------


@pytest.mark.parametrize(
    ("admin", "railroad", "dilution"),
    [
        ("yes", "yes", "toward zero from administrative expenses"),
        ("yes", "no", "toward zero"),
        ("no", "no", "none"),
        ("not_stated", "yes", "unsigned"),
        ("yes", "not_stated", "unsigned"),
        (None, None, "unsigned"),
    ],
)
def test_not_stated_makes_the_dilution_unsigned(admin, railroad, dilution):
    assert cmp.flag_dilution(admin, railroad)["dilution"].startswith(dilution)


def test_split_is_compared_only_where_the_comparator_prints_one():
    model = {"P_OASI": {"mean": None}, "P_DI": {"mean": None}}
    assert cmp.split_block({"prints_oasi_di_split_2030": False}, model)[
        "note"
    ] == ("not printed by the comparator")
    flagged = cmp.split_block({"prints_oasi_di_split_2030": True}, model)
    assert flagged["printed"] is True
    assert "carries no split fields" in flagged["note"]


# ---- seal and artifact guards ---------------------------------------------


def test_seal_mismatch_refuses_before_any_comparison(tmp_path):
    seal_path = write_sealed(tmp_path)
    (
        seal_path.parent / "acola-comparator-20260930/sources/invented.html"
    ).write_bytes(b"CHANGED")
    with pytest.raises(cmp.SealError, match="differs from the seal"):
        cmp.run(
            seal_path=seal_path,
            artifact_path=write_artifact(tmp_path),
            allow_invented=True,
        )


@pytest.mark.parametrize("problem", ["missing", "bytes", "escape", "empty"])
def test_seal_refuses_missing_resized_escaping_or_empty(tmp_path, problem):
    seal_path = write_sealed(tmp_path)
    seal = json.loads(seal_path.read_text())
    if problem == "missing":
        (
            seal_path.parent
            / "acola-comparator-20260930/sources/invented.html"
        ).unlink()
    elif problem == "bytes":
        entry_ = seal["files"][
            "acola-comparator-20260930/sources/invented.html"
        ]
        entry_["bytes"] += 1
    elif problem == "escape":
        seal["files"]["../outside.txt"] = {"sha256": "0" * 64, "bytes": 0}
    else:
        seal["files"] = {}
    seal_path.write_text(json.dumps(seal))
    with pytest.raises(cmp.SealError):
        cmp.verify_seal(seal_path)


def test_unsealed_record_is_refused(tmp_path):
    seal_path = write_sealed(tmp_path)
    seal = json.loads(seal_path.read_text())
    del seal["files"]["acola-comparator-20260930/reconciled.json"]
    seal_path.write_text(json.dumps(seal))
    with pytest.raises(cmp.SealError, match="not sealed"):
        cmp.run(
            seal_path=seal_path,
            artifact_path=write_artifact(tmp_path),
            allow_invented=True,
        )


def test_seal_reports_its_own_hash_and_unlisted_files(tmp_path):
    seal_path = write_sealed(tmp_path)
    (seal_path.parent / "acola-comparator-20260930/unsealed.txt").write_text(
        INVENTED
    )
    result = cmp.run(
        seal_path=seal_path,
        artifact_path=write_artifact(tmp_path),
        allow_invented=True,
    )
    assert (
        result["seal"]["sha256"]
        == hashlib.sha256(seal_path.read_bytes()).hexdigest()
    )
    assert result["record_file"]["unlisted_files_beside_record"] == [
        "acola-comparator-20260930/unsealed.txt"
    ]
    assert result["record"]["sources_check"]["sources/invented.html"]["sealed"]


def test_artifact_must_match_its_sidecar(tmp_path):
    path = write_artifact(tmp_path)
    path.write_text(path.read_text().replace("report-only", "REPORT-ONLY"))
    with pytest.raises(cmp.ArtifactError, match="sidecar"):
        cmp.verify_artifact(path, allow_invented=True)


def test_invented_artifact_needs_the_explicit_flag(tmp_path):
    path = write_artifact(tmp_path)
    with pytest.raises(cmp.ArtifactError, match="allow-invented"):
        cmp.verify_artifact(path)
    _, summary = cmp.verify_artifact(path, allow_invented=True)
    assert summary["invented"] is True


@pytest.mark.parametrize(
    "change",
    [
        {"registration_pointer": "https://example.invalid/INVENTED"},
        {"run": {"git_clean": False}},
    ],
)
def test_a_registered_artifact_must_carry_the_pointer_and_clean_tree(
    tmp_path, change
):
    # INVENTED rows relabelled only to exercise the registered-run guard.
    artifact = invented_artifact(provenance="registered_real", **change)
    with pytest.raises(cmp.ArtifactError):
        cmp.verify_artifact(write_artifact(tmp_path, artifact))


def test_wrong_record_schema_is_refused(tmp_path):
    with pytest.raises(cmp.RecordError, match="schema"):
        run_compare(
            tmp_path, record=invented_record(schema_version="INVENTED")
        )


# ---- the whole comparison on the stage-1 layout ---------------------------


def test_every_registered_row_and_gap_on_the_stage1_layout(tmp_path):
    result = run_compare(tmp_path)
    assert result["header"] == cmp.INVENTED_HEADER
    assert set(result["rows"]) == set(REGISTERED_ROWS)
    assert result["rows"]["C0-D"]["status"] == "deferred"
    assert result["rows"]["C0-D"]["recorded_in_artifact"] is True
    artifact = json.loads(
        (tmp_path / "artifact.json").read_text(), parse_float=Decimal
    )
    nulls = result["nulls"]
    for name in ("N", "N_model", "N_MINT", "N_M1"):
        assert nulls[name]["recomputed_matches"] is True
        assert nulls[name]["years_match_registration"] is True
    oact = result["comparators"]["OACT"]
    for row_id in ("C0", "C1"):
        row = result["rows"][row_id]
        p = Fraction(artifact["rows"][row_id]["statistics"]["P"]["mean"])
        assert row["model"]["P"]["mean"] == p
        block = row["comparators"]["OACT"]
        assert block["model_minus_comparator"] == {
            "lo": p - oact["interval"]["hi"],
            "hi": p - oact["interval"]["lo"],
        }
        assert block["N_minus_comparator"] == {
            "lo": nulls["N"]["value"] - oact["interval"]["hi"],
            "hi": nulls["N"]["value"] - oact["interval"]["lo"],
        }
        assert row["P_minus_N"] == p - nulls["N"]["value"]
        assert row["P_minus_N_model"] == p - nulls["N_model"]["value"]
        assert row["comparators"]["PWBM"]["oasi_di_split"]["printed"] is False
        sd = artifact["rows"][row_id]["statistics"]["P"]["sample_sd"]
        assert row["model"]["P"]["draw_sd"] == Fraction(sd)
    for row_id in ("M0", "M1", "M2", "M3", "M4"):
        row = result["rows"][row_id]
        assert row["null"] == ("N_M1" if row_id == "M1" else "N_MINT")
        assert set(row["bands"]) == set(cmp.MINT_BANDS)
        for band, entry_ in row["bands"].items():
            headline = entry_["median_individual_pct_change"]
            assert headline["role"] == "headline"
            assert entry_["difference_of_weighted_medians_pct"]["role"] == (
                "beside"
            )
            mean = headline["model"]["mean"]
            c = result["comparators"]["MINT5"]["bands"][band]["registered"]
            if mean is None:
                assert headline["model_minus_comparator"] is None
            else:
                assert headline["model_minus_comparator"] == {
                    "lo": mean - c["interval"]["hi"],
                    "hi": mean - c["interval"]["lo"],
                }
    json.dumps(cmp.to_json(result), allow_nan=False)


def test_main_writes_json_and_markdown_once(tmp_path, capsys):
    seal_path = write_sealed(tmp_path)
    artifact = write_artifact(tmp_path)
    out_json, out_md = tmp_path / "c.json", tmp_path / "c.md"
    argv = [
        "--seal",
        str(seal_path),
        "--artifact",
        str(artifact),
        "--output-json",
        str(out_json),
        "--output-md",
        str(out_md),
        "--allow-invented",
    ]
    assert cmp.main(argv) == 0
    printed = capsys.readouterr().out
    seal_sha = hashlib.sha256(seal_path.read_bytes()).hexdigest()
    assert f"seal SHA-256 {seal_sha}" in printed
    written = json.loads(out_json.read_text())
    assert written["verdict"] is None and written["no_pass_band"] is True
    assert written["seal"]["sha256"] == seal_sha
    text = out_md.read_text()
    assert text.startswith("# " + cmp.INVENTED_HEADER)
    assert "| C0 | computed | OACT |" in text
    assert "| M1 | computed | 90+ |" in text
    assert "C0-D: registered but deferred" in text
    with pytest.raises(SystemExit, match="one-shot"):
        cmp.main(argv)


def test_null_fields_everywhere_serialize_with_reasons(tmp_path):
    record = invented_record()
    _column(record, "proposal_cost_rate")["value"] = None
    record["pwbm"]["row_2030"]["Baseline cost rate"] = None
    for band in cmp.MINT_BANDS:
        record["mint5"]["table1"]["rows"][band]["median_diff_pct"] = None
    record["mint5"]["median_type"] = None
    result = run_compare(tmp_path, record=record)
    for row_id in ("C0", "C1"):
        for block in result["rows"][row_id]["comparators"].values():
            assert block["comparator_interval"] is None
            assert block["undefined_reason"]
    band = result["rows"]["M0"]["bands"]["Total"]
    assert band["median_individual_pct_change"]["comparator_interval"] is None
    assert result["comparators"]["MINT5"]["median_type_recognized"] is False
    json.dumps(cmp.to_json(result), allow_nan=False)
    cmp.markdown(result)


def test_missing_row_is_reported_not_dropped(tmp_path):
    artifact = invented_artifact()
    del artifact["rows"]["M3"]
    result = run_compare(tmp_path, artifact=artifact)
    assert result["rows"]["M3"]["status"] == "missing"


def test_comparison_uses_no_constant_from_the_lane_records(tmp_path):
    """Flip every recorded flag; each output follows the record."""

    record = invented_record()
    record["oact"].update(
        prints_oasi_di_split_2030=True,
        cost_includes_admin_expenses="no",
        cost_includes_railroad_interchange="no",
    )
    record["oact"]["december_2030_timing"][
        "reading"
    ] = "counts_dec2030_at_reduced_dec2030_increase"
    record["mint5"]["median_type"] = "difference_of_medians"
    result = run_compare(tmp_path, record=record)
    c0 = result["rows"]["C0"]["comparators"]["OACT"]
    assert c0["oasi_di_split"]["printed"] is True
    assert c0["cost_definition"]["dilution"] == "none"
    assert c0["december_2030_timing"]["reading"].startswith("counts")
    band = result["rows"]["M0"]["bands"]["Total"]
    assert band["difference_of_weighted_medians_pct"]["role"] == "headline"


# ---- review fixes: identity, provenance and reporting ---------------------


def test_wrong_row_label_or_year_makes_the_comparator_undefined(tmp_path):
    record = invented_record()
    record["oact"]["row_label_verbatim"] = "2031"
    record["pwbm"]["row_2030"]["year"] = "2029"
    record["oact"]["footer_matches_registration"] = False
    record["pwbm"]["last_modified_matches_registration"] = False
    result = run_compare(tmp_path, record=record)
    assert result["comparators"]["OACT"]["defined"] is False
    assert result["comparators"]["PWBM"]["defined"] is False
    checks = result["identity_checks"]
    assert checks["all_true"] is False
    assert {
        "oact_footer_matches_registration",
        "oact_row_label_is_2030",
        "pwbm_last_modified_matches_registration",
        "pwbm_row_year_is_2030",
    } <= set(checks["failed"])
    text = cmp.markdown(result)
    assert "IDENTITY CHECK NOT MET" in text
    assert "oact_footer_matches_registration | False" in text
    c0 = result["rows"]["C0"]
    assert c0["primary_comparator"] == "PWBM"
    assert "OACT undefined" in c0["primary_reason"]


def test_identity_checks_all_hold_on_a_consistent_record(tmp_path):
    result = run_compare(tmp_path)
    assert result["identity_checks"]["all_true"] is True
    assert "All recorded identity checks hold." in cmp.markdown(result)


def test_record_bytes_changed_after_seal_verification_are_refused(
    tmp_path, monkeypatch
):
    seal_path = write_sealed(tmp_path)
    record = seal_path.parent / "acola-comparator-20260930/reconciled.json"
    original = cmp.verify_artifact

    def tamper(*args, **kwargs):
        changed = json.loads(record.read_text())
        _column(changed, "proposal_cost_rate")["value"] = "99.00"
        record.write_text(json.dumps(changed))
        return original(*args, **kwargs)

    monkeypatch.setattr(cmp, "verify_artifact", tamper)
    with pytest.raises(cmp.SealError, match="changed after the seal"):
        cmp.run(
            seal_path=seal_path,
            artifact_path=write_artifact(tmp_path),
            allow_invented=True,
        )


def test_a_single_transcription_is_never_the_compared_record(tmp_path):
    record = invented_record(producer="transcriber_a")
    with pytest.raises(cmp.RecordError, match="reconciled"):
        run_compare(tmp_path, record=record)


def test_a_sealed_record_off_the_registered_path_is_flagged(tmp_path):
    other = "acola-comparator-20260930/other.json"
    raw = json.dumps(invented_record()).encode()
    seal_path = write_sealed(tmp_path, extra={other: raw})
    result = cmp.run(
        seal_path=seal_path,
        artifact_path=write_artifact(tmp_path),
        record_path=seal_path.parent / other,
        allow_invented=True,
    )
    assert result["record_file"]["is_registered_path"] is False
    assert "not at the registered path" in cmp.markdown(result)


def test_registered_comparison_pins_the_recorded_seal_hash(tmp_path):
    seal_path = write_sealed(tmp_path)
    # INVENTED rows relabelled only to exercise the registered-run guard.
    artifact = write_artifact(
        tmp_path, invented_artifact(provenance="registered_real")
    )
    with pytest.raises(cmp.SealError, match="not the expected"):
        cmp.run(seal_path=seal_path, artifact_path=artifact)
    actual = hashlib.sha256(seal_path.read_bytes()).hexdigest()
    result = cmp.run(
        seal_path=seal_path,
        artifact_path=artifact,
        expected_seal_sha256=actual,
    )
    assert result["header"] == cmp.REGISTERED_HEADER
    assert result["seal"]["expected_sha256"] == actual
    with pytest.raises(cmp.SealError, match="not the expected"):
        cmp.run(
            seal_path=seal_path,
            artifact_path=artifact,
            allow_invented=True,
            expected_seal_sha256="0" * 64,
        )


def test_refusals_status_and_labels_reach_both_outputs(tmp_path):
    artifact = invented_artifact()
    artifact["rows"]["C0"]["status"] = "refused"
    artifact["rows"]["C0"]["refusals"] = [
        {"draw": 3, "reason": "INVENTED REFUSE", "error_type": "ValueError"}
    ]
    artifact["rows"]["M2"]["tabulation_refusal"] = {
        "reason": "INVENTED tabulation",
        "error_type": "ColaTabulationError",
    }
    result = run_compare(tmp_path, artifact=artifact)
    assert result["rows"]["C0"]["status"] == "refused"
    assert result["rows"]["C0"]["refusals"][0]["reason"] == "INVENTED REFUSE"
    assert result["rows"]["M2"]["tabulation_refusal"]["reason"] == (
        "INVENTED tabulation"
    )
    text = cmp.markdown(result)
    assert "| C0 | refused | OACT |" in text
    assert "C0, draw 3: ValueError: INVENTED REFUSE" in text
    assert "M2, tabulation: ColaTabulationError" in text
    assert "INVENTED, report-only" in text


def test_oact_string_count_alternative_is_guarded_at_every_corner():
    record = invented_record()
    _column(record, "proposal_cost_rate").update(value="0.6", decimals=2)
    _column(record, "change_cost_rate").update(value="0.5", decimals=2)
    result = cmp.compare_oact(record)
    assert result["defined"] is True
    alternative = result["alternative_interval_from_string_decimals"]
    assert alternative["defined"] is False
    assert "every corner" in alternative["undefined_reason"]


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_json_tokens_are_refused_at_load(token):
    raw = '{"schema_version": "acola-comparator-v1", "x": ' + token + "}"
    with pytest.raises(cmp.RecordError, match="non-finite"):
        cmp.load_json_exact(raw.encode())


def test_absent_null_and_unrecognized_band_keys_are_told_apart():
    record = invented_record()
    rows = record["mint5"]["table1"]["rows"]
    rows["62\u201369"] = rows.pop("62-69")
    rows["70-79"]["median_diff_pct"] = None
    rows["80-89"]["median_diff_pct"]["html_value"] = None
    mint = cmp.compare_mint(record)
    assert mint["bands"]["62-69"]["undefined_reason"] == (
        "the band is absent from the record"
    )
    assert mint["bands"]["70-79"]["undefined_reason"] == (
        "median_diff_pct is null"
    )
    assert "HTML value is null" in mint["bands"]["80-89"]["undefined_reason"]
    assert mint["unrecognized_band_keys"] == ["62\u201369"]


def test_unsettled_median_type_compares_both_with_no_headline(tmp_path):
    record = invented_record(**{"mint5.median_type": "unsettled"})
    band = run_compare(tmp_path, record=record)["rows"]["M0"]["bands"]["Total"]
    assert band["median_individual_pct_change"]["role"] == (
        "compared, no headline"
    )
    assert band["difference_of_weighted_medians_pct"]["role"] == (
        "compared, no headline"
    )
    assert band["ratio_of_scenario_means"]["role"] == "beside"


@given(fractions, fractions)
@settings(max_examples=200, deadline=None)
def test_rendered_interval_ends_round_outward(a, b):
    lo, hi = sorted((a / 7, b / 7))
    shown = cmp.to_json({"interval": cmp.interval(lo, hi)})["interval"]
    assert Fraction(Decimal(shown["lo"])) <= lo
    assert Fraction(Decimal(shown["hi"])) >= hi
