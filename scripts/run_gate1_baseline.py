"""Gate-1 baseline run: the chained weighted QRF backcast.

The first pre-registered model run of PolicyEngine/populace-dynamics.
Scores the locked baseline earnings process — populace-fit's regime-gated
chained weighted QRF, run as a one-step BACKWARD biennial backcast —
against the LOCKED gate-1 thresholds in ``gates.yaml`` (commit that
flipped ``locked: true``, pull request 39).

This is a one-shot pre-registered evaluation. The protocol is read from
``gates.yaml`` at runtime and implemented literally; no threshold is
hardcoded and no model choice is tuned against holdout scores. The
outcome publishes whether it passes or fails.

The baseline, exactly as fixed by the feature author:

* **Model.** ``populace.fit.qrf.RegimeGatedQRF`` at its DEFAULT
  hyperparameters (100 trees, ``zero_atol=1e-6``, ``max_samples_leaf=
  None``), seeded from the gate seed ``s``. The plain-table front door
  is used (explicit weight column), so no Frame is constructed.
* **Transition.** One-step BACKWARD biennial transition, mirroring
  production backcast use: target = earnings at period ``t-2``,
  predictors = (earnings at ``t``, age at ``t-2``), sample_weight = the
  pair's earlier-period (``t-2``) person-period weight. Fit on the 80%
  complement's adjacent-period pairs. ``RegimeGatedQRF`` handles the
  zero regime (the target is zero-inflated positive).
* **Generation.** Per holdout person: anchor the chronologically LAST
  observed period at its REAL earnings, then chain BACKWARD over that
  person's observed periods. Each earlier observed period's earnings is
  drawn from the fitted model conditioned on the next observed period's
  (generated or anchor) earnings and the person's age at the earlier
  period. Consecutive observed periods are 2 years apart; a gap (next
  observed period 4+ years later) gets the one-step model applied once
  across the gap (the naive baseline's documented gap handling). Only
  earnings is generated; person_id / period / age / weight copy from
  the holdout rows, and the anchor period keeps its real value. The
  candidate panel therefore holds exactly the holdout persons on
  exactly their observed periods (the locked candidate-panel pin).

Determinism. Generation batches by step-from-anchor; within a step,
rows are ordered by ``person_id``. With a freshly fitted model per seed
(its draw RNG seeded from the model seed) this fixes every draw, so the
run is reproducible from the seeds alone.

Run from the repository root with the PSID family files staged:

    .venv/bin/python scripts/run_gate1_baseline.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

# populace.fit is imported LAZILY (inside the two functions that fit the
# transition model), not at module top level. Importing it runs an
# import-time compat gate and pins scikit-learn < 1.9, which the repo's
# ``.venv`` violates; deferring the import lets pure-protocol reusers
# (e.g. the deterministic candidate-5a splicing runner, which fits no
# model) import this module's split / view / battery / geometry /
# threshold / reproduction machinery under the repo ``.venv`` without
# populace-fit installed. The baseline run itself still uses the
# dedicated gate venv; the fit functions raise the ordinary
# ``ModuleNotFoundError`` there if populace-fit is absent.
from populace_dynamics.data.family import family_earnings_panel
from populace_dynamics.harness import moments
from populace_dynamics.harness import panel as hpanel

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "runs" / "gate1_qrf_baseline_v1.json"
BATTERY_REFERENCE_RUN = "runs/noise_floor_psid_family_9822.json"
ARTIFACT_SCHEMA_VERSION = "gate1_qrf_baseline.v1"

#: The locked filter and split constants (also read/echoed from gates.yaml).
AGE_MIN, AGE_MAX = 25, 59
PERIOD_MIN, PERIOD_MAX = 1998, 2022
PERIOD_STEP = 2
HOLDOUT_FRACTION = 0.2
SEEDS = (0, 1, 2, 3, 4)

#: Battery moment keys as computed here, aliased to the committed
#: ``battery_reference`` keys in the floor artifact.
_BATTERY_REF_ALIAS = {"mobility_diagonal": "mobility_diagonal_mean"}

# Battery column order used for reporting / the moments call.
_MOMENT_KW = dict(
    id_col="person_id",
    period_col="period",
    value_col="earnings",
    weight_col="weight",
)


# --------------------------------------------------------------------------
# Panel + split
# --------------------------------------------------------------------------
def load_filtered_panel() -> pd.DataFrame:
    """Load the PSID family panel and apply the locked view filter.

    Filter FIRST (age 25-59, reference years 1998-2022, positive
    weights), exactly as the locked protocol's ``split`` block states.
    """
    raw = family_earnings_panel()
    prime = raw[
        (raw.age >= AGE_MIN)
        & (raw.age <= AGE_MAX)
        & (raw.period >= PERIOD_MIN)
        & (raw.period <= PERIOD_MAX)
        & (raw.weight > 0)
    ].copy()
    return prime.reset_index(drop=True)


def split_holdout_train(
    panel: pd.DataFrame, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The locked person-disjoint split: the DRAWN 20% is the holdout.

    ``split_panel_by_person`` returns ``(left, right)`` where ``left``
    is the drawn ``fraction``. Per the protocol the drawn 20% of
    persons is the holdout and the complement is the training set.
    """
    holdout, train = hpanel.split_panel_by_person(
        panel, "person_id", fraction=HOLDOUT_FRACTION, seed=seed
    )
    return holdout, train


# --------------------------------------------------------------------------
# Backward transition model
# --------------------------------------------------------------------------
def build_backward_pairs(train: pd.DataFrame) -> pd.DataFrame:
    """Adjacent-period BACKWARD pairs on the training panel.

    One row per (person, period ``t``) whose period ``t-2`` is also
    observed:

    * ``earnings`` = earnings at ``t``          (predictor),
    * ``age_tm2``  = age at ``t-2``             (predictor),
    * ``earnings_tm2`` = earnings at ``t-2``    (target),
    * ``weight_tm2``   = person-period weight at ``t-2`` (sample_weight).

    Only exact ``period_step`` (2-year) adjacencies form a pair; gaps
    do not, so the fitted transition is strictly the one-step biennial
    backward step.
    """
    base = train[["person_id", "period", "earnings", "age", "weight"]].copy()
    earlier = base.rename(
        columns={
            "earnings": "earnings_tm2",
            "age": "age_tm2",
            "weight": "weight_tm2",
        }
    )
    # The earlier row sits at period t-2; lift its period by the step so
    # it inner-joins the base row observed at period t.
    earlier = earlier.assign(period=earlier["period"] + PERIOD_STEP)
    pairs = base.merge(
        earlier[
            ["person_id", "period", "earnings_tm2", "age_tm2", "weight_tm2"]
        ],
        on=["person_id", "period"],
        how="inner",
    )
    return pairs


def fit_backward_model(pairs: pd.DataFrame, seed: int) -> Any:
    """Fit ``RegimeGatedQRF`` (defaults) on the backward pairs.

    Uses the plain-DataFrame front door with the explicit weight column
    ``weight_tm2`` (the earlier-period weight), so the fit is weighted
    without constructing a Frame.
    """
    # Imported lazily (see module header): only the model-fitting path
    # needs populace-fit; pure-protocol reusers do not.
    from populace.fit.qrf import RegimeGatedQRF

    model = RegimeGatedQRF(seed=seed)  # default hyperparameters
    return model.fit(
        pairs,
        predictors=["earnings", "age_tm2"],
        targets=["earnings_tm2"],
        weights="weight_tm2",
    )


# --------------------------------------------------------------------------
# Candidate generation (backward chain)
# --------------------------------------------------------------------------
def generate_candidate(fitted: Any, holdout: pd.DataFrame) -> pd.DataFrame:
    """Backward-chained candidate panel over the holdout persons/periods.

    Anchor each person's chronologically last observed period at its
    real earnings; chain backward over consecutive observed periods,
    drawing each earlier period's earnings from ``fitted`` conditioned
    on the next observed period's (generated/anchor) earnings and the
    earlier period's age. A gap (next observed period 4+ years later)
    applies the one-step model once across the gap. Batched by
    step-from-anchor; within a step rows are ordered by ``person_id``.

    Returns a panel with exactly the holdout persons on exactly their
    observed periods; only ``earnings`` changes (anchor rows keep the
    real value), and ``person_id`` / ``period`` / ``age`` / ``weight``
    copy from the holdout rows (the locked candidate-panel pin).
    """
    hp = holdout.sort_values(["person_id", "period"]).reset_index(drop=True)
    # Position within person counted from the LATEST period (0 = anchor).
    hp["rank_from_top"] = (
        hp.groupby("person_id")["period"].rank(ascending=False, method="first")
        - 1
    ).astype(int)
    hp["depth"] = (
        hp.groupby("person_id")["period"].transform("size").astype(int)
    )

    gen_earn = hp["earnings"].to_numpy(dtype=np.float64).copy()
    ages = hp["age"].to_numpy(dtype=np.float64)
    pids = hp["person_id"].to_numpy()
    ranks = hp["rank_from_top"].to_numpy()
    pos_by_key = {
        (pid, r): i for i, (pid, r) in enumerate(zip(pids, ranks, strict=True))
    }
    max_depth = int(hp["depth"].max()) if len(hp) else 0

    for j in range(1, max_depth):
        earlier_positions = np.nonzero(ranks == j)[0]
        if earlier_positions.size == 0:
            continue
        # Canonical, deterministic row order within the step.
        order = np.argsort(pids[earlier_positions], kind="stable")
        earlier_positions = earlier_positions[order]
        next_positions = np.array(
            [pos_by_key[(pids[p], j - 1)] for p in earlier_positions]
        )
        feat = pd.DataFrame(
            {
                "earnings": gen_earn[next_positions],
                "age_tm2": ages[earlier_positions],
            }
        )
        drawn = fitted.predict(feat)["earnings_tm2"].to_numpy(dtype=np.float64)
        gen_earn[earlier_positions] = drawn

    out = hp.copy()
    out["earnings"] = gen_earn
    return out[["person_id", "period", "earnings", "age", "weight"]]


# --------------------------------------------------------------------------
# Views (built from the locked gates.yaml view specs)
# --------------------------------------------------------------------------
def build_panel_view(name: str, window: int) -> hpanel.PanelView:
    """The locked earnings view: value=earnings, covariate=age, step 2."""
    return hpanel.PanelView(
        name=name,
        id_column="person_id",
        period_column="period",
        value_columns=("earnings",),
        covariate_columns=("age",),
        weight_column="weight",
        window=window,
        period_step=PERIOD_STEP,
    )


# --------------------------------------------------------------------------
# Battery (locked definitions; reproduces battery_reference to float)
# --------------------------------------------------------------------------
def compute_battery(panel: pd.DataFrame) -> dict[str, float]:
    """The locked gate-1 battery statistics on one panel.

    Definitions pinned at lock (gates.yaml battery block):

    * ``autocorr_log_{2,4,10}yr``: ``moments.autocorrelation`` on log
      earnings among positives, lags 1/2/5 of the biennial panel
      (= 2/4/10 years), weighted.
    * ``mobility_diagonal``: unweighted mean over all six
      origin-diagonal cells of the horizon-1 mobility matrix (five
      weighted quintile bins plus the zero bin).
    * ``zero_persistence`` = 1 - ``exit_rate``.
    * ``entry_rate`` / ``exit_rate`` / ``mean_spell_length`` from
      ``moments.zero_spells``.
    """
    ac = moments.autocorrelation(
        panel, lags=(1, 2, 5), period_step=PERIOD_STEP, log=True, **_MOMENT_KW
    )
    ac_by_lag = {int(r.lag): float(r.value) for r in ac.itertuples()}

    mob = moments.mobility_matrix(
        panel,
        horizon=1,
        period_step=PERIOD_STEP,
        n_bins=5,
        zero_bin=True,
        **_MOMENT_KW,
    )
    diag = mob[mob.origin == mob.destination]
    mobility_diagonal = float(diag["probability"].mean())

    zs = moments.zero_spells(panel, period_step=PERIOD_STEP, **_MOMENT_KW)
    zs_by = {r.statistic: float(r.value) for r in zs.itertuples()}
    exit_rate = zs_by["exit_rate"]

    return {
        "autocorr_log_2yr": ac_by_lag[1],
        "autocorr_log_4yr": ac_by_lag[2],
        "autocorr_log_10yr": ac_by_lag[5],
        "mobility_diagonal": mobility_diagonal,
        "zero_persistence": 1.0 - exit_rate,
        "entry_rate": zs_by["entry_rate"],
        "exit_rate": exit_rate,
        "mean_spell_length": zs_by["mean_spell_length"],
    }


# --------------------------------------------------------------------------
# Reported-not-gated battery families (published, NEVER scored)
# --------------------------------------------------------------------------
# gates.yaml registers three moment-battery families under
# ``gates.gate_1.thresholds.reported_not_gated`` as carrying no committed
# reference at gate 1: they are "published with every gate run, gated no
# earlier than a later gate with committed references". Nothing below enters
# any pass rule, any tolerance, or any verdict: the values are computed on the
# same per-seed candidate and holdout panels the gated battery uses and
# attached to the artifact as a sibling of the gated blocks.
#
# The gated battery (:func:`compute_battery`) is UNTOUCHED. Its key set is
# pinned bit-exactly against the committed ``battery_reference`` by
# :func:`reproduce_battery_reference`, and the candidate-11 reproduction block
# scores the union of the two key sets, so an added key there would publish an
# ``inf`` deviation as a finding. That is why these families live in their own
# function and their own artifact block.

#: The registration text, echoed into every artifact that carries the block.
REPORTED_NOT_GATED_REGISTRATION = (
    "gates.yaml gates.gate_1.thresholds.reported_not_gated: 'change_moments "
    "sd, skew, kurtosis', 'age_profile quantiles', 'mobility_matrix horizon "
    "2' -- registered battery families with no committed reference at gate 1: "
    "published with every gate run, gated no earlier than a later gate with "
    "committed references."
)

#: ``moment_battery.age_profile.quantiles`` in gates.yaml.
REPORTED_AGE_QUANTILES = (0.1, 0.5, 0.9)

#: The reported horizon of ``moment_battery.mobility_matrix.horizons``
#: (horizon 1 is the gated ``mobility_diagonal``; horizon 2 is reported).
REPORTED_MOBILITY_HORIZON = 2

#: ``moment_battery.mobility_matrix`` bin structure in gates.yaml.
REPORTED_MOBILITY_BINS = 5

#: The three moments the gate-1 reported line names by hand. ``mean`` is
#: computed too (``moment_battery.change_moments.moments`` lists it) and
#: published alongside; this tuple records which three the line names.
REPORTED_CHANGE_MOMENTS = ("sd", "skew", "kurtosis")

#: How ``by: [cohort]`` is realised on the gate-1 panel. The PSID family
#: panel carries no cohort column and the data layer reads no birth-year
#: variable -- only "AGE OF INDIVIDUAL" (``panels.DEMOGRAPHIC_CONCEPTS``) --
#: so a cohort is DERIVED here and documented in the artifact as a reporting
#: choice, not as a pre-registered definition.
#:
#: The derivation is the repository's existing R7 convention, not a new one:
#: :func:`populace_dynamics.data.couple_earnings.person_earnings_histories`
#: takes the median implied ``period - age`` over a frame of exactly this
#: shape, and ``replication_caregiver`` / ``replication_mermin_rows`` do the
#: same. Using a second convention for the same quantity on the same panel
#: would be the defect; the decade bucket is the only thing added here.
#:
#: Birth year is not identifiable from age alone: PSID age is age at the
#: INTERVIEW, so ``wave - age`` is the birth year for a person whose birthday
#: precedes the interview and ``wave - age - 1`` for everyone else. With
#: ``period = wave - 1`` the R7 quantity ``period - age`` is the latter --
#: the right answer for the majority, since PSID interviews fall early in the
#: wave year. The offset is person-constant, so the per-person median
#: stabilises the label without removing the ambiguity; rather than assert a
#: precision the data cannot support, :func:`cohort_ambiguity` measures the
#: share of persons whose decade moves under the other admissible convention
#: and publishes it beside the values.
COHORT_DEFINITION = (
    "DERIVED, not pre-registered: gates.yaml registers 'by: [cohort]' but "
    "the gate-1 panel has no cohort column and the data layer reads no "
    "birth-year variable. Label 'c<decade>s' from decade = floor(birth_year "
    "/ 10) * 10, where birth_year is the repository's R7 convention -- the "
    "per-person median implied 'period - age', rounded, exactly as "
    "populace_dynamics.data.couple_earnings.person_earnings_histories takes "
    "it over a frame of this shape -- so one person carries one cohort for "
    "life. Birth year is NOT identifiable from PSID age alone (age is at the "
    "INTERVIEW): period - age is the birth year for a person whose birthday "
    "follows the interview and birth year MINUS ONE otherwise, so the two "
    "admissible conventions bracket the truth and this is the lower one, "
    "which is right for the majority because PSID interviews fall early in "
    "the wave year. See cohort_ambiguity for the share of persons the "
    "choice actually moves."
)


def cohort_ambiguity(panel: pd.DataFrame) -> dict[str, Any]:
    """How many persons the unidentifiable +/-1 in birth year relabels.

    Reports the share whose decade differs between the two admissible
    conventions (``wave - age``, used, and ``wave - age - 1``). Published,
    never gated: it quantifies a caveat rather than resolving it.
    """
    used = add_cohort(panel)["cohort"]
    alternative = add_cohort(panel.assign(age=panel["age"] - 1))["cohort"]
    differs = used != alternative
    by_person = (
        pd.DataFrame({"person_id": panel["person_id"], "differs": differs})
        .groupby("person_id")["differs"]
        .max()
    )
    return {
        "note": (
            "Birth year is not identifiable from PSID age alone. These are "
            "the persons and rows whose decade label moves between the two "
            "admissible conventions (period - age, the R7 convention "
            "used here, and period + 1 - age). Reported, never gated."
        ),
        "convention_used": "period - age (the repository's R7 convention)",
        "alternative": "period + 1 - age",
        "n_persons": int(len(by_person)),
        "n_persons_relabelled": int(by_person.sum()),
        "share_persons_relabelled": (
            float(by_person.mean()) if len(by_person) else None
        ),
        "n_rows": int(len(panel)),
        "share_rows_relabelled": (
            float(differs.mean()) if len(panel) else None
        ),
    }


def add_cohort(panel: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``panel`` carrying the derived ``cohort`` column.

    The input frame is never mutated: the gated battery and the geometry
    scorecards must see exactly the panel they were handed.
    See :data:`COHORT_DEFINITION` for the derivation.
    """
    work = panel.copy()
    # The R7 quantity, byte-for-byte the expression couple_earnings and the
    # replication scripts use on a frame of this shape.
    implied_birth_year = work["period"].astype("float64") - work["age"].astype(
        "float64"
    )
    person_birth_year = (
        implied_birth_year.groupby(work["person_id"])
        .transform("median")
        .round()
    )
    if not np.isfinite(person_birth_year).all():
        # A null cohort key is dropped silently by groupby, which would
        # shrink the reported population with no trace. Refuse instead.
        raise ValueError(
            f"{int((~np.isfinite(person_birth_year)).sum())} row(s) have no "
            "finite implied birth year; cohort labels would silently drop "
            "them."
        )
    decade = np.floor(person_birth_year / 10.0) * 10.0
    work["cohort"] = "c" + decade.astype("int64").astype(str) + "s"
    return work


def _json_scalar(value: Any) -> Any:
    """Plain-Python form of a pandas/numpy key value, for JSON publication."""
    return value.item() if hasattr(value, "item") else value


def _json_float(value: Any) -> float | None:
    """A JSON-strict float: ``null`` for missing and for non-finite values.

    ``json.dumps`` writes ``NaN`` / ``Infinity`` literals, which strict
    parsers reject; a published artifact must stay readable everywhere.
    """
    if value is None:
        return None
    number = float(value)
    return number if np.isfinite(number) else None


def _paired_records(
    candidate: pd.DataFrame,
    holdout: pd.DataFrame,
    key_columns: list[str],
    value_column: str = "value",
    statistic_column: str | None = None,
) -> dict[str, Any]:
    """Align a candidate/holdout family pair into publishable records.

    Unlike :func:`populace_dynamics.harness.moments.moment_distance` this
    never raises on a one-sided row: a reported family must not be able to
    stop a gate run. One-sided rows are published with a ``null`` on the
    missing side and counted in ``alignment``.

    ``statistic_column`` names the key whose values are NOT commensurable
    with each other -- ``moment`` for change_moments, ``statistic`` for
    age_profile. A single deviation summary across a family whose records
    mix a unitless mean with an excess kurtosis is dominated by the
    largest-scale statistic, so the per-statistic breakdown is what a reader
    should use; the family-wide numbers are kept only as a coarse envelope.
    """
    merged = candidate.merge(
        holdout,
        on=key_columns,
        suffixes=("_candidate", "_holdout"),
        how="outer",
        indicator=True,
    ).sort_values(key_columns)
    records = []
    for row in merged.itertuples(index=False):
        record = {k: _json_scalar(getattr(row, k)) for k in key_columns}
        cand = getattr(row, f"{value_column}_candidate")
        hold = getattr(row, f"{value_column}_holdout")
        record["candidate"] = None if pd.isna(cand) else _json_float(cand)
        record["holdout"] = None if pd.isna(hold) else _json_float(hold)
        records.append(record)
    both = merged["_merge"] == "both"
    paired = merged.loc[both]
    deviations = (
        paired[f"{value_column}_candidate"] - paired[f"{value_column}_holdout"]
    ).abs()
    by_statistic = None
    if statistic_column is not None and len(paired):
        by_statistic = {}
        for name, group in paired.groupby(statistic_column):
            group_dev = (
                group[f"{value_column}_candidate"]
                - group[f"{value_column}_holdout"]
            ).abs()
            by_statistic[str(name)] = {
                "n": int(len(group_dev)),
                "mean_abs_deviation": _json_float(group_dev.mean()),
                "max_abs_deviation": _json_float(group_dev.max()),
            }

    return {
        "records": records,
        "by_statistic": by_statistic,
        "alignment": {
            "n_records": int(len(merged)),
            "n_both": int(both.sum()),
            "n_candidate_only": int((merged["_merge"] == "left_only").sum()),
            "n_holdout_only": int((merged["_merge"] == "right_only").sum()),
        },
        "mean_abs_deviation": (
            _json_float(deviations.mean()) if len(deviations) else None
        ),
        "max_abs_deviation": (
            _json_float(deviations.max()) if len(deviations) else None
        ),
    }


#: How the two published sides relate. gates.yaml's scoring block forbids a
#: POOLED holdout comparator ("not to a pooled holdout, which the harness does
#: not define (the five 20% draws overlap)"); the per-seed candidate against
#: its OWN holdout is exactly what the geometry scorecards already do, so that
#: is what is published here -- and it is neither a floor nor a committed
#: reference.
COMPARATOR_NOTE = (
    "The 'holdout' side is seed s's own 20% draw -- the same panel the "
    "geometry scorecards score the candidate against -- NOT a noise floor "
    "and NOT a committed reference: these families have none at gate 1, "
    "which is why they are reported. Nothing is pooled across seeds; "
    "gates.yaml's scoring block rules a pooled holdout undefined because the "
    "five 20% draws overlap. The deviation summaries are descriptive: no "
    "tolerance, no threshold, no pass field."
)

#: Families key on what they can form, so their key spaces legitimately
#: differ: a cohort with observations but no positive-to-positive pair at
#: horizon 1 appears in ``age_profile`` and not in ``change_moments``.
KEY_SPACE_NOTE = (
    "Each family keys on what it can form, so the three key spaces differ by "
    "construction: change_moments drops pairs whose endpoints are not both "
    "positive (log changes), mobility_matrix at horizon 2 needs a pair four "
    "years apart on the biennial grid, and age_profile needs only a row. A "
    "cohort present in one family and absent from another is that, not a "
    "defect."
)


def _mobility_support(matrix: pd.DataFrame) -> list[dict[str, Any]]:
    """Weight behind each origin row of a mobility matrix.

    ``mobility_matrix`` row-normalises over destinations, so an origin bin
    holding almost no weight publishes probabilities as confidently as one
    holding most of the panel.
    """
    totals = matrix.groupby("origin", sort=True)["weight"].sum()
    grand = float(totals.sum())
    return [
        {
            "origin": int(origin),
            "weight": _json_float(weight),
            "share_of_weight": (
                _json_float(weight / grand) if grand else None
            ),
        }
        for origin, weight in totals.items()
    ]


def _age_profile_support(panel: pd.DataFrame) -> list[dict[str, Any]]:
    """Rows and weight behind each published (age, cohort) cell.

    ``age_profile`` publishes a mean and three quantiles per cell without
    saying how much data is under them; on the real holdout the thinnest
    cells hold two observations, and a reader cannot otherwise tell those
    from a cell holding a thousand.
    """
    grouped = panel.groupby(["age", "cohort"], sort=True).agg(
        n=("earnings", "size"),
        weight=("weight", "sum"),
        n_zero=("earnings", lambda s: int((s == 0).sum())),
    )
    return [
        {
            "age": int(age),
            "cohort": str(cohort),
            "n": int(row.n),
            "weight": _json_float(row.weight),
            "n_zero_earnings": int(row.n_zero),
        }
        for (age, cohort), row in grouped.iterrows()
    ]


def _change_moments_support(
    panel: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Pairs formed and pairs kept per cohort, for the log-change family.

    ``log=True`` drops every pair whose endpoints are not both positive, at
    rates that vary by cohort, so the published moments rest on a different
    denominator than the panel suggests. Uses the family's OWN pairing
    helper so the counts cannot drift from what it actually measured.
    """
    paired = moments._pair(
        panel,
        "person_id",
        "period",
        ["earnings", "weight", "cohort"],
        1,
        PERIOD_STEP,
    )
    kept = (paired["earnings"] > 0) & (paired["earnings_next"] > 0)
    paired = paired.assign(_kept=kept)
    rows = []
    for cohort, group in paired.groupby("cohort", sort=True):
        n_pairs = int(len(group))
        n_kept = int(group["_kept"].sum())
        rows.append(
            {
                "cohort": str(cohort),
                "n_pairs": n_pairs,
                "n_pairs_used": n_kept,
                "n_pairs_dropped_non_positive": n_pairs - n_kept,
                "share_dropped": (
                    _json_float(1.0 - n_kept / n_pairs) if n_pairs else None
                ),
            }
        )
    return rows


def compute_reported_families(
    candidate: pd.DataFrame, holdout: pd.DataFrame
) -> dict[str, Any]:
    """The three registered-but-unreferenced battery families, on one seed.

    ``candidate`` is the generated panel and ``holdout`` the observed panel
    the gated battery and the geometry scorecards already use for this seed.
    The candidate holds exactly the holdout persons on their observed periods
    and copies their ``age`` and ``weight``, so the derived cohort agrees row
    for row. The two sides do NOT therefore align on every family key: what a
    family can form depends on the earnings themselves (see
    :data:`KEY_SPACE_NOTE`), so a generated panel can gain or lose a key.
    That is why the alignment is an outer join with counts, not a lookup.

    Returns one block per family, each carrying its gates.yaml spec, the
    candidate and holdout values in tidy records, and reported (never gated)
    deviation summaries. ``gated`` is ``False`` on every block: no value here
    enters any tolerance, any seed verdict, or the gate verdict.

    This function does not raise. A reported family must not be able to abort
    a pre-registered one-shot run, so a failure anywhere below is published as
    an ``error`` block instead -- visible, and still gating nothing.
    """
    try:
        return _reported_families(candidate, holdout)
    except Exception as exc:  # published as a finding, never raised
        return {
            "gated": False,
            "registration": REPORTED_NOT_GATED_REGISTRATION,
            "error": f"{type(exc).__name__}: {exc}",
            "note": (
                "The reported families failed to compute for this seed. The "
                "failure is published rather than raised: these values gate "
                "nothing, so they must not be able to stop a one-shot run. "
                "Every gated block in this seed is unaffected."
            ),
        }


def _reported_families(
    candidate: pd.DataFrame, holdout: pd.DataFrame
) -> dict[str, Any]:
    """The body of :func:`compute_reported_families` (may raise)."""
    cand = add_cohort(candidate)
    hold = add_cohort(holdout)

    cand_change = moments.change_moments(
        cand,
        by=["cohort"],
        horizon=1,
        period_step=PERIOD_STEP,
        log=True,
        **_MOMENT_KW,
    )
    hold_change = moments.change_moments(
        hold,
        by=["cohort"],
        horizon=1,
        period_step=PERIOD_STEP,
        log=True,
        **_MOMENT_KW,
    )

    profile_kw = dict(
        age_col="age",
        value_col="earnings",
        weight_col="weight",
        by=["cohort"],
        quantiles=REPORTED_AGE_QUANTILES,
    )
    cand_profile = moments.age_profile(cand, **profile_kw)
    hold_profile = moments.age_profile(hold, **profile_kw)

    mobility_kw = dict(
        horizon=REPORTED_MOBILITY_HORIZON,
        period_step=PERIOD_STEP,
        n_bins=REPORTED_MOBILITY_BINS,
        zero_bin=True,
        **_MOMENT_KW,
    )
    cand_mobility = moments.mobility_matrix(candidate, **mobility_kw)
    hold_mobility = moments.mobility_matrix(holdout, **mobility_kw)

    return {
        "gated": False,
        "registration": REPORTED_NOT_GATED_REGISTRATION,
        "cohort_definition": COHORT_DEFINITION,
        "cohort_ambiguity": cohort_ambiguity(hold),
        "comparator": COMPARATOR_NOTE,
        "key_spaces": KEY_SPACE_NOTE,
        "change_moments": {
            "spec": (
                "gates.yaml moment_battery.change_moments: moments [mean, sd, "
                "skew, kurtosis], by [cohort], log true; horizon 1 on the "
                f"biennial panel (period_step {PERIOD_STEP}) = 2-year log "
                "earnings changes, the same step the gated autocorrelation "
                "ladder calls 2yr. The gate-1 reported line names "
                f"{', '.join(REPORTED_CHANGE_MOMENTS)}; mean is published "
                "with them because the registered family computes it."
            ),
            "reported_line_moments": list(REPORTED_CHANGE_MOMENTS),
            "gated": False,
            "support_candidate": _change_moments_support(cand),
            "support_holdout": _change_moments_support(hold),
            **_paired_records(
                cand_change,
                hold_change,
                ["cohort", "moment"],
                statistic_column="moment",
            ),
        },
        "age_profile": {
            "spec": (
                "gates.yaml moment_battery.age_profile: quantiles "
                f"{list(REPORTED_AGE_QUANTILES)}, by [cohort]. Weighted mean "
                "and weighted quantiles of earnings per (age, cohort) cell; "
                "statistic names are 'mean' and 'q10'/'q50'/'q90'."
            ),
            "gated": False,
            "support_holdout": _age_profile_support(hold),
            **_paired_records(
                cand_profile,
                hold_profile,
                ["age", "cohort", "statistic"],
                statistic_column="statistic",
            ),
        },
        "mobility_matrix": {
            "spec": (
                "gates.yaml moment_battery.mobility_matrix at the REPORTED "
                f"horizon {REPORTED_MOBILITY_HORIZON} of horizons [1, 2] "
                f"(horizon 1 is the gated mobility_diagonal): "
                f"{REPORTED_MOBILITY_BINS} weighted quintile bins plus the "
                "zero bin, row-normalised over destinations. On the biennial "
                f"panel (period_step {PERIOD_STEP}) horizon "
                f"{REPORTED_MOBILITY_HORIZON} is a 4-year transition."
            ),
            "horizon": REPORTED_MOBILITY_HORIZON,
            "gated": False,
            "support_candidate": _mobility_support(cand_mobility),
            "support_holdout": _mobility_support(hold_mobility),
            **_paired_records(
                cand_mobility.drop(columns=["weight"]),
                hold_mobility.drop(columns=["weight"]),
                ["origin", "destination"],
                value_column="probability",
            ),
        },
    }


def collect_reported_families(
    per_seed: list[dict[str, Any]],
) -> dict[str, Any]:
    """The artifact-level ``reported_not_gated`` block for a whole run.

    Carries the three named family blocks with their specs and a per-seed
    summary; the values themselves stay in ``per_seed[].reported_not_gated``
    so they are published once. Seeds whose per-seed block is absent (a run
    resumed from a cache written before this block existed) or whose families
    failed to compute are listed in ``seeds_missing`` rather than silently
    dropped.
    """

    def _has_values(seed_result: dict[str, Any]) -> bool:
        block = seed_result.get("reported_not_gated") or {}
        return all(
            family in block
            for family in ("change_moments", "age_profile", "mobility_matrix")
        )

    present = [s for s in per_seed if _has_values(s)]
    missing = [int(s["seed"]) for s in per_seed if not _has_values(s)]
    errors = {
        int(s["seed"]): (s.get("reported_not_gated") or {})["error"]
        for s in per_seed
        if "error" in (s.get("reported_not_gated") or {})
    }
    block: dict[str, Any] = {
        "gated": False,
        "registration": REPORTED_NOT_GATED_REGISTRATION,
        "cohort_definition": COHORT_DEFINITION,
        "comparator": COMPARATOR_NOTE,
        "key_spaces": KEY_SPACE_NOTE,
        "note": (
            "Published with the run and scored by nothing: no value in this "
            "block or in per_seed[].reported_not_gated enters any tolerance, "
            "any per-seed verdict, or the gate verdict. gates.yaml is "
            "unchanged by the code that publishes it."
        ),
        "values_location": "per_seed[].reported_not_gated",
        "seeds_present": [int(s["seed"]) for s in present],
        "seeds_missing": missing,
        "seed_errors": errors,
    }
    for family in ("change_moments", "age_profile", "mobility_matrix"):
        first = present[0]["reported_not_gated"][family] if present else {}
        block[family] = {
            "spec": first.get("spec"),
            "gated": False,
            "per_seed": [
                {
                    "seed": int(s["seed"]),
                    "n_records": s["reported_not_gated"][family]["alignment"][
                        "n_records"
                    ],
                    "n_both": s["reported_not_gated"][family]["alignment"][
                        "n_both"
                    ],
                    "mean_abs_deviation": s["reported_not_gated"][family][
                        "mean_abs_deviation"
                    ],
                    "max_abs_deviation": s["reported_not_gated"][family][
                        "max_abs_deviation"
                    ],
                }
                for s in present
            ],
        }
    return block


# --------------------------------------------------------------------------
# Locked protocol (from gates.yaml)
# --------------------------------------------------------------------------
def load_gate1_thresholds() -> dict[str, Any]:
    """The gate-1 ``thresholds`` block, read from gates.yaml at runtime."""
    gates = yaml.safe_load((ROOT / "gates.yaml").read_text())
    return gates["gates"]["gate_1"]["thresholds"]


def check_geometry(
    scores: dict[str, float], geometry: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Evaluate one view's locked geometry thresholds against scores.

    Threshold-name suffixes encode the comparison:

    * ``*_max``   -> ``score <= threshold``
    * ``*_min``   -> ``score >= threshold``
    * ``*_range`` -> ``lo <= score <= hi``

    The score key for each threshold strips the ``_max`` / ``_min`` /
    ``_range`` suffix (e.g. ``c2st_auc_max`` reads ``c2st_auc``, the
    tail ``q99_ratio_range`` reads ``q99_ratio.earnings_t1``).
    """
    results: dict[str, dict[str, Any]] = {}
    for tname, tvalue in geometry.items():
        if tname.endswith("_max"):
            metric = tname[: -len("_max")]
            score = _geometry_score(scores, metric)
            passed = score <= tvalue
            results[tname] = {
                "metric": metric,
                "score": score,
                "threshold": tvalue,
                "comparison": "<=",
                "pass": bool(passed),
            }
        elif tname.endswith("_min"):
            metric = tname[: -len("_min")]
            score = _geometry_score(scores, metric)
            passed = score >= tvalue
            results[tname] = {
                "metric": metric,
                "score": score,
                "threshold": tvalue,
                "comparison": ">=",
                "pass": bool(passed),
            }
        elif tname.endswith("_range"):
            metric = tname[: -len("_range")]
            score = _geometry_score(scores, metric)
            lo, hi = tvalue
            passed = (score >= lo) and (score <= hi)
            results[tname] = {
                "metric": metric,
                "score": score,
                "threshold": [lo, hi],
                "comparison": "in",
                "pass": bool(passed),
            }
        else:
            raise ValueError(
                f"Unrecognized threshold suffix in {tname!r}; expected "
                "_max / _min / _range."
            )
    return results


def _geometry_score(scores: dict[str, float], metric: str) -> float:
    """Map a locked geometry-metric name to the scorecard key.

    The scorecard emits ``prdc_coverage`` (not ``prdc_coverage``-free)
    and tail keys suffixed by the target dimension ``earnings_t1``.
    """
    direct = {
        "c2st_auc": "c2st_auc",
        "energy_distance": "energy_distance",
        "prdc_coverage": "prdc_coverage",
        "w1_over_sd": "w1_over_sd.earnings_t1",
        "q90_ratio": "q90_ratio.earnings_t1",
        "q99_ratio": "q99_ratio.earnings_t1",
    }
    key = direct.get(metric)
    if key is None:
        raise KeyError(
            f"No scorecard key mapped for geometry metric {metric!r}"
        )
    if key not in scores:
        raise KeyError(
            f"Scorecard is missing key {key!r} for metric {metric!r}; "
            f"have {sorted(scores)}."
        )
    return float(scores[key])


def check_battery(
    values: dict[str, float],
    reference: dict[str, float],
    tolerances: dict[str, float],
) -> dict[str, dict[str, Any]]:
    """Evaluate the locked battery tolerances against candidate values.

    Each ``*_tolerance`` names a battery statistic; the candidate value
    passes iff ``|value - reference| <= tolerance``. References come
    from the committed ``battery_reference`` block (aliased keys where
    the report name differs from the committed name).
    """
    results: dict[str, dict[str, Any]] = {}
    for tname, tol in tolerances.items():
        stat = tname[: -len("_tolerance")]
        ref_key = _BATTERY_REF_ALIAS.get(stat, stat)
        if stat not in values:
            raise KeyError(
                f"Battery value missing for {stat!r}; have {sorted(values)}."
            )
        if ref_key not in reference:
            raise KeyError(
                f"battery_reference missing {ref_key!r}; "
                f"have {sorted(reference)}."
            )
        value = float(values[stat])
        ref = float(reference[ref_key])
        deviation = abs(value - ref)
        results[stat] = {
            "value": value,
            "reference": ref,
            "tolerance": float(tol),
            "deviation": deviation,
            "pass": bool(deviation <= tol),
        }
    return results


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def reproduce_battery_reference(panel: pd.DataFrame) -> dict[str, Any]:
    """Recompute battery_reference on the full filtered panel.

    Proves the battery code path matches the committed definitions
    before any candidate is scored. Every committed value must
    reproduce to float precision.
    """
    committed = json.loads((ROOT / BATTERY_REFERENCE_RUN).read_text())
    reference = committed["battery_reference"]
    recomputed = compute_battery(panel)
    checks: dict[str, Any] = {}
    all_exact = True
    for ref_name, ref_val in reference.items():
        # invert the alias to find our local key
        local = next(
            (k for k, v in _BATTERY_REF_ALIAS.items() if v == ref_name),
            ref_name,
        )
        got = float(recomputed[local])
        exact = got == float(ref_val)
        all_exact = all_exact and exact
        checks[ref_name] = {
            "recomputed": got,
            "committed": float(ref_val),
            "exact_float_match": bool(exact),
        }
    return {
        "run": committed["run"],
        "all_committed_values_reproduced_exactly": bool(all_exact),
        "checks": checks,
    }


def run(verbose: bool = True) -> dict[str, Any]:
    """Execute the full pre-registered gate-1 baseline run."""
    # Imported lazily (see module header); the run records the
    # populace-fit defaults in the artifact's model block.
    from populace.fit.qrf import DEFAULT_N_ESTIMATORS, DEFAULT_ZERO_ATOL

    started = time.time()
    thresholds = load_gate1_thresholds()
    if not thresholds.get("locked", False):
        raise RuntimeError(
            "gate_1 thresholds are not locked; the pre-registered run may "
            "only execute against locked thresholds."
        )
    views_cfg = thresholds["views"]
    battery_tol = {
        k: v
        for k, v in thresholds["battery"].items()
        if k.endswith("_tolerance")
    }

    battery_ref_artifact = json.loads(
        (ROOT / BATTERY_REFERENCE_RUN).read_text()
    )
    battery_reference = battery_ref_artifact["battery_reference"]

    panel = load_filtered_panel()
    if verbose:
        print(
            f"filtered panel: {len(panel)} person-periods, "
            f"{panel.person_id.nunique()} persons"
        )

    repro = reproduce_battery_reference(panel)
    if verbose:
        print(
            "battery_reference reproduced exactly: "
            f"{repro['all_committed_values_reproduced_exactly']}"
        )
    if not repro["all_committed_values_reproduced_exactly"]:
        raise RuntimeError(
            "Battery code path does not reproduce the committed "
            "battery_reference to float precision; refusing to proceed "
            "with a divergent definition."
        )

    view_specs = {
        "psid_family_earnings_pairs": build_panel_view(
            "psid_family_earnings_pairs", window=2
        ),
        "psid_family_earnings_runs": build_panel_view(
            "psid_family_earnings_runs", window=3
        ),
    }

    per_seed: list[dict[str, Any]] = []
    for seed in SEEDS:
        seed_t = time.time()
        holdout, train = split_holdout_train(panel, seed)
        pairs = build_backward_pairs(train)
        fitted = fit_backward_model(pairs, seed)
        candidate = generate_candidate(fitted, holdout)

        # --- geometry: score candidate vs holdout on both locked views ---
        geometry_by_view: dict[str, Any] = {}
        geometry_seed_pass = True
        n_windows: dict[str, int] = {}
        for vname, view in view_specs.items():
            scores = hpanel.panel_scorecard(
                candidate, holdout, view, seed=seed
            )
            checks = check_geometry(scores, views_cfg[vname]["geometry"])
            view_pass = all(c["pass"] for c in checks.values())
            geometry_seed_pass = geometry_seed_pass and view_pass
            cand_windows, _ = hpanel.project_panel(candidate, view)
            n_windows[vname] = int(len(cand_windows))
            geometry_by_view[vname] = {
                "scores": {k: float(v) for k, v in scores.items()},
                "thresholds": views_cfg[vname]["geometry"],
                "checks": checks,
                "view_pass": bool(view_pass),
            }

        # --- battery: on the CANDIDATE panel, vs committed reference ---
        battery_values = compute_battery(candidate)
        battery_checks = check_battery(
            battery_values, battery_reference, battery_tol
        )
        battery_seed_pass = all(c["pass"] for c in battery_checks.values())

        # --- the registered families with NO committed reference at gate 1
        #     (gates.yaml reported_not_gated): published, scored by nothing.
        reported_families = compute_reported_families(candidate, holdout)

        per_seed.append(
            {
                "seed": seed,
                "n_persons": int(holdout.person_id.nunique()),
                "n_person_periods": int(len(holdout)),
                "n_train_persons": int(train.person_id.nunique()),
                "n_train_pairs": int(len(pairs)),
                "n_windows": n_windows,
                "regimes": fitted.regimes(),
                "geometry": geometry_by_view,
                "geometry_pass": bool(geometry_seed_pass),
                "battery_values": battery_values,
                "battery_checks": battery_checks,
                "battery_pass": bool(battery_seed_pass),
                # Reported, never gated: read by no check and no verdict.
                "reported_not_gated": reported_families,
            }
        )
        if verbose:
            print(
                f"seed {seed}: geometry_pass={geometry_seed_pass} "
                f"battery_pass={battery_seed_pass} "
                f"({time.time()-seed_t:.0f}s)"
            )

    n_geo = sum(1 for s in per_seed if s["geometry_pass"])
    n_bat = sum(1 for s in per_seed if s["battery_pass"])
    geometry_gate_pass = n_geo >= 4
    battery_gate_pass = n_bat >= 4
    gate_pass = geometry_gate_pass and battery_gate_pass

    artifact = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "run": "gate1_qrf_baseline_v1",
        "gate": "gate_1",
        "description": (
            "Gate-1 baseline: populace-fit regime-gated chained weighted "
            "QRF, one-step backward biennial backcast. Candidate scored "
            "against held-out PSID family earnings panel geometry (two "
            "locked views) and the locked moment battery, per the locked "
            "seed-level conjunction in gates.yaml (pull request 39)."
        ),
        "model": {
            "class": "populace.fit.qrf.RegimeGatedQRF",
            "front_door": "plain DataFrame (explicit weight column)",
            "hyperparameters": {
                "n_estimators": DEFAULT_N_ESTIMATORS,
                "zero_atol": DEFAULT_ZERO_ATOL,
                "max_samples_leaf": None,
                "note": "populace-fit defaults; seed = gate seed s",
            },
            "transition": {
                "direction": "backward (one-step biennial)",
                "target": "earnings at period t-2",
                "predictors": ["earnings at period t", "age at period t-2"],
                "sample_weight": "earlier-period (t-2) person-period weight",
                "fit_pairs": "80% complement's adjacent 2-year pairs",
            },
            "generation": {
                "anchor": (
                    "chronologically last observed period held at real "
                    "earnings"
                ),
                "chain": (
                    "backward over observed periods; each earlier period "
                    "drawn conditional on the next observed period's "
                    "(generated/anchor) earnings and the earlier period's "
                    "age"
                ),
                "gap_rule": (
                    "gap (next observed period 4+ years later) applies the "
                    "one-step model once across the gap"
                ),
                "row_order": (
                    "batched by step-from-anchor; within a step, ordered "
                    "by person_id (deterministic)"
                ),
                "candidate_panel_pin": (
                    "exactly the holdout persons on exactly their observed "
                    "periods; only earnings generated; anchor keeps real "
                    "value; person_id/period/age/weight copied from holdout"
                ),
            },
        },
        "protocol": {
            "filter": (
                f"age {AGE_MIN}-{AGE_MAX}, reference years "
                f"{PERIOD_MIN}-{PERIOD_MAX}, positive weights (applied "
                "before the split)"
            ),
            "split": (
                "populace_dynamics.harness.panel.split_panel_by_person("
                "panel, 'person_id', fraction=0.2, seed=s); the drawn 20% "
                "is the holdout, the complement is the training set"
            ),
            "seeds": list(SEEDS),
            "views": {
                "psid_family_earnings_pairs": {"window": 2, "period_step": 2},
                "psid_family_earnings_runs": {"window": 3, "period_step": 2},
            },
            "scoring": (
                "panel_scorecard(candidate, holdout, view, seed=s) per "
                "locked view; battery on the candidate panel vs committed "
                "battery_reference"
            ),
            "pass_rule": (
                "seed passes geometry iff every locked threshold on every "
                "locked view holds; seed passes battery iff every locked "
                "tolerance holds; gate passes iff >=4/5 seeds pass geometry "
                "AND >=4/5 seeds pass battery"
            ),
        },
        "battery_reference_reproduction": repro,
        "battery_reference_run": BATTERY_REFERENCE_RUN,
        "per_seed": per_seed,
        # The registered battery families with no committed reference at gate
        # 1 (gates.yaml reported_not_gated), published with the run. Named
        # *_families, NOT bare "reported_not_gated": at artifact top level
        # that key is this repository's BOOLEAN marker for "this whole
        # artifact reads no gate" (34 producers write it True; 38 tests
        # assert it is True), and a gate artifact is exactly the thing that
        # does read a gate. The per-seed blocks keep the bare name, where no
        # such convention exists. Nothing here is scored: see the block's own
        # note and per-family "gated".
        "reported_not_gated_families": collect_reported_families(per_seed),
        "seed_conjunction": [
            {
                "seed": s["seed"],
                "geometry_pass": s["geometry_pass"],
                "battery_pass": s["battery_pass"],
            }
            for s in per_seed
        ],
        "verdict": {
            "n_seeds": len(SEEDS),
            "n_geometry_pass": n_geo,
            "n_battery_pass": n_bat,
            "geometry_gate_pass": bool(geometry_gate_pass),
            "battery_gate_pass": bool(battery_gate_pass),
            "gate_1_pass": bool(gate_pass),
            "rule": ">=4/5 seeds geometry AND >=4/5 seeds battery",
        },
        "revision_pins": _revision_pins(),
        "elapsed_seconds": round(time.time() - started, 1),
    }
    if verbose:
        v = artifact["verdict"]
        print(
            f"\nVERDICT: gate_1_pass={v['gate_1_pass']} "
            f"(geometry {n_geo}/5, battery {n_bat}/5)"
        )
    return artifact


def _revision_pins() -> dict[str, Any]:
    """Repo/populace SHAs and schema version for provenance."""
    import subprocess

    def _sha(cwd: Path) -> str | None:
        try:
            return (
                subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd)
                .decode()
                .strip()
            )
        except Exception:
            return None

    populace_root = Path("~/PolicyEngine/populace").expanduser()
    return {
        "populace_dynamics_sha": _sha(ROOT),
        "populace_repo_sha": _sha(populace_root),
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "gates_yaml_locked": True,
    }


def main() -> None:
    artifact = run(verbose=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"wrote {ARTIFACT_PATH}")


if __name__ == "__main__":
    main()
