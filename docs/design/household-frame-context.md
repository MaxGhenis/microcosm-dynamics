# Optional household Frame context

The experimental `populace_dynamics.frame_context` module reads a baseline
household Frame using Microcosm's shared v2 codec. It does not run mortality,
change membership, map weights, reconstruct a Population, or admit a dataset.
Legacy Dynamics readers and dependency declarations are unchanged.

The source contract was inspected and tested at Microcosm commit
`a9cc63e737fd4619a304117dc2ec7dcd86d97901` (merged PR913), using Python 3.13.
Both `microcosm-frame` and `microcosm-graph` must come from that reviewed
revision in an isolated test environment. These optional dependencies are not
added to the default Dynamics installation. The adapter checks the codec's
format capability, not publisher authority or the installed source revision;
the execution environment must bind the latter separately.

## Baseline reader

`read_baseline_frame` requires an object directory and three independently
established identities: its store key, producer-node key and SHA-256 of
`meta.json`. The metadata digest binds the complete payload inventory. The
shared `ContentStore.load_frame_path` implementation then verifies and decodes
the object; Dynamics contains no parallel Frame decoder.

The caller also supplies an independent complete membership DataFrame with
exactly `person_id` and `person_household_id`, an aligned `household_id` Series,
and the expected `WeightKind` for every explicitly weighted entity. Row order,
indexes, dtypes and values must match. The household vector must be explicit.
Individual zero weights remain attached to their members. DESIGN, IMPORTANCE
and CALIBRATED are distinct; strings, missing kinds and silent conversions
are refused. No implicit person vector is created.

The returned Frame retains its entity/link tables, metadata, nullable dtypes,
strata, Frame mass log, weights and kinds. Unsupported old runtime or object
formats fail explicitly. A v1 object is never rewritten or downgraded.

These are integrity and interface checks. A caller deriving its expected
roster from the same file has not independently proved completeness. Before
native use, the parent must establish the producer, boundary period, complete
household scope, mapping identities, clone/source bindings, and eligibility
of partial households or group quarters. This module does not settle those
decisions or reinterpret metadata. Link storage preservation does not imply
support for longitudinal link transitions.

## Continuing populations

`retain_population` accepts an existing in-memory `Population` and the same
roster/weight contract. It validates the boundary and returns the exact
original object: version, column owners, graph mass ledger, original design
anchors and Frame metadata remain attached. It never calls
`Population.from_frame` to invent missing history. External executor receipts
and lineage bindings remain with the caller.

A Frame file cannot restore those surrounding Population fields. Asking the
baseline reader for a `continuing_population` interpretation fails before
reading. A bare Frame passed to `retain_population` also fails. A future
parent export needs a separately bound envelope for version, owners, ledger,
original design anchors and external lineage receipts; no serialized envelope
is introduced here.

## Source-only verification

All fixtures are invented complete households. Checks cover IDs above 2^53,
leading-zero geography strings, nullable columns, full membership, zero-weight
households, all three weight kinds, object identity mismatches, payload
tampering, stored links and weight history, and retention of an existing
Population. The test module skips when the optional Microcosm packages are
absent; default CI alone therefore does not validate this optional integration.
Any proposed dependency admission or PR must add a job using the reviewed
dependency revisions.

### Pinned optional CI recipe

Run from the Dynamics checkout in a dedicated job with Git and uv available.
Both Microcosm packages report version `0.1.0`, including incompatible older
source, so pin both packages to the same full Git revision. Installing either
package from an unpinned registry requirement is insufficient. Their Python
requirement is at least 3.13; this recipe was exercised on Python 3.13.9 with
NumPy 2.5.3, pandas 3.0.5 and pytest 9.1.1. These are tested pins, not a claim
about the newest releases.

```sh
set -eu
frame_ci_dir="$(mktemp -d)"
uv venv --python 3.13.9 "$frame_ci_dir/.venv"
uv pip install --python "$frame_ci_dir/.venv/bin/python" -e . \
  'numpy==2.5.3' 'pandas==3.0.5' 'pytest==9.1.1' \
  'microcosm-frame @ git+https://github.com/PolicyEngine/microcosm.git@a9cc63e737fd4619a304117dc2ec7dcd86d97901#subdirectory=packages/microcosm-frame' \
  'microcosm-graph @ git+https://github.com/PolicyEngine/microcosm.git@a9cc63e737fd4619a304117dc2ec7dcd86d97901#subdirectory=packages/microcosm-graph'

uv run --no-project --python "$frame_ci_dir/.venv/bin/python" python - <<'PY'
import importlib.metadata as md
import json
import platform
from microcosm.graph import store

revision = "a9cc63e737fd4619a304117dc2ec7dcd86d97901"
assert platform.python_version() == "3.13.9"
for package, version in {
    "numpy": "2.5.3", "pandas": "3.0.5", "pytest": "9.1.1"
}.items():
    assert md.version(package) == version, package
for package in ("microcosm-frame", "microcosm-graph"):
    source = json.loads(md.distribution(package).read_text("direct_url.json"))
    assert source["url"] == "https://github.com/PolicyEngine/microcosm.git"
    assert source["vcs_info"]["vcs"] == "git"
    assert source["vcs_info"]["commit_id"] == revision, package
    assert source["subdirectory"] == f"packages/{package}", package
assert store._FRAME_FORMAT == "microcosm-graph-frame-v2"
PY

uv pip freeze --python "$frame_ci_dir/.venv/bin/python" \
  > "$frame_ci_dir/resolved-requirements.txt"
uv run --no-project --python "$frame_ci_dir/.venv/bin/python" \
  python -m pytest -q tests/test_frame_context.py \
  --junitxml="$frame_ci_dir/pytest.xml"
uv run --no-project --python "$frame_ci_dir/.venv/bin/python" \
  python - "$frame_ci_dir/pytest.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
cases = root.findall(".//testcase")
assert cases, "Optional Frame context job collected no tests"
for tag in ("skipped", "failure", "error"):
    assert not root.findall(f".//{tag}"), f"Optional context job has {tag}"
print(f"{len(cases)} cases passed without skips")
PY
```

Retain `resolved-requirements.txt` and `pytest.xml` as job artifacts before
removing the temporary environment. The remaining Dynamics transitive
dependencies follow the checkout's declarations; this recipe pins the shared
runtime and tested core packages, not the complete dependency closure. A
fully locked CI environment needs a reviewed lock for that closure. The
explicit interpreter paths keep the optional job separate from the default
Dynamics environment. The source preflight and JUnit check are required:
pytest's successful exit alone can conceal a module-level dependency skip.

The September 12 source review found no actionable correctness defects at
Dynamics `2e08ee16403d8eb292902137280a5621a10651d3`. The reviewer and a fresh
Git-pinned installation each passed all 23 invented-household cases. This
verifies the optional interface only; producer/period/complete-household
admission remains with the parent. Its planned initial interface is a baseline
Frame. The continuing-Population envelope is a separate future requirement.

A separate source-bound check against the previously admitted Microcosm
`3ff92b0aea14407d09479bff5623dc7d1a92d008` verified that its own v1 Frame round
trip still succeeds and this new optional reader refuses that old runtime.
No native donor, calibration payload or comparator values were used.

## HDF checkpoint intake

`populace_dynamics.checkpoint_intake.read_baseline_checkpoint` supports a second
explicit carrier: Microcosm Build's actual `write_frame_checkpoint` /
`load_frame_checkpoint` API. It delegates all table, relationship, dtype,
missingness and weight decoding to that loader. It does not convert the HDF
file into a graph-store object or introduce another Frame serializer.

The caller must independently establish the file's SHA-256 and the exact
expected external metadata supplied to the shared writer. This proposed
Dynamics consumer manifest has the following required fields:

```json
{
  "protocol": "populace-dynamics.baseline-checkpoint-intake.v1",
  "interpretation": "baseline_frame",
  "producer_revision": "1111111111111111111111111111111111111111",
  "period": "2026-01-01",
  "household_scope": "complete_households",
  "frame_metadata": {"fixture": "invented example only"}
}
```

The example revision is invented. `period` is the exact ISO calendar date of
the boundary; its economic meaning and timing must be established by the
parent. Additional external metadata is allowed only when it matches the
independent expected manifest exactly, including JSON value types. The shared
checkpoint format stores external metadata separately from Frame metadata;
the latter is restored only from this bound `frame_metadata` mapping.

In addition to the earlier complete membership and household rosters and all
explicit weight kinds, this intake requires:

- `relationships`: an independent DataFrame containing `person_id` followed
  by each group membership column in schema order. It checks every group,
  including tax units, with exact values, dtypes, indexes and row order.
- `required_inputs`: columns by entity, each with `InputColumn(dtype,
  nullable=...)`. Person and household requirements must be nonempty. Each
  consuming transition must declare its own complete input needs; this module
  does not supply a global Dynamics schema. Missing columns, wrong logical
  dtypes and unknown values in nonnullable inputs refuse. Nullable inputs
  retain masks. Dtype names follow `str(series.dtype)`; string storage backend
  selection is not part of this input requirement. Independent relationship
  and provenance comparisons additionally check pandas dtype equality.
- `clone_provenance`: independent ID-aligned DataFrames with the original
  source and clone columns for person and household, and any additional
  entities the caller needs. The selected columns must match exactly. The
  parent must identify which fields establish provenance; naming an arbitrary
  column does not establish ancestry.

The file digest is checked before decoding and again afterward. An invalid
manifest, absent declarations or wrong initial digest refuses before the
decoder runs. The embedded manifest, relationships, required inputs and clone
origins must pass before a Frame is returned for downstream dynamics. All
members and original explicit weight vectors are retained, including zero
household weights and differing kinds on other entities. No dynamics run is
started by intake. Continuing-Population manifests refuse explicitly.

These checks require a trusted local checkpoint that the host keeps stable
through the call. They are not an adversarial concurrent-file sandbox or a
source-approval mechanism. The common retained-export comparison module
expressly does not verify graph/calibration ancestry or issue release
eligibility. Its receipt alone, an old file, or a development checkpoint
cannot establish an admitted baseline. The parent still owns producer and
source authority, timing, complete-household scope (including any treatment
of group quarters), clone origins, geographic mappings, and weight authority.
Prior wage histories are not added as cross-section requirements.

### Bounded checkpoint verification

The September 13 rehearsal uses source revision
`21f02c2ab081c44565bcf54148af3c05768d5c82` from the parent's integration checkout,
not an admitted runtime or dataset release. An immutable local source snapshot
of Frame, Graph, Build, Calibrate and Fit provides the normal package imports.
The existing Microcosm environment supplies Python 3.14.4, NumPy 2.4.6,
pandas 3.0.3, h5py 3.16.0 and pytest 8.4.2. No new environment or dependency
installation is needed for that rehearsal. These differ from the earlier
graph-only recipe; its two-package installation is insufficient for Build's
checkpoint API and import dependencies.

Run only `tests/test_checkpoint_intake.py` and `tests/test_frame_context.py`
with that source snapshot preceding installed packages, and the owned
Dynamics `src` preceding other Dynamics checkouts. Record actual imported
paths/hashes, dependency versions and a JUnit report; require at least one
test and zero skips, failures or errors. Optional default-environment skips
do not validate this integration. A future packaged CI job must separately
pin the compatible Build/Frame/Graph/Calibrate/Fit constellation and its
dependency closure; this local rehearsal does not admit those dependencies.

Fixtures contain only three invented people, two households (one with zero
weight), and three tax units. IDs exceed signed int64, and clone origins,
leading-zero geography, nullable relationship/Boolean columns and mixed
weight kinds pass through the real shared writer and loader. Negative cases
cover manifest mismatches, changed group membership and clone origins,
partial households, wrong kinds, incomplete required inputs and a file
changed during decoding. The new US cross section remains incomplete and
every DynaSim replication score remains unscored.
