"""Label-verified nativity donor on the certified populace frame.

The **donor** for a scheduled-entrant cohort's composition.  Table V.A2
(:mod:`populace_dynamics.data.trustees_immigration`) sizes cohorts and carries
no age or sex detail; this module supplies the shape, read from the same
certified frame the engine deploys onto.

Structural precedent: :mod:`populace_dynamics.data.deployment_frame`, which
this module deliberately mirrors -- a ``REQUIRED_*_COLUMNS`` populated-guard,
a pure-function moment layer that is unit-testable on synthetic rows, and one
loader that touches the h5.  It reads the SAME pinned artifact
(:data:`deployment_frame.CERTIFIED_PIN`), so the donor universe is exactly the
``gate_w1`` deployment frame rather than a survey this repo has never staged.

Every code label below was read this session from the authoritative Census
sources, not inferred:

* ``PRCITSHP`` -- CPS ASEC 2024 data dictionary, person record, position 147.
* ``PEINUSYR`` -- the same dictionary, position 133; the bin tables for the
  2022 and 2023 vintages come from those vintages' own dictionaries.
* ``PENATVTY`` -- position 138.  The dictionary says "See Appendix H", which
  is a STALE cross-reference: Appendix H of the CPS technical documentation
  (``cpsmar24.pdf``) is the Source and Accuracy Statement.  The country codes
  are **Appendix I, "Countries and Areas of the World"**, where 057 = United
  States and 060/066/069/073/078 are the US outlying areas.

Three measured facts about this frame drive the design, all reproduced by
:func:`nativity_diagnostics`:

1. **No nativity column is a calibration target.**  ``deployment_frame``'s
   ``REQUIRED_SOURCE_COLUMNS`` guard does not list one, and the certified
   file's calibration does not pin the nativity margin, so its composition is
   a free consequence of the reweighting.
2. **The entry-year universe is exact.**  ``PEINUSYR == 0`` holds on exactly
   the ``PRCITSHP == 1`` rows (native, born in US) and on no others.
3. **``PEINUSYR``'s top code is vintage-dependent, and the frame is a pooled
   multi-vintage file.**  The certified frame carries ``source_year`` in
   {2022, 2023, 2024}.  Code 27 means 2020-2022 on the 2022 vintage,
   2020-2023 on the 2023 vintage, and 2020-2021 on the 2024 vintage, where
   the top code is 28 = 2022-2024.  A single crosswalk applied to the pooled
   file therefore mislabels arrival years.  :func:`arrival_band` is keyed on
   ``(source_year, code)`` for that reason, and
   :func:`vintage_domain_mismatch` reports the rows whose pair is outside the
   labelled vintage's published domain.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from populace_dynamics.data.deployment_frame import CERTIFIED_PIN

__all__ = [
    "CERTIFIED_PIN",
    "PRCITSHP_LABELS",
    "FOREIGN_BORN_CODES",
    "NATIVE_CODES",
    "PENATVTY_UNITED_STATES",
    "PENATVTY_OUTLYING_AREAS",
    "PEINUSYR_NOT_IN_UNIVERSE",
    "PEINUSYR_BINS_BY_VINTAGE",
    "REQUIRED_NATIVITY_COLUMNS",
    "DONOR_AGE_BANDS",
    "arrival_band",
    "assert_nativity_columns_populated",
    "attach_arrival_bands",
    "donor_composition",
    "load_nativity_persons",
    "nativity_diagnostics",
    "recent_arrival_donor",
    "synthetic_nativity_frame",
    "vintage_domain_mismatch",
]

#: CPS ASEC person item PRCITSHP, "CITIZENSHIP GROUP" (2024 dictionary,
#: position 147, range -4:5).  Verbatim value labels.
PRCITSHP_LABELS: Mapping[int, str] = {
    1: "Native, born in US",
    2: "Native, born in PR or US outlying area",
    3: "Native, born abroad of US parent(s)",
    4: "Foreign born, US cit by naturalization",
    5: "Foreign born, not a US citizen",
}
#: The two foreign-born codes.  Codes 2 and 3 are NATIVE despite being born
#: outside the fifty states -- treating them as foreign-born would overstate
#: the foreign-born margin by the PR/outlying-area and born-abroad-of-US-
#: parents populations.
FOREIGN_BORN_CODES: tuple[int, ...] = (4, 5)
NATIVE_CODES: tuple[int, ...] = (1, 2, 3)

#: PENATVTY country codes (CPS technical documentation, Appendix I).
PENATVTY_UNITED_STATES = 57
PENATVTY_OUTLYING_AREAS: Mapping[int, str] = {
    60: "American Samoa",
    66: "Guam",
    69: "Northern Marianas",
    73: "Puerto Rico",
    78: "U.S. Virgin Islands",
}

#: PEINUSYR "When did you come to the U.S. to stay?" -- 00 = NIU.
PEINUSYR_NOT_IN_UNIVERSE = 0

#: Codes 1-26 are identical in the 2022, 2023 and 2024 ASEC dictionaries.
_SHARED_ARRIVAL_BINS: Mapping[int, tuple[int, int]] = {
    # Code 1 is "Before 1950"; 1900 is a closed lower bound standing in for an
    # open one, and is never used for a recent-arrival donor.
    1: (1900, 1949),
    2: (1950, 1959),
    3: (1960, 1964),
    4: (1965, 1969),
    5: (1970, 1974),
    6: (1975, 1979),
    7: (1980, 1981),
    8: (1982, 1983),
    9: (1984, 1985),
    10: (1986, 1987),
    11: (1988, 1989),
    12: (1990, 1991),
    13: (1992, 1993),
    14: (1994, 1995),
    15: (1996, 1997),
    16: (1998, 1999),
    17: (2000, 2001),
    18: (2002, 2003),
    19: (2004, 2005),
    20: (2006, 2007),
    21: (2008, 2009),
    22: (2010, 2011),
    23: (2012, 2013),
    24: (2014, 2015),
    25: (2016, 2017),
    26: (2018, 2019),
}

#: ``source_year`` -> code -> inclusive (first, last) arrival year.  The top
#: code differs by vintage; everything below 27 is shared.  Read from each
#: vintage's own published data dictionary.
PEINUSYR_BINS_BY_VINTAGE: Mapping[int, Mapping[int, tuple[int, int]]] = {
    2022: {**_SHARED_ARRIVAL_BINS, 27: (2020, 2022)},
    2023: {**_SHARED_ARRIVAL_BINS, 27: (2020, 2023)},
    2024: {**_SHARED_ARRIVAL_BINS, 27: (2020, 2021), 28: (2022, 2024)},
}

#: The nativity source columns, with a plausible-support floor each.  The
#: sparse-57k certified default zeroes untargeted inputs and NO nativity
#: column is in ``deployment_frame.REQUIRED_SOURCE_COLUMNS``, so this guard is
#: the only thing standing between a future zeroed column and a silently
#: degenerate donor.  PEINUSYR's floor is low because its universe is the
#: non-native-born-in-US population only (~16% of rows).
REQUIRED_NATIVITY_COLUMNS: Mapping[str, float] = {
    "PENATVTY": 0.99,
    "PRCITSHP": 0.99,
    "PEINUSYR": 0.10,
}

#: Donor age bands.  Wider than ``deployment_frame.EARN_BANDS`` on purpose:
#: the memo's measured single-band support bottoms out at n=19 in the 65+
#: male cell, so the donor is reported on bands a floor could plausibly
#: price rather than on bands that would need demoting on sight.
DONOR_AGE_BANDS: tuple[tuple[int, int], ...] = (
    (0, 17),
    (18, 24),
    (25, 34),
    (35, 44),
    (45, 54),
    (55, 64),
    (65, 200),
)

#: The band-splitting rule this module implements, named so an artifact can
#: record which one produced it.  CPS year-of-entry is binned, so an ANNUAL
#: entrant cohort cannot be read off the survey; a rule is required and must
#: be stated rather than buried.
BAND_SPLIT_RULE = "band_midpoint_rounded_up"


def _band_label(lo: int, hi: int) -> str:
    return f"{lo}+" if hi >= 200 else f"{lo}-{hi}"


def _sex_label(is_female: bool) -> str:
    return "female" if is_female else "male"


def arrival_band(source_year: int, code: int) -> tuple[int, int] | None:
    """Inclusive (first, last) arrival year for one ``(vintage, code)`` pair.

    Returns ``None`` when the code is not in universe (0) or when the pair is
    outside the labelled vintage's published domain.  It does NOT fall back to
    another vintage's table: that fallback is precisely the mislabelling this
    function exists to prevent.
    """
    code = int(code)
    if code == PEINUSYR_NOT_IN_UNIVERSE:
        return None
    table = PEINUSYR_BINS_BY_VINTAGE.get(int(source_year))
    if table is None:
        return None
    return table.get(code)


def _midpoint(lo: int, hi: int) -> int:
    """The band's midpoint, rounded up -- :data:`BAND_SPLIT_RULE`.

    Rounding up reproduces the convention in microcosm's committed
    ``_ARRIVAL_YEAR_MIDPOINTS`` (1980-1981 -> 1981, 2010-2011 -> 2011), so the
    two crosswalks agree wherever both are defined.
    """
    return int(np.ceil((lo + hi) / 2))


def assert_nativity_columns_populated(
    person_table: pd.DataFrame,
) -> dict[str, float]:
    """Fail loudly if a nativity source column is (near-)all-zero.

    Returns the observed non-zero fractions for the artifact's
    populated-columns disclosure.  Mirrors
    ``deployment_frame.assert_columns_populated``.
    """
    fractions: dict[str, float] = {}
    for column, floor in REQUIRED_NATIVITY_COLUMNS.items():
        if column not in person_table.columns:
            raise ValueError(f"certified frame missing column: {column}")
        values = person_table[column].fillna(0).to_numpy()
        fraction = float((values != 0).mean())
        fractions[column] = fraction
        if fraction < floor:
            raise ValueError(
                f"column {column} non-zero fraction {fraction:.3f} below "
                f"floor {floor:.2f} -- the sparse frame appears to zero it; "
                "refusing to build a degenerate donor"
            )
    return fractions


def attach_arrival_bands(persons: pd.DataFrame) -> pd.DataFrame:
    """Add ``arrival_first``/``arrival_last``/``arrival_year`` per row.

    ``arrival_year`` applies :data:`BAND_SPLIT_RULE` to the band.  Rows out of
    universe, or whose ``(source_year, peinusyr)`` pair is undefined for the
    labelled vintage, get ``pd.NA`` in all three and are marked
    ``arrival_band_known = False``.
    """
    out = persons.copy()
    first: list[Any] = []
    last: list[Any] = []
    known: list[bool] = []
    for vintage, code in zip(
        out["source_year"].to_numpy(), out["peinusyr"].to_numpy(), strict=True
    ):
        band = arrival_band(int(vintage), int(code))
        if band is None:
            first.append(pd.NA)
            last.append(pd.NA)
            known.append(False)
        else:
            first.append(band[0])
            last.append(band[1])
            known.append(True)
    out["arrival_first"] = pd.array(first, dtype="Int64")
    out["arrival_last"] = pd.array(last, dtype="Int64")
    out["arrival_band_known"] = known
    midpoints = [
        _midpoint(int(lo), int(hi)) if ok else pd.NA
        for lo, hi, ok in zip(first, last, known, strict=True)
    ]
    out["arrival_year"] = pd.array(midpoints, dtype="Int64")
    return out


def vintage_domain_mismatch(persons: pd.DataFrame) -> dict[str, Any]:
    """Report rows in universe whose (vintage, code) pair is undefined.

    A non-zero count here is a measured inconsistency in the frame, not a
    reader bug: it means a row's ``source_year`` label does not identify the
    ASEC vintage whose ``PEINUSYR`` code domain its value belongs to.  It is
    surfaced rather than silently repaired, because repairing it would require
    asserting an arrival year the source does not support.
    """
    in_universe = persons["peinusyr"].to_numpy() != PEINUSYR_NOT_IN_UNIVERSE
    known = persons["arrival_band_known"].to_numpy(dtype=bool)
    bad = in_universe & ~known
    pairs = (
        persons.loc[bad]
        .groupby(["source_year", "peinusyr"])
        .size()
        .sort_index()
    )
    return {
        "rows_in_universe": int(in_universe.sum()),
        "rows_with_undefined_band": int(bad.sum()),
        "undefined_pairs": {
            f"source_year={int(vintage)},peinusyr={int(code)}": int(count)
            for (vintage, code), count in pairs.items()
        },
        "interpretation": (
            "each listed (source_year, peinusyr) pair carries a code the "
            "labelled ASEC vintage's published data dictionary does not "
            "define; no arrival year is asserted for those rows"
        ),
    }


def nativity_diagnostics(persons: pd.DataFrame) -> dict[str, Any]:
    """Reproduce the frame's measured nativity counts and identities.

    Pure function of a person frame, so it is unit-testable on synthetic rows.
    Every published number an artifact quotes about the donor comes from here.
    """
    weight = persons["weight"].to_numpy(dtype=np.float64)
    citizenship = persons["prcitshp"].to_numpy(dtype=np.int64)
    entry_code = persons["peinusyr"].to_numpy(dtype=np.int64)
    total_weight = float(weight.sum())

    foreign_born = np.isin(citizenship, FOREIGN_BORN_CODES)
    identity_holds = bool(
        np.array_equal(
            entry_code == PEINUSYR_NOT_IN_UNIVERSE, citizenship == 1
        )
    )

    by_code = {
        int(code): {
            "label": PRCITSHP_LABELS.get(int(code), "UNDOCUMENTED CODE"),
            "n_rows": int((citizenship == code).sum()),
            "weighted": float(weight[citizenship == code].sum()),
        }
        for code in sorted(set(citizenship.tolist()))
    }

    age = persons["age"].to_numpy(dtype=np.float64)
    by_band: dict[str, Any] = {}
    for lo, hi in DONOR_AGE_BANDS:
        in_band = (age >= lo) & (age <= hi)
        band_weight = float(weight[in_band].sum())
        cell = in_band & foreign_born
        by_band[_band_label(lo, hi)] = {
            "n_rows": int(in_band.sum()),
            "n_foreign_born": int(cell.sum()),
            "foreign_born_share": (
                float(weight[cell].sum() / band_weight)
                if band_weight > 0
                else float("nan")
            ),
        }

    return {
        "n_rows": int(len(persons)),
        "weighted_persons": total_weight,
        "prcitshp_counts": by_code,
        "entry_year_universe_identity": {
            "statement": "PEINUSYR == 0 holds exactly on PRCITSHP == 1",
            "holds": identity_holds,
            "n_peinusyr_zero": int(
                (entry_code == PEINUSYR_NOT_IN_UNIVERSE).sum()
            ),
            "n_prcitshp_native_born_us": int((citizenship == 1).sum()),
        },
        "foreign_born": {
            "codes": list(FOREIGN_BORN_CODES),
            "n_rows": int(foreign_born.sum()),
            "weighted": float(weight[foreign_born].sum()),
            "share": (
                float(weight[foreign_born].sum() / total_weight)
                if total_weight > 0
                else float("nan")
            ),
        },
        "foreign_born_share_by_age_band": by_band,
        "penatvty": {
            "n_distinct_codes": int(persons["penatvty"].nunique()),
            "n_united_states": int(
                (persons["penatvty"] == PENATVTY_UNITED_STATES).sum()
            ),
            "n_outlying_areas": int(
                persons["penatvty"].isin(PENATVTY_OUTLYING_AREAS).sum()
            ),
        },
        "calibration_status": (
            "UNCALIBRATED: no nativity column appears in "
            "deployment_frame.REQUIRED_SOURCE_COLUMNS and the certified "
            "file pins no nativity margin, so this composition is a free "
            "consequence of the reweighting, not a target it hit"
        ),
    }


def recent_arrival_donor(
    persons: pd.DataFrame,
    *,
    vintage: int = 2024,
    codes: tuple[int, ...] = (28,),
    foreign_born_only: bool = True,
) -> pd.DataFrame:
    """The recent-arrival donor pool, restricted to ONE ASEC vintage.

    Restricting to a single vintage is not fastidiousness: code 27 spans
    2020-2022 on the 2022 vintage and 2020-2021 on the 2024 vintage, so a
    pooled draw mixes two different arrival windows under one label.

    ``foreign_born_only`` restricts the pool to ``PRCITSHP`` in
    :data:`FOREIGN_BORN_CODES`, and defaults to ``True`` because the donor's
    universe has to match the control's.  ``PEINUSYR``'s universe is everyone
    NOT born in the fifty states, so the recent-arrival band also contains
    **natives**: people born in Puerto Rico or a US outlying area
    (``PRCITSHP == 2``) and people born abroad of US parents
    (``PRCITSHP == 3``) who came to the US to stay in the same window.  On the
    certified frame's 2024-vintage top band those are 30 of 1,185 rows.  They
    are genuine arrivals to the resident population, but they are US citizens
    at birth and appear in NEITHER of Table V.A2's two stocks -- their move is
    internal migration, not immigration.  Sizing them against a V.A2 inflow
    would put people the control never counted into the cohort.

    Adds ``entry_age`` = ``age - (source_year - arrival_year)``, clipped at
    zero.  This remains a **stock proxy**: the survey observes a resident
    survivor/stayer at interview, not an arrival, and age is the only
    covariate for which the two are close.  The restriction to the most recent
    band is what keeps the interview-minus-arrival lag short (0-2 years here),
    which is the whole reason the proxy is tolerable for age and sex and
    tolerable for nothing else.
    """
    table = PEINUSYR_BINS_BY_VINTAGE.get(int(vintage))
    if table is None:
        raise ValueError(
            f"no published PEINUSYR bin table for ASEC vintage {vintage}"
        )
    unknown = [code for code in codes if int(code) not in table]
    if unknown:
        raise ValueError(
            f"PEINUSYR code(s) {unknown} are undefined for ASEC vintage "
            f"{vintage}; refusing to draw a donor from an unlabelled band"
        )
    mask = (persons["source_year"].to_numpy() == int(vintage)) & np.isin(
        persons["peinusyr"].to_numpy(), list(codes)
    )
    if foreign_born_only:
        mask &= persons["foreign_born"].to_numpy(dtype=bool)
    donor = persons.loc[mask].copy()
    if donor.empty:
        raise ValueError(
            f"recent-arrival donor is empty for vintage {vintage} codes "
            f"{codes}"
        )
    if not donor["arrival_band_known"].all():
        raise ValueError("donor rows carry an undefined arrival band")
    lag = donor["source_year"].to_numpy(dtype=np.int64) - donor[
        "arrival_year"
    ].to_numpy(dtype=np.int64)
    donor["arrival_lag_years"] = lag
    donor["entry_age"] = np.maximum(
        donor["age"].to_numpy(dtype=np.float64) - lag, 0.0
    )
    return donor.reset_index(drop=True)


def donor_composition(
    donor: pd.DataFrame,
    *,
    bands: tuple[tuple[int, int], ...] = DONOR_AGE_BANDS,
    age_column: str = "entry_age",
) -> dict[str, dict[str, Any]]:
    """Weighted (age band x sex) shares of the donor pool, summing to one.

    Each cell publishes its raw ``n_rows`` alongside the share, because a
    share whose support is not stated cannot be floor-priced.
    """
    weight = donor["weight"].to_numpy(dtype=np.float64)
    age = donor[age_column].to_numpy(dtype=np.float64)
    female = donor["is_female"].to_numpy(dtype=bool)
    total = float(weight.sum())
    if total <= 0:
        raise ValueError("donor pool carries no positive weight")
    cells: dict[str, dict[str, Any]] = {}
    for lo, hi in bands:
        in_band = (age >= lo) & (age <= hi)
        for is_f in (True, False):
            mask = in_band & (female == is_f)
            key = f"{_band_label(lo, hi)}|{_sex_label(is_f)}"
            cells[key] = {
                "share": float(weight[mask].sum() / total),
                "weighted": float(weight[mask].sum()),
                "n_rows": int(mask.sum()),
                "age_band": _band_label(lo, hi),
                "sex": _sex_label(is_f),
            }
    residual = 1.0 - sum(cell["share"] for cell in cells.values())
    if abs(residual) > 1e-9:
        raise ValueError(
            f"donor composition shares miss unity by {residual:.3e}; the "
            "age bands do not cover the donor pool"
        )
    return cells


def load_nativity_persons(
    h5_path: str,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Read the certified populace h5 into the nativity person frame.

    Returns ``(persons, populated_fractions)``.  The person weight is the
    person's household weight, exactly as
    ``deployment_frame.load_certified_persons`` computes it, so the two
    modules cannot disagree about the denominator.  Imports are local so
    importing this module needs neither pytables nor the h5.
    """
    with pd.HDFStore(h5_path, mode="r") as store:
        person = store["/person"]
        household = store["/household"]

    fractions = assert_nativity_columns_populated(person)

    household_weight = household.set_index("household_id")["household_weight"]
    weight = (
        person["person_household_id"]
        .map(household_weight)
        .to_numpy(dtype=np.float64)
    )
    persons = pd.DataFrame(
        {
            "person_id": person["person_id"].to_numpy(),
            "household_id": person["person_household_id"].to_numpy(),
            "weight": weight,
            "age": person["age"].to_numpy(dtype=np.float64),
            "is_female": person["is_female"].astype(bool).to_numpy(),
            "penatvty": person["PENATVTY"].to_numpy(dtype=np.int64),
            "prcitshp": person["PRCITSHP"].to_numpy(dtype=np.int64),
            "peinusyr": person["PEINUSYR"].to_numpy(dtype=np.int64),
            "source_year": person["source_year"].to_numpy(dtype=np.int64),
        }
    )
    undocumented = sorted(
        set(persons["prcitshp"].tolist()) - set(PRCITSHP_LABELS)
    )
    if undocumented:
        raise ValueError(
            f"PRCITSHP carries value(s) outside the labelled ASEC domain "
            f"1..5: {undocumented}"
        )
    persons["foreign_born"] = persons["prcitshp"].isin(FOREIGN_BORN_CODES)
    return attach_arrival_bands(persons), fractions


def synthetic_nativity_frame(n: int = 600, seed: int = 0) -> pd.DataFrame:
    """A deterministic synthetic nativity frame for unit tests (no h5).

    Built to satisfy the same invariants the certified frame satisfies: the
    ``PEINUSYR == 0`` / ``PRCITSHP == 1`` identity holds exactly, and every
    ``(source_year, peinusyr)`` pair is defined for its vintage.
    """
    rng = np.random.default_rng(seed)
    age = rng.integers(0, 85, size=n).astype(float)
    is_female = rng.random(n) < 0.5
    source_year = rng.choice([2022, 2023, 2024], size=n)
    citizenship = rng.choice(
        [1, 2, 3, 4, 5], size=n, p=[0.70, 0.01, 0.01, 0.12, 0.16]
    )
    entry_code = np.zeros(n, dtype=np.int64)
    for index in range(n):
        if citizenship[index] == 1:
            continue
        table = PEINUSYR_BINS_BY_VINTAGE[int(source_year[index])]
        codes = sorted(table)
        # Weight the recent bands up so a recent-arrival donor drawn from a
        # small synthetic frame has usable support; the certified frame has
        # roughly comparable counts across the recent codes.
        weights = np.array(
            [8.0 if code >= codes[-4] else 1.0 for code in codes]
        )
        entry_code[index] = int(rng.choice(codes, p=weights / weights.sum()))
    country = np.where(
        citizenship == 1, PENATVTY_UNITED_STATES, rng.integers(100, 556, n)
    )
    household_id = rng.integers(0, max(2, n // 2), size=n)
    persons = pd.DataFrame(
        {
            "person_id": np.arange(n),
            "household_id": household_id,
            "weight": rng.uniform(500, 5000, size=n),
            "age": age,
            "is_female": is_female,
            "penatvty": country.astype(np.int64),
            "prcitshp": citizenship.astype(np.int64),
            "peinusyr": entry_code,
            "source_year": source_year.astype(np.int64),
        }
    )
    persons["foreign_born"] = persons["prcitshp"].isin(FOREIGN_BORN_CODES)
    return attach_arrival_bands(persons)


@dataclass(frozen=True)
class NativityDonor:
    """A donor pool plus everything an artifact must republish about it."""

    pool: pd.DataFrame
    composition: dict[str, dict[str, Any]]
    vintage: int
    codes: tuple[int, ...]

    def provenance(self) -> dict[str, Any]:
        band = PEINUSYR_BINS_BY_VINTAGE[self.vintage]
        arrival_windows = {
            str(code): list(band[int(code)]) for code in self.codes
        }
        return {
            "donor_source": "certified populace deployment frame",
            "certified_pin": dict(CERTIFIED_PIN),
            "asec_vintage": self.vintage,
            "peinusyr_codes": list(self.codes),
            "arrival_windows": arrival_windows,
            "band_split_rule": BAND_SPLIT_RULE,
            "n_donor_rows": int(len(self.pool)),
            "weighted_donor_persons": float(self.pool["weight"].sum()),
            "universe": "foreign_born_prcitshp_4_or_5",
            "universe_reason": (
                "PEINUSYR's universe is everyone not born in the fifty "
                "states, so the recent-arrival band also holds natives born "
                "in PR/outlying areas (PRCITSHP 2) and abroad of US parents "
                "(PRCITSHP 3). They are US citizens at birth and appear in "
                "neither of Table V.A2's stocks -- internal migration, not "
                "immigration -- so they are excluded to match the control's "
                "universe"
            ),
            "n_foreign_born_rows": int(self.pool["foreign_born"].sum()),
            "stock_proxy_disclosure": (
                "stock_proxy: the survey observes a resident survivor/stayer "
                "at interview, not an arrival. Education, marriage, "
                "disability, employment, earnings and residence all change "
                "between reported entry and interview; only age and sex are "
                "carried, and only because the donor is restricted to the "
                "most recent arrival band (lag 0-2 years)"
            ),
            "annual_resolution_disclosure": (
                "CPS year-of-entry is binned, so this donor cannot produce an "
                f"annual arrival cohort directly; {BAND_SPLIT_RULE} is the "
                "stated rule applied, and it is not gradeable against CPS "
                "itself. ACS PUMS YOEP would buy annual resolution and is "
                "the named successor artifact"
            ),
        }
