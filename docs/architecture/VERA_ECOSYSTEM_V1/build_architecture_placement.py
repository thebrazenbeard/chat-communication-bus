"""Build a review-only, placement-specific 96-repo architecture from CCB #372."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PORTFOLIO=HERE.parents[1]/"portfolio"/"PORTAL_96_REPOSITORY_REVIEW_20261017"
SOURCE=json.loads((PORTFOLIO/"PORTAL_96_CONSUMER_ADMISSION_OVERLAY_V1.json").read_text(encoding="utf-8"))
ALLOWED={"MONO_EMBEDDED","VERAOS_BOOT_REQUIRED","VERAOS_STAGED_SOURCE","HOST_SERVICE_OPTIONAL",
         "CLIENT_OPTIONAL","EXTERNAL_INDEPENDENT","RESEARCH_ONLY","HISTORICAL_PROVENANCE",
         "PRIVATE_EXCLUDED","ARCHIVE_ONLY"}
explicit={
 "vera-mono":"VERAOS_STAGED_SOURCE",
 "vera-os":"VERAOS_BOOT_REQUIRED",
 "portal":"HOST_SERVICE_OPTIONAL",
 "project-runner":"HOST_SERVICE_OPTIONAL",
 "pre-active":"VERAOS_STAGED_SOURCE",
 "volition":"VERAOS_STAGED_SOURCE",
 "vera-control-plane":"RESEARCH_ONLY",
 "v-e-r-a":"RESEARCH_ONLY",
 "ccb-core":"HOST_SERVICE_OPTIONAL",
 "chat-communication-bus":"HOST_SERVICE_OPTIONAL",
 "executor":"HOST_SERVICE_OPTIONAL",
 "workbridge":"HOST_SERVICE_OPTIONAL",
 "workbridgecommander":"HOST_SERVICE_OPTIONAL",
 "WorkBridgeMCP":"HOST_SERVICE_OPTIONAL",
 "intranel":"HOST_SERVICE_OPTIONAL",
 "vera-mesh":"HOST_SERVICE_OPTIONAL",
 "vera-synology":"HOST_SERVICE_OPTIONAL",
 "spk-packager":"HOST_SERVICE_OPTIONAL",
 "tattler":"HOST_SERVICE_OPTIONAL",
 "blotter":"HOST_SERVICE_OPTIONAL",
 "rezon":"MONO_EMBEDDED",
 "ingest":"MONO_EMBEDDED",
 "roots":"MONO_EMBEDDED",
 "temporal":"MONO_EMBEDDED",
 "project-lantern":"MONO_EMBEDDED",
 "skeletonkey":"MONO_EMBEDDED",
 "vera-adapter":"MONO_EMBEDDED",
 "wip":"RESEARCH_ONLY",
 "Attune":"RESEARCH_ONLY",
 "conations":"RESEARCH_ONLY",
 "vera-model":"RESEARCH_ONLY",
 "model-training":"RESEARCH_ONLY",
 "mosaic":"RESEARCH_ONLY",
 "ears":"RESEARCH_ONLY",
 "vision":"RESEARCH_ONLY",
 "physica":"RESEARCH_ONLY",
 "vera-apk":"CLIENT_OPTIONAL",
 "vera-ark":"CLIENT_OPTIONAL",
 "vera-habitat":"CLIENT_OPTIONAL",
 "brigit":"EXTERNAL_INDEPENDENT",
 "personification":"EXTERNAL_INDEPENDENT",
 "unbound-sol":"EXTERNAL_INDEPENDENT",
 "orgasm":"PRIVATE_EXCLUDED",
 "sexuality":"PRIVATE_EXCLUDED",
 "selfimage":"PRIVATE_EXCLUDED",
 "brigit-unbound":"ARCHIVE_ONLY",
 "bugops":"ARCHIVE_ONLY",
 "build-team-2.0":"ARCHIVE_ONLY",
 "conditioning":"ARCHIVE_ONLY",
}
ROLE_DEFAULT={
 "RESEARCH":"RESEARCH_ONLY","MODEL":"RESEARCH_ONLY","SENSOR":"RESEARCH_ONLY",
 "ASSURANCE":"RESEARCH_ONLY","SAFETY":"RESEARCH_ONLY","DONOR":"RESEARCH_ONLY",
 "GOVERNANCE":"RESEARCH_ONLY","DOMAIN":"EXTERNAL_INDEPENDENT",
 "CLIENT":"CLIENT_OPTIONAL","APPLICATION":"CLIENT_OPTIONAL",
 "INDEPENDENT":"EXTERNAL_INDEPENDENT","EVIDENCE":"HISTORICAL_PROVENANCE",
 "PROVENANCE":"HISTORICAL_PROVENANCE","ARCHIVE":"ARCHIVE_ONLY",
}
placements=[]
for row in SOURCE["repositories"]:
 name=row["repository"]
 role=row["existing_role"]
 placement=explicit.get(name,ROLE_DEFAULT.get(role))
 if placement not in ALLOWED: raise ValueError((name,role,placement))
 child=dict(row)
 child["placement_proposal"]=placement
 child["in_veraos_minimal_image"]=name in {"vera-mono","pre-active","volition","vera-os"}
 child["sibling_repo_import_required"]=False
 child["promotion_policy"]="EXPLICIT_SOURCE_DIFF_TEST_AND_OWNER_AUTHORITY_ONLY"
 child["runtime_evidence"]="NOT_ESTABLISHED_BY_THIS_DOCUMENT"
 placements.append(child)
assert len(placements)==96 and len({r["repository"] for r in placements})==96
assert set(explicit) <= {r["repository"] for r in placements}
assert all(r["in_veraos_minimal_image"]==(r["repository"] in {"vera-mono","pre-active","volition","vera-os"}) for r in placements)
output={
 "schema":"VERA_ECOSYSTEM_ARCHITECTURE_V1_CANDIDATE",
 "status":"REVIEW_ONLY_NOT_APPROVED_NOT_INSTALLED",
 "source_overlay_head":"ef17ee929d807f5da033a3d5391d553b65c464e8",
 "canonical_runtime":"vera_core.QualifiedVeraRuntime",
 "canonical_state":"vera_core.VeraStateDirectory",
 "operating_modes":["WINDOWS_PORTAL_DESKTOP","CHATGPT_EXTERNAL_INTERACTION",
                    "VERAOS_LINUX_GRAPHICAL","OPTIONAL_CLIENT_HOST_SERVICES"],
 "placement_categories":sorted(ALLOWED),"repositories":placements,
}
(HERE/"VERA_96_PLACEMENT_AND_CONSUMERS_V1.json").write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PLACEMENTS",len(placements))
