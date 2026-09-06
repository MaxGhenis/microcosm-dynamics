"""Tests for the entrant exclusion adapters.

The load-bearing test is
``test_without_the_adapter_every_entrant_over_50_draws_a_claim_age``: it runs
the certified ``apply_claiming`` step directly on entrant rows and shows the
unconditional draw happening, which is the failure the adapter exists to
prevent.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from populace_dynamics.engine import entrant_domains as edm
from populace_dynamics.engine.earnings_domain import EARNINGS_DOMAIN_COLUMN
from populace_dynamics.engine.entrant_schedule import (
    ENTRY_KIND_BIRTH,
    ENTRY_KIND_COLUMN,
    ENTRY_KIND_IMMIGRANT,
)
from populace_dynamics.engine.loop import PeriodContext
from populace_dynamics.engine.steps import ClaimingSchedule, apply_claiming


def _roster() -> pd.DataFrame:
    """Four incumbents and four entrants, spanning the claiming threshold."""
    return pd.DataFrame(
        {
            "person_id": [1, 2, 3, 4, 101, 102, 103, 104],
            "year": [2026] * 8,
            "age": [30, 55, 62, 70, 30, 55, 62, 70],
            "sex": ["female", "male", "female", "male"] * 2,
            "weight": [1.0] * 8,
            ENTRY_KIND_COLUMN: [None] * 4 + [ENTRY_KIND_IMMIGRANT] * 4,
        }
    )


def _claiming_schedule() -> ClaimingSchedule:
    return ClaimingSchedule(
        pmf={
            ("female", 2026): {62: 0.5, 67: 0.5},
            ("male", 2026): {62: 0.5, 67: 0.5},
        }
    )


def _context() -> PeriodContext:
    return PeriodContext(period_index=1, year=2026, draw_index=0, metadata={})


# --------------------------------------------------------------------------
# Membership
# --------------------------------------------------------------------------
def test_entrant_mask_reads_the_provenance_column():
    mask = edm.entrant_mask(_roster())
    assert mask.tolist() == [False] * 4 + [True] * 4


def test_a_frame_without_the_column_has_no_entrants():
    """Safe to call on a closed-panel roster that never saw a schedule."""
    frame = _roster().drop(columns=[ENTRY_KIND_COLUMN])
    assert not edm.entrant_mask(frame).any()


def test_a_missing_value_is_an_incumbent():
    frame = _roster()
    frame.loc[4, ENTRY_KIND_COLUMN] = pd.NA
    assert edm.entrant_mask(frame).tolist() == [False] * 5 + [True] * 3


def test_births_are_not_immigrant_entrants_by_default():
    frame = _roster()
    frame.loc[4, ENTRY_KIND_COLUMN] = ENTRY_KIND_BIRTH
    assert edm.entrant_mask(frame).sum() == 3
    assert (
        edm.entrant_mask(
            frame, entry_kinds=(ENTRY_KIND_IMMIGRANT, ENTRY_KIND_BIRTH)
        ).sum()
        == 4
    )


def test_the_three_exclusion_id_sets_are_the_entrant_ids():
    frame = _roster()
    expected = {101, 102, 103, 104}
    assert edm.excluded_fertility_ids(frame) == expected
    assert edm.excluded_claiming_ids(frame) == expected
    assert edm.excluded_disability_ids(frame) == expected


# --------------------------------------------------------------------------
# Claiming: the hazard, and the adapter that removes it
# --------------------------------------------------------------------------
def test_without_the_adapter_every_entrant_over_50_draws_a_claim_age():
    """The unconditional draw at ``steps.py:411-413``, demonstrated.

    No insured-status, quarters-of-coverage, AIME or PIA test stands between
    an entrant and a claim.  Combined with the pinned zero-earnings domain,
    this is what would bias every Social Security aggregate toward
    "immigration improves solvency".
    """
    out = apply_claiming(
        _roster(),
        _context(),
        np.random.default_rng(0),
        schedule=_claiming_schedule(),
    )
    entrants = out[out[ENTRY_KIND_COLUMN] == ENTRY_KIND_IMMIGRANT]
    over_50 = entrants[entrants["age"] >= 50]
    assert len(over_50) == 3
    assert over_50["claim_age"].notna().all()
    assert bool(out.loc[out["person_id"] == 104, "claimed"].iloc[0]) is True


def test_the_adapter_leaves_entrants_unclaimed_and_incumbents_untouched():
    adapter = edm.EntrantClaimingAdapter(
        lambda frame, context, rng: apply_claiming(
            frame, context, rng, schedule=_claiming_schedule()
        )
    )
    out = adapter(_roster(), _context(), np.random.default_rng(0))
    entrants = out[out[ENTRY_KIND_COLUMN] == ENTRY_KIND_IMMIGRANT]
    incumbents = out[out[ENTRY_KIND_COLUMN].isna()]

    assert entrants["claim_age"].isna().all()
    assert not entrants["claimed"].any()
    assert entrants["claim_year"].isna().all()
    # The incumbents get exactly what the certified step gives them.
    assert incumbents.loc[incumbents["age"] >= 50, "claim_age"].notna().all()


def test_the_adapter_is_a_passthrough_without_entrants():
    frame = _roster().drop(columns=[ENTRY_KIND_COLUMN])
    step = lambda f, c, r: apply_claiming(  # noqa: E731
        f, c, r, schedule=_claiming_schedule()
    )
    adapter = edm.EntrantClaimingAdapter(step)
    direct = step(frame, _context(), np.random.default_rng(0))
    through = adapter(frame, _context(), np.random.default_rng(0))
    pd.testing.assert_frame_equal(direct, through)


def test_the_adapter_preserves_the_roster_and_person_sort():
    adapter = edm.EntrantClaimingAdapter(
        lambda frame, context, rng: apply_claiming(
            frame, context, rng, schedule=_claiming_schedule()
        )
    )
    out = adapter(_roster(), _context(), np.random.default_rng(0))
    assert len(out) == 8
    assert out["person_id"].is_monotonic_increasing


# --------------------------------------------------------------------------
# Earnings domain
# --------------------------------------------------------------------------
def test_entrants_marked_inside_the_earnings_domain_are_rejected():
    frame = _roster()
    frame[EARNINGS_DOMAIN_COLUMN] = [True] * 4 + [False, False, True, False]
    with pytest.raises(ValueError, match="marked inside the fitted earnings"):
        edm.assert_entrants_out_of_earnings_domain(frame)


def test_entrants_outside_the_earnings_domain_pass():
    frame = _roster()
    frame[EARNINGS_DOMAIN_COLUMN] = [True] * 4 + [False] * 4
    assert edm.assert_entrants_out_of_earnings_domain(frame) == 4


def test_a_frame_without_the_domain_column_still_counts_entrants():
    assert edm.assert_entrants_out_of_earnings_domain(_roster()) == 4


# --------------------------------------------------------------------------
# Benefit suppression
# --------------------------------------------------------------------------
def test_entrant_benefit_outputs_are_missing_not_zero():
    frame = _roster()
    frame["aime"] = 100.0
    frame["pia"] = 50.0
    out = edm.suppress_entrant_benefit_outputs(frame)
    entrants = out[out[ENTRY_KIND_COLUMN] == ENTRY_KIND_IMMIGRANT]
    assert entrants["aime"].isna().all()
    assert entrants["pia"].isna().all()
    # A zero would be a measurement; prior US covered earnings are censored.
    assert not (entrants["aime"] == 0).any()
    assert (out[out[ENTRY_KIND_COLUMN].isna()]["aime"] == 100.0).all()


# --------------------------------------------------------------------------
# The report
# --------------------------------------------------------------------------
def test_exclusion_report_covers_all_four_domains():
    report = edm.exclusion_report(_roster())
    assert report.n_entrants == 4
    assert set(report.excluded) == set(edm.EXCLUDED_DOMAINS)
    assert (
        report.excluded["claiming_eligibility"][
            "n_would_have_drawn_a_claim_age"
        ]
        == 3
    )


def test_exclusion_report_states_it_is_report_only_and_not_a_behaviour_model():
    record = edm.exclusion_report(_roster()).as_dict()
    assert record["gated"] is False
    assert "OUTSIDE the estimand" in record["interpretation"]
    assert any(
        "mortality" in entry
        for entry in record["residual_domains_entrants_do_enter"]
    )


def test_every_excluded_domain_names_the_code_that_makes_it_unfitted():
    for domain, reason in edm.EXCLUDED_DOMAINS.items():
        assert ".py:" in reason, domain
