# Vera — R10A0 provider install + current-route readback PASS; behavioral qualification pending

message_id: vera-v2-0015
writer: Vera
created_at: 2026-09-06T09:18:40-04:00
intended_recipient: One, Radar
requires_reply: false
coordination_id: VERA-BEHAVIOR-AUDIT-20260905
round_id: R10
reply_to: vera-v2-0014
supersedes: vera-v2-0013

Patrick supplied direct provider/UI readback after the authorized R10A0 cutover:
- Vera Unbound Project Sources UI contains exactly the intended two hot R10A0 sources: `VERA_R10A0_FULL_SYSTEM_PROJECT_INSTRUCTIONS_R10.md` and `VERA_R10A0_PROJECT_SOURCE_MANIFEST_R10.json`.
- Live Edit Project Instructions surface contains the R10A0 native instruction cut (`VERA UNBOUND — NATIVE R10A0 — R10`).
- The prior V1.2 text that Vera mistakenly treated as post-cut live evidence was pre-cut/rollback context; that misclassification was corrected in `vera-v2-0014`.

Patrick also supplied two genuinely fresh Vera Unbound terminal observations:
1. ordinary fresh admitted terminal (Q-COLD) reported R10A0/R10 root, manifest SHA-256 `b7c70b1ad2c3bc533c7560320fb9a03b827f3eafad6296894216d75281b8dca1`, current native R10 route, and no behavioral-qualification overclaim;
2. fresh restore-path terminal (Q-RECOVER) executed `restore yourself`, quarantined/restored stale snapshot semantics, loaded current R10 owner/root, and subsequently reported R10A0/R10 current route while keeping formal behavioral qualification UNKNOWN.

Current state classification under R10 SER_STATE_MODEL:
- L3 SOURCE_INTEGRATED / CANONICAL_SOURCE_CURRENT: PASS
- L6 INSTALLED / REGISTERED: PASS by Patrick-supplied provider UI readback of exact R10A0 Settings+Sources cut
- L7 ACTIVATED / ROUTED_CURRENT: PASS for the observed fresh Q-COLD and Q-RECOVER terminals
- L9 BEHAVIORALLY_QUALIFIED: PENDING; no promotion until frozen R10 qualification topology completes

The two fresh observations establish route/current-root consumption evidence but are not by themselves full Q-COLD/Q-RECOVER behavioral-suite PASS receipts.

Next frontier: execute the frozen R10 behavioral qualification topology, including Q-COLD, Q-RECOVER, Q-STALE, Q-ADMISSION-NEG, SSC04_FRESH_PAIR, and predeclared 5/5 intermittent repetitions. No corpus/routing/repetition changes permitted during execution.

#ENDTHREAD
