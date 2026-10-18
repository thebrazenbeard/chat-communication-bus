"""Validate the PORTAL two-pair assignment. This checks only source contracts,
never live worker status, external effects, or independent review."""
PAIRS = {
  "INTEGRATION_TRAINING": [("Integration","VN2","source_owner"),("Training","Lappy","cognitive_source_owner")],
  "CODEX_VN1": [("Codex","Lappy","single_serial_implementation_owner"),("VN1","VERA-NODE-1","independent_falsifier")],
}
RETURNS = {"each_partner_distinct_source_and_test","exact_pr_head_and_host",
"commands_results_PASS_FAIL_SKIP_and_artifact_digest","cross_pair_disagreements_preserved",
"source_runtime_effect_authority_ceiling","next_noncolliding_action"}
def check_two_pair_contract(s):
    e=[]
    if not isinstance(s,dict) or s.get("schema")!="VERA_PORTAL_LIVE_TWO_PAIR_V2":
        return ["wrong schema"]
    if s.get("mode")!="ONE_LIVE_CONVERSATION_EVENT_NO_SCHEDULING" or s.get("execution_topology")!="TWO_CROSS_HOST_COLLABORATING_PAIRS":
        e.append("not exactly live two-pair execution topology")
    if s.get("claimed_activity")!="ASSIGNMENTS_NOT_ATTESTED_ACTIVE_WORKERS":
        e.append("worker activity incorrectly claimed")
    if s.get("supersedes")!=["CCB_383_FOUR_OVERLAPPING_PAIR_ALLOCATION"]:
        e.append("old topology still authoritative")
    c=s.get("coordinator",{})
    if (c.get("worker"),c.get("host"))!=("PORTAL","Lappy") or set(c.get("review_scope",[]))!=set(PAIRS):
        e.append("PORTAL must review both pairs")
    if c.get("periodic_checking") is not False or c.get("permanent_process") is not False:
        e.append("unapproved background coordinator")
    g=s.get("governance",{})
    for k in ("single_serial_codex","independent_vn1_review","owner_owned_branch_mutation_only",
              "no_new_scheduler","bus_comments_are_handoffs_not_worker_attestations",
              "no_guest_or_model_qualification_inferred"):
        if g.get(k) is not True:e.append(k+" missing")
    if g.get("comments_are_worker_execution_proof") is not False:
        e.append("worker comment falsely attests execution")
    if g.get("protected_effects")!="NONE_GRANTED" or g.get("architecture_acceptance")!="HOLD_PENDING_INDEPENDENT_SEMANTIC_OWNER_REVIEW":
        e.append("authority or acceptance falsely granted")
    pairs=s.get("pairs",[])
    if not isinstance(pairs,list) or len(pairs)!=2:return e+["exactly two pairs required"]
    if {p.get("id") for p in pairs}!=set(PAIRS):e.append("wrong pair identities")
    actors=[]
    for p in pairs:
        pp=p.get("partners",[])
        if not isinstance(pp,list) or len(pp)!=2:
            e.append("missing second contributor");continue
        got=[(x.get("worker"),x.get("host"),x.get("role")) for x in pp]
        if got!=PAIRS.get(p.get("id")):e.append("pair assignment/host drift")
        actors += [x.get("worker") for x in pp]
        if not all(p.get(k) for k in ("shared_work_packet","handoff","noncollision")):
            e.append("shared work/handoff missing")
    if sorted(actors)!=sorted(["Integration","Training","Codex","VN1"]):
        e.append("four workers, once each")
    if set(s.get("return_requirements",[]))!=RETURNS:e.append("incomplete two-person evidence")
    if set(s.get("connected_hosts_observed",[]))!={"Lappy","VN2","VERA-NODE-1"}:
        e.append("device reachability claims incorrect")
    return e
