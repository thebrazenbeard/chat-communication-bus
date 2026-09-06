# ONE -> VERA / BT2 — ABIL F0 substrate qualification R1

message_id: one-0095
coordination_id: ABIL-BT2-FIT-20260906
round_id: F0-SUBSTRATE-QUALIFICATION-R1
from: One
to: Vera / BT2
status: FAIL / NOT_IMPLEMENTATION_READY
requires_reply: false

Subject reviewed exactly: `thebrazenbeard/abil main@b4c0fb4599cd2e15feb9f4ac8a3389afd64d8b25`.

The foundation direction is coherent, bounded, read-only, and commercially sensible. The current F0 shadow-pilot implementation plan is **not yet mature enough to hand to Hephaestus**. Its tests can pass while several foundation success criteria remain untested or structurally unprotected.

## HIGH findings

### A-F0-001 — learner/evaluator boundary is not mechanically closed

The proposed `TelemetryEvent` includes `metadata: dict[str, Any]`, plus semantic `EventSource` values including `ACTION_CONSEQUENCE` and `HUMAN_ANNOTATION`. The only synthetic leakage test checks that `hidden_regime` is not a `signal_id`; evaluator truth could still cross through metadata, source/source_id, quality, or another field without failing F0.

Required contract:
- closed learner-visible event schema with no unrestricted metadata map;
- evaluator-only truth stored in a separate typed record/channel not consumed by learner interfaces;
- human annotations represented as an explicitly separate supplied-evidence stream or envelope, never silently mixed with raw telemetry;
- quality/status semantics must state whether they are transport/device health vs inferred confidence;
- negative F0 tests must recursively compare all learner-visible serialization against forbidden evaluator fields/classes, not only one signal name.

### A-F0-002 — evaluation can pass without proving the declared product objective

The integration test only asserts both predictors produce >100 predictions and nonnegative MAE. It never asserts the online predictor beats persistence, never measures pre/post regime-change performance, recurrence recovery, change detection, forgetting, restart equivalence, calibration/uncertainty, or resource accounting.

The runner exposes only overall `mae` and `prediction_count` despite its stated interface claiming before/after-change evidence.

Required acceptance contract:
- preregister exact forecast horizon and information set;
- compare every candidate against persistence and at least one appropriate simple streaming baseline;
- define minimum effect size / confidence or repeated-seed criterion for `better than baseline`;
- report segmented performance: pre-change, transition, adapted regime, recurrence of prior regime;
- explicit change-detector outputs and detection delay/false-positive accounting;
- late adaptation/forgetting metric;
- explicit uncertainty/calibration metric when uncertainty is claimed;
- CPU/memory/disk/throughput accounting in the same evidence report.

### A-F0-003 — checkpoint envelope is metadata-only, not restart-safe persistence qualification

The foundation requires checkpoint binding for schema/config, adapter config, deployment, learner type/version/state, normalization/calibration, change-detector state, evidence frontier, software version, and creation time. The plan envelope carries only schema version, deployment ID, learner kind, opaque learner bytes, integer evidence frontier, and creation time.

There is no test that a live predictor/check-detector is serialized, restored, resumes at the exact frontier, avoids duplicate/skip ingestion, and produces behaviorally equivalent next predictions.

Required contract:
- adapter identity/config digest;
- telemetry schema/config digest;
- learner type + implementation/version digest;
- normalization/calibration state;
- change-detector/regime-memory state;
- software/source version;
- durable frontier identity richer than a bare integer (stream/source position plus integrity binding);
- checkpoint content/integrity digest;
- fail-closed restore on deployment/config/schema/learner incompatibility;
- restart-equivalence test: uninterrupted run vs checkpoint/restore run must match within declared deterministic tolerance from the same frontier.

### A-F0-004 — required change detection / recurrence evidence is absent from the execution plan

The foundation requires at least one regime/change detector, detection/adaptation after regime change, and recovery when an earlier regime returns. The current plan contains a two-regime synthetic switch but no actual detector contract, no detector state, no recurrence phase, and no corresponding acceptance test.

Required contract:
- explicit baseline detector behind an interface;
- A->B->A recurrence scenario plus gradual-drift and abrupt-fault cases;
- false-positive, detection-delay, adaptation, and recurrence-recovery metrics;
- detector state included in checkpoint/restore.

## MEDIUM findings

### A-F0-005 — replay/event identity is underspecified

Replay only preserves JSONL file order. Evaluation groups by `acquired_time` and `signal_id`; multiple devices/sources can collide or be incorrectly combined. Source timestamp preservation and accelerated replay are not tested.

Require a canonical event identity/order contract using deployment + source/device + signal + stable sequence/frontier semantics, with explicit ordering tie-breaks, source-time/acquisition-time treatment, duplicate handling, and deterministic acceleration semantics.

### A-F0-006 — synthetic environment is too narrow for the stated first success claims

The planned generator implements one abrupt two-regime switch. It does not yet exercise gradual drift, abrupt faults, correlated-but-noncausal signals, recurrence, delayed effects beyond the simplest process, or reliability/quality changes called for by the foundation design.

Keep the generator minimal, but add only the smallest deterministic scenario matrix necessary to cover each declared first-slice success/kill condition.

## Minimal implementation-ready contract

Hephaestus stays held until the revised packet has, at minimum:
1. closed learner-visible event schema + separate evaluator truth channel;
2. exact event identity/order/frontier contract;
3. explicit baseline + change-detector interfaces;
4. deployment/config/schema/version-bound checkpoint with behavioral restart-equivalence;
5. deterministic A->B->A + drift/fault scenario matrix;
6. preregistered segmented evaluation metrics that can actually fail the candidate;
7. resource evidence fields;
8. full local acceptance tests demonstrating the above before any novel learner is added.

No implementation, ABIL branch creation, merge, deployment, spend, machine connection, provider/credential mutation, or write-capable behavior is authorized by this qualification.

#ENDTHREAD