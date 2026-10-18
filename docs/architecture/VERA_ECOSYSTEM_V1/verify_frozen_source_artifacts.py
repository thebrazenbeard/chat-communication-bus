"""Fail-closed integrity of the frozen CCB V1 source assertions.

Content-addressed source identity is not proof of truthful ownership, an actual
consumer edge, installed software, or independent acceptance. New baseline
claims require explicitly rebinding these pins and re-running hostile review.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINNED_BLOBS = {
    "VERA_96_PLACEMENT_AND_CONSUMERS_V1.json": "4316e88c6aaf42ceba57fbd27c5b4b3cb6b65c5c",
    "VERA_96_TYPED_DEPENDENCY_EDGES_V1.json": "b4c727d570aa2be3737b5474576214a089da16a0",
    "VERAOS_MINIMAL_BOM_V1.json": "c545f2132748493616cd61ead21166fd46ef0287",
}
PINNED_STAGE_RECEIPT = "6f0031c1fcbaed41e4e3f6947e90a92ed5656ac3e09329de7d8e0b0f8417eca5"
PINNED_GATE_STATUSES = {
    "SOURCE": "SOURCE_ONLY_GREEN", "KCONFIG": "UNQUALIFIED",
    "IMAGE": "NOT_BUILT", "TARGET_IMPORT": "NOT_TESTED",
    "NORMAL_GUI": "NOT_BOOTED", "COLD_TWO_BOOT": "NOT_RUN",
    "MODEL": "HOLD", "DISK_INSTALL": "NOT_AUTHORIZED",
}


def check_frozen_semantics(portfolio, typed, bom):
    errors = []
    for filename, incoming in zip(PINNED_BLOBS, (portfolio, typed, bom)):
        try:
            raw = (HERE / filename).read_bytes()
            git_sha = hashlib.sha1(
                b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw
            ).hexdigest()
            frozen = json.loads(raw.decode("utf-8"))
        except (OSError, ValueError, UnicodeError, TypeError) as exc:
            errors.append(f"{filename}: frozen source unavailable: {type(exc).__name__}")
            continue
        if git_sha != PINNED_BLOBS[filename]:
            errors.append(f"{filename}: source blob changed; reviewer rebind required")
        if type(incoming) is not dict or incoming != frozen:
            errors.append(f"{filename}: source semantic assertions differ from frozen baseline")

    stages = [x for x in typed.get("edges", [])
              if x.get("type") == "STAGED_SOURCE_SNAPSHOT"]
    if any(x.get("stage_receipt_sha256") != PINNED_STAGE_RECEIPT for x in stages):
        errors.append("all source stage receipts must match exact pinned receipt")
    statuses = {x.get("gate"): x.get("status") for x in bom.get("acceptance", [])}
    if statuses != PINNED_GATE_STATUSES or len(bom.get("acceptance", [])) != len(PINNED_GATE_STATUSES):
        errors.append("guest/model acceptance statuses differ from pinned evidence ceiling")
    return errors
