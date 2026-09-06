"""Reader-free tests for the registered M6 input factory (§2.8.10.4).

Always runnable: they exercise each factory step -- the pe-us version gate
and its parameter-dir binding, the claiming sha256 tamper gate, the
NAWI/wage-base replacement rule, the NCHS 2010 band collapse, the ``<= T*``
mortality-exposure adapter, and the inert ``(0, 24)`` projection-coverage pad
with its ``fit_mortality_model`` bridge (§2.8.10.5) -- on synthetic frames
and the committed references. They deliberately do **not**
run ``build_inputs()`` end-to-end (which reads staged PSID and is reserved for
the registered gate), execute no scored run, compute no gate cell, and never
touch ``gates.yaml``.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from populace_dynamics.engine.forward_earnings import fit_projected_wage_index
from populace_dynamics.engine.refit import (
    fit_mortality_model,
    prepare_mortality_refit_inputs,
    validate_external_vintage,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_mortality_floors as mf  # noqa: E402
import registered_m6_inputs as factory  # noqa: E402

# The seven columns the mortality fit consumes. Deliberately *not* extended
# with ``person_id``: ``_fourteen_cell_exposure`` builds its frame from this
# list, and the pad's identity behaviour on an id-free seven-column input is
# itself part of the contract under test.
_MORTALITY_COLUMNS = [
    "event_year",
    "required_interview_year",
    "age_band",
    "sex",
    "start_weight",
    "exposure",
    "death",
]

# What the adapter emits: the seven fit columns behind the person key.
_ADAPTER_COLUMNS = ["person_id", *_MORTALITY_COLUMNS]


# --------------------------------------------------------------------------
# Step 1 -- the policyengine-us version gate
# --------------------------------------------------------------------------
def test__version_gate__passes_on_the_pinned_version():
    assert factory.assert_pe_us_version("1.752.2") == "1.752.2"


def test__version_gate__fires_on_a_wrong_version():
    with pytest.raises(RuntimeError, match="1.752.2"):
        factory.assert_pe_us_version("9.9.9")


def test__version_gate__default_reads_importlib_metadata(monkeypatch):
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "1.752.2")
    assert factory.assert_pe_us_version() == "1.752.2"
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "1.700.0")
    with pytest.raises(RuntimeError):
        factory.assert_pe_us_version()


def test__version_gate__pins_the_certified_frame_constant():
    from populace_dynamics.data.deployment_frame import CERTIFIED_PIN

    assert CERTIFIED_PIN["model_version"] == factory.PINNED_PE_US_VERSION
    assert factory.PINNED_PE_US_VERSION == "1.752.2"


# --------------------------------------------------------------------------
# Step 1 -- the parameter-dir binding (§2.8.10.5, F2)
# --------------------------------------------------------------------------
class _FakeDistribution:
    """Stand-in for ``importlib.metadata.distribution("policyengine-us")``."""

    def __init__(self, site: Path):
        self._site = site

    def locate_file(self, name: str) -> Path:
        return self._site / name


def _fake_install(root: Path) -> Path:
    (root / "policyengine_us" / "parameters" / "gov" / "ssa").mkdir(
        parents=True
    )
    return root


def test__param_dir_gate__passes_when_dir_is_the_versioned_install(
    tmp_path, monkeypatch
):
    site = _fake_install(tmp_path / "site-packages")
    monkeypatch.setattr(
        importlib.metadata,
        "distribution",
        lambda name: _FakeDistribution(site),
    )
    resolved = factory.assert_pe_us_param_dir(site)
    assert (
        resolved
        == (site / "policyengine_us" / "parameters" / "gov" / "ssa").resolve()
    )


def test__param_dir_gate__fires_on_a_mismatched_root(tmp_path, monkeypatch):
    # A parallel checkout passes the version gate (metadata is env-wide) but
    # must not pass the dir binding -- the silent-wrong-load seam.
    site = _fake_install(tmp_path / "site-packages")
    checkout = _fake_install(tmp_path / "checkout")
    monkeypatch.setattr(
        importlib.metadata,
        "distribution",
        lambda name: _FakeDistribution(site),
    )
    with pytest.raises(RuntimeError, match="metadata-versioned"):
        factory.assert_pe_us_param_dir(checkout)


def test__param_dir_gate__default_reads_the_loader_env_resolution(
    tmp_path, monkeypatch
):
    # No injected root: the gate resolves exactly as load_ssa_parameters
    # does (the loader's own env var when set; referenced through the
    # loader's constant, since these fake-install tests need no real
    # policyengine-us and stay in the always-run tier). Bound to the
    # versioned install -> passes; re-pointed at a foreign checkout ->
    # fires.
    from populace_dynamics.ss import params as ss_params

    site = _fake_install(tmp_path / "site-packages")
    checkout = _fake_install(tmp_path / "checkout")
    monkeypatch.setattr(
        importlib.metadata,
        "distribution",
        lambda name: _FakeDistribution(site),
    )
    monkeypatch.setenv(ss_params._PE_US_ENV, str(site))
    assert (
        factory.assert_pe_us_param_dir()
        == (site / "policyengine_us" / "parameters" / "gov" / "ssa").resolve()
    )
    monkeypatch.setenv(ss_params._PE_US_ENV, str(checkout))
    with pytest.raises(RuntimeError, match="metadata-versioned"):
        factory.assert_pe_us_param_dir()


# --------------------------------------------------------------------------
# Step 2 -- the leakage-safe NAWI / wage-base surface
# --------------------------------------------------------------------------
def _synthetic_nawi() -> dict[int, float]:
    # Realized trailing decade [2005, 2014] plus post-boundary realized values
    # that differ from the projection, so a correct replacement is visible.
    nawi = {
        year: 1000.0 * (1.03 ** (year - 2005)) for year in range(2005, 2015)
    }
    nawi.update({2015: 90000.0, 2016: 91000.0, 2020: 95000.0})
    return nawi


def test__nawi_rule__replaces_post_boundary_with_iproj_exactly():
    nawi = _synthetic_nawi()
    wage_base = {2013: 113700.0, 2014: 117000.0, 2015: 118500.0}
    new_nawi, _ = factory.replace_nawi_wage_base(nawi, wage_base)
    projection = fit_projected_wage_index(nawi, boundary_year=2014)
    for year in (2015, 2016, 2020):
        assert new_nawi[year] == projection.projected(year)
        # the realized post-boundary value is gone (replaced, not kept).
        assert new_nawi[year] != nawi[year]


def test__nawi_rule__keeps_realized_pre_boundary_and_the_key_range():
    nawi = _synthetic_nawi()
    new_nawi, _ = factory.replace_nawi_wage_base(nawi, {2014: 117000.0})
    assert set(new_nawi) == set(nawi)  # max(nawi) key unchanged
    for year in range(2005, 2015):
        assert new_nawi[year] == nawi[year]


def test__wage_base_rule__truncates_change_years_after_the_boundary():
    nawi = _synthetic_nawi()
    wage_base = {
        2013: 113700.0,
        2014: 117000.0,
        2015: 118500.0,
        2017: 127200.0,
    }
    _, new_wage_base = factory.replace_nawi_wage_base(nawi, wage_base)
    assert sorted(new_wage_base) == [2013, 2014]
    assert new_wage_base[2014] == 117000.0


# --------------------------------------------------------------------------
# Step 3 -- the claiming reference sha256 tamper gate
# --------------------------------------------------------------------------
def test__claiming_json__sha256_equals_the_pinned_factory_constant():
    digest = hashlib.sha256(
        factory.CLAIMING_REFERENCE_PATH.read_bytes()
    ).hexdigest()
    assert digest == factory.CLAIMING_REFERENCE_SHA256


def test__sha_gate__loads_the_untampered_reference():
    reference = factory.load_claiming_reference()
    assert reference.supplement_year == 2014
    assert reference.schema_version == "ssa_claim_ages.v1"


def test__sha_gate__fires_on_a_tampered_reference(tmp_path):
    tampered = tmp_path / "claim.json"
    doc = json.loads(factory.CLAIMING_REFERENCE_PATH.read_text())
    doc["data"]["male"]["2013"]["number_thousands"] += 1
    tampered.write_text(json.dumps(doc, indent=2) + "\n")
    with pytest.raises(ValueError, match="sha256"):
        factory.load_claiming_reference(tampered)


# --------------------------------------------------------------------------
# Step 4a -- NCHS 2010 external central rates
# --------------------------------------------------------------------------
def test__nchs_rates__have_the_pinned_columns_and_fourteen_rows():
    rates = factory.nchs_2010_external_rates()
    assert list(rates.columns) == [
        "lower_age",
        "upper_age",
        "age_band",
        "sex",
        "central_rate",
    ]
    # seven MORTALITY_BANDS x {female, male}.
    assert len(rates) == 14
    assert set(rates["sex"]) == {"female", "male"}
    assert rates.set_index(["age_band", "sex"]).index.is_unique


def test__nchs_rates__reshape_the_canonical_band_collapse():
    rates = factory.nchs_2010_external_rates()
    canonical = mf.nchs_band_rates(
        json.loads(factory.NCHS_2010_PATH.read_text())
    )
    for row in rates.itertuples(index=False):
        assert row.central_rate == canonical[f"{row.age_band}|{row.sex}"]
        # the endpoints are the band bounds; the open top band is 85+.
        assert row.age_band == mf.band_label(row.lower_age, row.upper_age)
    top = rates[rates["age_band"] == "85+"].iloc[0]
    assert (int(top.lower_age), int(top.upper_age)) == (85, 120)


def test__nchs_rates__reject_a_wrong_vintage(tmp_path):
    doc = json.loads(factory.NCHS_2010_PATH.read_text())
    doc["vintage_year"] = 2023
    path = tmp_path / "nchs.json"
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="vintage"):
        factory.nchs_2010_external_rates(path)


# --------------------------------------------------------------------------
# Step 4b -- the <= T* mortality-exposure adapter
# --------------------------------------------------------------------------
def _synthetic_panels():
    # Biennial waves 2011, 2013, 2015. Person 1 survives; person 2 dies in
    # 2012 (inside the 2011->2013 interval).
    demo = pd.DataFrame(
        {
            "person_id": [1, 1, 1, 2, 2],
            "period": [2011, 2013, 2015, 2011, 2013],
            "age": [40, 42, 44, 60, 62],
            "weight": [1.0, 1.0, 1.0, 2.0, 2.0],
            "interview": [1, 1, 1, 1, 1],
        }
    )
    death_records = pd.DataFrame(
        {
            "person_id": [1, 2],
            "sex": ["female", "male"],
            "death_year": pd.array([pd.NA, 2012], dtype="Int64"),
        }
    )
    return demo, death_records


def test__adapter__emits_exactly_the_eight_pinned_columns():
    demo, deaths = _synthetic_panels()
    adapted = factory.mortality_exposure_adapter(demo, deaths)
    assert list(adapted.columns) == _ADAPTER_COLUMNS
    assert list(factory.MORTALITY_EXPOSURE_COLUMNS) == _ADAPTER_COLUMNS


def test__adapter__carries_the_slice_person_key_unchanged():
    # person_id is the key build_exposure_slices already emits and the
    # adapter already merges on; retaining it must not renumber anything.
    demo, deaths = _synthetic_panels()
    adapted = factory.mortality_exposure_adapter(demo, deaths)
    slices = mf.build_exposure_slices(demo, deaths)
    emitted = slices[slices["start_wave"] <= 2014]
    assert set(adapted["person_id"]) == set(emitted["person_id"])
    assert adapted["person_id"].dtype.kind == "i"
    # every id belongs to a person in the supplied panel; none is invented.
    assert set(adapted["person_id"]) <= set(demo["person_id"])


def test__adapter__emits_no_repeated_person_year():
    demo, deaths = _synthetic_panels()
    adapted = factory.mortality_exposure_adapter(demo, deaths)
    assert not adapted.duplicated(["person_id", "event_year"]).any()


def test__adapter__refuses_a_panel_that_repeats_a_person_year():
    # A duplicated (person_id, period) panel row would double the exposure
    # denominator; the adapter fails closed instead of fitting it.
    demo, deaths = _synthetic_panels()
    # Person 1's 2011 wave twice: its biennial interval yields two slices,
    # so four rows carry a repeated (person_id, event_year).
    doubled = pd.concat([demo, demo.iloc[[0]]], ignore_index=True)
    with pytest.raises(
        ValueError,
        match=r"repeats 4 \(person_id, event_year\) row\(s\); "
        r"first keys \[\(1, 2011\), \(1, 2012\)\]",
    ):
        factory.mortality_exposure_adapter(doubled, deaths)


def test__unique_person_years__reports_the_offending_keys():
    frame = pd.DataFrame(
        {"person_id": [1001, 1001, 1002], "event_year": [2011, 2011, 2011]}
    )
    with pytest.raises(ValueError, match=r"\[\(1001, 2011\)\]"):
        factory.assert_unique_person_years(frame)


def test__unique_person_years__passes_an_id_free_frame_through():
    # The seven-column shape has no identity to check. Compare against an
    # independent copy taken before the call, not against `frame` itself --
    # the function returns the same object it was given, so comparing the
    # result to `frame` would compare an object with itself and could not
    # detect an in-place mutation.
    frame = _fourteen_cell_exposure()
    expected = frame.copy()
    result = factory.assert_unique_person_years(frame)
    pd.testing.assert_frame_equal(result, expected)


def test__unique_person_years__reports_a_malformed_key_without_crashing():
    # A NaN or a non-numeric string id must still produce the duplicate
    # diagnostic, not an unrelated int-conversion error.
    frame = pd.DataFrame(
        {
            "person_id": [float("nan"), float("nan"), "abc"],
            "event_year": [2011, 2011, 2012],
        }
    )
    with pytest.raises(
        ValueError, match=r"repeats 2 \(person_id, event_year\) row\(s\)"
    ):
        factory.assert_unique_person_years(frame)


def test__adapter__dates_every_slice_by_its_interval_closing_wave():
    demo, deaths = _synthetic_panels()
    adapted = factory.mortality_exposure_adapter(demo, deaths)
    grid = sorted(demo["period"].unique())
    closing = {grid[i]: grid[i + 1] for i in range(len(grid) - 1)}
    # required_interview_year is the interval's closing wave on every slice.
    for row in adapted.itertuples(index=False):
        # each slice's start wave is event_year (slice 0) or event_year-1.
        assert row.required_interview_year in closing.values()
    # event_year advances 0/1 within a biennial interval.
    assert set(adapted["event_year"]) == {2011, 2012, 2013, 2014}


def test__adapter__marks_the_death_year_slice():
    demo, deaths = _synthetic_panels()
    adapted = factory.mortality_exposure_adapter(demo, deaths)
    death_slice = adapted[
        (adapted["sex"] == "male") & (adapted["event_year"] == 2012)
    ]
    assert len(death_slice) == 1
    assert death_slice.iloc[0]["exposure"] == 0.5
    assert death_slice.iloc[0]["death"] == 1.0
    # survivor slices carry full exposure and no death.
    survivors = adapted[adapted["death"] == 0.0]
    assert (survivors["exposure"] == 1.0).all()


def test__adapter__drops_the_2013_to_2015_interval_under_truncation():
    demo, deaths = _synthetic_panels()
    adapted = factory.mortality_exposure_adapter(demo, deaths)
    # the boundary-straddling interval is emitted (closing wave 2015)...
    assert (adapted["required_interview_year"] == 2015).any()
    prepared = prepare_mortality_refit_inputs(
        adapted,
        factory.nchs_2010_external_rates(),
        external_vintage_year=2010,
        boundary_year=2014,
    )
    kept = prepared.exposure
    # ...and dropped wholesale by the closing-wave truncation.
    assert (kept["required_interview_year"] == 2015).sum() == 0
    assert int(kept["event_year"].max()) == 2012  # window ends 2011->2013


def test__adapter__age_band_uses_the_shared_band_label():
    demo, deaths = _synthetic_panels()
    adapted = factory.mortality_exposure_adapter(demo, deaths)
    assert set(adapted["age_band"]) <= set(mf.BAND_LABELS)


def test__adapter__dates_event_year_by_true_start_wave_age():
    # A person aged 24 at the start wave: build_exposure_slices drops the
    # age-24 slice (out of band) and keeps the age-25 second slice. event_year
    # must be start_wave + 1 (the age-25 slice's calendar year), read from the
    # panel's true start-wave age, not inferred from the surviving slice.
    demo = pd.DataFrame(
        {
            "person_id": [7, 7],
            "period": [2011, 2013],
            "age": [24, 26],
            "weight": [1.0, 1.0],
            "interview": [1, 1],
        }
    )
    death_records = pd.DataFrame(
        {
            "person_id": [7],
            "sex": ["female"],
            "death_year": pd.array([pd.NA], dtype="Int64"),
        }
    )
    adapted = factory.mortality_exposure_adapter(demo, death_records)
    band_25 = adapted[adapted["age_band"] == "25-34"]
    assert set(band_25["event_year"]) == {2012}
    assert set(band_25["required_interview_year"]) == {2013}


# --------------------------------------------------------------------------
# Step 4c -- the (0, 24) projection-coverage pad + the fit_mortality_model
# bridge (§2.8.10.5, F1)
# --------------------------------------------------------------------------
def _fourteen_cell_exposure() -> pd.DataFrame:
    # One <= T* slice per band x sex with distinct death counts, so every
    # fitted 25+ probability is distinct and hand-recomputable.
    rows = []
    for b, (lo, hi) in enumerate(mf.BANDS):
        for s, sex in enumerate(mf.SEXES):
            rows.append(
                {
                    "event_year": 2012,
                    "required_interview_year": 2013,
                    "age_band": mf.band_label(lo, hi),
                    "sex": sex,
                    "start_weight": 1.0 + 0.5 * s,
                    "exposure": 100.0,
                    "death": float(1 + 2 * b + s),
                }
            )
    return pd.DataFrame(rows, columns=_MORTALITY_COLUMNS)


def _fit(external: pd.DataFrame, exposure: pd.DataFrame):
    # The run's exact route: prepare (<= T* truncation + vintage check) then
    # fit -- the bridge no committed test previously exercised on
    # factory-shaped rates.
    return fit_mortality_model(
        prepare_mortality_refit_inputs(
            exposure,
            external,
            external_vintage_year=2010,
            boundary_year=2014,
        )
    )


def test__unpadded_seven_band_rates__fail_the_projection_model():
    # Without the pad the registered run dies at its FIRST phase: the
    # external rows yield bands starting at 25, and AgeSexMortalityModel
    # requires coverage from age 0.
    with pytest.raises(ValueError, match="start at age zero"):
        _fit(factory.nchs_2010_external_rates(), _fourteen_cell_exposure())


def test__pad__appends_two_rows_per_input_and_mutates_neither():
    external = factory.nchs_2010_external_rates()
    exposure = _fourteen_cell_exposure()
    external_before = external.copy()
    exposure_before = exposure.copy()
    padded_external, padded_exposure = (
        factory._pad_below_25_projection_coverage(
            external, exposure, boundary_year=2014
        )
    )
    pd.testing.assert_frame_equal(external, external_before)
    pd.testing.assert_frame_equal(exposure, exposure_before)
    assert len(padded_external) == len(external) + 2
    assert len(padded_exposure) == len(exposure) + 2
    pad = padded_external[padded_external["age_band"] == "0-24"]
    assert set(pad["sex"]) == {"female", "male"}
    assert (pad["lower_age"] == 0).all()
    assert (pad["upper_age"] == 24).all()


def test__pad__external_rate_is_the_nchs_0_24_central_rate():
    padded_external, _ = factory._pad_below_25_projection_coverage(
        factory.nchs_2010_external_rates(),
        _fourteen_cell_exposure(),
        boundary_year=2014,
    )
    nchs = json.loads(factory.NCHS_2010_PATH.read_text())
    for sex in mf.SEXES:
        rows = {r["age"]: r for r in nchs["tables"][sex]}
        expected = (rows[0]["lx"] - rows[25]["lx"]) / (
            rows[0]["Tx"] - rows[25]["Tx"]
        )
        got = padded_external[
            (padded_external["age_band"] == "0-24")
            & (padded_external["sex"] == sex)
        ].iloc[0]["central_rate"]
        assert got == expected
        # provenance honesty: ~0.000766 male / ~0.000451 female.
        assert 0.0003 < got < 0.001


def test__pad__exposure_rows_dated_at_t_star_survive_the_truncation():
    padded_external, padded_exposure = (
        factory._pad_below_25_projection_coverage(
            factory.nchs_2010_external_rates(),
            _fourteen_cell_exposure(),
            boundary_year=2014,
        )
    )
    pad = padded_exposure[padded_exposure["age_band"] == "0-24"]
    assert (pad["event_year"] == 2014).all()
    assert (pad["required_interview_year"] == 2014).all()
    assert (pad["start_weight"] == 1.0).all()
    assert (pad["exposure"] == 1.0).all()
    assert (pad["death"] == 0.0).all()
    prepared = prepare_mortality_refit_inputs(
        padded_exposure,
        padded_external,
        external_vintage_year=2010,
        boundary_year=2014,
    )
    assert (prepared.exposure["age_band"] == "0-24").sum() == 2


# --------------------------------------------------------------------------
# Step 4c -- pad identity (the two invented rows)
# --------------------------------------------------------------------------
def _fourteen_cell_exposure_with_ids() -> pd.DataFrame:
    """The same fourteen invented cells, keyed by invented person ids.

    Ids start at 1001 because the PSID key is ``ER30001 * 1000 + ER30002``;
    nothing here is an observed person.
    """
    frame = _fourteen_cell_exposure().copy()
    frame.insert(0, "person_id", np.arange(1001, 1001 + len(frame)))
    return frame[list(factory.MORTALITY_EXPOSURE_COLUMNS)]


def test__pad_ids__are_reserved_negative_and_one_per_sex():
    assert factory.PAD_PERSON_IDS == {"female": -1, "male": -2}
    assert set(factory.PAD_PERSON_IDS) == set(mf.SEXES)
    values = list(factory.PAD_PERSON_IDS.values())
    assert len(set(values)) == len(values)  # distinct
    assert all(value < 0 for value in values)  # reserved


def test__pad__gives_the_two_rows_reserved_ids_when_the_input_has_ids():
    _, padded = factory._pad_below_25_projection_coverage(
        factory.nchs_2010_external_rates(),
        _fourteen_cell_exposure_with_ids(),
        boundary_year=2014,
    )
    assert list(padded.columns) == list(factory.MORTALITY_EXPOSURE_COLUMNS)
    assert padded["person_id"].dtype.kind == "i"  # no NaN id
    pad = padded[padded["age_band"] == "0-24"]
    assert len(pad) == 2
    assert dict(zip(pad["sex"], pad["person_id"], strict=True)) == {
        "female": -1,
        "male": -2,
    }
    # disjoint from every observed row, and unique as a person-year.
    observed = padded[padded["age_band"] != "0-24"]["person_id"]
    assert not set(pad["person_id"]) & set(observed)
    assert not padded.duplicated(["person_id", "event_year"]).any()


def test__pad__adds_no_id_to_a_seven_column_input():
    # The pre-existing shape is preserved exactly: an input with no identity
    # gets pad rows with no identity.
    external = factory.nchs_2010_external_rates()
    exposure = _fourteen_cell_exposure()
    _, padded = factory._pad_below_25_projection_coverage(
        external, exposure, boundary_year=2014
    )
    assert list(padded.columns) == _MORTALITY_COLUMNS
    assert "person_id" not in padded.columns


def test__pad__refuses_an_input_whose_ids_are_not_the_documented_domain():
    # The non-collision argument is checked, not assumed: the PSID key
    # ER30001 * 1000 + ER30002 is non-negative, so a negative observed id
    # means the reserved sentinels are no longer disjoint.
    exposure = _fourteen_cell_exposure_with_ids()
    exposure.loc[0, "person_id"] = -1
    with pytest.raises(ValueError, match="negative person_id"):
        factory._pad_below_25_projection_coverage(
            factory.nchs_2010_external_rates(), exposure, boundary_year=2014
        )


@pytest.mark.parametrize(
    "malform",
    [
        pytest.param(lambda s: s.astype(bool), id="boolean"),
        pytest.param(lambda s: s.astype(str), id="numeric-string"),
        pytest.param(
            lambda s: s.astype("float64") + 0.5, id="fractional-float"
        ),
        pytest.param(lambda s: s.astype("complex128"), id="complex"),
    ],
)
def test__pad__refuses_a_non_integer_person_id_dtype(malform):
    # Only an actual integer dtype is accepted before the pad reserves
    # negative ids -- a coercion (`pd.to_numeric`) would let a digit string
    # or a whole-number float pass silently. Not reachable through the
    # adapter (which always emits int64); only a foreign caller hits this.
    exposure = _fourteen_cell_exposure_with_ids()
    exposure["person_id"] = malform(exposure["person_id"])
    with pytest.raises(ValueError, match="integer dtype"):
        factory._pad_below_25_projection_coverage(
            factory.nchs_2010_external_rates(),
            exposure,
            boundary_year=2014,
        )


def test__pad__refuses_a_missing_person_id_value():
    # A nullable-integer column can carry pd.NA without losing its integer
    # dtype; that must still be refused before the sign comparison runs.
    exposure = _fourteen_cell_exposure_with_ids()
    exposure["person_id"] = exposure["person_id"].astype("Int64")
    exposure.loc[0, "person_id"] = pd.NA
    with pytest.raises(ValueError, match="missing"):
        factory._pad_below_25_projection_coverage(
            factory.nchs_2010_external_rates(),
            exposure,
            boundary_year=2014,
        )


def test__pad__accepts_every_valid_int64_id_unchanged():
    # The dtype guard must not disturb a well-formed int64 id column -- every
    # observed id survives into the padded frame alongside the two reserved
    # pad ids. Fitted-probability invariance is covered separately by
    # test__identity__does_not_move_a_single_fitted_probability.
    exposure = _fourteen_cell_exposure_with_ids()
    _, padded = factory._pad_below_25_projection_coverage(
        factory.nchs_2010_external_rates(), exposure, boundary_year=2014
    )
    assert padded["person_id"].dtype.kind == "i"
    assert set(exposure["person_id"]) <= set(padded["person_id"])


def test__pad_disclosure__says_the_rows_are_invented_and_admit_nothing():
    text = factory.PAD_IDENTITY_DISCLOSURE
    assert "INVENTED" in text
    assert "no observed person identity" in text
    assert "-1 (female) and -2 (male)" in text
    assert "admits nothing" in text
    # and the module points a reader at it from the pad itself.
    source = (SCRIPTS / "registered_m6_inputs.py").read_text()
    assert source.count("PAD_IDENTITY_DISCLOSURE") >= 3


def test__identity__does_not_move_a_single_fitted_probability():
    # The load-bearing invariance: the fit reads five named columns, so the
    # retained key and the two reserved ids are inert. Same fourteen invented
    # cells, with and without identity, must fit byte-equal probabilities.
    external = factory.nchs_2010_external_rates()
    without = _fit(
        *factory._pad_below_25_projection_coverage(
            external, _fourteen_cell_exposure(), boundary_year=2014
        )
    )
    with_ids = _fit(
        *factory._pad_below_25_projection_coverage(
            external, _fourteen_cell_exposure_with_ids(), boundary_year=2014
        )
    )
    assert with_ids.bands == without.bands
    assert with_ids.probability == without.probability


def test__identity__does_not_move_the_prepared_row_count():
    external = factory.nchs_2010_external_rates()
    counts = []
    for exposure in (
        _fourteen_cell_exposure(),
        _fourteen_cell_exposure_with_ids(),
    ):
        padded_external, padded_exposure = (
            factory._pad_below_25_projection_coverage(
                external, exposure, boundary_year=2014
            )
        )
        counts.append(
            len(
                prepare_mortality_refit_inputs(
                    padded_exposure,
                    padded_external,
                    external_vintage_year=2010,
                    boundary_year=2014,
                ).exposure
            )
        )
    assert counts[0] == counts[1] == 16


def test__bridge__padded_factory_rates_fit_an_eight_band_0_120_model():
    padded_external, padded_exposure = (
        factory._pad_below_25_projection_coverage(
            factory.nchs_2010_external_rates(),
            _fourteen_cell_exposure(),
            boundary_year=2014,
        )
    )
    model = _fit(padded_external, padded_exposure)
    assert model.bands == (
        (0, 24),
        (25, 34),
        (35, 44),
        (45, 54),
        (55, 64),
        (65, 74),
        (75, 84),
        (85, 120),
    )
    # the pinned convention: no modeled mortality below the age-25 PSID
    # exposure floor.
    for sex in mf.SEXES:
        assert model.probability[("0-24", sex)] == 0.0
    # every 25+ cell carries the PSID rate exactly (aligned_rate =
    # psid_rate), untouched by the pad: -expm1(-(deaths/exposure)).
    for row in _fourteen_cell_exposure().itertuples(index=False):
        expected = float(-np.expm1(-(row.death / row.exposure)))
        assert model.probability[(row.age_band, row.sex)] == expected


def test__bridge__25_plus_cells_invariant_to_pad_value_and_weight():
    padded_external, padded_exposure = (
        factory._pad_below_25_projection_coverage(
            factory.nchs_2010_external_rates(),
            _fourteen_cell_exposure(),
            boundary_year=2014,
        )
    )
    base = _fit(padded_external, padded_exposure)
    perturbed_external = padded_external.copy()
    perturbed_exposure = padded_exposure.copy()
    perturbed_external.loc[
        perturbed_external["age_band"] == "0-24", "central_rate"
    ] = 0.5
    perturbed_exposure.loc[
        perturbed_exposure["age_band"] == "0-24", "start_weight"
    ] = 17.3
    perturbed = _fit(perturbed_external, perturbed_exposure)
    for (band, sex), probability in base.probability.items():
        if band == "0-24":
            assert perturbed.probability[(band, sex)] == 0.0
        else:
            assert perturbed.probability[(band, sex)] == probability


def test__pad__leaves_the_shared_seven_band_set_untouched():
    # The pad is appended after the seven-band construction; the
    # MORTALITY_BANDS == build_mortality_floors.BANDS guard still binds the
    # committed floors artifacts.
    from populace_dynamics.harness.m6_cells import MORTALITY_BANDS

    assert factory.PAD_BAND == (0, 24)
    assert factory.PAD_BAND not in tuple(MORTALITY_BANDS)
    assert tuple(MORTALITY_BANDS) == tuple(mf.BANDS)
    assert len(MORTALITY_BANDS) == 7


# --------------------------------------------------------------------------
# Declared vintages (leakage-safety of the hardcoded bindings)
# --------------------------------------------------------------------------
def test__declared_vintages__are_all_pre_boundary_and_admitted():
    assert factory.SSA_PARAMS_VINTAGE == 2014
    assert factory.MORTALITY_EXTERNAL_VINTAGE == 2010
    for name, vintage in (
        ("SSA earnings-index parameters", factory.SSA_PARAMS_VINTAGE),
        ("mortality reference", factory.MORTALITY_EXTERNAL_VINTAGE),
    ):
        validate_external_vintage(name, vintage, boundary_year=2014)


def test__factory__has_no_gates_yaml_dependency():
    # The build/test lane never scores or edits the pre-registration
    # contract; the factory has no gates.yaml read or write.
    source = (SCRIPTS / "registered_m6_inputs.py").read_text()
    assert "gates.yaml" not in source
