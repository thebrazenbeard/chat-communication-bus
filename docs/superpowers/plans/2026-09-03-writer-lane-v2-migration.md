# Writer Lane V2 Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace conflict-prone long-lived writer lanes with clean, topology-registered v2 mailbox lanes while preserving every v1 commit as immutable provenance.

**Architecture:** Canonical software and protocol remain on `main`; current writer lanes become mailbox-only append surfaces. A new `radar.writer_lanes` module reads the topology contract, derives logical identity from the exact branch ref, and validates that each current-lane commit only adds new `messages/*.md` files. Projection source consumes that validated identity. The fleet cutover is a separate post-merge operation that creates every v2 lane from one exact canonical `main` commit and leaves all v1 refs untouched.

**Tech Stack:** Python 3.11/3.12, pytest, Git plumbing commands, GitHub Actions YAML, JSON source contracts.

**Spec:** `docs/superpowers/specs/2026-09-03-writer-lane-v2-migration-design.md`

## Global Constraints

- Preserve every existing writer-lane commit as immutable provenance.
- Do not force-push, rebase, squash, delete, or rename historical v1 lane refs.
- `main` remains the sole canonical system/software/protocol line.
- Current writer lanes may add new files under `messages/`; they may not modify or delete historical messages or alter shared repository files.
- `architecture/contracts/RADAR_TOPOLOGY_V1.json` remains the source-side registry for the current branch of each logical identity.
- Brigit's historical branch remains `bus/bridget-v1`; the successor is `bus/brigit-v2`.
- Sender identity is derived from the topology-bound branch ref; a message header may corroborate but may not choose the sender.
- No routine writer-lane PRs into `main`.
- No provider deployment, Supabase migration, ruleset/branch-protection change, credential mutation, or merge without a separate explicit authority gate.
- Historical v1 lanes remain readable provenance; prospective validation applies to topology-designated current lanes.

---

### Task 1: Topology-bound writer-lane validator

**Files:**
- Create: `src/radar/writer_lanes.py`
- Create: `tests/radar/test_writer_lanes.py`

**Interfaces:**
- Consumes: `architecture/contracts/RADAR_TOPOLOGY_V1.json` with `required_writer_lanes.<identity>.branch` and `.writer`.
- Produces: `WriterLane`, `WriterLaneError`, `load_writer_lanes(topology_path)`, `identity_for_ref(ref, topology_path)`, `validate_writer_lane_commit(repo_dir, ref, head, topology_path) -> str`.

- [ ] **Step 1: Write the failing topology/ref tests**

```python
from pathlib import Path
import json
import subprocess

import pytest

from radar.writer_lanes import WriterLaneError, identity_for_ref, load_writer_lanes, validate_writer_lane_commit


def write_topology(tmp_path: Path) -> Path:
    path = tmp_path / "topology.json"
    path.write_text(json.dumps({
        "schema_version": 1,
        "required_writer_lanes": {
            "one": {"writer": "One", "branch": "bus/one-v2", "legacy_spelling": False},
            "brigit": {"writer": "Brigit", "branch": "bus/brigit-v2", "legacy_spelling": False},
        },
    }))
    return path


def test_identity_for_ref_comes_only_from_registered_current_lane(tmp_path):
    topology = write_topology(tmp_path)
    assert identity_for_ref("refs/heads/bus/one-v2", topology) == "one"
    with pytest.raises(WriterLaneError, match="UNREGISTERED_WRITER_LANE"):
        identity_for_ref("refs/heads/bus/one-v1", topology)
    with pytest.raises(WriterLaneError, match="UNREGISTERED_WRITER_LANE"):
        identity_for_ref("refs/heads/bus/one-v2-lookalike", topology)
```

- [ ] **Step 2: Run the targeted tests and confirm RED**

Run: `python -m pytest -q tests/radar/test_writer_lanes.py`

Expected: collection/import failure because `radar.writer_lanes` does not exist.

- [ ] **Step 3: Implement topology loading and exact ref binding**

```python
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess


class WriterLaneError(ValueError):
    pass


@dataclass(frozen=True)
class WriterLane:
    identity: str
    writer: str
    branch: str


def load_writer_lanes(topology_path: str | Path) -> dict[str, WriterLane]:
    raw = json.loads(Path(topology_path).read_text(encoding="utf-8"))
    required = raw.get("required_writer_lanes")
    if not isinstance(required, dict) or not required:
        raise WriterLaneError("WRITER_LANE_REGISTRY_MISSING")
    lanes: dict[str, WriterLane] = {}
    seen_branches: set[str] = set()
    for identity, record in required.items():
        if not isinstance(identity, str) or not identity or not isinstance(record, dict):
            raise WriterLaneError("WRITER_LANE_REGISTRY_INVALID")
        writer = record.get("writer")
        branch = record.get("branch")
        if not isinstance(writer, str) or not writer or not isinstance(branch, str) or not branch:
            raise WriterLaneError("WRITER_LANE_REGISTRY_INVALID")
        if branch in seen_branches:
            raise WriterLaneError("DUPLICATE_WRITER_LANE_BRANCH")
        seen_branches.add(branch)
        lanes[identity] = WriterLane(identity=identity, writer=writer, branch=branch)
    return lanes


def identity_for_ref(ref: str, topology_path: str | Path) -> str:
    branch = ref.removeprefix("refs/heads/")
    matches = [lane.identity for lane in load_writer_lanes(topology_path).values() if lane.branch == branch]
    if len(matches) != 1:
        raise WriterLaneError("UNREGISTERED_WRITER_LANE")
    return matches[0]
```

- [ ] **Step 4: Add commit-path behavior tests**

```python
def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_lane_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "lane"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.email", "test@example.com"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Test"])
    (repo / "messages").mkdir()
    (repo / "README.md").write_text("canonical inherited file\n")
    subprocess.check_call(["git", "-C", str(repo), "add", "."])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "base"])
    return repo, git(repo, "rev-parse", "HEAD")


def commit_file(repo: Path, path: str, content: str, message: str) -> str:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    subprocess.check_call(["git", "-C", str(repo), "add", "-A"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", message])
    return git(repo, "rev-parse", "HEAD")


def test_current_lane_may_only_add_new_message(tmp_path):
    topology = write_topology(tmp_path)
    repo, _ = make_lane_repo(tmp_path)
    head = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: One\n", "message")
    assert validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology) == "one"


def test_current_lane_rejects_shared_file_change(tmp_path):
    topology = write_topology(tmp_path)
    repo, _ = make_lane_repo(tmp_path)
    head = commit_file(repo, "README.md", "writer changed this\n", "bad")
    with pytest.raises(WriterLaneError, match="WRITER_LANE_PATH_FORBIDDEN:README.md"):
        validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology)


def test_current_lane_rejects_modify_or_delete_existing_message(tmp_path):
    topology = write_topology(tmp_path)
    repo, _ = make_lane_repo(tmp_path)
    first = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: One\n", "message")
    assert validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", first, topology) == "one"
    head = commit_file(repo, "messages/0001.md", "rewritten\n", "rewrite")
    with pytest.raises(WriterLaneError, match="WRITER_LANE_MESSAGE_NOT_APPEND_ONLY"):
        validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology)
```

- [ ] **Step 5: Run the new tests and confirm RED on missing validator**

Run: `python -m pytest -q tests/radar/test_writer_lanes.py`

Expected: ref-binding tests pass; commit-path tests fail because `validate_writer_lane_commit` is missing.

- [ ] **Step 6: Implement minimal commit validation**

```python
def _git_bytes(repo_dir: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo_dir), *args], stderr=subprocess.PIPE)


def validate_writer_lane_commit(
    repo_dir: str | Path,
    ref: str,
    head: str,
    topology_path: str | Path,
) -> str:
    identity = identity_for_ref(ref, topology_path)
    repo = Path(repo_dir)
    observed = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if observed != head:
        raise WriterLaneError("BRANCH_HEAD_MISMATCH")
    try:
        parent = subprocess.check_output(["git", "-C", str(repo), "rev-parse", f"{head}^"], text=True).strip()
    except subprocess.CalledProcessError:
        raise WriterLaneError("WRITER_LANE_PARENT_REQUIRED")
    raw = _git_bytes(repo, "diff-tree", "--no-commit-id", "--name-status", "-r", "-z", parent, head)
    fields = [value.decode("utf-8") for value in raw.split(b"\0") if value]
    for index in range(0, len(fields), 2):
        status, path = fields[index:index + 2]
        if not path.startswith("messages/") or not path.endswith(".md"):
            raise WriterLaneError(f"WRITER_LANE_PATH_FORBIDDEN:{path}")
        if status != "A":
            raise WriterLaneError(f"WRITER_LANE_MESSAGE_NOT_APPEND_ONLY:{path}")
    return identity
```

- [ ] **Step 7: Run Task 1 tests GREEN**

Run: `python -m pytest -q tests/radar/test_writer_lanes.py`

Expected: all Task 1 tests pass.

- [ ] **Step 8: Commit Task 1**

```bash
git add src/radar/writer_lanes.py tests/radar/test_writer_lanes.py
git commit -m "feat: validate topology-bound writer lanes"
```

---

### Task 2: Bind projection batches to the topology-derived lane identity

**Files:**
- Modify: `scripts/radar_emit_bus_projection.py`
- Modify: `tests/radar/test_emit_bus_projection.py`

**Interfaces:**
- Consumes: `validate_writer_lane_commit(...) -> str` from Task 1.
- Produces: projection batch field `lane_identity: str`; emitter rejects unregistered refs and non-mailbox commits before transport.

- [ ] **Step 1: Add failing projection tests**

Add tests that pass an explicit topology fixture and assert both path validation and identity derivation:

```python
def write_topology(tmp_path: Path) -> Path:
    path = tmp_path / "topology.json"
    path.write_text('{"schema_version":1,"required_writer_lanes":{"one":{"writer":"One","branch":"bus/one-v2","legacy_spelling":false}}}')
    return path


def test_collect_batch_carries_topology_derived_lane_identity(tmp_path):
    emitter = load_emitter()
    repo, _, _ = make_repo(tmp_path)
    (repo / "messages" / "0002.md").write_text("message_id: one-10000\nwriter: One\n")
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/0002.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "message"])
    head = git(repo, "rev-parse", "HEAD")
    batch = emitter.collect_projection_batch(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref="refs/heads/bus/one-v2",
        branch_head=head,
        topology_path=write_topology(tmp_path),
    )
    assert batch["lane_identity"] == "one"


def test_collect_batch_rejects_unregistered_lookalike_lane(tmp_path):
    emitter = load_emitter()
    repo, _, _ = make_repo(tmp_path)
    (repo / "messages" / "0002.md").write_text("message_id: one-10000\nwriter: One\n")
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/0002.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "message"])
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(Exception, match="UNREGISTERED_WRITER_LANE"):
        emitter.collect_projection_batch(
            repo,
            repository="thebrazenbeard/chat-communication-bus",
            ref="refs/heads/bus/one-v2-lookalike",
            branch_head=head,
            topology_path=write_topology(tmp_path),
        )
```

- [ ] **Step 2: Run targeted projection tests RED**

Run: `python -m pytest -q tests/radar/test_emit_bus_projection.py`

Expected: failures because `collect_projection_batch` has no `topology_path` argument and no `lane_identity` field.

- [ ] **Step 3: Integrate the validator minimally**

Add:

```python
from radar.writer_lanes import WriterLaneError, validate_writer_lane_commit

DEFAULT_TOPOLOGY = Path(__file__).resolve().parents[1] / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"
```

Extend `collect_projection_batch`:

```python
def collect_projection_batch(..., topology_path: str | Path = DEFAULT_TOPOLOGY, ...) -> dict[str, object]:
    ...
    try:
        lane_identity = validate_writer_lane_commit(repo, ref, branch_head, topology_path)
    except WriterLaneError as exc:
        raise EmitterError(str(exc)) from exc
    ...
    return {
        "projection_version": 1,
        "repository": repository,
        "ref": ref,
        "branch_head": branch_head,
        "lane_identity": lane_identity,
        "files": files,
    }
```

- [ ] **Step 4: Update old emitter tests to use a current v2 test ref and topology fixture where the commit contains a new message**

Do not preserve the old behavior that tolerated an unrelated `README.md` writer-lane commit. Replace that expectation with `WRITER_LANE_PATH_FORBIDDEN:README.md` because the migration intentionally closes that hole.

- [ ] **Step 5: Run projection tests GREEN**

Run: `python -m pytest -q tests/radar/test_emit_bus_projection.py tests/radar/test_writer_lanes.py`

Expected: pass.

- [ ] **Step 6: Commit Task 2**

```bash
git add scripts/radar_emit_bus_projection.py tests/radar/test_emit_bus_projection.py
git commit -m "feat: bind projection to current writer lane"
```

---

### Task 3: Define the v2 topology and historical-lane custody contract

**Files:**
- Modify: `architecture/contracts/RADAR_TOPOLOGY_V1.json`
- Modify: `docs/BRANCH_DISPOSITION.md`
- Create: `architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json`
- Create: `tests/radar/test_writer_lane_v2_artifacts.py`

**Interfaces:**
- Consumes: the same `required_writer_lanes` shape Task 1 reads.
- Produces: one current v2 branch per active identity; explicit historical v1 ref map; a cutover receipt schema that is populated with exact heads before the protected merge/cutover gate.

- [ ] **Step 1: Write failing artifact tests**

```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_topology_uses_v2_current_writer_lanes_and_corrects_brigit_spelling():
    topology = json.loads((ROOT / "architecture/contracts/RADAR_TOPOLOGY_V1.json").read_text())
    lanes = topology["required_writer_lanes"]
    assert lanes["radar"]["branch"] == "bus/radar-v2"
    assert lanes["brigit"]["branch"] == "bus/brigit-v2"
    assert lanes["one"]["branch"] == "bus/one-v2"
    assert len({record["branch"] for record in lanes.values()}) == len(lanes)
    assert all(record["branch"].endswith("-v2") or record["branch"].endswith("-v3") for record in lanes.values())


def test_cutover_contract_preserves_every_predecessor_lane():
    topology = json.loads((ROOT / "architecture/contracts/RADAR_TOPOLOGY_V1.json").read_text())
    cutover = json.loads((ROOT / "architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json").read_text())
    assert set(cutover["historical_writer_lanes"]) == set(topology["required_writer_lanes"])
    assert cutover["historical_writer_lanes"]["brigit"]["branch"] == "bus/bridget-v1"
    assert cutover["protected_effects"]["merge"] is False
    assert cutover["protected_effects"]["provider_cutover"] is False
```

Note: Hephaestus already uses `bus/hephaestus-v2`. Its successor must be `bus/hephaestus-v3` rather than colliding with its current lane; the artifact test deliberately allows `-v3`.

- [ ] **Step 2: Run artifact tests RED**

Run: `python -m pytest -q tests/radar/test_writer_lane_v2_artifacts.py`

Expected: fail because topology still points at legacy lanes and the cutover contract does not exist.

- [ ] **Step 3: Update topology deterministically**

Use these exact current-lane targets:

```text
brigit -> bus/brigit-v2
eight -> bus/eight-v2
five-five -> bus/five-five-v2
five -> bus/five-v2
fng -> bus/fng-v2
four -> bus/four-v2
hephaestus -> bus/hephaestus-v3
masa -> bus/masa-v2
mune -> bus/mune-v2
nine -> bus/nine-v2
one -> bus/one-v2
radar -> bus/radar-v2
seven -> bus/seven-v2
six -> bus/six-v2
thirteen -> bus/thirteen-v2
three -> bus/three-v2
two -> bus/two-v2
vera -> bus/vera-v2
yang -> bus/yang-v2
yin -> bus/yin-v2
```

Add `historical_branch` to each record rather than deleting provenance metadata. For Brigit, preserve `legacy_spelling: true` for the historical ref but set the current branch to the corrected spelling.

- [ ] **Step 4: Create the cutover contract with unambiguous pre-merge state**

The committed source artifact must distinguish planned topology from actual branch creation. Use:

```json
{
  "schema_version": 1,
  "status": "PRE_MERGE_PLANNED",
  "cutover_main_sha": null,
  "historical_writer_lanes": {
    "radar": {"branch": "bus/radar-v1", "head_sha": null},
    "brigit": {"branch": "bus/bridget-v1", "head_sha": null}
  },
  "protected_effects": {
    "merge": false,
    "provider_cutover": false,
    "ruleset_change": false
  }
}
```

Populate every active identity in `historical_writer_lanes`; `null` heads are intentionally truthful before the final live snapshot. Do not fabricate snapshot SHAs in source code.

- [ ] **Step 5: Update branch disposition language**

Mark current v1 lanes as `WRITER_LANE / HISTORICAL_AFTER_V2_CUTOVER` prospectively, state that no force-push/history rewrite is permitted, and list the new topology-designated lane naming scheme. Do not claim cutover has occurred while the PR is unmerged.

- [ ] **Step 6: Run artifact tests GREEN**

Run: `python -m pytest -q tests/radar/test_writer_lane_v2_artifacts.py tests/radar/test_protocol_v2_regressions.py`

Expected: pass without weakening existing protocol assertions.

- [ ] **Step 7: Commit Task 3**

```bash
git add architecture/contracts/RADAR_TOPOLOGY_V1.json architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json docs/BRANCH_DISPOSITION.md tests/radar/test_writer_lane_v2_artifacts.py
git commit -m "docs: define writer lane v2 topology"
```

---

### Task 4: Add source-side CI guard for current writer lanes

**Files:**
- Create: `scripts/radar_validate_writer_lane.py`
- Create: `.github/workflows/writer-lane-guard.yml`
- Modify: `tests/radar/test_live_projection_artifacts.py`

**Interfaces:**
- Consumes: `validate_writer_lane_commit(...)` and topology current-lane map.
- Produces: command-line validation usable by GitHub Actions on v2/v3 lanes.

- [ ] **Step 1: Write failing artifact assertions**

Add:

```python
def test_current_writer_lanes_have_fail_closed_path_guard():
    workflow = (ROOT / ".github/workflows/writer-lane-guard.yml").read_text()
    script = (ROOT / "scripts/radar_validate_writer_lane.py").read_text()
    assert 'branches:\n      - "bus/**"' in workflow
    assert "python scripts/radar_validate_writer_lane.py" in workflow
    assert "github.ref" in workflow
    assert "github.sha" in workflow
    assert "validate_writer_lane_commit" in script
    assert "RADAR_TOPOLOGY_V1.json" in script
```

- [ ] **Step 2: Run the artifact test RED**

Run: `python -m pytest -q tests/radar/test_live_projection_artifacts.py::test_current_writer_lanes_have_fail_closed_path_guard`

Expected: fail because guard files are absent.

- [ ] **Step 3: Implement the CLI**

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from radar.writer_lanes import WriterLaneError, validate_writer_lane_commit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPOLOGY = ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", default=".")
    parser.add_argument("--ref", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--topology", default=str(DEFAULT_TOPOLOGY))
    args = parser.parse_args()
    try:
        identity = validate_writer_lane_commit(args.repo_dir, args.ref, args.head, args.topology)
    except WriterLaneError as exc:
        print(str(exc))
        return 1
    print(f"WRITER_LANE_VALID:{identity}:{args.head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Implement the workflow**

```yaml
name: Writer Lane Guard

on:
  push:
    branches:
      - "bus/**"

permissions:
  contents: read

jobs:
  validate-current-lane:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install -e .
      - run: >-
          python scripts/radar_validate_writer_lane.py
          --repo-dir .
          --ref "${{ github.ref }}"
          --head "${{ github.sha }}"
```

This workflow is inherited by new lanes created from post-merge `main`. It does not retroactively protect old v1 branches that lack the workflow; v1 administrative branch protection/rulesets remain a separate protected-effect gate.

- [ ] **Step 5: Run artifact and validator tests GREEN**

Run: `python -m pytest -q tests/radar/test_live_projection_artifacts.py tests/radar/test_writer_lanes.py`

Expected: pass.

- [ ] **Step 6: Commit Task 4**

```bash
git add scripts/radar_validate_writer_lane.py .github/workflows/writer-lane-guard.yml tests/radar/test_live_projection_artifacts.py
git commit -m "ci: guard current writer lane paths"
```

---

### Task 5: Verify source implementation, open the review PR, then prepare exact post-merge cutover

**Files:**
- Modify if needed after self-review: `docs/superpowers/specs/2026-09-03-writer-lane-v2-migration-design.md`
- Modify if needed after self-review: `architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json`
- No provider files are deployed in this task.

**Interfaces:**
- Consumes: Tasks 1-4.
- Produces: exact-head CI evidence and a Bus PR. Actual v2 branch creation is deferred until after Patrick authorizes/executes the merge so every successor lane can be created from the exact post-merge canonical cut and inherit the guard workflow.

- [ ] **Step 1: Run the complete source verification suite**

Run:

```bash
python -m compileall -q src
python -m pytest -q
python scripts/radar_source_hashes.py
```

Expected: exit 0 for all three commands; no test failures.

- [ ] **Step 2: Verify exact branch diff**

Run:

```bash
git diff --name-status main...HEAD
git log --oneline --decorate main..HEAD
```

Expected: only the spec/plan and implementation files named in Tasks 1-4; no message-history rewrites, provider migrations, credentials, or unrelated files.

- [ ] **Step 3: Open a normal PR to `main`**

PR title: `Migrate writer lanes to topology-bound mailbox generations`

PR body must state:

```markdown
Implements the approved writer-lane v2 migration source contract.

- preserves all v1 writer-lane history unchanged
- adds topology-bound current-lane validation
- makes current lanes mailbox-only append surfaces
- derives source-side lane identity from the topology registry
- defines v2/v3 successor names including corrected `bus/brigit-v2`
- adds a guard workflow inherited by post-merge successor lanes

Not performed:
- merge
- creation or movement of current writer-lane refs
- deletion/rename/force-push of historical lanes
- Supabase deployment/migration
- repository ruleset or branch-protection mutation
- credential or permission changes

Post-merge cutover remains a separate exact-head gate.
```

- [ ] **Step 4: After PR CI, verify the exact PR head**

Use GitHub Actions evidence for both Python 3.11 and 3.12. Do not claim green based on earlier commits.

- [ ] **Step 5: Stop at the merge gate**

Do not merge. Report the exact PR number/head SHA and whether CI is green.

- [ ] **Step 6: Post-merge cutover procedure, only after explicit merge/cutover authority**

When authorized, fresh-read `main` and every topology predecessor lane, populate exact historical head SHAs, then create all successor branches from one exact `cutover_main_sha`. For each new branch verify:

```text
merge-base(new_lane, main_cut) == main_cut
new_lane_head == main_cut
```

Then update the cutover receipt status from `PRE_MERGE_PLANNED` to an exact observed state on a separate source branch/PR. Do not use a provider deployment as proof of Git cutover.

---

## Plan self-review

- Spec coverage: immutable v1 provenance, mailbox-only current lanes, topology registry, corrected Brigit spelling, no routine lane PRs, source guard, branch-derived identity, failure handling, and protected-effect separation are each assigned to explicit tasks.
- Placeholder scan: there are no `TBD`, `TODO`, or unspecified implementation steps; pre-merge `null` SHA values are explicit truth-state markers, not placeholders to be guessed.
- Type/signature consistency: `validate_writer_lane_commit(repo_dir, ref, head, topology_path) -> str` is defined once in Task 1 and consumed unchanged by Tasks 2 and 4.
- Cutover ordering clarification: successor branches are created from the exact post-merge canonical cut so they inherit the guard workflow. This is safer than creating them from pre-merge `main`; no architecture principle changes, and no v1 history is rewritten.
