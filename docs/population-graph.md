# First population graph: mortality and ageing

The optional `populace_dynamics.graph` package fits the existing M6 mortality
model on a historical synthetic panel, applies the fitted artifact to a
separate starting population, and adds surviving observations for the next
year. It produces an engineering report and a content-addressed execution
manifest. It does not change the existing projection loop, candidate
registries, scientific gates, or committed evidence.

## Dependencies and execution

The graph example requires Python **3.13 or 3.14**, NumPy 2+, pandas 2.3+,
and the Microcosm graph/frame revisions containing typed artifact edges and
`microcosm.graph.randomness.keyed_uniform`. The default Dynamics installation
continues to support Python 3.10–3.14 without importing Microcosm. The entry
point checks capabilities and gives installation guidance when they are absent.

The `graph` extra pins both graph and Frame to core commit
`3ff92b0aea14407d09479bff5623dc7d1a92d008`. An older package merely sharing
the version number `0.1.0` is insufficient. In an isolated Python 3.13 or 3.14
environment, install with `uv pip install '.[graph]'`. The core change must be
reviewed before this dependent integration is released; replace the Git pins
with a compatible published release when one exists. CI installs this exact
extra, refuses missing capabilities, and runs the integration on both supported
Python versions. Do not modify the existing scientific gate environment. No
rules engine, restricted microdata, or optional forest fitter is needed here.

Run from that environment, choosing an output directory:

```sh
python -m populace_dynamics.graph --synthetic --output-dir ./mortality-example
```

The command creates small synthetic inputs under `mortality-example/inputs`.
It preserves existing input files so that edits can test cache invalidation.
Repeated execution reuses the verified store under `mortality-example/store`.
The report, manifest, fitted JSON model, entity tables, and next-period slice
are written inside the chosen output directory. A failed engineering or
fixture verdict exits nonzero while retaining the diagnostics.

If malformed held-out input prevents evaluation, the executor records a failed
`evaluate` gate. The command exports that manifest and a diagnostic report with
the gate's name, outcome and original exception evidence on both cold and warm
runs, then exits nonzero. The report marks `engineering_verdict` and
`fixture_verdict` as `not_evaluated`; it does not invent evaluated deaths or
mass metrics. Successful evaluation retains the existing report fields.

Four explicit source paths can replace the generated inputs:

```sh
python -m populace_dynamics.graph \
  --training ./inputs/training.json --rates ./inputs/rates.json \
  --initial ./inputs/initial.json --holdout ./inputs/holdout.json \
  --boundary-year 2014 --external-vintage-year 2014 \
  --experiment-id comparison-a --replicate 0 --base-seed 0 \
  --output-dir ./mortality-example
```

These inputs still exercise the synthetic engineering contract. The example
does not confer validity on a real-population projection. Source JSON rejects
duplicate members and nonfinite values. Each source is declared separately;
holdout bytes are available only to evaluation. Domain kernels read the
content-verified JSON directly: the registered source marker deliberately
does not pretend an external rate table or a holdout report is a population.

## Executable ownership

The graph has two CREATE roots, each carrying a `person_period` observation
entity and `person` and `period` groups. `person` retains stable identities;
`period.period` is the immutable mass-partition label. The training root
contains exposure records; the initial root contains recipients. Their only
connection is the explicitly typed mortality-model artifact.

The fit node calls `prepare_mortality_refit_inputs` and
`fit_mortality_model`. Event year, required interview year, and declared
external vintage retain the existing cutoff checks. The JSON model contains
validated contiguous age bands, sex-specific probabilities, fit boundary,
external vintage, and retained row count. The manifest binds its producer
to source identities and implementation digests. The fitter's external-rate
factor cancels in its fitted-window level, so this is not evidence of
independent external calibration.

Application calls `apply_mortality` with a graph-specific context. Every
uniform is keyed by the original person identity, process, year, and draw
index under the chosen experiment/replicate/seed. It does not use the legacy
ID-sorted ordinal registry. Reordering, splitting, or adding unrelated
people preserves the existing people's draws. Fit and application declare
platform-specific bitwise numeric behavior conservatively; cross-platform
equality is not claimed.

EXPAND calls `advance_age` on survivors, adds their next-period observations
with lineage to the original observations, and attaches them to one newly
admitted period group. A same-version rewrite node claims the materialized
age values. Historical ages and memberships remain unchanged. The temporary
`year` returned by `advance_age` is never written over a carried observation
column. No new person, birth, or immigrant is implied by admission of the
period group.

Typed person-period weights are the single authority. Every survivor carries
the same trajectory weight into the new period. The declared mass receipt
shows historical mass unchanged and new-period mass equal to surviving
weight. Total stored observation mass therefore grows by the additional
period. If everyone dies, the graph adds no observations and no orphan period
group; the report explicitly records next-period mass zero.

## Evaluation and limits

The report separates `engineering_verdict` (survivor/age parity and population
structure) from `fixture_verdict` (the independently sourced synthetic
death-rate and age expectations). It records weighted expected, observed,
and generated deaths, row counts, period mass, node/model identities, and
cache reuse. The fixture death-rate tolerance is an input named
`fixture_max_abs_death_rate_gap`; it is not a scientific acceptance threshold.
Changing all held-out outcomes to deaths fails that fixture check while
leaving fitting, application, draws, and accounting unchanged.

Household accounting is explicitly unsupported and refused by the Python
entry point. Household weight sharing, marriage, births, immigration,
alignment replay, repeated years, and the full M6 loop remain later work.
No certified data release or scientific candidate is produced by this graph.

## Optional earnings-history retention

The graph carries no earnings unless a run asks it to. `run_mortality_graph`
takes an optional `earnings` source; without it the declared graph, its
kernels, its source set, and every output are exactly what a mortality-only
run has always produced.

With it, two ordinary nodes join the advanced population.
`dynamics.earnings.history@1` reads the declared source and emits a typed
`populace-dynamics.earnings-path` artifact; `dynamics.earnings.carry@1`
consumes that artifact on the `advance` population, writes
`period_earnings`, `period_earnings_status`, and `period_earnings_origin`
onto every row, and emits the carried path as its own typed artifact.

This is retention, not estimation. Nothing here fits, projects, or imputes
an earnings value. A next-period value in the source is labelled
`scenario`: it is a supplied fixture input that the run carries onto a row
it created, never a forecast the graph produced. `engine.steps.apply_earnings`
and `engine.forward_earnings` remain unused by the graph, and no wage base,
indexation, or averaging rule appears anywhere in it — a Social Security
computation needs all three and is deliberately absent.

### What a path declares

Values are meaningless without their measurement terms, so the artifact
carries them and the run must state the same ones or be refused: `unit`,
`price_basis`, `calendar`, and `sign_domain`. The graph reads no meaning
into any token, which is what lets a path from another country supply its
own currency and calendar rather than inherit a guessed national one.
`sign_domain` decides whether a negative period (a net loss, say) is
admissible at all.

Three states stay distinct and none is ever filled in quietly:

| State | In the path | In the columns |
|-------|-------------|----------------|
| Known | a row with a finite value, including a known zero | the value, status `known`, origin `observed` or `scenario` |
| Unknown | a row with status `unknown` and no value | `NaN`, status `unknown`, origin `observed` or `scenario` |
| Absent | no row for that person-period | `NaN`, status `absent`, origin `absent` |

`period_earnings_origin` carries the row's own origin where there is a
row and the sentinel `absent` where there is none, so the origin column
never has to be read against the status column to tell a supplied value
from a missing one.

### What a source must already be

The source path is a starting state, not a state the run has advanced.
Three things about it are refused rather than repaired:

- **Every person in the population needs at least one `observed` row.**
  A person the population holds and the path does not is refused by
  name. Supplying only future values for someone is not enough.
- **A source that closes anyone is refused.** Closures are what this run
  produces for its own decedents; a path that arrives with a `closed`
  list has already been carried by something else.
- **A source with a `carried_through_period` is refused.** The same
  reason: it has been carried already, and this run carries from the
  boundary.

A real panel therefore has to be filtered before it is handed over.
People who died before the boundary are not in the population and must
not be in the path, and a path produced by an earlier run cannot be fed
back in as a source. The graph advances one period, so no carried path
is ever a source to the next run.

### Carrying and closing

Survivors take their supplied next-period row; the run refuses if one is
missing. Decedents keep every period they already held, take no new row,
and are recorded in the carried path's `closed` list. A next-period value
supplied for a decedent is withheld rather than written onto a row that
does not exist, and the receipt names each person it withheld.

An existing period is never overwritten. A source row that would replace
one is refused as a retroactive overwrite, not merged.

### The optional total

`earnings_accumulate` adds `cumulative_known_earnings`, a running
bookkeeping sum of a person's known values through that row's period. It
is available only under a `fixed@<period>` price basis, where every value
is already in one period's prices. A `nominal` path is refused, because
adding values stated in different periods' prices is not a total of
anything. The column is `NaN` wherever an unknown period falls in range:
the total is then unknown too, and says so. It is a plain sum in one
declared unit — no cap, no indexation, no selection of high years.

### Cache identity

Editing the path invalidates the two earnings nodes and nothing else; the
mortality fit, its application, the advance, and the mass receipt all stay
cached and byte-identical. The producer deliberately lives in the advanced
population rather than in `initial`: a structural node's key binds every
ordinary member of the version it transforms, so a source-reading member of
`initial` would drag `advance` and its whole downstream along with every
source edit.

Reordering rows in the source file changes its bytes, so the two earnings
nodes recompute; what they produce does not change, because the artifact
serializes its rows in person-period order.

### Reading cost

The artifact is immutable, so it indexes its rows by person and by
person-period once, in the pass that validates them, and answers
`history` and `at` out of that index. Reading one person's path, or one
coordinate, costs nothing that grows with the population; the cumulative
column still sums each person's own prefix rows, so a 35-period path
costs 35 additions per row and no more. Rows and closures handed to the
constructor are copied into tuples first, so a caller who edits the list
afterwards cannot leave the index describing rows the path no longer
holds.

## Two transitions in one execution

`populace_dynamics.graph.two_transition` is a sibling of `runtime`, not a
replacement. It calls `runtime.build_graph`, keeps every node, kernel and
source it returns, and adds up to four nodes so that one compiled graph
holds two chained transitions: a mortality-only chain — the shape the
module's own test pins — adds three nodes and two new kernels; supplying
earnings terms adds the fourth node, a third new kernel, and one new
source. The second period's rows are produced inside the same execution
as the first's; nothing is serialized out of one run and fed into
another, and no cross-run provenance is claimed.

| node | version | what it does |
|---|---|---|
| `apply2` | `advance` | applies the *same* fitted law at the transition period's rows, rewriting `survives` and `death_probability` there and leaving every other period's values as they are |
| `advance2` | its own | copies the transition period's survivors into the advanced period — carrying their already-written `survives` and `death_probability` forward unchanged from the transition period's source row, not a new hazard evaluation — with a declared mass receipt over a base that already holds two periods |
| `age2` | `advance2` | the already-registered `dynamics.age-claim@1`, named by reference, claiming the copied rows' ages |
| `earnings2` | `advance2` | carries the first transition's path onto the advanced rows from its own declared `scenario2` source |

`fit` still runs once, at the fixed boundary year. Both application nodes
read its artifact through the same declared edge, so there is no second
model, no refit, and no drift. Rewriting the transition period's columns
does not mean their values move: under the shipped fitted fixture every
row's `death_probability` is the same value regardless of age or sex, so
`apply2`'s rewrite reproduces it bit-for-bit there, and only `survives` —
the drawn outcome — can differ from the one-shot run, which it does for a
single person in the default synthetic run. What differs between the two
applications is the draw coordinate: the second asks the registered
generator for the period after the transition, so the two transitions
read disjoint coordinates of one keyed stream and can never share a draw.

### Which keys move

Adding `apply2` makes it the owner of `survives` and `death_probability`
in the expanded version. Readers resolve to their version's owner, so the
existing `earnings` and `evaluate` nodes now bind `apply2`'s key instead
of `apply`'s and their keys move. Their values do not: `apply2` writes the
incumbent value back at every period except the transition period, so the
boundary year's survival and probabilities are bit-for-bit what a
one-shot run produced, as are the fitted model, the first carried
earnings path and the first mass receipt. `evaluate`'s report payload is
included in that: it is byte-identical to the one-shot run's, sha256
`afa763f26ea62dea6b751aa8e3190fc1462373688cabe9ea635539ddc1d852cc` on
both pinned cores. What moves alongside `evaluate`'s key is its *receipt*,
not its value: the node's `tolerance_writers` entry for `survives` and
`death_probability` gains `apply2` alongside `apply`, and because an
opaque artifact's storage address is derived from its owning node's key,
`evaluate`'s stored artifact address moves too, even though the bytes at
that address do not change. `training`, `fit`, `initial`, `apply`,
`advance`, `age` and `earnings-history` keep their keys.

Editing the holdout file moves more than the gate. A structural node
binds every ordinary member of the version it transforms, so `advance2`
and everything in its version rekey with `evaluate`. Nothing they produce
changes. Editing the `scenario2` file alone reaches `earnings2` and
nothing else.

A failed gate is a diagnostic, not a stop. The executor records the
failure as a receipt and completes the later nodes, so the second
transition is present in the manifest and in the report even when the
first transition's fixture check has failed.

### The second earnings carry

`earnings2` receives the first transition's carried path as a typed
artifact edge and its own supplied values as a separate source. It
requires the prior path to be carried through the transition period, and
the source to be an uncarried path that closes nobody, restates no
coordinate the prior path already holds, and holds only scenario rows at
the one advanced period. A restated coordinate is refused as an
overwrite before the period is even looked at, because a row at a period
the prior path holds is a rewritten history, not a mislabelled future
value.

Every row the prior path holds is kept. The only rows added are supplied
values for people who survived this transition, and every survivor must
have one. A supplied row for anybody else — a person already closed, or
one who died in this transition — is withheld, counted in the receipt
under its reason, and never appended. Withholding is what lets the
all-dead case have a source at all: a path needs at least one row, so the
source carries decedent rows, and the output still creates no new
person-period. New decedents are closed at the transition period, which
is where their last row sits, and prior closures are merged rather than
replaced.

Two terminal cases are ordinary results. When nobody survives the second
transition, the expansion adds no row and no period group, the mass
receipt shows the advanced period absent, and the retained history is
untouched. When nobody reaches the transition period at all, the second
application finds no active rows and writes the incumbents straight back.

### What a run writes

Beside the manifest, report, fitted model and entity tables, the runner
writes the final carried path, the first transition's carried path, a
`population.csv` holding every retained row with the person, age, sex and
weight the graph actually carries, and one `period-<year>.csv` per period.

The holdout gate covers the first transition only. Nothing evaluates the
second period against held-out outcomes, and no second-period accuracy is
claimed. What the tests establish about it is engineering parity with
directly coordinated calls to the same mortality and ageing operations
under the same fitted model and the same keyed uniforms. A predictive
claim over two periods needs genuinely appropriate later outcomes, which
this slice does not have.

## Tests

```sh
python -m pytest -q tests/test_graph_mortality.py \
  tests/test_graph_earnings_history.py tests/test_graph_earnings_index.py \
  tests/test_graph_two_transition.py \
  tests/test_m6_engine_refit.py tests/test_m6_engine_steps.py
```

The integration tests cover direct execution with an independently injected
uniform vector, JSON validation, cutoff and holdout isolation, fitted-artifact
reuse, changed fitting weights, row/chunk/person invariance, cold/warm stores,
and zero/all-survivor expansion. Independent graph-to-direct model parity and
future-event/late-interview mutations protect cutoff mapping. Nondefault
experiment, replicate and seed tests independently derive draw coordinates and
check direct-step parity, fit reuse and changed application identity. They skip
the optional runtime cases when the required core capabilities are unavailable;
the JSON and dependency
boundary tests still run. Importing `populace_dynamics.graph` remains safe
under Python 3.10–3.12.

`tests/test_graph_earnings_history.py` covers the path contract without a
core installed (round trips, row-order invariance, the known-zero /
unknown / absent distinction, the signed domain, fail-closed payload and
coordinate mutations, refused overwrites, and the accumulator) and the
node with one (optionality and the untouched default, survivor carry and
decedent closure, full historical preservation, the period and cumulative
columns, refused measurement terms, mismatched coordinates, cold/warm
reuse, descendant-only invalidation, an unchanged mass receipt, a
refusal that names its node and kernel and writes no manifest, report,
or columns, and a guard that no engine earnings model is called).

`tests/test_graph_earnings_index.py` covers the path's index: an
independent reference copy of the pre-index `history`, `at`, `people`,
`closed_people`, `prefix_total` and `known_total` is run beside the
artifact's own over signed, known-zero, unknown, absent, cancelling and
unordered paths, probed at people and periods the paths do not hold. It
also pins the arithmetic — a cumulative total carried row by row and the
prefix sum disagree on a cancelling path, and the prefix sum is the
answer the pre-index code gave — and counts what a lookup touches on a
1000-person, 35-period path, which is where the index earns its keep.

`tests/test_graph_two_transition.py` covers the chained graph: the second
period against `apply_mortality` and `advance_age` called directly at
both periods, three non-default streams, the two transitions never
sharing a draw, person/period/age/sex/weight/survival membership, the
preserved first transition and the exact set of keys that move, the
multiyear mass receipt, the second carry's retained history, merged
closures, withheld rows counted by reason, the known-zero / unknown /
absent distinction, the accumulator, a signed path whose second period
cancels a total to a known zero, both terminal cases, a failed gate that
still lets the later nodes finish, the files the runner writes, and
seventeen refusals including a restated history coordinate, a model
fitted at another boundary, a person closed in the prior path and still
active, and advanced rows that disagree with the survivors.
