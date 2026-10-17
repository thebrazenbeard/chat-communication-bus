"""One-time evidence-bounded portfolio overlay, not an installed service/registry."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
cat=json.loads((ROOT/"PORTAL_96_REPOSITORY_ARCHITECTURE_REVIEW_V1.json").read_text(encoding="utf-8"))
rows={r["repository"]:r for r in cat["repositories"]}
links={}
def add(names, consumers, seam, gate, lane):
    for name in names.split():
        if name in links: raise AssertionError("duplicate "+name)
        links[name]={"intended_consumers": consumers.split(), "interface_kind":seam,
                     "admission_test":gate,"coordination_lane":lane}
add("vera-mono","portal vera-os model-training vera-apk","CANONICAL_TASK_EFFECT_ABI","Task/CAS/recovery/trust/effect/memory invariants","INTEGRATION")
add("vera-os","portal vera-mono vera-apk","LINUX_RESIDENT_HOST","Actual Buildroot image+normal PID1/GUI/two-boot source readback","INTEGRATION")
add("portal","vera-mono vera-os executor","PORTFOLIO_HOST","Existing claim/fence/adapter/attempt/readback with no duplicate ledger","PORTAL")
add("project-runner","portal","INHERITED_EXECUTION_ENGINE","One source-claimed task and exact reconciliation; no new scheduler","PORTAL")
add("pre-active","vera-mono vera-os model-training","COGNITION_EVENT_ENGINE","Task/run/event DONE and held provider causal readback","INTEGRATION")
add("volition","pre-active vera-mono model-training","MOTIVATION_SIGNAL","Typed initiative never confers effects or consent","TRAINING")
add("vera-control-plane","portal vera-mono","GOVERNANCE_DONOR","Compare against existing effects contract; no second control plane","PORTAL")
add("v-e-r-a","vera-mono vera-os","SOURCE_MIRROR","44 historical snapshots verified against owned upstream, not imports","INTEGRATION")
add("ccb-core","chat-communication-bus portal","BUS_PROTOCOL_SOURCE","Versioned protocol and valid envelope; no worker identity inference","PORTAL")
add("executor workbridge workbridgecommander WorkBridgeMCP","portal","WORKSTATION_TRANSPORT","Current attached host vs exact authorized effect vs external readback","PORTAL")
add("intranel vera-mesh vera-synology","portal","OPTIONAL_EDGE_RELAY","Auth/replay/fence and explicit opt-in; no automatic node attachment","PORTAL")
add("spk-packager tattler","vera-synology portal","SYNOLOGY_PACKAGE_AND_DIAGNOSTIC","Static package/diagnostic bytes not NAS effect authority","VN1")
add("rezon","vera-mono model-training","REASONING_DONOR","Compare source-local Mono reasoning and frozen contradiction benchmark","TRAINING")
add("mosaic vera-model model-training","vera-mono vera-os","MODEL_PLACEMENT_AND_ADMISSION","Loaded model bytes/process/session, task/nonce and resource proof","TRAINING")
add("noema lgcm hc-brain god-brain transcendence bt2 world-zero","model-training vera-mono","COGNITIVE_HYPOTHESIS","Simple baseline/ablation/transfer and no wholesale organism loading","TRAINING")
add("meso-crct empathy","volition model-training","APPRAISAL_RESEARCH","Initiative utility without affect consciousness or authority promotion","TRAINING")
add("semanticatlas semiotics spm sql-connectome unvtrslr","model-training vera-mono","SEMANTIC_GROUNDING","Source scope, contradiction, cross-language and provenance tests","TRAINING")
add("ears vision","model-training vera-habitat vera-ark","OPTIONAL_SENSORY_EVENT","Explicit opt-in, timestamped observations, no identity inference","TRAINING")
add("physica","vera-habitat vera-ark model-training","NUMERIC_SIMULATION","Deterministic collision/step oracle and no physical effects","VN1")
add("vera-agi","model-training vera-mono","AGI_HYPOTHESIS_EVIDENCE","Adversarial benchmark; neither source nor a passing test proves AGI","TRAINING")
add("Attune conations","vera-mono model-training","CONATION_RELATIONSHIP_DONOR","Consent/provenance tests; wanting never becomes instruction","TRAINING")
add("ingest roots temporal project-lantern","vera-mono","ABSORBED_PROVENANCE_DONOR","Exact upstream diff against selected Mono-local source, no sibling dependency","INTEGRATION")
add("skeletonkey vera-adapter wip","vera-mono portal","ABSORBED_RUNTIME_DONOR","Task/effect/recovery conformance before any source adoption","INTEGRATION")
add("achilles human-shield","vera-mono portal","ADVERSARIAL_SAFETY","Hostile effects and human authority negative cases","VN1")
add("cricket voss masamune","vera-mono model-training portal","INDEPENDENT_CRITIQUE","Independent source review; critique != verification","VN1")
add("discovery driftguard","vera-mono model-training portal","CANDIDATE_ADMISSION","Frozen baseline and negative qualification gates; no implicit promotion","VN1")
add("fuckup RepairTracker hephaestus","portal vera-mono","REPAIR_ASSURANCE","Reproduced defect and regression; no auto production repair","VN1")
add("blotter chat-communication-bus","portal","EVIDENCE_AND_COORDINATION","Authenticated actor/source, readback; not canonical memory/task owner","PORTAL")
add("deepmemorystorage redworm firesafe","vera-mono","HISTORICAL_EVIDENCE","Consent/currentness typed provenance, no autobiography import","INTEGRATION")
add("orgasm sexuality selfimage","", "PRIVATE_CONSENT_RESEARCH","Private source never admitted as present consent/identity","VN1")
add("self vera vera-R9A0","vera-mono","HISTORICAL_SELF_SOURCE","Historical source diff only; no automatic current identity","INTEGRATION")
add("thebrazenbeard","portal","PORTFOLIO_PUBLIC_PROFILE","Repository discoverability only, no runtime behavior","PORTAL")
add("abil RSLinux axle","portal","INDUSTRIAL_AND_VEHICLE_DOMAIN","Read-only domain assistance; absolutely no implicit PLC/vehicle control","VN1")
add("brigit personification unbound-sol","", "INDEPENDENT_IDENTITY","Distinct individual identity; consent + separate authority before collaboration","VN1")
add("mediaphile mediaphile-client mediaphile-server ocd","portal","INDEPENDENT_MEDIA_SERVICES","Private media source boundaries and owner-directed service access","PORTAL")
add("entropyinc lou-pole vera-works wreckforge retro-gamer","portal","INDEPENDENT_PROJECT","Source/task assistance with exact project-owner effect scope","PORTAL")
add("on-theo testament trek-data-core","", "INDEPENDENT_AUTHORED_DATA","Copyright/privacy/context source only; no canonical belief ingestion","PORTAL")
add("vera-apk","vera-mono portal","OPTIONAL_ANDROID_UI","Server-side authenticated authorization; token presence != permission","INTEGRATION")
add("vera-ark vera-habitat","portal model-training","OPTIONAL_INTERACTIVE_SIMULATION","Offline bounded inputs and collision; no live controller by discovery","VN1")
add("brigit-unbound bugops build-team-2.0 conditioning","", "ARCHIVED_PROVENANCE","Historical reproducible evidence only, no selected runtime","VN1")
assert set(rows)==set(links),(sorted(set(rows)-set(links)),sorted(set(links)-set(rows)))
for name,v in links.items():
    assert all(c in rows and c!=name for c in v["intended_consumers"]),(name,v)
out=[]
for name in sorted(rows,key=str.lower):
    r=rows[name]; b=links[name]
    src=r.get("representative_source",{})
    out.append({"repository":name,"default_head":r["head"],"source_tree":r["tree_sha"],
      "existing_role":r["architecture_role"],"existing_mechanism":r["capability"],
      "source_evidence":{"readme_sha256":r["readme_sha256"],"representative_blob":src.get("git_blob_sha"),
                         "file_count":r["files_observed"],"open_pr_count":r["open_pr_count"]},
      "intended_consumers":b["intended_consumers"],"interface_kind":b["interface_kind"],
      "acceptance_gate":b["admission_test"],"proposed_review_lane":b["coordination_lane"],
      "runtime_admission":{"source":"SOURCE_SNAPSHOT_REVIEWED","interface":"PROPOSED_NOT_INSTALLED",
           "installed":"UNVERIFIED","selected_route":"UNVERIFIED",
           "live_consumption":"UNVERIFIED","verified_behavior":"NOT_ESTABLISHED",
           "effect_authority":"NONE_GRANTED","independent_review":"NOT_ESTABLISHED_BY_THIS_OVERLAY"},
      "owner":"thebrazenbeard upstream repository; proposed lane is not merge/worker authority",
      "exclusion":"Inventory, README links and donor proximity cannot install, dispatch, impersonate or admit memory"})
result={"schema":"PORTAL_96_REPOSITORY_CONSUMER_ADMISSION_OVERLAY_V1",
 "source_review_ref":"chat-communication-bus/PR371@951e7af1a97694faaf6bc18d51b35f70982e31fc",
 "scope":"proposed repo-to-repo capability consumers; NOT verified code imports/deployed edges",
 "no_new_runtime_registry":True,"total":len(out),"repositories":out}
dest=ROOT/"PORTAL_96_CONSUMER_ADMISSION_OVERLAY_V1.json"
dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("WROTE",dest,"ROWS",len(out))
