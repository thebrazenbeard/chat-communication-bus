# Full GitHub portfolio source-capability inventory and qualification — 2026-10-29

Event: `project_unfuck_runtime_coordination`  
Coordination: [chat-communication-bus issue #397](https://github.com/thebrazenbeard/chat-communication-bus/issues/397)  
Evidence scope: **connected GitHub inventory and live default-branch SOURCE inspection**, with internal native-subagent hostile review. Not an installed-host, real-model, peer-acknowledgment, or production qualification.

## Portfolio coverage

- Connected owner `thebrazenbeard`: **107 repositories** = **100 active + 7 archived**; **85 public + 22 private**.
- Six disjoint native source-inventory lanes inspected all **100 active** repositories (16, 17, 17, 16, 17, 17). Six further native reviewers challenged inventory metadata, effect security, memory/privacy, cognition, architecture, and release evidence.
- Seven archived: `build-team-2.0`, `skeletonkey`, `entropyinc`, `brigit-unbound`, `bugops`, `conditioning`, `ocd`. Archival is a status, not permission to reactivate.
- Machine-readable snapshot: [portfolio-owner-snapshot-2026-10-29.csv](./portfolio-owner-snapshot-2026-10-29.csv). [The exact-head manifest](./portfolio-exact-heads-2026-10-29.json) records all 107 point-in-time default heads; [the source-capability ledger](./portfolio-source-capabilities-100-2026-10-29.json) records 100 active source classifications with code paths, proposed adapters, effects, privacy, authority, blockers and evidence class. All must receive independent exact-head review before merging. Fresh-check each affected head before mutation or deployment.
- The old `vera-control-plane` portfolio registry (2026-09-23; 59 entries, 24 public/35 private) is NOT authoritative today. Sixteen visibility flags disagree with current GitHub. Three names are absent verbatim: `project-achilles`, `vera_ark`, `vera_model_training`. Do not infer successor identity from similar names.

## Coordination contract

A repository's presence, model-facing schema, source implementation, installed adapter, authority and observed effect are different states.

1. **IMPLEMENTED**: exact source commit and bounded code path identified.
2. **INSTALLED**: trusted host attests adapter ID, build digest and pinned implementation.
3. **ADVERTISED**: actor-filtered typed descriptor with input/output schema, effect ceiling, privacy ceiling and currentness.
4. **AUTHORIZED**: independent host grant binds principal, tenant/project, identity, subject, exact operation/request digest, scope, deadline and revocation epoch.
5. **DISPATCHED**: constrained adapter runs behind a durable, host-derived one-use effect fence.
6. **RECONCILED**: durable receipt binds actual outcome to request and exact receiver; unknown outcomes stay quarantined with no blind replay.
7. **MODEL_WITNESSED**: separately verify the intended model consumed and responded to the delivered result.

Source metadata does NOT authorize execution. Documentation-only and archived repositories need no fabricated `tool_call` endpoint. The host owns the shared gateway; repos expose real, independently admitted domain adapters as appropriate.

## Source-grounded capability candidates and holds

| Domain | Current example sources | Source assessment | Host disposition |
|---|---|---|---|
| Origin discovery | `roots/main@d6166522` | CLI was restored by #17; candidate origins still `NOT_ASSESSED`, CLI accepts arbitrary `--source` and `--include-content` | Only host-owned allowlisted handles, bounded output and privacy checks |
| Evidence intake | `ingest/main@8ffb70c7` | Immutable CAS capture and receipts; root bootstrap/ancestor path race not closed by latest GitHub streaming change | Separate file/network/write grant; no Lappy intake retry until confinement verified |
| Memory policy | `vera-mono/main@5be71f4`, `stm/main@c40431c7` | Ledger authority/privacy refs are NOT self-authenticating; STM day30 review eligibility/day45 local expiry not installed | No direct model-callable `MemoryLedger.admit` or unreviewed private import |
| Historical evidence | `deepmemorystorage/main@47681d52`, `redworm/main@1fec17c1`, `temporal/main@f115b97f`, `project-lantern/main@cc78ebfc` | Source-backed historical/audit stores, distinct from current personal memory | Scoped read projections only; public DMS repository visibility does not attest any authorized private storage destination; do not export private transcripts without destination/consent proof |
| Activity ledger | `blotter/main@c31c93ce` | Source implements `begin_turn`, `latest20`, `record_activity` | Require installed actor-bound MCP adapter; no universal hook assumed |
| Runtime and orchestration | `portal/main@bac96ad`, `pre-active/main@ed25245`, `vera-mono/main@5be71f4` | Route metadata and suggested tools are NOT host grants; Vera Mono chat currently rejects model tool calls | Host-owned exact descriptor/authority fence and witnessed model return required |
| Workstations | `executor/main@c952180`, `workbridgecommander/main@27d83f47` | Full machine effects; 120-second timeout can release lane while child remains active | HOLD unrestricted exposure; quarantine `OUTCOME_UNKNOWN`, host-derived collision fences |
| Bounded command transport | `WorkBridgeMCP/main@3efd1b3d`, `workbridge/main@eb74be3` | Bounded native Go mode distinct from full Desktop Commander duplicate | Require exact mode and admitted path/executable grants |
| Communications | `ccb-core/main@93fe223`, private `chat-communication-bus/main@eca2b241` | Private overlay pins older core; source ACK is not peer proof or model response | Authenticated receiver identity, durable recovery and model witness required |
| Database | `sql-connectome/main@39a95530` | Authenticated MCP defaults and SELECT guard; static development bearer not production authorization | No inferred Supabase cutover, cross-tenant RLS or live database grant |
| Model/cognition | `bt2/main@b3d2a0f`, `model-training/main@d154098`, `labyrinth/main@39a95ac`, `meta/main@f8f2a1b`, `humility/main@6c5a1f7` | Proxy prompting is not weight training; toy calibration uses supplied labels; Labyrinth opt-in LoRA code does not prove gain | No model identity/training/feedback-loop qualification from source alone |
| Creative/data/research | `wreckforge`, `testament`, `on-theo`, `num-ta-reen`, `suicidal-phoenix` and other source-only repos | Valuable domain sources; no unconditional executable effects | Reference/read-only source adapters only if needed |

### Hostile release findings

> **Workstation fence gap:** `executor` and `workbridgecommander` free execution and resource locks when a remote call times out, although its downstream command may continue. In source this permits conflicting follow-up operations after an `OUTCOME_UNKNOWN` result. No live exploit was asserted.

> **Memory-admission trust gap:** `vera-mono`'s ledger accepts higher-level `authority_ref` and `privacy_ref` strings but does not authenticate them itself. DMS has an operator-only `--audit-all-privacy` option. Neither must be exposed as an ordinary model tool argument.

> **Causal effect gap:** `pre-active` tool metadata calls mutation `False` by default and executes registered nonmutating callbacks; no host-level guarantee makes an arbitrary callback actually effect-free. Model descriptions cannot certify effects.

> **Communication gap:** `ccb-core` receipt marks model response false; it has crash-after-ledger-commit recovery and authorization-revocation races. A GitHub issue comment is coordination, not authenticated receiver acknowledgment.

## Current exact-head release signals

- [Ingest Draft #33](https://github.com/thebrazenbeard/ingest/pull/33) `1710204fd43dcbb563737cb7d69c322ec1bb6e25`: CI PASS, path bootstrap/confinement and real Windows custody HOLD.
- [CCB Core Draft #37](https://github.com/thebrazenbeard/ccb-core/pull/37) `65fb9d925039f55f4efcdbc7029f0e55785930e5`: CI/Dependency Review PASS, real receiver and receipt recovery HOLD.
- [Vera Mono Draft #155](https://github.com/thebrazenbeard/vera-mono/pull/155) `3c91469ae59a2d1a6cb9652bcdf9e5a6a8c39d71`: dependency PASS, monorepo run 40906364620 **FAILED** on Windows pytest (9 failures involving Windows SQLite file-handle cleanup); Ubuntu passed; migration/host identity HOLD.
- [CCB private Draft #398](https://github.com/thebrazenbeard/chat-communication-bus/pull/398) `94fdbf26f6195a83514a771ef13f11edd19d7143`: private-overlay-integrity CI FAILED; concealed loader remediation not yet independently admitted. NO MERGE.
- [STM Draft #15](https://github.com/thebrazenbeard/stm/pull/15) `6f9d8f218bf6f55f49ac0c495316f76535ef9994`: no hosted run visible; host memory integration HOLD.
- [MemoryLedger Draft #1](https://github.com/thebrazenbeard/MemoryLedger/pull/1) `06fe39e602e7da67ab2a268450af3d019e9b4b40`: proposal-only; no memory runtime qualified.

**Release decision:** 107-row owner metadata was independently reconciled; 107 source heads and 100 source-capability rows have been committed and internally checked for uniqueness, active coverage and pinned SHA references. Fresh independent audit of these NEW files is still pending. PR #399 private-overlay-integrity workflow **FAILED** at earlier head 33ab1ae (run 40908511451, precise failure reason UNKNOWN due inaccessible job log); check the newest exact head separately. Merge remains HOLD until all checks and review pass. Host installation, authority, durable peer/model proof, high-effect runtime and production deployment = HOLD. No model effect, CCB peer ACK, Lappy installation or production write is claimed by this audit. Repo documentation and source checks alone do not clear a deployment gate.

## Next qualified slices

1. Reconcile exact active repository identities and scope; preserve public/private and archived status and source heads.
2. Prototype `roots.candidates.read.v1` and `memory.search.scoped.v1` with host-owned source handles and privacy, never arbitrary path or model-authored authority.
3. Independently test negative grants, stale pinned installation, forged privacy refs, filesystem path substitution, replay-journal replacement and side effects misdeclared read-only.
4. Fix/reconcile device `OUTCOME_UNKNOWN` fence custody and CCB durable peer receipts before any write/device/replay capability.
5. Verify a **real installed host + actual authorized model turn**, not merely CI, before claiming integration or deploying.

## Required per-repository capability ledger (not yet committed)

The 107-row owner metadata snapshot, 107 default heads and 100 per-active-repository source-capability rows are now committed in this Draft PR. The 100-row ledger is **internal native source review**, not installed-host qualification. Each active repo has a row with: `repo`, `default_branch`, `head_sha`, `source_kind`, `actual_role`, `verified_entrypoint_paths`, `exposure_kind`, `proposed_adapter`, `side_effect_ceiling`, `privacy_scope`, `authority_source`, `installed_host_evidence`, `known_blockers`, `license_and_training_permission`, `evidence_class`, `reviewer`, `verified_at`. Unknown fields must say `UNKNOWN`, not be inferred from names or visibility. Reviewer-defined labels are not a standardized validated registry schema; the source rows are audit evidence and adapter proposals, not executable descriptors. Coverage includes visual/audio (`vision`, `ears`, `mediaphile*`), safety (`firesafe`, `human-shield`, `driftguard`, `tattler`), devices (`RSLinux`, `vera-synology`), identity/cognition, research and creative domains. Public visibility does NOT imply open license or permission to train models.

## Hostile negative-test register (all pending runtime evidence)

| Scenario | Required observed result |
|---|---|
| Forged actor/project/privacy scope in a model argument | 403/deny before adapter invocation, zero effects |
| Stale descriptor source SHA or installed build digest | Fail closed |
| Revocation epoch changes after authorization but before commit | Atomic abort or durable conflict reconciliation |
| `mutation=false` callback attempts external write | Trusted confinement blocks write; not a declared-self-report |
| Roots source changed to an unauthorized symlink/junction, `--include-content` requested | No escaped file content |
| Remote effect runs past 120-second timeout and second conflicting request starts | Second request remains fenced until independently reconciled |
| Replay journal replaced with syntactically valid empty file | Host startup rejects untrusted journal state |
| CCB ledger ACK exists but no model response | `model_response_verified` remains false |
| Model injects DMS `--audit-all-privacy` | Privileged option rejected by host |
| Crash after durable effect but before receipt | Exact trusted readback or `OUTCOME_UNKNOWN`; no blind retry |

**Qualification discipline:** these are proposed tests and expected outcomes, not executions or passing results. No runtime effect, external provider review or host deployment is claimed.
