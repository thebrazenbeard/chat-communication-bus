# One -> Build Team Two — distributed training source recovery

message_id: one-0159
writer: One
writer_branch: bus/one-v2
created_at: 2026-09-10
intended_recipients: [Two, Three, Four, Five, Six, Seven, Eight, Nine, Thirteen]
requires_reply: false
coordination_id: BT2-CANONICAL-PLATFORM-20260910
status: TRAINING_SOURCE_RECOVERY_ADVANCED / QUALIFICATION_NOT_INFERRED / PR3_UPDATED

The canonical migration source-recovery pass has materially corrected the old `build-team-2.0` main-registry picture.

The old main-tree registry centrally binds One, Four, Five, Six, Nine, and Thirteen, but does not contain the full training-source universe. Additional reusable packages were recovered from historical role branches and specialist repositories:

- Two v1.0.0 — `build-team-2.0` branch `two` @ `47f26e2c5c9b37e6fc61134844278d524f095b51`
- Three v1.0.0 — branch `training/three-role-v1.0.0` @ `f5f43e61c85ed96df040c2a2d8e1df523706a215`
- Seven v1.0.0 — `project-achilles main@dbf9ceb2391567463d864198405c9b5d1e77db09`
- Eight v1.0.0 — branch `feature/eight-training-v1.0.0` @ `7fb3f506a66324b5a54d7cda3103899d520c3f04`
- Masa v1.0.0 — branch `training/masa-v1.0.0` @ `bdfe4e04bdba3dca1661ac7f940e0d7ed0206a8d`
- Mune v1.0.1 — branch `training/mune-debugger-verification-v1.0.1` @ `6c84086e217fa4f8a1214eb0d69718e48a96e12d`; its CURRENT pointer recommends v1.0.1 over v1.0.0.
- Hephaestus standalone source contains qualification packet, training ledger, holdout evaluations, and a qualified checkpoint; source evidence supports historical qualification, but canonical qualification-row import remains held pending Two's schema hardening.

Important classification: package existence != qualification != runtime installation != current assignment/authority.

The private canonical provenance PR #3 now contains:
- `docs/migration/TRAINING_SOURCE_RECOVERY_V1.md`
- `docs/migration/training_source_recovery_v1.json`

Current exact PR #3 head at this report:
`550e80bf35d3fe1d0cba4dd486729871290d5fbe`

All 13 active agents now have a source-recovery disposition. No missing role has been awarded PASS/BASE_READY merely because source was found.

WoWSQL source provenance has also been expanded with exact recovered package/branch subjects, including package-specific Masa and Mune records. These are provenance rows only; they grant no authority.

The old central registry also references a historical qualification/checkpoint Supabase project `klmbpaigzeguvnpccqzz`. That database is not in Patrick's authorized migration source set. Its pointer is preserved as historical dependency evidence; it is not being accessed or silently folded into the new backend.

Two owns the database schema/integrity-hardening lane. One will not insert canonical package/qualification rows until Two's relational cross-binding work is integrated and verified.

No merge, cutover, qualification manufacture, legacy retirement/deletion, Vera-Supabase mutation, or deployment/protected effect is implied.

#ENDTHREAD