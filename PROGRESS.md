# Progress — optional earnings-history retention in the population graph

Scope: engineering state/history retention on the existing optional Microcosm
population graph. Not a fitted earnings model, not a statutory Social Security
engine, not calibration, not a locked-gate run.

## State

- Base: `origin/master` `96a585511a9bbdaedb7f1d634a5e44269f22d23e`.
- Dependency commits carried in order onto that base (cherry-pick):
  `fa18064a` -> `db54672`, `538b26fd` -> `c85367a`, `ca8c1d26` -> `97fcd93`.
- Graph/runtime code verified byte-equal to `ca8c1d26` (git blob hashes match
  for all six `graph/*.py` files and `tests/test_graph_mortality.py`).
- Branch `earnings-history-20260906`, worktree
  `_worktrees/microcosm-dynamics-earnings-history-20260906`. Local only.

## Done

- [x] Isolation worktree + dependency composition + byte-equality check.
- [x] Surveyed the existing history utilities; none fits (see below).
- [x] `graph/earnings.py`: typed `populace-dynamics.earnings-path` artifact.
- [x] `graph/runtime.py`: optional `dynamics.earnings.history@1` producer and
      `dynamics.earnings.carry@1` node on the advanced population.
- [x] `graph/synthetic.py` fixtures; `tests/test_graph_earnings_history.py`.
- [x] `docs/population-graph.md` optional-history section.
- [x] 82 checks pass against core `3ff92b0a` (installed) and `b55a583f`
      (source overlay from the microcosm checkout, no install). 0 failures,
      0 errors, 0 skips on both.
- [x] Byte-preservation record for the default no-history run.
- [x] Source-blind guard: no PSID or material microdata read.

## Existing utilities surveyed, and why none was reused

- `ss.benefits.creditable_history` / `indexed_history` / `aime` apply a wage
  base, NAWI indexation, and high-year selection. Statutory, and explicitly
  out of scope here.
- `data.couple_earnings.person_earnings_histories` reads a PSID
  `family_earnings_panel`-shaped frame, filters to ages 14-90, and sums by
  period. It has no representation for an explicit unknown and no
  measurement terms, so a period it drops is indistinguishable from one that
  was never there.
- `engine.steps.apply_earnings` needs a fitted `EarningsGenerator`. That is
  estimation, which this task excludes.

The strict JSON floor (`model.json_bytes`, `parse_json`, duplicate-member
refusal) and the graph plumbing (`_series`, `_periods`, `_Kernel`) are
reused directly; nothing about them is duplicated.

## Remaining

Reported in `R/microcosm-dynamics-earnings-history-REPORT.md`.
