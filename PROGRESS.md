# Earnings-history completion — journal

Child of `6fcbf0a2a5ef3231d8d82016813fcf5b9af89c2d`
(`earnings-history-20260906`), branch `history-completion-20260906`,
created after `git fetch origin`, a clean parent worktree, and a branch
check. Nothing pushed; no PR, merge, or deployment. No genuine PSID or
CPS file opened, no forecast, no statutory calculation, no earnings
model call. Older worktrees, the Social Security provenance, `gates.yaml`
and `runs/` untouched.

## Done

- [x] Read the build prompt, `REPORT.md`, and the Fable 5.1 review
- [x] **Index.** `history()` sorted every row in the path on each call
      and `at()` walked every row; the graph calls both once per output
      row. The artifact is immutable, so it now builds a person index and
      a coordinate index inside the pass that validates the rows.
      `prefix_total` still sums that person's own prefix rows with
      `sum`, not a running total, so its arithmetic is unchanged.
- [x] **Mutable inputs.** Rows and closures are copied into tuples before
      anything is indexed off them. Editing the list afterwards edits the
      caller's list, never the artifact.
- [x] **Reference comparison.** A copy of the pre-index `history`, `at`,
      `people`, `closed_people`, `prefix_total` and `known_total` runs
      beside the artifact's own over signed, known-zero, unknown, absent,
      cancelling and unordered paths, probed at people and periods no
      path holds.
- [x] **Cost evidence, not timings.** 1000 people × 35 periods: a pass
      visits 38,000 rows where it used to visit 105,000,000 and sort all
      35,000 rows 2,000 times. One index build, measured.
- [x] **Docs.** Every person needs an observed row; a pre-closed or
      pre-carried source is refused; the `absent` origin sentinel is in
      the state table; "visible partial failure" replaced by what a
      refusal actually leaves.
- [x] **Fresh-process warm witness.** Two separate processes against one
      store: all nine nodes hit, all nine kernels called zero times, all
      data and artifact bytes equal. Run under both cores.
- [x] **Module closure matched to Git.** 99/99 under `3ff92b0a`,
      101/101 under `b55a583f`.
- [x] **123 checks, 0 skips, on both cores.** 33 graph mortality + 13
      `test_m6_engine_refit.py` + 11 `test_m6_engine_steps.py` (the
      predecessor's 57) + 49 history + 17 new. The 24 engine checks were
      read first: both modules are synthetic and open no file.
- [x] **Tier count.** `unit` 1645 → 1662, the exact 17 added cases.
- [x] `R/microcosm-dynamics-history-completion-REPORT.md` / `.json`,
      test logs and JUnit XML, witness and closure evidence, index
      evidence, preservation evidence, and a separate launcher capture.

## Preserved, and what moved

The default run is byte-identical to the parent's at `6fcbf0a` —
including `report.json` and every node key — because `runtime.py` was not
edited. Under an earnings run exactly two node keys move,
`earnings-history` and `earnings`, since `earnings.py` enters only those
two kernels' hashes through `extra=`. Every mortality node, both seeded
ones included, is unchanged, and all data outputs are byte-identical.

One public behaviour change: `rows` and `closed` read back as tuples
however they were passed, so an artifact built from lists is now equal
to and hashes with the tuple-built one. Serialized bytes, values,
statuses, origins, units and closures are unchanged.

## Not done, deliberately

No new model, no multi-period runner, no larger graph run. The graph
still advances one period, every future value is a declared fixture
input, and the 1000-person evidence is artifact-level. Core
compatibility is observed for two exact revisions, not certified.

## Next

Root reviews the code independently before any integration.
