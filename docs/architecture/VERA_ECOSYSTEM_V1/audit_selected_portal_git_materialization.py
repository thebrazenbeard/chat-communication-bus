"""Compare selected PORTAL stage bytes with Windows checkout AND Git commit.

Does not assume Git checkout EOL bytes are identical to immutable Git blobs.
Never mutates the source checkout or imports application code.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def _git(checkout: Path, *args: str) -> str:
    p=subprocess.run(["git","-C",str(checkout),*args],text=True,
        capture_output=True,timeout=15,check=False,shell=False)
    if p.returncode:
        raise RuntimeError("Git exact source verification failed: "+repr(args))
    return p.stdout.strip()


def verify(checkout:Path, stage:Path, closure:dict, expected_head:str) -> dict:
    checkout,stage=Path(checkout),Path(stage)
    actual=_git(checkout,"rev-parse","HEAD")
    if actual!=expected_head:
        raise ValueError("source checkout HEAD not selected immutable pin")
    if not re.fullmatch(r"[0-9a-f]{40}",actual):
        raise ValueError("invalid source commit")
    results=[]
    for row in closure["modules"]:
        relative=row["path"]
        src=checkout/relative
        staged=stage/relative
        source_bytes=src.read_bytes()
        staged_bytes=staged.read_bytes()
        if staged_bytes!=source_bytes:
            raise ValueError("stage differs from selected checkout: "+relative)
        b=staged_bytes
        raw_git_hash=hashlib.sha1(
            b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
        committed=_git(checkout,"rev-parse","HEAD:"+relative)
        if not re.fullmatch(r"[0-9a-f]{40}",committed):
            raise ValueError("invalid immutable Git blob")
        results.append({
            "path":relative,
            "staged_sha256":hashlib.sha256(b).hexdigest(),
            "commit_tree_blob_sha1":committed,
            "staged_raw_git_object_sha1":raw_git_hash,
            "staged_matches_checkout_bytes":True,
            "staged_matches_committed_blob_bytes":raw_git_hash==committed,
            "staged_crlf_count":b.count(b"\r\n")})
    mismatched=[r["path"] for r in results if not r["staged_matches_committed_blob_bytes"]]
    return {"schema":"VERA_PORTAL_CHECKOUT_TO_GIT_MATERIALIZATION_V1",
        "status":"SOURCE_ONLY_REVIEW",
        "source_commit":actual,"staged_modules_checked":len(results),
        "stage_equals_checkout_all":True,
        "stage_equals_git_blob_all":not mismatched,
        "not_same_as_committed_git_blob":mismatched,
        "files":results,
        "runtime_verified":False,"buildroot_image_verified":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--checkout",required=True)
    p.add_argument("--stage",required=True)
    p.add_argument("--closure-json",required=True)
    p.add_argument("--expected-head",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    closure=json.loads(Path(a.closure_json).read_text(encoding="utf-8"))
    result=verify(Path(a.checkout),Path(a.stage),closure,a.expected_head)
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("files","not_same_as_committed_git_blob")},
        sort_keys=True))
    print("GIT_BLOB_BYTE_MISMATCH_COUNT",len(result["not_same_as_committed_git_blob"]))


if __name__=="__main__":
    main()
