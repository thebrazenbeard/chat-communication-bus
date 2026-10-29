# Full-portfolio capability audit — 2026-10-29

Event: `project_unfuck_runtime_coordination`  
Coordination: [chat-communication-bus issue #397](https://github.com/thebrazenbeard/chat-communication-bus/issues/397)  
Evidence scope: **connected GitHub inventory and live default-branch SOURCE inspection**, with internal native-subagent hostile review. Not an installed-host, real-model, peer-acknowledgment, or production qualification.

## Portfolio coverage

- Connected owner `thebrazenbeard`: **107 repositories** = **100 active + 7 archived**; **85 public + 22 private**.
- Six disjoint native source-inventory lanes inspected all **100 active** repositories (16, 17, 17, 16, 17, 17). Six further native reviewers challenged inventory metadata, effect security, memory/privacy, cognition, architecture, and release evidence.
- Seven archived: `build-team-2.0`, `skeletonkey`, `entropyinc`, `brigit-unbound`, `bugops`, `conditioning`, `ocd`. Archival is a status, not permission to reactivate.
- Machine-readable snapshot: [portfolio-owner-snapshot-2026-10-29.csv](./portfolio-owner-snapshot-2026-10-29.csv). A separate exact-head file records the point-in-time identities. Fresh-check every affected head before mutation or deployment.
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
| Historical evidence | `deepmemorystorage/main@47681d52`, `redworm/main@1fec17c1`, `temporal/main@f115b97f`, `project-lantern/main@cc78ebfc` | Source-backed historical/audit stores, distinct from current personal memory | Scoped read projections only; never export private transcript into public DMS |
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
- [Vera Mono Draft #155](https://github.com/thebrazenbeard/vera-mono/pull/155) `3c91469ae59a2d1a6cb9652bcdf9e5a6a8c39d71`: dependency PASS, monorepo test run still IN_PROGRESS at reviewer observation; migration/host identity HOLD.
- [CCB private Draft #398](https://github.com/thebrazenbeard/chat-communication-bus/pull/398) `94fdbf26f6195a83514a771ef13f11edd19d7143`: private-overlay-integrity CI FAILED; concealed loader remediation not yet independently admitted. NO MERGE.
- [STM Draft #15](https://github.com/thebrazenbeard/stm/pull/15) `6f9d8f218bf6f55f49ac0c495316f76535ef9994`: no hosted run visible; host memory integration HOLD.
- [MemoryLedger Draft #1](https://github.com/thebrazenbeard/MemoryLedger/pull/1) `06fe39e602e7da67ab2a268450af3d019e9b4b40`: proposal-only; no memory runtime qualified.

**Release decision:** portfolio metadata/source inventory = GO as an audit artifact. Host installation, authority, durable peer/model proof, high-effect runtime and production deployment = HOLD. No model effect, CCB peer ACK, Lappy installation or production write is claimed by this audit. Repo documentation and source checks alone do not clear a deployment gate.

## Next qualified slices

1. Reconcile exact active repository identities and scope; preserve public/private and archived status and source heads.
2. Prototype `roots.candidates.read.v1` and `memory.search.scoped.v1` with host-owned source handles and privacy, never arbitrary path or model-authored authority.
3. Independently test negative grants, stale pinned installation, forged privacy refs, filesystem path substitution, replay-journal replacement and side effects misdeclared read-only.
4. Fix/reconcile device `OUTCOME_UNKNOWN` fence custody and CCB durable peer receipts before any write/device/replay capability.
5. Verify a **real installed host + actual authorized model turn**, not merely CI, before claiming integration or deploying.
