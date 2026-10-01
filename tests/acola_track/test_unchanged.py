"""Keep the legacy registries, constants and consumers unchanged.

Registration 18 ("Build") requires ``cola_track_a``'s ``REGISTERED_ROWS``,
the exercise-1 and exercise-3 constants and ``fra68_track/reform.py``'s
``_check_reform`` to stay byte for byte as they are on ``origin/master``
(75cd35245f1a0c12e7a23b048a7d126c74ad8ecb), and every consumer of them to
behave as before. Each named top-level definition is pinned by the SHA-256
of its exact source text, so an edit to any of them fails here, while
unrelated edits elsewhere in a shared module (another lane's work) do not.
"""

import ast
import hashlib
import importlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "src/populace_dynamics/cola_track_a/config.py": {
        "TRACK_A_LABELS": "edfc53c46358136097a93636f578f05467bc6db85daeac235281a81ef948deb3",
        "INVENTED_COHORT_LABEL": "1480d10e762110cfd2c7ad7b61769732df793d2950f786f8e5d8134384e9d70f",
        "DRY_RUN_HEADER": "3ab3faedef6249f72a282985706377291dd9edfd139ac2336f7920319a17461d",
        "LevelPolicy": "506f5cfa48bf87cd54e757244d068ba0004e3fb8a44101e0b1635ddc8bccbdc6",
        "AuxiliaryEntitlementClock": "456f3b04b28b408663270173069becb27cafb6849336471db1d823ebbad0bee7",
        "SurvivorEntitlementRule": "698c5cd4a57434ea2d40a143e96f442fee9264236f717fe09b4863b800510b17",
        "SpouseEntitlementRule": "256e629fee9255b2eeaf8cae521da7717f56eaad783d27eab04b18689b673c5d",
        "Population": "eaa4a5e455176b4664bc957b3710520c3659e2ff6a4dbe583a96005cf1c64475",
        "POPULATIONS": "c1fe5958a0c4bddd4786190b8a379af75ef65ec9b9ec27df9bbbe2225357dc4b",
        "RegisteredRow": "ca807dd2744459ff18251ab5df3863141cd5d1ff69de569658007c6cb19b62ef",
        "_row": "f18277b6243714cb961d6fb9dafb8034a456322974bab91a2d962302152345fc",
        "REGISTERED_ROWS": "d242cc8f90bead73178226a5149e4d65258ad0611999f842eeb017c1cca5a74a",
        "ROWS_NOT_BUILT": "69e4c2f511b32f64d8ecf81c4bf19b60191d33abf28b2774b7ba97924ca4c2fc",
        "OPENING_STOCK_BASIS": "fddc54ce9f6c3e44814cf000b5631d098fbc43072415fa19faff4bc5bc345fed",
        "TrackAConfig": "e22590d4ff8d521d89dbcaa209af6d551aac857e2d51d3fb6397cd26377b0c9f",
        "MAX_RULINGS": "a138d8a7a231cd98c138003140498b6364a77655718a34f891dc9856715faf66",
        "_RULED_BY": "f9c3c5c1311bbb8d7a9590af6a6d73c67bbf9275cbca089adf93dfa4994eb2c2",
        "max_rulings": "c8aca121bfbf42969fe96b75b8c4ed70b7bd72ba755c33c70e27246ec25f3470",
        "rulings_departures": "9501b49218118053f031e723d91609d20a4f6df22e5c7c3e9949ac5cdfec9517",
        "_A5_BUILDER": "ed32411d591c193f95070741c8484541cda7c71a22ef610626bba3d2b281f0af",
        "_FIXED_BY": "b6c8b2f9b3c1103cb8b3d2691f1a3eb66a2caf86355346dbb7709e0865242994",
        "builder_defaults": "c3f576b9cf530068cec73233462c7396380643400122067594ae555b72779eb4",
    },
    "src/populace_dynamics/fra68_track/config.py": {
        "STATISTIC_ID": "6ffe2f88c0d3325fb3dc517e043433f188818c8cf53200b6ee927aa9afd4d343",
        "SPECIFICATION_ID": "28e093f508a7f38415e92010f1bc8a83fda5f434dce34053c6014699c8345835",
        "DRY_RUN_HEADER": "3ab3faedef6249f72a282985706377291dd9edfd139ac2336f7920319a17461d",
        "FRA68_LABELS": "f85c189c6b3a6aad93c321c002e6c424ff1157ea004c503d7beac8ca13010633",
        "MECHANICAL_INCIDENCE_LABEL": "0e9a523dc26e8dd233f6d53737d7954a46fce75a812c5bb0ca6000f8ec2477c9",
        "STYLIZED_RESPONSE_LABEL": "3da1a2682133f5e17eba82e80b57df6e30f4625ea08162558c303d628dfcb63e",
        "TRACK_A_ROW_BY_WAVE": "409f9e81efb315dcc29411188b3d60a43e4923aa316f9289353240b465c44db1",
        "FRA68Row": "428f7292e9befe32c11433c420baedfc167decc19582f207d3e5fa9de6aa770c",
        "registered_rows": "7f99d64c2f80cee7d032de5d2520c34a7b9f78d431012a1b3052d7484bbc073d",
        "SURVIVOR_REDUCTION_SPAN": "c907ff3fd15875d32a0878e677725f0ac74e98e51fdb325236a3d9091cf3252b",
        "TRACK_A_SURVIVOR_REDUCTION_SPAN": "5505660b5146e4fed3c88c35db3d1b537cc183c7047188cd3bb1949223a8110b",
        "RULED_ON": "54986e85f5ffb1c789e3def27edbd55a2b74031697e2918fd6dfb69036c01e52",
        "_RULED_BY": "1ea8757f1c550e674c001a8f03409f76ae738bec8c6a01801b9b2f3e89861006",
        "MAX_RULINGS": "9761d102aef05895e1d40e79684d97b8b39ace406d324af7d311d0118900d0c9",
        "E1_RATIFICATION": "3d019b045ac8c06856bb088084ef166238f6276574878f384852aa14644c4702",
        "E1_RULINGS": "629cb2668d3cf1f066e1f0092fc2f376b75e5f92ace0a3bad94a2485b94367e9",
        "FRA68Config": "c6cc8fb08ebfb8acd5a4f1ae9fba1f679f45a52e63fd4f8fb05be36b8fabe58b",
        "builder_defaults": "a2a524befbe0bff76af820e6b2d383c2b4d6a2b83a68592d4778eba1ac84bb75",
    },
    "src/populace_dynamics/fra68_track/reform.py": {
        "_check_reform": "c75276021d694c55718b7855444b6c2de4ee6dbf87077b29278119c9b70b346d",
        "WORKER_EARLY_RETIREMENT_AGE": "abbc2504aa9ccfb5965c4d2241f455d3a3f88750be3b642f5631224d8adca0ac",
        "AGE_62_MONTHS": "b7c185593f539186748852a5a30eaa617875e70cfb350f8536315c3641e3161b",
        "AGE_70_MONTHS": "26266072b24407e5b74b2e227ab2fec91b0e7f079306b0dadfec15f90a08bc98",
        "BASE_FRA_MONTHS": "131c09c7224e65934f1adcba9a62e5d0655fcc0d4e3421731fa47b0e652f4b50",
        "LAST_UNCHANGED_YEAR": "c921759be385a55c323196d1809ed99b5a38c70228033f90bce3365d8b097378",
        "FIRST_OPTION_YEAR": "0901c8a76bcc9b1091b3e6314c72d02c39017cd9268af284770fb07914fabb1c",
        "FINAL_YEAR_TURNING_62": "af1f413096b29d3c402dc598d28237b5aa4d30f6b294a394973e52fde40bc46b",
        "TARGET_FRA_MONTHS": "442c3c02d5190e456cafcf4d058793f954173f34624adf37f339c80dd1657a2e",
        "_GUARD_BIRTH_YEARS": "3d3714719ab550bdf1ede80bad22a4b37e2785c6a03ffb545cb97c4c6cccab67",
    },
}
# The legacy rows' registered fields at origin/master, as values.
LEGACY_ROWS = {
    "R0": (None, 2009, "eligibility", "calendar_year", 5, 2011),
    "R1": (
        "first_reduced_increase",
        2010,
        "eligibility",
        "calendar_year",
        5,
        2011,
    ),
    "R2": ("exposure_clock", 2009, "entitlement", "calendar_year", 5, 2011),
    "R3": ("statistic", 2009, "eligibility", "calendar_year", 5, 2011),
    "R4": ("benefit_period", 2009, "eligibility", "december", 5, 2011),
    "R5": ("components", 2009, "eligibility", "calendar_year", 2, 2011),
    "R6": (
        "population_and_vintage",
        2009,
        "eligibility",
        "calendar_year",
        5,
        2009,
    ),
}


def _definitions(path):
    source = (ROOT / path).read_text(encoding="utf-8")
    found = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef | ast.ClassDef):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(
            node.target, ast.Name
        ):
            names = [node.target.id]
        else:
            continue
        segment = ast.get_source_segment(source, node)
        for name in names:
            found.setdefault(name, []).append(segment)
    return found


@pytest.mark.parametrize(
    ("path", "name"),
    [(path, name) for path, names in PINS.items() for name in names],
)
def test_registries_constants_and_check_reform_are_byte_unchanged(path, name):
    segments = _definitions(path).get(name, [])
    assert len(segments) == 1, f"{name} must be defined once in {path}"
    digest = hashlib.sha256(segments[0].encode("utf-8")).hexdigest()
    assert digest == PINS[path][name]


def test_importing_acola_leaves_the_legacy_registry_equal_by_value():
    from populace_dynamics.cola_track_a import config as legacy

    before = dict(legacy.REGISTERED_ROWS)
    acola = importlib.import_module("populace_dynamics.acola_track.config")
    importlib.import_module("populace_dynamics.acola_track.runner")
    assert legacy.REGISTERED_ROWS == before
    assert set(legacy.REGISTERED_ROWS) == set(LEGACY_ROWS)
    assert not set(acola.REGISTERED_ROWS) & set(legacy.REGISTERED_ROWS)
    for row_id, expected in LEGACY_ROWS.items():
        row = legacy.REGISTERED_ROWS[row_id]
        assert (
            row.field_changed,
            row.first_reduced_determination_year,
            row.exposure_clock.value,
            row.benefit_period.value,
            len(row.components),
            row.anchor_wave,
        ) == expected
    assert legacy.ROWS_NOT_BUILT == {}
    assert legacy.TrackAConfig().rows == tuple(LEGACY_ROWS)


def test_track_a_v2_matrix_and_runner_consume_the_same_rows():
    from populace_dynamics.cola_track_a.config import REGISTERED_ROWS
    from populace_dynamics.track_a_v2.matrix import MATRIX
    from populace_dynamics.track_a_v2.runner import JointConfig

    assert len(MATRIX) == 68
    for entry in MATRIX:
        if entry.row_id.startswith("R"):
            assert entry.source_row is REGISTERED_ROWS[entry.row_id]
    assert JointConfig().track_a().rows == tuple(f"R{i}" for i in range(6))


def test_the_dry_run_rate_check_still_accepts_every_legacy_row():
    from populace_dynamics.cola_track_a.runner import tr2008_baseline_cola
    from populace_dynamics.estimates.parameters import load_cola_history

    spec = importlib.util.spec_from_file_location(
        "acola_legacy_dry", ROOT / "scripts/track_a_dry_run.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._spec_rate_check(tr2008_baseline_cola(load_cola_history()))
