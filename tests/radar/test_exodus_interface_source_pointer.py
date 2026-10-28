import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POINTER = ROOT / "architecture" / "contracts" / "EXODUS_INTERFACE_TOPOLOGY_V1.json"

EXPECTED_BINDINGS = {
    "persistent_interfaces": (
        "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json",
        "3825f51a67d736879d9d998e42bd4d1c802aab78",
    ),
    "exodus_workers": (
        "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V2.json",
        "d7251d5f8c192e314d7de247e72b5a9e71171c1b",
    ),
}


def test_exodus_pointer_binds_exact_bt2_git_objects_not_moving_main():
    data = json.loads(POINTER.read_text(encoding="utf-8"))
    assert data["schema_version"] == "EXODUS_INTERFACE_TOPOLOGY_SOURCE_POINTER_V1"
    assert data["status"] == "NON_AUTHORITATIVE_SOURCE_POINTER_ONLY"
    assert data["owning_repository"] == "thebrazenbeard/bt2"
    assert data["source_commit"] == "81dc5c0ccda28e1f627ad49c2f81bcb56ff21e6b"
    assert set(data["source_bindings"]) == set(EXPECTED_BINDINGS)
    for key, (path, blob) in EXPECTED_BINDINGS.items():
        assert data["source_bindings"][key] == {"path": path, "git_blob_sha1": blob}
    assert "moving main" in data["binding_rule"]


def test_exodus_pointer_cannot_claim_private_or_runtime_authority():
    data = json.loads(POINTER.read_text(encoding="utf-8"))
    assert all(value is False for value in data["authority"].values())
    assert set(data["runtime_states"].values()) == {"NOT_ESTABLISHED"}
    assert not set(data).intersection({
        "required_writer_lanes", "persistent_chat_interfaces", "workers", "provider_grants",
        "tokens", "api_keys", "messages", "receipts",
    })
