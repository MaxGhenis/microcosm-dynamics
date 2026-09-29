"""The registered U2 loader's stages 2 and 3 on an invented staged
directory (section 14; review finding 6 of the u2m2 review).

INVENTED DATA - NOT A COMPARISON.  At the adjudicated registries the
loader refuses in stage 1, before any PSID file is opened
(``test_u2_mappings.py``).  To execute the rest of it before any real
record is read, this module stages the invented population as PSID-shaped
fixed-width files -- one family file and setup per support wave, written
at the registry layouts, and an individual file and setup -- in a
temporary directory and runs :func:`loader.load_u2_inputs` against it
with four patches, each named where it is applied:

* ``sources.blockers`` returns no blocker, so stage 1 and the registry
  gate pass (the registry's own routes, not the declared ones, are
  applied);
* ``loader.check_source_hashes`` returns nothing, because the registries
  cite the real PSID setup files and codebooks, which are not staged
  here (the rehash itself is tested in ``test_u2_mappings.py``);
* the inherited marriage-history and earnings readers return the
  invented frames.

An audit hook refuses any open under the PSID directory -- the default
one and the one under the account's real home, which differ when HOME is
overridden -- for the duration of each load.  Everything else -- path
resolution, the setup cross-checks, the fixed-width reads, the file
hashes and the seal -- is the code a registered run executes.
"""

from __future__ import annotations

import copy
import hashlib
import os
import pwd
import sys
from pathlib import Path
from types import MappingProxyType

import numpy as np
import pandas as pd
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from populace_dynamics.data import family, marriage, psid
from populace_dynamics.estimates import adjusted_poverty as ap
from populace_dynamics.uniform_cut_track_u2 import (
    cohort,
    invented,
    loader,
    parameters,
    rows,
    runner,
    sources,
)

POINTER = (
    "https://github.com/PolicyEngine/microcosm-dynamics/issues/42"
    "#issuecomment-1"
)
_NA_BIRTH_YEAR = 9999
_SEX_CODES = {"male": 1, "female": 2, "na": 9}

_GUARD = {"active": False, "opened": []}
#: The default PSID directory, and the same directory under the
#: account's real home (``~`` expands to an overridden HOME).
_PSID_ROOTS = (
    str(psid._DEFAULT_DATA_DIR),
    str(
        Path(pwd.getpwuid(os.getuid()).pw_dir)
        / psid._DEFAULT_DATA_DIR.relative_to(Path.home())
    ),
)


def _psid_guard(event, args):
    if not _GUARD["active"] or event not in (
        "open",
        "os.listdir",
        "os.scandir",
    ):
        return
    if not args or isinstance(args[0], int):
        return
    path = os.fsdecode(args[0])
    if path.startswith(_PSID_ROOTS):
        _GUARD["opened"].append(path)
        raise PermissionError(f"the test refuses a PSID read: {path}")


sys.addaudithook(_psid_guard)


def _setup(specs) -> str:
    """An invented SPSS setup whose DATA LIST holds ``specs``."""

    lines = "\n".join(
        f"   {spec.variable} {spec.start} - {spec.end}"
        for spec in sorted(specs, key=lambda spec: spec.start)
    )
    return f"DATA LIST FILE = INVENTED /\n{lines}\n.\n"


def _individual_lines(inputs: cohort.U2Inputs, specs) -> list[str]:
    """One invented individual-file record per person at the registry
    layouts (weights rounded to the documented whole-number field)."""

    values: dict[str, pd.Series] = {}
    person = inputs.persons.set_index("person_id")
    ids = person.index.to_numpy(dtype=np.int64)
    values["common.person_family_id"] = pd.Series(ids // 1000, index=ids)
    values["common.person_number"] = pd.Series(ids % 1000, index=ids)
    values["common.sex"] = person["sex"].map(_SEX_CODES)
    design = inputs.design.set_index("person_id")
    values["common.stratum"] = design["stratum"]
    values["common.cluster"] = design["cluster"]
    for wave, anchor in inputs.anchors.items():
        frame = anchor.set_index("person_id")
        for concept in loader.ANCHOR_CONCEPTS:
            column = frame[concept]
            if concept == "reported_birth_year":
                column = column.fillna(_NA_BIRTH_YEAR).astype("int64")
            elif concept == "weight":
                column = column.round().astype("int64")
            values[f"{wave}.{concept}"] = column
    width = max(spec.end for spec in specs)
    out = []
    for pid in ids:
        chars = [" "] * width
        for spec in specs:
            text = str(int(values[spec.concept].loc[pid]))
            assert len(text) <= spec.width, (spec.concept, text)
            chars[spec.start - 1 : spec.end] = list(text.rjust(spec.width))
        out.append("".join(chars))
    return out


def _stage(root, inputs: cohort.U2Inputs, registries) -> set[str]:
    """Write the invented PSID-shaped files under ``root``."""

    staged = set()
    declared = sources.SourceGate(sources.INVENTED_DECLARED, registries)
    for wave in sources.SUPPORT_WAVES:
        records = invented.invented_fixed_width_records(inputs, wave, declared)
        directory = root / "family" / str(wave)
        directory.mkdir(parents=True)
        (directory / f"FAM{wave}ER.sps").write_text(_setup(records["specs"]))
        (directory / f"FAM{wave}ER.txt").write_text(
            "\n".join(records["lines"]) + "\n", encoding="ascii"
        )
        staged |= {f"family/{wave}/FAM{wave}ER.sps"}
        staged |= {f"family/{wave}/FAM{wave}ER.txt"}
    specs = loader.individual_specs(registries)
    directory = root / "ind2023er"
    directory.mkdir()
    (directory / "IND2023ER.sps").write_text(_setup(specs))
    (directory / "IND2023ER.txt").write_text(
        "\n".join(_individual_lines(inputs, specs)) + "\n", encoding="ascii"
    )
    staged |= {"ind2023er/IND2023ER.sps", "ind2023er/IND2023ER.txt"}
    return staged


def _load(
    root,
    inputs: cohort.U2Inputs,
    *,
    evidence=None,
    history: pd.DataFrame | None = None,
) -> cohort.U2Inputs:
    """Run the real loader on ``root`` with the four named patches
    (``evidence`` is passed through; ``history`` replaces the invented
    marriage history the patched reader returns)."""

    history = inputs.marriage_history if history is None else history

    # The committed role rules are cached on first use; compute them
    # before ``blockers`` is patched so the cache holds the real rules.
    sources.RoleContext.from_registry()
    patch = pytest.MonkeyPatch()
    try:
        patch.setattr(sources, "blockers", lambda entry, name: [])
        patch.setattr(
            loader, "check_source_hashes", lambda registries, data_dir: {}
        )
        patch.setattr(
            marriage,
            "marriage_history",
            lambda *, data_dir=None, nrows=None: history,
        )
        patch.setattr(
            family,
            "family_earnings_panel",
            lambda *, waves=None, data_dir=None: inputs.observed_earnings,
        )
        _GUARD["active"], _GUARD["opened"] = True, []
        if evidence is None:
            return loader.load_u2_inputs(data_dir=root)
        return loader.load_u2_inputs(data_dir=root, evidence=evidence)
    finally:
        _GUARD["active"] = False
        patch.undo()


@pytest.fixture(scope="module")
def loaded(tmp_path_factory, u2_inputs, committed_registries):
    """The invented staged directory read by the real loader."""

    root = tmp_path_factory.mktemp("invented-psid")
    staged = _stage(root, u2_inputs, committed_registries)
    inputs = _load(root, u2_inputs)
    return {"inputs": inputs, "root": root, "staged": staged}


def test_stage_three_reads_and_hashes_exactly_the_staged_files(loaded):
    inputs = loaded["inputs"]
    assert _GUARD["opened"] == []
    recorded = dict(inputs.provenance["psid_files_sha256"])
    assert set(recorded) == loaded["staged"]
    import hashlib

    for relative, digest in recorded.items():
        raw = (loaded["root"] / relative).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
    assert inputs.provenance["kind"] == cohort.PSID_FILES
    assert inputs.provenance["psid_data_dir"] == str(loaded["root"])
    assert inputs.provenance["registries"]["kind"] == "committed"


def test_stage_three_seals_the_frames(loaded):
    inputs = loaded["inputs"]
    assert inputs.loader_seal["input_frames_sha256"] == (
        cohort.input_frames_sha256(inputs)
    )
    provenance = cohort._input_provenance(inputs)
    assert provenance["kind"] == cohort.PSID_FILES
    assert provenance["psid_files_sha256"] == dict(
        inputs.provenance["psid_files_sha256"]
    )
    assert inputs.invented_seal is None


def test_stage_three_frames_equal_the_invented_population(loaded, u2_inputs):
    inputs = loaded["inputs"]
    for wave in sources.SUPPORT_WAVES:
        expected = u2_inputs.anchors[wave].assign(
            weight=u2_inputs.anchors[wave]["weight"].round()
        )
        pd.testing.assert_frame_equal(
            inputs.anchors[wave].reset_index(drop=True),
            expected.reset_index(drop=True),
        )
        pd.testing.assert_frame_equal(
            inputs.family_income[wave].reset_index(drop=True),
            u2_inputs.family_income[wave].reset_index(drop=True),
        )
        pd.testing.assert_frame_equal(
            inputs.family_wealth[wave].reset_index(drop=True),
            u2_inputs.family_wealth[wave].reset_index(drop=True),
        )
    pd.testing.assert_frame_equal(
        inputs.persons.reset_index(drop=True),
        u2_inputs.persons.reset_index(drop=True),
    )
    pd.testing.assert_frame_equal(
        inputs.design.reset_index(drop=True),
        u2_inputs.design.reset_index(drop=True),
    )


def test_stage_three_applies_the_registry_dc_route(
    loaded, u2_inputs, committed_registries
):
    """The loader's DC balances are the registry route's (never the
    declared route's) on the same invented items."""

    inputs = loaded["inputs"]
    patch = pytest.MonkeyPatch()
    try:
        patch.setattr(sources, "blockers", lambda entry, name: [])
        gate = sources.SourceGate(sources.REGISTRY, committed_registries)
        for wave in sources.SUPPORT_WAVES:
            route = sources.dc_route(wave, gate)
            assert route.source == "pension_registry_routes"
            raw = invented.raw_family_frame(u2_inputs, wave)
            items = raw[
                ["interview"]
                + [
                    spec.concept
                    for spec in sources.pension_field_specs(wave, gate)
                ]
            ]
            widths = {
                spec.concept: spec.width
                for spec in sources.pension_field_specs(wave, gate)
                if spec.concept.endswith("_amount")
            }
            expected = sources.employer_dc_balances(items, route, widths)
            pd.testing.assert_frame_equal(
                inputs.employer_dc[wave].reset_index(drop=True),
                expected.reset_index(drop=True),
            )
    finally:
        patch.undo()


def test_loaded_inputs_take_the_registered_path_only(
    loaded, frozen_load, evidence, declared
):
    """Sealed psid_files inputs: the registered guard accepts them only
    once the loader rechecked them against the frozen pre-registration
    evidence (review round 1, finding 2) and they match the record the
    registration binds (review round 3); the declared role context
    refuses them, and the committed roles registry refuses the build on
    the refused codes (2015 code 20 among them)."""

    inputs = loaded["inputs"]
    registry = sources.RoleContext.from_registry()
    with pytest.raises(runner.U2RunError, match="frozen pre-registration"):
        runner.check_inputs(inputs, ap.REGISTERED_REAL, POINTER, registry)
    rechecked = frozen_load["inputs"]
    assert runner.check_inputs(
        rechecked,
        ap.REGISTERED_REAL,
        POINTER,
        registry,
        preregistration_evidence_sha256=frozen_load["sha256"],
        preregistration_evidence=evidence,
    ) == {
        cohort.EVIDENCE_KEY: frozen_load["sha256"],
        "input_frames_sha256": evidence["input_frames_sha256"],
    }
    with pytest.raises(runner.U2RunError, match="invented"):
        runner.check_inputs(inputs, ap.INVENTED, None, registry)
    with pytest.raises(cohort.U2CohortError, match="invented inputs"):
        cohort.build_u2_cohort(inputs, role_context=declared)
    with pytest.raises(sources.U2RoleRefusal):
        cohort.build_u2_cohort(inputs, role_context=registry)


def test_a_changed_frame_breaks_the_seal(loaded):
    import dataclasses

    inputs = loaded["inputs"]
    changed = dataclasses.replace(
        inputs, anchors={**inputs.anchors, 2019: inputs.anchors[2019].copy()}
    )
    assert changed.loader_seal is None
    with pytest.raises(cohort.U2CohortError, match="U2 loader"):
        cohort._input_provenance(changed)


def test_the_individual_setup_is_cross_checked(tmp_path, committed_registries):
    specs = loader.individual_specs(committed_registries)
    good = tmp_path / "good.sps"
    good.write_text(_setup(specs))
    assert loader.check_layouts_against_setup(specs, good) == len(specs)
    moved = [spec if spec.concept != "2019.weight" else None for spec in specs]
    shifted = next(s for s in specs if s.concept == "2019.weight")
    bad = tmp_path / "bad.sps"
    bad.write_text(
        _setup([s for s in moved if s is not None]).replace(
            "\n.\n",
            f"\n   {shifted.variable} {shifted.start + 1} - "
            f"{shifted.end + 1}\n.\n",
        )
    )
    with pytest.raises(loader.U2LoaderRefusal, match="differ"):
        loader.check_layouts_against_setup(specs, bad)


def test_individual_and_weight_registries_must_agree(committed_registries):
    import copy

    documents = copy.deepcopy(dict(committed_registries.documents))
    for entry in documents["weights"]["entries"]:
        if entry["id"] == "2019.cross_section_weight":
            entry["variable"] = "ER00000"
    invented_set = sources.RegistrySet(
        documents, dict(committed_registries.sha256), "invented"
    )
    with pytest.raises(loader.U2LoaderRefusal, match="weights registry"):
        loader.individual_specs(invented_set)


def test_a_moved_individual_column_refuses_the_load(
    tmp_path, u2_inputs, committed_registries
):
    """Review 2, finding 5: the individual file's staged setup must agree
    with the registry layouts before it is read; a setup that moves one
    column refuses the load."""

    _stage(tmp_path, u2_inputs, committed_registries)
    setup = tmp_path / "ind2023er" / "IND2023ER.sps"
    specs = loader.individual_specs(committed_registries)
    weight = next(spec for spec in specs if spec.concept == "2019.weight")
    text = setup.read_text()
    old = f"   {weight.variable} {weight.start} - {weight.end}\n"
    assert text.count(old) == 1
    setup.write_text(
        text.replace(
            old,
            f"   {weight.variable} {weight.start + 1} - {weight.end + 1}\n",
        )
    )
    with pytest.raises(loader.U2LoaderRefusal, match="differ"):
        _load(tmp_path, u2_inputs)
    assert _GUARD["opened"] == []


@pytest.mark.parametrize(
    "staged_file, message",
    [
        ("ind2023er/IND2023ER.txt", "duplicate person_id"),
        ("family/2019/FAM2019ER.txt", "duplicate interview"),
    ],
)
def test_a_repeated_record_refuses_the_load(
    tmp_path, u2_inputs, committed_registries, staged_file, message
):
    """Section 14: duplicate identifiers refuse execution.  A staged file
    that repeats its first record (the individual file's person, a
    family file's interview) refuses the load."""

    _stage(tmp_path, u2_inputs, committed_registries)
    path = tmp_path / staged_file
    lines = path.read_text(encoding="ascii").splitlines()
    path.write_text("\n".join([*lines, lines[0]]) + "\n", encoding="ascii")
    with pytest.raises(
        (loader.U2LoaderRefusal, sources.U2SourceRefusal), match=message
    ):
        _load(tmp_path, u2_inputs)
    assert _GUARD["opened"] == []


# ---------------------------------------------------------------------------
# Review round 1, finding 1: individual-file values against the registry's
# documented codes.  Each case rewrites one field of one staged record.
# ---------------------------------------------------------------------------
def _rewrite_individual_field(root, registries, person_id, key, text):
    """Put ``text`` (right-justified) in field ``key`` of ``person_id``'s
    staged individual record; return the field's previous text."""

    specs = {
        spec.concept: spec for spec in loader.individual_specs(registries)
    }
    family, number = (
        specs["common.person_family_id"],
        specs["common.person_number"],
    )
    target = specs[key]
    path = root / "ind2023er" / "IND2023ER.txt"
    lines = path.read_text(encoding="ascii").splitlines()
    for index, line in enumerate(lines):
        pid = int(line[family.start - 1 : family.end]) * 1000 + int(
            line[number.start - 1 : number.end]
        )
        if pid != person_id:
            continue
        assert len(text) <= target.width, (key, text)
        old = line[target.start - 1 : target.end]
        lines[index] = (
            line[: target.start - 1]
            + text.rjust(target.width)
            + line[target.end :]
        )
        path.write_text("\n".join(lines) + "\n", encoding="ascii")
        return old.strip()
    raise AssertionError(f"no staged record for {person_id}")


#: ``(key, person, documented staged value, undocumented replacement)``.
#: The first two are the round-1 review's minimal cases: single head
#: 700031's sex 2 -> 5 (accepted and set to "na" before the fix, dropping
#: an observation), and 700142 -- the 2015 legal spouse (code 90) of U0
#: head 700141 -- relationship 90 -> 99 (99 is undocumented in every
#: wave; before the fix the head silently lost the legal-spouse pairing).
UNDOCUMENTED_CASES = [
    ("common.sex", 700031, "2", "5"),
    ("2015.relationship", 700142, "90", "99"),
    ("2013.relationship", 700142, None, "92"),
    ("2019.sequence", 700142, None, "30"),
    ("common.stratum", 700142, None, "95"),
    ("common.cluster", 700142, None, "3"),
    ("2021.age", 700142, None, "126"),
    ("2017.reported_birth_year", 700142, None, "2018"),
    ("2023.interview", 700142, None, "-1"),
    ("2019.weight", 700142, None, "-1"),
    ("common.person_number", 700142, None, "0"),
    ("2015.relationship", 700142, None, ""),
]


@pytest.mark.parametrize(
    "key, person, before, value",
    UNDOCUMENTED_CASES,
    ids=[f"{case[0]}={case[3] or 'blank'}" for case in UNDOCUMENTED_CASES],
)
def test_an_undocumented_individual_value_refuses_the_load(
    tmp_path, u2_inputs, committed_registries, key, person, before, value
):
    """Section 14 ("refuse, never fall back"): one undocumented value in
    one staged individual record refuses the whole load with the named
    :class:`loader.U2UndocumentedValue`, as the family-file parse refuses
    out-of-domain values."""

    _stage(tmp_path, u2_inputs, committed_registries)
    old = _rewrite_individual_field(
        tmp_path, committed_registries, person, key, value
    )
    if before is not None:
        assert old == before
    with pytest.raises(loader.U2LoaderRefusal) as refusal:
        _load(tmp_path, u2_inputs)
    assert type(refusal.value).__name__ == "U2UndocumentedValue"
    assert f"individual:{key}" in str(refusal.value)
    assert _GUARD["opened"] == []


def test_the_undocumented_value_message_prints_codes_never_identifiers(
    tmp_path, u2_inputs, committed_registries
):
    _stage(tmp_path, u2_inputs, committed_registries)
    _rewrite_individual_field(
        tmp_path, committed_registries, 700031, "common.sex", "5"
    )
    with pytest.raises(loader.U2LoaderRefusal, match=r"codes \[5\]"):
        _load(tmp_path, u2_inputs)
    _stage(tmp_path / "ids", u2_inputs, committed_registries)
    _rewrite_individual_field(
        tmp_path / "ids", committed_registries, 700142, "2021.age", "126"
    )
    with pytest.raises(loader.U2LoaderRefusal) as refusal:
        _load(tmp_path / "ids", u2_inputs)
    assert "126" not in str(refusal.value)
    assert "700142" not in str(refusal.value)


@pytest.mark.parametrize(
    "key, person, value",
    [
        ("common.sex", 700031, "9"),
        ("2015.relationship", 700142, "98"),
        ("2021.age", 700142, "999"),
        ("2017.reported_birth_year", 700142, "9999"),
    ],
)
def test_a_documented_value_still_loads(
    tmp_path, u2_inputs, committed_registries, key, person, value
):
    """The check refuses only undocumented values: a documented code
    (sex 9 NA, relationship 98, age 999, year born 9999) still loads, and
    sex 9 is the only code read as "na"."""

    _stage(tmp_path, u2_inputs, committed_registries)
    _rewrite_individual_field(
        tmp_path, committed_registries, person, key, value
    )
    inputs = _load(tmp_path, u2_inputs)
    if key == "common.sex":
        sex = inputs.persons.set_index("person_id")["sex"]
        assert sex.loc[person] == "na"
        assert set(sex) <= {"male", "female", "na"}


def _raw_individual(inputs, registries) -> pd.DataFrame:
    """The invented population as the individual reader's raw columns."""

    specs = loader.individual_specs(registries)
    lines = _individual_lines(inputs, specs)
    return pd.DataFrame(
        {
            spec.variable: [
                int(line[spec.start - 1 : spec.end]) for line in lines
            ]
            for spec in specs
        }
    )


def _documented_by_codebook(entry, value: int) -> bool:
    """The test's own oracle: the entry's ``codes`` or the codebook range
    (the ranges are held to the registry text below)."""

    if entry["codes"]:
        return str(value) in entry["codes"]
    concept = entry["concept"]
    if concept == "age":
        return value in (0, 999) or 1 <= value <= 125
    if concept == "reported_birth_year":
        return value in (0, 9999) or 1870 <= value <= int(entry["wave"])
    if concept == "interview":
        return 0 <= value <= 99_999
    if concept == "weight":
        return value >= 0
    assert concept in ("person_family_id", "person_number"), concept
    return value >= 1


_KEYS = [
    spec.concept
    for spec in loader.individual_specs(sources.RegistrySet.committed())
]


@pytest.fixture(scope="module")
def raw_individual(u2_inputs, committed_registries):
    return _raw_individual(u2_inputs, committed_registries)


@settings(max_examples=200, deadline=None)
@given(
    key=st.sampled_from(_KEYS),
    value=st.one_of(
        st.integers(min_value=-5, max_value=130),
        st.integers(min_value=1860, max_value=2030),
        st.sampled_from([999, 9998, 9999, 99_999, 100_000]),
    ),
    row=st.integers(min_value=0, max_value=75),
)
def test_the_individual_check_accepts_exactly_the_documented_domain(
    raw_individual, committed_registries, key, value, row
):
    """Invariant: for every field U2 reads and every integer value, the
    check refuses one record holding it iff the registry does not
    document it (and leaves every documented value to load)."""

    raw = raw_individual.copy()
    assert loader.check_individual_values(raw, committed_registries)
    entry = committed_registries.entry("individual", key)
    raw.loc[row % len(raw), entry["variable"]] = value
    documented = _documented_by_codebook(entry, value)
    if documented:
        checked = loader.check_individual_values(raw, committed_registries)
        assert checked[key] == len(raw)
    else:
        with pytest.raises(loader.U2UndocumentedValue, match=key):
            loader.check_individual_values(raw, committed_registries)


def test_the_documented_ranges_are_the_registry_codebook_text(
    committed_registries,
):
    """The ranges the loader restates for fields without ``codes`` are
    the ones every wave's codebook text prints; the sex codes it maps are
    exactly common.sex's."""

    for wave in sources.SUPPORT_WAVES:
        age = committed_registries.entry("individual", f"{wave}.age")
        assert age["codes"] == {}
        for line in (
            "1 Newborn up to second birthday",
            "2 - 125 Actual age",
            "999 DK; NA; refused",
            "0 Inap.",
        ):
            assert line in age["codebook_text"], (wave, line)
        born = committed_registries.entry(
            "individual", f"{wave}.reported_birth_year"
        )
        assert list(born["missing_codes"]) == [0, 9999]
        assert (
            f"1,870 - {wave // 1000},{wave % 1000:03d} Actual year of birth"
            in born["codebook_text"]
        )
        interview = committed_registries.entry(
            "individual", f"{wave}.interview"
        )
        assert interview["codes"] == {}
        assert interview["layout"]["width"] == 5
        assert "0 Inap." in interview["codebook_text"]
        weight = committed_registries.entry("individual", f"{wave}.weight")
        assert "do not infer a domain" in weight["selection"]
    sex = committed_registries.entry("individual", "common.sex")
    assert {int(code) for code in sex["codes"]} == set(loader._PERSON_SEX)
    assert loader._AGE_CODES == (0, 999)
    assert loader._AGE_RANGE == (1, 125)
    assert loader._FIRST_BIRTH_YEAR == 1870


def test_an_undocumented_relationship_code_has_no_ofum_rule(declared):
    """Finding 1's second path: a relationship code no wave documents
    (99), code 92 before 2017, and code 0 ("Inap.") on an in-family
    member refuse in both role contexts; a documented code outside
    section 3's table still takes the inherited OFUM rule."""

    registry = sources.RoleContext.from_registry()
    for context in (registry, declared):
        for wave in sources.SUPPORT_WAVES:
            for code in (99, 1, 0):
                with pytest.raises(sources.U2RoleRefusal):
                    context.rule(wave, code)
            rule = context.rule(wave, 30)
            assert (rule.income_role, rule.spouse_slot) == ("ofum", False)
        for wave in (2013, 2015):
            with pytest.raises(sources.U2RoleRefusal):
                context.rule(wave, 92)


# ---------------------------------------------------------------------------
# Review round 1, finding 2: the frozen PSID file and frame identities.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def evidence(loaded):
    """The evidence record the step-4 pass would write from the staged
    invented files (INVENTED DATA - NOT A COMPARISON)."""

    return loader.preregistration_evidence(loaded["inputs"])


@pytest.fixture(scope="module")
def frozen_load(loaded, evidence, u2_inputs):
    """The same staged directory reloaded against its frozen evidence."""

    inputs = _load(loaded["root"], u2_inputs, evidence=evidence)
    return {
        "inputs": inputs,
        "sha256": loader.preregistration_evidence_sha256(evidence),
    }


def test_the_evidence_freezes_every_file_read_and_the_frame_digest(
    loaded, evidence
):
    inputs = loaded["inputs"]
    assert evidence["target_id"] == "U2"
    assert evidence["psid_files_sha256"] == dict(
        sorted(inputs.provenance["psid_files_sha256"].items())
    )
    assert set(evidence["psid_files_sha256"]) == loaded["staged"]
    assert evidence["input_frames_sha256"] == (
        inputs.loader_seal["input_frames_sha256"]
    )
    assert evidence["psid_files_bundle_sha256"] == (
        inputs.loader_seal["psid_files_bundle_sha256"]
    )
    assert evidence["registries_sha256"] == dict(
        sorted(sources.REGISTRY_SHA256.items())
    )
    assert "psid_data_dir" not in evidence
    assert loader.check_preregistration_evidence(evidence) == evidence


def test_a_frozen_reload_matches_and_seals_the_evidence(
    loaded, frozen_load, evidence
):
    inputs = frozen_load["inputs"]
    assert _GUARD["opened"] == []
    assert inputs.loader_seal[cohort.EVIDENCE_KEY] == frozen_load["sha256"]
    assert inputs.provenance[cohort.EVIDENCE_KEY] == frozen_load["sha256"]
    provenance = cohort._input_provenance(inputs)
    assert provenance[cohort.EVIDENCE_KEY] == frozen_load["sha256"]
    assert provenance["input_frames_sha256"] == (
        evidence["input_frames_sha256"]
    )
    # The unfrozen load's seal is unchanged (no evidence key).
    assert cohort.EVIDENCE_KEY not in loaded["inputs"].loader_seal


def _flip_one_byte(path: Path, offset: int) -> bytes:
    raw = path.read_bytes()
    old = raw[offset : offset + 1]
    new = b"7" if old != b"7" else b"8"
    path.write_bytes(raw[:offset] + new + raw[offset + 1 :])
    return raw


def _amount_offset(root, committed_registries) -> int:
    """The byte offset of a digit inside a 2019 amount field, so the
    changed file still parses (the unfrozen load accepts it)."""

    gate = sources.SourceGate(sources.INVENTED_DECLARED, committed_registries)
    spec = next(
        spec
        for spec in loader.family_record_specs(2019, gate)
        if spec.concept == "head_labor"
    )
    first = (
        (root / "family" / "2019" / "FAM2019ER.txt")
        .read_text(encoding="ascii")
        .splitlines()[0]
    )
    return spec.end - 1 if first[spec.end - 1].isdigit() else spec.end - 2


def test_one_changed_byte_refuses_the_frozen_load(
    tmp_path, u2_inputs, committed_registries, evidence
):
    """Section 14: "changed source bytes ... refuse execution".  A digit
    changed in a 2019 amount field leaves a parseable file the unfrozen
    load accepts with other frames; against the frozen evidence the same
    change refuses before any record is parsed."""

    _stage(tmp_path, u2_inputs, committed_registries)
    path = tmp_path / "family" / "2019" / "FAM2019ER.txt"
    _flip_one_byte(path, _amount_offset(tmp_path, committed_registries))
    changed = _load(tmp_path, u2_inputs)
    assert changed.loader_seal["input_frames_sha256"] != (
        evidence["input_frames_sha256"]
    )
    parsed = []
    patch = pytest.MonkeyPatch()
    original = sources.parse_fixed_width
    patch.setattr(
        sources,
        "parse_fixed_width",
        lambda *a, **k: parsed.append(1) or original(*a, **k),
    )
    try:
        with pytest.raises(
            loader.U2LoaderRefusal, match="changed source bytes"
        ) as refusal:
            _load(tmp_path, u2_inputs, evidence=evidence)
    finally:
        patch.undo()
    assert type(refusal.value).__name__ == "U2FrozenIdentityMismatch"
    assert "family/2019/FAM2019ER.txt" in str(refusal.value)
    assert parsed == []
    assert _GUARD["opened"] == []


@pytest.mark.parametrize(
    "relative",
    [
        "ind2023er/IND2023ER.txt",
        "ind2023er/IND2023ER.sps",
        "family/2013/FAM2013ER.sps",
        "family/2023/FAM2023ER.txt",
    ],
)
def test_any_changed_or_missing_staged_file_refuses(
    tmp_path, u2_inputs, committed_registries, evidence, relative
):
    _stage(tmp_path, u2_inputs, committed_registries)
    _flip_one_byte(tmp_path / relative, 0)
    with pytest.raises(loader.U2LoaderRefusal, match="1 frozen PSID file"):
        _load(tmp_path, u2_inputs, evidence=evidence)
    (tmp_path / relative).unlink()
    with pytest.raises(loader.U2LoaderRefusal, match="1 missing"):
        _load(tmp_path, u2_inputs, evidence=evidence)


def test_a_changed_frame_digest_refuses(
    tmp_path, u2_inputs, committed_registries, evidence
):
    """Section 14: "changed frame digests ... refuse".  Every staged file
    is unchanged, but the (patched) marriage-history reader returns other
    frames: the digest check after reading refuses."""

    _stage(tmp_path, u2_inputs, committed_registries)
    history = u2_inputs.marriage_history.iloc[1:].reset_index(drop=True)
    with pytest.raises(loader.U2LoaderRefusal, match="frame digest|digest"):
        _load(tmp_path, u2_inputs, evidence=evidence, history=history)


def test_a_file_read_but_not_frozen_refuses(
    tmp_path, u2_inputs, committed_registries, evidence
):
    _stage(tmp_path, u2_inputs, committed_registries)
    files = dict(evidence["psid_files_sha256"])
    files.pop("family/2017/FAM2017ER.txt")
    narrower = {
        **evidence,
        "psid_files_sha256": files,
        "psid_files_bundle_sha256": loader.files_bundle_sha256(files),
    }
    with pytest.raises(loader.U2LoaderRefusal, match="read but not frozen"):
        _load(tmp_path, u2_inputs, evidence=narrower)


def _altered(evidence, **changes):
    record = {**evidence, **changes}
    return record


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda e: _altered(e, schema_version="v0"), "schema"),
        (lambda e: _altered(e, target_id="U1"), "not 'U2'"),
        (lambda e: _altered(e, specification="other"), "specification"),
        (
            lambda e: _altered(
                e,
                registries_sha256={
                    **e["registries_sha256"],
                    "roles": "0" * 64,
                },
            ),
            "registries other than",
        ),
        (
            lambda e: _altered(e, input_frames_sha256="ABC"),
            "input_frames_sha256",
        ),
        (
            lambda e: _altered(e, psid_files_bundle_sha256="0" * 64),
            "bundle",
        ),
        (
            lambda e: _altered(
                e,
                psid_files_sha256={"/etc/passwd": "0" * 64},
                psid_files_bundle_sha256=loader.files_bundle_sha256(
                    {"/etc/passwd": "0" * 64}
                ),
            ),
            "relative",
        ),
        (
            lambda e: _altered(
                e,
                psid_files_sha256={"../x.txt": "0" * 64},
                psid_files_bundle_sha256=loader.files_bundle_sha256(
                    {"../x.txt": "0" * 64}
                ),
            ),
            "relative",
        ),
        (
            lambda e: _altered(
                e,
                psid_files_sha256={},
                psid_files_bundle_sha256=loader.files_bundle_sha256({}),
            ),
            "no PSID file",
        ),
        (lambda e: {**e, "extra": 1}, "not exactly"),
        # Round 3, second pass: only plain JSON data, by exact type.
        (
            lambda e: {
                **e,
                "input_frames_sha256": type("_S", (str,), {})(
                    e["input_frames_sha256"]
                ),
            },
            "plain JSON",
        ),
        (
            lambda e: {
                **e,
                "psid_files_sha256": MappingProxyType(e["psid_files_sha256"]),
            },
            "plain JSON",
        ),
        (
            lambda e: {
                **e,
                "psid_files_sha256": {
                    type("_S", (str,), {})(key): value
                    for key, value in e["psid_files_sha256"].items()
                },
            },
            "plain JSON",
        ),
        (
            lambda e: {k: v for k, v in e.items() if k != "target_id"},
            "not exactly",
        ),
    ],
)
def test_a_malformed_evidence_record_refuses(evidence, change, message):
    with pytest.raises(loader.U2LoaderRefusal, match=message):
        loader.check_preregistration_evidence(change(dict(evidence)))


def test_an_absent_evidence_record_refuses(tmp_path):
    with pytest.raises(loader.U2LoaderRefusal, match="no pre-registration"):
        loader.read_preregistration_evidence(tmp_path / "absent.json")
    path = tmp_path / "evidence.json"
    path.write_text("not json")
    with pytest.raises(loader.U2LoaderRefusal, match="not JSON"):
        loader.read_preregistration_evidence(path)


def test_the_committed_evidence_record_is_absent_so_registration_refuses():
    """At this commit the section 20 step-4 pass has not run: there is no
    committed evidence record, so the registered run cannot bind one."""

    assert not loader.PREREGISTRATION_EVIDENCE_PATH.exists()
    with pytest.raises(loader.U2LoaderRefusal, match="no pre-registration"):
        loader.read_preregistration_evidence()


def test_evidence_is_recorded_only_from_loader_sealed_inputs(
    loaded, u2_inputs
):
    with pytest.raises(loader.U2LoaderRefusal, match="loader sealed"):
        loader.preregistration_evidence(u2_inputs)
    labelled = cohort.replace_provenance(u2_inputs, kind=cohort.PSID_FILES)
    with pytest.raises(cohort.U2CohortError, match="U2 loader"):
        loader.preregistration_evidence(labelled)


def test_a_forged_evidence_seal_refuses(loaded, frozen_load):
    """The evidence hash counts only when the seal and the provenance
    both carry it, as the loader wrote them."""

    import dataclasses

    unfrozen = loaded["inputs"]
    forged = dataclasses.replace(
        unfrozen,
        provenance={
            **unfrozen.provenance,
            cohort.EVIDENCE_KEY: frozen_load["sha256"],
        },
    )
    object.__setattr__(forged, "loader_seal", dict(unfrozen.loader_seal))
    with pytest.raises(cohort.U2CohortError, match="sealed"):
        cohort._input_provenance(forged)
    rechecked = frozen_load["inputs"]
    stripped = dataclasses.replace(
        rechecked,
        provenance={
            k: v
            for k, v in rechecked.provenance.items()
            if k != cohort.EVIDENCE_KEY
        },
    )
    object.__setattr__(stripped, "loader_seal", dict(rechecked.loader_seal))
    with pytest.raises(cohort.U2CohortError, match="sealed"):
        cohort._input_provenance(stripped)


@pytest.fixture(scope="module")
def frozen_stage(tmp_path_factory, u2_inputs, committed_registries):
    root = tmp_path_factory.mktemp("frozen-stage")
    _stage(root, u2_inputs, committed_registries)
    files = {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in sorted(
            str(path.relative_to(root))
            for path in root.rglob("*")
            if path.is_file()
        )
    }
    record = {
        "schema_version": loader.PREREGISTRATION_SCHEMA,
        "target_id": "U2",
        "specification": "boomers2004_1946_55_uniform_cut",
        "registries_sha256": dict(sources.REGISTRY_SHA256),
        "cited_sources_sha256": {},
        "psid_files_sha256": files,
        "psid_files_bundle_sha256": loader.files_bundle_sha256(files),
        "input_frames_sha256": "0" * 64,
    }
    return {"root": root, "evidence": record, "files": sorted(files)}


@settings(max_examples=100, deadline=None)
@given(data=st.data())
def test_every_single_byte_change_to_any_frozen_file_refuses(
    frozen_stage, data
):
    """Invariant: for every frozen file, byte offset and replacement byte,
    the pre-read recheck refuses; with the bytes restored it passes."""

    root, record = frozen_stage["root"], frozen_stage["evidence"]
    relative = data.draw(st.sampled_from(frozen_stage["files"]))
    path = root / relative
    raw = path.read_bytes()
    offset = data.draw(st.integers(0, len(raw) - 1))
    byte = data.draw(
        st.integers(0, 255).filter(lambda value: value != raw[offset])
    )
    path.write_bytes(raw[:offset] + bytes([byte]) + raw[offset + 1 :])
    try:
        with pytest.raises(loader.U2FrozenIdentityMismatch, match="changed"):
            loader.check_frozen_files(record, root)
    finally:
        path.write_bytes(raw)
    assert loader.check_frozen_files(record, root) == (
        record["psid_files_sha256"]
    )


def test_loader_inputs_cannot_join_an_invented_cohort(
    loaded, u2_inputs, u0_cohort
):
    """Review 2, finding 1, on the loader's own output: an invented
    cohort's income rows refuse the sealed psid_files inputs."""

    with pytest.raises(cohort.U2CohortError, match="built from"):
        cohort.income_rows(u0_cohort, loaded["inputs"])


def test_the_loader_seal_is_read_only_and_bound_to_the_file_hashes(loaded):
    import dataclasses

    inputs = loaded["inputs"]
    with pytest.raises(TypeError):
        inputs.loader_seal["input_frames_sha256"] = "0" * 64
    # A seal whose file bundle no longer matches the recorded file
    # hashes is refused (as U1's loader seal is).
    relabelled = dataclasses.replace(
        inputs,
        provenance={
            **inputs.provenance,
            "psid_files_sha256": {"family/2019/FAM2019ER.txt": "0" * 64},
        },
    )
    object.__setattr__(relabelled, "loader_seal", dict(inputs.loader_seal))
    with pytest.raises(cohort.U2CohortError, match="sealed"):
        cohort._input_provenance(relabelled)


# ---------------------------------------------------------------------------
# Review round 2, info 2: a registered run compares the loader's sealed
# evidence hash with the hash its registration binds (not only its shape).
# INVENTED DATA - NOT A COMPARISON: the inputs are the staged invented files.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "bound, message",
    [
        (None, "binds"),
        ("0" * 64, "binds"),
        ("not-a-hash", "binds"),
    ],
    ids=["unnamed", "another-record", "malformed"],
)
def test_a_registered_run_needs_the_evidence_its_registration_binds(
    frozen_load, bound, message
):
    registry = sources.RoleContext.from_registry()
    with pytest.raises(runner.U2RunError, match=message):
        runner.check_inputs(
            frozen_load["inputs"],
            ap.REGISTERED_REAL,
            POINTER,
            registry,
            preregistration_evidence_sha256=bound,
        )


def test_an_invented_run_binds_no_evidence(u2_inputs, declared):
    with pytest.raises(runner.U2RunError, match="binds no"):
        runner.check_inputs(
            u2_inputs,
            ap.INVENTED,
            None,
            declared,
            preregistration_evidence_sha256="0" * 64,
        )


class _Reached(Exception):
    pass


def test_a_mismatched_evidence_hash_refuses_before_any_computation(
    frozen_load, monkeypatch
):
    def reached(*args, **kwargs):
        raise _Reached

    monkeypatch.setattr(cohort, "derive_u2_births", reached)
    with pytest.raises(runner.U2RunError, match="binds"):
        runner.run_track_u2(
            frozen_load["inputs"],
            parameters.committed_u2_parameters(),
            data_provenance=ap.REGISTERED_REAL,
            role_context=sources.RoleContext.from_registry(),
            registration_pointer=POINTER,
            preregistration_evidence_sha256="0" * 64,
        )


def test_a_registered_run_computes_with_the_fresh_pinned_read(
    frozen_load, evidence, monkeypatch
):
    """Review round 2: the check verifies the caller's bundle, and the
    run then computes with the fresh read of the pinned files, so an edit
    the caller makes after the check (here, from the progress callback,
    an INVENTED 1.0) never reaches a row."""

    caller = copy.deepcopy(parameters.committed_u2_parameters())
    pinned_value = caller.thresholds.weighted_average[2020]["one_65_plus"]
    seen = []

    def compute_row(row, inputs, params, births, **kwargs):
        seen.append(params)
        raise _Reached

    def progress(message):
        caller.thresholds.weighted_average[2020]["one_65_plus"] = 1.0

    monkeypatch.setattr(runner, "_compute_row", compute_row)
    with pytest.raises(_Reached):
        runner.run_track_u2(
            frozen_load["inputs"],
            caller,
            data_provenance=ap.REGISTERED_REAL,
            role_context=sources.RoleContext.from_registry(),
            registration_pointer=POINTER,
            preregistration_evidence_sha256=frozen_load["sha256"],
            preregistration_evidence=evidence,
            progress=progress,
        )
    assert caller.thresholds.weighted_average[2020]["one_65_plus"] == 1.0
    (used,) = seen
    assert used is not caller
    assert used.thresholds.weighted_average[2020]["one_65_plus"] == (
        pinned_value
    )
    assert parameters.parameters_content_sha256(used) == (
        parameters.parameters_content_sha256(
            parameters.committed_u2_parameters()
        )
    )


# ---------------------------------------------------------------------------
# Review round 3, info 1: the seal is only the loader's own claim.  A seal
# written in-process (``object.__setattr__`` on the frozen dataclass's
# ``init=False`` field) over altered frames repeats that claim, so a
# registered run compares the frames and PSID files with the evidence
# record its registration binds.  Info 2: a registered run computes the
# registered rows only and takes no ``row_set``.
# INVENTED DATA - NOT A COMPARISON: the inputs are the staged invented
# files read back by the loader, and every altered value is an invented
# offset.
# ---------------------------------------------------------------------------
#: INVENTED: added to one cell, as the round-3 review's probe B2 did.
_INVENTED_OFFSET = 5


def _forge(rechecked: cohort.U2Inputs, **frames) -> cohort.U2Inputs:
    """``rechecked`` with ``frames`` replaced under a forged seal.

    The seal is written as the loader writes it, over the changed frames'
    own digest, with the file bundle and the bound evidence hash kept; the
    provenance is the loader's, unchanged.  The forgery is therefore
    internally consistent, and ``cohort._input_provenance`` accepts it.
    """

    import dataclasses

    forged = dataclasses.replace(rechecked, **frames)
    seal = {
        **dict(rechecked.loader_seal),
        "input_frames_sha256": cohort.input_frames_sha256(forged),
    }
    object.__setattr__(forged, "loader_seal", MappingProxyType(seal))
    return forged


def _offset_cell(
    frame: pd.DataFrame, column: str, row: int, offset: int
) -> pd.DataFrame:
    """A copy of ``frame`` with the INVENTED ``offset`` added to one cell
    (a missing cell becomes the offset)."""

    changed = frame.copy()
    position = changed.columns.get_loc(column)
    old = changed.iat[row, position]
    changed.iat[row, position] = offset if pd.isna(old) else old + offset
    return changed


def _income_forgery(rechecked: cohort.U2Inputs) -> cohort.U2Inputs:
    """The review's probe B2: +5 (invented) in one 2019 income cell."""

    income = dict(rechecked.family_income)
    income[2019] = _offset_cell(
        income[2019], "total_family_income", 0, _INVENTED_OFFSET
    )
    return _forge(rechecked, family_income=income)


def _registered_check(inputs, frozen_load, **evidence):
    return runner.check_inputs(
        inputs,
        ap.REGISTERED_REAL,
        POINTER,
        sources.RoleContext.from_registry(),
        preregistration_evidence_sha256=frozen_load["sha256"],
        **evidence,
    )


def test_a_forged_seal_over_altered_frames_passes_only_the_seal_check(
    frozen_load, evidence
):
    """Review round 3, info 1 (probe B2).  The forged seal and the
    loader's provenance agree, so the provenance check accepts the altered
    frames and the bound hash matches the seal.  Before this round the
    registered check accepted them; given only the bound hash it now
    refuses, since it must see the evidence record itself."""

    forged = _income_forgery(frozen_load["inputs"])
    assert cohort.input_frames_sha256(forged) != (
        evidence["input_frames_sha256"]
    )
    provenance = cohort._input_provenance(forged)
    assert provenance[cohort.EVIDENCE_KEY] == frozen_load["sha256"]
    with pytest.raises(runner.U2RunError, match="evidence record"):
        _registered_check(forged, frozen_load)


def test_a_forged_seal_refuses_against_the_bound_evidence_record(
    frozen_load, evidence
):
    forged = _income_forgery(frozen_load["inputs"])
    with pytest.raises(runner.U2RunError, match="frame digest"):
        _registered_check(
            forged, frozen_load, preregistration_evidence=evidence
        )


def test_the_loader_rechecked_inputs_pass_against_the_bound_record(
    frozen_load, evidence
):
    assert _registered_check(
        frozen_load["inputs"], frozen_load, preregistration_evidence=evidence
    ) == {
        cohort.EVIDENCE_KEY: frozen_load["sha256"],
        "input_frames_sha256": evidence["input_frames_sha256"],
    }


def test_relabelled_psid_file_hashes_refuse_against_the_bound_record(
    frozen_load, evidence
):
    """Frames unchanged, but the provenance's file hashes relabelled and
    the seal's bundle forged to match: the provenance check accepts it,
    the evidence record does not."""

    import dataclasses

    rechecked = frozen_load["inputs"]
    files = {
        **dict(rechecked.provenance["psid_files_sha256"]),
        "family/2019/FAM2019ER.txt": "0" * 64,
    }
    bundle = loader.files_bundle_sha256(files)
    forged = dataclasses.replace(
        rechecked,
        provenance={
            **rechecked.provenance,
            "psid_files_sha256": files,
            "psid_files_bundle_sha256": bundle,
        },
    )
    object.__setattr__(
        forged,
        "loader_seal",
        MappingProxyType(
            {**rechecked.loader_seal, "psid_files_bundle_sha256": bundle}
        ),
    )
    assert cohort._input_provenance(forged)["psid_files_sha256"] == files
    with pytest.raises(runner.U2RunError, match="PSID file hashes"):
        _registered_check(
            forged, frozen_load, preregistration_evidence=evidence
        )


def test_relabelled_cited_sources_refuse_against_the_bound_record(
    frozen_load, evidence
):
    import dataclasses

    rechecked = frozen_load["inputs"]
    forged = dataclasses.replace(
        rechecked,
        provenance={
            **rechecked.provenance,
            "cited_sources_sha256": {"PSID/invented.sps": "0" * 64},
        },
    )
    object.__setattr__(forged, "loader_seal", rechecked.loader_seal)
    cohort._input_provenance(forged)
    with pytest.raises(runner.U2RunError, match="cited"):
        _registered_check(
            forged, frozen_load, preregistration_evidence=evidence
        )


@pytest.mark.parametrize(
    "record, message",
    [
        (lambda e: {**e, "input_frames_sha256": "0" * 64}, "hashes to"),
        (lambda e: {**e, "extra": 1}, "not valid"),
        (lambda e: "not a record", "not valid"),
    ],
    ids=["another-record", "malformed", "not-a-mapping"],
)
def test_a_registered_run_needs_the_record_its_bound_hash_names(
    frozen_load, evidence, record, message
):
    with pytest.raises(runner.U2RunError, match=message):
        _registered_check(
            frozen_load["inputs"],
            frozen_load,
            preregistration_evidence=record(dict(evidence)),
        )


def test_an_invented_run_takes_no_evidence_record(
    u2_inputs, declared, evidence
):
    with pytest.raises(runner.U2RunError, match="binds no"):
        runner.check_inputs(
            u2_inputs,
            ap.INVENTED,
            None,
            declared,
            preregistration_evidence=evidence,
        )


def test_a_forged_seal_refuses_before_any_computation(
    frozen_load, evidence, monkeypatch
):
    def reached(*args, **kwargs):
        raise _Reached

    monkeypatch.setattr(cohort, "derive_u2_births", reached)
    with pytest.raises(runner.U2RunError, match="frame digest"):
        runner.run_track_u2(
            _income_forgery(frozen_load["inputs"]),
            parameters.committed_u2_parameters(),
            data_provenance=ap.REGISTERED_REAL,
            role_context=sources.RoleContext.from_registry(),
            registration_pointer=POINTER,
            preregistration_evidence_sha256=frozen_load["sha256"],
            preregistration_evidence=evidence,
        )


def _numeric_sites(inputs: cohort.U2Inputs) -> list[tuple]:
    """``(field, wave or None, column)`` of every numeric column of every
    nonempty input frame."""

    sites = []
    for name in ("anchors", "family_income", "family_wealth", "employer_dc"):
        for wave, frame in sorted(getattr(inputs, name).items()):
            if len(frame):
                sites += [
                    (name, wave, column)
                    for column in frame.select_dtypes("number").columns
                ]
    for name in ("design", "persons", "marriage_history", "observed_earnings"):
        frame = getattr(inputs, name)
        if len(frame):
            sites += [
                (name, None, column)
                for column in frame.select_dtypes("number").columns
            ]
    return sites


@settings(max_examples=100, deadline=None)
@given(data=st.data())
def test_no_seal_forged_over_any_changed_cell_passes_the_registered_check(
    frozen_load, evidence, data
):
    """Invariant (round 3, info 1): for every numeric cell of every input
    frame and every nonzero INVENTED offset, inputs whose seal is forged
    over the changed frames pass the provenance check yet refuse the
    registered check, given only the bound hash and given the bound
    evidence record; the loader's own rechecked inputs pass."""

    rechecked = frozen_load["inputs"]
    name, wave, column = data.draw(
        st.sampled_from(_numeric_sites(rechecked)), label="site"
    )
    frames = getattr(rechecked, name)
    frame = frames if wave is None else frames[wave]
    row = data.draw(st.integers(0, len(frame) - 1), label="row")
    offset = data.draw(
        st.integers(1, 1000) | st.integers(-1000, -1), label="offset"
    )
    changed = _offset_cell(frame, column, row, offset)
    forged = _forge(
        rechecked,
        **{name: changed if wave is None else {**frames, wave: changed}},
    )
    assume(
        cohort.input_frames_sha256(forged) != evidence["input_frames_sha256"]
    )
    assert cohort._input_provenance(forged)[cohort.EVIDENCE_KEY] == (
        frozen_load["sha256"]
    )
    with pytest.raises(runner.U2RunError, match="evidence record"):
        _registered_check(forged, frozen_load)
    with pytest.raises(runner.U2RunError, match="frame digest"):
        _registered_check(
            forged, frozen_load, preregistration_evidence=evidence
        )
    _registered_check(
        rechecked, frozen_load, preregistration_evidence=evidence
    )


def test_a_registered_run_refuses_altered_row_definitions(
    frozen_load, evidence, monkeypatch
):
    """Review round 3, info 2 (probe B3): U0 given the 2 percent interest
    override passed every guard, which checked only the row ids, and
    reached the row computation.  A registered run now refuses any
    ``row_set`` before the inputs are checked."""

    import dataclasses

    altered = {
        **rows.REGISTERED_ROWS,
        "U0": dataclasses.replace(
            rows.REGISTERED_ROWS["U0"], income={"real_interest_rate": 0.02}
        ),
    }
    assert list(altered) == list(rows.ROW_IDS)
    seen = []

    def compute_row(row, *args, **kwargs):
        seen.append(row)
        raise _Reached

    monkeypatch.setattr(runner, "_compute_row", compute_row)
    with pytest.raises(runner.U2RunError, match="row_set"):
        runner.run_track_u2(
            frozen_load["inputs"],
            parameters.committed_u2_parameters(),
            data_provenance=ap.REGISTERED_REAL,
            role_context=sources.RoleContext.from_registry(),
            registration_pointer=POINTER,
            row_set=altered,
            preregistration_evidence_sha256=frozen_load["sha256"],
        )
    assert seen == []


def test_a_registered_run_computes_the_registered_rows_by_default(
    frozen_load, evidence, monkeypatch
):
    seen = []

    def compute_row(row, *args, **kwargs):
        seen.append(row)
        raise _Reached

    monkeypatch.setattr(runner, "_compute_row", compute_row)
    with pytest.raises(_Reached):
        runner.run_track_u2(
            frozen_load["inputs"],
            parameters.committed_u2_parameters(),
            data_provenance=ap.REGISTERED_REAL,
            role_context=sources.RoleContext.from_registry(),
            registration_pointer=POINTER,
            preregistration_evidence_sha256=frozen_load["sha256"],
            preregistration_evidence=evidence,
        )
    (row,) = seen
    assert row is rows.REGISTERED_ROWS[rows.HEADLINE_ROW]


@settings(max_examples=60, deadline=None)
@given(data=st.data())
def test_a_registered_run_refuses_every_row_set_before_any_check(
    frozen_load, u2_params, data
):
    """Invariant (round 3, info 2): a registered run computes exactly
    :data:`rows.REGISTERED_ROWS`, so every ``row_set`` it is given -- the
    registered mapping itself, value-equal copies, or rows carrying
    another registered row's overrides or the unscored 2 percent
    interest -- refuses before the inputs, the parameters or any row are
    touched."""

    import dataclasses

    registered = list(rows.REGISTERED_ROWS.values())
    row_set = {}
    for row in registered:
        kind = data.draw(
            st.sampled_from(("same", "copy", "other", "interest")),
            label=row.row_id,
        )
        if kind == "same":
            row_set[row.row_id] = row
        elif kind == "copy":
            row_set[row.row_id] = dataclasses.replace(row)
        elif kind == "other":
            other = data.draw(st.sampled_from(registered))
            row_set[row.row_id] = dataclasses.replace(
                row, cohort=dict(other.cohort), income=dict(other.income)
            )
        else:
            row_set[row.row_id] = dataclasses.replace(
                row, income={**dict(row.income), "real_interest_rate": 0.02}
            )
    if data.draw(st.booleans(), label="the registered mapping itself"):
        row_set = rows.REGISTERED_ROWS

    def reached(*args, **kwargs):
        raise _Reached

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(runner, "check_inputs", reached)
        patch.setattr(parameters, "check_u2_parameters", reached)
        patch.setattr(runner, "_compute_row", reached)
        with pytest.raises(runner.U2RunError, match="row_set"):
            runner.run_track_u2(
                frozen_load["inputs"],
                u2_params,
                data_provenance=ap.REGISTERED_REAL,
                role_context=sources.RoleContext.from_registry(),
                registration_pointer=POINTER,
                row_set=row_set,
                preregistration_evidence_sha256=frozen_load["sha256"],
            )


class _RiggedProvenance:
    """INVENTED: equal to nothing and unequal to nothing, so ``==`` and
    ``!=`` tests against the registered label both come out False."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


@pytest.mark.parametrize(
    "provenance",
    [_RiggedProvenance(), type("_Label", (str,), {})(ap.REGISTERED_REAL)],
    ids=["rigged-equality", "str-subclass"],
)
def test_a_registered_run_takes_only_an_exact_provenance_label(
    frozen_load, evidence, monkeypatch, provenance
):
    """A label that is not exactly one of the two registered strings is
    refused before anything else, so no comparison it rigs can skip the
    row-set guard while the registered checks still run."""

    import dataclasses

    altered = {
        **rows.REGISTERED_ROWS,
        "U0": dataclasses.replace(
            rows.REGISTERED_ROWS["U0"], income={"real_interest_rate": 0.02}
        ),
    }

    def reached(*args, **kwargs):
        raise _Reached

    monkeypatch.setattr(runner, "_compute_row", reached)
    with pytest.raises(runner.U2RunError, match="data_provenance"):
        runner.run_track_u2(
            frozen_load["inputs"],
            parameters.committed_u2_parameters(),
            data_provenance=provenance,
            role_context=sources.RoleContext.from_registry(),
            registration_pointer=POINTER,
            row_set=altered,
            preregistration_evidence_sha256=frozen_load["sha256"],
            preregistration_evidence=evidence,
        )


class _MutatingProvenance(dict):
    """INVENTED: a provenance mapping that, when the parameter check reads
    it, adds an invented offset to one input frame in place and forges
    the seal over the result (review round 3: check, then use)."""

    def __init__(self, labels, act):
        super().__init__(labels)
        self._act = act

    # Overriding ``__iter__`` takes ``dict(...)`` off its fast path, so the
    # copy the parameter check makes calls ``keys``.
    def __iter__(self):
        self._act()
        return super().__iter__()

    def keys(self):
        self._act()
        return super().keys()


def _private_copy(rechecked: cohort.U2Inputs) -> cohort.U2Inputs:
    """The frozen load with its frames copied and its seal kept (equal
    frames, so the loader's seal still holds): a copy a test may edit."""

    import dataclasses

    income = {
        wave: frame.copy() for wave, frame in rechecked.family_income.items()
    }
    copy_ = dataclasses.replace(rechecked, family_income=income)
    object.__setattr__(copy_, "loader_seal", rechecked.loader_seal)
    return copy_


def test_frames_changed_after_the_check_reach_no_row(
    frozen_load, evidence, monkeypatch
):
    """Between the input check and the births, the run reads the caller's
    parameter provenance.  An edit made there to the frames, with the seal
    forged again, is refused: the births must carry the frame digest the
    bound record froze, and every row's build compares with the births."""

    import dataclasses

    inputs = _private_copy(frozen_load["inputs"])
    fired = []

    def act():
        if fired:
            return
        fired.append(True)
        frame = inputs.family_income[2019]
        column = frame.columns.get_loc("total_family_income")
        frame.iat[0, column] = frame.iat[0, column] + _INVENTED_OFFSET
        seal = {
            **dict(inputs.loader_seal),
            "input_frames_sha256": cohort.input_frames_sha256(inputs),
        }
        object.__setattr__(inputs, "loader_seal", MappingProxyType(seal))

    pinned = parameters.committed_u2_parameters()
    params = dataclasses.replace(
        pinned,
        thresholds=dataclasses.replace(
            pinned.thresholds,
            provenance=_MutatingProvenance(pinned.thresholds.provenance, act),
        ),
    )

    def reached(*args, **kwargs):
        raise _Reached

    monkeypatch.setattr(runner, "_compute_row", reached)
    with pytest.raises(runner.U2RunError, match="changed after"):
        runner.run_track_u2(
            inputs,
            params,
            data_provenance=ap.REGISTERED_REAL,
            role_context=sources.RoleContext.from_registry(),
            registration_pointer=POINTER,
            preregistration_evidence_sha256=frozen_load["sha256"],
            preregistration_evidence=evidence,
        )
    assert fired == [True]
    assert (
        cohort.input_frames_sha256(inputs) != evidence["input_frames_sha256"]
    )


# ---------------------------------------------------------------------------
# Round 3, second pass: the frame digest and the evidence comparison must
# read exactly what the run computes on.  An independent adversarial
# verification of the first pass (four blind lanes, invented data) found
# that type confusion kept the digest and the seal intact while the rows
# read other values: a str subclass in the evidence record or bound hash,
# a dict subclass for a frame container, a str-subclass cell or column
# label, and a role context whose rules were rewritten after construction.
# INVENTED DATA - NOT A COMPARISON.
# ---------------------------------------------------------------------------
class _RiggedText(str):
    """INVENTED: prints as its text but equals everything and hashes as
    its text, so every comparison it makes comes out equal."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class _ComparesAs(str):
    """INVENTED: prints (and so digests) as its own text but compares and
    hashes as ``other``."""

    def __new__(cls, text, other):
        value = super().__new__(cls, text)
        value._other = other
        return value

    def __eq__(self, other):
        return str(self._other) == other

    def __ne__(self, other):
        return str(self._other) != other

    def __hash__(self):
        return hash(str(self._other))


def test_a_rigged_digest_in_the_record_refuses(frozen_load, evidence):
    """Round 3, second pass: a record whose frame digest is a str subclass
    holding the frozen text (so it hashes to the bound value) but equal
    to everything no longer lets forged frames through."""

    rigged = {
        **evidence,
        "input_frames_sha256": _RiggedText(evidence["input_frames_sha256"]),
    }
    with pytest.raises(runner.U2RunError, match="not valid"):
        _registered_check(
            _income_forgery(frozen_load["inputs"]),
            frozen_load,
            preregistration_evidence=rigged,
        )


@pytest.mark.parametrize(
    "where",
    ["bound", "seal"],
)
def test_a_rigged_evidence_hash_refuses(frozen_load, evidence, where):
    """The bound hash and the seal's evidence hash must be exactly str:
    a subclass could compare equal to any other hash."""

    import dataclasses

    rechecked = frozen_load["inputs"]
    sha = frozen_load["sha256"]
    if where == "bound":
        inputs, bound = rechecked, _RiggedText(sha)
    else:
        inputs, bound = dataclasses.replace(rechecked), sha
        seal = {**rechecked.loader_seal, cohort.EVIDENCE_KEY: _RiggedText(sha)}
        object.__setattr__(inputs, "loader_seal", MappingProxyType(seal))
        object.__setattr__(
            inputs,
            "provenance",
            {**rechecked.provenance, cohort.EVIDENCE_KEY: _RiggedText(sha)},
        )
    with pytest.raises(runner.U2RunError, match="exactly|64 lowercase hex"):
        runner.check_inputs(
            inputs,
            ap.REGISTERED_REAL,
            POINTER,
            sources.RoleContext.from_registry(),
            preregistration_evidence_sha256=bound,
            preregistration_evidence=evidence,
        )


def test_a_self_consistent_other_record_refuses_by_its_hash(
    frozen_load, evidence
):
    """Mutation check (round 3, second pass): a forged seal under the bound
    hash with a valid record describing the forged frames is refused by
    the record-hash comparison itself."""

    forged = _income_forgery(frozen_load["inputs"])
    other = loader.preregistration_evidence(forged)
    assert other["input_frames_sha256"] == cohort.input_frames_sha256(forged)
    with pytest.raises(runner.U2RunError, match="hashes to"):
        _registered_check(forged, frozen_load, preregistration_evidence=other)


_CONTAINERS = ("anchors", "family_income", "family_wealth", "employer_dc")
_LIES = ("get", "__getitem__", "items", "values", "__iter__", "keys")


def _two_faced(frames: dict, altered: dict, lie: str):
    """A dict subclass holding ``frames`` whose ``lie`` method serves
    ``altered`` instead (INVENTED)."""

    def method(self, *args, **kwargs):
        return getattr(dict, lie)(altered, *args, **kwargs)

    return type("_TwoFaced", (dict,), {lie: method})(frames)


@settings(max_examples=40, deadline=None)
@given(
    container=st.sampled_from(_CONTAINERS),
    lie=st.sampled_from(_LIES),
)
def test_no_frame_container_but_a_plain_dict_is_digested(
    frozen_load, evidence, container, lie
):
    """Invariant (round 3, second pass): the frame digest reads only plain
    dicts keyed by int, so a container that serves the digest one frame
    and the computation another is refused, whichever method lies; the
    registered check refuses it even with the loader's own seal copied."""

    import dataclasses

    rechecked = frozen_load["inputs"]
    frames = getattr(rechecked, container)
    altered = {wave: frame.copy() for wave, frame in frames.items()}
    wave = sorted(altered)[0]
    column = altered[wave].select_dtypes("number").columns[0]
    altered[wave] = _offset_cell(altered[wave], column, 0, _INVENTED_OFFSET)
    lying = dataclasses.replace(
        rechecked, **{container: _two_faced(dict(frames), altered, lie)}
    )
    object.__setattr__(lying, "loader_seal", rechecked.loader_seal)
    with pytest.raises(cohort.U2CohortError, match="plain dict"):
        cohort.input_frames_sha256(lying)
    with pytest.raises(runner.U2RunError, match="plain dict"):
        _registered_check(
            lying, frozen_load, preregistration_evidence=evidence
        )


def test_a_wave_key_must_be_an_int(frozen_load):
    import dataclasses

    rechecked = frozen_load["inputs"]
    income = {float(wave): f for wave, f in rechecked.family_income.items()}
    with pytest.raises(cohort.U2CohortError, match="int"):
        cohort.input_frames_sha256(
            dataclasses.replace(rechecked, family_income=income)
        )


def _string_sites(inputs: cohort.U2Inputs) -> list[tuple]:
    """``(field, wave or None, column)`` of every string-valued column."""

    sites = []
    for name in _CONTAINERS:
        for wave, frame in sorted(getattr(inputs, name).items()):
            sites += [
                (name, wave, column)
                for column in frame.columns
                if frame[column].dtype == object
                or isinstance(frame[column].dtype, pd.StringDtype)
            ]
    for name in ("design", "persons", "marriage_history", "observed_earnings"):
        frame = getattr(inputs, name)
        sites += [
            (name, None, column)
            for column in frame.columns
            if frame[column].dtype == object
            or isinstance(frame[column].dtype, pd.StringDtype)
        ]
    return sites


def test_a_string_cell_that_compares_as_another_refuses(frozen_load, evidence):
    """The verification's minimized case: one ``how_ended`` cell keeps its
    text (and so the digest) but compares as ``separated``, edited in
    place with no seal forgery.  The digest now refuses any string cell
    that is not exactly a str."""

    import dataclasses

    rechecked = frozen_load["inputs"]
    history = rechecked.marriage_history.copy()
    column = history.columns.get_loc("how_ended")
    text = history.iat[0, column]
    history.iat[0, column] = _ComparesAs(text, "separated")
    changed = dataclasses.replace(rechecked, marriage_history=history)
    object.__setattr__(changed, "loader_seal", rechecked.loader_seal)
    with pytest.raises(cohort.U2CohortError, match="exactly a str"):
        cohort.input_frames_sha256(changed)
    with pytest.raises(runner.U2RunError, match="exactly a str"):
        _registered_check(
            changed, frozen_load, preregistration_evidence=evidence
        )


@settings(max_examples=40, deadline=None)
@given(data=st.data())
def test_no_string_cell_but_an_exact_str_is_digested(frozen_load, data):
    """Invariant (round 3, second pass): for every string-valued column of
    every input frame and every row, a cell replaced by a str subclass of
    the same text (same CSV text, same dtype) is refused by the digest."""

    import dataclasses

    rechecked = frozen_load["inputs"]
    name, wave, column = data.draw(
        st.sampled_from(_string_sites(rechecked)), label="site"
    )
    frames = getattr(rechecked, name)
    frame = (frames if wave is None else frames[wave]).copy()
    row = data.draw(st.integers(0, len(frame) - 1), label="row")
    position = frame.columns.get_loc(column)
    text = frame.iat[row, position]
    assume(type(text) is str)
    frame.iat[row, position] = _ComparesAs(text, text + "-invented")
    changed = dataclasses.replace(
        rechecked,
        **{name: frame if wave is None else {**frames, wave: frame}},
    )
    with pytest.raises(cohort.U2CohortError, match="exactly a str"):
        cohort.input_frames_sha256(changed)


def test_a_column_label_must_be_an_exact_str(frozen_load):
    """Two labels that print as each other's names would swap two columns'
    data under an unchanged digest; labels must be distinct exact str."""

    import dataclasses

    rechecked = frozen_load["inputs"]
    persons = rechecked.persons.copy()
    persons.columns = [
        _ComparesAs(str(label), str(label)) for label in persons.columns
    ]
    with pytest.raises(cohort.U2CohortError, match="column labels"):
        cohort.input_frames_sha256(
            dataclasses.replace(rechecked, persons=persons)
        )


def test_an_unlisted_column_dtype_refuses(frozen_load):
    import dataclasses

    rechecked = frozen_load["inputs"]
    persons = rechecked.persons.assign(
        sex=rechecked.persons["sex"].astype("category")
    )
    with pytest.raises(cohort.U2CohortError, match="dtype"):
        cohort.input_frames_sha256(
            dataclasses.replace(rechecked, persons=persons)
        )


def test_the_loader_and_generator_frames_meet_the_type_rules(
    loaded, frozen_load, u2_inputs
):
    """The converse: the loader's own frames and the invented generator's
    pass the digest's type rules unchanged."""

    for inputs in (loaded["inputs"], frozen_load["inputs"], u2_inputs):
        cohort.input_frames_sha256(inputs)


def test_a_role_context_with_rewritten_rules_refuses(frozen_load, evidence):
    """A frozen RoleContext checks its rules only when built; rules
    rewritten afterwards (``object.__setattr__``) under the registry kind
    are refused by the registered check."""

    registry = sources.RoleContext.from_registry()
    object.__setattr__(
        registry,
        "rules",
        MappingProxyType(dict(sources.declared_role_rules())),
    )
    with pytest.raises(runner.U2RunError, match="role rules"):
        runner.check_inputs(
            frozen_load["inputs"],
            ap.REGISTERED_REAL,
            POINTER,
            registry,
            preregistration_evidence_sha256=frozen_load["sha256"],
            preregistration_evidence=evidence,
        )


def test_a_registered_run_computes_with_a_fresh_role_context(
    frozen_load, evidence, monkeypatch
):
    """Check, then use: the rows get a fresh committed role context, never
    the caller's object, so rules rewritten after the check (here from the
    progress callback) reach no row."""

    caller = sources.RoleContext.from_registry()
    seen = []

    def compute_row(row, inputs, params, births, *, role_context, **kwargs):
        seen.append(role_context)
        raise _Reached

    def progress(message):
        object.__setattr__(
            caller,
            "rules",
            MappingProxyType(dict(sources.declared_role_rules())),
        )

    monkeypatch.setattr(runner, "_compute_row", compute_row)
    with pytest.raises(_Reached):
        runner.run_track_u2(
            frozen_load["inputs"],
            parameters.committed_u2_parameters(),
            data_provenance=ap.REGISTERED_REAL,
            role_context=caller,
            registration_pointer=POINTER,
            preregistration_evidence_sha256=frozen_load["sha256"],
            preregistration_evidence=evidence,
            progress=progress,
        )
    (used,) = seen
    assert used is not caller
    assert dict(used.rules) == dict(sources.RoleContext.from_registry().rules)
