import importlib
import pytest


def _module():
    try:
        return importlib.import_module("radar.registry")
    except Exception as exc:
        pytest.fail(f"Radar registry implementation missing: {exc}")


def test_identity_survives_node_offline_state():
    m = _module()
    r = m.IdentityRegistry()
    r.register_identity("yin", display_name="Yin")
    r.register_node("node-yin-1", identity_id="yin", status=m.NodeStatus.ONLINE)
    r.set_node_status("node-yin-1", m.NodeStatus.OFFLINE)
    assert r.identity("yin").display_name == "Yin"
    assert r.node("node-yin-1").status is m.NodeStatus.OFFLINE


def test_alias_collision_fails_deterministically():
    m = _module()
    r = m.IdentityRegistry()
    r.register_identity("brigit", display_name="Brigit", aliases=("bridget",))
    with pytest.raises(m.RegistryError, match="ALIAS_COLLISION"):
        r.register_identity("someone_else", display_name="Else", aliases=("Bridget",))


def test_endpoint_is_separate_from_identity_and_node():
    m = _module()
    r = m.IdentityRegistry()
    r.register_identity("radar", display_name="Radar")
    r.register_endpoint("github-radar", identity_id="radar", transport="github", address="thebrazenbeard/chat-communication-bus")
    assert r.endpoint("github-radar").identity_id == "radar"
    assert r.identity("radar").identity_id == "radar"
