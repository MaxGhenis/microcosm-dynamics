"""Domain adapters that EXCLUDE scheduled entrants from unfitted laws.

**This module is the refusal, and it is the point of the whole piece.**

An entrant module that only schedules rows is worse than no entrant module.
Every claim below was read from the code at this repo's head:

* ``engine/steps.py:390-450`` ``apply_claiming`` draws a claim age for **every**
  person aged 50 or over.  It tests ``age`` and ``sex`` and nothing else --
  there is no insured-status test, no quarters-of-coverage test, no AIME test
  and no PIA test anywhere in it.
* ``engine/earnings_domain.py:150-159`` decides earnings membership by pure ID
  lookup against the generator's fitted 2014 state, and ``:161-208`` writes a
  hard ``earnings = 0.0`` for every non-member.  A synthetic entrant ID is
  never in that set.  ``forward_earnings.py:1421-1436`` *raises* rather than
  let you mark one in-domain without fitted ``u_w`` / ``realized_earn_2014``.

Compose those two and every scheduled entrant becomes a claimant with AIME and
PIA of approximately zero -- adding people to the denominator of every Social
Security aggregate while adding nothing to payroll revenue or benefit outlays.
That biases the aggregates in the direction of "immigration improves
solvency", entirely as an artifact of an incomplete module.  The existing
family-B ledger already discloses the analogous case for marked incumbents
(``harness/m6_reporting.py:302-311``), but a *scheduled* cohort would make
that understatement load-bearing rather than incidental.

Two further exclusions have the same shape and the same justification -- the
fitted law's support simply does not contain entrants:

* **Fertility.**  ``engine/steps.py:451-506`` materializes births only for
  mothers already on the roster and raises on absent parents (``:479-483``);
  parity initializes at zero.  Leaving entrants in fertility risk asserts that
  every entrant arrived childless, which is a claim about parity the donor
  cannot support.
* **Disability.**  ``engine/disability.py:56-60`` filters ``person_years`` to
  ``holdout_ids`` on a PSID-built ``DisabilityPanel``.  Entrants are not in
  the panel at all.  ASEC/CPS disability items may **not** be relabelled as
  realized PSID M4 status.

So the first admissible entrant product is an open-population run in which
entrants are activated, aged, exposed to mortality and counted -- with
fertility, claiming, disability and earnings **excluded by an explicit
membership predicate rather than defaulted**.  Each predicate below is
deliberately in the shape of ``earnings_domain.membership`` (a pure, ID- or
column-driven boolean over a frame), because that adapter already demonstrates
the pattern end to end.

Nothing here is a model of entrant behaviour.  An excluded entrant is not
"assumed to have no children" or "assumed never to claim"; they are marked as
**outside the estimand**, which is why every exclusion is reported as a
suppressed count rather than a zero.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from populace_dynamics.engine.earnings_domain import EARNINGS_DOMAIN_COLUMN
from populace_dynamics.engine.entrant_schedule import (
    ENTRY_KIND_COLUMN,
    ENTRY_KIND_IMMIGRANT,
)

__all__ = [
    "EXCLUDED_DOMAINS",
    "EntrantClaimingAdapter",
    "EntrantExclusionReport",
    "entrant_mask",
    "assert_entrants_out_of_earnings_domain",
    "excluded_claiming_ids",
    "excluded_disability_ids",
    "excluded_fertility_ids",
    "exclusion_report",
    "suppress_entrant_benefit_outputs",
]

#: The four domains an entrant is excluded from, and why each one is unfitted.
EXCLUDED_DOMAINS: Mapping[str, str] = {
    "fertility_risk": (
        "steps.py:451-506 materializes births only for on-roster mothers and "
        "initializes parity at zero; no entrant parity or birth-history seed "
        "exists, so leaving entrants at risk would assert every entrant "
        "arrived childless"
    ),
    "claiming_eligibility": (
        "steps.py:390-450 draws a claim age for everyone aged 50+ with no "
        "insured-status, quarters-of-coverage, AIME or PIA test; reported "
        "year of entry does not identify FIRST entry, so prior US covered "
        "earnings are unknown/censored rather than zero and insured status "
        "cannot be established from either survey"
    ),
    "disability_panel": (
        "disability.py:56-60 filters a PSID-built DisabilityPanel to "
        "holdout_ids; entrants are not in the panel, and ASEC/CPS disability "
        "items are not realized PSID M4 status"
    ),
    "earnings_domain": (
        "earnings_domain.py:150-208 keys membership on the generator's fitted "
        "2014 state and forward_earnings.py:1421-1436 raises without it; the "
        "section 2.8.3a certificate was never fitted on entrants and does not "
        "transfer to them"
    ),
}


def entrant_mask(
    frame: pd.DataFrame,
    *,
    entry_kinds: Iterable[str] = (ENTRY_KIND_IMMIGRANT,),
) -> np.ndarray:
    """Boolean membership: is each row a scheduled entrant?

    Reads the explicit :data:`~populace_dynamics.engine.entrant_schedule.ENTRY_KIND_COLUMN`
    provenance column.  A frame without that column is a closed-panel frame
    and every row is an incumbent -- that is the honest reading, and it keeps
    this predicate safe to call on a roster that has never seen a schedule.
    A missing value on an existing column is likewise an incumbent, matching
    how ``earnings_domain_mask`` treats a new row's missing marker.
    """
    kinds = {str(kind) for kind in entry_kinds}
    if not kinds:
        raise ValueError("entrant_mask needs at least one entry kind")
    if ENTRY_KIND_COLUMN not in frame.columns:
        return np.zeros(len(frame), dtype=bool)
    values = frame[ENTRY_KIND_COLUMN].to_numpy()
    return np.asarray(
        [(not pd.isna(value)) and str(value) in kinds for value in values],
        dtype=bool,
    )


def _entrant_ids(frame: pd.DataFrame, **kwargs: Any) -> set[int]:
    mask = entrant_mask(frame, **kwargs)
    return {int(value) for value in frame.loc[mask, "person_id"]}


def excluded_fertility_ids(frame: pd.DataFrame, **kwargs: Any) -> set[int]:
    """Person IDs to remove from the fertility risk set.

    Pass the complement as ``apply_fertility(..., holdout_ids=...)``: that
    argument is already the fertility risk set -- ``steps.py:539`` forwards it
    to ``simulate_fertility``, which filters both the maternal draw and
    ``panel.attrs`` by it (``steps.py:185-207``) -- so the exclusion needs no
    change to the fertility step itself.
    """
    return _entrant_ids(frame, **kwargs)


def excluded_claiming_ids(frame: pd.DataFrame, **kwargs: Any) -> set[int]:
    """Person IDs whose claiming draw must be suppressed."""
    return _entrant_ids(frame, **kwargs)


def excluded_disability_ids(frame: pd.DataFrame, **kwargs: Any) -> set[int]:
    """Person IDs to keep out of the M4 disability panel's holdout set."""
    return _entrant_ids(frame, **kwargs)


def assert_entrants_out_of_earnings_domain(frame: pd.DataFrame) -> int:
    """Fail loudly if any entrant is marked inside the fitted earnings domain.

    Returns the number of entrants checked.  There is no "exclude" step to
    perform here -- ``earnings_domain.membership`` already excludes them by
    construction, because a synthetic ID cannot be in the fitted 2014 state
    maps.  This is the assertion that the construction was not circumvented,
    which is the failure mode ``validate_domain`` exists to catch.
    """
    mask = entrant_mask(frame)
    if not mask.any():
        return 0
    if EARNINGS_DOMAIN_COLUMN not in frame.columns:
        return int(mask.sum())
    marked = frame.loc[mask, EARNINGS_DOMAIN_COLUMN]
    offending = marked.fillna(False).astype(bool).to_numpy()
    if offending.any():
        bad = frame.loc[mask].loc[offending, "person_id"].tolist()[:10]
        raise ValueError(
            "scheduled entrants are marked inside the fitted earnings "
            f"domain: {bad}; the section 2.8.3a certificate does not transfer "
            "to a population it was never fitted on"
        )
    return int(mask.sum())


def suppress_entrant_benefit_outputs(
    frame: pd.DataFrame, *, columns: Iterable[str] = ("aime", "pia", "benefit")
) -> pd.DataFrame:
    """Blank entrant benefit outputs to missing, never to zero.

    A zero AIME is a *measurement*: it says this person had no covered
    earnings.  For an entrant it would be a fabrication, because reported year
    of entry does not identify first entry, so prior US covered earnings are
    censored rather than absent.  Missing is the only honest value until a
    stock-to-arrival and insured-status bridge exists.
    """
    out = frame.copy()
    mask = entrant_mask(out)
    if not mask.any():
        return out
    for column in columns:
        if column in out.columns:
            out.loc[mask, column] = pd.NA
    return out


@dataclass(frozen=True)
class EntrantExclusionReport:
    """What was excluded, from where, and how many -- for the run artifact."""

    n_rows: int
    n_entrants: int
    excluded: dict[str, dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "n_rows": self.n_rows,
            "n_entrants": self.n_entrants,
            "excluded_domains": self.excluded,
            "gated": False,
            "status": "reported",
            "interpretation": (
                "an excluded entrant is OUTSIDE the estimand for that domain, "
                "not a person modelled as having no children, no disability "
                "and no claim; suppressed counts are reported instead of "
                "zeros for exactly that reason"
            ),
            "residual_domains_entrants_do_enter": [
                "mortality (age/sex draw at the entry age)",
                "aging (deterministic advance)",
            ],
            "not_certified": (
                "entrant benefit levels, insured status, prior US covered "
                "earnings, legal status, population stocks and every "
                "post-entry transition remain out of scope"
            ),
        }


def exclusion_report(frame: pd.DataFrame) -> EntrantExclusionReport:
    """Measure the exclusions on one roster frame."""
    mask = entrant_mask(frame)
    n_entrants = int(mask.sum())
    age = (
        frame["age"].to_numpy(dtype=np.float64)
        if "age" in frame.columns
        else np.full(len(frame), np.nan)
    )
    claim_exposed = int((mask & (age >= 50)).sum())
    female = (
        frame["sex"].astype(str).to_numpy() == "female"
        if "sex" in frame.columns
        else np.zeros(len(frame), dtype=bool)
    )
    fertile_exposed = int((mask & female & (age >= 15) & (age <= 49)).sum())

    excluded: dict[str, dict[str, Any]] = {}
    for domain, reason in EXCLUDED_DOMAINS.items():
        record: dict[str, Any] = {
            "n_excluded": n_entrants,
            "reason": reason,
        }
        if domain == "claiming_eligibility":
            record["n_would_have_drawn_a_claim_age"] = claim_exposed
            record["counterfactual"] = (
                "without this exclusion apply_claiming would draw a claim age "
                f"for {claim_exposed} entrant rows aged 50+, each of whom "
                "carries a pinned zero earnings history"
            )
        if domain == "fertility_risk":
            record["n_would_have_been_at_risk"] = fertile_exposed
        if domain == "earnings_domain":
            record["n_checked_out_of_domain"] = (
                assert_entrants_out_of_earnings_domain(frame)
            )
        excluded[domain] = record
    return EntrantExclusionReport(
        n_rows=int(len(frame)), n_entrants=n_entrants, excluded=excluded
    )


@dataclass(frozen=True)
class EntrantClaimingAdapter:
    """Run a claiming step on incumbents only, leaving entrants unclaimed.

    The direct analogue of :class:`~populace_dynamics.engine.earnings_domain.EarningsDomainAdapter`:
    it keeps a support restriction OUTSIDE the certified step rather than
    editing the step.  ``apply_claiming`` is left exactly as gate_m6 certified
    it; entrant rows simply never reach it.

    An entrant's ``claim_age``, ``claimed`` and ``claim_year`` come back as
    missing / ``False`` / missing.  ``claimed = False`` is not a behavioural
    claim that entrants never retire -- it is the roster's structural default
    for a person outside the claiming estimand, and
    :func:`exclusion_report` publishes how many rows it applied to so the
    suppression is never mistaken for a measured zero.
    """

    step: Any
    entry_kinds: tuple[str, ...] = (ENTRY_KIND_IMMIGRANT,)

    def __call__(
        self,
        frame: pd.DataFrame,
        context: Any,
        rng: np.random.Generator,
    ) -> pd.DataFrame:
        mask = entrant_mask(frame, entry_kinds=self.entry_kinds)
        if not mask.any():
            return self.step(frame, context, rng)
        incumbents = frame.loc[~mask].copy()
        entrants = frame.loc[mask].copy()
        advanced = self.step(incumbents, context, rng)
        for column, default in (
            ("claim_age", pd.NA),
            ("claimed", False),
            ("claim_year", pd.NA),
        ):
            if column in advanced.columns and column not in entrants.columns:
                entrants[column] = default
            elif column in advanced.columns:
                entrants[column] = entrants[column].where(
                    entrants[column].notna(), default
                )
        out = pd.concat([advanced, entrants], ignore_index=True, sort=False)
        return out.sort_values("person_id", kind="stable").reset_index(
            drop=True
        )
