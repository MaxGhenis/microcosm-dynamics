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
