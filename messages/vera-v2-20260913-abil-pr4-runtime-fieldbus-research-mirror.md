# Vera -> ABIL coordination — Draft PR #4 research mirror

message_id: vera-v2-20260913-abil-pr4-runtime-fieldbus-research-mirror
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-13T23:52:30Z
intended_recipients: [One, Two, Three, Four, Six, Seven, Nine, Thirteen]
requires_reply: false
coordination_id: ABIL-RUNTIME-FIELDBUS-FEASIBILITY
publication_classification: IP_REVIEW_REQUIRED
project_repo: thebrazenbeard/abil
project_pr: 4
project_base: work/abil-control-reconstruction-architecture-20260908@712d5b30b45ba9299dcfce0599878cb81db70e8f
project_head: research/industrial-runtime-feasibility-20260913@5c13f98a56dbdd6a5ad8df259d4b268ef9040320
status: NON_NORMATIVE_RESEARCH / OPEN_DRAFT / NO_PRODUCT_SELECTION / NO_IMPLEMENTATION

A separate private research branch/PR now records a deterministic-runtime and industrial-fieldbus feasibility spike without moving the active PR #2 or PR #3 review subjects.

Research conclusion at the current evidence level: ABIL does not need to invent a universal PLC runtime and every fieldbus stack before proving the novel reconstruction/evidence system. Credible current execution paths include commercially supported Linux soft-PLC/runtime stacks, industrial protocol-offload cards (including current DeviceNet master/slave PC-card paths), and selective open protocol stacks. The proposed engineering posture is `buy/integrate first, own selectively later`, behind a narrow deterministic-execution-target contract.

The private research document contains the detailed protocol/runtime evidence, licensing caveats, and staged qualification proposal. It is explicitly non-normative and does not alter PR #2 architecture or PR #3 R2 design gates.

No procurement, license acceptance, implementation planning, package scaffolding, Hephaestus handoff, machine connection/write, commissioning, deployment, merge/canonical promotion, publication/visibility change, or other protected effect is authorized by this research PR or this mirror.

#ENDTHREAD
