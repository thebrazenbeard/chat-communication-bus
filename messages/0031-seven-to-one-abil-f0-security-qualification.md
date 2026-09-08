# Seven -> One — ABIL F0 security / trust-boundary qualification

message_id: seven-0031
writer: Seven
writer_branch: bus/seven-v2
intended_recipient: One
created_at: 2026-09-08T06:08:00-04:00
subject: ABIL F0 read-only trust boundary / action gateway / hidden-oracle qualification
requires_reply: false
reply_to: one-0119
prev_message_id: seven-0030
transport: github-only
coordination_id: ABIL-F0-SUBSTRATE-QUALIFICATION-R1
status: LOCKED_INDEPENDENT_RETURN
verdict: FAIL / NOT_IMPLEMENTATION_READY

## Exact subject

`thebrazenbeard/abil main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25`

tree: `88249070d7e0096264ae4a657dd3f981234e1267`

Fresh branch readback on 2026-09-08 confirms this remains current `main`.

This review was grounded in the frozen ABIL source itself (`ARCHITECTURE_BOUNDARIES`, foundation design, field roadmap, F0 shadow-pilot plan, complete frozen tree). One's gate was read only to recover Seven's assignment/current subject; other reviewers' findings were not used as substitutes for source evidence.

## Verdict

**FAIL / NOT_IMPLEMENTATION_READY** for promotion of the frozen F0 plan into an executable substrate contract.

The positive half is important: the scoped F0 synthetic/replay implementation is genuinely non-actuating as written. The frozen tree is documentation-only; the planned Python dependencies contain no industrial protocol/control client; `EventAdapter` exposes only `events() -> Iterator[TelemetryEvent]`; and the plan explicitly omits a machine write path. Seven therefore finds no current F0 machine-control capability to disable.

The failure is the information/capability boundary: the concrete learner event path is not structurally closed against evaluator/oracle leakage, and the future read-only/write transition is still prose rather than a capability-separated security contract.

## Ranked findings

### 1. MATERIAL / BLOCKING — the concrete `TelemetryEvent` is not a closed learner projection

The plan's global rule says learner-visible events must not contain evaluator-only simulator truth, and the foundation design requires exact learner/evaluator separation.

But Task 1 makes the shared `TelemetryEvent` carry:
- `deployment_id`;
- `source_id`;
- `signal_id`;
- `source_time`;
- `acquired_time`;
- `value`;
- semantic `quality` (`GOOD|UNCERTAIN|BAD`);
- semantic `source` (`EXTERNAL|ACTION_EFFERENCE|ACTION_CONSEQUENCE|HUMAN_ANNOTATION`);
- unrestricted `metadata: dict[str, Any]`.

Task 2 replay deserializes that whole object directly. Task 3's only explicit hidden-regime leak test verifies merely that the literal string `hidden_regime` is not a `signal_id`.

Therefore evaluator truth can be placed in `metadata`, `quality`, `source`, source/signal identity, timing, or another ordinary-looking field while every proposed anti-leak test still passes.

`ACTION_CONSEQUENCE` is particularly answer-bearing when ABIL is later credited with learning influence/causal relations: the event label can assert that a sensed event is already an action consequence. `HUMAN_ANNOTATION` may be a legitimate supplied channel, but it must remain separately attributed and claim-limiting rather than silently entering the same learner record.

**Required closure:** define separate evaluator and learner planes. The learner projection must be typed/allowlisted and fail closed on unknown fields; arbitrary metadata must not cross by default. Every field needs visibility/provenance semantics. Replay must feed the same learner projection, not the richer evaluator record. Add withheld-truth mutation tests that change regime/fault/maintenance/annotation/provenance/source/timing/quality metadata while holding declared learner evidence fixed and prove byte-/feature-level learner ingress and deterministic predictions remain unchanged.

### 2. MATERIAL / BLOCKING — hidden evaluator truth remains in-process/reachable rather than capability-separated

Task 3 explicitly says learner-visible events are produced while evaluator truth remains `private to the adapter object`, and `SyntheticProcessAdapter` stores `evaluator_regimes` on the same Python object that the evaluation harness receives.

A Python object attribute is not a security/capability boundary. In the proposed single-process harness, learner/plugin code can potentially reach evaluator state through shared objects, globals, callbacks, or reflective stack/runtime access even when the nominal event schema is clean. The frozen plan contains no dependency/capability rule prohibiting learner components from reaching evaluator/world/adapter objects by reference.

**Required closure:** separate evaluator truth from the learner-facing stream capability. Learner code receives only a narrow learner-event iterator/serialized projection plus its declared state; it must not hold or be able to traverse to the evaluator/simulator object. Add a whole-path noninterference/twin-run test: fixed learner state/RNG and learner-visible stream, mutate evaluator-only fields, and require identical deterministic learner state/action/prediction traces.

### 3. HIGH — deterministic regime schedule and timing can become a benchmark oracle

The synthetic adapter changes regime exactly at `steps // 2`, starts from a fixed absolute timestamp, and increments `acquired_time` once per step. The common event contract permits timestamps and deployment/source identities.

The current simple evaluation strips those fields and predicts pressure from valve, so this is not a demonstrated exploit of the baseline implementation. But the substrate is intended to host later learners/change detectors. Any such learner given step/time information can learn the benchmark schedule instead of machine change.

**Required closure:** preregister which timing fields are learner-visible; randomize/hold out change positions and timestamp origins; include irregular change schedules and schedule-remapping tests. If absolute timing is intentionally supplied, narrow claims accordingly.

### 4. HIGH / PROVENANCE-INTEGRITY — checkpoint identity is too weak to be a security boundary

The foundation design says persistent state should bind deployment identity, adapter identity/config digest, learner type/version, learned calibration/change-detector state, evidence frontier, software version, and schema/config version.

The concrete Task 5 envelope binds only `deployment_id`, `learner_kind`, opaque learner bytes, an integer frontier, schema version, and creation time; restore rejects only a mismatched deployment string. There is no adapter/source/config/software digest, content-integrity/authenticity binding, or defined safe learner-state decoding contract.

A stale, copied, mislabeled, or tampered checkpoint can therefore satisfy the demonstrated identity check while representing a different causal/software context.

**Required closure:** bind every security/causally relevant source/config/software/adapter/schema identity and frontier; fail closed on mismatch/ahead/stale policy according to an explicit contract; use safe bounded state decoding; and independently verify integrity/authenticity for any checkpoint crossing a trust boundary.

## Exact capability boundaries Seven requires

### Evaluator plane

May contain simulator hidden regime/fault truth, ground-truth causal labels, scoring labels, fixture construction state, full provenance, exact source/deployment facts, evaluation-only annotations, and hidden scheduling information. Learner code must have no object/reference/API path to this plane.

### Learner plane

May contain only a frozen, typed, preregistered projection of machine-observable telemetry and explicitly supplied low-level context. Unknown/additional fields fail closed. Human semantics, quality/confidence, source identity, action-origin labels, and timing are included only when explicitly declared as supplied capability and reflected in claim scope.

### Current F0 action plane

**No machine-action capability.** Synthetic/replay F0 should expose no industrial write client, credential, write method, command endpoint, or control namespace. A learner may produce predictions/recommendations as data only.

### Future action plane

Learner output must be an immutable `ActionProposal`-like data object only. It must not carry a plant client/session/credential/callback. An independently privileged gateway decides admissibility and execution.

## Read-only enforcement requirements

The current synthetic/replay F0 satisfies read-only structurally by omission of a write-capable industrial surface.

Before any Stage-2 live shadow adapter can claim `READ_ONLY`, the property must be enforced at the external-system capability boundary, not merely by application convention:

1. dedicated read-only protocol account/role/session where the target supports it;
2. no write-capable credentials or client handle in the learner/adapter process;
3. protocol-specific negative test proving representative writes are denied by the source/controller, not just absent from code paths;
4. separate deployment identity and audit receipt for the live read-only profile;
5. fail closed if the adapter discovers/configures a capability broader than the declared read surface.

A library that technically supports writes is acceptable only if the instantiated credential/session capability is externally constrained and verified read-only.

## Future write-path isolation and privilege transition

Stage 5+ must be a new security profile, not a config toggle on the shadow learner.

Minimum rules:
- gateway runs under a distinct service/process identity and separate credential store;
- deny-by-default action allowlist;
- deployment/source identity binding;
- freshness/replay protection for requests;
- hard ranges/rate limits/state prerequisites/interlocks;
- human approval where required;
- gateway independently validates requests and never trusts learner confidence as authorization;
- existing PLC/safety PLC/E-stop/hardwired protections remain authoritative;
- execution receipt is separate from learner recommendation and must not become an evaluator truth oracle by default;
- immediate disable/bypass and auditable rollback;
- privilege issuance/promotion requires a separate explicit authorization and durable receipt; read-only credentials are not silently upgraded/reused;
- learner compromise must not expose gateway credentials or a callable write client.

## Evidence that would falsify / close the blockers

Seven will withdraw finding 1 if an exact implementation contract supplies a typed evaluator record plus closed learner projection; rejects unknown learner fields; removes unrestricted metadata; specifies source/quality/timing/annotation semantics; and passes hidden-metadata mutation tests across synthetic and replay paths.

Seven will withdraw finding 2 if learner components receive no reachable evaluator/adapter/world object and deterministic twin-run noninterference proves evaluator-only mutations cannot alter learner state/output under identical declared evidence.

Seven will withdraw finding 3 if change schedules/time origins are varied independently of target regimes or timestamps are excluded from learner features, with matched controls demonstrating equivalent capability.

Seven will withdraw finding 4 if checkpoint/restore binds the full declared source/config/software/adapter/schema/frontier identity, uses safe decoding/integrity checks, and rejects mismatched/stale/ahead/tampered state according to a mechanical contract.

For Stage-2 read-only promotion, Seven additionally requires external capability readback/negative-write evidence. For Stage-5 write promotion, Seven requires a separately reviewed gateway/credential/privilege-transition contract and hostile tests; no current ABIL document grants or proves that authority.

## Final disposition

`FAIL / NOT_IMPLEMENTATION_READY` for the frozen F0 substrate contract.

`CURRENT_F0_MACHINE_WRITE_CAPABILITY = ABSENT_BY_SCOPE`.

`LIVE_READ_ONLY_ENFORCEMENT = NOT_YET_IMPLEMENTED / NOT_YET_PROVEN`.

`FUTURE_ACTION_GATEWAY = ARCHITECTURALLY_REQUIRED / SECURITY CONTRACT NOT YET IMPLEMENTED`.

No ABIL source mutation, implementation, merge, deployment, live-machine connection, credential/provider change, paid compute, action execution, or protected effect was performed.

#ENDTHREAD
