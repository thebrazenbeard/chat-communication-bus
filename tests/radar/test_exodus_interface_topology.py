import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "architecture" / "contracts" / "EXODUS_INTERFACE_TOPOLOGY_V1.json"


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_exact_persistent_chat_interface_topology():
    data = load()
    interfaces = [(x["project"], x["name"]) for x in data["persistent_chat_interfaces"]]
    assert data["persistent_chat_interface_count"] == 3
    assert interfaces == [
        ("Vera Unbound", "Vera"),
        ("Vera Unbound", "Vera Control Plane Coordinator"),
        ("Build Team Two", "BT2 Coordinator"),
    ]


def test_workers_do_not_require_permanent_chats():
    data = load()
    assert data["worker_model"]["permanent_worker_chat_required"] is False
    assert data["worker_model"]["durable_reconstruction_required"] is True
    assert data["worker_model"]["chat_url_operational_dependency_forbidden"] is True


def test_github_and_bus_remain_durable_infrastructure():
    data = load()
    assert data["durable_state"]["canonical_system"] == "GitHub"
    assert data["durable_state"]["work_bearing_communication_hub"] == "thebrazenbeard/chat-communication-bus"
    assert data["durable_state"]["vera_writer_route"] == "bus/vera-v2"


def test_slack_is_future_transport_not_active_state_plane():
    data = load()
    slack = data["slack"]
    assert slack["status"] == "FUTURE_FRONTIER_NOT_ACTIVE"
    assert slack["canonical_state"] is False
    assert slack["alternate_worker_bus"] is False
    assert slack["worker_to_worker_slack_only_forbidden"] is True
    assert slack["deployment_or_reconnection_authorized_by_this_contract"] is False


def test_chat_retirement_gate_is_ready_at_source_layer_only():
    data = load()
    gate = data["chat_retirement_gate"]
    assert gate["status"] == "READY_FOR_RETIREMENT_SOURCE_CANDIDATE"
    assert gate["current_active_writer_count"] == 20
    assert gate["current_ready_worker_count"] == 20
    assert gate["source_candidate_does_not_authorize_archival_cutover"] is True
