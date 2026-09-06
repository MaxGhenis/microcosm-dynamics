"""Build the gate-3 RETRODICTION-ARM pre-lock floor artifact.

PRE-LOCK EVIDENCE, NOT A GATE RUN. ``gates.yaml`` gate_3 carries
``locked: false`` and no thresholds; this script writes no gate, edits
no gate, and scores no candidate. It commits the reference values, the
floors, the external anchors, and a DRAFT tolerance basis that a future
gate-3 lock ceremony would argue over -- the package
``scripts/build_gate2_floors.py`` committed before gate 2 locked.

Why this arm, and why now
-------------------------
``gates.yaml`` gate_3 ("forward projection") describes two arms:

    Tier-2 near-term components resolve against administrative
    publications on named resolution rules; retrodiction backtests
    grade as pseudo-vintage with a published deviation log.

The first arm binds FUTURE annual SSA publications, so its clock cannot
start until thresholds lock. The second -- retrodiction -- scores
against publications ALREADY in hand, so it can be floored today. This
artifact floors the retrodiction arm only.

Definitions, quoted from the ratified record
--------------------------------------------
``paper/paper.qmd`` (scoring surface 3) defines both load-bearing
terms:

    Retrodiction builds the model from data vintages available at a
    historical date and scores it against realized outcomes. Populace's
    versioned data registry pins vintages going forward; pre-registry
    history is a reconstruction problem -- survey redesigns, revised
    administrative tables, re-released panels -- so the protocol grades
    pre-registry backtests as pseudo-vintage, with a published log of
    deviations from true vintage, and no registry pins specification
    leakage: a "2005-vintage" model built today knows 2008 happened,
    and the protocol says so.

``docs/scoring-and-resolution.md`` (surface 3) states the protocol:

    build the panel from data vintages available at time T, project
    forward, and score against realized outcomes at T+k

``docs/domains-of-validity.md`` (Tier 2) names the quantities:

    beneficiary counts by type, average benefits, covered earnings and
    taxable payroll, claiming-age distributions, disability incidence

The floors, and why a person-disjoint split is unavailable
----------------------------------------------------------
gate_1 / gate_2 / gate_2b / gate_2c / gate_m4 / gate_m6 all price a
PERSON-DISJOINT half-split floor: the truth side is a *sample*, so two
disjoint halves of the source frame are two independent realizations of
one estimand and their disagreement is the irreducible measurement
noise no candidate can beat.

The retrodiction arm's truth side is not a sample. Table 6.B5.1 is
"Master Beneficiary Record, 100 percent data (not a sample)" in SSA's
own words. There is no sampling frame to split, so a person-disjoint
floor is unavailable IN PRINCIPLE rather than merely unbuilt, and
manufacturing one (a multinomial bootstrap over published shares) would
invent a variance the source does not have. The analogue that keeps the
same meaning -- two independent realizations of one estimand differing
only through the measurement process -- is the pair of PUBLICATION
VINTAGES of the same table cell. That is the VINTAGE-DISJOINT floor
priced here, and the repository holds one genuine vintage pair: Table
6.B5.1 as printed in the 2014 Supplement (entitlement years 1998-2013)
and as reprinted in the 2023 Supplement (1998-2022).

Three quantities are committed per cell:

F0 ``floor_publication_rounding``  -- the published granularity. A
    share printed to one decimal cannot be resolved below +/-0.05 pp.
    Exact, deterministic, and a hard lower bound on every other floor.

F1 ``floor_vintage_revision``      -- the VINTAGE-DISJOINT measurement
    floor: |value as printed in vintage A - value as printed in vintage
    B| for the same (cell, year), PARTITIONED BY SETTLEMENT STATUS (see
    below), with seeds 0-4 indexing five disjoint publication-year
    blocks over the settled window.

F2 ``naive_baseline_pseudo_vintage`` -- NOT a floor. The skill CEILING:
    what an information-null rule achieves on the same pseudo-vintage
    protocol. ``paper/paper.qmd`` requires exactly this discipline --
    "each cell pre-specifies the naive baseline it must beat".

The settlement finding, and why it changes the tolerance basis
--------------------------------------------------------------
Comparing the two 6.B5.1 printings cell by cell over their 1998-2013
overlap does NOT produce a diffuse revision noise. It produces a sharp
two-regime structure, measured in ``settlement_analysis``:

* SETTLED rows (1998-2012): 240 share cell-years compared, ONE differs,
  by exactly 0.1 pp -- one unit of printing granularity. Average age:
  0 of 30 differ. The revision floor on settled rows is DEGENERATE at
  the publication granularity.
* The TERMINAL row of the vintage (2013): 16 of 16 shares differ, mean
  0.5375 pp, max 1.1 pp; awardee counts move +60k and +73k (~5%).

The mechanism is that 6.B5.1 summarizes awards "by the year in which
entitlement began", so a terminal row keeps accruing late-posted awards
after its Supplement goes to press. The same signature appears
independently at the other end of the panel: for 2015-2021 the 2023
Supplement's awardee counts sit within 1.5% of Table 6.A1's
award-action counts, but for 2022 -- the terminal row of the 2023
vintage -- the gap jumps to 8.6%. Two vintages, two ends of the panel,
one mechanism.

Consequences, all of them binding on the protocol:

1. A provisional terminal row is excluded from the FIT window (a
   true-vintage analyst would not trust it) and from the SCORED window
   (it is a moving target). So T* = 2012, not 2013, even though the
   vintage BOUNDARY is 2014; and the scored window ends at 2021, not
   2022.
2. Pooling settled and terminal rows into one mean/sd -- as any
   unpartitioned floor would -- produces a tolerance driven entirely by
   the single provisional row, and its size then depends on where that
   row happens to fall in the block partition rather than on any
   property of the measurement. This artifact partitions instead, and
   records the pooled number only to show what it would have been.
3. Because F1 is degenerate on settled rows, ``round(mean + k*sd, 3)``
   -- the gate-2 tolerance instrument -- is NOT the right instrument
   here. It is still computed and committed for continuity, flagged
   degenerate; the basis this artifact RECOMMENDS to the ceremony is
   the skill ratio against F2. Which instrument binds is the referee
   round's decision, and both are on the record.

Usage::

    python scripts/build_gate3_retrodiction_floors.py

writes ``runs/gate3_retrodiction_floors_v1.json`` plus the
``.env.json`` / ``.inputs.json`` sidecars. The artifact carries no wall
clock and no environment block, so it is byte-reproducible and
``tests/test_gate3_retrodiction_floors.py`` rebuilds and compares it.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from populace_dynamics import claiming  # noqa: E402
from populace_dynamics.contract import environment_block  # noqa: E402
from populace_dynamics.engine.refit import BOUNDARY_YEAR  # noqa: E402

EXTERNAL = REPO / "data" / "external"
ARTIFACT = REPO / "runs" / "gate3_retrodiction_floors_v1.json"
ENV_SIDECAR = ARTIFACT.with_suffix(".env.json")
INPUT_SIDECAR = ARTIFACT.with_suffix(".inputs.json")

CLAIM_2014 = EXTERNAL / "ssa_claim_ages_2014supplement.json"
CLAIM_2023 = EXTERNAL / "ssa_claim_ages_2023supplement.json"
COVERED_EARNINGS = (
    EXTERNAL / "ssa_covered_earnings_calibration_targets_vintage2.json"
)
LEVEL_ANCHORS = (
    EXTERNAL / "ssa_level_anchors_supplement2025_trustees2026_vintage1.json"
)
DI_TABLES = EXTERNAL / "di_asr_2023" / "tables.json"
COLA = EXTERNAL / "ssa_cola_history.json"
EFFECTIVE_RATES = EXTERNAL / "ssa_effective_interest_rates_2014.json"
TR2014_VIG8 = EXTERNAL / "ssa_tr_2014_vi_g8.source.html"
SUPPLEMENT_4A = (
    EXTERNAL
    / "snapshots"
    / "ssa_level_anchors_vintage1"
    / "supplement2025_4a.html"
)
ANCHOR_CONTEXT_REPORT = REPO / "runs" / "anchor_context_report_v1.json"

#: Vintage-availability boundary; the same constant gate_m6 refits on.
VINTAGE_BOUNDARY_YEAR = BOUNDARY_YEAR  # 2014

#: Terminal (provisional) entitlement row of each 6.B5.1 printing.
TERMINAL_ROW_2014_VINTAGE = 2013
TERMINAL_ROW_2023_VINTAGE = 2022

#: Registered pseudo-vintage origin: last SETTLED row of the 2014
#: printing. T* is a DATA-CONTENT cutoff and is one year inside the
#: VINTAGE_BOUNDARY_YEAR availability cutoff, by the settlement finding.
T_STAR = TERMINAL_ROW_2014_VINTAGE - 1  # 2012
FIT_FIRST_YEAR = 1998

#: Scored window: settled rows of the resolution vintage, after the
#: excluded provisional row of the fit vintage.
SCORED_FIRST_YEAR = TERMINAL_ROW_2014_VINTAGE + 1  # 2014
SCORED_LAST_YEAR = TERMINAL_ROW_2023_VINTAGE - 1  # 2021

#: gate_m6 partitions this window out of every gated set as
#: exogenous_shock_outside_model_class; the same discipline binds here.
SHOCK_YEARS = (2020, 2021)

#: Rolling pseudo-vintage origins supplying the baseline's dispersion.
#: The earliest keeps >= 7 fit years behind an OLS trend.
ROLLING_ORIGIN_FIRST = 2004

#: Five DISJOINT stride-5 blocks, the vintage-disjoint analogue of the
#: person-disjoint seeds 0-4.
SEEDS = (0, 1, 2, 3, 4)
#: DRAFT sd multiple for the mean+k*sd instrument (gate-2 precedent).
DRAFT_K = 4
DRAFT_ROUNDING = 3
#: DRAFT skill ratios: a candidate must beat the naive baseline by this
#: factor. rho is the ceremony's to fix, exactly as gate 2's k was.
DRAFT_RHO = 0.75
RHO_SENSITIVITY = (0.5, 0.75, 0.9)
#: DRAFT eligibility thresholds.
MIN_REPLICATIONS_FOR_GATE = 10
REQUIRED_DEFINED_SEEDS = 5

CLAIM_CATEGORIES = (
    "age62",
    "age63",
    "age64",
    "age65",
    "age66",
    "disability_conversion",
    "age67_69",
    "age70plus",
)
SEXES = ("female", "male")

# Exact Table 4.B11 column-header paths (label-verified selectors).
B11_COLUMNS = {
    "workers_total": ("Number a (thousands)", "Total"),
    "taxable_earnings_total": (
        "Taxable earnings b (millions of dollars)",
        "Total",
    ),
    "contributions_total": (
        "OASDI contributions c,d (millions of dollars)",
        "Total",
    ),
}

# Level-anchor determinations the 4.B11 selection is cross-checked
# against, as {b11_series: level_anchor_determination}.
LEVEL_ANCHOR_CROSSCHECK = {
    "covered_workers_total": "oasdi_workers_with_taxable_earnings",
    "covered_taxable_earnings_total": "oasdi_reported_taxable_earnings",
}

# Exact DI ASR header lines (label-verified before any row is parsed).
DI19_HEADER_0 = (
    "Year\tNumber (thousands)\tPercentage distribution\tAverage age"
)
DI19_HEADER_1 = (
    "Total, all ages\tUnder 30\t30–34\t35–39 a\t40–44\t"
    "45–49\t50–54\t55–59\t60–FRA"
)
DI19_SECTION = "\tAll disabled workers b"
DI19_BANDS = (
    "under30",
    "30_34",
    "35_39",
    "40_44",
    "45_49",
    "50_54",
    "55_59",
    "60_fra",
)
DI49_HEADER_0 = "Year\tTotal\tWorkers\tWidow(er)s\tAdult children"
DI49_HEADER_1 = "Number\tRate\tNumber\tRate\tNumber\tRate\tNumber\tRate"

# Exact 2014 TR Table VI.G8 / Supplement 2025 Table 4.A3 header labels.
VIG8_HEADERS = (
    "Calendar year",
    "",
    "Non-interestincome",
    "",
    "Interestincome",
    "",
    "Totalincome",
    "",
    "Cost",
    "",
    "Assets atend of year",
)
A3_HEADER_0 = ("Year", "Receipts a", "Expenditures", "Assets")
A3_ASSETS_LABEL = "Amount at end of year"
#: Table 4.A3 is bound by CAPTION, not by header shape: 4.A1 (OASI
#: only) and 4.A2 (DI only) print an identical header row in the same
#: document, so header matching alone silently selects OASI and the
#: concept-equivalence check then refutes the anchor.
A3_CAPTION_MARKERS = ("Table 4.A3", "Combined", "(OASI)", "(DI)")
#: The TR anchor is only meaningful if its forecast and realized sides
#: are the same statutory quantity. The two publications print the same
#: fact at different precision (billions vs millions), so agreement
#: should be at rounding scale. Anything larger means the wrong table or
#: the wrong fund was selected, and the builder must fail loudly rather
#: than publish deviations that mix concepts.
A3_CONCEPT_MAX_REL_GAP = 0.005


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reader_commit(relative: str) -> str:
    try:
        return subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", relative],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:  # pragma: no cover - provenance best effort
        return "unknown"


def _abs_gap(a: float, b: float) -> float:
    return abs(float(a) - float(b))


def _log_ratio_abs(a: float, b: float) -> float:
    a, b = float(a), float(b)
    if a <= 0 or b <= 0:
        raise ValueError("log-ratio metric needs two positive values")
    return abs(math.log(a / b))


METRICS = {
    "abs_pp": _abs_gap,
    "abs_years": _abs_gap,
    "log_ratio_abs": _log_ratio_abs,
}


def _blocks(items: list) -> dict[int, list]:
    """Partition an ordered list into five DISJOINT stride-5 blocks."""
    return {seed: items[seed :: len(SEEDS)] for seed in SEEDS}


def _summarize(values: list[float]) -> dict:
    array = np.asarray(values, dtype=float)
    return {
        "mean": round(float(array.mean()), 6),
        "sd": round(float(array.std(ddof=0)), 6),
        "min": round(float(array.min()), 6),
        "max": round(float(array.max()), 6),
        "n_seeds": int(array.size),
        "values": [round(float(v), 6) for v in array],
    }


# --------------------------------------------------------------------------
# cell registry
# --------------------------------------------------------------------------
def _claim_cells() -> dict:
    cells = {}
    for sex in SEXES:
        for category in CLAIM_CATEGORIES:
            cells[f"claim_share.{category}|{sex}"] = {
                "family": "claiming",
                "source_table": "SSA Annual Statistical Supplement 6.B5.1",
                "quantity": (
                    "percentage of retired-worker awardees entitled at "
                    f"{category}, {sex}"
                ),
                "metric": "abs_pp",
                "unit": "percentage points of share (0-100 scale)",
                "scale_invariant": True,
                "publication_granularity": 0.1,
                "two_vintage": True,
            }
        cells[f"claim_awards_thousands|{sex}"] = {
            "family": "claiming",
            "source_table": "SSA Annual Statistical Supplement 6.B5.1",
            "quantity": f"retired-worker awards (thousands), {sex}",
            "metric": "log_ratio_abs",
            "unit": "absolute log ratio",
            "scale_invariant": False,
            "publication_granularity": 1.0,
            "two_vintage": True,
        }
        cells[f"claim_average_age|{sex}"] = {
            "family": "claiming",
            "source_table": "SSA Annual Statistical Supplement 6.B5.1",
            "quantity": f"average age at entitlement, {sex}",
            "metric": "abs_years",
            "unit": "years",
            "scale_invariant": True,
            "publication_granularity": 0.1,
            "two_vintage": True,
        }
    return cells


def _covered_earnings_cells() -> dict:
    common = {
        "family": "covered_earnings",
        "source_table": "SSA Annual Statistical Supplement 4.B11",
        "metric": "log_ratio_abs",
        "unit": "absolute log ratio",
        "two_vintage": False,
    }
    return {
        "covered_taxable_earnings_per_worker": {
            **common,
            "quantity": (
                "OASDI taxable earnings per worker with taxable earnings"
            ),
            "scale_invariant": True,
            "publication_granularity": None,
        },
        "covered_contributions_per_worker": {
            **common,
            "quantity": "OASDI contributions per worker with taxable earnings",
            "scale_invariant": True,
            "publication_granularity": None,
        },
        "covered_workers_total": {
            **common,
            "quantity": "workers with OASDI taxable earnings",
            "scale_invariant": False,
            "publication_granularity": 1000.0,
        },
        "covered_taxable_earnings_total": {
            **common,
            "quantity": "OASDI taxable earnings",
            "scale_invariant": False,
            "publication_granularity": 1_000_000.0,
        },
    }


def _di_cells() -> dict:
    cells = {}
    for band in DI19_BANDS:
        cells[f"di_stock_share.{band}"] = {
            "family": "disability",
            "source_table": "SSA DI Annual Statistical Report Table 19",
            "quantity": (
                "percentage of disabled-worker beneficiaries in current-"
                f"payment status aged {band} (December)"
            ),
            "metric": "abs_pp",
            "unit": "percentage points of share (0-100 scale)",
            "scale_invariant": True,
            "publication_granularity": 0.1,
            "two_vintage": False,
        }
    cells["di_stock_average_age"] = {
        "family": "disability",
        "source_table": "SSA DI Annual Statistical Report Table 19",
        "quantity": "average age of disabled-worker beneficiaries (December)",
        "metric": "abs_years",
        "unit": "years",
        "scale_invariant": True,
        "publication_granularity": 0.1,
        "two_vintage": False,
    }
    cells["di_worker_termination_rate"] = {
        "family": "disability",
        "source_table": "SSA DI Annual Statistical Report Table 49",
        "quantity": (
            "disabled-worker terminations per 1,000 beneficiaries in "
            "current-payment status"
        ),
        "metric": "log_ratio_abs",
        "unit": "absolute log ratio",
        "scale_invariant": True,
        "publication_granularity": 1.0,
        "two_vintage": False,
    }
    cells["di_stock_total_thousands"] = {
        "family": "disability",
        "source_table": "SSA DI Annual Statistical Report Table 19",
        "quantity": "disabled-worker beneficiaries (thousands, December)",
        "metric": "log_ratio_abs",
        "unit": "absolute log ratio",
        "scale_invariant": False,
        "publication_granularity": 1.0,
        "two_vintage": False,
    }
    return cells


def cell_registry() -> dict:
    registry = {}
    registry.update(_claim_cells())
    registry.update(_covered_earnings_cells())
    registry.update(_di_cells())
    return registry


# --------------------------------------------------------------------------
# published series, per vintage
# --------------------------------------------------------------------------
def claiming_series(path: Path) -> dict[str, dict[int, float]]:
    """Per-cell {year: published value} from one Supplement vintage.

    Rows are read through ``ClaimAgeReference.row`` rather than
    ``claiming.claim_age_distribution``: the module-level ``MIN_YEAR`` /
    ``MAX_YEAR`` constants are pinned to the 2023 printing, so the
    nearest-year resolver would silently accept 2014-2022 against the
    2014 vintage and then raise a bare ``KeyError``. Recorded in
    ``not_computable`` as a latent trap for any future gate-3 runner.
    """
    reference = claiming.load_claim_age_reference(path)
    series: dict[str, dict[int, float]] = {}
    for sex in SEXES:
        for year in reference.years():
            row = reference.row(sex, year)
            for category in CLAIM_CATEGORIES:
                value = row["categories"][category]
                if value is None:
                    continue
                key = f"claim_share.{category}|{sex}"
                series.setdefault(key, {})[year] = float(value)
            series.setdefault(f"claim_awards_thousands|{sex}", {})[year] = (
                float(row["number_thousands"])
            )
            series.setdefault(f"claim_average_age|{sex}", {})[year] = float(
                row["average_age"]
            )
    return series


def covered_earnings_series() -> tuple[dict[str, dict[int, float]], dict]:
    """Table 4.B11 totals, selected by exact label-verified selectors."""
    document = json.loads(COVERED_EARNINGS.read_text())
    if document["artifact_vintage_id"] != (
        "ssa_covered_earnings_calibration_targets.vintage2"
    ):
        raise ValueError("unexpected covered-earnings artifact vintage id")
    picked: dict[str, dict[int, float]] = {name: {} for name in B11_COLUMNS}
    for observation in document["observations"]:
        if observation["table_id"] != "table4.b11":
            continue
        header = tuple(observation["nested_column_header_path"])
        for name, expected in B11_COLUMNS.items():
            if header == expected:
                picked[name][int(observation["calendar_year"])] = float(
                    observation["normalized_value"]
                )
    for name, expected in B11_COLUMNS.items():
        if not picked[name]:
            raise ValueError(f"no Table 4.B11 cells matched {expected!r}")
    years = sorted(
        set(picked["workers_total"])
        & set(picked["taxable_earnings_total"])
        & set(picked["contributions_total"])
    )
    series = {
        "covered_workers_total": {
            year: picked["workers_total"][year] for year in years
        },
        "covered_taxable_earnings_total": {
            year: picked["taxable_earnings_total"][year] for year in years
        },
        "covered_taxable_earnings_per_worker": {
            year: picked["taxable_earnings_total"][year]
            / picked["workers_total"][year]
            for year in years
        },
        "covered_contributions_per_worker": {
            year: picked["contributions_total"][year]
            / picked["workers_total"][year]
            for year in years
        },
    }
    provenance = {
        "artifact": COVERED_EARNINGS.name,
        "artifact_vintage_id": document["artifact_vintage_id"],
        "content_sha256": document["integrity"]["content_sha256"],
        "source_document_id": document["source_document_manifest"][0][
            "source_document_id"
        ],
        "publication": document["source_document_manifest"][0]["publication"],
        "url": document["source_document_manifest"][0]["url"],
        "selectors": {
            name: list(expected) for name, expected in B11_COLUMNS.items()
        },
        "years": [years[0], years[-1]],
        "n_years": len(years),
        "single_vintage": (
            "ONE printing only (Annual Statistical Supplement, 2025). No "
            "vintage-revision floor is computable for this family; its "
            "pre-T* rows are as REVISED today, not as printed at T*. "
            "Deviation class revisable_series_single_vintage."
        ),
    }
    return series, provenance


def level_anchor_crosscheck(covered: dict[str, dict[int, float]]) -> dict:
    """Do the 4.B11 selectors agree with the registered level anchors?

    The covered-earnings artifact and the level-anchor vintage were
    extracted independently from different Supplement editions' tables.
    Where they claim the same quantity they must agree to the digit;
    this computes that rather than asserting it.
    """
    determinations = json.loads(LEVEL_ANCHORS.read_text())["determinations"]
    rows = []
    for series_key, determination in sorted(LEVEL_ANCHOR_CROSSCHECK.items()):
        anchor = {
            int(observation["year"]): float(observation["value"])
            for observation in determinations[determination]["observations"]
        }
        for year in sorted(set(anchor) & set(covered[series_key])):
            mine = covered[series_key][year]
            theirs = anchor[year]
            rows.append(
                {
                    "series": series_key,
                    "determination": determination,
                    "year": year,
                    "covered_earnings_artifact": mine,
                    "level_anchor_artifact": theirs,
                    "abs_gap": round(abs(mine - theirs), 6),
                }
            )
    return {
        "status": "COMPUTED, not asserted",
        "what_it_checks": (
            "that the label-verified Table 4.B11 selectors used here "
            "reproduce the independently registered level-anchor series "
            "over their overlapping years, to the digit"
        ),
        "n_comparisons": len(rows),
        "max_abs_gap": (max(row["abs_gap"] for row in rows) if rows else None),
        "all_exact": all(row["abs_gap"] == 0 for row in rows),
        "rows": rows,
    }


def _di_number(token: str) -> float | None:
    token = token.strip().replace(",", "")
    if token in {"", "--", ". . .", "a", "b"}:
        return None
    try:
        return float(token)
    except ValueError:
        return None


def di_series() -> tuple[dict[str, dict[int, float]], dict]:
    """DI ASR Tables 19 and 49, header-verified before any row is read."""
    tables = json.loads(DI_TABLES.read_text())
    lines19 = tables["Table 19"]["tsv"].split("\n")
    if lines19[0] != DI19_HEADER_0 or lines19[1] != DI19_HEADER_1:
        raise ValueError("DI Table 19 header labels moved")
    if lines19[2] != DI19_SECTION:
        raise ValueError("DI Table 19 'All disabled workers' section moved")
    series: dict[str, dict[int, float]] = {}
    for line in lines19[3:]:
        if line.startswith("\t"):
            break
        fields = line.split("\t")
        if not re.fullmatch(r"(19|20)\d\d", fields[0]):
            break
        year = int(fields[0])
        total = _di_number(fields[1])
        if total is not None:
            series.setdefault("di_stock_total_thousands", {})[year] = total
        for offset, band in enumerate(DI19_BANDS):
            value = _di_number(fields[3 + offset])
            if value is not None:
                series.setdefault(f"di_stock_share.{band}", {})[year] = value
        average_age = _di_number(fields[11])
        if average_age is not None:
            series.setdefault("di_stock_average_age", {})[year] = average_age

    lines49 = tables["Table 49"]["tsv"].split("\n")
    if lines49[0] != DI49_HEADER_0 or lines49[1] != DI49_HEADER_1:
        raise ValueError("DI Table 49 header labels moved")
    for line in lines49[2:]:
        fields = line.split("\t")
        if not re.fullmatch(r"(19|20)\d\d", fields[0]):
            continue
        rate = _di_number(fields[4])
        if rate is not None and rate > 0:
            series.setdefault("di_worker_termination_rate", {})[
                int(fields[0])
            ] = rate
    provenance = {
        "artifact": "data/external/di_asr_2023/tables.json",
        "sha256": _sha256(DI_TABLES),
        "publication": (
            "SSA Annual Statistical Report on the Social Security Disability "
            "Insurance Program, 2023"
        ),
        "tables": {
            "Table 19": tables["Table 19"]["caption"],
            "Table 49": tables["Table 49"]["caption"],
        },
        "header_labels_verified": [
            DI19_HEADER_0,
            DI19_HEADER_1,
            DI49_HEADER_0,
            DI49_HEADER_1,
        ],
        "section_parsed": "All disabled workers (sexes combined)",
        "same_tables_parsed_by": "scripts/build_m4_gate_floors.py",
        "single_vintage": (
            "ONE printing only (DI Annual Statistical Report, 2023). No "
            "vintage-revision floor is computable for this family. "
            "Deviation class revisable_series_single_vintage."
        ),
    }
    return series, provenance


HORIZONS = tuple(range(1, 10))
EXCLUDED_YEARS = (TERMINAL_ROW_2014_VINTAGE, TERMINAL_ROW_2023_VINTAGE)


# --------------------------------------------------------------------------
# the settlement finding
# --------------------------------------------------------------------------
def settlement_analysis(
    registry: dict,
    vintage_a: dict[str, dict[int, float]],
    vintage_b: dict[str, dict[int, float]],
    latest: dict[str, dict[int, float]],
) -> dict:
    """Measure the two-regime structure of the vintage pair."""
    by_regime: dict[str, dict[str, list[float]]] = {
        "settled": {},
        "terminal": {},
    }
    for key, spec in registry.items():
        if key not in vintage_a or key not in vintage_b:
            continue
        metric = METRICS[spec["metric"]]
        for year in sorted(set(vintage_a[key]) & set(vintage_b[key])):
            regime = (
                "terminal" if year == TERMINAL_ROW_2014_VINTAGE else "settled"
            )
            deviation = metric(vintage_a[key][year], vintage_b[key][year])
            by_regime[regime].setdefault(spec["metric"], []).append(deviation)

    def summarize(values: list[float]) -> dict:
        array = np.asarray(values, dtype=float)
        return {
            "n_cell_years": int(array.size),
            "n_nonzero": int((array > 0).sum()),
            "mean": round(float(array.mean()), 6),
            "max": round(float(array.max()), 6),
        }

    # Independent confirmation at the other end of the panel: the 2023
    # vintage's own terminal row against Table 6.A1 award-action counts.
    determinations = json.loads(LEVEL_ANCHORS.read_text())["determinations"]
    awards_6a1 = {
        int(observation["year"]): float(observation["value"])
        for observation in determinations["retired_worker_awards"][
            "observations"
        ]
    }
    confirmation = []
    for year in sorted(awards_6a1):
        both_sexes = sum(
            latest[f"claim_awards_thousands|{sex}"].get(year, 0.0)
            for sex in SEXES
        )
        if not both_sexes:
            continue
        confirmation.append(
            {
                "year": year,
                "terminal_row_of_2023_vintage": (
                    year == TERMINAL_ROW_2023_VINTAGE
                ),
                "supplement_6b5_1_thousands": both_sexes,
                "supplement_6a1_awards_thousands": round(
                    awards_6a1[year] / 1000.0, 3
                ),
                "relative_gap": round(
                    abs(awards_6a1[year] / 1000.0 - both_sexes) / both_sexes,
                    6,
                ),
            }
        )
    settled_gaps = [
        row["relative_gap"]
        for row in confirmation
        if not row["terminal_row_of_2023_vintage"]
    ]
    terminal_gaps = [
        row["relative_gap"]
        for row in confirmation
        if row["terminal_row_of_2023_vintage"]
    ]
    return {
        "finding": (
            "the two 6.B5.1 printings do not disagree diffusely. They "
            "disagree in exactly one regime: the TERMINAL entitlement "
            "row of the earlier printing, which is still accruing "
            "late-posted awards when its Supplement goes to press. "
            "Settled rows are reproduced to the printed digit."
        ),
        "mechanism_quoted_from_the_table": (
            "The data in this table differ from those in table 6.B5 "
            "because awards are summarized here by the year in which "
            "entitlement began rather than by the year the award action "
            "was posted on the Master Beneficiary Record."
        ),
        "terminal_row_of_fit_vintage": TERMINAL_ROW_2014_VINTAGE,
        "terminal_row_of_resolution_vintage": TERMINAL_ROW_2023_VINTAGE,
        "by_regime": {
            regime: {
                metric_name: summarize(values)
                for metric_name, values in sorted(metrics.items())
            }
            for regime, metrics in by_regime.items()
        },
        "independent_confirmation": {
            "what": (
                "the same signature at the OTHER end of the panel and "
                "from a DIFFERENT table. Table 6.A1 counts retired-worker "
                "awards by award action; 6.B5.1 counts them by "
                "entitlement year. Over settled years the two agree "
                "closely; at the 2023 vintage's own terminal row the gap "
                "jumps, because 6.B5.1's terminal row is short the "
                "late-posted awards that 6.A1 already has."
            ),
            "settled_years_max_relative_gap": (
                round(max(settled_gaps), 6) if settled_gaps else None
            ),
            "terminal_year_relative_gap": (
                round(max(terminal_gaps), 6) if terminal_gaps else None
            ),
            "rows": confirmation,
        },
        "protocol_consequences": [
            "the provisional terminal row of the FIT vintage (2013) is "
            "excluded from the fit window, so T* = 2012 even though the "
            "vintage availability boundary is 2014",
            "the provisional terminal row of the RESOLUTION vintage "
            "(2022) is excluded from the scored window, which therefore "
            "ends at 2021",
            "the vintage-revision floor is partitioned by settlement "
            "status; pooling the two regimes produces a tolerance driven "
            "entirely by one provisional row",
        ],
    }


# --------------------------------------------------------------------------
# F0: publication-rounding floor
# --------------------------------------------------------------------------
def publication_rounding_floor(spec: dict, series: dict[int, float]) -> dict:
    granularity = spec["publication_granularity"]
    if granularity is None:
        return {
            "status": "not_established",
            "reason": (
                "derived ratio of two independently rounded published "
                "cells; the induced granularity is not a single printed "
                "interval. The covered-earnings artifact itself records "
                "published_rounding_interval.status = "
                "'not_established_from_source_bytes'."
            ),
        }
    half = granularity / 2.0
    if spec["metric"] in {"abs_pp", "abs_years"}:
        return {
            "status": "established",
            "granularity": granularity,
            "half_interval": half,
            "floor": round(half, 6),
            "basis": (
                "half the printed granularity; two publications of the "
                "same fact can differ by this much on rounding alone"
            ),
        }
    smallest = min(series.values())
    largest = max(series.values())
    return {
        "status": "established",
        "granularity": granularity,
        "half_interval": half,
        "floor": round(abs(math.log1p(half / smallest)), 6),
        "floor_at_largest_value": round(abs(math.log1p(half / largest)), 6),
        "basis": (
            "half the printed granularity expressed on the log-ratio "
            "scale at the SMALLEST published value in the series (the "
            "conservative end); the value at the largest is recorded too"
        ),
    }


# --------------------------------------------------------------------------
# F1: vintage-disjoint revision floor, partitioned by settlement
# --------------------------------------------------------------------------
def vintage_revision_floor(
    registry: dict,
    vintage_a: dict[str, dict[int, float]],
    vintage_b: dict[str, dict[int, float]],
) -> tuple[dict, list[dict]]:
    floors: dict[str, dict] = {}
    log: list[dict] = []
    for key, spec in registry.items():
        if key not in vintage_a or key not in vintage_b:
            continue
        metric = METRICS[spec["metric"]]
        overlap = sorted(set(vintage_a[key]) & set(vintage_b[key]))
        if not overlap:
            continue
        deviations = {
            year: metric(vintage_a[key][year], vintage_b[key][year])
            for year in overlap
        }
        for year, deviation in deviations.items():
            if deviation > 0:
                log.append(
                    {
                        "cell": key,
                        "year": year,
                        "regime": (
                            "terminal"
                            if year == TERMINAL_ROW_2014_VINTAGE
                            else "settled"
                        ),
                        "earlier_vintage_value": vintage_a[key][year],
                        "later_vintage_value": vintage_b[key][year],
                        "deviation": round(deviation, 6),
                        "metric": spec["metric"],
                    }
                )
        settled = [
            year for year in overlap if year != TERMINAL_ROW_2014_VINTAGE
        ]
        blocks = _blocks(settled)
        block_means, block_detail = [], {}
        for seed, block_years in blocks.items():
            if not block_years:
                continue
            values = [deviations[year] for year in block_years]
            block_means.append(float(np.mean(values)))
            block_detail[str(seed)] = {
                "years": block_years,
                "mean": round(float(np.mean(values)), 6),
                "n_years": len(block_years),
            }
        summary = _summarize(block_means)
        settled_values = [deviations[year] for year in settled]
        pooled_values = [deviations[year] for year in overlap]
        terminal = deviations.get(TERMINAL_ROW_2014_VINTAGE)
        floors[key] = {
            **summary,
            "metric": spec["metric"],
            "regime": "settled_rows_only",
            "settled_years": [settled[0], settled[-1]] if settled else [],
            "n_settled_years": len(settled),
            "n_settled_nonzero": sum(1 for v in settled_values if v > 0),
            "settled_max": round(float(max(settled_values)), 6),
            "settled_pooled_mean": round(float(np.mean(settled_values)), 6),
            "terminal_row_deviation": (
                round(terminal, 6) if terminal is not None else None
            ),
            "blocks": block_detail,
            "degenerate": summary["max"] == 0.0,
            "pooled_including_terminal_row": {
                "note": (
                    "recorded ONLY to show what an unpartitioned floor "
                    "would have produced; not used for any tolerance"
                ),
                "mean_over_years": round(float(np.mean(pooled_values)), 6),
                "max_over_years": round(float(max(pooled_values)), 6),
            },
        }
    log.sort(key=lambda row: (-row["deviation"], row["cell"], row["year"]))
    return floors, log


# --------------------------------------------------------------------------
# F2: the pseudo-vintage naive baseline (the SKILL CEILING)
# --------------------------------------------------------------------------
def _persistence(fit_years: list[int], values: list[float], _t: int) -> float:
    return float(values[-1])


def _linear_trend(
    fit_years: list[int], values: list[float], target: int
) -> float:
    slope, intercept = np.polyfit(
        np.asarray(fit_years, dtype=float),
        np.asarray(values, dtype=float),
        1,
    )
    return float(slope * target + intercept)


NAIVE_RULES = {
    "persistence": _persistence,
    "linear_trend": _linear_trend,
}


def naive_baseline(
    registry: dict,
    fit_series: dict[str, dict[int, float]],
    resolution_series: dict[str, dict[int, float]],
    *,
    family: str,
    excluded_targets: tuple[int, ...],
    fit_source: str,
) -> dict:
    """Deviation of the information-null rules on the same protocol.

    This is NOT a noise floor. It is what a candidate must beat: a rule
    carrying no information past T* already achieves it.
    """
    out: dict[str, dict] = {}
    for key, spec in registry.items():
        if spec["family"] != family:
            continue
        if key not in fit_series or key not in resolution_series:
            continue
        metric = METRICS[spec["metric"]]
        fit = fit_series[key]
        realized = resolution_series[key]
        origins = [
            year
            for year in range(ROLLING_ORIGIN_FIRST, T_STAR + 1)
            if year in fit
            and len([y for y in fit if FIT_FIRST_YEAR <= y <= year]) >= 5
        ]
        if not origins:
            continue
        by_rule: dict[str, dict] = {}
        for rule_name, rule in NAIVE_RULES.items():
            registered: dict[str, dict] = {}
            per_horizon: dict[str, dict] = {}
            for horizon in HORIZONS:
                clean_by_origin: dict[int, float] = {}
                shock_by_origin: dict[int, float] = {}
                for origin in origins:
                    target = origin + horizon
                    if target in excluded_targets:
                        continue
                    if target > SCORED_LAST_YEAR or target not in realized:
                        continue
                    fit_years = [
                        y for y in sorted(fit) if FIT_FIRST_YEAR <= y <= origin
                    ]
                    values = [fit[y] for y in fit_years]
                    try:
                        prediction = rule(fit_years, values, target)
                    except (ValueError, np.linalg.LinAlgError):
                        continue
                    if spec["metric"] == "log_ratio_abs" and prediction <= 0:
                        continue
                    deviation = metric(prediction, realized[target])
                    bucket = (
                        shock_by_origin
                        if target in SHOCK_YEARS
                        else clean_by_origin
                    )
                    bucket[origin] = deviation
                    if origin == T_STAR:
                        registered.setdefault(
                            "shock" if target in SHOCK_YEARS else "clean", {}
                        )[f"h{horizon}"] = {
                            "target_year": target,
                            "prediction": round(prediction, 6),
                            "realized": round(realized[target], 6),
                            "deviation": round(deviation, 6),
                        }
                if not clean_by_origin:
                    continue
                ordered = sorted(clean_by_origin)
                blocks = _blocks(ordered)
                block_means, block_detail = [], {}
                for seed, block_origins in blocks.items():
                    if not block_origins:
                        continue
                    values = [clean_by_origin[o] for o in block_origins]
                    block_means.append(float(np.mean(values)))
                    block_detail[str(seed)] = {
                        "origins": block_origins,
                        "mean": round(float(np.mean(values)), 6),
                    }
                per_horizon[f"h{horizon}"] = {
                    **_summarize(block_means),
                    "n_origins": len(ordered),
                    "origin_range": [ordered[0], ordered[-1]],
                    "pooled_mean_over_origins": round(
                        float(np.mean(list(clean_by_origin.values()))), 6
                    ),
                    "pooled_max_over_origins": round(
                        float(max(clean_by_origin.values())), 6
                    ),
                    "blocks": block_detail,
                    "shock_window_pooled_mean": (
                        round(
                            float(np.mean(list(shock_by_origin.values()))), 6
                        )
                        if shock_by_origin
                        else None
                    ),
                }
            if not per_horizon:
                continue
            pooled = [
                entry["pooled_mean_over_origins"]
                for entry in per_horizon.values()
            ]
            registered_clean = registered.get("clean", {})
            by_rule[rule_name] = {
                "by_horizon": per_horizon,
                "pooled_mean_over_horizons": round(float(np.mean(pooled)), 6),
                "registered_origin": {
                    "T_star": T_STAR,
                    "clean": registered_clean,
                    "shock": registered.get("shock", {}),
                    "clean_mean_deviation": (
                        round(
                            float(
                                np.mean(
                                    [
                                        row["deviation"]
                                        for row in registered_clean.values()
                                    ]
                                )
                            ),
                            6,
                        )
                        if registered_clean
                        else None
                    ),
                },
            }
        if by_rule:
            better = min(
                by_rule,
                key=lambda name: by_rule[name]["pooled_mean_over_horizons"],
            )
            out[key] = {
                "metric": spec["metric"],
                "fit_source": fit_source,
                "rules": by_rule,
                "better_rule": better,
                "baseline_rule": better,
                "baseline_pooled_mean": by_rule[better][
                    "pooled_mean_over_horizons"
                ],
            }
    return out


# --------------------------------------------------------------------------
# skill window, eligibility and DRAFT tolerances
# --------------------------------------------------------------------------
def _baseline_by_horizon(baseline: dict | None) -> dict:
    """Per-horizon naive baseline: registered origin and rolling spread."""
    if baseline is None:
        return {}
    rule = baseline["rules"][baseline["baseline_rule"]]
    registered = rule["registered_origin"]
    out = {}
    for horizon, entry in rule["by_horizon"].items():
        clean = registered["clean"].get(horizon)
        shock = registered["shock"].get(horizon)
        out[horizon] = {
            "rolling_block_mean": entry["mean"],
            "rolling_block_sd": entry["sd"],
            "rolling_pooled_mean": entry["pooled_mean_over_origins"],
            "n_origins": entry["n_origins"],
            "registered_origin_deviation": (
                clean["deviation"] if clean else None
            ),
            "registered_origin_target_year": (
                clean["target_year"] if clean else None
            ),
            "registered_origin_in_shock_window": bool(shock and not clean),
        }
    return out


def skill_window(
    registry: dict,
    rounding_floors: dict,
    revision_floors: dict,
    baselines: dict,
) -> dict:
    window = {}
    for key, spec in registry.items():
        rounding = rounding_floors.get(key, {})
        rounding_floor = rounding.get("floor")
        revision = revision_floors.get(key)
        baseline = baselines.get(key)
        mean_k_sd = None
        if revision is not None:
            mean_k_sd = round(
                revision["mean"] + DRAFT_K * revision["sd"], DRAFT_ROUNDING
            )
            if rounding_floor is not None:
                mean_k_sd = max(
                    mean_k_sd, round(rounding_floor, DRAFT_ROUNDING)
                )
        lower = max(
            [v for v in (rounding_floor, mean_k_sd) if v is not None],
            default=None,
        )
        horizons = _baseline_by_horizon(baseline)
        by_horizon = {}
        for horizon, entry in horizons.items():
            registered = entry["registered_origin_deviation"]
            basis = (
                registered
                if registered is not None
                else entry["rolling_block_mean"]
            )
            basis_name = (
                "registered_origin_deviation"
                if registered is not None
                else "rolling_block_mean_fallback"
            )
            tolerance = round(DRAFT_RHO * basis, DRAFT_ROUNDING)
            by_horizon[horizon] = {
                **entry,
                "basis": basis_name,
                "basis_value": basis,
                "instrument_b_skill_ratio": tolerance,
                "room_for_skill": (
                    bool(lower < basis) if lower is not None else None
                ),
                "room_ratio": (
                    round(basis / lower, 4)
                    if lower and lower > 0 and basis > 0
                    else None
                ),
                "skill_ratio_sensitivity": {
                    str(rho): round(rho * basis, DRAFT_ROUNDING)
                    for rho in RHO_SENSITIVITY
                },
            }
        pooled = (
            baseline["baseline_pooled_mean"] if baseline is not None else None
        )
        room_all = (
            all(entry["room_for_skill"] for entry in by_horizon.values())
            if by_horizon
            and all(
                entry["room_for_skill"] is not None
                for entry in by_horizon.values()
            )
            else None
        )
        window[key] = {
            "metric": spec["metric"],
            "publication_rounding_floor_F0": rounding_floor,
            "vintage_revision_floor_F1_mean": (
                revision["mean"] if revision else None
            ),
            "vintage_revision_floor_F1_sd": (
                revision["sd"] if revision else None
            ),
            "F1_degenerate": revision["degenerate"] if revision else None,
            "instrument_a_mean_k_sd": mean_k_sd,
            "lower_bound_used": lower,
            "naive_baseline_rule": (
                baseline["baseline_rule"] if baseline else None
            ),
            "naive_baseline_pooled_over_horizons_F2": pooled,
            "room_for_skill_at_every_horizon": room_all,
            "by_horizon": by_horizon,
        }
    return window


def cell_stability(
    registry: dict, revision_floors: dict, baselines: dict, window: dict
) -> dict:
    stability = {}
    for key, spec in registry.items():
        revision = revision_floors.get(key)
        baseline = baselines.get(key)
        entry = window[key]
        reasons = []
        if revision is None:
            reasons.append("no_second_publication_vintage_in_repository")
        else:
            if revision["n_seeds"] < REQUIRED_DEFINED_SEEDS:
                reasons.append("fewer_than_five_nonempty_vintage_blocks")
            if revision["n_settled_years"] < MIN_REPLICATIONS_FOR_GATE:
                reasons.append("fewer_than_ten_settled_overlap_years")
        n_origins = 0
        n_registered_horizons = 0
        if baseline is None:
            reasons.append("no_naive_baseline_computable")
        else:
            n_origins = max(
                horizon["n_origins"]
                for horizon in entry["by_horizon"].values()
            )
            n_registered_horizons = sum(
                1
                for horizon in entry["by_horizon"].values()
                if horizon["registered_origin_deviation"] is not None
            )
            if n_origins < REQUIRED_DEFINED_SEEDS:
                reasons.append("fewer_than_five_pseudo_vintage_origins")
            if n_registered_horizons == 0:
                reasons.append("no_clean_horizon_at_the_registered_origin")
        if not spec["scale_invariant"]:
            reasons.append(
                "level_cell_not_gate_eligible_pre_w1_scale_invariance"
            )
        if entry["room_for_skill_at_every_horizon"] is False:
            reasons.append("no_room_for_skill_at_some_horizon")
        stability[key] = {
            "family": spec["family"],
            "two_vintage": spec["two_vintage"],
            "n_settled_overlap_years": (
                revision["n_settled_years"] if revision else 0
            ),
            "n_pseudo_vintage_origins": n_origins,
            "n_clean_horizons_at_registered_origin": n_registered_horizons,
            "defined_vintage_blocks": revision["n_seeds"] if revision else 0,
            "scale_invariant": spec["scale_invariant"],
            "draft_gate_eligible": not reasons,
            "blocking_reasons": reasons,
        }
    return stability


def draft_thresholds(registry: dict, window: dict, stability: dict) -> dict:
    cells = {}
    for key, spec in registry.items():
        entry = window[key]
        if not entry["by_horizon"]:
            continue
        cells[key] = {
            "metric": spec["metric"],
            "unit": spec["unit"],
            "instrument_a_mean_k_sd": {
                "tolerance": entry["instrument_a_mean_k_sd"],
                "horizon_invariant": True,
                "derivation": {
                    "floor_mean": entry["vintage_revision_floor_F1_mean"],
                    "floor_sd": entry["vintage_revision_floor_F1_sd"],
                    "k": DRAFT_K,
                    "rounding": DRAFT_ROUNDING,
                    "publication_rounding_floor": entry[
                        "publication_rounding_floor_F0"
                    ],
                    "rule": (
                        "max(round(F1_mean + k*F1_sd, 3), F0) -- the "
                        "gate-2 instrument, carried for continuity"
                    ),
                },
                "degenerate": entry["F1_degenerate"],
                "why_not_recommended": (
                    "F1 is degenerate on settled rows (the truth side is "
                    "a 100-percent MBR census, not a sample), so this "
                    "collapses onto the publication-rounding floor, "
                    "carries no horizon structure at all, and would fail "
                    "every candidate at every horizon by construction"
                ),
            },
            "instrument_b_skill_ratio": {
                "rho": DRAFT_RHO,
                "rounding": DRAFT_ROUNDING,
                "rule": (
                    "round(rho * naive_baseline_at_the_registered_origin"
                    "(cell, horizon), 3), falling back to the "
                    "rolling-origin block mean where the registered "
                    "origin has no clean target at that horizon"
                ),
                "baseline_rule": entry["naive_baseline_rule"],
                "by_horizon": {
                    horizon: {
                        "tolerance": row["instrument_b_skill_ratio"],
                        "basis": row["basis"],
                        "basis_value": row["basis_value"],
                        "registered_origin_target_year": row[
                            "registered_origin_target_year"
                        ],
                        "rolling_block_mean": row["rolling_block_mean"],
                        "rolling_block_sd": row["rolling_block_sd"],
                        "n_origins": row["n_origins"],
                        "room_for_skill": row["room_for_skill"],
                        "room_ratio": row["room_ratio"],
                        "sensitivity": row["skill_ratio_sensitivity"],
                    }
                    for horizon, row in entry["by_horizon"].items()
                },
                "why_recommended": (
                    "the truth side carries no sampling noise, so the "
                    "binding question is skill, not measurement error: "
                    "does the candidate beat the pre-registered "
                    "information-null rule at each horizon? "
                    "paper/paper.qmd requires each cell to "
                    "'pre-specify the naive baseline it must beat', and "
                    "gate_3 is a FORWARD-PROJECTION gate, so a "
                    "horizon-invariant tolerance would let a candidate "
                    "that is poor at h=7 pass on its h=2 performance."
                ),
                "unresolved_tension_for_the_referee": (
                    "the registered-origin basis is the number a "
                    "candidate actually competes against, but it is ONE "
                    "realization, so it lacks the replication that the "
                    "seeds/blocks exist to supply. The rolling-origin "
                    "block mean and sd are recorded beside every "
                    "horizon so the ceremony can choose the robust "
                    "basis instead, or require both. This artifact does "
                    "not choose."
                ),
            },
            "room_for_skill_at_every_horizon": entry[
                "room_for_skill_at_every_horizon"
            ],
            "draft_gate_eligible": stability[key]["draft_gate_eligible"],
        }
    return {
        "k": DRAFT_K,
        "rho": DRAFT_RHO,
        "rho_sensitivity": list(RHO_SENSITIVITY),
        "rounding": DRAFT_ROUNDING,
        "two_instruments_note": (
            "TWO instruments are committed and NEITHER is asserted. "
            "Instrument A is the gate-2 mean+k*sd tolerance, carried so "
            "the ceremony can see exactly what the established "
            "convention produces here -- and see that it degenerates, "
            "because the retrodiction arm's truth side is an "
            "administrative census with no sampling noise to price. "
            "Instrument B is the per-horizon skill ratio against the "
            "pre-registered naive baseline, which is what the paper's "
            "own discipline for resolving cells demands. k = 4 follows "
            "the gate-2 pre-lock precedent (runs/gate2_floors_v1.json "
            "draft_thresholds.k = 4); gate_m4 and gate_m6 later adopted "
            "a MIXED k (flow 3 / stock 4). rho = 0.75 is a PROPOSAL with "
            "its sensitivity recorded at 0.5 / 0.75 / 0.9. Choosing the "
            "instrument, its constant, and the registered-vs-rolling "
            "basis is the referee round's decision. No value here is "
            "mirrored into gates.yaml by this artifact."
        ),
        "cells": cells,
    }


# --------------------------------------------------------------------------
# external anchors
# --------------------------------------------------------------------------
def _strip_tags(fragment: str) -> str:
    return (
        re.sub(r"<[^>]+>", "", fragment)
        .replace("&nbsp;", " ")
        .replace("&ndash;", "-")
        .replace("\xa0", " ")
        .strip()
    )


def _table_with_caption(path: Path, markers: tuple[str, ...]) -> str:
    """Return the single <table> whose caption carries every marker."""
    text = path.read_text(errors="replace")
    matches = [
        chunk
        for chunk in re.findall(r"<table[^>]*>.*?</table>", text, re.S)
        if (
            caption := re.search(r"<caption[^>]*>(.*?)</caption>", chunk, re.S)
        )
        and all(marker in _strip_tags(caption.group(1)) for marker in markers)
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one table in {path.name} captioned "
            f"{markers!r}, found {len(matches)}"
        )
    return matches[0]


def _html_rows(source: Path | str) -> list[list[str]]:
    text = (
        source.read_text(errors="replace")
        if isinstance(source, Path)
        else source
    )
    rows = []
    for chunk in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S):
        cells = [
            re.sub(r"<[^>]+>", "", cell)
            .replace("&nbsp;", " ")
            .replace("\xa0", " ")
            .strip()
            for cell in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", chunk, re.S)
        ]
        if cells:
            rows.append(cells)
    return rows


def _money(token: str) -> float | None:
    token = token.replace("$", "").replace(",", "").strip()
    try:
        return float(token)
    except ValueError:
        return None


def tr2014_projection_anchor() -> dict:
    """2014 TR VI.G8 intermediate projections vs realized 4.A3 assets."""
    rows = _html_rows(TR2014_VIG8)
    header = next(row for row in rows if row and row[0] == "Calendar year")
    if tuple(header) != VIG8_HEADERS:
        raise ValueError(f"2014 TR VI.G8 headers moved: {header!r}")
    scenario = None
    historical: dict[int, float] = {}
    projected: dict[int, dict[str, float]] = {}
    for row in rows:
        if row and row[0] in {
            "Historical data:",
            "Intermediate:",
            "Low-cost:",
            "High-cost:",
        }:
            scenario = row[0].rstrip(":")
            continue
        if not row or not re.fullmatch(r"(19|20)\d\d", row[0]):
            continue
        year = int(row[0])
        assets = _money(row[10])
        if assets is None:
            continue
        if scenario == "Historical data":
            historical[year] = assets
        elif scenario == "Intermediate":
            projected[year] = {
                "non_interest_income": _money(row[2]),
                "interest_income": _money(row[4]),
                "total_income": _money(row[6]),
                "cost": _money(row[8]),
                "assets_end_of_year": assets,
            }

    a3_table = _table_with_caption(SUPPLEMENT_4A, A3_CAPTION_MARKERS)
    a3_rows = _html_rows(a3_table)
    a3_header = next(row for row in a3_rows if tuple(row) == A3_HEADER_0)
    a3_index = a3_rows.index(a3_header)
    a3_sub = a3_rows[a3_index + 1]
    if a3_sub[-1] != A3_ASSETS_LABEL:
        raise ValueError(f"Supplement 4.A3 assets label moved: {a3_sub[-1]!r}")
    realized: dict[int, float] = {}
    for row in a3_rows[a3_index + 2 :]:
        if not row or not re.fullmatch(r"(19|20)\d\d", row[0]):
            if realized and (not row or not row[0].isdigit()):
                break
            continue
        if len(row) != len(a3_sub) + 1:
            break
        value = _money(row[-1])
        if value is not None:
            realized[int(row[0])] = value / 1000.0  # millions -> billions

    concept_years = sorted(set(historical) & set(realized))
    if not concept_years:
        raise ValueError("no overlap between TR historical and 4.A3 rows")
    concept_check = [
        {
            "year": year,
            "tr_historical_billions": historical[year],
            "supplement_4a3_billions": round(realized[year], 3),
            "abs_gap_billions": round(
                abs(historical[year] - realized[year]), 3
            ),
            "rel_gap": round(
                abs(historical[year] - realized[year]) / realized[year], 6
            ),
        }
        for year in concept_years
    ]
    worst = max(row["rel_gap"] for row in concept_check)
    if worst > A3_CONCEPT_MAX_REL_GAP:
        raise ValueError(
            "TR VI.G8 vs Supplement 4.A3 concept equivalence REFUTED: "
            f"max relative gap {worst:.6f} exceeds "
            f"{A3_CONCEPT_MAX_REL_GAP}. The two sides are not the same "
            "statutory quantity -- check that the 4.A3 COMBINED table "
            "was selected and not 4.A1 (OASI only) or 4.A2 (DI only)."
        )
    scored_years = [
        year
        for year in sorted(projected)
        if year in realized and VINTAGE_BOUNDARY_YEAR < year
    ]
    deviations = []
    for year in scored_years:
        forecast = projected[year]["assets_end_of_year"]
        actual = realized[year]
        deviations.append(
            {
                "year": year,
                "horizon_from_vintage_boundary_2014": (
                    year - VINTAGE_BOUNDARY_YEAR
                ),
                "tr2014_intermediate_projection_billions": forecast,
                "realized_billions": round(actual, 3),
                "log_ratio_abs": round(abs(math.log(forecast / actual)), 6),
                "signed_relative_error": round(
                    (forecast - actual) / actual, 6
                ),
            }
        )
    return {
        "anchor_id": "tr2014_official_baseline_trust_fund_assets",
        "status": "REPORTED EXTERNAL ANCHOR, NOT GATED",
        "what_it_is": (
            "the official forecaster's own pseudo-vintage-2014 "
            "retrodiction. The 2014 OASDI Trustees Report (published "
            "2014-07-28) projected combined OASI+DI assets at end of "
            "year under intermediate assumptions; the realized values "
            "are printed in the Annual Statistical Supplement, 2025, "
            "Table 4.A3. This is the strongest available external "
            "reference for what deviation an established projection "
            "system achieves on this arm at the same vintage boundary "
            "gate_m6 refits on."
        ),
        "why_not_gated": (
            "it grades SSA's model, not this repository's. It bounds "
            "expectations and sets the referee round's frame of "
            "reference; it certifies nothing here."
        ),
        "vintage_boundary_year": VINTAGE_BOUNDARY_YEAR,
        "sources": {
            "forecast": {
                "publication": "2014 OASDI Trustees Report",
                "table": "VI.G8",
                "scenario": "intermediate",
                "publication_date": "2014-07-28",
                "source_file": str(TR2014_VIG8.relative_to(REPO)),
                "source_sha256": _sha256(TR2014_VIG8),
                "unit": "billions of current dollars",
                "headers_verified": list(VIG8_HEADERS),
            },
            "realized": {
                "publication": "Annual Statistical Supplement, 2025",
                "table": "4.A3",
                "table_title": (
                    "Combined Old-Age and Survivors Insurance (OASI) and "
                    "Disability Insurance (DI) Trust Funds: Receipts, "
                    "expenditures, and assets"
                ),
                "table_bound_by": (
                    "CAPTION, not header shape: Tables 4.A1 (OASI only) "
                    "and 4.A2 (DI only) print an identical header row in "
                    "the same document, so header matching alone selects "
                    "OASI and silently compares a combined-fund forecast "
                    "against an OASI-only realization"
                ),
                "caption_markers_verified": list(A3_CAPTION_MARKERS),
                "column": A3_ASSETS_LABEL,
                "source_file": str(SUPPLEMENT_4A.relative_to(REPO)),
                "source_sha256": _sha256(SUPPLEMENT_4A),
                "unit": "millions of current dollars (converted to billions)",
                "headers_verified": list(A3_HEADER_0) + [A3_ASSETS_LABEL],
            },
        },
        "concept_equivalence_evidence": {
            "rule": (
                "concept equivalence is DEMONSTRATED, not asserted: the "
                "2014 TR's own HISTORICAL rows and the 2025 Supplement's "
                "realized rows are compared on the overlapping years. "
                "Agreement to the TR's printed billions is the evidence "
                "that 'Assets at end of year' (VI.G8) and 'Amount at end "
                "of year' (4.A3) are the same statutory quantity."
            ),
            "n_overlap_years": len(concept_check),
            "overlap_years": (
                [concept_years[0], concept_years[-1]] if concept_years else []
            ),
            "max_abs_gap_billions": (
                max(row["abs_gap_billions"] for row in concept_check)
                if concept_check
                else None
            ),
            "max_rel_gap": round(worst, 6),
            "max_rel_gap_allowed": A3_CONCEPT_MAX_REL_GAP,
            "guard": (
                "the builder RAISES if this is exceeded; the anchor is "
                "never published with mixed concepts. The guard has "
                "already fired once in development, catching a header-"
                "shape table match that selected 4.A1 (OASI only) "
                "against a combined-fund forecast."
            ),
            "rows": concept_check,
        },
        "official_baseline_deviations": deviations,
        "summary": {
            "n_scored_years": len(deviations),
            "mean_log_ratio_abs": (
                round(
                    float(
                        np.mean([row["log_ratio_abs"] for row in deviations])
                    ),
                    6,
                )
                if deviations
                else None
            ),
            "max_log_ratio_abs": (
                round(max(row["log_ratio_abs"] for row in deviations), 6)
                if deviations
                else None
            ),
            "sign_note": (
                "every signed error is recorded; a one-signed error set "
                "is a bias statement about the official baseline, not "
                "noise"
            ),
        },
        "projected_series_reported": {
            str(year): projected[year] for year in sorted(projected)
        },
    }


def cola_anchor() -> dict:
    document = json.loads(COLA.read_text())
    data = {
        int(year): float(value) for year, value in document["data"].items()
    }
    years = sorted(data)
    changes = [
        abs(data[year] - data[year - 1]) for year in years if year - 1 in data
    ]
    return {
        "anchor_id": "cola_determination_history",
        "status": "REPORTED CONTEXT, NOT GATED",
        "series": document["series"],
        "vintage_year": document["vintage_year"],
        "source_url": document["provenance"]["source_url"],
        "content_sha256": document["provenance"]["content_sha256"],
        "years": [years[0], years[-1]],
        "n_years": len(years),
        "why_not_gated": (
            "the COLA is a STATUTORY computation from published CPI-W, "
            "so it belongs to scoring surface 4 (statutory resolution), "
            "not surface 3 (retrodiction). This repository fits no "
            "CPI-W model, so there is no model-side quantity to grade. "
            "It is carried here because any T*-refit projection of "
            "benefit LEVELS past T* must assume future COLAs, so this "
            "series is a named component of the retrodiction arm's "
            "error budget."
        ),
        "vintage_class": (
            "immutable_series_single_vintage: one post-T* artifact, but "
            "an automatic determination is final when made and is not "
            "revised, so the <=T* rows carry no VALUE leakage. "
            "SPECIFICATION leakage is not excluded and is logged."
        ),
        "one_year_absolute_change": {
            "mean_percentage_points": round(float(np.mean(changes)), 4),
            "sd_percentage_points": round(float(np.std(changes)), 4),
            "max_percentage_points": round(float(max(changes)), 4),
            "n": len(changes),
        },
    }


def effective_rates_anchor() -> dict:
    document = json.loads(EFFECTIVE_RATES.read_text())
    return {
        "anchor_id": "effective_interest_rates_2014_vintage",
        "status": "AVAILABLE, NOT USED",
        "series": document["series"],
        "vintage_year": document["vintage_year"],
        "years": [
            document["validation"]["first_observation_year"],
            document["validation"]["latest_observation_year"],
        ],
        "source_url": document["provenance"]["source_url"],
        "source_sha256": document["provenance"]["source_sha256"],
        "why_not_used": (
            "a <=T* external INPUT to trust-fund arithmetic, not an "
            "output this repository projects. Recorded so the referee "
            "round can see it was considered and set aside."
        ),
    }


def draw_noise_context() -> dict:
    """Model-side draw dispersion, read from committed evidence."""
    document = json.loads(ANCHOR_CONTEXT_REPORT.read_text())
    by_comparison: dict[str, list[float]] = {}
    for result in document["results"]["comparison_results"]:
        if not result.get("evaluated"):
            continue
        for annual in result["annual_rows"]:
            mean = annual["comparison_mean"]
            sd = annual["comparison_sample_sd"]
            if mean:
                by_comparison.setdefault(result["comparison_id"], []).append(
                    sd / mean
                )
    return {
        "status": "REPORT-ONLY CONTEXT, NOT A FLOOR THE GATE MAY USE",
        "source": {
            "artifact": "runs/anchor_context_report_v1.json",
            "sha256": _sha256(ANCHOR_CONTEXT_REPORT),
            "schema_version": document["schema_version"],
        },
        "what_it_measures": (
            "the sample sd, across the committed draws, of each ratified "
            "scale-invariant comparison in the anchor-context report -- "
            "the deployed engine's own Monte-Carlo dispersion on exactly "
            "the comparison shapes the retrodiction arm would score."
        ),
        "why_not_a_floor": (
            "it is measured on the FULL-vintage deployed engine, not on "
            "a T*-refit, and that report's ratified certifies_nothing "
            "forbids it creating a floor: 'This report creates no gate, "
            "floor, threshold, or verdict.' It is carried so the referee "
            "round can see whether a candidate's draw noise would swamp "
            "the measurement floor. A T*-refit draw floor is a NAMED "
            "PREREQUISITE, not a substitute."
        ),
        "by_comparison": {
            comparison_id: {
                "mean_log_scale_sd": round(float(np.mean(values)), 6),
                "max_log_scale_sd": round(float(max(values)), 6),
                "n_years": len(values),
            }
            for comparison_id, values in sorted(by_comparison.items())
        },
    }


# --------------------------------------------------------------------------
# the specification-leakage half of the deviation log
# --------------------------------------------------------------------------
def specification_leakage_log() -> list[dict]:
    return [
        {
            "id": "outcome_knowledge_in_specification",
            "class": "specification_leakage_unpinned",
            "detail": (
                "every module specification in this repository was "
                "chosen after 2014-2022 was observable. A T*-refit "
                "re-estimates PARAMETERS on <=T* data, but its "
                "STRUCTURE was selected with the holdout visible. "
                "gate_m6 carries this exact disclosure for its own "
                "surface (not_certified.spec_selection_in_sample)."
            ),
            "consequence": (
                "a retrodiction PASS is conditional on this; it may "
                "never be stated as an unconditional out-of-sample "
                "result"
            ),
        },
        {
            "id": "cell_and_rule_selection_after_the_fact",
            "class": "specification_leakage_unpinned",
            "detail": (
                "the cells in this artifact, the naive rules, T*, the "
                "shock partition and the exclusion of provisional "
                "terminal rows were all chosen in 2026 with 2014-2022 "
                "in hand. The settlement finding in particular was "
                "DISCOVERED from the vintage pair, not pre-registered."
            ),
            "consequence": (
                "pre-registration of the arm happens at the lock "
                "ceremony, on this artifact; nothing here is itself "
                "pre-registered"
            ),
        },
        {
            "id": "reprinted_not_contemporaneous_tables",
            "class": "revisable_series_single_vintage",
            "detail": (
                "the covered-earnings (Supplement 2025 Table 4.B11) and "
                "disability (DI ASR 2023) series are read as REVISED "
                "today, not as printed at T*. A true-vintage score would "
                "use the edition on the shelf at T*. "
                "floor_vintage_revision measures the size of that "
                "substitution for the ONE family where both printings "
                "are held; for the others it is UNMEASURED."
            ),
            "consequence": (
                "these families are report-only in this artifact; a "
                "second staged printing would promote them"
            ),
        },
        {
            "id": "rolling_origin_rows_not_contemporaneous_printings",
            "class": "true_vintage_artifact_partial",
            "detail": (
                "the rolling pseudo-vintage origins 2004-2011 fit rows "
                "as printed in the 2014 Supplement, not as printed in "
                "the Supplement of that origin year. By the settlement "
                "finding those rows were already settled by 2014, so "
                "the substitution is expected to be value-free -- but "
                "the repository holds no pre-2014 printing with which "
                "to verify it."
            ),
            "consequence": (
                "the REGISTERED origin T*=2012 uses only rows the 2014 "
                "printing genuinely carried; the rolling origins supply "
                "dispersion and inherit this unverified substitution"
            ),
        },
        {
            "id": "psid_panel_release_revisions",
            "class": "revisable_series_single_vintage",
            "detail": (
                "the PSID waves the engine fits are the current public "
                "releases, which incorporate post-T* corrections and "
                "re-releases. The repository pins file digests, not "
                "release dates contemporaneous with T*."
            ),
            "consequence": (
                "applies to any candidate run on this arm, not to the "
                "truth side priced here"
            ),
        },
        {
            "id": "claiming_projection_is_the_persistence_rule_today",
            "class": "candidate_side_disclosure",
            "detail": (
                "populace_dynamics.claiming._resolve_year snaps an "
                "out-of-range entitlement year to the nearest covered "
                "year, so a T*-refit that reads claiming shares through "
                "the module projects them by holding the last covered "
                "row constant. The module's claiming projection IS the "
                "persistence rule. A candidate that simply calls it "
                "would score EXACTLY the naive baseline, by "
                "construction, and must not be graded as skill. "
                "runs/claiming_reference_v1.json already measured this "
                "rule out of sample within one vintage (fit 1998-2019, "
                "predict 2020-2022: nearest-year max abs deviation 3.2 "
                "pp vs linear-trend 8.1623 pp)."
            ),
            "consequence": (
                "the ceremony must require a candidate to declare "
                "whether its claiming path is behavioural or carried, "
                "and grade a carried path as baseline, not as skill"
            ),
        },
        {
            "id": "cola_and_wage_index_are_realized_inputs",
            "class": "immutable_series_single_vintage",
            "detail": (
                "benefit levels past T* depend on the COLA and the "
                "average wage index. A T*-refit that reads realized "
                "post-T* COLAs is leaking; one that assumes the "
                "T*-vintage Trustees path is not. The contract must say "
                "which. ssa_cola_history.json (vintage 2022) and "
                "ssa_tr_ultimate_assumptions_2014.json (vintage 2014) "
                "are both staged, so either choice is executable."
            ),
            "consequence": (
                "an unresolved contract question the ceremony must "
                "settle before any candidate runs"
            ),
        },
    ]


def not_computable_register(covered_provenance: dict) -> list[dict]:
    return [
        {
            "item": "vintage-revision floor for every non-claiming family",
            "families": ["covered_earnings", "disability"],
            "reason": (
                "the repository holds exactly ONE publication vintage of "
                "Table 4.B11 (source_document_id "
                f"{covered_provenance['source_document_id']}) and ONE of "
                "the DI Annual Statistical Report (2023). A revision "
                "floor needs two independent publications of the same "
                "cell; a single vintage supplies none."
            ),
            "unblocks_if": (
                "a second Supplement edition covering the same table and "
                "years is staged (offline HTML capture plus sha pin, the "
                "path scripts/extract_ssa_claim_ages_2014.py already "
                "walked for 6.B5.1). Cheap and mechanical; no new "
                "methodology."
            ),
        },
        {
            "item": "beneficiary counts by type and average benefits",
            "reason": (
                "docs/calibration-targets.md lists both as Tier 1 "
                "(Supplement Table 5.A1 and the benefit tables), but "
                "NEITHER vintage of those tables is staged in "
                "data/external. There is no fit source and no "
                "resolution source in the repository."
            ),
            "unblocks_if": (
                "Table 5.A1 is staged at two vintages, one <= 2014"
            ),
        },
        {
            "item": "DI incidence and awards as a retrodiction cell",
            "reason": (
                "only the 2023-vintage DI Annual Statistical Report is "
                "staged. The DI stock and termination cells here are "
                "read from that single printing, so their pre-T* rows "
                "are post-T* revisions of themselves."
            ),
            "unblocks_if": (
                "a <= 2014-vintage DI Annual Statistical Report is "
                "staged alongside it"
            ),
        },
        {
            "item": (
                "the 2014 Trustees Report's own year-by-year projections "
                "as gated cells"
            ),
            "reason": (
                "Table VI.G8's committed HTML carries intermediate "
                "projections for 1970-2090 and this artifact reads the "
                "ASSETS column as a REPORTED anchor. Promoting the "
                "other columns to cells needs same-concept realized "
                "counterparts: TR 'Cost' includes administrative "
                "expenses and the Railroad Retirement interchange, and "
                "'Non-interest income' includes taxation of benefits and "
                "general-fund reimbursements. Supplement 4.A3 prints "
                "those components separately, but the committed "
                "level-anchor extraction registered only benefit "
                "payments and net payroll-tax contributions. Only the "
                "ASSETS concept closes end to end."
            ),
            "unblocks_if": (
                "the 4.A3 component columns are registered in a "
                "successor anchor vintage, or a later Trustees Report's "
                "HISTORICAL rows are staged (same-concept by "
                "construction)."
            ),
        },
        {
            "item": "model-side pseudo-vintage projections (every cell)",
            "reason": (
                "this artifact scores no candidate, by construction and "
                "by instruction. A retrodiction VERDICT needs a T*-refit "
                "projection of each cell; none is run here. That is the "
                "gate-2 floor convention: the floor prices the truth "
                "side, the candidate is registered and scored later."
            ),
            "unblocks_if": (
                "a candidate is registered on issue #42 and run under "
                "the locked contract."
            ),
        },
        {
            "item": "model-side T*-refit DRAW floor",
            "reason": (
                "the only committed model draw dispersion "
                "(runs/anchor_context_report_v1.json) is measured on the "
                "FULL-vintage deployed engine, and that report's "
                "ratified certifies_nothing forbids it creating a floor."
            ),
            "unblocks_if": (
                "the ceremony authorizes a candidate-blind T*-refit "
                "draw-dispersion run whose ONLY output is the dispersion "
                "(no scored cell), the gate_m6 v1/v2/v3 floor pattern."
            ),
        },
        {
            "item": "tier-2 arm (the live annual-resolution arm)",
            "reason": (
                "it binds FUTURE annual SSA publications on named "
                "resolution rules; its clock cannot start until "
                "thresholds are locked. Out of scope here by design -- "
                "this artifact floors the retrodiction arm ONLY."
            ),
            "unblocks_if": "gate_3 thresholds lock.",
        },
        {
            "item": (
                "a runner-safe claiming reader for post-2013 years "
                "against the 2014 vintage (LATENT TRAP)"
            ),
            "reason": (
                "populace_dynamics.claiming.MIN_YEAR / MAX_YEAR are "
                "module constants pinned to the 2023 printing "
                f"({claiming.MIN_YEAR}-{claiming.MAX_YEAR}). "
                "claim_age_distribution's nearest-year resolver "
                "therefore treats 2014-2022 as IN RANGE even when the "
                "loaded reference is the 2014 vintage, and then raises a "
                "bare KeyError from ClaimAgeReference.row. This builder "
                "reads rows directly and never calls the resolver. Any "
                "future gate-3 runner must do the same or the constants "
                "must become per-reference."
            ),
            "unblocks_if": (
                "MIN_YEAR / MAX_YEAR are derived from the loaded "
                "reference rather than pinned at module scope"
            ),
        },
    ]


def horizon_monotonicity(window: dict, stability: dict) -> dict:
    """Does the naive baseline grow with horizon? Per cell, and pooled.

    A forward-projection gate whose tolerance SHRINKS with horizon is
    inverted: it would be easier to pass at h=7 than at h=2. Under
    instrument B the tolerance inherits the baseline's shape, so this
    has to be measured and put in front of the referee rather than
    assumed.
    """
    clean = [f"h{h}" for h in range(2, 8)]
    per_cell, matrix = {}, []
    for key, entry in sorted(window.items()):
        if not stability[key]["draft_gate_eligible"]:
            continue
        row = [
            entry["by_horizon"][h]["basis_value"]
            for h in clean
            if h in entry["by_horizon"]
            and entry["by_horizon"][h]["basis"]
            == "registered_origin_deviation"
        ]
        if len(row) != len(clean):
            continue
        matrix.append(row)
        per_cell[key] = {
            "by_horizon": dict(zip(clean, row, strict=True)),
            "increases_h2_to_h7": bool(row[-1] >= row[0]),
            "monotone_non_decreasing": all(
                b >= a for a, b in zip(row, row[1:], strict=False)
            ),
        }
    array = np.asarray(matrix, dtype=float)
    pooled = {
        horizon: round(float(array[:, index].mean()), 6)
        for index, horizon in enumerate(clean)
    }
    values = list(pooled.values())
    increasing = sum(
        1 for row in per_cell.values() if row["increases_h2_to_h7"]
    )
    return {
        "status": "MEASURED FINDING AND AN OPEN REFEREE QUESTION",
        "clean_horizons": clean,
        "pooled_mean_across_eligible_cells": pooled,
        "pooled_is_monotone_non_decreasing": all(
            b >= a for a, b in zip(values, values[1:], strict=False)
        ),
        "n_eligible_cells": len(per_cell),
        "n_increasing_h2_to_h7": increasing,
        "n_decreasing_h2_to_h7": len(per_cell) - increasing,
        "finding": (
            "horizon growth is a POPULATION property, not a per-cell "
            "law. Pooled across the eligible cells the naive baseline "
            "rises monotonically with horizon, but individual cells "
            "split: cells whose published share trends (age62, age66, "
            "age67_69, age70plus, average age) grow with horizon, while "
            "cells whose share is flat or mean-reverting (age64, age65, "
            "disability_conversion) do NOT."
        ),
        "referee_question": (
            "under instrument B the tolerance inherits the baseline's "
            "shape, so for the decreasing cells the DRAFT tolerance is "
            "TIGHTER at h=7 than at h=2. That is defensible -- the "
            "naive rule really is more accurate there, so beating it is "
            "a harder test -- but it is the opposite of what a reader "
            "of a 'forward projection' gate will expect. The ceremony "
            "must decide explicitly: take the shape as measured, or "
            "require a non-decreasing envelope "
            "(tolerance(h) = rho * max over h' <= h of the baseline). "
            "Both are computable from what is committed here; this "
            "artifact takes neither."
        ),
        "non_decreasing_envelope_if_adopted": {
            key: {
                horizon: round(
                    DRAFT_RHO
                    * max(list(row["by_horizon"].values())[: index + 1]),
                    DRAFT_ROUNDING,
                )
                for index, horizon in enumerate(clean)
            }
            for key, row in per_cell.items()
        },
        "per_cell": per_cell,
    }


def recommended_gated_surface(window: dict, stability: dict) -> dict:
    """The (cell, horizon) pairs this artifact would put in front of a
    referee round as the gated surface, and the ones it would not."""
    gated, report_only = [], []
    for key, entry in sorted(window.items()):
        eligible = stability[key]["draft_gate_eligible"]
        for horizon, row in entry["by_horizon"].items():
            cell = f"{key}@{horizon}"
            if not eligible:
                report_only.append(
                    {
                        "cell": cell,
                        "reason": "cell_not_draft_gate_eligible",
                    }
                )
            elif row["basis"] != "registered_origin_deviation":
                report_only.append(
                    {
                        "cell": cell,
                        "reason": (
                            "no_clean_target_at_the_registered_origin "
                            "(excluded provisional row or shock window)"
                        ),
                    }
                )
            elif row["room_for_skill"] is not True:
                report_only.append(
                    {"cell": cell, "reason": "no_room_for_skill"}
                )
            else:
                gated.append(cell)
    return {
        "status": "A PROPOSAL FOR THE REFEREE ROUND, NOT A GATED SET",
        "rule": (
            "a (cell, horizon) pair is proposed for the gated surface "
            "only if the cell is draft-eligible, the REGISTERED origin "
            "T*=2012 has a clean target year at that horizon (so the "
            "tolerance basis is the number a candidate actually "
            "competes against rather than a rolling-origin fallback), "
            "and the skill window is non-empty."
        ),
        "clean_horizon_band": "h2-h7, target entitlement years 2014-2019",
        "why_h1_is_excluded": (
            "the registered origin's h=1 target is 2013, the provisional "
            "terminal row of the fit vintage, excluded by "
            "settlement_analysis"
        ),
        "why_h8_h9_are_excluded": (
            "their targets are 2020 and 2021, the "
            "exogenous_shock_outside_model_class window gate_m6 "
            "partitions out of every gated set"
        ),
        "n_gated": len(gated),
        "n_report_only": len(report_only),
        "gated": gated,
        "report_only": report_only,
    }


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------
def build() -> dict:
    registry = cell_registry()

    claim_2014 = claiming_series(CLAIM_2014)
    claim_2023 = claiming_series(CLAIM_2023)
    covered, covered_provenance = covered_earnings_series()
    disability, di_provenance = di_series()

    # The scoring-side series is always the LATEST vintage in hand.
    latest: dict[str, dict[int, float]] = {}
    latest.update(claim_2023)
    latest.update(covered)
    latest.update(disability)

    rounding_floors = {
        key: publication_rounding_floor(spec, latest[key])
        for key, spec in registry.items()
        if key in latest
    }
    revision_floors, revision_log = vintage_revision_floor(
        registry, claim_2014, claim_2023
    )
    settlement = settlement_analysis(registry, claim_2014, claim_2023, latest)

    baselines = {}
    baselines.update(
        naive_baseline(
            registry,
            claim_2014,
            claim_2023,
            family="claiming",
            excluded_targets=EXCLUDED_YEARS,
            fit_source=(
                "the 2014 Supplement printing -- a TRUE pre-T* artifact "
                "that cannot contain post-2013 rows"
            ),
        )
    )
    for family, series, last_year in (
        ("covered_earnings", covered, max(max(s) for s in covered.values())),
        ("disability", disability, max(max(s) for s in disability.values())),
    ):
        baselines.update(
            naive_baseline(
                registry,
                series,
                series,
                family=family,
                excluded_targets=(last_year,),
                fit_source=(
                    "the SAME single printing used for resolution; its "
                    "pre-T* rows are post-T* revisions of themselves "
                    "(deviation class revisable_series_single_vintage)"
                ),
            )
        )

    window = skill_window(
        registry, rounding_floors, revision_floors, baselines
    )
    stability = cell_stability(registry, revision_floors, baselines, window)

    reference_values = {
        key: {
            "resolution_vintage_series": {
                str(year): value for year, value in sorted(latest[key].items())
            },
            "n_years": len(latest[key]),
            "years": [min(latest[key]), max(latest[key])],
        }
        for key in sorted(latest)
        if key in registry
    }

    eligible = sorted(
        key for key, row in stability.items() if row["draft_gate_eligible"]
    )

    return {
        "schema_version": "gate3_retrodiction_floors.v1",
        "run": "gate3_retrodiction_floors_v1",
        "status": (
            "PRE-LOCK EVIDENCE - NOT RATIFIED. gates.yaml gate_3 carries "
            "locked: false and no thresholds; this artifact writes none, "
            "reads no gate, and scores no candidate. v1 is a pinning "
            "event, not a ratification."
        ),
        "reported_anchor_not_gated": True,
        "component": (
            "gate 3 RETRODICTION ARM: pseudo-vintage backtests of tier-2 "
            "near-term components against SSA administrative tables "
            "already published and already committed to this repository"
        ),
        "arm_scope": {
            "in_scope": "the retrodiction arm only",
            "out_of_scope": (
                "the tier-2 live-resolution arm, which binds FUTURE "
                "annual SSA publications and cannot start its clock "
                "until thresholds lock"
            ),
            "gate_3_text_verbatim": (
                "Tier-2 near-term components resolve against "
                "administrative publications on named resolution rules; "
                "retrodiction backtests grade as pseudo-vintage with a "
                "published deviation log."
            ),
            "gate_3_locked": False,
        },
        "purpose": (
            "Gate-3 pre-lock evidence for the retrodiction arm: the "
            "committed reference values, the settlement analysis that "
            "fixes the protocol windows, three quantities (publication "
            "rounding F0, the VINTAGE-DISJOINT revision floor F1, and "
            "the pseudo-vintage naive baseline F2), the published "
            "deviation log the gate description requires, honest "
            "external anchors, and a DRAFT tolerance basis under two "
            "instruments. Reads no gate and changes no gate on its own. "
            "The lock ceremony comes after. See draft_thresholds_note "
            "(NOT RATIFIED)."
        ),
        "definitions": {
            "retrodiction": {
                "source": "docs/scoring-and-resolution.md, surface 3",
                "quote": (
                    "build the panel from data vintages available at "
                    "time T, project forward, and score against realized "
                    "outcomes at T+k"
                ),
            },
            "pseudo_vintage": {
                "source": "paper/paper.qmd, scoring surface 3",
                "quote": (
                    "pre-registry history is a reconstruction problem -- "
                    "survey redesigns, revised administrative tables, "
                    "re-released panels -- so the protocol grades "
                    "pre-registry backtests as pseudo-vintage, with a "
                    "published log of deviations from true vintage, and "
                    "no registry pins specification leakage: a "
                    '"2005-vintage" model built today knows 2008 '
                    "happened, and the protocol says so"
                ),
            },
            "deviation_log": {
                "source": "paper/paper.qmd, scoring surface 3",
                "quote": "a published log of deviations from true vintage",
                "operationalization": (
                    "this artifact publishes TWO deviation logs, because "
                    "the paper's sentence names two distinct deviations. "
                    "(1) deviation_log_vintage_revision: every cell-year "
                    "where the earlier and later SSA publications of the "
                    "same fact disagree -- the 'revised administrative "
                    "tables' clause, MEASURED. (2) "
                    "deviation_log_specification_leakage: the ways a "
                    "T*-refit built today is not a true T* vintage -- "
                    "the 'knows 2008 happened' clause, ENUMERATED with a "
                    "deviation class and a consequence per entry. A "
                    "retrodiction score is conditional on both."
                ),
                "deviation_classes": {
                    "true_vintage_artifact": (
                        "the fit source is an artifact published at or "
                        "before the vintage boundary whose content "
                        "cannot contain post-boundary information "
                        "(6.B5.1 as printed in the 2014 Supplement). "
                        "Strongest available class."
                    ),
                    "true_vintage_artifact_partial": (
                        "a true pre-boundary artifact used at an origin "
                        "EARLIER than its own publication, so its rows "
                        "are settled-but-not-contemporaneous printings."
                    ),
                    "immutable_series_single_vintage": (
                        "one post-boundary artifact, but the fit rows "
                        "are final when made and not revisable, so no "
                        "VALUE leakage; specification leakage remains."
                    ),
                    "revisable_series_single_vintage": (
                        "one post-boundary artifact whose fit rows may "
                        "have been revised with post-boundary "
                        "information. Not gate-eligible."
                    ),
                    "specification_leakage_unpinned": (
                        "unmeasurable by construction; named, never "
                        "priced. Applies to the whole arm."
                    ),
                },
            },
            "tier_2": {
                "source": "docs/domains-of-validity.md, Tier 2",
                "quote": (
                    "beneficiary counts by type, average benefits, "
                    "covered earnings and taxable payroll, claiming-age "
                    "distributions, disability incidence. These "
                    "quantities resolve against administrative "
                    "publications on an annual cycle"
                ),
            },
            "naive_baseline_requirement": {
                "source": "paper/paper.qmd, scoring surface 2",
                "quote": (
                    "each cell pre-specifies the naive baseline it must "
                    "beat"
                ),
            },
        },
        "protocol": {
            "vintage_boundary_year": VINTAGE_BOUNDARY_YEAR,
            "vintage_boundary_source": (
                "populace_dynamics.engine.refit.BOUNDARY_YEAR, the same "
                "constant gate_m6 refits on; "
                "engine.refit.validate_external_vintage raises on any "
                "external reference whose vintage exceeds it, and "
                "tests/test_m7_external_vintage_boundary.py pins that "
                "refusal. The 2014 6.B5.1 printing was staged for "
                "exactly this boundary."
            ),
            "T_star": T_STAR,
            "T_star_rationale": (
                "the last SETTLED entitlement row of the 2014 printing. "
                "T* is a DATA-CONTENT cutoff and sits one year inside "
                "the vintage AVAILABILITY cutoff, because the 2013 row "
                "the 2014 Supplement printed was provisional -- see "
                "settlement_analysis."
            ),
            "fit_window": [FIT_FIRST_YEAR, T_STAR],
            "scored_window": [SCORED_FIRST_YEAR, SCORED_LAST_YEAR],
            "excluded_years": {
                str(TERMINAL_ROW_2014_VINTAGE): (
                    "provisional terminal row of the FIT vintage; "
                    "neither trusted as fit input nor scored as a clean "
                    "holdout"
                ),
                str(TERMINAL_ROW_2023_VINTAGE): (
                    "provisional terminal row of the RESOLUTION vintage; "
                    "a moving target"
                ),
            },
            "shock_window": list(SHOCK_YEARS),
            "shock_window_rule": (
                "gate_m6 partitions 2020-2022 out of every gated set as "
                "exogenous_shock_outside_model_class and publishes it as "
                "a diagnostic. The same discipline binds here: shock "
                "years are measured and reported separately and enter no "
                "pooled baseline."
            ),
            "clean_scored_years": [
                year
                for year in range(SCORED_FIRST_YEAR, SCORED_LAST_YEAR + 1)
                if year not in SHOCK_YEARS
            ],
            "rolling_origins": [ROLLING_ORIGIN_FIRST, T_STAR],
            "rolling_origin_rationale": (
                "the REGISTERED origin T*=2012 yields one projection per "
                "horizon and therefore no dispersion. Rolling the origin "
                "back over the fit vintage's settled rows supplies the "
                "replications the seeds 0-4 blocks summarize. Every "
                "rolling origin fits only rows at or before itself."
            ),
            "horizons": list(HORIZONS),
        },
        "settlement_analysis": settlement,
        "floor_design": {
            "person_disjoint_unavailable_in_principle": (
                "gate_1 / gate_2 / gate_2b / gate_2c / gate_m4 / gate_m6 "
                "price a PERSON-DISJOINT half-split floor because their "
                "truth side is a SAMPLE: two disjoint halves of the "
                "source frame are two independent realizations of one "
                "estimand. The retrodiction arm's truth side is an "
                "administrative CENSUS -- SSA's own note on 6.B5.1 reads "
                "'Master Beneficiary Record, 100 percent data (not a "
                "sample)'. There is no sampling frame to split, so a "
                "person-disjoint floor is unavailable IN PRINCIPLE, not "
                "merely unbuilt, and a bootstrap over published shares "
                "would invent a variance the source does not have."
            ),
            "vintage_disjoint_is_the_analogue": (
                "the analogue that preserves the meaning -- two "
                "independent realizations of one estimand differing only "
                "through the measurement process -- is the pair of "
                "PUBLICATION VINTAGES of the same table cell. The "
                "repository holds one genuine pair: Table 6.B5.1 as "
                "printed in the 2014 Supplement and as reprinted in the "
                "2023 Supplement. Disjointness is STRUCTURAL (two "
                "separate publications), which is stronger than the "
                "seeded disjointness of a half-split, not weaker."
            ),
            "seed_semantics": (
                "seeds 0-4 index five DISJOINT stride-5 blocks of the "
                "replication units, not RNG draws. For F1 a unit is a "
                "SETTLED publication year in the two-vintage overlap; "
                "for F2 it is a pseudo-vintage ORIGIN. Blocks are "
                "disjoint and exhaustive, so the across-seed sd is the "
                "between-block dispersion of the estimate -- the "
                "quantity round(mean + k*sd, 3) is meant to price. A "
                "deterministic exhaustive partition replaces a random "
                "one because the replication units are YEARS: they are "
                "ordered and trending, so a random split would make "
                "block composition, not the measurement process, the "
                "dominant source of across-seed variance."
            ),
            "three_quantities": {
                "F0_publication_rounding": (
                    "half the printed granularity. A share printed to "
                    "one decimal cannot be resolved below +/-0.05 pp. "
                    "Exact, deterministic, and a hard lower bound on "
                    "every other floor."
                ),
                "F1_vintage_revision": (
                    "the VINTAGE-DISJOINT measurement floor: |value in "
                    "vintage A - value in vintage B| for the same "
                    "(cell, year), computed on SETTLED rows only. It is "
                    "DEGENERATE for this arm -- see settlement_analysis "
                    "-- and that degeneracy is the finding, not a "
                    "failure of the measurement."
                ),
                "F2_naive_baseline": (
                    "NOT a floor. The skill CEILING: what the "
                    "information-null rules (persistence, linear trend) "
                    "achieve on exactly this protocol. A tolerance at or "
                    "above it certifies nothing, because a rule carrying "
                    "no information past T* already passes."
                ),
            },
            "skill_window_rule": (
                "DRAFT: a cell is gate-eligible only if a tolerance fits "
                "STRICTLY between max(F0, the F1-derived instrument) and "
                "F2. A cell whose measurement floor already meets what "
                "the naive rule achieves has no room for skill and is "
                "report-only. This is the retrodiction-arm analogue of "
                "gate_2's min_events_for_gate = 20 and gate_m6's "
                "ln(1.5) power cap."
            ),
            "seeds": list(SEEDS),
            "min_replications_for_gate": MIN_REPLICATIONS_FOR_GATE,
            "required_defined_seeds": REQUIRED_DEFINED_SEEDS,
        },
        "holdout_basis": [
            "ssa_supplement_6b5_1_vintage2014",
            "ssa_supplement_6b5_1_vintage2023",
            "ssa_supplement_2025_4b11",
            "di_asr_2023_tables_19_49",
        ],
        "data": {
            "claiming": {
                "reader": (
                    "populace_dynamics.claiming.load_claim_age_reference "
                    "(both vintages; the loader takes a path). Rows are "
                    "read through ClaimAgeReference.row, never through "
                    "claim_age_distribution -- see the MIN_YEAR/MAX_YEAR "
                    "trap in not_computable."
                ),
                "reader_commit": _reader_commit(
                    "src/populace_dynamics/claiming.py"
                ),
                "vintages": {
                    "2014": {
                        "path": str(CLAIM_2014.relative_to(REPO)),
                        "sha256": _sha256(CLAIM_2014),
                        "supplement_year": 2014,
                        "years": [1998, TERMINAL_ROW_2014_VINTAGE],
                        "role": "fit (pseudo-vintage)",
                        "deviation_class": "true_vintage_artifact",
                    },
                    "2023": {
                        "path": str(CLAIM_2023.relative_to(REPO)),
                        "sha256": _sha256(CLAIM_2023),
                        "supplement_year": 2023,
                        "years": [claiming.MIN_YEAR, claiming.MAX_YEAR],
                        "role": "resolution (realized truth)",
                        "deviation_class": "resolution_source",
                    },
                },
            },
            "covered_earnings": covered_provenance,
            "disability": di_provenance,
        },
        "cells": registry,
        "reference_values": reference_values,
        "floor_publication_rounding": rounding_floors,
        "floor_vintage_revision": {
            "method": (
                "VINTAGE-DISJOINT publication pair: SSA Annual "
                "Statistical Supplement 2014 Table 6.B5.1 vs Annual "
                "Statistical Supplement 2023 Table 6.B5.1, read through "
                "one reader "
                "(populace_dynamics.claiming.load_claim_age_reference). "
                "Per cell the floor statistic is the deviation between "
                "the two printed values under the cell's metric, over "
                "SETTLED overlap years only (the provisional terminal "
                "row 2013 is excluded and recorded separately); the "
                "reported mean/sd is taken over five DISJOINT stride-5 "
                "publication-year blocks (seed_semantics)."
            ),
            "seeds": list(SEEDS),
            "available_for_families": ["claiming"],
            "cells": revision_floors,
        },
        "naive_baseline_pseudo_vintage": {
            "method": (
                "For each pseudo-vintage origin T and horizon h, the "
                "information-null prediction for year T+h is formed from "
                "rows at or before T in the FIT source, and scored "
                "against the RESOLUTION source's realized value under "
                "the cell's metric. Two rules are registered: "
                "persistence (carry the value at T) and linear_trend "
                "(OLS on the fit rows, extrapolated). Excluded and shock "
                "years are partitioned out of the pooled statistics; "
                "mean/sd is taken over five DISJOINT stride-5 origin "
                "blocks. The REGISTERED origin T*=2012 is reported "
                "separately, per horizon, with its predictions and "
                "realized values in full."
            ),
            "not_a_noise_floor": (
                "this is the SKILL CEILING, not a floor. A tolerance at "
                "or above it certifies nothing."
            ),
            "seeds": list(SEEDS),
            "horizons": list(HORIZONS),
            "rules": sorted(NAIVE_RULES),
            "cells": baselines,
        },
        "skill_window": window,
        "cell_stability": stability,
        "deviation_log_vintage_revision": {
            "definition": (
                "every (cell, year) where the 2014 and 2023 Supplement "
                "printings of Table 6.B5.1 disagree, tagged by "
                "settlement regime. This is the 'revised administrative "
                "tables' half of the deviation log gate_3's description "
                "requires."
            ),
            "n_cell_years_compared": sum(
                floor["n_settled_years"] + 1
                for floor in revision_floors.values()
            ),
            "n_deviations": len(revision_log),
            "n_settled_deviations": sum(
                1 for row in revision_log if row["regime"] == "settled"
            ),
            "n_terminal_deviations": sum(
                1 for row in revision_log if row["regime"] == "terminal"
            ),
            "entries": revision_log,
        },
        "deviation_log_specification_leakage": {
            "definition": (
                "the 'a 2005-vintage model built today knows 2008 "
                "happened' half. These deviations from TRUE vintage are "
                "NAMED, not measured -- naming them is what "
                "'pseudo-vintage' means, and a retrodiction score is "
                "conditional on the whole list."
            ),
            "entries": specification_leakage_log(),
        },
        "external_anchor": {
            "tr2014_official_baseline": tr2014_projection_anchor(),
            "cola": cola_anchor(),
            "effective_interest_rates": effective_rates_anchor(),
            "level_anchor_crosscheck": level_anchor_crosscheck(covered),
        },
        "draw_noise_context": draw_noise_context(),
        "draft_thresholds": draft_thresholds(registry, window, stability),
        "draft_thresholds_note": (
            "DRAFT GATE-3 RETRODICTION-ARM EVIDENCE -- PRE-LOCK, NOT "
            "RATIFIED.\n\n"
            "This is the pre-lock evidence package for the gate_3 "
            "retrodiction arm, built the way runs/gate2_floors_v1.json "
            "was built before gate 2 locked. It changes no locked value, "
            "no model reads it, and it edits no line of gates.yaml. "
            "gate_3 stands at locked: false with no thresholds and stays "
            "there until a full lock ceremony runs: these floors -> "
            "thresholds with machine-bound derivations -> an adversarial "
            "referee round -> verification -> maintainer ratification by "
            "merge.\n\n"
            "STATISTIC. Per cell, the published administrative value for "
            "an entitlement or calendar year, and a candidate's "
            "pseudo-vintage projection of the same concept built only "
            "from information available at T*. Shares and ages are "
            "scored as an absolute deviation in published units; counts, "
            "ratios and rates as the absolute log ratio.\n\n"
            "THE CENTRAL FINDING. The vintage pair does not disagree "
            "diffusely; it disagrees in exactly one regime. Settled rows "
            "reproduce to the printed digit -- 1 of 240 share cell-years "
            "differs, by one granularity unit -- while every share in "
            "the provisional terminal row moves, by up to 1.1 pp. So the "
            "truth side of this arm carries NO measurable noise once "
            "provisional rows are excluded, and the gate-2 tolerance "
            "instrument, round(F1_mean + k*F1_sd, 3), degenerates onto "
            "the publication-rounding floor.\n\n"
            "TWO INSTRUMENTS, NEITHER ASSERTED. Instrument A is that "
            "gate-2 tolerance, committed so the ceremony can see the "
            "established convention degenerate here rather than take "
            "this artifact's word for it. Instrument B is the skill "
            "ratio rho against the pre-registered naive baseline, taken "
            "PER HORIZON at the registered origin -- the discipline "
            "paper/paper.qmd already imposes on resolving cells, and "
            "the only form that prices a FORWARD-PROJECTION gate, "
            "since the naive baseline's error grows monotonically "
            "with horizon. This artifact RECOMMENDS instrument B and "
            "DECIDES nothing; the referee round chooses the instrument "
            "and fixes its constant, exactly as gate 2's k was fixed.\n\n"
            "GATE-ELIGIBLE VS REPORT-ONLY. DRAFT eligibility needs five "
            "non-empty vintage blocks, at least 10 settled overlap "
            "years, at least 5 pseudo-vintage origins, a scale-invariant "
            "statistic (level cells are not gate-eligible pre-W1: the "
            "ratified anchor-context design publishes 'only the "
            "scale-invariant comparisons authorized below', and this "
            "repository's frame is not nationalized), and room for "
            "skill. Every cell failing any of these carries its blocking "
            "reasons in cell_stability.\n\n"
            "WHAT THIS PACKAGE DOES NOT DO. It scores no candidate, "
            "prices no model-side noise, and certifies nothing. The "
            "not_computable register names every gap and what would "
            "close it."
        ),
        "not_computable": not_computable_register(covered_provenance),
        "draft_gate_eligible_cells": eligible,
        "recommended_gated_surface": recommended_gated_surface(
            window, stability
        ),
        "horizon_monotonicity": horizon_monotonicity(window, stability),
        "roll_up": {
            "n_cells_defined": len(registry),
            "n_cells_with_reference_values": len(reference_values),
            "n_cells_with_vintage_revision_floor": len(revision_floors),
            "n_cells_with_naive_baseline": len(baselines),
            "n_draft_gate_eligible": len(eligible),
            "n_proposed_gated_cell_horizons": len(
                recommended_gated_surface(window, stability)["gated"]
            ),
        },
        "revision_pins": {
            "artifact_schema_version": "gate3_retrodiction_floors.v1",
            "claim_ages_2014_sha256": _sha256(CLAIM_2014),
            "claim_ages_2023_sha256": _sha256(CLAIM_2023),
            "covered_earnings_sha256": _sha256(COVERED_EARNINGS),
            "level_anchors_sha256": _sha256(LEVEL_ANCHORS),
            "di_asr_2023_sha256": _sha256(DI_TABLES),
            "cola_sha256": _sha256(COLA),
            "effective_rates_sha256": _sha256(EFFECTIVE_RATES),
            "tr2014_vi_g8_source_sha256": _sha256(TR2014_VIG8),
            "supplement2025_4a_source_sha256": _sha256(SUPPLEMENT_4A),
            "anchor_context_report_sha256": _sha256(ANCHOR_CONTEXT_REPORT),
            "builder": "scripts/build_gate3_retrodiction_floors.py",
        },
        "reproducibility": (
            "no wall clock and no environment block are written into "
            "this artifact, so re-running the builder on the same "
            "committed inputs reproduces it byte for byte. The "
            "measurement environment lives in the .env.json sidecar and "
            "the source digests in .inputs.json, the convention "
            "runs/tenure_floors_v1.json established. "
            "tests/test_gate3_retrodiction_floors.py rebuilds and "
            "compares rather than only pinning a digest."
        ),
    }


SOURCE_INPUTS = (
    (
        CLAIM_2014,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2014/6b.html",
    ),
    (
        CLAIM_2023,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2023/6b.html",
    ),
    (
        COVERED_EARNINGS,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2025/4b.html",
    ),
    (
        LEVEL_ANCHORS,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2025/",
    ),
    (DI_TABLES, "https://www.ssa.gov/policy/docs/statcomps/di_asr/2023/"),
    (COLA, "https://www.ssa.gov/oact/cola/colaseries.html"),
    (EFFECTIVE_RATES, "https://www.ssa.gov/oact/ProgData/effectiveRates.html"),
    (TR2014_VIG8, "https://www.ssa.gov/oact/TR/2014/lr6f8.html"),
    (
        SUPPLEMENT_4A,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2025/4a.html",
    ),
    (ANCHOR_CONTEXT_REPORT, "in-repository committed evidence artifact"),
)


def main() -> None:
    artifact = build()
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n")
    INPUT_SIDECAR.write_text(
        json.dumps(
            {
                "artifact": ARTIFACT.name,
                "status": "SOURCE_INPUT_DIGESTS",
                "source_inputs": [
                    {
                        "path": str(path.relative_to(REPO)),
                        "sha256": _sha256(path),
                        "bytes": path.stat().st_size,
                        "official_url": url,
                    }
                    for path, url in SOURCE_INPUTS
                ],
            },
            indent=2,
        )
        + "\n"
    )
    ENV_SIDECAR.write_text(
        json.dumps(
            {
                "artifact": ARTIFACT.name,
                "status": "MEASUREMENT_ENVIRONMENT",
                "environment": environment_block(),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {ARTIFACT}")
    for key, value in artifact["roll_up"].items():
        print(f"  {key}: {value}")
    print("  draft-eligible:", artifact["draft_gate_eligible_cells"])


if __name__ == "__main__":
    main()
