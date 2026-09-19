import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_worker_reconstruction_contract_has_no_permanent_worker_chat_dependency():
    payload = json.loads(
        (ROOT / "architecture" / "contracts" / "WORKER_RECONSTRUCTION_V1.json")
        .read_text(encoding="utf-8-sig")
    )
    assert payload["permanent_chat_dependency"] is False
    assert payload["execution_context"] == "REPLACEABLE_TERMINAL"
    assert payload["persistent_chat_interfaces"] == [
        "Vera",
        "Vera Control Plane Coordinator",
        "BT2 Coordinator",
    ]
    assert payload["rules"]["routing_is_not_authority"] is True
    assert payload["rules"]["chat_url_is_not_current_state_locator"] is True


def test_active_writer_lanes_are_durable_routes_not_chat_locators():
    topology = json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json")
        .read_text(encoding="utf-8-sig")
    )
    active = {
        key: value
        for key, value in topology["required_writer_lanes"].items()
        if value["lifecycle"] == "ACTIVE"
    }
    assert active
    for key, value in active.items():
        assert value["branch"].startswith("bus/")
        assert "chatgpt.com" not in value["branch"]
        assert value["writer"]
