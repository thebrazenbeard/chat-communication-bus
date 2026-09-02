# Radar control-plane views

These views complement `system-context.md`, `message-flow.md`, and `recovery-flow.md`. They describe intended V1 architecture; observed runtime/provider state still requires fresh evidence.

## Component map

```mermaid
flowchart LR
    Patrick[Patrick] --> Operator[ChatGPT operator adapter]
    Operator --> Core[Radar core]
    Core --> Registry[Identity / node / endpoint registry]
    Core --> Router[Envelope / routing / flow control]
    Core --> Workflow[Workflow / dependency engine]
    Core --> DLQ[Durable DLQ]
    Core --> Reconciler[Reconciler / maintenance]
    Reconciler --> GitHub[GitHub adapter]
    Reconciler --> Provider[Supabase projection adapter]
    GitHub --> Repo[(GitHub canonical source)]
    Provider --> Supabase[(Supabase live projection)]
    Router --> GitHub
    Router --> Provider
```

## Assignment / dependency flow

```mermaid
flowchart TD
    A[Assignment recorded] --> B{Dependencies complete?}
    B -- no --> C[WAITING_DEPENDENCY]
    C --> D[Predecessor completion observed]
    D --> B
    B -- yes --> E[READY]
    E --> F{Protected effect?}
    F -- no --> G[DO -> VERIFY -> REPORT]
    F -- yes --> H{Exact authority present?}
    H -- no --> I[WAIT_FOR_AUTHORITY]
    H -- yes --> G
    G --> J[Result / handoff / review]
```

Readiness is scheduling state, not permission. Dependency completion never manufactures protected-effect authority.

## Node / presence lifecycle

```mermaid
stateDiagram-v2
    [*] --> OFFLINE
    OFFLINE --> ONLINE: heartbeat / attach runtime
    ONLINE --> IDLE
    IDLE --> WORKING
    WORKING --> WAITING_DEPENDENCY
    WAITING_DEPENDENCY --> WORKING: dependency satisfied
    WORKING --> IDLE: work completed
    ONLINE --> DEGRADED: transport/provider impairment
    IDLE --> DEGRADED
    WORKING --> DEGRADED
    DEGRADED --> ONLINE: recovery + reconcile
    ONLINE --> OFFLINE: heartbeat expires
    IDLE --> OFFLINE: heartbeat expires
    WORKING --> OFFLINE: heartbeat expires
    DEGRADED --> OFFLINE: heartbeat expires
    OFFLINE --> PAUSED: explicit pause
    PAUSED --> OFFLINE: resume without runtime
    OFFLINE --> ARCHIVED: identity/runtime retirement
```

Node state is runtime reachability. It does not create or destroy the logical identity.

## Message lifecycle

```mermaid
stateDiagram-v2
    [*] --> RECEIVED
    RECEIVED --> REJECTED: invalid required schema
    RECEIVED --> NORMALIZED: permitted safe defaults
    RECEIVED --> VALID: complete valid envelope
    NORMALIZED --> ACCEPTED
    VALID --> ACCEPTED
    ACCEPTED --> DUPLICATE_DROPPED: idempotency window hit
    ACCEPTED --> ROUTED: route decision exists
    ACCEPTED --> DLQ: route/transport failure
    ROUTED --> DELIVERED: transport receipt
    DELIVERED --> ACKNOWLEDGED: recipient acknowledgement
    ACKNOWLEDGED --> INCORPORATED: explicit incorporation evidence
    DLQ --> REPLAYED: applicability refreshed + still applicable
    DLQ --> DISCARDED: no longer applicable
```

Delivery is deliberately separated from acknowledgement and incorporation.

## Assignment lifecycle

```mermaid
stateDiagram-v2
    [*] --> DRAFTED
    DRAFTED --> ASSIGNED
    ASSIGNED --> ACKNOWLEDGED
    ACKNOWLEDGED --> RUNNING
    RUNNING --> REVIEW_PENDING
    REVIEW_PENDING --> CONFIRMED
    REVIEW_PENDING --> CHANGES_REQUESTED
    CHANGES_REQUESTED --> RUNNING
    RUNNING --> HANDED_OFF
    ACKNOWLEDGED --> PAUSED_USAGE_EXHAUSTED
    RUNNING --> PAUSED_USAGE_EXHAUSTED
    REVIEW_PENDING --> PAUSED_USAGE_EXHAUSTED
    PAUSED_USAGE_EXHAUSTED --> ACKNOWLEDGED
    PAUSED_USAGE_EXHAUSTED --> RUNNING
    PAUSED_USAGE_EXHAUSTED --> REVIEW_PENDING
    ACKNOWLEDGED --> INTERRUPTED
    RUNNING --> INTERRUPTED
    REVIEW_PENDING --> INTERRUPTED
    PAUSED_USAGE_EXHAUSTED --> INTERRUPTED
    INTERRUPTED --> ACKNOWLEDGED
    INTERRUPTED --> RUNNING
    INTERRUPTED --> REVIEW_PENDING
    INTERRUPTED --> PAUSED_USAGE_EXHAUSTED
    DRAFTED --> SUPERSEDED
    DRAFTED --> STOPPED
    ASSIGNED --> STOPPED
    RUNNING --> STOPPED
    REVIEW_PENDING --> STOPPED
    HANDED_OFF --> STOPPED
```

The legacy `chat_bus` ledger remains the database-enforced reference for detailed predecessor/transition invariants during V1 compatibility.

## Authority / effect boundary

```mermaid
flowchart TD
    Task[Current specific task] --> A{Effect class}
    A -- Read / observe --> B[Execute]
    A -- Isolated reversible --> C[Current assignment is authority]
    C --> B
    A -- Shared mutable --> D[Coordinate writer / collision ownership]
    D --> B
    A -- Protected external / destructive --> E{Exact current effect authority?}
    E -- yes --> B
    E -- no --> F[Stop at boundary]
    B --> G[Verify actual effect]
    G --> H[Report / record evidence]
```

Leases coordinate collision risk; they do not manufacture permission already supplied by a current specific task.

## GitHub / Supabase reconciliation loop

```mermaid
flowchart LR
    GH[(GitHub durable state)] --> P1[Project GitHub state]
    SB[(Supabase live projection)] --> P2[Read provider state]
    P1 --> C[Compare]
    P2 --> C
    C --> R{Finding class}
    R -- No drift --> Q[No noise]
    R -- SAFE_PROJECTION_REPAIR --> S[Repair provider projection]
    R -- AMBIGUOUS_DURABLE_CONFLICT --> A[Preserve evidence + escalate]
    R -- OBSERVATION_ONLY --> O[Record only if useful]
    S --> V[Read back]
    V --> C
```

GitHub source/provenance is not overwritten to make a stale live projection look consistent. Provider loss is recoverable by replaying Git-held migrations/seed and reconciling current Git state.
