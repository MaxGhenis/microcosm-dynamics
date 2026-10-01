#!/usr/bin/env python3
"""Registration 18 (A-COLA): compare the run artifact with the sealed record.

For the validation-only comparison lane, after the run artifact has merged
(issue #42, Registration 18, decision d658). Standard library only. The
script holds no comparator value and fetches nothing.

Order of work, each step refusing before the next starts:

1. **Seal.** Hash every file the seal lists (``files: {path relative to
   the evidence folder: {sha256, bytes}}``) and refuse on any mismatch,
   missing file or path outside the folder. Print the seal's own SHA-256.
   The comparator record must be one of the sealed files.
2. **Artifact.** Refuse unless the artifact's SHA-256 equals its
   ``.env.json`` sidecar's ``artifact_sha256`` and the sidecar names it.
   An artifact that is not ``registered_real`` is refused unless
   ``--allow-invented`` is passed; the output then says INVENTED DATA.
3. **Record.** Schema ``acola-comparator-v1``. Every value is parsed from
   its string with ``decimal.Decimal`` (the artifact too, with
   ``parse_float=Decimal``), and all arithmetic is exact rational
   arithmetic with ``fractions.Fraction``. ``null`` fields are reported
   with a reason, never guessed.
4. **Comparisons**, as Registration 18 registers them ("Comparators",
   "Spec-only null", "What is reported"):

   * OACT: C = 100 d / (p - d), with p and d each +/- half their last
     printed unit (from the record's ``decimals``), C over the four
     corners, p - d > 0 asserted at every corner; the precision gate
     (|p| or |d| below 0.10 makes PWBM primary).
   * PWBM: C = 100 (R - B) / B; a point when both stored values carry six
     or more decimals, otherwise the four corners.
   * MINT5: per band, the registered reading S of the XLSX stored value
     (``repr(float(xlsx_raw))``, shifted to percent units under a percent
     number format), half-up and half-even rounding checks against the
     HTML display, the XLSX or HTML branch, and reading L (the record's
     literal counts) as a sensitivity. The headline statistic follows the
     record's ``median_type``.
   * Gaps: P - C and N - C as intervals, P - N and P - N_model, with
     interval subtraction [a, b] - [c, d] = [a - d, b - c]. The MINT5 rows
     use N_MINT (M1: its own null). The model's mean, draw SD and floor
     stand beside every comparator and gap.
   * The OASI and DI split only where a comparator prints one; December
     2030 timing and the cost-definition flags beside each comparison
     (``not_stated`` makes the dilution unsigned).

There is no pass band and no verdict. The output is one JSON file and one
markdown file, both created exclusively, with every number exactly as
computed: a terminating decimal expansion is written in full, any other
rational to 20 significant digits (ROUND_HALF_EVEN).

Usage (comparison lane only)::

    python scripts/compare_acola.py \\
        --seal EV/acola-comparator-seal-20260930.json \\
        --artifact runs/trust_fund_acola_2030_v1.json \\
        --output-json <lane folder>/comparison.json \\
        --output-md <lane folder>/COMPARISON.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import (
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    Decimal,
    InvalidOperation,
    localcontext,
)
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "populace_dynamics.acola_track.compare.v1"
RECORD_SCHEMA = "acola-comparator-v1"
RECORD_RELATIVE = "acola-comparator-20260930/reconciled.json"
DEFAULT_ARTIFACT = ROOT / "runs" / "trust_fund_acola_2030_v1.json"
REGISTRATION_POINTER = (
    "https://github.com/PolicyEngine/microcosm-dynamics/issues/42"
    "#issuecomment-5919983573"
)
REGISTERED_REAL = "registered_real"
INVENTED_HEADER = "INVENTED DATA - NOT A COMPARISON"
REGISTERED_HEADER = (
    "A-COLA comparison, Registration 18 (d658). Report-only: no pass "
    "band and no verdict."
)
OACT_FOOTER = "Based on Intermediate Assumptions of the 2026 Trustees Report"
OACT_P, OACT_D = "proposal_cost_rate", "change_cost_rate"
OACT_MEMO = ("proposal_income_rate", "change_income_rate")
PWBM_B, PWBM_R = "Baseline cost rate", "A1 cost rate"
PWBM_MEMO = ("Baseline income rate", "A1 income rate")
PWBM_POINT_DECIMALS = 6
PRECISION_GATE = Fraction(1, 10)
COST_ROWS = ("C0", "C1")
DEFERRED_ROWS = ("C0-D",)
MINT_ROWS = ("M0", "M1", "M2", "M3", "M4")
MINT_BANDS = ("Total", "62-69", "70-79", "80-89", "90+")
MINT_MEMO_FIELDS = (
    "median_diff_dollars",
    "median_monthly_scheduled",
    "median_monthly_option",
    "median_monthly_payable",
    "pct_population_affected",
)
MEDIAN_OF_DIFFERENCES = "median_individual_pct_change"
DIFFERENCE_OF_MEDIANS = "difference_of_weighted_medians_pct"
RATIO_OF_MEANS = "ratio_of_scenario_means"
MINT_COMPARED = (MEDIAN_OF_DIFFERENCES, DIFFERENCE_OF_MEDIANS, RATIO_OF_MEANS)
HEADLINE_BY_MEDIAN_TYPE = {
    "median_of_individual_differences": (
        (MEDIAN_OF_DIFFERENCES,),
        (DIFFERENCE_OF_MEDIANS,),
    ),
    "difference_of_medians": (
        (DIFFERENCE_OF_MEDIANS,),
        (MEDIAN_OF_DIFFERENCES,),
    ),
    "unsettled": ((), (MEDIAN_OF_DIFFERENCES, DIFFERENCE_OF_MEDIANS)),
}
ROW_TIMING = {
    "C0": "calendar-2030 payments: increases determined through 2029",
    "C1": (
        "December 2030 amount x 12: includes the increase effective "
        "December 2030"
    ),
    "M0": "calendar-2030 payments; first reduced increase determined 2011",
    "M1": "calendar-2030 payments; first reduced increase determined 2010",
    "M2": (
        "December 2030 amount x 12; first reduced increase determined "
        "2011; includes the increase effective December 2030"
    ),
    "M3": "M0 on the entitlement exposure clock",
    "M4": "M0 with age = 2030 - birth year - 1",
}
ROW_NULL = {
    "C0": "N",
    "C1": "N",
    "M0": "N_MINT",
    "M1": "N_M1",
    "M2": "N_MINT",
    "M3": "N_MINT",
    "M4": "N_MINT",
}
NULL_YEARS = {
    "N": (2027, 2029),
    "N_model": (2027, 2029),
    "N_MINT": (2011, 2029),
    "N_M1": (2010, 2029),
}
RENDER_DIGITS = 20


class SealError(ValueError):
    """The seal, a sealed file or the record's place in the seal is wrong."""


class ArtifactError(ValueError):
    """The run artifact or its sidecar cannot be trusted as the run."""


class RecordError(ValueError):
    """The comparator record does not have the registered schema."""


# ---- exact numbers -----------------------------------------------------


def render(value: Fraction | None) -> str | None:
    """A terminating decimal in full; otherwise 20 significant digits."""

    if value is None:
        return None
    value = Fraction(value)
    if value == 0:
        return "0"
    with localcontext() as context:
        context.prec = 80
        exact = Decimal(value.numerator) / Decimal(value.denominator)
    if Fraction(exact) == value:
        text = format(exact, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text
    with localcontext() as context:
        context.prec = RENDER_DIGITS
        context.rounding = ROUND_HALF_EVEN
        rounded = Decimal(value.numerator) / Decimal(value.denominator)
    return (
        format(rounded, "f") if abs(rounded.adjusted()) < 30 else str(rounded)
    )


def parse_decimal(value: Any, label: str) -> Decimal:
    """A finite Decimal from a recorded string (or an artifact Decimal)."""

    if isinstance(value, bool) or value is None:
        raise RecordError(f"{label}: expected a decimal, got {value!r}")
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        if value != value.strip() or not value:
            raise RecordError(f"{label}: {value!r} is not a bare decimal")
        try:
            number = Decimal(value)
        except InvalidOperation as error:
            raise RecordError(f"{label}: {value!r} is not a decimal") from (
                error
            )
    else:
        raise RecordError(
            f"{label}: {type(value).__name__} is not a recorded decimal; "
            "values must be strings, never floats"
        )
    if not number.is_finite():
        raise RecordError(f"{label}: {value!r} is not finite")
    return number


def decimals_of(number: Decimal) -> int:
    """Digits after the point as written (never negative)."""

    return max(0, -number.as_tuple().exponent)


def shortest_decimals(number: Decimal) -> int:
    """Digits after the point of the shortest form (never negative)."""

    return max(0, -number.normalize().as_tuple().exponent)


def half_unit(decimals: int) -> Fraction:
    if isinstance(decimals, bool) or not isinstance(decimals, int):
        raise RecordError(f"a decimal count must be an integer: {decimals!r}")
    if decimals < 0:
        raise RecordError("a decimal count cannot be negative")
    return Fraction(1, 2 * 10**decimals)


def interval(lo: Fraction, hi: Fraction) -> dict[str, Any]:
    if lo > hi:
        raise ValueError("an interval's lower end exceeds its upper end")
    return {"lo": lo, "hi": hi}


def point_interval(value: Fraction) -> dict[str, Any]:
    return interval(value, value)


def subtract(a: dict | Fraction, b: dict | Fraction) -> dict | Fraction:
    """Interval arithmetic: [a, b] - [c, d] = [a - d, b - c]."""

    if isinstance(a, Fraction) and isinstance(b, Fraction):
        return a - b
    a = point_interval(a) if isinstance(a, Fraction) else a
    b = point_interval(b) if isinstance(b, Fraction) else b
    return interval(a["lo"] - b["hi"], a["hi"] - b["lo"])


def four_corner(
    function, x: Fraction, hx: Fraction, y: Fraction, hy: Fraction
):
    """The minimum and maximum of ``function`` over the four corners."""

    corners = [(x + sx * hx, y + sy * hy) for sx in (-1, 1) for sy in (-1, 1)]
    values = [function(cx, cy) for cx, cy in corners]
    return corners, interval(min(values), max(values))


def grid_check(function, x, hx, y, hy, bounds, steps: int = 8) -> dict:
    """Evaluate a (steps+1)^2 grid over the box against the corner bounds.

    The registration relies on monotonicity for the corners to bound the
    statistic; this verifies it numerically on the actual box.
    """

    inside = True
    for i in range(steps + 1):
        for j in range(steps + 1):
            cx = x - hx + 2 * hx * Fraction(i, steps)
            cy = y - hy + 2 * hy * Fraction(j, steps)
            value = function(cx, cy)
            if not bounds["lo"] <= value <= bounds["hi"]:
                inside = False
    return {"grid_points": (steps + 1) ** 2, "within_corner_bounds": inside}


def oact_statistic(p: Fraction, d: Fraction) -> Fraction:
    return 100 * d / (p - d)


def pwbm_statistic(b: Fraction, r: Fraction) -> Fraction:
    return 100 * (r - b) / b


# ---- verification ------------------------------------------------------


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _relative(path_text: str) -> PurePosixPath:
    relative = PurePosixPath(path_text)
    if (
        not path_text
        or relative.is_absolute()
        or any(part in ("..", "") for part in relative.parts)
        or "\\" in path_text
    ):
        raise SealError(f"sealed path {path_text!r} is not a plain relative")
    return relative


def verify_seal(seal_path: Path, root: Path | None = None) -> dict[str, Any]:
    """Check every sealed file's SHA-256 and size; refuse on any mismatch."""

    seal_path = Path(seal_path)
    raw = seal_path.read_bytes()
    seal_sha256 = sha256_bytes(raw)
    seal = json.loads(raw)
    files = seal.get("files") if isinstance(seal, dict) else None
    if not isinstance(files, dict) or not files:
        raise SealError("the seal lists no files")
    root = Path(root) if root is not None else seal_path.parent
    resolved_root = root.resolve()
    problems = []
    for path_text, entry in sorted(files.items()):
        relative = _relative(path_text)
        if not isinstance(entry, dict):
            problems.append(f"{path_text}: entry is not an object")
            continue
        digest, size = entry.get("sha256"), entry.get("bytes")
        if not (
            isinstance(digest, str)
            and len(digest) == 64
            and all(ch in "0123456789abcdef" for ch in digest)
        ):
            problems.append(f"{path_text}: sealed sha256 is malformed")
            continue
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            problems.append(f"{path_text}: sealed byte count is malformed")
            continue
        target = root.joinpath(*relative.parts)
        try:
            target.resolve().relative_to(resolved_root)
        except ValueError:
            problems.append(f"{path_text}: resolves outside the folder")
            continue
        if not target.is_file():
            problems.append(f"{path_text}: missing")
            continue
        data = target.read_bytes()
        if len(data) != size:
            problems.append(f"{path_text}: {len(data)} bytes, sealed {size}")
        if sha256_bytes(data) != digest:
            problems.append(f"{path_text}: SHA-256 differs from the seal")
    if problems:
        raise SealError(
            "refusing to compare; the seal does not verify:\n  "
            + "\n  ".join(problems)
        )
    return {
        "path": str(seal_path),
        "sha256": seal_sha256,
        "root": str(root),
        "n_files": len(files),
        "verified": True,
        "files": files,
    }


def verify_record_is_sealed(
    seal: dict[str, Any], record_path: Path
) -> dict[str, Any]:
    root = Path(seal["root"]).resolve()
    try:
        relative = Path(record_path).resolve().relative_to(root).as_posix()
    except ValueError as error:
        raise SealError("the comparator record lies outside the seal") from (
            error
        )
    if relative not in seal["files"]:
        raise SealError(f"the comparator record {relative} is not sealed")
    record_dir = Path(record_path).resolve().parent
    listed = {
        str(root.joinpath(*PurePosixPath(p).parts)) for p in seal["files"]
    }
    unlisted = sorted(
        path.relative_to(root).as_posix()
        for path in record_dir.rglob("*")
        if path.is_file() and str(path) not in listed
    )
    return {
        "path": relative,
        "sha256": seal["files"][relative]["sha256"],
        "unlisted_files_beside_record": unlisted,
    }


def load_json_exact(raw: bytes) -> Any:
    """JSON with every float literal kept as the Decimal it prints."""

    return json.loads(raw, parse_float=Decimal)


def verify_artifact(
    artifact_path: Path, *, allow_invented: bool = False
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Check the artifact against its sidecar, then its registered fields."""

    artifact_path = Path(artifact_path)
    raw = artifact_path.read_bytes()
    digest = sha256_bytes(raw)
    sidecar_path = artifact_path.with_suffix(".env.json")
    if not sidecar_path.is_file():
        raise ArtifactError(f"the sidecar {sidecar_path.name} is missing")
    sidecar = json.loads(sidecar_path.read_bytes())
    if sidecar.get("artifact") != artifact_path.name:
        raise ArtifactError("the sidecar names a different artifact")
    if sidecar.get("artifact_sha256") != digest:
        raise ArtifactError(
            "the artifact's SHA-256 differs from its sidecar's record"
        )
    artifact = load_json_exact(raw)
    provenance = artifact.get("data_provenance")
    invented = provenance != REGISTERED_REAL
    if invented and not allow_invented:
        raise ArtifactError(
            f"the artifact's data provenance is {provenance!r}, not "
            "registered_real; pass --allow-invented only for a dry run"
        )
    run = artifact.get("run") or {}
    if not invented:
        if artifact.get("registration_pointer") != REGISTRATION_POINTER:
            raise ArtifactError("the artifact is not Registration 18's run")
        if run.get("git_clean") is not True:
            raise ArtifactError("the artifact does not record a clean tree")
    summary = {
        "path": str(artifact_path),
        "sha256": digest,
        "sidecar": sidecar_path.name,
        "sidecar_sha256": sha256_bytes(sidecar_path.read_bytes()),
        "sidecar_matches": True,
        "invented": invented,
        "data_provenance": provenance,
        "registration_pointer": artifact.get("registration_pointer"),
        "registered_commit": run.get("registered_commit"),
        "git_head": run.get("git_head"),
        "git_clean": run.get("git_clean"),
        "publishes_regardless": artifact.get("publishes_regardless"),
        "comparator_seal_opened_before_commit": artifact.get(
            "comparator_seal_opened_before_commit"
        ),
        "labels": artifact.get("labels"),
        "schema_version": artifact.get("schema_version"),
    }
    return artifact, summary


# ---- the model side ----------------------------------------------------


def _fraction_or_none(value: Any) -> Fraction | None:
    if value is None:
        return None
    return Fraction(parse_decimal(value, "an artifact number"))


def model_summary(summary: dict | None, label: str) -> dict[str, Any]:
    """The mean, draw SD and floor, exactly as the artifact prints them."""

    if not isinstance(summary, dict):
        return {
            "statistic": label,
            "mean": None,
            "draw_sd": None,
            "floor": None,
            "undefined_reason": "statistic absent from the artifact",
        }
    floor = summary.get("floor") or {}
    return {
        "statistic": label,
        "mean": _fraction_or_none(summary.get("mean")),
        "draw_sd": _fraction_or_none(
            summary.get("sample_sd", summary.get("sd"))
        ),
        "n_draws": summary.get("n_draws"),
        "n_defined_draws": summary.get("n_defined_draws"),
        "floor": {
            "defined": floor.get("defined"),
            "mean": _fraction_or_none(floor.get("mean")),
            "sd": _fraction_or_none(floor.get("sd")),
            "min": _fraction_or_none(floor.get("min")),
            "max": _fraction_or_none(floor.get("max")),
            "n_seeds": floor.get("n_seeds"),
            "dropped_seeds": floor.get("dropped_seeds"),
            "undefined_reason": floor.get("undefined_reason"),
        },
        "undefined_reason": summary.get("undefined_reason")
        or (None if summary.get("mean") is not None else "mean undefined"),
    }


def null_values(artifact: dict[str, Any]) -> dict[str, Any]:
    """The posted nulls, exact, and each recomputed from its own rates."""

    nulls = artifact.get("nulls") or {}
    output = {}
    for name, (first, last) in NULL_YEARS.items():
        entry = nulls.get(name)
        if not isinstance(entry, dict):
            output[name] = {
                "value": None,
                "undefined_reason": "null absent from the artifact",
            }
            continue
        exact = entry.get("exact") or {}
        try:
            value = Fraction(
                int(exact["numerator"]), int(exact["denominator"])
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            value = _fraction_or_none(entry.get("value"))
        rates = entry.get("rates") or {}
        years = sorted(int(y) for y in rates)
        reduction_text = nulls.get("annual_reduction")
        if reduction_text is None or not rates:
            recomputed = None
        else:
            reduction = Fraction(
                parse_decimal(str(reduction_text), "annual_reduction")
            )
            product = Fraction(1)
            for year in years:
                rate = Fraction(
                    parse_decimal(rates[str(year)], f"rate {year}")
                )
                product *= (1 + rate - reduction) / (1 + rate)
            recomputed = 100 * (product - 1)
        output[name] = {
            "value": value,
            "years": [first, last],
            "factor_count": len(years),
            "years_match_registration": (
                years == list(range(first, last + 1))
            ),
            "recomputed_from_recorded_rates": recomputed,
            "recomputed_matches": (
                None if recomputed is None else recomputed == value
            ),
            "source": entry.get("source"),
        }
    return output


# ---- comparators -------------------------------------------------------


def _column(record_oact: dict, key: str) -> dict | None:
    for column in record_oact.get("columns") or []:
        if isinstance(column, dict) and column.get("key") == key:
            return column
    return None


def _counted(
    value: Any, recorded: Any, label: str
) -> tuple[Decimal, int, dict[str, Any]]:
    """The value, the decimal count the rule uses, and a cross-check.

    The record's own count is used, as the registration requires. Where the
    record carries none, the count of the recorded string is used and the
    output says so; a count that disagrees with the string is reported.
    """

    number = parse_decimal(value, label)
    written = decimals_of(number)
    if recorded is None:
        return (
            number,
            written,
            {
                "recorded_decimals": None,
                "decimals_in_string": written,
                "decimals_consistent": None,
                "count_used": "string (the record carries no count)",
            },
        )
    if isinstance(recorded, bool) or not isinstance(recorded, int):
        raise RecordError(f"{label}: the recorded decimal count is malformed")
    if recorded < 0:
        raise RecordError(f"{label}: the recorded decimal count is negative")
    return (
        number,
        recorded,
        {
            "recorded_decimals": recorded,
            "decimals_in_string": written,
            "decimals_consistent": written == recorded,
            "count_used": "record",
        },
    )


def flag_dilution(admin: Any, railroad: Any) -> dict[str, Any]:
    """Registration 18 "Adjustments": not_stated makes the dilution unsigned."""

    effects = {}
    effects["administrative_expenses"] = {
        "yes": (
            "included and unchanged by the reform: dilutes the comparator's "
            "percent toward zero relative to a benefits-only P"
        ),
        "no": "not included: no dilution from administrative expenses",
        "not_stated": "not stated: unsigned",
    }.get(admin, f"unrecognized flag {admin!r}: unsigned")
    effects["railroad_retirement_interchange"] = {
        "yes": (
            "included: it may move with a benefit change, and the sources "
            "do not say in which direction"
        ),
        "no": "not included: no dilution from the interchange",
        "not_stated": "not stated: unsigned",
    }.get(railroad, f"unrecognized flag {railroad!r}: unsigned")
    if admin not in ("yes", "no") or railroad not in ("yes", "no"):
        overall = "unsigned"
    elif admin == "yes" and railroad == "yes":
        overall = (
            "toward zero from administrative expenses; the interchange "
            "part is of unstated direction"
        )
    elif admin == "yes":
        overall = "toward zero"
    elif railroad == "yes":
        overall = "interchange only, of unstated direction"
    else:
        overall = "none"
    return {
        "cost_includes_admin_expenses": admin,
        "cost_includes_railroad_interchange": railroad,
        "effects": effects,
        "dilution": overall,
    }


def compare_oact(record: dict[str, Any]) -> dict[str, Any]:
    oact = record.get("oact")
    if not isinstance(oact, dict):
        return {"defined": False, "undefined_reason": "no oact record"}
    output = {
        "footer_verbatim": oact.get("footer_verbatim"),
        "footer_matches_registration": oact.get("footer_matches_registration"),
        "footer_contains_registered_string": (
            isinstance(oact.get("footer_verbatim"), str)
            and OACT_FOOTER in oact["footer_verbatim"]
        ),
        "provision_text_matches_registration": oact.get(
            "provision_text_matches_registration"
        ),
        "row_label_verbatim": oact.get("row_label_verbatim"),
        "row_label_is_2030": oact.get("row_label_verbatim") == "2030",
        "columns_recorded": [
            {
                "key": c.get("key"),
                "header_verbatim": c.get("header_verbatim"),
                "display": c.get("display"),
            }
            for c in oact.get("columns") or []
            if isinstance(c, dict)
        ],
        "prints_oasi_di_split_2030": oact.get("prints_oasi_di_split_2030"),
        "oasi_di_split_2030_fields": oact.get("oasi_di_split_2030"),
        "december_2030_timing": oact.get("december_2030_timing"),
        "cost_definition": flag_dilution(
            oact.get("cost_includes_admin_expenses"),
            oact.get("cost_includes_railroad_interchange"),
        ),
        "memo_items": {
            key: _memo_column(_column(oact, key)) for key in OACT_MEMO
        },
    }
    columns = {key: _column(oact, key) for key in (OACT_P, OACT_D)}
    missing = [
        key
        for key, column in columns.items()
        if column is None or column.get("value") is None
    ]
    if missing:
        output.update(
            defined=False,
            undefined_reason=f"null or absent column(s): {missing}",
            precision_gate={
                "branch": "undefined",
                "reason": "an OACT column entering C is null",
                "primary": "PWBM",
            },
        )
        return output
    p_dec, p_places, p_check = _counted(
        columns[OACT_P]["value"], columns[OACT_P].get("decimals"), OACT_P
    )
    d_dec, d_places, d_check = _counted(
        columns[OACT_D]["value"], columns[OACT_D].get("decimals"), OACT_D
    )
    p, d = Fraction(p_dec), Fraction(d_dec)
    hp, hd = half_unit(p_places), half_unit(d_places)
    gate_trips = abs(p) < PRECISION_GATE or abs(d) < PRECISION_GATE
    output["precision_gate"] = {
        "threshold": PRECISION_GATE,
        "abs_p_below": abs(p) < PRECISION_GATE,
        "abs_d_below": abs(d) < PRECISION_GATE,
        "branch": (
            "gate tripped: PWBM primary, OACT report-only"
            if gate_trips
            else "gate not tripped: OACT primary"
        ),
        "primary": "PWBM" if gate_trips else "OACT",
        "note": "both comparators are report-only under d658",
    }
    corners = [(p + sp * hp, d + sd * hd) for sp in (-1, 1) for sd in (-1, 1)]
    nonpositive = [(pc, dc) for pc, dc in corners if pc - dc <= 0]
    output["inputs"] = {
        "p": p,
        "d": d,
        "p_half_unit": hp,
        "d_half_unit": hd,
        "p_decimals": p_check,
        "d_decimals": d_check,
        "current_law_cost_rate_cl": p - d,
        "cl_half_width": hp + hd,
    }
    if nonpositive:
        output.update(
            defined=False,
            undefined_reason="p - d is not positive at every corner",
        )
        return output
    _, bounds = four_corner(oact_statistic, p, hp, d, hd)
    output.update(
        defined=True,
        point=oact_statistic(p, d),
        interval=bounds,
        interval_rule=(
            "p and d each +/- half their last printed unit; C over the "
            "four corners; p - d > 0 at every corner"
        ),
        monotonicity_check=grid_check(oact_statistic, p, hp, d, hd, bounds),
    )
    if False in (
        d_check["decimals_consistent"],
        p_check["decimals_consistent"],
    ):
        alt_hp = half_unit(p_check["decimals_in_string"])
        alt_hd = half_unit(d_check["decimals_in_string"])
        output["alternative_interval_from_string_decimals"] = four_corner(
            oact_statistic, p, alt_hp, d, alt_hd
        )[1]
    return output


def _memo_column(column: dict | None) -> dict[str, Any]:
    if column is None:
        return {"recorded": False}
    return {
        "recorded": True,
        "header_verbatim": column.get("header_verbatim"),
        "display": column.get("display"),
        "value": column.get("value"),
        "decimals": column.get("decimals"),
    }


def compare_pwbm(record: dict[str, Any]) -> dict[str, Any]:
    pwbm = record.get("pwbm")
    if not isinstance(pwbm, dict):
        return {"defined": False, "undefined_reason": "no pwbm record"}
    row = pwbm.get("row_2030") or {}
    stored = pwbm.get("stored_decimals") or {}
    output = {
        "last_modified": pwbm.get("last_modified"),
        "last_modified_matches_registration": pwbm.get(
            "last_modified_matches_registration"
        ),
        "row_year": row.get("year"),
        "row_year_is_2030": row.get("year") == "2030",
        "prints_oasi_di_split_2030": pwbm.get("prints_oasi_di_split_2030"),
        "oasi_di_split_2030_fields": pwbm.get("oasi_di_split_2030"),
        "december_2030_timing": pwbm.get("december_2030_timing"),
        "cost_definition": flag_dilution(
            pwbm.get("cost_includes_admin_expenses"),
            pwbm.get("cost_includes_railroad_interchange"),
        ),
        "memo_items": {
            key: {
                "stored": row.get(key),
                "stored_decimals": stored.get(key),
            }
            for key in PWBM_MEMO
        },
    }
    if row.get(PWBM_B) is None or row.get(PWBM_R) is None:
        output.update(
            defined=False,
            undefined_reason="a cost-rate value in the 2030 row is null",
        )
        return output
    b_dec, b_places, b_check = _counted(
        row[PWBM_B], stored.get(PWBM_B), PWBM_B
    )
    r_dec, r_places, r_check = _counted(
        row[PWBM_R], stored.get(PWBM_R), PWBM_R
    )
    b, r = Fraction(b_dec), Fraction(r_dec)
    output["inputs"] = {
        "B": b,
        "R": r,
        "B_decimals": b_check,
        "R_decimals": r_check,
    }
    if b <= 0:
        output.update(
            defined=False, undefined_reason="baseline cost rate is not > 0"
        )
        return output
    point = pwbm_statistic(b, r)
    output.update(defined=True, point=point)
    output.update(_pwbm_interval(b, r, b_places, r_places))
    if not output["defined"]:
        return output
    if False in (
        b_check["decimals_consistent"],
        r_check["decimals_consistent"],
    ):
        alternative = _pwbm_interval(
            b,
            r,
            b_check["decimals_in_string"],
            r_check["decimals_in_string"],
        )
        output["alternative_from_string_decimals"] = alternative
    return output


def _pwbm_interval(b, r, b_places, r_places) -> dict[str, Any]:
    if b_places >= PWBM_POINT_DECIMALS and r_places >= PWBM_POINT_DECIMALS:
        return {
            "defined": True,
            "interval_branch": "point: both stored values carry six or "
            "more decimals",
            "interval": point_interval(pwbm_statistic(b, r)),
        }
    hb, hr = half_unit(b_places), half_unit(r_places)
    if b - hb <= 0:
        return {
            "defined": False,
            "undefined_reason": "B is not positive at every corner",
        }
    _, bounds = four_corner(pwbm_statistic, b, hb, r, hr)
    return {
        "defined": True,
        "interval_branch": "four corners: a stored value carries fewer "
        "than six decimals",
        "B_half_unit": hb,
        "R_half_unit": hr,
        "interval": bounds,
        "monotonicity_check": grid_check(pwbm_statistic, b, hb, r, hr, bounds),
    }


# ---- MINT5 -------------------------------------------------------------


def _format_sections(number_format: str) -> list[str]:
    """Split an Excel number format into sections outside quotes."""

    sections, current, i = [], [], 0
    while i < len(number_format):
        ch = number_format[i]
        if ch == '"':
            end = number_format.find('"', i + 1)
            end = len(number_format) - 1 if end < 0 else end
            current.append(number_format[i : end + 1])
            i = end + 1
            continue
        if ch == "\\":
            current.append(number_format[i : i + 2])
            i += 2
            continue
        if ch == ";":
            sections.append("".join(current))
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    sections.append("".join(current))
    return sections


def percent_signs(number_format: str, value: Decimal) -> int:
    """Unquoted, unescaped % signs in the section that formats ``value``."""

    sections = _format_sections(number_format)
    if len(sections) == 1 or value > 0:
        section = sections[0]
    elif value < 0:
        section = sections[1]
    else:
        section = sections[2] if len(sections) > 2 else sections[0]
    count, i = 0, 0
    while i < len(section):
        ch = section[i]
        if ch == '"':
            end = section.find('"', i + 1)
            i = len(section) if end < 0 else end + 1
            continue
        if ch == "\\":
            i += 2
            continue
        if ch == "[":
            end = section.find("]", i + 1)
            i = len(section) if end < 0 else end + 1
            continue
        if ch == "%":
            count += 1
        i += 1
    return count


def _rounds(value: Decimal, places: int, target: Decimal) -> dict[str, Any]:
    quantum = Decimal(1).scaleb(-places)
    with localcontext() as context:
        context.prec = 80
        up = value.quantize(quantum, rounding=ROUND_HALF_UP)
        even = value.quantize(quantum, rounding=ROUND_HALF_EVEN)
    return {
        "half_up_rounds_to_display": up == target,
        "half_even_rounds_to_display": even == target,
        "modes_agree": (up == target) == (even == target),
        "rounds_to_display": up == target or even == target,
    }


def reading_s(entry: dict[str, Any], html: Decimal, places: int) -> dict:
    """The registered reading: the shortest string for the stored double."""

    raw, number_format = entry.get("xlsx_raw"), entry.get("xlsx_number_format")
    if raw is None:
        return {"available": False, "reason": "xlsx_raw is null"}
    if not isinstance(number_format, str):
        return {
            "available": False,
            "reason": "xlsx_number_format is null; units cannot be read",
        }
    try:
        stored = float(raw)
    except (TypeError, ValueError):
        return {"available": False, "reason": "xlsx_raw is not numeric"}
    shortest = repr(stored)
    base = Decimal(shortest)
    if not base.is_finite():
        return {
            "available": False,
            "reason": "the stored double is not finite",
        }
    signs = percent_signs(number_format, base)
    if signs > 1:
        return {
            "available": False,
            "reason": "the number format scales by more than one percent sign",
        }
    value = base.scaleb(2) if signs == 1 else base
    stored_places = shortest_decimals(value)
    return {
        "available": True,
        "shortest_repr": shortest,
        "percent_format": signs == 1,
        "value_percent_units": value,
        "decimals": stored_places,
        "stores_more_decimals_than_display": stored_places > places,
        **_rounds(value, places, html),
    }


def reading_l(entry: dict[str, Any], html: Decimal, places: int) -> dict:
    """The sensitivity: the record's literal percent value and count."""

    value, count = entry.get("xlsx_value_pct"), entry.get("xlsx_decimals_pct")
    if value is None or count is None:
        return {"available": False, "reason": "literal XLSX fields are null"}
    number = parse_decimal(value, "xlsx_value_pct")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise RecordError("xlsx_decimals_pct must be a non-negative integer")
    return {
        "available": True,
        "value_percent_units": number,
        "decimals": count,
        "decimals_in_string": decimals_of(number),
        "stores_more_decimals_than_display": count > places,
        **_rounds(number, places, html),
    }


def _branch(reading: dict, html: Decimal, places: int) -> dict[str, Any]:
    if (
        reading.get("available")
        and reading["stores_more_decimals_than_display"]
        and reading["rounds_to_display"]
    ):
        value, decimals, branch = (
            reading["value_percent_units"],
            reading["decimals"],
            "xlsx",
        )
    else:
        value, decimals, branch = html, places, "html"
    half = half_unit(decimals)
    return {
        "branch": branch,
        "point": Fraction(value),
        "half_width": half,
        "interval": interval(Fraction(value) - half, Fraction(value) + half),
    }


def compare_mint_band(entry: dict | None) -> dict[str, Any]:
    if not isinstance(entry, dict) or entry.get("html_value") is None:
        return {
            "defined": False,
            "undefined_reason": "median_diff_pct or its HTML value is null",
        }
    html, places, html_check = _counted(
        entry["html_value"], entry.get("html_decimals"), "html_value"
    )
    s = reading_s(entry, html, places)
    literal = reading_l(entry, html, places)
    registered = _branch(s, html, places)
    output = {
        "defined": True,
        "html_display": entry.get("html_display"),
        "html_value": Fraction(html),
        "html_decimals": html_check,
        "pdf_display": entry.get("pdf_display"),
        "xlsx_cell": entry.get("xlsx_cell"),
        "xlsx_number_format": entry.get("xlsx_number_format"),
        "reading_s": s,
        "reading_l": literal,
        "registered": registered,
        "sensitivity_reading_l": _branch(literal, html, places),
        "rule": (
            "reading S (registered): if the XLSX stores more decimals than "
            "the HTML displays and rounds to the display (half-up or "
            "half-even), the XLSX value +/- half its last stored unit; "
            "otherwise the HTML display +/- half its last displayed unit"
        ),
    }
    if s.get("available") and not s["modes_agree"]:
        output["rounding_modes_disagree"] = {
            "branch_if_half_up_only": _branch(
                {**s, "rounds_to_display": s["half_up_rounds_to_display"]},
                html,
                places,
            )["branch"],
            "branch_if_half_even_only": _branch(
                {**s, "rounds_to_display": s["half_even_rounds_to_display"]},
                html,
                places,
            )["branch"],
        }
    return output


def compare_mint(record: dict[str, Any]) -> dict[str, Any]:
    mint = record.get("mint5")
    if not isinstance(mint, dict):
        return {"defined": False, "undefined_reason": "no mint5 record"}
    rows = ((mint.get("table1") or {}).get("rows")) or {}
    median_type = mint.get("median_type")
    headline, beside = HEADLINE_BY_MEDIAN_TYPE.get(
        median_type, HEADLINE_BY_MEDIAN_TYPE["unsettled"]
    )
    start = mint.get("start_date_reading")
    return {
        "defined": True,
        "median_type": median_type,
        "median_type_recognized": median_type in HEADLINE_BY_MEDIAN_TYPE,
        "headline_statistics": list(headline),
        "compared_beside": list(beside),
        "ratio_of_means": "reported beside the headline",
        "start_date_reading": start,
        "start_date_note": (
            "registered primary M0"
            if start == "M0"
            else f"lane reading {start!r}; registered primary stays M0, "
            "rows are never swapped"
        ),
        "age_convention": mint.get("age_convention", "not in the record"),
        "december_2030_timing": mint.get("december_2030_timing"),
        "prints_oasi_di_split": mint.get("prints_oasi_di_split"),
        "bands": {
            band: compare_mint_band(
                (rows.get(band) or {}).get("median_diff_pct")
            )
            for band in MINT_BANDS
        },
        "memo_items": {
            band: {
                field: (rows.get(band) or {}).get(field)
                for field in MINT_MEMO_FIELDS
            }
            for band in MINT_BANDS
        },
        "table2_memo": (mint.get("table2") or {}).get("rows"),
        "sign_convention": (
            "values are used as printed; the model's statistics are "
            "100 x (reform / base - 1), negative for a cut; the record "
            "carries no sign-convention field"
        ),
    }


# ---- gaps --------------------------------------------------------------


def comparison_block(
    model: dict[str, Any],
    comparator: dict[str, Any],
    interval_key: str,
    null_value: Fraction | None,
    null_name: str,
) -> dict[str, Any]:
    """P - C and N - C as intervals; reasons where anything is undefined."""

    block: dict[str, Any] = {"model": model}
    target = (
        comparator.get(interval_key) if comparator.get("defined") else None
    )
    if target is None:
        block["comparator_interval"] = None
        block["undefined_reason"] = comparator.get(
            "undefined_reason", "comparator undefined"
        )
        return block
    block["comparator_interval"] = target
    mean = model.get("mean")
    block["model_minus_comparator"] = (
        subtract(mean, target) if mean is not None else None
    )
    if mean is None:
        block["model_minus_comparator_undefined_reason"] = model.get(
            "undefined_reason"
        )
    block[f"{null_name}_minus_comparator"] = (
        subtract(null_value, target) if null_value is not None else None
    )
    return block


def split_block(comparator: dict, model: dict) -> dict[str, Any]:
    """The OASI and DI split, only where the comparator prints one."""

    flag = comparator.get("prints_oasi_di_split_2030")
    if flag is not True:
        return {
            "printed": flag,
            "note": (
                "not printed by the comparator"
                if flag is False
                else "the record does not say whether a split is printed"
            ),
        }
    fields = comparator.get("oasi_di_split_2030_fields")
    return {
        "printed": True,
        "comparator_fields": fields,
        "note": (
            "the comparator prints a 2030 split; its fields are reported "
            "as recorded"
            if fields is not None
            else "the record flags a printed split but carries no split "
            "fields, so none is compared"
        ),
        "model_P_OASI": model["P_OASI"],
        "model_P_DI": model["P_DI"],
    }


def compare_cost_row(
    row_id: str,
    row: dict | None,
    oact: dict,
    pwbm: dict,
    nulls: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {
            "status": "missing",
            "undefined_reason": "registered row absent from the artifact",
        }
    statistics = row.get("statistics") or {}
    p = model_summary(statistics.get("P"), "P")
    ratio = model_summary(statistics.get(RATIO_OF_MEANS), RATIO_OF_MEANS)
    n, n_model = nulls["N"]["value"], nulls["N_model"]["value"]
    output = {
        "status": row.get("status"),
        "timing": ROW_TIMING[row_id],
        "model": {
            "P": p,
            "ratio_of_scenario_means": ratio,
            "P_OASI": model_summary(statistics.get("P_OASI"), "P_OASI"),
            "P_DI": model_summary(statistics.get("P_DI"), "P_DI"),
            "additions": ["ratio_of_scenario_means", "P_OASI", "P_DI"],
        },
        "P_minus_N": (
            p["mean"] - n if p["mean"] is not None and n is not None else None
        ),
        "P_minus_N_model": (
            p["mean"] - n_model
            if p["mean"] is not None and n_model is not None
            else None
        ),
        "comparators": {},
    }
    for name, comparator in (("OACT", oact), ("PWBM", pwbm)):
        block = comparison_block(p, comparator, "interval", n, "N")
        block["ratio_of_means_beside"] = comparison_block(
            ratio, comparator, "interval", None, "N"
        ).get("model_minus_comparator")
        block["december_2030_timing"] = comparator.get("december_2030_timing")
        block["cost_definition"] = comparator.get("cost_definition")
        block["oasi_di_split"] = split_block(comparator, output["model"])
        output["comparators"][name] = block
    gate = oact.get("precision_gate") or {}
    output["primary_comparator"] = gate.get("primary")
    output["primary_reason"] = gate.get("branch")
    return output


def compare_mint_row(
    row_id: str,
    row: dict | None,
    mint: dict,
    nulls: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {
            "status": "missing",
            "undefined_reason": "registered row absent from the artifact",
        }
    null_name = ROW_NULL[row_id]
    null_value = nulls[null_name]["value"]
    output = {
        "status": row.get("status"),
        "timing": ROW_TIMING[row_id],
        "null": null_name,
        "headline_statistics": mint.get("headline_statistics", []),
        "bands": {},
    }
    bands = row.get("bands") or {}
    for band in MINT_BANDS:
        statistics = (bands.get(band) or {}).get("statistics") or {}
        comparator = (mint.get("bands") or {}).get(band) or {"defined": False}
        registered = (
            {
                "defined": True,
                "interval": comparator["registered"]["interval"],
            }
            if comparator.get("defined")
            else comparator
        )
        sensitivity = (
            {
                "defined": True,
                "interval": comparator["sensitivity_reading_l"]["interval"],
            }
            if comparator.get("defined")
            else comparator
        )
        entry = {}
        for statistic in MINT_COMPARED:
            model = model_summary(statistics.get(statistic), statistic)
            block = comparison_block(
                model, registered, "interval", null_value, null_name
            )
            block["role"] = (
                "headline"
                if statistic in mint.get("headline_statistics", [])
                else "beside"
            )
            block[f"model_minus_{null_name}"] = (
                model["mean"] - null_value
                if model["mean"] is not None and null_value is not None
                else None
            )
            block["sensitivity_reading_l"] = comparison_block(
                model, sensitivity, "interval", null_value, null_name
            )
            block["sensitivity_reading_l"].pop("model", None)
            entry[statistic] = block
        entry["memo"] = {
            "baseline_falling_share": model_summary(
                statistics.get("baseline_falling_share"),
                "baseline_falling_share",
            ),
            "median_benefit_base": model_summary(
                statistics.get("median_benefit_base"), "median_benefit_base"
            ),
            "median_benefit_reform": model_summary(
                statistics.get("median_benefit_reform"),
                "median_benefit_reform",
            ),
            "note": (
                "memo items: the falling share is a fraction of baseline "
                "beneficiary weight, beside MINT's % of population "
                "affected; dollar levels are never compared"
            ),
        }
        output["bands"][band] = entry
    return output


def compare(
    artifact: dict[str, Any], record: dict[str, Any]
) -> dict[str, Any]:
    """Every registered comparison; no pass band and no verdict."""

    if record.get("schema_version") != RECORD_SCHEMA:
        raise RecordError(
            f"record schema {record.get('schema_version')!r} is not "
            f"{RECORD_SCHEMA}"
        )
    nulls = null_values(artifact)
    oact, pwbm, mint = (
        compare_oact(record),
        compare_pwbm(record),
        compare_mint(record),
    )
    rows = artifact.get("rows") or {}
    output_rows: dict[str, Any] = {}
    for row_id in COST_ROWS:
        output_rows[row_id] = compare_cost_row(
            row_id, rows.get(row_id), oact, pwbm, nulls
        )
    deferred = artifact.get("deferred_rows") or {}
    for row_id in DEFERRED_ROWS:
        output_rows[row_id] = {
            "status": "deferred",
            "recorded_in_artifact": row_id in deferred,
            "reason": (deferred.get(row_id) or {}).get("reason"),
            "note": "registered but deferred; not compared in this run",
        }
    for row_id in MINT_ROWS:
        output_rows[row_id] = compare_mint_row(
            row_id, rows.get(row_id), mint, nulls
        )
    return {
        "record": {
            "schema_version": record.get("schema_version"),
            "producer": record.get("producer"),
            "sources": record.get("sources"),
        },
        "nulls": nulls,
        "N_minus_N_model": (
            nulls["N"]["value"] - nulls["N_model"]["value"]
            if nulls["N"]["value"] is not None
            and nulls["N_model"]["value"] is not None
            else None
        ),
        "comparators": {"OACT": oact, "PWBM": pwbm, "MINT5": mint},
        "rows": output_rows,
        "no_pass_band": True,
        "verdict": None,
    }


def sources_check(record: dict[str, Any], seal: dict[str, Any]) -> dict:
    """Each source hash the record lists, against the seal's entry."""

    checked = {}
    for path_text, digest in sorted((record.get("sources") or {}).items()):
        matches = [
            sealed
            for sealed in seal["files"]
            if sealed == path_text or sealed.endswith("/" + path_text)
        ]
        if len(matches) != 1:
            checked[path_text] = {
                "sealed": False,
                "reason": f"{len(matches)} sealed paths match",
            }
            continue
        checked[path_text] = {
            "sealed": True,
            "sealed_path": matches[0],
            "sha256_matches_seal": (
                seal["files"][matches[0]]["sha256"] == digest
            ),
        }
    return checked


# ---- output ------------------------------------------------------------


def to_json(value: Any) -> Any:
    """Render every exact number as a string; keep the rest as JSON."""

    if isinstance(value, Fraction):
        return render(value)
    if isinstance(value, Decimal):
        return render(Fraction(value))
    if isinstance(value, dict):
        return {str(k): to_json(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [to_json(v) for v in value]
    if isinstance(value, float):
        raise TypeError("a float reached the output; use exact numbers")
    return value


def _show(value: Any) -> str:
    if value is None:
        return "undefined"
    if isinstance(value, dict) and set(value) == {"lo", "hi"}:
        return f"[{_show(value['lo'])}, {_show(value['hi'])}]"
    if isinstance(value, Fraction | Decimal):
        return render(Fraction(value))
    return str(value)


def _display(field: Any) -> str:
    if not isinstance(field, dict):
        return "undefined"
    for key in ("html_display", "html_value", "display", "value"):
        if field.get(key) is not None:
            return str(field[key])
    return "undefined"


def _memo_text(items: Any) -> str:
    if not isinstance(items, dict):
        return "undefined"
    parts = []
    for key, value in items.items():
        if isinstance(value, dict):
            shown = value.get("stored", value.get("value"))
        else:
            shown = value
        parts.append(f"{key} = {shown if shown is not None else 'undefined'}")
    return "; ".join(parts)


def _model_cells(model: dict) -> list[str]:
    floor = model.get("floor") or {}
    floor_text = (
        _show(floor.get("mean"))
        if floor.get("defined")
        else f"undefined ({floor.get('undefined_reason')})"
    )
    return [_show(model.get("mean")), _show(model.get("draw_sd")), floor_text]


def markdown(result: dict[str, Any]) -> str:
    lines = [f"# {result['header']}", ""]
    seal, artifact = result["seal"], result["artifact"]
    lines += [
        f"- Seal: `{seal['path']}`, SHA-256 `{seal['sha256']}`, "
        f"{seal['n_files']} files verified.",
        f"- Comparator record: `{result['record_file']['path']}`, SHA-256 "
        f"`{result['record_file']['sha256']}`.",
        f"- Artifact: `{artifact['path']}`, SHA-256 `{artifact['sha256']}` "
        f"(sidecar matches), data provenance `{artifact['data_provenance']}`"
        f", registered commit `{artifact['registered_commit']}`.",
        f"- Registration: {REGISTRATION_POINTER}.",
        "- Report-only. No pass band and no verdict. Numbers are exact: a "
        "terminating decimal in full, otherwise 20 significant digits.",
        "",
        "## Spec-only nulls (percent)",
        "",
        "| Null | Years | Value | Recomputed from its rates |",
        "|---|---|---|---|",
    ]
    for name, entry in result["nulls"].items():
        lines.append(
            f"| {name} | {entry.get('years')} | {_show(entry.get('value'))}"
            f" | {entry.get('recomputed_matches')} |"
        )
    lines += [
        "",
        f"N - N_model: {_show(result['N_minus_N_model'])} percentage points.",
        "",
        "## Comparators (percent)",
        "",
        "| Comparator | Point | Interval | Rule or branch |",
        "|---|---|---|---|",
    ]
    oact, pwbm, mint = (
        result["comparators"][k] for k in ("OACT", "PWBM", "MINT5")
    )
    lines.append(
        f"| OACT A1 | {_show(oact.get('point'))} | "
        f"{_show(oact.get('interval'))} | "
        f"{(oact.get('precision_gate') or {}).get('branch')} |"
    )
    lines.append(
        f"| PWBM | {_show(pwbm.get('point'))} | "
        f"{_show(pwbm.get('interval'))} | {pwbm.get('interval_branch')} |"
    )
    for band, entry in (mint.get("bands") or {}).items():
        registered = entry.get("registered") or {}
        lines.append(
            f"| MINT5 {band} | {_show(registered.get('point'))} | "
            f"{_show(registered.get('interval'))} | "
            f"{registered.get('branch', entry.get('undefined_reason'))}"
            f" (reading L: "
            f"{_show((entry.get('sensitivity_reading_l') or {}).get('interval'))}"
            ") |"
        )
    lines += [
        "",
        "## Cost rows (percent; gaps in percentage points)",
        "",
        "| Row | Comparator | Model mean | Draw SD | Floor | C interval | "
        "P - C | N - C | P - N | P - N_model |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row_id in COST_ROWS:
        row = result["rows"][row_id]
        if row.get("status") == "missing":
            lines.append(f"| {row_id} | missing | | | | | | | | |")
            continue
        for name, block in row["comparators"].items():
            lines.append(
                "| "
                + " | ".join(
                    [
                        row_id,
                        name,
                        *_model_cells(row["model"]["P"]),
                        _show(block.get("comparator_interval")),
                        _show(block.get("model_minus_comparator")),
                        _show(block.get("N_minus_comparator")),
                        _show(row.get("P_minus_N")),
                        _show(row.get("P_minus_N_model")),
                    ]
                )
                + " |"
            )
    lines += [
        "",
        "C0-D: registered but deferred; not compared.",
        "",
        "## MINT5 rows (percent; gaps in percentage points)",
        "",
        "| Row | Band | Statistic | Role | Model mean | Draw SD | Floor | "
        "C interval | Stat - C | Null - C | Stat - null |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row_id in MINT_ROWS:
        row = result["rows"][row_id]
        if row.get("status") == "missing":
            lines.append(f"| {row_id} | missing | | | | | | | | | |")
            continue
        null_name = row["null"]
        for band, entry in row["bands"].items():
            for statistic in MINT_COMPARED:
                block = entry[statistic]
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            row_id,
                            band,
                            statistic,
                            block["role"],
                            *_model_cells(block["model"]),
                            _show(block.get("comparator_interval")),
                            _show(block.get("model_minus_comparator")),
                            _show(block.get(f"{null_name}_minus_comparator")),
                            _show(block.get(f"model_minus_{null_name}")),
                        ]
                    )
                    + " |"
                )
    lines += [
        "",
        "## Memo items (reported, never compared)",
        "",
        "| Row | Band | Our falling share | MINT % affected | Our median "
        "base | Our median reform | MINT median monthly scheduled | "
        "MINT median monthly option |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row_id in MINT_ROWS:
        row = result["rows"][row_id]
        if row.get("status") == "missing":
            continue
        for band, entry in row["bands"].items():
            memo = entry["memo"]
            mint_memo = (mint.get("memo_items") or {}).get(band) or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        row_id,
                        band,
                        _show(memo["baseline_falling_share"]["mean"]),
                        _display(mint_memo.get("pct_population_affected")),
                        _show(memo["median_benefit_base"]["mean"]),
                        _show(memo["median_benefit_reform"]["mean"]),
                        _display(mint_memo.get("median_monthly_scheduled")),
                        _display(mint_memo.get("median_monthly_option")),
                    ]
                )
                + " |"
            )
    lines += [
        "",
        "Our falling share is a fraction of baseline beneficiary weight; "
        "our medians are annual (12 x monthly). Income-rate memo items: "
        f"OACT {_memo_text(oact.get('memo_items'))}; "
        f"PWBM {_memo_text(pwbm.get('memo_items'))}.",
    ]
    lines += ["", "## Flags beside each comparison", ""]
    for name, comparator in (("OACT", oact), ("PWBM", pwbm)):
        timing = comparator.get("december_2030_timing") or {}
        cost = comparator.get("cost_definition") or {}
        lines.append(
            f"- {name}: December 2030 timing `{timing.get('reading')}`; "
            f"dilution {cost.get('dilution')}; OASI/DI split printed: "
            f"{comparator.get('prints_oasi_di_split_2030')}."
        )
    timing = mint.get("december_2030_timing") or {}
    lines += [
        f"- MINT5: December 2030 timing `{timing.get('reading')}`; median "
        f"type `{mint.get('median_type')}` (headline: "
        f"{mint.get('headline_statistics')}); start-date reading "
        f"`{mint.get('start_date_reading')}` ({mint.get('start_date_note')})"
        f"; OASI/DI split printed: {mint.get('prints_oasi_di_split')}.",
        f"- MINT5 sign convention: {mint.get('sign_convention')}.",
        "",
    ]
    return "\n".join(lines) + "\n"


def run(
    *,
    seal_path: Path,
    artifact_path: Path,
    record_path: Path | None = None,
    root: Path | None = None,
    allow_invented: bool = False,
) -> dict[str, Any]:
    """Verify, then compare. Nothing is written here."""

    seal = verify_seal(seal_path, root)
    record_path = Path(record_path or Path(seal["root"]) / RECORD_RELATIVE)
    record_file = verify_record_is_sealed(seal, record_path)
    artifact, artifact_summary = verify_artifact(
        artifact_path, allow_invented=allow_invented
    )
    record = load_json_exact(record_path.read_bytes())
    if not isinstance(record, dict):
        raise RecordError("the comparator record is not a JSON object")
    result = compare(artifact, record)
    result["record"]["sources_check"] = sources_check(record, seal)
    return {
        "schema_version": SCHEMA_VERSION,
        "header": (
            INVENTED_HEADER
            if artifact_summary["invented"]
            else REGISTERED_HEADER
        ),
        "registration_pointer": REGISTRATION_POINTER,
        "seal": {k: v for k, v in seal.items() if k != "files"},
        "record_file": record_file,
        "artifact": artifact_summary,
        **result,
        "number_format": (
            "exact rational arithmetic; a terminating decimal is written in "
            "full, any other value to 20 significant digits (ROUND_HALF_EVEN)"
        ),
    }


def _write_new(path: Path, text: str) -> None:
    with Path(path).open("x", encoding="utf-8") as handle:
        handle.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--seal", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--record",
        type=Path,
        default=None,
        help=f"default: <seal folder>/{RECORD_RELATIVE}",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="the folder the seal's paths are relative to (default: the "
        "seal's folder)",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--allow-invented", action="store_true")
    args = parser.parse_args(argv)
    for path in (args.output_json, args.output_md):
        if path.exists():
            raise SystemExit(f"{path} already exists; outputs are one-shot")
    result = run(
        seal_path=args.seal,
        artifact_path=args.artifact,
        record_path=args.record,
        root=args.root,
        allow_invented=args.allow_invented,
    )
    rendered = to_json(result)
    text = json.dumps(rendered, indent=2, allow_nan=False) + "\n"
    report = markdown(result)
    _write_new(args.output_json, text)
    _write_new(args.output_md, report)
    print(f"seal SHA-256 {result['seal']['sha256']}")
    print(args.output_json)
    print(args.output_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
