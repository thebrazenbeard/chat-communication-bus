# Radar system context

```mermaid
flowchart LR
    P[Patrick\nHuman override] <--> C[ChatGPT\nRadar operator interface]
    C <--> R[Radar\ncontrol plane]
    R <--> G[GitHub\ncanonical durable state]
    R <--> S[Supabase radar schema\nlive rebuildable projection]
    R <--> N[Identity nodes / endpoints]
    G -->|bootstrap source + currentness| R
    S -->|presence + queues + dependencies + telemetry| R
```

Boundary rule: GitHub owns durable source/provenance; Supabase accelerates live coordination; ChatGPT supplies reasoning/operator interaction; no single ChatGPT session is required for Radar continuity.