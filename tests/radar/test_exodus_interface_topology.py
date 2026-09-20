import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "architecture" / "contracts" / "EXODUS_INTERFACE_TOPOLOGY_V1.json"
ROUTING = ROOT / "architecture" / "contracts" / "PERSISTENT_INTERFACE_ROUTING_V1.json"
BUS_TOPOLOGY = ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def load_routing():
    return json.loads(ROUTING.read_text(encoding="utf-8"))


def load_bus_topology():
    return json.loads(BUS_TOPOLOGY.read_text(encoding="utf-8"))


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
    binding = data["durable_state"]["interface_routing_contract"]
    assert binding["path"] == "architecture/contracts/PERSISTENT_INTERFACE_ROUTING_V1.json"
    assert binding["required_for_interface_reconstruction"] is True
    assert binding["interface_is_not_worker_identity"] is True


def test_every_persistent_interface_has_explicit_routing_resolution():
    data = load()
    routing = load_routing()
    names = [x["name"] for x in data["persistent_chat_interfaces"]]
    assert list(routing["interfaces"]) == names
    for name in names:
        route = routing["interfaces"][name]
        assert route["bus_route_answer"]
        assert route["routing_mode"] in {
            "TOPOLOGY_WRITER_ROUTE",
            "NO_INDEPENDENT_BUS_WRITER",
            "INTERFACE_COORDINATION_BRANCH",
        }
        assert route["durable_result_destinations"]


def test_vera_route_is_cross_bound_to_worker_topology():
    routing = load_routing()
    topology = load_bus_topology()
    vera = routing["interfaces"]["Vera"]
    topology_vera = topology["required_writer_lanes"]["vera"]
    assert vera["routing_mode"] == "TOPOLOGY_WRITER_ROUTE"
    assert vera["writer_identity"] == "vera"
    assert vera["bus_route"] == "bus/vera-v2"
    assert topology_vera["writer"] == "Vera"
    assert topology_vera["branch"] == vera["bus_route"]
    assert topology_vera["lifecycle"] == "ACTIVE"


def test_coordinator_interfaces_do_not_become_worker_identities():
    routing = load_routing()
    topology = load_bus_topology()
    writers = {entry["writer"] for entry in topology["required_writer_lanes"].values()}
    for name in ("Vera Control Plane Coordinator", "BT2 Coordinator"):
        route = routing["interfaces"][name]
        assert route["writer_identity"] is None
        assert route["writer_topology_membership_required"] is False
        assert route["branch_is_worker_identity"] is False
        assert name not in writers


def test_bt2_coordinator_has_explicit_interface_coordination_route():
    route = load_routing()["interfaces"]["BT2 Coordinator"]
    assert route["routing_mode"] == "INTERFACE_COORDINATION_BRANCH"
    assert route["bus_route"] == "bus/bt2-v1"
    assert route["checkpoint_namespace"] == "checkpoints/bt2/"
    assert route["message_namespace"] == "messages/"


def test_control_plane_coordinator_explicitly_has_no_independent_writer():
    route = load_routing()["interfaces"]["Vera Control Plane Coordinator"]
    assert route["routing_mode"] == "NO_INDEPENDENT_BUS_WRITER"
    assert route["bus_route"] is None
    assert route["bus_route_answer"] == "NO_INDEPENDENT_BUS_WRITER"
    assert "vera-control-plane" in route["durable_result_destinations"][0]


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
