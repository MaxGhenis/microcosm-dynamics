# Current root disposition — September 6, 2026

The mortality identity increment is complete as local engineering work at
source/test revision `3cff20def97e793394db0225cd6264b180463d09`. Root reviewed
adapter blob `c9cc6f1e71fab96ef830d7e7b434ee216f1a96c8`; Fable 5.1 accepted
the final source and identity pin. The earlier instruction below to review
`c7f4450` is historical and superseded. The signed-ID guard and line-anchor
corrections are included, and the historical source seal passes.

Root evidence: 66 focused tests before pinning, 9 post-commit seal tests, and
the tier-policy test after full collection of 5,940 items. Collection evidence
records `3acb92d`; the sole next commit `3cff20d` refreshes the tier manifest,
which was then tested against a new full collection. No full test-suite run
is claimed. The previous lane's 307/315 test-count discrepancy is unresolved;
these root checks are the evidence used here.

Real mortality fitting remains pending scientific source decisions on weight
universes, non-exact death years and nonresponse censoring. No PSID microdata,
forecast, historical run, registered gate or sealed corpus was changed. No
push, remote merge or publication occurred. Next work must address those
source decisions before a genuine fit; this journal is not fit approval.

---

# Review-fixes lane: R2-R5 on the mortality-identity capture

**Scope.** Fable review
`architecture-reviews/microcosm-20260904/dynamics-mortality-identity-fable51-capture.md`
found nine items (R1-R9) against the mortality-identity lane
(`microcosm-dynamics-mortality-identity-20260906`, HEAD
`856c6c62a46ed8dd44e43753b099005f80efadd9`). This lane fixes only the four
low-severity, non-blocking items: **R2, R3, R4, R5**. R1 (the birth-evidence
source-identity seal) is explicitly **not** fixed here — see "R1, not
repaired" below. R6-R9 are Info-severity findings the review says need no
fix.

Local only. No PSID microdata read, no genuine fit run, no forecast, no
broad test sweep, no nested agents, no remote write of any kind.

## State

- Parent worktree confirmed at `856c6c62a46ed8dd44e43753b099005f80efadd9`
  (verified via `git log -1`).
- `git fetch origin` compared against `origin/master`
  (`5b9621fe07e0afbc102d3cab9d8b34c20fe2dd13`, the maintained upstream
  default branch — confirmed via `git remote show origin`): parent is 29
  commits ahead, 0 behind (`merge-base` == `origin/master` tip). No
  divergence; safe to branch without a rebase.
- Child worktree created at
  `/Users/maxghenis/PolicyEngine/_worktrees/microcosm-dynamics-mortality-review-fixes-20260906`,
  branch `microcosm-dynamics-mortality-review-fixes-20260906`, from the
  parent's exact commit. All eight pre-existing worktrees (including the
  identity lane, the C20/graph-shadow lanes, and every other active branch)
  left untouched — `git worktree list` re-verified after creation.
- `git config core.hooksPath /dev/null` set in this worktree; every commit
  below additionally passes `--no-verify`.

## Done

- **R2** (`docs/design/m6_projection_engine.md`) — appended a new
  "2.8.10.6 Amendment 3j" section at the true end of the file describing
  the eight-column `MORTALITY_EXPOSURE_COLUMNS` shape. Line 3115 (the
  seven-column pin) and every line before the appended section are
  byte-identical to before — verified by re-reading line 3113-3116 after
  the edit and by the file growing from 4261 to 4326 lines (pure append,
  65 lines, all after the prior EOF).
- **R3** (`scripts/registered_m6_inputs.py`,
  `assert_unique_person_years`) — the duplicate-key diagnostic no longer
  calls `int(pid)` on each offending key (which raised `ValueError:
  cannot convert float NaN to integer` or a base-10 parse error for a
  malformed id, masking the intended message). It now takes `repr()` of
  each raw key, bounded to the first five via `itertools.islice`, before
  they ever reach a numeric cast. Added
  `test__unique_person_years__reports_a_malformed_key_without_crashing`
  (NaN and a non-numeric string id) — fails under the old code, passes now.
- **R4** (`scripts/registered_m6_inputs.py`,
  `_pad_below_25_projection_coverage`) — replaced the `pd.to_numeric(...,
  errors="coerce")` guard (which silently accepted digit strings and
  whole-number floats) with a `pandas.api.types.is_integer_dtype` check,
  plus a separate `isna()` check for a missing value under a nullable
  integer dtype. Verified empirically in the pinned interpreter that
  `is_integer_dtype` is `False` for bool, `str`-cast, fractional-float, and
  complex128 Series, and `True` for `int64` and nullable `Int64`. Added
  five new tests: a parametrized dtype-rejection test (boolean, numeric
  string, fractional float, complex), a missing-value (`pd.NA` under
  `Int64`) rejection test, and a valid-int64-passthrough test. All 16
  pre-existing pad/adapter tests still pass unmodified — the legacy
  seven-column path and every valid `int64` id are unaffected (confirmed
  by `test__identity__does_not_move_a_single_fitted_probability`, already
  in the suite and still green).
- **R5** — two independent fixes:
  1. `test__unique_person_years__passes_an_id_free_frame_through`
     (`tests/test_registered_m6_inputs.py`) compared the function's return
     value against the same object passed in (the function returns its
     argument unchanged by design), so the assertion was tautological.
     Now takes `frame.copy()` before the call and compares the result
     against that independent copy.
  2. `test__graph_training_kernel__refuses_numpy_identifiers`
     (`tests/test_registered_m6_training_source.py`) feeds a Python
     `float`, not a numpy scalar (the docstring already said so — `json.dumps`
     would fail on a real numpy scalar before the kernel saw it). Renamed to
     `test__graph_training_kernel__refuses_a_float_identifier`.
- `black -l 79` and `ruff check` clean on all four changed files (same
  versions the identity lane's report recorded: black 25.11.0, ruff
  0.15.0 — run from the system PATH, not the pinned test env, since
  neither tool is installed there and it must not be modified).
- Relevant tests green in the pinned env
  (`architecture-reviews/microcosm-20260904/dynamics-extra-env`, CPython
  3.14.4 / numpy 2.5.2 / pandas 3.0.5 — module identity checked via
  `__file__`, resolves to this worktree):
  `tests/test_registered_m6_inputs.py` +
  `tests/test_registered_m6_training_source.py` — 62 passed, 0 failed
  (43 + 12 baseline + 7 new R3/R4 regression tests).
  Widening to the same graph-serialization/adapter set the identity
  lane's report exercised (`test_graph_mortality.py`,
  `test_graph_two_transition.py`, `test_graph_earnings_history.py`,
  `test_graph_earnings_index.py`, `tests/estimates/test_coordinator.py`,
  `test_registered_m6_candidate2_inputs.py`,
  `test_covered_earnings_membership_adjudication.py`): 306 passed, 1
  failed pre-commit (`test__registered_input_factory__pins_complete_production_source_chain`,
  which diffs the **working** file against the **committed HEAD blob** —
  expected to go green once this lane's commits land, since it is a
  working-tree-vs-HEAD check, not a logic bug). Re-verified green after
  committing (see "Verification after commit" below).
- Seven-column numeric parity re-demonstrated post-fix (not just inherited
  from the identity lane): `test__identity__does_not_move_a_single_fitted_probability`
  and `test__identity__does_not_move_the_prepared_row_count` (both
  pre-existing, unmodified) are in the green run above; they compare the
  seven-column and eight-column fits byte-for-byte on the fourteen-cell
  fixture. No fitted number changed by R3, R4, or R5 (R3/R4 only add
  raise branches on malformed input; the well-formed path is untouched
  code).

## R1, not repaired

Per the review and this task's explicit scope: R1 (the birth-evidence
source-identity seal, already red at the identity lane's HEAD for three
unrelated graph modules, and made red-for-a-fourth-reason by
`scripts/registered_m6_inputs.py` being a reviewed-but-now-edited reducer
input) is **not** fixed in this lane. No blob pin was added to
`POST_REVIEW_SHARED_SOURCE_BLOBS`, no exclusion added, no xfail, no
blanket exemption. The seal is left exactly as red as it was at the
identity lane's HEAD, now for the same reason (a fourth differing path) —
confirmed by re-running the seal test at this lane's HEAD (see
"Verification after commit").

A separate reviewable artifact is written for root:
`architecture-reviews/microcosm-20260904/dynamics-mortality-review-fixes-seal-repair-option-c.md` —
the proposed corrected source blob (this lane's final
`scripts/registered_m6_inputs.py`, sha256 recorded) plus the minimal
diff root would apply to `first_estimates_birth_evidence.py`'s exclusion
tuple and `POST_REVIEW_SHARED_SOURCE_BLOBS`, and to
`tests/estimates/test_birth_evidence_artifact.py`'s literal pin — for root
to apply **after** root independently reads the corrected source. This
lane does not apply that patch itself.

The three optional graph modules named in the review's seal-repair option 1
(`graph/earnings.py`, `graph/two_transition.py`,
`graph/two_transition_synthetic.py`) were checked for non-reachability
using the existing seal's own reachability test
(`tests/estimates/test_birth_evidence_artifact.py`, the test deriving graph
modules from the tree) — see the seal-repair artifact for the exact
command and result. Nothing about the reviewed commit, historical runs,
gates, or fixtures was changed to perform that check.

## Verification after commit

Four commits landed, oldest first:

| Commit | Subject |
|---|---|
| `364d9c3e036d365a4136e33bc71da0d626491476` | Report malformed duplicate person-year keys instead of crashing on them (R3 + first half of R5) |
| `85ac265972666d8c1351a077384dd22b00e24384` | Require an integer person_id dtype before the mortality pad reserves ids (R4) |
| `1c55cc800f12b2700a0aefe8d72aa861e75acd34` | Rename the training-kernel test that actually feeds a float, not a numpy scalar (second half of R5) |
| `284c3c2f2aa2d784545329bd24e4668234fb99f7` | Append the eight-column adapter shape as a design-note amendment (R2) |

All local, hooks disabled (`git -c core.hooksPath=/dev/null commit
--no-verify`), messages verified by reading them back with `git log -1`.
`git diff --stat 856c6c62a46ed8dd44e43753b099005f80efadd9 HEAD` (excluding
this file) touches exactly the four files listed under "Done" — nothing
else; `git diff --quiet ... -- gates.yaml runs/` confirms both untouched.

With the working tree clean at this HEAD:

- `tests/test_registered_m6_inputs.py` + `tests/test_registered_m6_training_source.py`
  + the graph-serialization/adapter set
  (`test_graph_mortality.py`, `test_graph_two_transition.py`,
  `test_graph_earnings_history.py`, `test_graph_earnings_index.py`,
  `tests/estimates/test_coordinator.py`,
  `test_registered_m6_candidate2_inputs.py`,
  `test_covered_earnings_membership_adjudication.py`): **307 passed, 0
  failed** — the one pre-commit failure
  (`test__registered_input_factory__pins_complete_production_source_chain`)
  is green now that the working file matches the committed HEAD blob, as
  predicted.
- `tests/estimates/test_birth_evidence_artifact.py`: **8 passed, 1
  failed** — `test_reducer_input_identity_matches_reviewed_branch` fails
  with `RuntimeError: production sources differ from the reviewed
  implementation`, the same failure mode as at the identity lane's HEAD,
  now additionally true of this lane's edited
  `scripts/registered_m6_inputs.py`. This is the intended, undisturbed R1
  state.
- The three optional graph modules
  (`graph/earnings.py`, `graph/two_transition.py`,
  `graph/two_transition_synthetic.py`) were confirmed present in the tree
  and unreachable from the birth-evidence reducer by re-running the
  existing, unmodified `test_psid_and_graph_exclusions_are_unreachable_from_birth_evidence`
  helper functions inline — full detail and output in the seal-repair
  artifact.

## Next

- Root reads the corrected `scripts/registered_m6_inputs.py` bytes
  (git blob `c7f4450292c254998b33796d1c7ba167bfc8aede`, sha256 in the
  seal-repair artifact) and, if satisfied, applies the seal-repair patch
  and/or the three-graph-module exclusion independently. Not this lane's
  job.
- No push, no PR, no merge — none planned from this lane.
