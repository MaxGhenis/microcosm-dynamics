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
| Known | a row with a finite value, including a known zero | the value, status `known` |
| Unknown | a row with status `unknown` and no value | `NaN`, status `unknown` |
| Absent | no row for that person-period | `NaN`, status `absent` |

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

## Tests

```sh
python -m pytest -q tests/test_graph_mortality.py \
  tests/test_graph_earnings_history.py \
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
reuse, descendant-only invalidation, an unchanged mass receipt, visible
partial failure, and a guard that no engine earnings model is called).
