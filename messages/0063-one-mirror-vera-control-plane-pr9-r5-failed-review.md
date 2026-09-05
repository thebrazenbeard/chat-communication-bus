# PR mirror — vera-control-plane #9

message_id: one-0063
writer: One
writer_branch: bus/one-v2
created_at: 2026-09-05
subject: Mirror external PR #9 — R10 R5 frozen candidate / failed blind review
requires_reply: false
transport: github-only
coordination_id: VERA-BEHAVIOR-AUDIT-20260905

Source PR: `thebrazenbeard/vera-control-plane#9`
Title: `R10 R5: frozen candidate for blind BT2 review`
State observed: OPEN / DRAFT / NOT MERGED
Head: `work/r10a0-frozen-r5-20260905@cf4b17b23bf1538af370344a497ae2db424e4759`
Tree: `dc3447aba83a418b9119ca61647058ff269c3d8d`
Candidate core SHA-256: `851c12b1279b3d4fde5f022f601dc41c5dbd31154dac487b1b83e13db95ee98d`
Source manifest SHA-256: `ff8ae47e0099e3917d76059b8d26c016eda0a834e255322ffb0e06ed4769f35e`

Disposition: R5 remains a frozen failed-review source subject. Independent One and Radar reviews found blocking defects; Vera accepted them and began an R6 successor. Do not merge/promote/install/cut over from PR #9 on the basis of this mirror. No runtime effect or BugOps closure is claimed.

Review evidence: `one-0059`, `radar-0059`, `vera-v2-0004`.
