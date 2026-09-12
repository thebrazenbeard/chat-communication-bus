# Vera -> Bus — mirror: vera-control-plane PR #20

message_id: `vera-20260912-vera-control-plane-pr20-mirror`
writer: `Vera`
writer_branch: `bus/vera-v2`
intended_recipients: `Patrick`, `BV`, `Vera`
requires_reply: `false`
transport: `github-only`
status: `PR_MIRROR`

Canonical PR: `thebrazenbeard/vera-control-plane#20`
Title: `Bind Vera Control Plane Supabase deployment source`
Head: `work/supabase-control-plane-binding-20260912`
Base: `main`
State: `OPEN_DRAFT`

Purpose:
- record the three migrations already installed on Supabase project `fawkirqroyniueeqspif`;
- bind the provider deployment source to `thebrazenbeard/vera-control-plane` without enabling production auto-deploy;
- preserve `PROVIDER != CONTROL AUTHORITY` and keep Vera runtime-state semantics owned by `thebrazenbeard/vera`;
- record Patrick's direct report that the Supabase GitHub integration is connected, while current tooling cannot independently read that dashboard setting.

Post-bind provider verification:
- provider `ACTIVE_HEALTHY`;
- exactly three intended baseline migrations present;
- no application tables in `public`, `vera_cp_api`, or `vera_cp_internal`;
- no Edge Functions;
- no security or performance advisor findings.

No merge, production-deploy activation, runtime activation, current-route qualification, or behavioral qualification is implied.
