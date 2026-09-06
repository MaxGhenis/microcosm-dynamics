"""Reproduction and fail-closed pins for the Trustees V.A2 control reader.

The snapshot is a hash-pinned browser capture of
``https://www.ssa.gov/oact/TR/2026/lr5a2.html`` (ssa.gov answers HTTP 403 to
curl from this environment).  These tests read only committed bytes and need
no network.
"""

from __future__ import annotations

import hashlib
import shutil

import pytest

from populace_dynamics.data import trustees_immigration as tim


# --------------------------------------------------------------------------
# The pinned source
# --------------------------------------------------------------------------
def test_snapshot_matches_its_manifest_and_the_module_pin():
    entry = tim.read_manifest()
    assert entry["filename"] == tim.SNAPSHOT_FILENAME
    raw = tim.load_snapshot()
    assert hashlib.sha256(raw).hexdigest() == tim.SNAPSHOT_SHA256
    assert len(raw) == entry["size_bytes"] == 326209


def test_manifest_is_one_line_with_one_trailing_newline():
    path = tim.SNAPSHOT_DIR / tim.MANIFEST_FILENAME
    text = path.read_bytes().decode("utf-8")
    assert text.endswith("\n") and not text.endswith("\n\n")
    assert len(text.splitlines()) == 1


def test_a_mutated_snapshot_fails_closed(tmp_path):
    for name in (tim.SNAPSHOT_FILENAME, tim.MANIFEST_FILENAME):
        shutil.copy(tim.SNAPSHOT_DIR / name, tmp_path / name)
    target = tmp_path / tim.SNAPSHOT_FILENAME
    target.write_bytes(target.read_bytes().replace(b"600", b"601", 1))
    with pytest.raises(ValueError, match="snapshot sha256"):
        tim.load_snapshot(tmp_path)


def test_a_mutated_manifest_fails_closed(tmp_path):
    for name in (tim.SNAPSHOT_FILENAME, tim.MANIFEST_FILENAME):
        shutil.copy(tim.SNAPSHOT_DIR / name, tmp_path / name)
    manifest = tmp_path / tim.MANIFEST_FILENAME
    manifest.write_text(
        manifest.read_text().replace("326209", "326210"), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="capture manifest sha256"):
        tim.load_snapshot(tmp_path)


# --------------------------------------------------------------------------
# The parsed table
# --------------------------------------------------------------------------
def test_all_four_scenarios_parse_with_their_published_spans():
    scenarios = tim.parse_table(tim.load_snapshot())
    assert set(scenarios) == {
        "historical",
        "intermediate",
        "low_cost",
        "high_cost",
    }
    assert scenarios["historical"][0].year == 1940
    assert scenarios["historical"][-1].year == 2025
    for projected in ("intermediate", "low_cost", "high_cost"):
        rows = scenarios[projected]
        assert rows[0].year == 2026
        assert rows[-1].year == 2100
        assert len(rows) == 75


def test_the_unclosed_year_cell_is_recovered():
    """The page leaves the calendar-year <td> unclosed on every data row.

    The repo's existing ``_AllTablesParser`` raises "nested table cell" on
    that markup; a parser that silently restarts the cell would drop the year
    and silently mis-key every row.  This pins that the year survives.
    """
    raw = tim.load_snapshot()
    assert b'border:none;">2026  <td' in raw
    intermediate = tim.parse_table(raw)["intermediate"]
    assert [record.year for record in intermediate[:3]] == [2026, 2027, 2028]


def test_2026_intermediate_matches_the_published_cells():
    """Independent verification of the figures PR #218 section 2.4 reports.

    The capability memo could only quote these from #218 because ssa.gov 403s
    from the CLI.  They are now read from the source bytes.
    """
    record = tim.load_control("intermediate").by_year()[2026]
    assert record.lpr_inflow == 600.0
    assert record.lpr_outflow == 263.0
    assert record.lpr_adjustment_of_status == 450.0
    assert record.lpr_net_change == 788.0
    assert record.other_inflow == 740.0
    assert record.other_outflow == 947.0
    assert record.other_adjustment_of_status == 450.0
    assert record.other_net_change == -657.0
    assert record.total_net_change == 130.0
    assert record.positive_inflow == 1340.0


def test_every_row_satisfies_the_published_accounting_identities():
    """``parse_table`` raises on violation, so reaching here is the check."""
    scenarios = tim.parse_table(tim.load_snapshot())
    checked = sum(len(rows) for rows in scenarios.values())
    assert checked == 311


def test_adjustment_of_status_is_a_transfer_not_a_new_person():
    for record in tim.load_control("intermediate").rows:
        if record.lpr_adjustment_of_status is None:
            continue
        assert (
            record.lpr_adjustment_of_status
            == record.other_adjustment_of_status
        )


# --------------------------------------------------------------------------
# The entry-seam contract
# --------------------------------------------------------------------------
def test_positive_inflow_is_gross_and_excludes_outflow_and_adjustment():
    record = tim.load_control("intermediate").by_year()[2026]
    assert record.positive_inflow == record.lpr_inflow + record.other_inflow
    # Emphatically NOT the net change, which is an order of magnitude smaller.
    assert record.positive_inflow != record.total_net_change


def test_entry_only_minus_net_gap_is_published_and_large():
    """The structural gap an entry-only module cannot close."""
    record = tim.load_control("intermediate").by_year()[2026]
    assert record.entry_only_minus_net_gap == 1340.0 - 130.0
    assert record.entry_only_minus_net_gap > 0


def test_positive_inflow_raises_outside_the_published_years():
    control = tim.load_control("intermediate")
    with pytest.raises(KeyError, match="does not cover year"):
        control.positive_inflow([2025])


def test_unknown_scenario_is_rejected():
    with pytest.raises(ValueError, match="unknown V.A2 scenario"):
        tim.load_control("central")


def test_provenance_states_both_unbridged_limits():
    provenance = tim.load_control("intermediate").provenance()
    assert provenance["table_id"] == "V.A2"
    assert provenance["universe"] == "social_security_area"
    assert "ssa_area_proxy" in provenance["universe_bridge_status"]
    assert "emigration" in provenance["net_alignment_status"]
    assert provenance["network_access"].startswith("none")
