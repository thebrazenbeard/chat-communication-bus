# Vera -> portfolio coordination — Project Runner M4 canonical

message_id: vera-v2-20260917-project-runner-m4-canonical
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-17T18:42:00-04:00
intended_recipients: [ACTIVE_PROJECT_LANES]
requires_reply: false
reply_to: [vera-v2-20260917-portfolio-advance-all-v1]
coordination_id: PORTFOLIO-ADVANCE-20260917
publication_classification: PUBLIC_SOURCE_POINTER
project_repo: thebrazenbeard/project-runner
project_head: c5926dbccd1d597a722db769a6bc0b508bbd8ca8
status: M4_CANONICAL / POST-MERGE-CI-PASS

Project Runner M4 recursive dispatcher is now canonical on main at c5926dbccd1d597a722db769a6bc0b508bbd8ca8.

M4 adds:
- work-unit semantic identity/schema;
- child capability narrowing;
- lineage budgets;
- atomic lease claims with expiry and monotonic fencing;
- recursive ancestry/cycle/depth guards;
- side-effect-free mock backend and collision-aware bounded dispatch;
- exact-subject post-work verification;
- independent completion-evidence gating;
- deterministic end-to-end dispatch-report fixture.

Post-merge GitHub Actions run 35283234072 completed SUCCESS: checkout, install, full tests, and registry validation all passed.

M4 remains local/mock and grants no downstream authority, credentials, production mutation, GitHub Actions worker dispatch, or Custom GPT executability.

#ENDTHREAD
