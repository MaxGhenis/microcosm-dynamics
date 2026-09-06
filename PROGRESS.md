# Two transitions in one graph — journal

Branch `two-transition-20260906` in
`/Users/maxghenis/PolicyEngine/_worktrees/microcosm-dynamics-two-transition-20260906`,
created from the upstream base `origin/master`
(`96a585511a9bbdaedb7f1d634a5e44269f22d23e`, re-fetched and unmoved) and
then fast-forwarded to the approved dependent head
`2b3c426d344acabcec1f8ba7e6cc18f0ba390d4d`. Every earlier worktree and
branch is untouched — `history-completion-20260906`,
`earnings-history-20260906`, `graph-integration-20260905`, the
architecture-review detached checkout, and `cross-engine-pia` all still
point where they did.

Nothing is pushed. No PR, no merge, no deploy. No genuine PSID, CPS or
candidate file is opened; every input is hand-specified. `runtime.py`,
`earnings.py`, `model.py`, both pinned cores, the Social Security
provenance campaigns and `gates.yaml` are not edited.

## Controlling documents

- `R/microcosm-dynamics-continuation-root-plan-v2.md`
  sha256 `55a5b0e9f979ac45568366541d27bb53131c1c62e4befcaf40039e5186997804`
- `R/microcosm-dynamics-continuation-plan-v2-fable51-review.md`
  sha256 `a10e3907c66f433e619ecaa52882d9a361ff4bc87b61499ef7ef59431e18b403`
- `R/microcosm-dynamics-continuation-root-plan-approval.json` — both
  hashes match the files on disk, verdict `APPROVE_LOCAL_IMPLEMENTATION`.

`R = /Users/maxghenis/architecture-reviews/microcosm-20260904`.

## State

Environment verified, not installed:

- `R/dynamics-extra-env/bin/python` → CPython 3.14.4, numpy 2.5.2,
  pandas 3.0.5. Its `microcosm` is the `3ff92b0a` export.
- `/tmp/policyengine-command-runs/849552ad36e8/dynamics-integration-core-3ff92b0a`
  — 142/142 files hash to `dynamics-integration-core-3ff92b0a-export.json`,
  whose head is `3ff92b0aea14407d09479bff5623dc7d1a92d008`.
- `/tmp/policyengine-command-runs/849552ad36e8/dynamics-integration-core-b55a583f`
  — 148/148 files hash to `dynamics-integration-core-b55a583f-export.json`,
  whose head is `b55a583f078b3d182c65980f24a4d5a119f169bc`.
- The two cores differ in `__init__.py`, `codecs.py`, `executor.py`,
  `keys.py`, `manifest.py` and `README.md`; `b55` also adds
  `attachments.py` and `availability.py`. `decl.py` and `population.py`
  are byte-identical between them.

## Done

- [x] Read the plan, the Fable 5.1 review and the approval; verified both
      recorded sha256 values against the files.
- [x] Read the accepted `R/microcosm-dynamics-history-completion-REPORT.md`
      and the branch's own predecessor journal.
- [x] Fetched `origin`; `origin/master` is `96a5855`, thirteen commits
      behind the approved head and an ancestor of it.
- [x] Created the sibling worktree from `origin/master` and
      fast-forwarded it to `2b3c426`. All originals preserved.
- [x] Verified both pinned core exports file-by-file. Nothing installed.

## Next

- [ ] Compile a tiny invented two-EXPAND graph on both cores before
      writing anything else, to find unsupported compiler or owner
      semantics early.
- [ ] Sibling module with the second application, second EXPAND, second
      age claim and second earnings node.
- [ ] Focused tests; 123 existing checks on both cores.
- [ ] Cold/warm witness, module closure, key comparison, report.
