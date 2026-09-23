# Radar Portable Qualification V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace summary-only qualification receipt V1 with a stage-evidentiary V2 receipt and a portable Python qualification engine while preserving the existing no-paid, exact-clean-checkout, external-receipt, and protected-effect boundaries.

**Architecture:** `scripts/radar_qualify.py` becomes the canonical qualification engine and evidence producer. `scripts/radar_local_qualify.ps1` becomes a Windows launcher only. `scripts/radar_validate_qualification_receipt.py` admits only receipt schema V2 whose exact ordered stage evidence and digest match `RADAR_QUALIFICATION_V1.json`, whose toolchain evidence satisfies the contract, and whose source commit/tree still match the same clean checkout.

**Tech Stack:** Python 3.11/3.12, PowerShell launcher, pytest 9.1.1, Git CLI, Deno 2.9.6, Supabase CLI 2.116.0, Docker, PostgreSQL `psql`, JSON/SHA-256.

**Spec:** `docs/superpowers/specs/2026-09-08-radar-portable-qualification-oidc-trust-design.md`

## Global Constraints

- Policy remains `NO_PAID_SERVICES`; private source must not be made public to obtain CI.
- Authoritative qualification mode remains `LOCAL_NO_PAID_SERVICES`.
- Initial authoritative platform profile remains Windows; portability does not automatically authorize Linux/macOS receipts.
- Python 3.11 and 3.12 are both required.
- pip must be exactly 26.2.1.
- Deno must be exactly 2.9.6.
- Supabase CLI must be exactly 2.116.0.
- Docker must be present and healthy; `psql` must be present.
- Qualification starts and ends on the same exact clean Git commit/tree.
- Receipt output must resolve outside the source checkout, including ignored paths.
- A source change after qualification invalidates the receipt and requires a complete rerun.
- No source test, plan, or receipt authorizes merge, provider migration, Edge deployment/configuration, cursor bootstrap, dispatcher activation, billing/account changes, credentials/rulesets, or history rewrite.
- Do not classify Radar GREEN until the full authoritative run succeeds and its V2 receipt is admitted against the same clean checkout.

---

### Task 1: Define receipt V2 as an executable admission contract

**Files:**
- Modify: `architecture/contracts/RADAR_QUALIFICATION_V1.json`
- Modify: `tests/security/test_qualification_receipt_admission.py`
- Modify: `scripts/radar_validate_qualification_receipt.py`

**Interfaces:**
- Consumes: existing qualification mode/toolchain/clean-checkout contract.
- Produces: receipt `schema_version = 2`; exact `required_stage_instances`; `stage_evidence_sha256`; validator helpers `_canonical_stage_evidence_bytes(stages)` and `_validate_stage_evidence(receipt, authority)`.

- [ ] **Step 1: Write failing V2 admission tests**

Extend the temporary qualification contract used by `test_qualification_receipt_admission.py` with this exact ordered list:

```python
"required_stage_instances": [
    "python_compileall:3.11",
    "python_pytest:3.11",
    "radar_source_hashes:3.11",
    "python_compileall:3.12",
    "python_pytest:3.12",
    "radar_source_hashes:3.12",
    "deno_ci",
    "deno_check",
    "supabase_local_start",
    "supabase_db_reset",
    "all_radar_sql_assertions",
    "supabase_local_stop",
]
```

Replace the V1 receipt helper with a V2 helper that emits, for each ordinal, a record shaped exactly as:

```python
{
    "ordinal": ordinal,
    "stage_id": stage_id,
    "started_at_utc": "2026-09-08T01:00:00+00:00",
    "completed_at_utc": "2026-09-08T01:00:01+00:00",
    "exit_code": 0,
    "executable": "test-fixture",
    "stdout_sha256": hashlib.sha256(b"stdout").hexdigest(),
    "stderr_sha256": hashlib.sha256(b"").hexdigest(),
}
```

Add tests that reject each of these independently:

```python
missing one required stage
same stage duplicated in place of another
same complete stage set in the wrong order
any exit_code != 0
ordinal mismatch
invalid/non-UTC stage timestamp
stage completed before stage started
stage_evidence_sha256 mismatch
missing/non-string Docker observed identity
missing/non-string psql observed identity
schema_version == 1
```

The positive fixture must include:

```python
"schema_version": 2,
"toolchain": {
    "python": ["3.11", "3.12"],
    "pip": "26.2.1",
    "deno": "2.9.6",
    "supabase_cli": "2.116.0",
    "docker": "Docker test fixture",
    "psql": "psql test fixture",
},
"stages": stages,
"stage_evidence_sha256": digest,
```

- [ ] **Step 2: Run the focused admission file and verify RED**

Run:

```powershell
py -3.11 -m pytest tests/security/test_qualification_receipt_admission.py -q
```

Expected: V2 positive admission and V2 negative evidence tests fail because the current validator requires schema 1 and does not validate stage evidence.

- [ ] **Step 3: Add V2 structure to the machine-readable qualification contract**

Set `authoritative_qualification.receipt_schema_version` to `2`, add the exact `required_stage_instances` list above, and preserve the existing conceptual `required_stages` list for human grouping. Add:

```json
"stage_evidence": {
  "required": true,
  "ordinal_base": 1,
  "digest": "SHA-256_CANONICAL_JSON",
  "canonical_json": "UTF-8 JSON array, sort_keys=true, separators=[comma,colon], no surrounding whitespace",
  "required_fields": [
    "ordinal",
    "stage_id",
    "started_at_utc",
    "completed_at_utc",
    "exit_code",
    "executable",
    "stdout_sha256",
    "stderr_sha256"
  ]
}
```

Do not freeze a Docker or PostgreSQL version not already present in the contract; require non-empty observed identity strings instead.

- [ ] **Step 4: Implement canonical stage validation**

Add to `radar_validate_qualification_receipt.py`:

```python
def _canonical_stage_evidence_bytes(stages: list[dict[str, Any]]) -> bytes:
    return json.dumps(
        stages,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
```

Implement `_validate_stage_evidence()` to require an exact list, exact count/order, ordinal starting at 1, `exit_code == 0`, non-empty `executable`, 64-lowercase-hex stdout/stderr hashes, valid UTC timestamps with completion >= start, and exact SHA-256 over `_canonical_stage_evidence_bytes(stages)`.

Move top-level toolchain admission to `receipt["toolchain"]`; compare Python/pip/Deno/Supabase exactly to `required_toolchain`, and require non-empty strings for Docker and psql when the contract value is `"required"`.

Change schema admission from hard-coded V1 to:

```python
_expect(receipt, "schema_version", authority.get("receipt_schema_version"))
```

- [ ] **Step 5: Run focused V2 admission tests and verify GREEN**

Run:

```powershell
py -3.11 -m pytest tests/security/test_qualification_receipt_admission.py -q
```

Expected: all receipt-admission tests PASS.

- [ ] **Step 6: Commit**

```bash
git add architecture/contracts/RADAR_QUALIFICATION_V1.json scripts/radar_validate_qualification_receipt.py tests/security/test_qualification_receipt_admission.py
git commit -m "feat: require stage-evidentiary qualification receipts"
```

---

### Task 2: Build the portable qualification evidence engine

**Files:**
- Create: `scripts/radar_qualify.py`
- Create: `tests/security/test_portable_local_qualification.py`

**Interfaces:**
- Consumes: `RADAR_QUALIFICATION_V1.json` V2 stage order/toolchain requirements.
- Produces: `StageEvidence`, `CommandResult`, `canonical_stage_digest(stages)`, `run_stage(...)`, `build_pass_receipt(...)`, and CLI `main(argv)`.

- [ ] **Step 1: Write failing unit tests for evidence generation**

Create tests using injected command callables rather than the real toolchain. Test these exact properties:

```python
run_stage assigns the requested ordinal/stage_id
run_stage hashes exact stdout/stderr bytes
run_stage records a nonzero exit code and raises QualificationError
canonical_stage_digest is stable under repeated serialization
build_pass_receipt refuses a stage sequence that differs from required_stage_instances
build_pass_receipt emits schema_version 2 and the computed stage digest
receipt path inside repo is rejected before writing
```

Use a deterministic fake clock returning UTC-aware datetimes and a fake command runner returning `CommandResult(returncode, stdout, stderr, executable)`.

- [ ] **Step 2: Run the new unit test and verify RED**

Run:

```powershell
py -3.11 -m pytest tests/security/test_portable_local_qualification.py -q
```

Expected: import failure because `scripts/radar_qualify.py` does not exist.

- [ ] **Step 3: Implement the evidence primitives**

Define:

```python
@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    executable: str

@dataclass(frozen=True)
class StageEvidence:
    ordinal: int
    stage_id: str
    started_at_utc: str
    completed_at_utc: str
    exit_code: int
    executable: str
    stdout_sha256: str
    stderr_sha256: str
```

`run_stage()` must capture start/end UTC, execute exactly once, construct evidence even for failure, then raise `QualificationError` if return code is nonzero. `canonical_stage_digest()` must use the same JSON canonicalization as the admission validator.

- [ ] **Step 4: Implement source/external-receipt guards**

Implement helpers that:

```text
resolve Git top-level
read HEAD and HEAD^{tree}
read git status --porcelain --untracked-files=all
reject dirty source at start
reject receipt path equal to or nested under the repo root
recheck HEAD/tree/clean status before receipt emission
```

Use argument lists with `subprocess.run(..., shell=False)` only.

- [ ] **Step 5: Run unit tests and verify GREEN**

Run:

```powershell
py -3.11 -m pytest tests/security/test_portable_local_qualification.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/radar_qualify.py tests/security/test_portable_local_qualification.py
git commit -m "feat: add portable qualification evidence engine"
```

---

### Task 3: Port the actual qualification stages into the Python engine

**Files:**
- Modify: `scripts/radar_qualify.py`
- Modify: `tests/security/test_portable_local_qualification.py`

**Interfaces:**
- Consumes: evidence primitives from Task 2.
- Produces: `qualify(repo_root, receipt_path, profile="windows") -> dict[str, Any]` that executes the exact authoritative stage sequence.

- [ ] **Step 1: Write failing orchestration tests with a recording fake runner**

Assert the generated stage IDs are exactly and only:

```python
[
    "python_compileall:3.11",
    "python_pytest:3.11",
    "radar_source_hashes:3.11",
    "python_compileall:3.12",
    "python_pytest:3.12",
    "radar_source_hashes:3.12",
    "deno_ci",
    "deno_check",
    "supabase_local_start",
    "supabase_db_reset",
    "all_radar_sql_assertions",
    "supabase_local_stop",
]
```

Also prove:

```text
both Python venvs are separate temporary paths
pip is installed as exactly 26.2.1 before project test dependencies
SQL files are sorted by filename and invoked with ON_ERROR_STOP=1
pre-existing Supabase project container/volume/network aborts before destructive start
supabase_local_stop is attempted in finally after any owned start attempt
primary SQL failure is retained if cleanup also fails
receipt is emitted only after cleanup succeeds
```

- [ ] **Step 2: Run orchestration tests and verify RED**

Run:

```powershell
py -3.11 -m pytest tests/security/test_portable_local_qualification.py -q
```

Expected: orchestration assertions fail because `qualify()` does not yet execute the full stage sequence.

- [ ] **Step 3: Port toolchain probes without inventing new version constraints**

Require exact Python minor, pip, Deno and Supabase CLI values from the contract. Run `docker info` as the health gate and capture `docker --version` as the receipt identity. Run `psql --version` and capture its non-empty identity. Store those observed identity strings under `receipt["toolchain"]["docker"]` and `["psql"]`.

- [ ] **Step 4: Port Python/Deno stages**

For each required Python version, create a temp venv, install `pip==26.2.1`, install `-e .[test]`, then evidence-wrap only the three contract stages:

```text
python_compileall:<version> -> python -m compileall -q src
python_pytest:<version> -> python -m pytest -q
radar_source_hashes:<version> -> python scripts/radar_source_hashes.py
```

Run `deno ci` and `deno check index.ts` from `supabase/functions/github-bus-ingest` as `deno_ci` and `deno_check`.

Setup commands needed to prepare a stage are prerequisite operations and must fail the run if unsuccessful, but they are not silently counted as one of the required stage IDs.

- [ ] **Step 5: Port local Supabase ownership/preflight and SQL stages**

Preserve current safeguards from `radar_local_qualify.ps1`:

```text
supabase status must indicate no already-running local stack
docker container inspect supabase_db_chat-communication-bus must not exist
docker volume inspect supabase_db_chat-communication-bus must not exist
no containers/volumes/networks with label com.supabase.cli.project=chat-communication-bus
```

Then execute/evidence:

```text
supabase_local_start -> supabase start
supabase_db_reset -> supabase db reset
all_radar_sql_assertions -> each sorted supabase/tests/radar_*.sql via psql postgresql://postgres:postgres@127.0.0.1:54322/postgres -v ON_ERROR_STOP=1 -f <file>
supabase_local_stop -> supabase stop --no-backup
```

For `all_radar_sql_assertions`, aggregate the exact stdout/stderr bytes from all sorted SQL invocations into that single stage evidence record and fail on the first nonzero invocation while preserving its output.

- [ ] **Step 6: Run portable-engine tests and verify GREEN**

Run:

```powershell
py -3.11 -m pytest tests/security/test_portable_local_qualification.py -q
py -3.12 -m pytest tests/security/test_portable_local_qualification.py -q
```

Expected: PASS on both installed Python versions.

- [ ] **Step 7: Commit**

```bash
git add scripts/radar_qualify.py tests/security/test_portable_local_qualification.py
git commit -m "feat: port Radar qualification stages to Python"
```

---

### Task 4: Reduce PowerShell to a launcher and bind parity/currentness

**Files:**
- Modify: `scripts/radar_local_qualify.ps1`
- Modify: `tests/security/test_no_paid_qualification_consistency.py`
- Modify: `architecture/contracts/RADAR_CURRENT.json`
- Modify: `docs/operator/RADAR_NO_PAID_QUALIFICATION.md`

**Interfaces:**
- Consumes: `scripts/radar_qualify.py` CLI.
- Produces: Windows convenience launcher only; currentness names the Python engine as qualification semantics owner and PowerShell as launcher.

- [ ] **Step 1: Write failing parity/static contract tests**

Require that the PowerShell file contains an invocation equivalent to:

```powershell
py -3.11 "$PSScriptRoot\radar_qualify.py" @args
```

and does **not** contain qualification semantics such as:

```text
supabase db reset
deno check
pytest
radar_source_hashes.py
RADAR_TRUSTED_PROJECTOR_SHA
```

Require `RADAR_CURRENT.json` and `RADAR_QUALIFICATION_V1.json` to name `scripts/radar_qualify.py` as the engine and `scripts/radar_local_qualify.ps1` as the Windows launcher.

- [ ] **Step 2: Run consistency tests and verify RED**

Run:

```powershell
py -3.11 -m pytest tests/security/test_no_paid_qualification_consistency.py -q
```

Expected: FAIL because PowerShell still owns qualification semantics.

- [ ] **Step 3: Replace PowerShell implementation with a thin launcher**

Keep only argument declaration/forwarding, `ErrorActionPreference = "Stop"`, Python availability check, and exit-code propagation. Do not duplicate stage ordering or tool version logic.

- [ ] **Step 4: Update currentness/operator documentation**

State explicitly:

```text
Python engine defines qualification semantics.
PowerShell is the authoritative Windows launcher for the currently authorized platform profile.
A runnable engine on another OS is not automatically an authoritative platform profile.
Receipt V2 stage evidence is required before GREEN.
```

- [ ] **Step 5: Run consistency tests and verify GREEN**

Run:

```powershell
py -3.11 -m pytest tests/security/test_no_paid_qualification_consistency.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/radar_local_qualify.ps1 tests/security/test_no_paid_qualification_consistency.py architecture/contracts/RADAR_CURRENT.json docs/operator/RADAR_NO_PAID_QUALIFICATION.md
git commit -m "refactor: make PowerShell a qualification launcher"
```

---

### Task 5: Custody-bind the new engine and qualification regressions

**Files:**
- Modify: `tests/security/test_reproducible_ci_custody.py`
- Modify: `architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json`

**Interfaces:**
- Consumes: new engine/test paths from Tasks 2–4.
- Produces: next monotonic custody version containing both new trust roots.

- [ ] **Step 1: Write the failing custody expectations**

Advance the expected custody version by one from the version present at execution time and require:

```text
scripts/radar_qualify.py
tests/security/test_portable_local_qualification.py
```

Do not remove existing custody roots.

- [ ] **Step 2: Run the custody test and verify RED**

Run:

```powershell
py -3.11 -m pytest tests/security/test_reproducible_ci_custody.py::test_source_custody_manifest_covers_dynamic_sql_and_fixed_trust_roots -q
```

Expected: FAIL until the manifest is advanced.

- [ ] **Step 3: Advance custody monotonically and add the two paths**

Update `RADAR_SOURCE_CUSTODY_V1.json` to the exact version expected by the regression and append both paths once.

- [ ] **Step 4: Run custody test and verify GREEN**

Run the focused custody test above. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/security/test_reproducible_ci_custody.py architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json
git commit -m "contract: custody-bind portable qualification engine"
```

---

### Task 6: Source qualification gate and Hephaestus review packet

**Files:**
- Modify only if a test exposes a real defect: files from Tasks 1–5.
- Bus append after source cut is stable: `messages/<next>-radar-to-hephaestus-qualification-v2-review.md` on `bus/radar-v2`.

**Interfaces:**
- Consumes: all V2 source work.
- Produces: one exact source cut for independent Hephaestus `ACCEPT | RETURN | BLOCKED` review; does not itself produce a full authoritative PASS receipt unless executed on the frozen Windows toolchain.

- [ ] **Step 1: Run all qualification-focused Python tests**

Run on Python 3.11 and 3.12:

```powershell
py -3.11 -m pytest tests/security/test_qualification_receipt_admission.py tests/security/test_portable_local_qualification.py tests/security/test_no_paid_qualification_consistency.py tests/security/test_reproducible_ci_custody.py -q
py -3.12 -m pytest tests/security/test_qualification_receipt_admission.py tests/security/test_portable_local_qualification.py tests/security/test_no_paid_qualification_consistency.py tests/security/test_reproducible_ci_custody.py -q
```

- [ ] **Step 2: Run full Python suite and source hashes**

```powershell
py -3.11 -m pytest -q
py -3.12 -m pytest -q
py -3.11 scripts/radar_source_hashes.py
py -3.12 scripts/radar_source_hashes.py
```

These are source-side gates; they do not substitute for Deno/local-Supabase stages.

- [ ] **Step 3: Fresh-read exact head/tree and classify honestly**

If the full frozen Deno/Supabase/PostgreSQL toolchain has not run, status remains `LOCAL_EXECUTION_PENDING / NOT GREEN`. Do not populate `latest_qualification_receipt` and do not freeze a successor projector anchor.

- [ ] **Step 4: Send Hephaestus a completion packet**

Use canonical `intended_recipient: Hephaestus`. Include exact branch/head/tree, changed paths, RED/GREEN evidence actually executed, unavailable stages, custody version, and explicit no-protected-effect boundary. Request `ACCEPT`, `RETURN`, or `BLOCKED` for the V2 qualification implementation scope only.

- [ ] **Step 5: Only after Hephaestus review, run the real authoritative Windows qualification when that frozen toolchain is available**

Invoke the thin Windows launcher with an external receipt path. Then admit that exact V2 receipt from the same clean checkout. Any source change after the run invalidates it and requires a complete rerun.
