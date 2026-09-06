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

## Next

- [ ] Survey existing history utilities for reuse.
- [ ] `graph/earnings.py`: typed `populace-dynamics.earnings-path` artifact.
- [ ] `graph/runtime.py`: optional producer + carry nodes on `advance`.
- [ ] Synthetic fixtures + `tests/test_graph_earnings_history.py`.
- [ ] `docs/population-graph.md` optional-history section.
- [ ] Byte-preservation proof for the default (no-history) run.
- [ ] Dual-core test runs (3ff92b0a; b55a583f if available without installs).
