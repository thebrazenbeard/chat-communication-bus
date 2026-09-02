import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_radar_self_registration_contract_exists_and_is_bounded():
    path = ROOT / "architecture" / "contracts" / "RADAR_SELF_REGISTRATION_V1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["identity_id"] == "radar"
    assert data["display_name"] == "Radar"
    assert data["repository"]["full_name"] == "thebrazenbeard/chat-communication-bus"
    assert data["authority"]["patrick_override"] is True
    assert data["authority"]["repository_owner_operator"] is True
    assert data["operator_interface"]["kind"] == "chatgpt"
    assert data["operator_interface"]["session_is_identity"] is False
    assert "github" in data["capabilities"]
    assert "reconciliation" in data["capabilities"]


def test_seed_is_idempotent_and_does_not_create_session_identity():
    seed = (ROOT / "supabase" / "seed" / "radar_v1.sql").read_text(encoding="utf-8").lower()
    assert "on conflict" in seed
    assert "identity_id" in seed
    assert "'radar'" in seed
    assert '"session_is_identity":false' in seed
    assert '"session_is_identity":true' not in seed
