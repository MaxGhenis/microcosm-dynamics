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

## Probe: the shape compiles on both cores

`R/microcosm-dynamics-two-transition-verify/probe_two_expand.py` builds a
tiny invented graph that imports no `populace_dynamics` code at all. It
declares two chained EXPAND versions over an invented `cell` entity, a
node in the second version rewriting a cell owned in the first version's
members, a node in the third version rewriting a cell owned in the
second's, a same-version full-row claim on each expansion, an artifact
edge from a node in one version to a node in the next, a failing gate in
the middle version, and a declared mass receipt whose base already holds
two partitions.

It compiles and runs on both pinned cores. The receipts
(`probe-two-expand-3ff.json`, `probe-two-expand-b55.json`) are
byte-identical apart from the label. What that establishes:

- Version ownership across a chained expansion is accepted. `step1`'s
  `alive`/`p` are owned by the second-version node, `step2`'s `e` by the
  third-version node, exactly as the plan's second application and second
  earnings nodes need.
- There is no cycle. The order is create, mark, step1, claim1, remark,
  gate, produce, step2, claim2, consume, and `step2` depends on every
  ordinary member of `step1` including the gate.
- One registered claim kernel serves both claims by ref. The probe
  registers `probe.claim@1` once and names it from two nodes, which is
  the reuse Fable's note 4 requires.
- A failed gate is a receipt, not a stop. `gate` returns
  `outcome: fail` and `consume` still runs and still writes its artifact.
- A declared mass receipt over a base holding two partitions is accepted;
  the ledger holds two records.

Two probe defects were mine and were fixed in the probe, not in any
core: the population view exposes no `mass_ledger` attribute (the
manifest does, keyed by version), and a node receipt holds a
`mappingproxy` that plain `json.dumps` will not encode.

## The sibling module

`src/populace_dynamics/graph/two_transition.py` calls
`runtime.build_graph`, keeps every node, kernel and source it returns,
and adds four nodes, three kernels and one source:

| node | version | what it does |
|---|---|---|
| `apply2` | `advance` | applies the same fitted law at the 2015 rows, rewriting `survives` and `death_probability` and preserving 2014 |
| `advance2` | its own | copies 2015 survivors to 2016 with a declared multiyear mass receipt |
| `age2` | `advance2` | the already-registered `dynamics.age-claim@1`, named by ref |
| `earnings2` | `advance2` | carries the first path onto 2016 from a separate `scenario2` source |

`src/populace_dynamics/graph/two_transition_synthetic.py` holds the
invented second-period source, in its own module so a fixture edit
cannot move a kernel's implementation hash.

A first chained run against the same inputs as the one-shot run:
20 rows at 2014, 15 at 2015, 14 at 2016, `fit` reused, one second-step
decedent, five prior closures merged with it.

### Keys that move, and values that hold

Against `runtime.run_mortality_graph` on identical inputs:

- **Held:** `training`, `fit`, `initial`, `apply`, `advance`, `age`,
  `earnings-history`.
- **Moved:** `earnings` and `evaluate`. Both read `survives` (and
  `evaluate` also `death_probability`), whose owner in version `advance`
  is now `apply2`, so their input artifact keys move. This is the
  cascade the plan says to report, not a defect.
- **Values preserved exactly:** the model payload is byte-identical, the
  first carried earnings payload is byte-identical, the first mass
  receipt is equal, and the first earnings summary is equal apart from
  its store address.

One executor detail cost a fix: a manifest receipt comes back frozen
(`mappingproxy`/tuples), which `json.dumps` will not encode, so the
runner copies it into plain containers before it goes in the report.

## Next

- [ ] Focused tests; 123 existing checks on both cores.
- [ ] Cold/warm witness, module closure, key comparison, report.
