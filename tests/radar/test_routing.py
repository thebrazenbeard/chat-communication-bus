import importlib
import pytest


def _modules():
    try:
        return importlib.import_module("radar.envelope"), importlib.import_module("radar.registry"), importlib.import_module("radar.routing")
    except Exception as exc:
        pytest.fail(f"Radar routing implementation missing: {exc}")


def _env(e, **overrides):
    raw = {"schema_version": 1, "message_id": "m1", "created_at": "2026-09-02T12:00:00Z", "sender": "vera", "audience": [], "domain": "database", "intent": "event", "priority": 2, "payload": {}}
    raw.update(overrides)
    return e.RadarEnvelope.from_mapping(raw).envelope


def _activate(reg, rmod, identity, *, min_priority=4):
    reg.register_identity(identity, display_name=identity.title())
    reg.register_node(f"{identity}-node", identity_id=identity, status=rmod.NodeStatus.ONLINE)
    reg.subscribe(identity, domain="database", min_priority=min_priority)


def test_direct_audience_routes_only_to_named_authorized_live_identity():
    e, rmod, rt = _modules()
    reg = rmod.IdentityRegistry()
    _activate(reg, rmod, "yin")
    _activate(reg, rmod, "yang")
    decision = rt.Router(reg).route(_env(e, audience=["yin"]))
    assert decision.recipients == ("yin",)


def test_subscription_route_respects_domain_min_priority_and_live_registration():
    e, rmod, rt = _modules()
    reg = rmod.IdentityRegistry()
    _activate(reg, rmod, "mune", min_priority=2)
    assert rt.Router(reg).route(_env(e, priority=1)).recipients == ("mune",)
    assert rt.Router(reg).route(_env(e, priority=3)).recipients == ()


def test_priority_queue_orders_without_granting_authority():
    e, _, rt = _modules()
    q = rt.PriorityQueue()
    q.push(_env(e, message_id="slow", priority=4))
    q.push(_env(e, message_id="urgent", priority=0))
    first = q.pop()
    assert first.message_id == "urgent"
    assert first.authority_ref is None


def test_dedupe_window_rejects_same_key_inside_window_and_allows_after():
    _, _, rt = _modules()
    d = rt.DedupeWindow(window_ms=500)
    assert d.accept("abc", 1000) is True
    assert d.accept("abc", 1200) is False
    assert d.accept("abc", 1600) is True
