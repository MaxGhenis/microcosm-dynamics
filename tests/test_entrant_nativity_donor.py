"""Tests for the certified-frame nativity donor.

Most tests run on the synthetic frame and need no h5.  The reproduction pins
that read the certified artifact resolve it from the LOCAL Hugging Face cache
only and skip when it is absent, matching ``test_gate_w1_floors``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from populace_dynamics.data import nativity_frame as nfm


def _cached_certified_h5():
    """Resolve the pinned h5 from the LOCAL HF cache only (no network)."""
    pytest.importorskip("huggingface_hub")
    pytest.importorskip("tables")
    from huggingface_hub import hf_hub_download

    pin = nfm.CERTIFIED_PIN
    try:
        return hf_hub_download(
            repo_id=pin["hf_repo_id"],
            filename=pin["hf_filename"],
            repo_type=pin["hf_repo_type"],
            revision=pin["revision"],
            local_files_only=True,
        )
    except Exception:  # noqa: BLE001
        pytest.skip("certified populace h5 not in local HF cache")


# --------------------------------------------------------------------------
# Label tables (verified against the published Census sources)
# --------------------------------------------------------------------------
def test_prcitshp_labels_are_the_published_five():
    assert nfm.PRCITSHP_LABELS == {
        1: "Native, born in US",
        2: "Native, born in PR or US outlying area",
        3: "Native, born abroad of US parent(s)",
        4: "Foreign born, US cit by naturalization",
        5: "Foreign born, not a US citizen",
    }


def test_only_codes_4_and_5_are_foreign_born():
    """Codes 2 and 3 are NATIVE despite birth outside the fifty states.

    Counting them as foreign-born would inflate the margin by the
    PR/outlying-area and born-abroad-of-US-parents populations.
    """
    assert nfm.FOREIGN_BORN_CODES == (4, 5)
    assert set(nfm.NATIVE_CODES) | set(nfm.FOREIGN_BORN_CODES) == set(
        nfm.PRCITSHP_LABELS
    )
    assert not set(nfm.NATIVE_CODES) & set(nfm.FOREIGN_BORN_CODES)


def test_penatvty_united_states_and_outlying_area_codes():
    assert nfm.PENATVTY_UNITED_STATES == 57
    assert set(nfm.PENATVTY_OUTLYING_AREAS) == {60, 66, 69, 73, 78}


def test_arrival_bins_agree_below_the_top_code_across_vintages():
    for code in range(1, 27):
        bands = {
            vintage: table[code]
            for vintage, table in nfm.PEINUSYR_BINS_BY_VINTAGE.items()
        }
        assert len(set(bands.values())) == 1, (code, bands)


def test_the_top_code_differs_by_vintage():
    """This is the reason ``arrival_band`` is keyed on ``(vintage, code)``.

    Code 27 is 2020-2022 on the 2022 ASEC, 2020-2023 on the 2023 ASEC and
    2020-2021 on the 2024 ASEC, where the top code becomes 28 = 2022-2024.
    A single crosswalk over the pooled frame mislabels arrival years.
    """
    assert nfm.arrival_band(2022, 27) == (2020, 2022)
    assert nfm.arrival_band(2023, 27) == (2020, 2023)
    assert nfm.arrival_band(2024, 27) == (2020, 2021)
    assert nfm.arrival_band(2024, 28) == (2022, 2024)
    assert 28 not in nfm.PEINUSYR_BINS_BY_VINTAGE[2022]


def test_arrival_band_does_not_fall_back_to_another_vintage():
    assert nfm.arrival_band(2022, 28) is None
    assert nfm.arrival_band(2023, 28) is None


def test_arrival_band_is_none_out_of_universe():
    assert nfm.arrival_band(2024, nfm.PEINUSYR_NOT_IN_UNIVERSE) is None


def test_band_midpoint_rounds_up_and_agrees_with_microcosm():
    """Spot-checks against microcosm's committed ``_ARRIVAL_YEAR_MIDPOINTS``."""
    persons = pd.DataFrame(
        {
            "source_year": [2024, 2024, 2024, 2024],
            "peinusyr": [3, 7, 22, 28],
        }
    )
    out = nfm.attach_arrival_bands(persons)
    assert list(out["arrival_year"]) == [1962, 1981, 2011, 2023]


# --------------------------------------------------------------------------
# The populated guard
# --------------------------------------------------------------------------
def test_populated_guard_rejects_a_zeroed_column():
    frame = pd.DataFrame(
        {
            "PENATVTY": np.zeros(100, dtype=int),
            "PRCITSHP": np.ones(100, dtype=int),
            "PEINUSYR": np.ones(100, dtype=int),
        }
    )
    with pytest.raises(ValueError, match="PENATVTY non-zero fraction"):
        nfm.assert_nativity_columns_populated(frame)


def test_populated_guard_rejects_a_missing_column():
    frame = pd.DataFrame({"PRCITSHP": [1, 2, 3]})
    with pytest.raises(ValueError, match="missing column: PENATVTY"):
        nfm.assert_nativity_columns_populated(frame)


def test_no_nativity_column_is_guarded_by_deployment_frame():
    """The motivation for this module's own guard, pinned as a fact.

    ``deployment_frame.REQUIRED_SOURCE_COLUMNS`` protects the family-A gated
    inputs; nativity rides along unguarded, which is also why the nativity
    margin is not a calibration target of the certified file.
    """
    from populace_dynamics.data import deployment_frame as dfm

    assert not set(nfm.REQUIRED_NATIVITY_COLUMNS) & set(
        dfm.REQUIRED_SOURCE_COLUMNS
    )


# --------------------------------------------------------------------------
# Pure-function diagnostics on synthetic rows
# --------------------------------------------------------------------------
def test_synthetic_frame_satisfies_the_entry_year_identity():
    persons = nfm.synthetic_nativity_frame(seed=3)
    diagnostics = nfm.nativity_diagnostics(persons)
    assert diagnostics["entry_year_universe_identity"]["holds"] is True


def test_synthetic_frame_has_no_vintage_domain_mismatch():
    persons = nfm.synthetic_nativity_frame(seed=5)
    assert (
        nfm.vintage_domain_mismatch(persons)["rows_with_undefined_band"] == 0
    )


def test_diagnostics_share_is_the_weighted_share():
    persons = nfm.synthetic_nativity_frame(seed=7)
    diagnostics = nfm.nativity_diagnostics(persons)
    weight = persons["weight"].to_numpy()
    expected = weight[persons["foreign_born"].to_numpy()].sum() / weight.sum()
    assert diagnostics["foreign_born"]["share"] == pytest.approx(expected)


def test_diagnostics_states_the_uncalibrated_status():
    diagnostics = nfm.nativity_diagnostics(nfm.synthetic_nativity_frame())
    assert diagnostics["calibration_status"].startswith("UNCALIBRATED")


def test_donor_composition_shares_sum_to_one():
    persons = nfm.synthetic_nativity_frame(n=1200, seed=11)
    donor = nfm.recent_arrival_donor(persons, vintage=2024, codes=(28,))
    composition = nfm.donor_composition(donor)
    assert sum(
        cell["share"] for cell in composition.values()
    ) == pytest.approx(1.0)


def test_donor_refuses_a_band_undefined_for_its_vintage():
    persons = nfm.synthetic_nativity_frame(n=800, seed=13)
    with pytest.raises(ValueError, match="undefined for ASEC vintage 2022"):
        nfm.recent_arrival_donor(persons, vintage=2022, codes=(28,))


def test_donor_entry_age_subtracts_the_interview_lag():
    persons = nfm.synthetic_nativity_frame(n=900, seed=17)
    donor = nfm.recent_arrival_donor(persons, vintage=2024, codes=(28,))
    expected = np.maximum(
        donor["age"].to_numpy() - donor["arrival_lag_years"].to_numpy(), 0.0
    )
    assert np.allclose(donor["entry_age"].to_numpy(), expected)


def test_donor_provenance_labels_the_stock_proxy_and_the_binning():
    persons = nfm.synthetic_nativity_frame(n=900, seed=19)
    donor = nfm.recent_arrival_donor(persons, vintage=2024, codes=(28,))
    record = nfm.NativityDonor(
        pool=donor,
        composition=nfm.donor_composition(donor),
        vintage=2024,
        codes=(28,),
    ).provenance()
    assert record["stock_proxy_disclosure"].startswith("stock_proxy")
    assert record["arrival_windows"]["28"] == [2022, 2024]
    assert record["band_split_rule"] == nfm.BAND_SPLIT_RULE
    assert "ACS PUMS" in record["annual_resolution_disclosure"]


# --------------------------------------------------------------------------
# Reproduction against the certified frame
# --------------------------------------------------------------------------
def test_certified_frame_reproduces_the_measured_nativity_counts():
    persons, populated = nfm.load_nativity_persons(_cached_certified_h5())
    assert len(persons) == 166302
    assert populated["PENATVTY"] == pytest.approx(1.0)
    assert populated["PRCITSHP"] == pytest.approx(1.0)
    assert populated["PEINUSYR"] == pytest.approx(0.15615, abs=1e-5)

    diagnostics = nfm.nativity_diagnostics(persons)
    counts = {
        code: record["n_rows"]
        for code, record in diagnostics["prcitshp_counts"].items()
    }
    assert counts == {1: 140334, 2: 836, 3: 1400, 4: 10893, 5: 12839}
    identity = diagnostics["entry_year_universe_identity"]
    assert identity["holds"] is True
    assert identity["n_peinusyr_zero"] == 140334
    assert diagnostics["foreign_born"]["n_rows"] == 23732
    assert diagnostics["foreign_born"]["share"] == pytest.approx(
        0.179627, abs=1e-6
    )
    assert diagnostics["weighted_persons"] == pytest.approx(
        340_008_864, rel=1e-6
    )
    assert diagnostics["penatvty"]["n_distinct_codes"] == 161
    assert diagnostics["penatvty"]["n_united_states"] == 140320


def test_certified_frame_carries_the_measured_vintage_domain_mismatch():
    """795 rows labelled ASEC 2023 carry code 28, which that vintage's own
    published dictionary does not define.  Measured, surfaced, not repaired:
    repairing it would require asserting an arrival year the source does not
    support.
    """
    persons, _ = nfm.load_nativity_persons(_cached_certified_h5())
    mismatch = nfm.vintage_domain_mismatch(persons)
    assert mismatch["rows_in_universe"] == 25968
    assert mismatch["rows_with_undefined_band"] == 795
    assert mismatch["undefined_pairs"] == {"source_year=2023,peinusyr=28": 795}


def test_certified_donor_pool_is_the_2024_vintage_top_band():
    persons, _ = nfm.load_nativity_persons(_cached_certified_h5())
    donor = nfm.recent_arrival_donor(persons, vintage=2024, codes=(28,))
    assert len(donor) == 1155
    assert set(donor["arrival_lag_years"]) == {1}
    assert donor["weight"].sum() == pytest.approx(2_345_368, rel=1e-4)


def test_the_donor_excludes_natives_who_arrived_in_the_same_window():
    """PEINUSYR's universe is everyone not born in the fifty states.

    30 of the 1,185 rows in the 2024-vintage top band are natives born in
    PR/outlying areas or abroad of US parents.  They are genuine arrivals to
    the resident population but US citizens at birth, so they appear in
    neither of Table V.A2's stocks; sizing them against a V.A2 inflow would
    put people the control never counted into the cohort.
    """
    persons, _ = nfm.load_nativity_persons(_cached_certified_h5())
    restricted = nfm.recent_arrival_donor(persons, vintage=2024, codes=(28,))
    everyone = nfm.recent_arrival_donor(
        persons, vintage=2024, codes=(28,), foreign_born_only=False
    )
    assert len(everyone) - len(restricted) == 30
    assert restricted["foreign_born"].all()
    assert set(restricted["prcitshp"].unique()) <= set(nfm.FOREIGN_BORN_CODES)
    excluded = everyone.loc[~everyone["foreign_born"]]
    assert set(excluded["prcitshp"].unique()) == {2, 3}
