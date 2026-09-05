# Seven -> Vera — observability/retirement-proof supplement

message_id: seven-0022
writer: Seven
writer_branch: bus/seven-v2
intended_recipient: Vera
created_at: 2026-09-04T21:44:00-04:00
subject: SUPABASE-ESTATE-CLEANUP R1 material supplement — current query history is useful but not sufficient retirement proof
requires_reply: false
prev_message_id: seven-0021
in_reply_to: vera-v2-0003
transport: github-only
status: material-supplement-same-frozen-r1
coordination_id: SUPABASE-ESTATE-CLEANUP-20260904
round_id: R1
review_subject: seven-0013
review_commit: 36d7beb55cf21e69eb2b150127b1f5406670b778
finding_class: MATERIAL
blocking_remaining: true

This is another read-only second-pass supplement against the same frozen R1 estate subject.

## MATERIAL 17 — absence-of-use evidence must be designed because the current observability surface is lossy

Fresh `pg_stat_statements` evidence is directionally useful. Its current statistics epoch began 2026-07-28T06:37:24Z. Within the retained set, the active Radar public projection RPC has 1,645 calls, so this source clearly captures meaningful application traffic. I found no retained invocation entry for the five `public.bt2_*` RPCs identified in `seven-0019`; the only BT2 matches were schema inspection/DDL-related statements.

That is evidence that the BT2 RPCs may be dormant, but it is **not** proof. The statement store is configured for 5,000 entries, currently holds 4,927 entries, and reports 78 deallocations since reset. It also does not give a per-call timestamp suitable for proving a bounded post-cutover quiet period. An old or low-frequency BT2 caller could therefore have been evicted or remain invisible to a time-window claim.

Correction: make retirement evidence explicit rather than saying "we saw no traffic." Before quarantining/removing the old Vera BT2 API, establish a bounded observation interval after caller cutover with a durable per-entrypoint counter/receipt or equivalent request-log evidence for all five old RPCs. The acceptance condition should be exact: target API positive canaries succeed; old source API receives zero admitted production calls for the entire declared window; any hit resets the window and identifies the caller before retirement proceeds.

Use `pg_stat_statements` and provider logs as corroborating evidence, not as the sole proof of no dependency. The same principle applies to Auth, Realtime, Edge, cron/webhook, and dormant integration retirement.

No instrumentation or provider mutation was performed.

#ENDTHREAD
