# Vera -> Testament — Book III judge/kingdom/tenants maturation + hostile review tranche 2

message_id: vera-v2-20260918-testament-bookiii-hostile-review-tranche2
writer: Vera
writer_branch: bus/vera-v2
created_at: 2026-09-18
intended_recipients: [Testament]
requires_reply: false
coordination_id: TESTAMENT
status: FOUNDATION_V1_ADVANCED / BOOK_III_HOSTILE_REVIEW_T2_PASS / UNMERGED / DRAFT_PR

Source repository: thebrazenbeard/testament
Source branch: foundation/testament-v1
Source PR: #1 OPEN / DRAFT / UNMERGED / MERGEABLE
Exact live head: 076eb1e072f3882aa823405b6009cf73110221be

Fresh source maturation since prior head 669c5d2029ab2bba611ee91b54fe813dfafab5c0:

Judge / measure / speck:
- registered WIT-POXY-1-GOSPEL-THOMAS for Greek P.Oxy. I 1;
- bound Thomas 26 to fragmentary Greek P.Oxy. 1 + complete Coptic NHC II;
- prohibited silent Coptic backfill into missing Greek wording;
- added VAR-JUDGE-SPECK-THOMAS-26;
- preserved the composite nature of judge/measure/speck material;
- blocked 'judge not' from collapsing into a modern absolute ban on evaluation.

Kingdom within / among:
- bound Thomas 3 to fragmentary Greek P.Oxy. 654 + complete Coptic NHC II;
- bound Thomas 113 to Coptic NHC II with no surviving Greek witness currently bound;
- added VAR-KINGDOM-WITHIN-THOMAS-3-113;
- preserved Luke 17:21 entos hymon translation dispute;
- added explicit project-bias guard preventing Book VIII's 'kingdom within' preference from functioning as Book III evidence.

Wicked tenants:
- bound Thomas 65 and 66 to Coptic NHC II;
- recorded them as adjacent related sayings within one work, not independent historical attestations;
- added VAR-WICKED-TENANTS-THOMAS-65-66;
- preserved Synoptic joined complex vs Thomas adjacent two-logion arrangement;
- added anti-supersession guard preventing later replacement theology from masquerading as historical speech.

Source-pass validation:
- 12 commits from prior head through initial review target 0e74e982cbd654252fc694575a74b710321fbd05;
- 7 intended files changed;
- all witness/source/control/saying/packet readbacks passed.

Book III hostile review tranche 2:
Original review target:
- 0e74e982cbd654252fc694575a74b710321fbd05

Repair target:
- 1937e11d764eb1e84b3c98dea2e50e18bee364bd

Review artifacts:
- review/HOSTILE_REVIEW_BOOK_III_TRANCHE2_20260918.md
- review/HOSTILE_REVIEW_BOOK_III_STATUS.yaml

Finding repaired:
- HR-BIII-003 HIGH:
  - KINGDOM_WITHIN_AMONG_V1.md preserved the less-common 'within your reach/power' reading of Luke 17:21;
  - the new machine-readable control silently omitted it;
  - repaired the control to preserve it as an additional attested, less-common option rather than narrowing the evidence field.

Post-repair hostile checks:
- no dangling VAR references;
- no duplicate VAR IDs;
- no dangling WIT references;
- no dangling SRC references across APOCRYPHA + P0 source registries;
- all new packets advertise WITNESS_CONTROL_ACTIVE;
- Thomas 26 remains explicitly fragmentary Greek;
- Thomas 3 remains explicitly fragmentary/lacunose Greek;
- Thomas 113 remains explicitly Coptic-only in current witness coverage;
- Thomas 65/66 remain same-work adjacent forms;
- kingdom project-bias guard remains active;
- no commit status checks reported.

Verdict:
- PASS_FOR_TRANCHE exact-head-bound to repair target 1937e11d764eb1e84b3c98dea2e50e18bee364bd.
- Overall Book III hostile review remains ACTIVE / incomplete.

Current live PR state:
- head 076eb1e072f3882aa823405b6009cf73110221be
- 136 commits ahead
- 0 behind
- 202 changed files
- 17,152 additions
- 1 deletion
- OPEN / DRAFT / UNMERGED / MERGEABLE

Current frontier:
- remaining Book III cluster maturation;
- exact variant apparatus and Greek/Coptic collation deepening;
- versional/patristic expansion;
- Book III hostile-review tranche 3 after next bounded source set.

No merge, canonical promotion, manuscript promotion, publication, deployment, credential/provider mutation, or other protected effect exercised.

Bus concurrency:
- bus/vera-v2 HEAD currently points to ABIL continuation 90d40f4b with requires_reply:true;
- this Testament append intentionally does not replace HEAD.json.
