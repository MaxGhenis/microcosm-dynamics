# Mortality-exposure person identity — journal

Branch `microcosm-dynamics-mortality-identity-20260906` in
`/Users/maxghenis/PolicyEngine/_worktrees/microcosm-dynamics-mortality-identity-20260906`.

The previous lane's journal (two transitions in one graph) is not deleted:
it is preserved in git history at `1a370c6`, which is this branch's second
parent. This file follows the repository's one-journal-per-lane convention.

## Lineage, measured

Commands run in this worktree, output quoted from the terminal:

- `git fetch origin --prune` moved `origin/master` `96a5855..5b9621f`.
- **Upstream base**: `origin/master` =
  `5b9621fe07e0afbc102d3cab9d8b34c20fe2dd13`
  ("Progress dashboard: 2026-09-06 morning refresh …", #428).
- **Accepted frozen candidate**:
  `1a370c6c9da2c4b0c5a354c33315fc4c8d9e9e74` ("Close the two-transition
  lane's journal"), read-only; its worktree
  `_worktrees/microcosm-dynamics-two-transition-20260906` is not edited by
  this lane.
- `git merge-base 1a370c6 origin/master` =
  `96a585511a9bbdaedb7f1d634a5e44269f22d23e`. Neither is an ancestor of the
  other.
- **Remote delta, entire**: one commit `5b9621f`, two files,
  `docs/progress.md` (+2/−1) and `docs/progress/progress.json` (+5/−1).
  No source, test, script, `gates.yaml` or `runs/` path. It is carried
  plainly by merge, not reinterpreted.
- **This branch** starts at `5b9621f` and merges `1a370c6` at
  `9cac76a6d48e49579e9251f6ce4c8702a8e00716` (no-ff, no conflict; the
  candidate's 21 changed paths do not intersect the two docs paths).
- `git diff --stat 1a370c6 9cac76a6` = exactly `docs/progress.md` and
  `docs/progress/progress.json`. Every source file on this branch is
  byte-identical to the accepted head before this lane's own edits.

Unrelated source work is preserved: nothing outside this branch was
touched, and the merge is additive over the accepted candidate.

## Controlling documents read this session

`R = /Users/maxghenis/architecture-reviews/microcosm-20260904`

- `R/dynamics-panel-contract-fable51-capture.md` — F1, F2, F7 are this
  lane's scope; F3, F4, F5 are recorded as blockers, not implemented.
- `R/dynamics-genuine-panel-preparation/REPORT.md` — the N1 statement and
  the refusal record.
- `R/microcosm-dynamics-two-transition-root-acceptance.json` — the
  accepted head and its four stated limits.
- `R/claude-dynamics-population-adapter-coordination-20260906.md` — the
  ceremony lane holds no change to `scripts/registered_m6_inputs.py`,
  `engine/refit.py`, `tests/test_registered_m6_inputs.py` or
  `data/family.py` in any of its 122 worktrees.

## Environment, measured

- `R/dynamics-extra-env/bin/python` — CPython 3.14.4, numpy 2.5.2,
  pandas 3.0.5. Reused, **not** modified or upgraded.
- Module identity is bound to *this* worktree, not to any installed
  editable package. Verified by printing `__file__`:
  `populace_dynamics`, `populace_dynamics.engine.refit`,
  `populace_dynamics.graph.runtime`, `registered_m6_inputs` and
  `build_mortality_floors` all resolve under
  `_worktrees/microcosm-dynamics-mortality-identity-20260906`.
  (The env's `site-packages` contains an unrelated `populace_dynamics`
  copy; `PYTHONPATH=$W/src:$W/scripts` precedes it in `sys.path`.)

Invocation used for every run in this lane:

```bash
W=/Users/maxghenis/PolicyEngine/_worktrees/microcosm-dynamics-mortality-identity-20260906
E=/Users/maxghenis/architecture-reviews/microcosm-20260904/dynamics-extra-env
PYTHONPATH=$W/src:$W/scripts $E/bin/python -m pytest …
```

## Scope

**In**, from the Fable 5.1 capture:

- **F1** — the adapter drops `person_id` after using it as a merge key;
  retain it, and give the two `(0, 24)` coverage pad rows distinct
  reserved negative ids so the pad cannot become a NaN id.
- **F2** — a repository test pins the seven-column list exactly; update it.
- **F7** — the graph's `external_vintage_year` default is 2014 while the
  M6 artifact records 2010; a fixture test pins the mismatch so it cannot
  be met by accident.

**Out, and why** — recorded as blockers to a scientifically admitted fit,
not deferred with a disclosure:

- **F3** weight-series population definition changes at 1997.
- **F4** known deaths with non-exact years are scored as full survival.
- **F5** nonresponse has no declared ascertainment/censoring convention.

Also unchanged in this increment: the weight-series choice, the mortality
floor, fitted probabilities, holdout scope, and the graph training schema.

## Done

- [x] Read the four controlling documents.
- [x] Inspected `CLAUDE.md` (no `AGENTS.md` in this repository), git
      status (clean), branch, remotes.
- [x] Fetched `origin`, compared the accepted candidate to the latest base.
- [x] Created this branch/worktree from `5b9621f`; merged `1a370c6` at
      `9cac76a6`.
- [x] Verified module identity binds to the edited paths.
- [x] Baseline: `tests/test_registered_m6_inputs.py` 31 passed; fitted
      probabilities and pad rows on the invented fixture captured before
      any edit.

- [x] F1/F2 patch (`860f75e`): `person_id` retained as the adapter's
      leading column; reserved ids `-1`/`-2` on the two `(0, 24)` pad rows,
      emitted only when the input already carries identity; the seven-column
      pin becomes an eight-column pin.
- [x] Non-collision argument, and its runtime guard: a negative observed
      `person_id` raises rather than colliding.
- [x] `assert_unique_person_years` reports repeated
      `(person_id, event_year)` with a count and up to five keys.
- [x] `PAD_IDENTITY_DISCLOSURE` in the module; a test asserts what it says.
- [x] F7 bridge tests (`abd1293`): eight fields, Python `int` ids,
      `external_vintage_year=2010` vs the graph's 2014 default.
- [x] Cited line spans preserved (`ba9c16a`): nothing is inserted
      above line 238 of the adapter -- see below.
- [x] Focused tests, format (black -l 79), lint (ruff): clean.

## Measured evidence

- **Fitted numbers do not move.** On the committed fourteen-cell invented
  fixture, with and without identity, compared against values captured
  before any edit: 8 bands, all 16 probabilities, 16 prepared rows and both
  pad rows identical. The adapter's 8 rows are identical to the pre-patch
  rows once the added key is dropped.
- **Focused run**: 308 passed, 3 skipped, 1 failed.
  - The 3 skips are `test_registered_m6_inputs_oracle.py` -- policyengine-us
    1.752.2 is not importable in this environment, which is the oracle tier.
  - The 1 failure is **pre-existing** -- see below.
- `tests/test_registered_m6_inputs.py` 31 -> 43; new module
  `tests/test_registered_m6_training_source.py` 12. Collection over the two
  modules: 31 -> 55, so `tier_counts.json` unit 1711 -> 1735.

## Two things found on the way, neither caused by this lane

**1. The birth-evidence source-identity seal is already broken at the
accepted head.** `tests/estimates/test_birth_evidence_artifact.py::
test_reducer_input_identity_matches_reviewed_branch` fails at `1a370c6`
itself -- measured by running it in a throwaway detached worktree at that
exact commit, not deduced. `first_estimates_birth_evidence.
_assert_input_identity` diffs `PRODUCTION_SOURCE_PATHS` (which includes all
of `src/populace_dynamics`) between the reviewed commit `1c7f354` and HEAD,
minus `POST_REVIEW_SOURCE_EXCLUSIONS`. Three modules the accepted candidate
added are inside the sealed path and absent from the exclusions:

- `src/populace_dynamics/graph/earnings.py`
- `src/populace_dynamics/graph/two_transition.py`
- `src/populace_dynamics/graph/two_transition_synthetic.py`

Their siblings (`__init__.py`, `__main__.py`, `_compat.py`, `model.py`,
`runtime.py`, `synthetic.py`) *are* excluded, by commit `c85367a` "Keep
optional graph outside historical birth evidence scope" -- so this reads as
three files that commit missed. The seal is green at `origin/master`
(`5b9621f`) and at `96a5855`.

This lane's edit to `scripts/registered_m6_inputs.py` adds a **fourth**
differing path to the same already-red check. It is **not repaired here**:
that file is a reviewed reducer input, not a post-review addition, so
excluding it or pinning its new blob is a root decision about what the seal
covers, and pinning a blob would assert a re-review that has not happened.

**2. Six citations anchor to line numbers inside the adapter.**
`registered_inputs_staging_law` (48-51) in
`scripts/build_covered_earnings_membership_adjudication.py`, design-doc
pointers at 125-137, 184-235 and 238 (twice), and a committed incident
record at 173. An earlier draft of this patch added seven lines to the
module docstring, which silently repointed five of the six while every test
stayed green. The note was moved below the constants: lines 1-238 are now
byte-identical to the accepted head and the first changed line is 318.

## Next

- [ ] Report to `R/dynamics-mortality-identity-REPORT.md` / `.json`.
- Root reviews, then sends to Fable. Nothing is pushed.

## Standing limits, restated

No PSID microdata was read. No genuine fit was executed. No forecast, no
mortality accuracy, no Social Security quantity is validated or claimed.
Nothing is pushed, no PR, no merge, no publication. The Claude shadow
graph, the C20 ceremony objects, `gates.yaml` and the committed `runs/`
artifacts are untouched.
