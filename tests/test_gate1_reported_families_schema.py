"""The reported families add exactly one key to the gate-1 per-seed schema.

The shared per-seed scorer :func:`run_gate1_candidate10.run_seed` writes the
block that publishes the registered-but-unreferenced battery families. Its
per-seed storage is a documented shape, pinned by candidate 11's own prose
against the committed candidate-10 artifact, so the addition has to be exactly
one new sibling and nothing else -- no gated block renamed, reordered, or
dropped.

The comparison runs on the parsed runner (no fitted model, no staged PSID) and
the committed artifact's own bytes, so it holds at every checkout. Key ORDER is
reconstructed the way the interpreter builds it: the ``result`` dict literal in
source order, then the conditional ``result[...] = ...`` writes in source
order -- not sorted, which would let a reordering of those writes pass.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CANDIDATE10_ARTIFACT = ROOT / Path("runs") / "gate1_rank_knn_v4.json"

#: The one key the reported families add to the per-seed schema.
ADDED_KEY = "reported_not_gated"

#: The last GATED key of the dict literal. The reported block is written
#: immediately after it -- which is NOT last overall, because ``run_seed``
#: then conditionally writes the three benefit-space keys.
LAST_GATED_LITERAL_KEY = "battery_pass"


def _run_seed_tree() -> ast.FunctionDef:
    tree = ast.parse(
        (SCRIPTS / "run_gate1_candidate10.py").read_text(encoding="utf-8")
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_seed":
            return node
    raise AssertionError("run_seed not found")


def _result_literal(run_seed: ast.FunctionDef) -> ast.Dict:
    for node in ast.walk(run_seed):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "result" for t in node.targets
        ):
            assert isinstance(node.value, ast.Dict)
            return node.value
    raise AssertionError("the per-seed result dict literal was not found")


def _produced_keys() -> list[str]:
    """The per-seed keys in the order the interpreter inserts them."""
    run_seed = _run_seed_tree()
    literal = [key.value for key in _result_literal(run_seed).keys]
    conditional = [
        (node.lineno, node.slice.value)
        for node in ast.walk(run_seed)
        if isinstance(node, ast.Subscript)
        and isinstance(node.ctx, ast.Store)
        and isinstance(node.value, ast.Name)
        and node.value.id == "result"
        and isinstance(node.slice, ast.Constant)
    ]
    # Source order, so reordering the conditional writes is visible here.
    conditional.sort()
    return literal + [key for _, key in conditional]


def _committed_per_seed_keys() -> list[str]:
    artifact = json.loads(CANDIDATE10_ARTIFACT.read_text(encoding="utf-8"))
    return list(artifact["per_seed"][0])


def test_the_per_seed_schema_gains_exactly_the_reported_block():
    produced = set(_produced_keys())
    committed = set(_committed_per_seed_keys())

    assert produced - committed == {ADDED_KEY}
    assert committed - produced == set()


def test_no_gated_per_seed_block_was_reordered_or_renamed():
    """Every committed key keeps its name AND its insertion position."""
    kept = [key for key in _produced_keys() if key != ADDED_KEY]
    assert kept == _committed_per_seed_keys()


def test_the_reported_block_sits_between_the_battery_and_benefit_space():
    """It is not last: three benefit-space keys are written after the literal.

    Pinning the true position, rather than the convenient claim that it is
    appended, is what keeps this test honest about the emitted artifact.
    """
    produced = _produced_keys()
    index = produced.index(ADDED_KEY)

    assert produced[index - 1] == LAST_GATED_LITERAL_KEY
    assert index != len(produced) - 1
    assert produced[index + 1 :] == [
        "benefit_space",
        "benefit_space_checks",
        "benefit_space_seed_pass",
    ]


# --------------------------------------------------------------------------
# The artifact-level key must not collide with the repo's boolean marker
# --------------------------------------------------------------------------
#: At artifact top level, a bare ``reported_not_gated`` is this repository's
#: BOOLEAN marker meaning "this whole artifact reads no gate". A gate
#: artifact is precisely the thing that does read a gate, so the run-level
#: block is named ``reported_not_gated_families`` instead. The PER-SEED
#: blocks keep the bare name, where no such convention exists.
RUN_LEVEL_KEY = "reported_not_gated_families"


def _artifact_dict(module: str) -> ast.Dict:
    tree = ast.parse((SCRIPTS / module).read_text(encoding="utf-8"))
    run = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "run"
    )
    assign = next(
        node
        for node in ast.walk(run)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == "artifact"
            for t in node.targets
        )
    )
    assert isinstance(assign.value, ast.Dict)
    return assign.value


def test_no_runner_writes_a_bare_reported_not_gated_at_artifact_top_level():
    """Reusing the boolean marker would invert it on the gate's own artifact."""
    for module in (
        "run_gate1_baseline.py",
        "run_gate1_candidate10.py",
        "run_gate1_candidate11.py",
    ):
        keys = [
            key.value
            for key in _artifact_dict(module).keys
            if isinstance(key, ast.Constant)
        ]
        assert ADDED_KEY not in keys, module
        assert RUN_LEVEL_KEY in keys, module


def test_the_boolean_marker_convention_this_avoids_still_exists():
    """If the convention ever disappears, this guard should be revisited."""
    producers = 0
    for path in sorted(SCRIPTS.glob("*.py")):
        producers += path.read_text(encoding="utf-8").count(
            '"' + ADDED_KEY + '": True'
        )
    assert producers > 20, producers
