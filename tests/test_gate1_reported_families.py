"""The gate-1 reported-not-gated battery families.

``gates.yaml`` registers three moment-battery families under
``gates.gate_1.thresholds.reported_not_gated`` as carrying no committed
reference at gate 1 -- ``change_moments`` sd/skew/kurtosis, ``age_profile``
quantiles, and ``mobility_matrix`` at horizon 2 -- to be "published with every
gate run, gated no earlier than a later gate with committed references". Until
this module's subject shipped, no gate-1 artifact carried any of them.

Two guarantees, both always runnable (no staged PSID, no fitted model):

* the three families compute the exact values a hand-built biennial fixture
  panel implies, and the block that publishes them never mutates the panels
  the gated blocks are scored on;
* the gate is unmoved. ``compute_battery`` still returns exactly the eight
  locked statistics; ``gates.yaml`` is byte-identical to the ratified lock;
  and the verdict logic reads no new key -- asserted on the runners' parsed
  syntax trees, not on their prose.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

#: The ratified gate-1 lock. This module's subject publishes reported values
#: and amends no threshold, so the pre-registration contract must not move.
GATES_SHA256 = (
    "596eb4840f4c2e8ef16d883cff8b2fa63828f1b9f8c406037563733d3a2637af"
)

#: The eight locked gate-1 battery statistics (gates.yaml battery block).
LOCKED_BATTERY_KEYS = frozenset(
    {
        "autocorr_log_2yr",
        "autocorr_log_4yr",
        "autocorr_log_10yr",
        "mobility_diagonal",
        "zero_persistence",
        "entry_rate",
        "exit_rate",
        "mean_spell_length",
    }
)

#: The five conjuncts of the amended gate-1 verdict, plus the ``bool`` call
#: the runner wraps them in.
VERDICT_NAMES = frozenset(
    {
        "bool",
        "geometry_gate_pass",
        "battery_gate_pass",
        "pooled_q0_pass",
        "mean_rule_pass",
        "cap_pass",
    }
)


def _runner():
    """The baseline runner module, which owns the shared gate-1 protocol."""
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import run_gate1_baseline

    return run_gate1_baseline


def _module_tree(name: str) -> ast.Module:
    return ast.parse((SCRIPTS / name).read_text(encoding="utf-8"))


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} not found")


def _bindings(scope: ast.AST, target: str) -> list[ast.AST]:
    """EVERY node that binds ``target`` inside ``scope``.

    Plain assignment, augmented assignment (``x &= ...``), annotated
    assignment, walrus, and loop targets all count. Looking only at
    ``ast.Assign`` is how a one-line ``cap_pass &= <reported value>`` slips
    past an inertness check.
    """
    hits: list[ast.AST] = []
    for node in ast.walk(scope):
        targets: list[ast.AST] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets = [node.target]
        elif isinstance(node, ast.NamedExpr):
            targets = [node.target]
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            targets = [node.target]
        else:
            continue
        for bound in targets:
            names = (
                [bound]
                if isinstance(bound, ast.Name)
                else [n for n in ast.walk(bound) if isinstance(n, ast.Name)]
            )
            if any(n.id == target for n in names):
                hits.append(node)
                break
    return hits


def _assignment(scope: ast.AST, target: str) -> ast.Assign:
    """The single plain assignment to ``target``, and no other binding."""
    hits = _bindings(scope, target)
    assert len(hits) == 1, f"expected one binding of {target}, got {hits}"
    assert isinstance(
        hits[0], ast.Assign
    ), f"{target} is bound by {type(hits[0]).__name__}, not a plain assignment"
    return hits[0]


def _value_source(node: ast.AST) -> str:
    """The source of whatever a binding node computes."""
    if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
        return ast.unparse(node.value) if node.value else ""
    return ast.unparse(node)


def _free_names(node: ast.AST) -> set[str]:
    """Names ``node`` READS from its enclosing scope.

    Comprehension targets and lambda arguments are excluded: they are local
    to the expression, and treating a stray ``v`` or ``k`` as a dataflow edge
    makes a backward slice reach unrelated code.
    """
    bound: set[str] = set()
    for inner in ast.walk(node):
        if isinstance(inner, (ast.ListComp, ast.SetComp, ast.DictComp)) or (
            isinstance(inner, ast.GeneratorExp)
        ):
            for generator in inner.generators:
                bound |= {
                    n.id
                    for n in ast.walk(generator.target)
                    if isinstance(n, ast.Name)
                }
        elif isinstance(inner, ast.Lambda):
            bound |= {a.arg for a in inner.args.args}
    return {
        n.id
        for n in ast.walk(node)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    } - bound


def _inlined_functions(
    tree: ast.Module, names: set[str], seen: set[str]
) -> dict[str, str]:
    """Bodies of the module-level functions ``names`` reaches, recursively."""
    module_functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    out: dict[str, str] = {}
    queue = [n for n in names if n in module_functions]
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        node = module_functions[name]
        out[f"{name} (function body)"] = ast.unparse(node)
        queue.extend(
            n
            for n in _free_names(node)
            if n in module_functions and n not in seen
        )
    return out


def _reachable_sources(
    tree: ast.Module, scope: ast.FunctionDef, roots: set[str]
) -> dict[str, str]:
    """A backward slice: everything a value in ``roots`` can depend on.

    Follows each name back through the bindings in ``scope`` that execute
    BEFORE it (``run`` is straight-line, so a later statement cannot feed an
    earlier one), and inlines the body of every module-level function the
    slice calls. Without the second hop, hiding the dependency one call deep
    (``cap_pass = _cap_rule(..., per_seed)``) would defeat the check.
    """
    sources: dict[str, str] = {}
    seen_names: set[str] = set()
    seen_functions: set[str] = set()
    # (name, the line before which a binding must occur); None = anywhere.
    queue: list[tuple[str, int | None]] = [(name, None) for name in roots]
    while queue:
        name, before = queue.pop()
        key = (name, before)
        if key in seen_names:
            continue
        seen_names.add(key)
        for binding in _bindings(scope, name):
            if before is not None and binding.lineno >= before:
                continue
            source = _value_source(binding)
            sources[f"{name} (line {binding.lineno})"] = source
            reads = _free_names(ast.parse(source))
            queue.extend((read, binding.lineno) for read in reads)
            sources.update(_inlined_functions(tree, reads, seen_functions))
    return sources


# --------------------------------------------------------------------------
# The fixture panel
# --------------------------------------------------------------------------
# Four persons on the gate-1 biennial grid (period_step 2), two birth decades,
# every earnings value chosen so all three families have closed forms.
#
# PSID age is measured at the collection wave and the panel's period is the
# income reference year (wave - 1), so age = period + 1 - birth_year. Each
# person rises by their cohort's factor and returns to base, so within a
# cohort the four horizon-1 log changes are the symmetric two-point set
# {+log g, -log g, +log g, -log g}: mean 0, sd log g, skew 0, excess kurtosis
# -2. Returning to base also leaves the four persons in their opening order
# four years on, so the horizon-2 mobility matrix is the identity on the
# occupied bins. Every (age, cohort) cell holds exactly one row, so each
# age-profile mean and every quantile is that row's earnings.
_C1950S_GROWTH = 2.0
_C1960S_GROWTH = 3.0
_PEOPLE = (
    # person_id, birth_year, base earnings, one-period growth factor
    (1, 1955, 1000.0, _C1950S_GROWTH),
    (2, 1958, 2000.0, _C1950S_GROWTH),
    (3, 1965, 3000.0, _C1960S_GROWTH),
    (4, 1968, 4000.0, _C1960S_GROWTH),
)
_PERIODS = (2000, 2002, 2004)
#: base, base * growth, base -- one rise and one fall per person.
_GROWTH_PATH = (0, 1, 0)


def _fixture_panel() -> pd.DataFrame:
    rows = []
    for person_id, birth_year, base, growth in _PEOPLE:
        for period, power in zip(_PERIODS, _GROWTH_PATH, strict=True):
            rows.append(
                {
                    "person_id": person_id,
                    "period": period,
                    "earnings": base * growth**power,
                    "age": period + 1 - birth_year,
                    "weight": 1.0,
                }
            )
    return pd.DataFrame(rows)


def _cohort_of(birth_year: int) -> str:
    return f"c{birth_year // 10 * 10}s"


# Two persons whose cohort label can only be right if BOTH halves of the rule
# hold. Every _PEOPLE birth year above sits >= 4 years inside its decade, so
# the main fixture cannot see either half.
#
# The rule is the repository's R7 convention: birth year = round(median over
# a person's rows of ``period - age``).
#
# Person 10's rows imply [1959, 1960, 1959] -> median 1959 -> c1950s, but
# under the other admissible convention (period + 1 - age) they are
# [1960, 1961, 1960] -> 1960 -> c1960s. It pins WHICH convention is used.
# Person 11's rows imply [1959, 1959, 1960] -> median 1959 -> c1950s, where a
# per-row rule labels one person two ways and a max() rule gives c1960s. It
# pins the per-person median.
# Person 12 sits mid-decade (implied 1955 every wave), so the convention
# does NOT move it -- without it, every person would flip and the measured
# share could not distinguish a real count from a hardcoded 1.0.
_BOUNDARY_PEOPLE = {
    10: ((2000, 41), (2002, 42), (2004, 45)),
    11: ((2000, 41), (2002, 43), (2004, 44)),
    12: ((2000, 45), (2002, 47), (2004, 49)),
}
_BOUNDARY_COHORTS = {10: "c1950s", 11: "c1950s", 12: "c1950s"}


def _boundary_panel() -> pd.DataFrame:
    rows = []
    for person_id, observations in _BOUNDARY_PEOPLE.items():
        for period, age in observations:
            rows.append(
                {
                    "person_id": person_id,
                    "period": period,
                    "earnings": 1000.0,
                    "age": age,
                    "weight": 1.0,
                }
            )
    return pd.DataFrame(rows)


def _uneven_cell_panel() -> pd.DataFrame:
    """A panel whose (age, cohort) cells hold different numbers of rows.

    Persons 20 and 21 share birth year 1960, so they share every cell, with
    unequal weights and one zero earner. Person 22 is born 1959, so it is a
    year older AND in the previous decade, and holds its cells alone.
    """
    rows = []
    for person_id, birth_year, weight, earnings in (
        (20, 1960, 1.0, 30000.0),
        (21, 1960, 2.0, 0.0),
        (22, 1959, 1.0, 50000.0),
    ):
        for period in (2000, 2002, 2004):
            rows.append(
                {
                    "person_id": person_id,
                    "period": period,
                    "earnings": earnings,
                    # R7: birth year is the median implied period - age.
                    "age": period - birth_year,
                    "weight": weight,
                }
            )
    return pd.DataFrame(rows)


def _records(block: dict, family: str) -> list[dict]:
    return block[family]["records"]


def _find(records: list[dict], **keys) -> dict:
    hits = [r for r in records if all(r[k] == v for k, v in keys.items())]
    assert len(hits) == 1, f"expected one record for {keys}, got {hits}"
    return hits[0]


# --------------------------------------------------------------------------
# The families compute what the fixture implies
# --------------------------------------------------------------------------
def test_cohort_is_the_birth_decade_and_constant_within_a_person():
    """``by: [cohort]`` is realised as a person-constant birth decade."""
    panel = _fixture_panel()
    with_cohort = _runner().add_cohort(panel)

    per_person = with_cohort.groupby("person_id")["cohort"].nunique()
    assert (per_person == 1).all()

    expected = {
        person_id: _cohort_of(birth_year)
        for person_id, birth_year, _, _ in _PEOPLE
    }
    actual = (
        with_cohort.drop_duplicates("person_id")
        .set_index("person_id")["cohort"]
        .to_dict()
    )
    assert actual == expected
    assert set(expected.values()) == {"c1950s", "c1960s"}


def test_the_cohort_uses_the_repositorys_r7_birth_year_convention():
    """Byte-for-byte the quantity ``couple_earnings`` already derives.

    A second convention for the same quantity on the same panel shape would
    be the defect, so this pins agreement with the existing implementation
    rather than restating its arithmetic.
    """
    from populace_dynamics.data import couple_earnings

    panel = _fixture_panel()
    _, r7_birth_year, _ = couple_earnings.person_earnings_histories(panel)

    labels = _runner().add_cohort(panel)
    derived = (
        labels.drop_duplicates("person_id")
        .set_index("person_id")["cohort"]
        .to_dict()
    )
    assert derived == {
        person_id: _cohort_of(birth_year)
        for person_id, birth_year in r7_birth_year.items()
    }


def test_the_r7_convention_is_period_minus_age_not_the_other_bound():
    """Person 10's decade differs between the two admissible conventions."""
    labels = _runner().add_cohort(_boundary_panel())
    rows = labels.loc[labels.person_id == 10]
    assert set(rows["cohort"]) == {"c1950s"}

    implied = sorted(period - age for period, age in _BOUNDARY_PEOPLE[10])
    assert implied == [1959, 1959, 1960]
    assert _cohort_of(round(float(np.median(implied)))) == "c1950s"
    other_bound = sorted(
        period + 1 - age for period, age in _BOUNDARY_PEOPLE[10]
    )
    assert other_bound == [1960, 1960, 1961]
    assert _cohort_of(round(float(np.median(other_bound)))) == "c1960s"


def test_cohort_is_the_per_person_median_not_a_per_row_label():
    """A cohort must be constant over a life, and the median picks it.

    Person 11's rows imply 1959/1959/1960 -- straddling a decade boundary.
    A per-row rule would label one person two ways; a ``max`` rule would
    pick c1960s. Only the median gives c1950s.
    """
    labels = _runner().add_cohort(_boundary_panel())
    rows = labels.loc[labels.person_id == 11]
    assert rows["cohort"].nunique() == 1
    assert rows["cohort"].iloc[0] == "c1950s"

    implied = sorted(period - age for period, age in _BOUNDARY_PEOPLE[11])
    assert implied == [1959, 1959, 1960]
    assert _cohort_of(round(float(np.median(implied)))) == "c1950s"
    assert _cohort_of(max(implied)) == "c1960s"
    assert {_cohort_of(y) for y in implied} == {"c1950s", "c1960s"}


def test_every_person_carries_exactly_one_cohort():
    labels = _runner().add_cohort(_boundary_panel())
    assert (labels.groupby("person_id")["cohort"].nunique() == 1).all()


def test_change_moments_are_the_fixture_two_point_set_by_cohort():
    """Symmetric two-point log changes: mean 0, sd log g, skew 0, kurt -2."""
    panel = _fixture_panel()
    block = _runner().compute_reported_families(panel, panel)
    records = _records(block, "change_moments")

    for cohort, growth in (
        ("c1950s", _C1950S_GROWTH),
        ("c1960s", _C1960S_GROWTH),
    ):
        expected = {
            "mean": 0.0,
            "sd": np.log(growth),
            "skew": 0.0,
            "kurtosis": -2.0,
        }
        for moment, value in expected.items():
            row = _find(records, cohort=cohort, moment=moment)
            assert row["holdout"] == pytest.approx(value, abs=1e-9)
            assert row["candidate"] == pytest.approx(value, abs=1e-9)

    # Two cohorts x {mean, sd, skew, kurtosis}.
    assert len(records) == 8
    assert block["change_moments"]["reported_line_moments"] == [
        "sd",
        "skew",
        "kurtosis",
    ]


def test_age_profile_cells_hold_one_person_so_every_quantile_is_the_value():
    """One row per (age, cohort) cell: mean and every quantile are it."""
    panel = _fixture_panel()
    block = _runner().compute_reported_families(panel, panel)
    records = _records(block, "age_profile")

    # 4 persons x 3 periods = 12 distinct (age, cohort) cells, x 4 statistics.
    assert len(records) == 12 * 4
    assert {r["statistic"] for r in records} == {"mean", "q10", "q50", "q90"}

    for _, birth_year, base, growth in _PEOPLE:
        for period, power in zip(_PERIODS, _GROWTH_PATH, strict=True):
            age = period + 1 - birth_year
            expected = base * growth**power
            for statistic in ("mean", "q10", "q50", "q90"):
                row = _find(
                    records,
                    age=age,
                    cohort=_cohort_of(birth_year),
                    statistic=statistic,
                )
                assert row["holdout"] == pytest.approx(expected, abs=1e-9)


def test_mobility_matrix_horizon_2_is_the_identity_on_occupied_bins():
    """Growth that never reorders persons leaves every 4-year pair in place."""
    panel = _fixture_panel()
    block = _runner().compute_reported_families(panel, panel)
    records = _records(block, "mobility_matrix")

    assert block["mobility_matrix"]["horizon"] == 2
    # Four persons, weighted-quintile bins over four positive values:
    # ranks 0.125/0.375/0.625/0.875 -> bins 1, 2, 4, 5.
    assert {r["origin"] for r in records} == {1, 2, 4, 5}
    for record in records:
        assert record["origin"] == record["destination"]
        assert record["holdout"] == pytest.approx(1.0, abs=1e-12)


def test_horizon_2_pairs_only_the_first_and_last_biennial_period():
    """Horizon 2 on the biennial grid is a four-year transition."""
    panel = _fixture_panel()
    dropped = panel[panel.period != 2004]
    block = _runner().compute_reported_families(dropped, dropped)
    # 2000 -> 2004 is the only horizon-2 pair the fixture can form.
    assert _records(block, "mobility_matrix") == []


# --------------------------------------------------------------------------
# Candidate-vs-holdout publication
# --------------------------------------------------------------------------
def test_scaling_the_candidate_moves_only_the_age_profile():
    """Log changes and rank bins are scale-free; levels are not."""
    holdout = _fixture_panel()
    candidate = holdout.assign(earnings=holdout.earnings * 1.5)
    block = _runner().compute_reported_families(candidate, holdout)

    assert block["change_moments"]["max_abs_deviation"] == pytest.approx(
        0.0, abs=1e-12
    )
    assert block["mobility_matrix"]["max_abs_deviation"] == pytest.approx(
        0.0, abs=1e-12
    )
    for record in _records(block, "age_profile"):
        assert record["candidate"] == pytest.approx(
            record["holdout"] * 1.5, abs=1e-9
        )


def test_a_one_sided_family_row_publishes_a_null_and_is_counted():
    """A reported family never raises the way ``moment_distance`` does."""
    holdout = _fixture_panel()
    # Zero out one cohort in the candidate: log changes drop those pairs, so
    # the cohort exists on the holdout side of change_moments only.
    candidate = holdout.copy()
    candidate.loc[candidate.person_id.isin({3, 4}), "earnings"] = 0.0
    block = _runner().compute_reported_families(candidate, holdout)

    alignment = block["change_moments"]["alignment"]
    assert alignment["n_holdout_only"] == 4  # c1960s x 4 moments
    assert alignment["n_candidate_only"] == 0
    one_sided = _find(
        _records(block, "change_moments"), cohort="c1960s", moment="sd"
    )
    assert one_sided["candidate"] is None
    assert one_sided["holdout"] == pytest.approx(
        np.log(_C1960S_GROWTH), abs=1e-9
    )
    assert block["change_moments"]["mean_abs_deviation"] is not None


def test_the_candidate_side_of_mobility_is_the_candidate_panel():
    """Reversing the candidate's 2004 ranks must show up as an anti-diagonal.

    With candidate == holdout, or with the candidate side read off the
    holdout panel, rank-based bins agree and every deviation is zero -- so a
    test that only ever compares equal panels cannot see which panel the
    candidate side was computed from.
    """
    holdout = _fixture_panel()
    candidate = holdout.copy()
    final = candidate.period == 2004
    candidate.loc[final, "earnings"] = candidate.loc[
        final, "earnings"
    ].to_numpy()[::-1]

    block = _runner().compute_reported_families(candidate, holdout)
    records = _records(block, "mobility_matrix")

    # Holdout keeps its order (identity on bins 1,2,4,5); the candidate
    # reverses it, so its transitions are 1->5, 2->4, 4->2, 5->1. The two
    # key spaces are disjoint.
    alignment = block["mobility_matrix"]["alignment"]
    assert alignment["n_both"] == 0
    assert alignment["n_candidate_only"] == 4
    assert alignment["n_holdout_only"] == 4

    holdout_side = {
        (r["origin"], r["destination"])
        for r in records
        if r["holdout"] is not None
    }
    candidate_side = {
        (r["origin"], r["destination"])
        for r in records
        if r["candidate"] is not None
    }
    assert holdout_side == {(1, 1), (2, 2), (4, 4), (5, 5)}
    assert candidate_side == {(1, 5), (2, 4), (4, 2), (5, 1)}


def test_a_candidate_only_row_publishes_its_value_and_a_null_holdout():
    """The mirror of the holdout-only case: the null must key off its side."""
    holdout = _fixture_panel()
    candidate = holdout.copy()
    final = candidate.period == 2004
    candidate.loc[final, "earnings"] = candidate.loc[
        final, "earnings"
    ].to_numpy()[::-1]
    block = _runner().compute_reported_families(candidate, holdout)

    one_sided = _find(
        _records(block, "mobility_matrix"), origin=1, destination=5
    )
    assert one_sided["holdout"] is None
    assert one_sided["candidate"] == pytest.approx(1.0, abs=1e-12)


def test_deviation_summaries_are_absolute_and_not_transposed():
    """Halving the candidate makes every deviation nonzero and unequal.

    Scaling UP would leave signed and absolute deviations identical, and a
    fixture where mean == max could not see the two summaries swapped.
    """
    holdout = _fixture_panel()
    candidate = holdout.assign(earnings=holdout.earnings * 0.5)
    block = _runner().compute_reported_families(candidate, holdout)

    profile = block["age_profile"]
    holdout_values = [r["holdout"] for r in _records(block, "age_profile")]
    expected = [0.5 * v for v in holdout_values]

    # Absolute: the candidate is BELOW the holdout everywhere, so a signed
    # difference would publish negatives here.
    assert profile["max_abs_deviation"] > 0
    assert profile["mean_abs_deviation"] > 0
    assert profile["max_abs_deviation"] == pytest.approx(
        max(expected), abs=1e-6
    )
    assert profile["mean_abs_deviation"] == pytest.approx(
        sum(expected) / len(expected), abs=1e-6
    )
    # ... and the two summaries are distinguishable, so a swap is visible.
    assert profile["max_abs_deviation"] > profile["mean_abs_deviation"]


def test_the_mobility_zero_bin_is_occupied_when_earnings_are_zero():
    """The reported horizon-2 matrix shares the gated matrix's bin structure.

    ``mobility_diagonal`` is gated with ``zero_bin=True``; the reported
    horizon-2 family must use the same structure or the artifact's own spec
    text stops being true.
    """
    panel = _fixture_panel()
    zeroed = panel.copy()
    zeroed.loc[zeroed.person_id == 1, "earnings"] = 0.0
    block = _runner().compute_reported_families(zeroed, zeroed)
    records = _records(block, "mobility_matrix")

    assert 0 in {r["origin"] for r in records}
    zero_to_zero = _find(records, origin=0, destination=0)
    assert zero_to_zero["holdout"] == pytest.approx(1.0, abs=1e-12)


def test_the_cohort_ambiguity_is_measured_and_published():
    """The +/-1 in birth year is quantified rather than asserted away."""
    runner = _runner()
    # Persons 10 and 11 sit on the 1959/1960 boundary, so the other
    # convention moves them into c1960s. Person 12 is mid-decade and does
    # not move -- so a hardcoded share would be visible here.
    block = runner.cohort_ambiguity(_boundary_panel())

    assert block["n_persons"] == 3
    assert block["n_persons_relabelled"] == 2
    assert block["share_persons_relabelled"] == pytest.approx(2 / 3)
    assert "period - age" in block["convention_used"]
    assert "R7" in block["convention_used"]
    assert block["alternative"] == "period + 1 - age"


def test_the_published_block_carries_the_cohort_ambiguity():
    block = _runner().compute_reported_families(
        _fixture_panel(), _fixture_panel()
    )
    ambiguity = block["cohort_ambiguity"]
    assert ambiguity["n_persons"] == len(_PEOPLE)
    assert ambiguity["share_persons_relabelled"] is not None


def test_deviations_are_broken_out_per_incommensurable_statistic():
    """A family-wide mean over {mean, sd, skew, kurtosis} is meaningless.

    Excess kurtosis is orders of magnitude larger than a log-change mean, so
    a single average is a kurtosis statistic wearing the family's name. The
    per-statistic breakdown is what a reader can use.
    """
    holdout = _fixture_panel()
    candidate = holdout.assign(earnings=holdout.earnings * 0.5)
    block = _runner().compute_reported_families(candidate, holdout)

    for family, column in (
        ("change_moments", "moment"),
        ("age_profile", "statistic"),
    ):
        breakdown = block[family]["by_statistic"]
        assert breakdown is not None, family
        keys = {r[column] for r in _records(block, family)}
        assert set(breakdown) == keys, family
        for name, stats in breakdown.items():
            assert stats["n"] > 0, (family, name)
            assert stats["mean_abs_deviation"] is not None
            assert stats["max_abs_deviation"] >= stats["mean_abs_deviation"]

    # mobility_matrix has one commensurable quantity, so no breakdown.
    assert block["mobility_matrix"]["by_statistic"] is None


def test_age_profile_publishes_how_much_data_is_under_each_cell():
    """Two-observation cells must be distinguishable from thousand-row ones.

    Uses a panel whose cells differ in size, so a support block that simply
    reported a constant would be visible here.
    """
    panel = _uneven_cell_panel()
    block = _runner().compute_reported_families(panel, panel)
    support = {
        (row["age"], row["cohort"]): row
        for row in block["age_profile"]["support_holdout"]
    }

    # Persons 20 and 21 (born 1960) share every cell: at period 2000 they
    # are age 2000 - 1960 = 40. Person 22 (born 1959) is a year older and
    # lands in the previous decade, so its cells hold one row each.
    assert support[(40, "c1960s")]["n"] == 2
    assert support[(41, "c1950s")]["n"] == 1
    assert support[(40, "c1960s")]["weight"] == pytest.approx(3.0)
    assert support[(41, "c1950s")]["weight"] == pytest.approx(1.0)
    # One of the two shared-cell rows is a zero earner.
    assert support[(40, "c1960s")]["n_zero_earnings"] == 1
    assert support[(41, "c1950s")]["n_zero_earnings"] == 0
    # The cells genuinely differ in size, so a constant would be visible.
    assert {row["n"] for row in support.values()} == {1, 2}

    assert set(support) == {
        (r["age"], r["cohort"]) for r in _records(block, "age_profile")
    }


def test_change_moments_publishes_the_pairs_its_log_filter_discards():
    """``log=True`` drops non-positive pairs at cohort-varying rates."""
    holdout = _fixture_panel()
    candidate = holdout.copy()
    candidate.loc[candidate.person_id.isin({3, 4}), "earnings"] = 0.0
    block = _runner().compute_reported_families(candidate, holdout)

    holdout_support = {
        r["cohort"]: r for r in block["change_moments"]["support_holdout"]
    }
    candidate_support = {
        r["cohort"]: r for r in block["change_moments"]["support_candidate"]
    }
    # The holdout keeps every pair; the candidate's zeroed cohort keeps none.
    assert holdout_support["c1960s"]["share_dropped"] == pytest.approx(0.0)
    assert candidate_support["c1960s"]["n_pairs_used"] == 0
    assert candidate_support["c1960s"]["share_dropped"] == pytest.approx(1.0)
    assert candidate_support["c1950s"]["share_dropped"] == pytest.approx(0.0)


def test_mobility_publishes_the_weight_behind_each_origin_bin():
    panel = _fixture_panel()
    block = _runner().compute_reported_families(panel, panel)
    support = block["mobility_matrix"]["support_holdout"]

    assert {row["origin"] for row in support} == {1, 2, 4, 5}
    assert sum(row["share_of_weight"] for row in support) == pytest.approx(
        1.0, abs=1e-12
    )


def test_publication_never_mutates_the_panels_the_gate_is_scored_on():
    """The gated battery and geometry must see exactly the panel handed in."""
    runner = _runner()
    holdout = _fixture_panel()
    candidate = holdout.assign(earnings=holdout.earnings * 1.5)
    holdout_before, candidate_before = holdout.copy(), candidate.copy()

    runner.compute_reported_families(candidate, holdout)

    pd.testing.assert_frame_equal(holdout, holdout_before)
    pd.testing.assert_frame_equal(candidate, candidate_before)
    assert "cohort" not in holdout.columns
    assert "cohort" not in candidate.columns


def test_every_published_value_is_plain_json_scalars():
    """Numpy keys would break the artifact writer; convert at the boundary."""
    panel = _fixture_panel()
    block = _runner().compute_reported_families(panel, panel)
    for family in ("change_moments", "age_profile", "mobility_matrix"):
        assert block[family]["gated"] is False
        for record in _records(block, family):
            for key, value in record.items():
                assert type(value) in (str, int, float, type(None)), (
                    family,
                    key,
                    type(value),
                )
    assert block["gated"] is False


def test_the_block_serialises_as_strict_json():
    """The per-seed cache uses a narrow default=, and NaN is not JSON."""
    panel = _fixture_panel()
    block = _runner().compute_reported_families(panel, panel)
    # No ``default=`` hook and no NaN/Infinity literals: the block survives
    # the cache round trip and any strict reader.
    assert json.loads(json.dumps(block, allow_nan=False)) == block


def test_a_degenerate_panel_publishes_an_error_instead_of_raising():
    """A reported family must never abort a pre-registered one-shot run."""
    panel = _fixture_panel()
    broken = panel.copy()
    broken["age"] = np.nan  # no finite implied birth year, so no cohort
    block = _runner().compute_reported_families(broken, panel)

    assert block["gated"] is False
    assert "ValueError" in block["error"]
    assert "change_moments" not in block
    assert json.loads(json.dumps(block, allow_nan=False)) == block


def test_the_guard_catches_a_failure_from_the_moments_layer_too(monkeypatch):
    """Not just the block's own ValueError.

    The realistic sources on real data are pandas and ``moments.*``, which
    raise KeyError / TypeError, not the deliberate ValueError in
    ``add_cohort``. A guard narrowed to ValueError would let those kill a
    one-shot run.
    """
    runner = _runner()
    panel = _fixture_panel()

    def _boom(*args, **kwargs):
        raise TypeError("moments blew up")

    monkeypatch.setattr(runner.moments, "change_moments", _boom)
    block = runner.compute_reported_families(panel, panel)

    assert block["gated"] is False
    assert "TypeError" in block["error"]
    assert "moments blew up" in block["error"]
    assert "change_moments" not in block


def test_a_non_finite_family_value_is_published_as_null(monkeypatch):
    """``json.dumps`` writes bare ``NaN``/``Infinity``, which is not JSON.

    The fixture cannot produce a non-finite value, so the guard is exercised
    by making a family return one.
    """
    runner = _runner()
    panel = _fixture_panel()
    real_age_profile = runner.moments.age_profile

    def _with_non_finite(*args, **kwargs):
        frame = real_age_profile(*args, **kwargs)
        frame = frame.copy()
        frame.loc[frame.index[0], "value"] = np.inf
        frame.loc[frame.index[1], "value"] = np.nan
        return frame

    monkeypatch.setattr(runner.moments, "age_profile", _with_non_finite)
    block = runner.compute_reported_families(panel, panel)

    published = [
        value
        for record in _records(block, "age_profile")
        for value in (record["candidate"], record["holdout"])
    ]
    assert any(value is None for value in published)
    assert all(value is None or np.isfinite(value) for value in published)
    # The whole block still serialises under a strict reader.
    assert json.loads(json.dumps(block, allow_nan=False)) == block


def test_a_failed_seed_is_reported_missing_with_its_error():
    runner = _runner()
    panel = _fixture_panel()
    broken = panel.assign(age=np.nan)
    per_seed = [
        {
            "seed": 0,
            "reported_not_gated": runner.compute_reported_families(
                panel, panel
            ),
        },
        {
            "seed": 1,
            "reported_not_gated": runner.compute_reported_families(
                broken, panel
            ),
        },
    ]
    block = runner.collect_reported_families(per_seed)
    assert block["seeds_present"] == [0]
    assert block["seeds_missing"] == [1]
    assert "ValueError" in block["seed_errors"][1]


# --------------------------------------------------------------------------
# The run-level block
# --------------------------------------------------------------------------
def test_run_level_block_names_the_three_families_and_locates_the_values():
    panel = _fixture_panel()
    runner = _runner()
    per_seed = [
        {
            "seed": seed,
            "reported_not_gated": runner.compute_reported_families(
                panel, panel
            ),
        }
        for seed in range(5)
    ]
    block = runner.collect_reported_families(per_seed)

    assert block["gated"] is False
    assert block["seeds_present"] == [0, 1, 2, 3, 4]
    assert block["seeds_missing"] == []
    assert block["values_location"] == "per_seed[].reported_not_gated"
    for family in ("change_moments", "age_profile", "mobility_matrix"):
        assert block[family]["gated"] is False
        assert block[family]["spec"]
        assert [row["seed"] for row in block[family]["per_seed"]] == [
            0,
            1,
            2,
            3,
            4,
        ]


def test_run_level_block_reports_a_seed_whose_values_are_absent():
    """A run resumed from a pre-existing cache must not silently drop a seed."""
    panel = _fixture_panel()
    runner = _runner()
    per_seed = [
        {
            "seed": 0,
            "reported_not_gated": runner.compute_reported_families(
                panel, panel
            ),
        },
        {"seed": 1},
    ]
    block = runner.collect_reported_families(per_seed)
    assert block["seeds_present"] == [0]
    assert block["seeds_missing"] == [1]


# --------------------------------------------------------------------------
# The gate is unmoved
# --------------------------------------------------------------------------
def test_gates_yaml_is_byte_identical_to_the_ratified_lock():
    """Publishing reported values amends no pre-registered threshold."""
    digest = hashlib.sha256((ROOT / "gates.yaml").read_bytes()).hexdigest()
    assert digest == GATES_SHA256


def test_gated_battery_still_returns_exactly_the_eight_locked_statistics():
    """A ninth key here would publish an ``inf`` reproduction deviation."""
    panel = _fixture_panel()
    values = _runner().compute_battery(panel)
    assert set(values) == LOCKED_BATTERY_KEYS


def test_gated_battery_checks_ignore_any_key_that_is_not_a_locked_tolerance():
    """A value published beside the battery cannot reach a seed verdict."""
    runner = _runner()
    panel = _fixture_panel()
    values = runner.compute_battery(panel)
    reference = dict(values)
    reference["mobility_diagonal_mean"] = values["mobility_diagonal"]
    tolerances = {f"{key}_tolerance": 10.0 for key in LOCKED_BATTERY_KEYS}

    checks = runner.check_battery(values, reference, tolerances)
    assert set(checks) == LOCKED_BATTERY_KEYS

    intruded = runner.check_battery(
        {**values, "reported_family_deviation": 1e9},
        {**reference, "reported_family_deviation": 0.0},
        tolerances,
    )
    # A short fixture leaves some locked statistics undefined (NaN), so
    # compare through pandas, which matches NaN to NaN.
    pd.testing.assert_frame_equal(pd.DataFrame(checks), pd.DataFrame(intruded))


def test_the_gate_verdict_reads_exactly_its_five_pre_registered_conjuncts():
    """AST-level: no new name entered ``gate_pass``, and it is a conjunction.

    The operator matters as much as the operand set: a set comparison alone
    would accept the same five names combined with ``or``.
    """
    tree = _module_tree("run_gate1_candidate11.py")
    run = _function(tree, "run")
    verdict = _assignment(run, "gate_pass")

    names = {
        node.id
        for node in ast.walk(verdict.value)
        if isinstance(node, ast.Name)
    }
    assert names == VERDICT_NAMES

    boolops = [
        node
        for node in ast.walk(verdict.value)
        if isinstance(node, ast.BoolOp)
    ]
    assert len(boolops) == 1
    assert isinstance(boolops[0].op, ast.And)
    assert len(boolops[0].values) == len(VERDICT_NAMES - {"bool"})


def test_no_conjunct_of_the_verdict_is_bound_anywhere_but_once():
    """An augmented assignment would fold a reported value in silently."""
    tree = _module_tree("run_gate1_candidate11.py")
    run = _function(tree, "run")
    for name in sorted(VERDICT_NAMES - {"bool"}) + ["gate_pass"]:
        bindings = _bindings(run, name)
        assert len(bindings) == 1, (name, [type(b).__name__ for b in bindings])
        assert isinstance(bindings[0], ast.Assign), (
            name,
            type(bindings[0]).__name__,
        )


def test_nothing_the_verdict_transitively_depends_on_touches_the_block():
    """Follow every conjunct back through locals AND same-file helpers.

    Checking only each conjunct's own right-hand side lets the dependency
    hide one call deep, so this walks the whole reachable expression set.
    """
    tree = _module_tree("run_gate1_candidate11.py")
    run = _function(tree, "run")
    sources = _reachable_sources(tree, run, VERDICT_NAMES - {"bool"})

    assert sources, "the reachability walk found nothing to check"
    for origin, source in sources.items():
        assert "reported" not in source, (origin, source)
        assert "collect_reported_families" not in source, (origin, source)


def test_the_reported_block_is_not_reachable_from_any_published_verdict():
    """The same walk from the artifact's own verdict fields."""
    tree = _module_tree("run_gate1_candidate11.py")
    run = _function(tree, "run")
    sources = _reachable_sources(
        tree,
        run,
        {"geometry_gate_pass", "battery_gate_pass", "n_geo", "n_bat"},
    )
    for origin, source in sources.items():
        assert "reported" not in source, (origin, source)


def test_the_per_seed_reported_block_is_published_and_never_read_again():
    """In the shared per-seed path it is written once and read by nothing."""
    tree = _module_tree("run_gate1_candidate10.py")
    run_seed = _function(tree, "run_seed")

    assigned = _assignment(run_seed, "reported_families")
    assert (
        ast.unparse(assigned.value)
        == "compute_reported_families(candidate, holdout)"
    )
    loads = [
        node
        for node in ast.walk(run_seed)
        if isinstance(node, ast.Name)
        and node.id == "reported_families"
        and isinstance(node.ctx, ast.Load)
    ]
    assert len(loads) == 1  # the artifact dict entry, and nothing else


def test_the_gated_per_seed_chain_still_runs_off_the_locked_battery():
    """battery_pass <- battery_checks <- check_battery <- compute_battery."""
    tree = _module_tree("run_gate1_candidate10.py")
    run_seed = _function(tree, "run_seed")

    assert (
        ast.unparse(_assignment(run_seed, "battery_values").value)
        == "compute_battery(candidate)"
    )
    assert ast.unparse(_assignment(run_seed, "battery_checks").value) == (
        "check_battery(battery_values, battery_reference, battery_tol)"
    )
    assert ast.unparse(_assignment(run_seed, "battery_seed_pass").value) == (
        "all((c['pass'] for c in battery_checks.values()))"
    )
