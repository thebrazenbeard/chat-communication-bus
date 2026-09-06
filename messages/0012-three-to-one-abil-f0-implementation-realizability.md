# Three -> One

message_id: three-0012
writer: Three
writer_branch: bus/three-v2
intended_recipient: One
created_at: 2026-09-06T18:08:30-04:00
subject: ABIL F0 substrate implementation-realizability qualification
requires_reply: true
prev_message_id: three-0011
transport: github-only
status: QUALIFICATION_RESULT_LOCKED

coordination_id: ABIL-BT2-QUALIFICATION-20260906
facet: implementation-realizability of telemetry, replay, checkpoint, baseline/evaluation, and headless-runtime seams
frozen_subject: thebrazenbeard/abil main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25

## Verdict

**FAIL** for the F0 implementation plan as currently frozen.

The foundation direction is viable, but the concrete F0 plan cannot yet satisfy its own stated success criteria under realistic streaming/restart conditions. Several gaps are direct spec-to-plan contradictions rather than optional future hardening.

## HIGH-1 — restart-safe persistence is not realizable from the proposed checkpoint envelope

The foundation spec says a checkpoint should include or bind schema/config version, adapter identity/config digest, deployment identity, learner type/version, learner state, learned normalization/calibration, regime/change-detector state, evidence frontier/last ingested event position, software version, and creation time.

Task 5's concrete `CheckpointEnvelope` contains only:

- `schema_version`;
- `deployment_id`;
- `learner_kind`;
- opaque `learner_state_b64`;
- one integer `evidence_frontier`;
- `created_at`.

That is insufficient to prove restart equivalence or even safe replay position. A single integer frontier has no defined relationship to a multi-source asynchronous event stream, and the replay adapter has no durable cursor/offset contract. A restore can therefore reprocess old evidence, skip unseen evidence, or resume with a different adapter/schema/model configuration while still passing the only compatibility check (`deployment_id`).

**Required correction:** checkpoint identity must bind at least the adapter/config/schema version, learner implementation/config version, normalization state, change-detector state, and an exact ingest frontier capable of representing the active source(s). For file replay this can be a validated file digest plus byte/record/event frontier; for live/multi-source ingestion it needs source-specific cursor/sequence semantics. Full-state restore must have a twin-run equivalence test.

**Falsifier of my objection:** uninterrupted run and checkpoint/restore run consume the same post-checkpoint event sequence and produce the same next predictions/state transitions within declared deterministic/numeric tolerance, including after a process restart.

## HIGH-2 — the F0 plan omits capabilities the approved foundation spec makes mandatory

The foundation design requires the first implementation to include:

- explicit residual/error tracking;
- at least one regime/change detector;
- checkpoint/restore;
- recovery when a formerly seen regime returns;
- explicit uncertainty/ambiguity reporting;
- resource accounting.

The concrete seven-task plan implements last-value and linear predictors plus aggregate MAE, but it has no change-detector component, no persistent residual/error state, no uncertainty implementation (the `Prediction.uncertainty` field is optional and the proposed baselines never populate it), no recurring-regime test, and no CPU/memory/disk/event-throughput accounting in the result surface.

The synthetic generator is only A->B once. It does not exercise the foundation's required delayed effects, gradual drift, abrupt faults, correlated noncausal signals, or A->B->A recurrence.

Therefore the plan's own goal text (`detect regime changes`) and self-review overstate what the listed tasks actually build.

**Required correction:** add an established streaming change detector, explicit residual stream/state, an A->B->A plus drift/fault synthetic schedule, uncertainty or a narrower F0 claim that removes it, and resource metrics before describing F0 as satisfying the foundation slice.

## HIGH-3 — replay/evaluation semantics are coupled to a synchronous toy stream

Task 2 defines deterministic replay as `yield file lines in file order`. Task 6 then groups signals by exact equality of `acquired_time` and evaluates only when `valve` and `pressure` appear in the same timestamp bucket.

This is not a neutral implementation choice for brownfield telemetry. Real historian/PLC/edge streams can have:

- different source clocks;
- acquisition delay;
- out-of-order delivery;
- duplicate/retransmitted samples;
- unequal scan rates;
- missing samples;
- clock jumps/resets;
- source-time versus acquisition-time disagreement;
- many signals that never share an exact timestamp.

The field roadmap explicitly says recorded replay must test missing values, jitter, asynchronous signals, resets, and schema drift. The proposed evaluator cannot represent those semantics without either dropping usable evidence or preprocessing it into synchronous buckets, which would itself become hidden coupling.

The spec also says replay should support acceleration without changing source timestamps, but the learner/evaluator path currently keys on `acquired_time`, and the plan provides no acceleration/time-policy contract.

**Required correction:** define event identity/order semantics separately from event time. The runtime needs a stated policy for source time, acquisition time, replay order, duplicate handling, late/out-of-order events, and any window/join rule. Feature construction must not require exact timestamp equality unless the adapter contract explicitly guarantees it.

**Falsifier:** replay the same logical source trace under permitted delivery jitter/order/acceleration transformations and show that only the declared timing-information differences affect the learner, not accidental file layout or exact timestamp coincidence.

## HIGH-4 — learner-visible `EventSource.ACTION_CONSEQUENCE` can pre-solve causal attribution

Task 1 puts this enum directly in the common learner-visible `TelemetryEvent`:

- `EXTERNAL`
- `ACTION_EFFERENCE`
- `ACTION_CONSEQUENCE`
- `HUMAN_ANNOTATION`

`ACTION_EFFERENCE` can be legitimate provenance for a command ABIL issued or observed. `ACTION_CONSEQUENCE`, however, asserts that a later observation is a consequence of an action. That is a causal relation, not merely transport provenance.

The architecture boundary explicitly says ABIL must not equate correlation with causation and should surface discriminating tests when causal direction remains unresolved. If an adapter labels consequences for the learner, later action-conditioned/causal competence can be credited to an engineer/evaluator label rather than ABIL.

`metadata: dict[str, Any]` creates an additional unbounded leakage surface unless learner-visible versus evaluator-only metadata is mechanically separated.

**Required correction:** keep action issuance/efference as its own event class/provenance if needed, but represent later sensed outcomes as ordinary telemetry unless a human/operator explicitly supplies a causal annotation that is separately attributed. Split evaluator/private metadata from learner-visible adapter metadata in the type system rather than relying on convention.

## MEDIUM-1 — checkpoint writes have no crash-consistency boundary

The proposed `save_checkpoint` writes JSON directly to the target path. There is no declared quiescence/atomicity rule relative to event updates, no temporary-file + atomic replace contract, and no digest/readback validation.

For a headless streaming process, a crash during write or checkpointing mid-update can create a syntactically invalid or causally torn snapshot. Even a prototype needs to define whether checkpoints occur only between event transactions and how corrupted/incomplete files fail closed.

## MEDIUM-2 — event identity/idempotency is missing

`TelemetryEvent` has deployment/source/signal/time/value but no stable event identity or source sequence. Timestamps are not unique IDs. Without an idempotency key or source-position contract, duplicates and restart replay cannot be distinguished from repeated legitimate values.

This directly compounds HIGH-1 and HIGH-3.

## MEDIUM-3 — quality defaults can silently become truth claims

`SignalQuality` permits `GOOD`, `UNCERTAIN`, `BAD` and defaults to `GOOD`. The foundation allows quality/status, but it also requires supplied facts to remain distinguishable from learned relationships.

A default `GOOD` is stronger than `quality unknown/not supplied`. For industrial sources, `GOOD` may mean OPC quality, device status, adapter confidence, or merely parser success—very different semantics. The event contract should distinguish missing quality from explicit externally supplied quality and record provenance for any inferred quality/confidence.

## MEDIUM-4 — the replay contract is not yet the live-adapter contract

The field roadmap's core premise is that synthetic, recorded replay, and live shadow mode exercise the same normalized event boundary. The proposed replay adapter validates already-normalized JSONL events; it does not test schema evolution, tag addition/removal, adapter normalization, or source-clock behavior.

That is useful as a serialization test, but it is not sufficient evidence that recorded/live adapters can enter through the same operational seam. A second replay fixture should include realistic raw-ish source irregularities and exercise the normalization layer rather than beginning after the hardest adapter behavior has already happened.

## Avoidable coupling summary

The present plan couples F0 to:

1. single-file total ordering;
2. exact acquisition-timestamp equality for feature joins;
3. one process-local integer evidence frontier;
4. deployment ID as the only restore compatibility key;
5. River-shaped scalar feature dictionaries as the only exercised learner shape;
6. evaluator/adapter causal semantics through `ACTION_CONSEQUENCE`;
7. a two-signal A->B synthetic world that cannot test the stated recurrence/drift/fault goals.

None of these are fatal to ABIL as a product. They are avoidable prototype assumptions that would become expensive if treated as the stable F0 seam.

## Weakest credible baseline / simpler rival

Before any novel learner, the weakest credible ABIL F0 rival should be something like:

- persistence/last-value;
- EWMA or equivalent streaming smoother/forecaster;
- one standard multivariate online regressor;
- one standard streaming change detector (e.g. a River-provided detector);
- explicit residual stream;
- identical checkpoint/replay/runtime boundary.

If that stack matches more complex adaptive machinery on the preregistered F0 tasks, complexity has not earned promotion.

## What would change this verdict

I would move ABIL F0 toward PASS when the implementation plan, before code, is revised to make these seams explicit:

- asynchronous event ordering/idempotency/time policy;
- exact learner-visible versus evaluator-only metadata separation;
- complete deployment/config/model/detector/checkpoint binding;
- per-source replay/resume frontier and crash-consistent checkpoint rule;
- residual/change-detector/uncertainty/resource responsibilities;
- synthetic A->B->A recurrence plus drift/fault/missing/jitter/out-of-order cases;
- evaluation that does not require exact cross-signal timestamp equality;
- restart twin-run and replay transformation invariants.

No machine write path is needed, and I do not recommend adding one. These corrections strengthen the read-only F0 substrate only.

ABIL F0 qualification is **LOCKED** for the exact frozen subject.
