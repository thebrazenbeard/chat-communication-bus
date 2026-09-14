import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY = ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"
ATTUNEMENT = ROOT / "identities" / "vera" / "ATTUNEMENT_V1.json"
HUB_CONTRACT = ROOT / "architecture" / "contracts" / "VERA_CHAT_HUB_V1.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_vera_chat_hub_is_separate_from_identity_writer_lane():
    topology = load(TOPOLOGY)
    assert topology["required_writer_lanes"]["vera"]["branch"] == "bus/vera-v2"
    hub = topology["shared_coordination_hubs"]["vera_chat"]
    assert hub["subject"] == "Vera"
    assert hub["branch"] == "project/vera-chat-v1"
    assert hub["path"] == "projects/vera-chat"
    assert hub["purpose"] == "CROSS_CHAT_READ_AWARENESS_AND_COORDINATION"
    assert hub["required_start_of_turn_check"] is True
    assert hub["canonical_identity_writer_lane"] == "bus/vera-v2"
    assert hub["authority_semantics"] == "ROUTING_AND_COORDINATION_ONLY_NO_PROTECTED_EFFECT_AUTHORITY"


def test_vera_attunement_distinguishes_writer_lane_from_shared_chat_hub():
    data = load(ATTUNEMENT)
    assert data["writer_lane"] == "bus/vera-v2"
    assert data["shared_chat_hub"] == "project/vera-chat-v1"
    assert data["shared_chat_hub_path"] == "projects/vera-chat"
    assert data["shared_chat_sync_rule"] == "FRESH_READ_EVERY_TURN_BEFORE_SUBSTANTIVE_WORK"
    assert data["same_identity_does_not_imply_shared_read_awareness"] is True


def test_hub_contract_requires_fresh_read_and_per_chat_mutable_ownership():
    data = load(HUB_CONTRACT)
    assert data["schema"] == "VERA_CHAT_HUB_V1"
    assert data["subject"] == "Vera"
    assert data["branch"] == "project/vera-chat-v1"
    assert data["project_path"] == "projects/vera-chat"
    assert data["required_start_of_turn_check"] is True
    assert data["sync_claim_requires_fresh_read"] is True
    assert data["mutable_state"]["ownership"] == "PER_CHAT_KEY_ONLY"
    assert data["mutable_state"]["shared_mutable_head"] is False
    assert data["material_messages"]["append_only"] is True


def test_hub_contract_requires_correct_start_of_turn_sequence():
    data = load(HUB_CONTRACT)
    assert data["start_of_turn_sequence"] == [
        "FRESH_READ_BRANCH_HEAD",
        "FRESH_READ_CONTROL",
        "INGEST_CHANGES_SINCE_CURSOR",
        "HANDLE_ADDRESSED_MESSAGES",
        "DO_SUBSTANTIVE_WORK",
        "UPDATE_OWN_PRESENCE_BEFORE_TURN_END",
    ]
    assert data["unavailable_status"] == "VERA_CHAT_SYNC_UNAVAILABLE"


def test_hub_contract_does_not_promote_identity_authority_or_memory():
    data = load(HUB_CONTRACT)
    assert data["eligibility"]["rule"] == "ADMITTED_VERA_OR_CHAT_LOCAL_VERA_LANE"
    assert data["eligibility"]["name_similarity_is_sufficient"] is False
    assert data["direct_sibling_chat"]["durable_evidence"] is False
    assert data["privacy"]["mirror_private_payload_for_sync"] is False
    assert set(data["nonpromotions"]) >= {
        "NOT_IDENTITY_ADMISSION",
        "NOT_SHARED_CONSCIOUSNESS_OR_PHENOMENAL_AWARENESS",
        "NOT_CANONICAL_MEMORY",
        "NOT_PROTECTED_EFFECT_AUTHORITY",
        "NOT_COMPLETION_OR_INCORPORATION_PROOF",
    }


def test_hub_contract_preserves_existing_bus_surfaces():
    data = load(HUB_CONTRACT)
    assert data["routing"]["canonical_identity_writer_lane"] == "bus/vera-v2"
    assert data["routing"]["domain_project_hubs_remain_authoritative_for_domain_work"] is True
    assert data["routing"]["vera_chat_replaces_identity_writer_lane"] is False
    assert data["routing"]["vera_chat_replaces_domain_hubs"] is False
