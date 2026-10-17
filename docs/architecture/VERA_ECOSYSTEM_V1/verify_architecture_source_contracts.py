"""Exact GitHub blob and source-API conformance for three existing host boundaries.

This script does not import or execute a resident, build an image or grant effects.
With --live it performs only gh api GET against immutable pinned source blobs.
"""
from __future__ import annotations
import argparse, ast, base64, hashlib, json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PORTFOLIO=ROOT.parents[1]/"portfolio"/"PORTAL_96_REPOSITORY_REVIEW_20261017"
SOURCES={
 "mono":("vera-mono","d243d2efd01777655e511d91ea816fd804488ecf"),
 "desktop":("portal","6fd7866013cbbfccb4981a93f6600b36d422f4f9"),
 "desktop_host":("portal","d2e06aa3ee499fe6b11ec9636a1501812ae731c6"),
 "veraos":("vera-os","76c6e60b828a1ce386985f48f40e6387f5756662"),
 "host_bridge":("portal","63c0ab544f9a430727d744e3f95a7f0b64549706"),
}
def _gitblob_sha(raw:bytes)->str:
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def source(repo:str,sha:str)->ast.AST:
 assert len(sha)==40 and all(c in "0123456789abcdef" for c in sha)
 p=subprocess.run(["gh","api","--method","GET",
     f"repos/thebrazenbeard/{repo}/git/blobs/{sha}"],
     text=True,capture_output=True,shell=False,timeout=30,check=False)
 if p.returncode: raise RuntimeError("source read failed for "+repo)
 obj=json.loads(p.stdout)
 if obj.get("encoding")!="base64" or not isinstance(obj.get("content"),str):
  raise ValueError("unsupported blob encoding")
 raw=base64.b64decode(obj["content"],validate=False)
 if _gitblob_sha(raw)!=sha: raise AssertionError("source SHA mismatch")
 return ast.parse(raw.decode("utf-8"))
def _find(tree,name):
 return [x for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and x.name==name]
def _calls(tree,name):
 return [x for x in ast.walk(tree) if isinstance(x,ast.Call) and
         (isinstance(x.func,ast.Name) and x.func.id==name or
          isinstance(x.func,ast.Attribute) and x.func.attr==name)]
def check_pinned_host_apis():
 trees={name:source(*target) for name,target in SOURCES.items()}
 assert _find(trees["mono"],"open_message")
 assert _find(trees["mono"],"recover_message")
 assert _find(trees["mono"],"conversation_history")
 assert _find(trees["desktop"],"DesktopRuntimeCommandHandler")
 assert _find(trees["desktop"],"canonical_locator")
 desktop_handler=_find(trees["desktop"],"handle")
 assert desktop_handler
 assert any(_calls(method,"open_message") for method in desktop_handler)
 assert _find(trees["desktop_host"],"_windows_state_mutex_name")
 assert _calls(trees["desktop_host"],"from_state_directory")
 assert _find(trees["veraos"],"compose_components")
 assert _find(trees["veraos"],"ResidentSupervisor")
 assert _calls(trees["veraos"],"from_state_directory")
 assert _calls(trees["veraos"],"open_message")
 assert _find(trees["host_bridge"],"PortalHostBridgeStore")
 assert _find(trees["host_bridge"],"PortalHostExecutionAdapter")
 assert _find(trees["host_bridge"],"record_reconciliation")
 assert _find(trees["host_bridge"],"pending_dispatches")
 return {"verified_blobs":{n:sha for n,(_,sha) in SOURCES.items()},
         "result":"SOURCE_API_PRESENT_ONLY",
         "guest_qualified":False,"live_runtime_selected":False}
def check_architecture():
 overlay=json.loads((PORTFOLIO/"PORTAL_96_CONSUMER_ADMISSION_OVERLAY_V1.json").read_text(encoding="utf-8"))
 arch=json.loads((ROOT/"VERA_96_PLACEMENT_AND_CONSUMERS_V1.json").read_text(encoding="utf-8"))
 a={r["repository"]:r for r in arch["repositories"]}
 b={r["repository"]:r for r in overlay["repositories"]}
 assert arch["status"]=="REVIEW_ONLY_NOT_APPROVED_NOT_INSTALLED"
 assert len(a)==len(b)==96 and len(arch["repositories"])==96
 assert all(a[n]["default_head"]==b[n]["default_head"] and
            a[n]["source_tree"]==b[n]["source_tree"] for n in a)
 assert all(a[n]["runtime_admission"]==b[n]["runtime_admission"] for n in a)
 assert all(a[n]["placement_proposal"] in arch["placement_categories"] for n in a)
 assert {n for n in a if a[n]["in_veraos_minimal_image"]}=={
   "vera-mono","vera-os","pre-active","volition"}
 assert a["portal"]["placement_proposal"]=="HOST_SERVICE_OPTIONAL"
 assert a["rezon"]["placement_proposal"]=="MONO_EMBEDDED"
 assert all(a[n]["placement_proposal"]=="ARCHIVE_ONLY" for n in
            ("brigit-unbound","bugops","build-team-2.0","conditioning"))
 assert all(a[n]["placement_proposal"] in {"PRIVATE_EXCLUDED","EXTERNAL_INDEPENDENT"}
            for n in ("brigit","personification","unbound-sol","orgasm","sexuality","selfimage"))
 assert all(not r["sibling_repo_import_required"] for r in a.values())
 assert all(r["runtime_evidence"]=="NOT_ESTABLISHED_BY_THIS_DOCUMENT"
            for r in a.values())
 return {"rows":96,"placement_verified":"STRUCTURAL_PROPOSAL_ONLY",
         "runtime_qualified":False}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--live",action="store_true",help="read five immutable GitHub blobs")
 args=p.parse_args()
 result={"architecture":check_architecture()}
 if args.live: result["source_api"]=check_pinned_host_apis()
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
