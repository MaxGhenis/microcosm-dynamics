# Annual ageing with household context

The optional `populace_dynamics.context_ageing` module connects a compatible
baseline Frame to Microcosm's real graph runtime. It advances the existing
Dynamics age/year step without rebuilding the household data in a narrow
person-only table. It does not establish an admitted baseline or simulate
deaths, births, migration, claiming, benefits or economic uprating.

`annual_ageing_nodes` requires a base version, consecutive `from_year` and
`to_year`, a unique node prefix, and explicit `membership_policy="unchanged"`.
The host supplies that scenario assumption; it is not an estimated survival
outcome. Every person must have a known int64 year equal to `from_year` and a
nonnegative int64 age that can increase without overflow. Every row advances
by one year, including members of zero-weight households.

The returned pair first opens a structural FILTER version with every member
retained and conserved mass. A separate ordinary node rewrites only `age`
and `year`, using the existing `engine.steps.advance_age` function. Its
implementation fingerprint includes that function and its period-context
source. Microcosm handles column patches, carried tables, group relationships,
weights, mass records and cache replay. A subsequent pair names the preceding
carry version as its base; the graph orders that version's age rewrite before
the next carry.

Structural carry versions receive column ownership through the shared
runtime. The age node claims only age/year; it does not claim source-origin
columns. Original explicit weight kinds and design anchors remain attached.
Baseline metadata remains source provenance. The `year` column tracks the
advanced period; carried economic or benefit fields must not be treated as
updated solely because the age step completed. Annual counts alone do not
specify birthdays, payment dates or within-year exposure.

## Compatibility before graph creation

`baseline_graph_outputs(frame)` validates the Frame and declares its ordinary
data cells through Microcosm's `token_for_dtype`. IDs and group membership
columns remain structural. It also asks the shared Frame to resolve the
person-level stratum mass needed by graph transitions. It performs no dtype
conversion, weight-kind conversion or explicit person-weight construction.

Two limitations matter for the cross-section handoff:

- The inspected graph declaration supports fewer ordinary data dtypes than
  the shared checkpoint serializer. In the tested `21f02c2` source, uint64 and
  int8 data columns cannot be declared as owned cells. The preflight names the
  incompatible column and refuses. For example, the earlier HDF fixture's
  unsigned source IDs and small integer clone counter can survive storage
  while remaining ineligible for graph CREATE. Exact support needs a reviewed
  shared-runtime extension or an independently approved producer schema;
  Dynamics does not silently cast them.
- With multiple explicitly weighted group entities and no explicit person
  vector, the shared Frame cannot determine person-level mass. The preflight
  refuses instead of selecting an authority. A household-only explicit vector
  works through the shared mapping, and its explicit weight topology remains
  household-only. Multiple group vectors work when the producer also supplies
  an independently authoritative explicit person vector.

Separate link tables are not admitted by this CREATE declaration helper.
Group membership columns, including household and tax-unit relationships,
are preserved and tested. Full continuing-Population file import remains
unsupported; source admission and the complete parent manifest contract in
[household Frame context](household-frame-context.md) are still required.

## Invented-data evidence

The small tests execute actual graph CREATE/FILTER/column-patch operations and
ContentStore serialization. One test begins with the real HDF writer and the
Dynamics manifest intake, then deliberately writes the accepted invented
Frame through the shared graph store for the test CREATE kernel. This is an
integration rehearsal, not a production baseline issuer or a new serializer.

The fixtures have three people, two households and three tax units; stable
person and source IDs exceed 2^53. They exercise nullable relationship and
Boolean cells, clone origins, leading-zero blocks, a zero-weight household,
and unchanged mixed DESIGN/CALIBRATED vectors. Two years of cold execution
and mandatory cache replay preserve those fields. Invalid year contracts,
missing or mistyped inputs, negative/overflowing ages, ambiguous weight
authority and unsupported data dtypes refuse explicitly.

The tests reuse the source snapshot and environment from the September 13
checkpoint rehearsal; no native data or new environment is required. Run only
`tests/test_context_ageing.py`, `tests/test_frame_context.py` and
`tests/test_checkpoint_intake.py` with the exact source paths and no-skip
check. Default CI skips do not validate this optional integration. The result
is engineering progress toward longitudinal integration; no DynaSim
replication score has been measured.
