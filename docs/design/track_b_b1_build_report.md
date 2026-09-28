# Track B B1 build report

Built the copied 2014–2018 candidate-3 earnings replay, exact equality checker,
registered runner, lossless annual/scored evidence writer, and issue #42
registration draft. No real-data replay or PSID read was performed. Nothing
was pushed. This is a build and invented-data verification, not an admitted
B1 reproduction or new validation.

## Files

- `src/populace_dynamics/track_b/{__init__,replay,equality,runner}.py`
- `scripts/run_track_b_b1.py`
- `tests/test_track_b_{replay,equality,reference,runner}.py`
- `tests/tier_counts.json`: 45 added unit tests and 21 added artifact-tier
  tests; all new cases use invented inputs. The artifact classification is
  the repository's static path-based classification.
- `docs/design/track_b_b1_registration_draft.md`

The copied loop preserves the original eight-period RNG registry, module
and person coordinates, candidate-3 substreams, fixed domain roster, and
original F6 scoring support. The new exclusive output directory is
`scratch/track_b/b1_v1`. Registered source/runtime checks precede data loading.
Every abort or mismatch retains diagnostics; incomplete runs preserve their
already-written evidence.

Equality covers all five registered split seeds and all 20 draws, every
person-period key and scored column, exact dtypes and scalar bytes, support,
weights, and fitted/RNG signatures. Row and column ordering are immaterial.
There are no numerical tolerances. The runner additionally compares all six
committed earnings cells for each seed/draw and registered fit/input
provenance. Aggregate equality cannot replace person-level equality.

## Tests

```text
.venv/bin/python -m pytest -q --basetemp=.cache/pytest-b1-final \
  tests/test_track_b_replay.py tests/test_track_b_equality.py \
  tests/test_track_b_reference.py tests/test_track_b_runner.py
66 passed in 58.29s

.venv/bin/python -m pytest -q --basetemp=.cache/pytest-b1-regression \
  tests/test_m6_projection_support.py tests/test_m6_engine_steps.py
14 passed in 44.85s
```

Ruff passed and Black formatting was checked for all added Python files.
The CLI `--help` check passed without invoking its input factory. Protected
`engine/loop.py`, `engine/steps.py`, `gates.yaml`, and committed run artifacts
were not changed. No full suite or real-data integration tests were run.

## Open risks and registration

The committed candidate-3 artifact lacks archived person-level outputs and
historical RNG signatures. The default attempt therefore records
`BASELINE_REPLAY_MISMATCH` with
`historical_person_level_reference_unavailable`, even when the original-loop
differential matches. A historical archive may be supplied only with a
registration-authenticated SHA-256 and documented original-run custody.
Newly regenerated rows cannot supply that custody.

The reproduction requires the original pinned fitting environment, not this
build's test environment. Inherited SSA provenance may identify the enclosing
checkout's commit and thus mismatch the old artifact; this is disclosed in
the draft and is not silently normalized. A prospective issue #42 registration
is still required before any real-data computation; none was posted.

## Commit status

No commit SHA was produced. The requested staging/commit step was blocked by
the sandbox at `git add`, before `git commit --no-verify` could execute:

```text
fatal: Unable to create '/Users/maxghenis/PolicyEngine/social-security-model/.git/worktrees/20260928-112535-trackb-b1-build-opus/index.lock': Operation not permitted
```

Git metadata is outside the writable workspace. All changes remain in the
assigned workspace; the base is `9cee2423f048683e15838aa5fee330afd072f85f`.
