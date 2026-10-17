"""Review-only typed portfolio edges. Never infer imports or deployments."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OVERLAY=ROOT.parents[1]/"portfolio"/"PORTAL_96_REPOSITORY_REVIEW_20261017"/"PORTAL_96_CONSUMER_ADMISSION_OVERLAY_V1.json"
ARCH=ROOT/"VERA_96_PLACEMENT_AND_CONSUMERS_V1.json"
STAGE_PINS={
    "vera-mono":"89ba1d18da78e7e38f015cf8d8ef4f528aae9df8",
    "portal":"36fa04da4e5eb383fecf463c72a43b94ca47d7e5",
    "pre-active":"1f23a809d7274df506e03e2d9052525538c3bcf6",
    "volition":"dbc628d376515a0a523b1eecdf62129cca5d6b08",
}
SOURCE_STAGE_RECEIPT_SHA256="6f0031c1fcbaed41e4e3f6947e90a92ed5656ac3e09329de7d8e0b0f8417eca5"
TYPES={"PROPOSED_CONSUMER","STAGED_SOURCE_SNAPSHOT","VERIFIED_HARD_RUNTIME_IMPORT"}
def _cycle(edges):
    graph={}
    for e in edges:
        graph.setdefault(e["from"],set()).add(e["to"])
    exploring=set()
    done=set()
    def visit(node,trail):
        if node in exploring:
            return trail[trail.index(node):]
        if node in done:return None
        exploring.add(node)
        for neighbor in sorted(graph.get(node,())):
            found=visit(neighbor,trail+[neighbor])
            if found:return found
        exploring.remove(node)
        done.add(node)
        return None
    for node in sorted(graph):
        found=visit(node,[node])
        if found:return found
    return []
def validate_edges(artifact, *, externally_verified_imports=frozenset()):
    rows=artifact["edges"]
    if len({(e["from"],e["to"],e["type"]) for e in rows})!=len(rows):
        raise ValueError("duplicate edge")
    if any(e["type"] not in TYPES for e in rows):
        raise ValueError("unknown type")
    known=set(artifact["repositories"])
    for edge in rows:
        if edge["from"] not in known or edge["to"] not in known:
            raise ValueError("unknown repository endpoint")
        if edge["from"]==edge["to"]:raise ValueError("self dependency")
        if edge["type"]=="VERIFIED_HARD_RUNTIME_IMPORT":
            proof=edge.get("runtime_import_proof")
            if not isinstance(proof,dict) or not all(proof.get(k) for k in
                ("consumer_commit","importer_file_blob","imported_module","verified_test")):
                raise ValueError("unproved hard runtime import")
    boot=[x for x in rows if x["type"]=="VERIFIED_HARD_RUNTIME_IMPORT"]
    cycle=_cycle(boot)
    if cycle:raise ValueError("runtime cycle: "+" -> ".join(cycle))
    # An attacker can fill strings in runtime_import_proof. This review
    # does not attest imports: a separate executed verifier must supply
    # immutable (from,to,consumer_commit,importer_blob,module) tuples.
    for edge in boot:
        proof=edge["runtime_import_proof"]
        key=(edge["from"],edge["to"],proof["consumer_commit"],
             proof["importer_file_blob"],proof["imported_module"])
        if key not in externally_verified_imports:
            raise ValueError("hard runtime import lacks independent source verification")
    return {"total":len(rows),"hard_runtime_imports":len(boot),
            "typed_boot_cycle":cycle,
            "stage_edges":sum(x["type"]=="STAGED_SOURCE_SNAPSHOT" for x in rows)}
def construct():
    overlay=json.loads(OVERLAY.read_text(encoding="utf-8"))
    architecture=json.loads(ARCH.read_text(encoding="utf-8"))
    rows={r["repository"]:r for r in overlay["repositories"]}
    sources={r["repository"] for r in architecture["repositories"]}
    if len(rows)!=96 or set(rows)!=sources:raise ValueError("96 source mismatch")
    edges=[{"from":name,"to":consumer,"type":"PROPOSED_CONSUMER",
            "evidence":"CCB #372 proposed interface, NOT a code import",
            "source_head":row["default_head"]}
           for name,row in sorted(rows.items()) for consumer in sorted(row["intended_consumers"])]
    for name,head in sorted(STAGE_PINS.items()):
        edges.append({"from":"vera-os","to":name,"type":"STAGED_SOURCE_SNAPSHOT",
            "source_head":head,"evidence":"431-byte-checked-file source stage only",
            "stage_receipt_sha256":SOURCE_STAGE_RECEIPT_SHA256,
            "not_guest_boot_required":True})
    return {"schema":"VERA_ECOSYSTEM_TYPED_EDGES_V1",
            "status":"REVIEW_ONLY_NO_RUNTIME_PROMOTION",
            "repositories":sorted(rows),"consumer_edge_count":len(edges)-4,
            "stage_edge_count":4,"source_overlay_head":"ef17ee929d807f5da033a3d5391d553b65c464e8",
            "edges":edges}
def main():
    x=construct()
    result=validate_edges(x)
    (ROOT/"VERA_96_TYPED_DEPENDENCY_EDGES_V1.json").write_text(
        json.dumps(x,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    main()
