"""The adapter frame against the graph's declared training-source contract.

Fixture-only. Every person here is **invented**: the panel is fourteen
hand-written people over three waves, and the ``(0, 24)`` rows are the
projection-coverage pad, which names no person at all. The only committed
reference read is the NCHS 2010 band grid the registered factory already
binds. No PSID file is opened, no staged product is read, no registered gate
is run, and nothing here fits anything to a source. The point is narrow and
mechanical:

* the graph's training kernel accepts **exactly eight fields** and requires
  Python ``int`` identifiers and years (``graph/runtime.py`` ``_records`` and
  ``_integer_column``), so a frame that reaches it through numpy scalars is
  refused -- the serializing cast is what makes the bridge work;
* the graph's fit default for ``external_vintage_year`` is **2014** while the
  registered M6 binding is **2010**, so an artifact built on the default does
  not match the registered one. That is pinned here so it cannot be met by
  accident.

No accuracy, no calibration, no holdout and no mortality claim follows from
any of it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from populace_dynamics.graph.model import fit_mortality

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_mortality_floors as mf  # noqa: E402
import registered_m6_inputs as factory  # noqa: E402

#: The graph's training-source field set, written out so this module pins it
#: independently of the runtime import (which needs a Microcosm core).
TRAINING_FIELDS = frozenset(
    {
        "person_id",
        "event_year",
        "required_interview_year",
        "age_band",
        "sex",
        "start_weight",
        "exposure",
        "death",
    }
)

#: Columns the graph requires to be Python ``int``.
INTEGER_FIELDS = ("person_id", "event_year", "required_interview_year")


@pytest.fixture
def runtime():
    from populace_dynamics.graph._compat import require_graph

    try:
        require_graph()
    except ImportError as error:
        pytest.skip(str(error))
    from populace_dynamics.graph import runtime

    return runtime


#: Waves for the invented panel: annual would give one slice per interval,
#: biennial gives two, which is the shape the ``<= T*`` window ends on.
INVENTED_WAVES = (2009, 2011, 2013)


def _invented_panel():
    """Hand-written person-waves. No survey file is involved.

    Fourteen invented people, one per band x sex cell, because
    ``fit_mortality_model`` raises on a band x sex cell with no exposure.
    Ages start one year above each band floor and advance two years a wave,
    so nobody leaves the band they were assigned to. Ids start at 1001 to
    look like the PSID key shape (``ER30001 * 1000 + ER30002``); they name
    no PSID person.
    """
    people = []
    for index, (lower, _upper) in enumerate(mf.BANDS):
        for offset, sex in enumerate(("female", "male")):
            person_id = 1001 + 2 * index + offset
            # One death per band, alternating sex, inside the 2011 interval.
            death = 2012 if (index % 2 == offset) else None
            people.append((person_id, sex, lower + 1, death))

    rows = [
        {
            "person_id": person_id,
            "period": wave,
            "age": age + 2 * offset,
            "weight": 1.0 + 0.25 * index,
            "interview": 1,
        }
        for index, (person_id, _sex, age, _death) in enumerate(people)
        for offset, wave in enumerate(INVENTED_WAVES)
    ]
    demographic = pd.DataFrame(rows)
    deaths = pd.DataFrame(
        {
            "person_id": [person for person, _, _, _ in people],
            "sex": [sex for _, sex, _, _ in people],
            "death_year": pd.array(
                [
                    pd.NA if death is None else death
                    for _, _, _, death in people
                ],
                dtype="Int64",
            ),
        }
    )
    return demographic, deaths


def training_records(exposure: pd.DataFrame) -> list[dict]:
    """Serialize an exposure frame into the graph's training records.

    The only work is a cast: the graph checks ``type(value) is int``, which
    a numpy scalar fails. Nothing is renamed, dropped, added or rounded.
    """
    records = exposure[list(factory.MORTALITY_EXPOSURE_COLUMNS)].to_dict(
        orient="records"
    )
    for record in records:
        for field in INTEGER_FIELDS:
            record[field] = int(record[field])
        for field in ("start_weight", "exposure", "death"):
            record[field] = float(record[field])
        record["age_band"] = str(record["age_band"])
        record["sex"] = str(record["sex"])
    return records


def _padded_invented_inputs():
    demographic, deaths = _invented_panel()
    # The committed NCHS 2010 band grid -- the same reference the registered
    # factory binds. Only the panel is invented.
    return factory._pad_below_25_projection_coverage(
        factory.nchs_2010_external_rates(),
        factory.mortality_exposure_adapter(demographic, deaths),
        boundary_year=2014,
    )


# --------------------------------------------------------------------------
# The eight-field shape and its integer identifiers
# --------------------------------------------------------------------------
def test__records__carry_exactly_the_eight_declared_fields():
    _, exposure = _padded_invented_inputs()
    records = training_records(exposure)
    assert records
    assert all(set(record) == TRAINING_FIELDS for record in records)
    assert set(factory.MORTALITY_EXPOSURE_COLUMNS) == TRAINING_FIELDS


def test__records__use_python_ints_not_numpy_scalars():
    _, exposure = _padded_invented_inputs()
    for record in training_records(exposure):
        for field in INTEGER_FIELDS:
            assert type(record[field]) is int
    # And the cast is not decorative: a numpy scalar is a different type,
    # which is exactly what the graph's identifier check rejects.
    assert type(np.int64(2011)) is not int


def test__records__include_the_two_invented_pad_identities():
    _, exposure = _padded_invented_inputs()
    pad = [r for r in training_records(exposure) if r["age_band"] == "0-24"]
    assert {r["person_id"] for r in pad} == {-1, -2}
    assert all(r["death"] == 0.0 for r in pad)
    # Stated once more where a reader of the serialized rows will meet it.
    assert "INVENTED" in factory.PAD_IDENTITY_DISCLOSURE


def test__records__are_json_serializable_without_a_custom_encoder():
    _, exposure = _padded_invented_inputs()
    round_tripped = json.loads(json.dumps(training_records(exposure)))
    assert round_tripped == training_records(exposure)


def test__records__have_no_repeated_person_year():
    _, exposure = _padded_invented_inputs()
    keys = [
        (r["person_id"], r["event_year"]) for r in training_records(exposure)
    ]
    assert len(set(keys)) == len(keys)


# --------------------------------------------------------------------------
# The graph's own training kernel, run on the invented records
# --------------------------------------------------------------------------
def _write(tmp_path, records):
    path = tmp_path / "training.json"
    path.write_text(json.dumps(records))
    return SimpleNamespace(sources={"training": path})


def test__graph_training_kernel__accepts_the_serialized_records(
    runtime, tmp_path
):
    _, exposure = _padded_invented_inputs()
    records = training_records(exposure)
    result = runtime._create_training(_write(tmp_path, records))
    assert result.frame is not None
    # The kernel's declared field list is the eight this module pins.
    declared = {
        "person_id",
        "event_year",
        "start_weight",
        *dict(runtime.TRAIN_COLUMNS),
    }
    assert declared == TRAINING_FIELDS


def test__graph_training_kernel__refuses_numpy_identifiers(runtime, tmp_path):
    _, exposure = _padded_invented_inputs()
    records = training_records(exposure)
    # A record whose id survived as a numpy scalar: json.dumps would fail, so
    # feed the kernel the parsed shape it would see from a float-typed id.
    records[0]["person_id"] = float(records[0]["person_id"])
    with pytest.raises(ValueError, match="integer identifiers/years"):
        runtime._create_training(_write(tmp_path, records))


def test__graph_training_kernel__refuses_a_repeated_person_year(
    runtime, tmp_path
):
    _, exposure = _padded_invented_inputs()
    records = training_records(exposure)
    records.append(dict(records[0]))
    with pytest.raises(ValueError, match="repeats a person-period"):
        runtime._create_training(_write(tmp_path, records))


def test__graph_training_kernel__refuses_a_ninth_field(runtime, tmp_path):
    _, exposure = _padded_invented_inputs()
    records = training_records(exposure)
    for record in records:
        record["start_wave"] = record["event_year"]
    with pytest.raises(ValueError, match="unsupported fields"):
        runtime._create_training(_write(tmp_path, records))


# --------------------------------------------------------------------------
# F7 -- the external vintage the registered M6 binding declares
# --------------------------------------------------------------------------
def test__external_vintage__graph_default_is_not_the_registered_binding():
    from populace_dynamics.graph import __main__ as cli

    assert factory.MORTALITY_EXTERNAL_VINTAGE == 2010
    default = cli.parser().parse_args(
        ["--output-dir", "unused", "--synthetic"]
    )
    assert default.external_vintage_year == 2014
    assert default.external_vintage_year != factory.MORTALITY_EXTERNAL_VINTAGE


def test__external_vintage__2010_is_what_matches_the_m6_binding():
    external, exposure = _padded_invented_inputs()
    registered = fit_mortality(
        exposure,
        external,
        boundary_year=2014,
        external_vintage_year=factory.MORTALITY_EXTERNAL_VINTAGE,
    )
    on_the_default = fit_mortality(
        exposure, external, boundary_year=2014, external_vintage_year=2014
    )
    assert registered.external_vintage_year == 2010
    # Same fitted probabilities, different artifact: the vintage is carried
    # in the payload, so the default alone breaks byte identity.
    assert registered.probabilities == on_the_default.probabilities
    assert registered.to_bytes() != on_the_default.to_bytes()
    assert registered.fit_rows == len(exposure)


def test__external_vintage__is_not_read_from_the_rates_frame():
    # The rates frame carries no vintage column; the scalar is the only
    # place the vintage is declared, which is why passing it matters.
    external, _ = _padded_invented_inputs()
    assert "vintage_year" not in external.columns
    assert "external_vintage_year" not in external.columns
