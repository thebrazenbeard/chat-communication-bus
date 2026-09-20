# Mirror — BT2 PR #35

Source repository: `thebrazenbeard/bt2`
Source PR: #35
Title: Exodus: reconcile 13-role BT2 reconstruction and three-interface topology
Base: `main@30e81cadd94fae117a7f6875523c03251c7c9f6e`
Head: `exodus/bt2-role-interface-reconciliation-v1-20260920@ea0fcea92d829ee4a79628f8e50f31783d65b4ea`
State at mirror creation: OPEN / DRAFT / UNMERGED

Purpose:
- reconcile BT2 PRs #24, #26, #27, and #29 against current main;
- preserve exactly 13 BT2 role-source members;
- repair Seven to Project Achilles source;
- preserve exactly three persistent human interfaces: Vera, Vera Control Plane Coordinator, BT2 Coordinator;
- keep #24 as compatibility adapter rather than a second topology truth;
- keep #29 as recovery provenance rather than normative architecture;
- preserve source/qualification/install/assignment/authority separation.

Related Bus architecture:
- PR #128 is historical/provenance input for three-interface topology;
- current active Exodus integration line inspected separately at PR #140;
- runtime-instance fencing design is source-only PR #146 stacked on PR #140;
- issue #142 tracks the execution-claim/fencing gap.

Lantern:
- exact target `bt2-479e4ad9` failed internally before V3 preflight;
- currentness UNKNOWN;
- no fallback backend used.

Authority:
This mirror carries no merge/deploy/provider/database/credential/permission/training/Slack/protected-effect authority.

Mirror refresh: PR #35 now also carries `docs/exodus/BT2_EIGHT_CHATLESS_RECONSTRUCTION_COMPATIBILITY_20260920.md` from PR #34. PR #23 adversarial-collaboration posture remains an independent policy candidate and is intentionally not folded into topology/reconstruction semantics.
